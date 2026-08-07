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


def _iter_outside_code_numbered(text):
    """Như `_iter_outside_code` nhưng kèm số dòng gốc (1-based) của mỗi dòng yield.

    Dùng khi cần báo lỗi trỏ đúng vị trí trong file gốc — `_iter_outside_code`
    không giữ số dòng vì các hàm dùng nó trước đây không cần.
    """
    in_code = False
    for i, line in enumerate(text.split("\n"), start=1):
        if FENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        yield i, line


def _iter_outside_code(text):
    for _, line in _iter_outside_code_numbered(text):
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


ROW_RE = re.compile(r"^\|\s*(RM-\d{3})\s*\|(.*)$")
DETAIL_RE = re.compile(r"^###\s+(RM-\d{3})\b")
FIELD_RE = re.compile(r"^\s*-\s*\*\*(.+?)\*\*\s*:\s*(.*)$")
# Placeholder = span trong ngoặc vuông KHÔNG phải link markdown (`](`). Bản thân
# regex này KHÔNG loại trừ checkbox task-list (`[ ]`, `[x]`) — việc đó do
# `check_placeholders` xử lý riêng bằng CHECKBOX_RE trước khi áp regex này,
# vì checkbox chỉ nằm ở đầu dòng còn placeholder ngoặc vuông trần thật có thể
# nằm bất cứ đâu trên dòng. Nội dung đã điền thật gần như không bao giờ còn
# ngoặc vuông trần.
BRACKET_RE = re.compile(r"\[[^\]\n]{1,120}\](?!\()")
# Checkbox task-list ở đầu dòng: `- [ ]`, `* [x]`, `+ [X]`, thụt lề tuỳ ý.
CHECKBOX_RE = re.compile(r"^(\s*[-*+]\s*)\[[ xX]\](.*)$")


def parse_roadmap(text):
    rows, row_order, details, detail_order = {}, [], {}, []
    cur = None
    for line in text.split("\n"):
        m = ROW_RE.match(line)
        if m:
            rid = m.group(1)
            cells = [c.strip() for c in m.group(2).split("|")]
            cells += [""] * (5 - len(cells))
            rows.setdefault(rid, {
                "man": cells[0], "module": cells[1], "wave": cells[2],
                "deps_raw": cells[3], "trang_thai": cells[4],
            })
            row_order.append(rid)
            continue
        d = DETAIL_RE.match(line)
        if d:
            cur = d.group(1)
            details.setdefault(cur, {})
            detail_order.append(cur)
            continue
        if cur:
            f = FIELD_RE.match(line)
            if f:
                details[cur].setdefault(f.group(1).strip(), f.group(2).strip())
    return {"rows": rows, "row_order": row_order,
            "details": details, "detail_order": detail_order}


def _dups(seq):
    seen, dup = set(), []
    for x in seq:
        if x in seen and x not in dup:
            dup.append(x)
        seen.add(x)
    return dup


def check_ids(parsed):
    errs = []
    for rid in _dups(parsed["row_order"]):
        errs.append(f"ID {rid} trùng trong bảng tổng.")
    for rid in _dups(parsed["detail_order"]):
        errs.append(f"ID {rid} trùng ở khối chi tiết.")
    for rid in parsed["row_order"]:
        if rid not in parsed["details"]:
            errs.append(f"{rid} có trong bảng tổng nhưng thiếu khối chi tiết.")
    for rid in parsed["detail_order"]:
        if rid not in parsed["rows"]:
            errs.append(f"{rid} có khối chi tiết nhưng thiếu dòng trong bảng tổng.")
    return sorted(set(errs))


def check_placeholders(text):
    errs = []
    for i, line in _iter_outside_code_numbered(text):
        if line.lstrip().startswith("<!--"):
            continue
        cb = CHECKBOX_RE.match(line)
        # Bỏ phần checkbox `- [ ]`/`- [x]` ở đầu dòng trước khi quét placeholder,
        # nhưng vẫn quét phần còn lại của dòng — checkbox có thể đi kèm placeholder
        # thật, ví dụ "- [ ] chuyển sang [module]".
        scan = cb.group(2) if cb else line
        for hit in BRACKET_RE.findall(scan):
            errs.append(f"Dòng {i}: còn placeholder chưa điền {hit}")
    return errs


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
