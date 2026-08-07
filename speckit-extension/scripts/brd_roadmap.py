#!/usr/bin/env python3
"""brd-roadmap — trích outline từ cây BRD markdown và gác cổng docs/roadmap.md.

    outline <brd-dir> [--out <json>] [--head N]
    verify <roadmap.md> --brd <dir> [--decisions <json>]
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

NODE_RE = re.compile(r"^\s*-\s*\{(.*)\}\s*$")


def _die(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def _scan_flow(body):
    """Tách các cặp `k: v` của một flow mapping một dòng, tôn trọng chuỗi có escape.

    Không dùng được `split(",")`: `title` có thể chứa dấu phẩy và `\\"` bên trong.
    """
    out, i, n = {}, 0, len(body)
    while i < n:
        while i < n and body[i] in " ,":
            i += 1
        j = body.find(":", i)
        if j < 0:
            break
        key = body[i:j].strip()
        i = j + 1
        while i < n and body[i] == " ":
            i += 1
        if i < n and body[i] == '"':
            i += 1
            buf = []
            while i < n:
                c = body[i]
                if c == "\\" and i + 1 < n:
                    buf.append(body[i + 1])
                    i += 2
                    continue
                if c == '"':
                    i += 1
                    break
                buf.append(c)
                i += 1
            val = "".join(buf)
        else:
            k = i
            while i < n and body[i] != ",":
                i += 1
            val = body[k:i].strip()
        out[key] = val
    return out


def parse_manifest(path):
    """Đọc `brd.manifest.yml` -> danh sách node theo thứ tự tài liệu."""
    path = Path(path)
    if not path.is_file():
        _die(f"Không thấy {path} — thư mục này không phải cây BRD do brd-import sinh ra.")
    nodes = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = NODE_RE.match(line)
        if not m:
            continue
        f = _scan_flow(m.group(1))
        parent = f.get("parent")
        nodes.append({
            "id": f["id"],
            "order": int(f["order"]),
            "depth": int(f["depth"]),
            "kind": f["kind"],
            "title": f["title"],
            "path": f.get("path"),
            "dir": f.get("dir"),
            "inline": f.get("inline") == "true",
            "parent": None if parent in (None, "null", "") else parent,
            "chars": int(f["chars"]),
        })
    if not nodes:
        _die(f"{path} không có node nào — manifest hỏng hoặc rỗng.")
    return nodes


def node_loc(node):
    """Vị trí của node trong cây: đường dẫn file, hoặc thư mục nếu node inline."""
    return node["path"] or node["dir"] or ""


def breadcrumbs(nodes):
    by_id = {n["id"]: n for n in nodes}
    out = {}
    for n in nodes:
        crumbs, cur = [], n["parent"]
        while cur and cur in by_id:
            crumbs.append(by_id[cur]["title"])
            cur = by_id[cur]["parent"]
        out[n["id"]] = list(reversed(crumbs))
    return out


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
PIPE_SEP_RE = re.compile(r"^\s*\|[\s|:-]*-{2,}[\s|:-]*\|?\s*$")
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(")

ACTION_WORDS = ("thêm", "sửa", "xoá", "xóa", "tìm kiếm", "lưu", "duyệt",
                "xuất", "nhập", "phê duyệt", "cập nhật", "tra cứu")
PERM_WORDS = ("quyền", "vai trò", "phân quyền", "nhóm người dùng")
FIELD_HEADERS = ("| trường", "| tên trường", "| tham số")


def strip_frontmatter(text):
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 3)
    if end < 0:
        return text
    return text[end + len("\n---\n"):]


def _iter_outside_code(text):
    in_code = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        yield line


def headings_of(text):
    out = []
    for line in _iter_outside_code(text):
        m = HEADING_RE.match(line)
        if m:
            out.append({"level": len(m.group(1)), "text": m.group(2)})
    return out


def head_lines(text, n):
    """`n` dòng đầu phi-rỗng, bỏ heading — đủ để nhận ra mục nói về cái gì."""
    out = []
    for line in _iter_outside_code(text):
        s = line.strip()
        if not s or HEADING_RE.match(line):
            continue
        out.append(s)
        if len(out) >= n:
            break
    return out


def signals_of(text):
    """Đếm cơ học các dấu hiệu 'đây là một màn' — LLM đọc số, không đọc toàn văn."""
    low = text.lower()
    lines = text.split("\n")
    return {
        "tables": low.count("<table") + sum(1 for l in lines if PIPE_SEP_RE.match(l)),
        "table_rows": low.count("<tr") + sum(1 for l in lines if l.lstrip().startswith("|")),
        "images": low.count("<img") + len(MD_IMG_RE.findall(text)),
        "action_words": sum(low.count(w) for w in ACTION_WORDS),
        "permission_words": sum(low.count(w) for w in PERM_WORDS),
        "field_table": any(h in low for h in FIELD_HEADERS),
        "words": len(low.split()),
    }


def tree_diff(brd_dir, nodes):
    """(file .md có trên đĩa mà manifest không khai, node khai mà file đã mất).

    BA sửa tay `docs/brd/` sau khi import là chuyện thường — hai danh sách này là
    cảnh báo, không chặn, nhưng lệnh phải báo ra.
    """
    brd_dir = Path(brd_dir)
    known = {n["path"] for n in nodes if n["path"]}
    on_disk = {str(p.relative_to(brd_dir)).replace("\\", "/")
               for p in brd_dir.rglob("*.md")}
    missing = sorted(p for p in known if not (brd_dir / p).is_file())
    extra = sorted(on_disk - known)
    return extra, missing


def build_outline(brd_dir, head):
    brd_dir = Path(brd_dir)
    nodes = parse_manifest(brd_dir / "brd.manifest.yml")
    crumbs = breadcrumbs(nodes)
    extra, missing = tree_diff(brd_dir, nodes)

    out_nodes = []
    for n in nodes:
        item = {
            "id": n["id"], "order": n["order"], "depth": n["depth"],
            "kind": n["kind"], "title": n["title"], "breadcrumb": crumbs[n["id"]],
            "path": n["path"], "dir": n["dir"], "inline": n["inline"],
            "parent": n["parent"], "chars": n["chars"],
            "headings": [], "head": [], "signals": None,
        }
        f = brd_dir / n["path"] if n["path"] else None
        if f is not None and f.is_file():
            body = strip_frontmatter(f.read_text(encoding="utf-8"))
            item["headings"] = headings_of(body)
            item["head"] = head_lines(body, head)
            item["signals"] = signals_of(body)
        out_nodes.append(item)

    return {
        "brd_dir": str(brd_dir).replace("\\", "/"),
        "node_count": len(out_nodes),
        "files_without_node": extra,
        "nodes_without_file": missing,
        "nodes": out_nodes,
    }


def cmd_outline(args):
    brd_dir = Path(args.brd_dir)
    if not brd_dir.is_dir():
        _die(f"Không thấy thư mục BRD: {brd_dir}")
    result = build_outline(brd_dir, args.head)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                   encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Trích outline cây BRD và gác cổng docs/roadmap.md."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("outline", help="Trích outline gọn từ cây BRD markdown")
    o.add_argument("brd_dir")
    o.add_argument("--out", default=".specify/tmp/roadmap-brd/outline.json")
    o.add_argument("--head", type=int, default=15)
    o.set_defaults(func=cmd_outline)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
