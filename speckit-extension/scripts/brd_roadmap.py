#!/usr/bin/env python3
"""brd-roadmap — trích outline từ cây BRD markdown và gác cổng docs/roadmap.md.

    manifest <brd-dir> [--write] [--out <yml>]
    outline <brd-dir> [--out <json>] [--head N] [--quiet]
    verify <roadmap.md> --brd <dir> --brd-rel <prefix> [--decisions <json>]
"""

import argparse
import json
import posixpath
import re
import sys
from pathlib import Path, PurePosixPath

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
        _die(f"Không thấy {path} — cây BRD chưa có manifest. Nếu đây là cây .md BA "
             f"viết tay, dựng manifest bằng: brd_roadmap.py manifest <thư-mục-brd> "
             f"(xem báo cáo trước, rồi chạy lại với --write).")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        _die(f"{path} không phải UTF-8, không đọc được ({e}).")
    nodes = []
    for lineno, line in enumerate(raw.split("\n"), start=1):
        m = NODE_RE.match(line)
        if not m:
            continue
        f = _scan_flow(m.group(1))
        parent = f.get("parent")
        try:
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
        except (KeyError, ValueError) as e:
            node_id = f.get("id", "?")
            _die(f"{path} dòng {lineno} (node {node_id}) hỏng, thiếu/sai kiểu trường "
                 f"bắt buộc ({e}) — manifest có thể đã bị sửa tay lỗi.")
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
            try:
                raw_body = f.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                _die(f"{f} không phải UTF-8, không đọc được ({e}).")
            body = strip_frontmatter(raw_body)
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
    if getattr(args, "quiet", False):
        n_nodes = result.get("node_count", len(result.get("nodes", [])))
        n_extra = len(result.get("files_without_node", []))
        n_missing = len(result.get("nodes_without_file", []))
        print(f"Đã trích {n_nodes} node, ghi vào {out} "
              f"(files_without_node: {n_extra}, nodes_without_file: {n_missing}).")
    else:
        print(json.dumps(result, ensure_ascii=False))


# ---------------------------------------------------------------- manifest --
# Cây BRD do BA viết tay không có `brd.manifest.yml`. Lệnh con `manifest` dựng
# nó từ chính cây thư mục: MỖI FILE .md LÀ ĐÚNG MỘT NODE, thư mục chỉ là đường
# dẫn (không sinh node). Không đụng một byte nào của file BA.
#
# Vì sao thư mục không thành node: cây do `brd-import` sinh có node `folder`
# ứng với một mục Word CÓ NỘI DUNG riêng. Thư mục trong cây viết tay thường chỉ
# để gom nhóm, không có nội dung — biến chúng thành node thì mọi thư mục đều
# phải "có item roadmap trỏ tới hoặc bị khai loại kèm lý do", đẻ ra hàng chục
# mục loại trừ giả và làm nổ oan cảnh báo "loại quá nửa số node" trong `verify`.

SKIP_DIR_NAMES = {"media", "__pycache__", "node_modules"}
INDEX_NAMES = ("_index.md", "README.md", "readme.md", "index.md")
ID_RE = re.compile(r"^(.*?)(\d+)$")
ORDER_TOKEN_RE = re.compile(r"(\border:\s*)(\d+)")


def _deslug(stem):
    """`03-mo-ta-chuc-nang` -> `Mo ta chuc nang` — chốt chặn cuối khi file không có heading."""
    s = re.sub(r"^\d+[-_. ]+", "", stem)
    s = s.replace("_", " ").replace("-", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return (s[:1].upper() + s[1:]) if s else stem


def _walk_md(d, out):
    """Duyệt cây theo thứ tự tài liệu: file index trước, rồi file thường, rồi thư mục con."""
    try:
        entries = sorted(d.iterdir(), key=lambda p: p.name.lower())
    except OSError as e:
        _die(f"Không đọc được thư mục {d} ({e}).")
    files = [p for p in entries
             if p.is_file() and p.suffix.lower() == ".md" and not p.name.startswith(".")]
    idx = [p for p in files if p.name in INDEX_NAMES]
    out.extend(idx)
    out.extend(p for p in files if p.name not in INDEX_NAMES)
    for sd in entries:
        if sd.is_dir() and sd.name not in SKIP_DIR_NAMES and not sd.name.startswith("."):
            _walk_md(sd, out)


FM_TITLE_RE = re.compile(r'^title:\s*"?(.+?)"?\s*$', re.MULTILINE)


def _title_of(path, text):
    # `title:` trong frontmatter là tên do người/`brd-import` đặt -> ưu tiên nhất.
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end > 0:
            m = FM_TITLE_RE.search(text[4:end])
            if m and m.group(1).strip():
                return m.group(1).strip()
    for h in headings_of(strip_frontmatter(text)):
        if h["text"].strip():
            return h["text"].strip()
    return _deslug(path.stem)


def scan_tree(brd_dir):
    """Cây .md -> danh sách node theo thứ tự tài liệu (chưa cấp id)."""
    brd_dir = Path(brd_dir)
    files = []
    _walk_md(brd_dir, files)
    if not files:
        _die(f"Không thấy file .md nào trong {brd_dir} — đây không phải cây BRD markdown.")

    # Thư mục nào có file index thì file đó là node đại diện, làm cha của mọi
    # node bên dưới. Thư mục không có index -> cha là node index của tổ tiên gần nhất.
    index_of_dir = {}
    for p in files:
        if p.name in INDEX_NAMES:
            index_of_dir.setdefault(p.parent, p)

    nodes = []
    for p in files:
        rel = p.relative_to(brd_dir).as_posix()
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            _die(f"{p} không phải UTF-8, không đọc được ({e}).")
        # Duyệt lên theo CÁC TỔ TIÊN TRONG brd_dir. Không dùng vòng `while` bám
        # `cur.parent`: file index ở gốc có `start` nằm ngoài brd_dir, `cur` không
        # bao giờ chạm brd_dir và `Path('.').parent == Path('.')` -> lặp vô hạn.
        rel_dirs = list(Path(rel).parents)          # [.., '.']  — trong brd_dir
        if p.name in INDEX_NAMES:
            rel_dirs = rel_dirs[1:]                 # index không nhận chính thư mục nó làm cha
        parent_file = None
        for rd in rel_dirs:
            parent_file = index_of_dir.get(brd_dir / rd if str(rd) != "." else brd_dir)
            if parent_file is not None:
                break
        is_root = p.name in INDEX_NAMES and p.parent == brd_dir
        nodes.append({
            "depth": len(Path(rel).parts) - 1,
            "kind": "root" if is_root else "leaf",
            "title": _title_of(p, text),
            "path": rel,
            "dir": None,
            "inline": False,
            "parent_path": None if parent_file is None else parent_file.relative_to(brd_dir).as_posix(),
            "chars": len(text),
        })
    return nodes


def _yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_node_line(n):
    parts = [f"id: {n['id']}", f"order: {n['order']}", f"depth: {n['depth']}",
             f"kind: {n['kind']}", f"title: {_yaml_str(n['title'])}"]
    if n.get("path"):
        parts.append(f"path: {_yaml_str(n['path'])}")
    else:
        parts.append("inline: true")
        parts.append(f"dir: {_yaml_str(n.get('dir') or '')}")
    parts.append(f"parent: {n['parent'] or 'null'}")
    parts.append(f"chars: {n['chars']}")
    return "  - { " + ", ".join(parts) + " }"


def _next_id_factory(existing_ids):
    """Cấp id mới nối tiếp id lớn nhất đang có; KHÔNG tái dùng id của node đã gỡ."""
    prefix, width, biggest = "BRD-", 4, -1
    for i in existing_ids:
        m = ID_RE.match(i)
        if m:
            prefix, width = m.group(1), max(width, len(m.group(2)))
            biggest = max(biggest, int(m.group(2)))
    counter = {"n": biggest}

    def nxt():
        counter["n"] += 1
        return f"{prefix}{counter['n']:0{width}d}"
    return nxt


def build_manifest(brd_dir, old_path):
    """Trả (danh sách dòng node, báo cáo). Có manifest cũ thì HOÀ GIẢI, không sinh lại.

    Node còn khớp `path` giữ nguyên **id và cả dòng gốc** (chỉ đánh lại `order`) —
    id ổn định là điều kiện để `decisions.json` và trường `Nguồn` của roadmap cũ
    không trỏ sai. Node của bản import cũ có `dir` (không ứng file .md nào) cũng
    giữ nguyên, để cây do `brd-import` sinh vẫn chạy đúng như trước.
    """
    scanned = scan_tree(brd_dir)
    old_path = Path(old_path)
    old_nodes, old_lines = [], {}
    if old_path.is_file():
        old_nodes = parse_manifest(old_path)
        raw = old_path.read_text(encoding="utf-8")
        for line in raw.split("\n"):
            m = NODE_RE.match(line)
            if m:
                f = _scan_flow(m.group(1))
                old_lines[f["id"]] = line

    by_path = {n["path"]: n for n in old_nodes if n["path"]}
    nxt = _next_id_factory([n["id"] for n in old_nodes])

    added, kept = [], []
    for n in scanned:
        old = by_path.get(n["path"])
        if old:
            n["id"] = old["id"]
            kept.append(n["path"])
        else:
            n["id"] = nxt()
            added.append(n["path"])
    id_by_path = {n["path"]: n["id"] for n in scanned}
    for n in scanned:
        n["parent"] = id_by_path.get(n["parent_path"])

    # Node cũ kiểu thư mục (`dir`, không có `path`): giữ nếu thư mục còn trên đĩa.
    brd = Path(brd_dir)
    dir_nodes, removed = [], []
    for o in old_nodes:
        if o["path"]:
            if o["path"] not in id_by_path:
                removed.append({"id": o["id"], "path": o["path"]})
            continue
        loc = (o["dir"] or "").rstrip("/")
        if loc and (brd / loc).is_dir():
            dir_nodes.append(o)
        else:
            removed.append({"id": o["id"], "dir": o["dir"]})

    # Thứ tự: node đã có trong manifest giữ ĐÚNG vị trí cũ (thứ tự tài liệu của
    # bản import là thông tin thật, không được xáo); node mới chèn ngay sau node
    # cũ gần nhất đứng trước nó trong cây. `order` đánh lại tuần tự sau cùng.
    old_order = {o["id"]: o["order"] for o in old_nodes}
    keyed, last_seen, tie = [], -1, 0
    for n in dir_nodes + scanned:
        if n["id"] in old_order:
            last_seen, tie = old_order[n["id"]], 0
            keyed.append(((last_seen, 0, 0), n))
        else:
            tie += 1
            keyed.append(((last_seen, 1, tie), n))
    keyed.sort(key=lambda t: t[0])
    ordered = [n for _, n in keyed]

    lines = []
    for i, n in enumerate(ordered):
        n["order"] = i
        raw_line = old_lines.get(n["id"])
        reuse = raw_line is not None and (not n.get("path") or n["path"] in kept)
        if reuse:
            lines.append(ORDER_TOKEN_RE.sub(lambda m: m.group(1) + str(i), raw_line, count=1))
        else:
            lines.append(render_node_line(n))

    warnings = []
    if removed:
        warnings.append(f"{len(removed)} node trong manifest cũ không còn trên đĩa — đã gỡ.")
    if any(n["kind"] == "root" for n in scanned) is False:
        warnings.append("Cây không có file index ở gốc (_index.md/README.md) — "
                        "không có node gốc, mọi file đều tính vào phủ coverage.")
    report = {
        "brd_dir": str(brd_dir).replace("\\", "/"),
        "total": len(ordered),
        "kept": len(kept) + len(dir_nodes),
        "added": added,
        "removed": removed,
        "warnings": warnings,
        "nodes": [{"id": n["id"], "kind": n["kind"], "title": n["title"],
                   "loc": n.get("path") or n.get("dir"), "chars": n["chars"]}
                  for n in ordered],
    }
    return lines, report


HEADER_DEFAULT = ('schema_version: "1.0"\n'
                  'source: { kind: handmade, note: "manifest dựng từ cây .md có sẵn, '
                  'không import từ .docx" }\n')


def cmd_manifest(args):
    brd_dir = Path(args.brd_dir)
    if not brd_dir.is_dir():
        _die(f"Không thấy thư mục BRD: {brd_dir}")
    out = Path(args.out) if args.out else brd_dir / "brd.manifest.yml"
    lines, report = build_manifest(brd_dir, out)

    header = HEADER_DEFAULT
    if out.is_file():
        raw = out.read_text(encoding="utf-8")
        i = raw.find("\nnodes:")
        head = raw[:i + 1] if i >= 0 else (raw if raw.endswith("\n") else raw + "\n")
        header = head
    content = header + "nodes:\n" + "\n".join(lines) + "\n"

    report["written"] = None
    if args.write:
        out.write_text(content, encoding="utf-8", newline="\n")
        report["written"] = str(out).replace("\\", "/")
    print(json.dumps(report, ensure_ascii=False, indent=2))


# Ô ID trong bảng tổng là LINK tới nguồn: `| [RM-001](docs/brd/…md#heading) |`.
# Vẫn nhận dạng trần `| RM-001 |` để roadmap viết trước khi đổi khuôn không gãy.
ROW_RE = re.compile(r"^\|\s*(?:\[\s*)?(RM-\d{3})\s*(?:\]\(([^)\n]*)\))?\s*\|(.*)$")
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
            cells = [c.strip() for c in m.group(3).split("|")]
            cells += [""] * (5 - len(cells))
            rows.setdefault(rid, {
                "man": cells[0], "module": cells[1], "wave": cells[2],
                "deps_raw": cells[3], "trang_thai": cells[4],
                "id_link": (m.group(2) or "").strip(),
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


LINK_RE = re.compile(r"^\[[^\]]*\]\((.+?)\)$")
BIG_NODE_CHARS = 40_000
MANY_HEADINGS = 5
BOILERPLATE_MIN_FILES = 3


def slugify_anchor(text):
    """Thường hoá, bỏ ký tự không phải chữ/số, khoảng trắng -> gạch.

    Đây KHÔNG phải slug GFM chính xác (GFM đổi mỗi khoảng trắng thành một gạch
    riêng, không gộp chuỗi khoảng trắng liên tiếp thành một gạch) — dùng
    `_norm_hyphens` khi so khớp để dung hoà khác biệt đó.
    """
    s = text.strip().lower()
    s = "".join(ch for ch in s if ch.isalnum() or ch in " -_")
    return re.sub(r"\s+", "-", s.strip())


def _norm_hyphens(s):
    """Gộp các chuỗi gạch nối liên tiếp thành một — để so khớp anchor khoan dung.

    Anchor GFM thật (lấy từ URL trên GitHub) có thể có nhiều gạch liên tiếp
    khi tên gốc có nhiều khoảng trắng hoặc dấu câu liền nhau; `slugify_anchor`
    gộp khoảng trắng nên hai chuỗi đó lệch nhau dù cùng trỏ một heading.
    """
    return re.sub(r"-{2,}", "-", s)


def resolve_link(link, roadmap_path):
    """Link markdown -> đường dẫn tương đối GỐC REPO.

    Link trong markdown resolve theo thư mục chứa file, còn `**Nguồn**` viết
    tương đối gốc repo. Hai hệ quy chiếu khác nhau: roadmap ở `docs/roadmap.md`
    thì link bấm được là `brd/…`, trong khi `Nguồn` là `docs/brd/…`. So sánh
    thẳng hai chuỗi sẽ ép người viết dùng `docs/brd/…` làm link — bấm vào ra
    `docs/docs/brd/…`, 404. Phải quy link về cùng hệ với `Nguồn` trước khi so.
    """
    v = (link or "").strip()
    if not v or "://" in v or v.startswith("/"):
        return v
    anchor = ""
    if "#" in v:
        v, anchor = v.split("#", 1)
        anchor = "#" + anchor
    base = PurePosixPath(str(roadmap_path).replace("\\", "/")).parent
    joined = posixpath.normpath(str(base / v.replace("\\", "/")))
    if joined.startswith("./"):
        joined = joined[2:]
    if v.endswith("/") and not joined.endswith("/"):
        joined += "/"
    return joined + anchor


def resolve_link_suggestion(nguon, roadmap_path):
    """Nghịch đảo `resolve_link`: `**Nguồn**` (gốc repo) -> link viết từ chỗ roadmap đứng."""
    v = (nguon or "").strip().strip("`").strip()
    m = LINK_RE.match(v)
    if m:
        v = m.group(1).strip()
    v = v.replace("\\", "/")
    base = PurePosixPath(str(roadmap_path).replace("\\", "/")).parent
    base_s = "" if str(base) in (".", "") else str(base).rstrip("/") + "/"
    return v[len(base_s):] if base_s and v.startswith(base_s) else v


def norm_source(raw, brd_rel):
    """Giá trị `**Nguồn**` -> (đường dẫn tương đối brd_dir, anchor).

    Trả (None, None) khi giá trị không trỏ vào cây BRD (đường dẫn code, `N/A`).
    """
    v = (raw or "").strip().strip("`").strip()
    m = LINK_RE.match(v)
    if m:
        v = m.group(1).strip()
    v = v.replace("\\", "/")
    anchor = None
    if "#" in v:
        v, anchor = v.split("#", 1)
        anchor = anchor.strip() or None
    v = v.strip()
    norm_rel = brd_rel.replace("\\", "/").strip()
    while norm_rel.startswith("./"):
        norm_rel = norm_rel[2:]
    prefix = norm_rel.rstrip("/") + "/"
    if v.startswith(prefix):
        return v[len(prefix):], anchor
    if v.endswith(".md") or v.endswith("/"):
        return v, anchor
    return None, None


def check_coverage(parsed, nodes, brd_dir, brd_rel, excluded):
    """Mọi node BRD phải hoặc được một item trỏ tới, hoặc nằm trong `excluded` kèm lý do.

    Trả về (errs, warns, ex_ids) — `ex_ids` là tập node_id thực sự được chấp nhận loại
    (đã qua mọi kiểm tra định dạng), dùng để báo cáo số lượng loại trừ thật, không phải
    số phần tử thô trong `excluded` (có thể chứa phần tử hỏng bị `check_coverage` bác).
    """
    brd_dir = Path(brd_dir)
    errs, warns = [], []

    by_loc, by_id = {}, {}
    root_locs = set()
    for n in nodes:
        by_id[n["id"]] = n
        if n["kind"] != "root":
            by_loc.setdefault(node_loc(n).rstrip("/"), []).append(n["id"])
        else:
            root_locs.add(node_loc(n).rstrip("/"))

    covered = {}
    for rid in parsed["row_order"]:
        raw = parsed["details"].get(rid, {}).get("Nguồn")
        if not raw:
            warns.append(f"{rid} không có trường **Nguồn** — không truy vết được về BRD.")
            continue
        rel, anchor = norm_source(raw, brd_rel)
        if rel is None:
            # Giá trị hợp lệ và cố ý không trỏ vào BRD (đường dẫn code, N/A) thì
            # im lặng — mẫu roadmap-template cho phép field này nhận cả hai dạng.
            # Chuẩn hoá giống norm_source (bỏ backtick, mở link markdown) trước khi
            # so "n/a" — nếu không, `N/A` viết có backtick/dạng link sẽ bị báo oan.
            v = raw.strip().strip("`").strip()
            m = LINK_RE.match(v)
            if m:
                v = m.group(1).strip()
            if v.strip().lower() != "n/a":
                warns.append(f"{rid}: **Nguồn** = {raw} — không trỏ vào cây BRD, "
                             f"không truy vết được (nếu cố ý thì bỏ qua cảnh báo này).")
            continue
        key = rel.rstrip("/")
        if key not in by_loc:
            if key in root_locs:
                errs.append(f"{rid}: **Nguồn** trỏ tới {raw} — đó là phần đầu tài liệu "
                            f"(node gốc), node gốc không tính vào phủ coverage, hãy trỏ tới "
                            f"node BRD thật (màn/mục) mà mục này mô tả.")
            elif (brd_dir / key).is_file():
                errs.append(f"{rid}: **Nguồn** trỏ tới {raw} — file có trên đĩa nhưng "
                            f"manifest không khai node nào ở đó (BA thêm tay sau import). "
                            f"Chạy `brd_roadmap.py manifest <thư-mục-brd> --write` để manifest "
                            f"biết file này, đừng trỏ **Nguồn** vào file ngoài manifest.")
            else:
                errs.append(f"{rid}: **Nguồn** trỏ tới {raw} — không có node BRD nào ở vị trí đó.")
            continue
        nids = by_loc[key]
        for nid in nids:
            covered.setdefault(nid, []).append(rid)
        if anchor:
            f = brd_dir / rel
            if f.is_dir():
                # Node `inline` không có file riêng -> `Nguồn` trỏ vào thư mục. Anchor ở
                # đây chỉ để phân biệt nhiều item cùng trỏ một node, không có file nào để
                # đối chiếu heading -> chấp nhận, không chấm. Không được báo lỗi: command
                # bảo dùng `#<tiêu đề mục>` cho đúng trường hợp này.
                continue
            if not f.is_file():
                errs.append(f"{rid}: **Nguồn** có anchor nhưng {rel} không phải file.")
                continue
            try:
                raw_body = f.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                _die(f"{f} không phải UTF-8, không đọc được ({e}).")
            hs = headings_of(strip_frontmatter(raw_body))
            anchor_slug = _norm_hyphens(slugify_anchor(anchor))
            found = any(h["text"].strip().lower() == anchor.lower()
                        or _norm_hyphens(slugify_anchor(h["text"])) == anchor_slug
                        for h in hs)
            if not found:
                errs.append(f"{rid}: anchor #{anchor} không khớp heading nào trong {rel}.")

    ex_ids = set()
    for e in excluded:
        if not isinstance(e, dict):
            errs.append(f"decisions.json có phần tử loại node sai định dạng: {e!r} — "
                        f"phải là object dạng {{\"node_id\": ..., \"title\": ..., \"reason\": ...}}.")
            continue
        raw_nid = e.get("node_id")
        if raw_nid is not None and not isinstance(raw_nid, str):
            errs.append(f"decisions.json có \"node_id\" sai kiểu (phải là chuỗi): {raw_nid!r}.")
            continue
        raw_reason = e.get("reason")
        if raw_reason is not None and not isinstance(raw_reason, str):
            errs.append(f"decisions.json có \"reason\" sai kiểu (phải là chuỗi): {raw_reason!r}.")
            continue
        nid = (raw_nid or "").strip()
        if not nid:
            errs.append("decisions.json có phần tử loại node thiếu \"node_id\".")
            continue
        if nid not in by_id:
            errs.append(f"decisions.json loại node {nid} không có trong manifest.")
            continue
        if not (raw_reason or "").strip():
            errs.append(f"decisions.json loại node {nid} nhưng bỏ trống lý do.")
            continue
        ex_ids.add(nid)
        if nid in covered:
            warns.append(f"{nid} vừa bị loại trong decisions.json vừa được "
                         f"{', '.join(covered[nid])} trỏ tới — mâu thuẫn.")

    # Loại node là cửa thoát rẻ nhất: `reason` không rỗng là qua. Hai cảnh báo dưới
    # không chặn nhưng buộc con số lộ ra, để loại hàng loạt bằng một nhãn chung
    # không trôi im lặng qua gate.
    n_real = sum(1 for n in nodes if n["kind"] != "root")
    if n_real and len(ex_ids) * 2 > n_real:
        warns.append(f"Loại {len(ex_ids)}/{n_real} node BRD (quá nửa) — kiểm lại: loại "
                     f"hàng loạt thường là dấu hiệu bỏ sót màn, không phải BRD toàn mục "
                     f"phi chức năng.")
    reason_count = {}
    for e in excluded:
        nid = e.get("node_id") if isinstance(e, dict) else None
        if isinstance(nid, str) and nid.strip() in ex_ids:
            r = " ".join((e.get("reason") or "").split()).lower()
            reason_count[r] = reason_count.get(r, 0) + 1
    for r, c in sorted(reason_count.items()):
        if c >= 3:
            warns.append(f"{c} node bị loại với cùng một lý do \"{r}\" — lý do phải gắn "
                         f"vào nội dung từng node, không phải nhãn chung dán hàng loạt.")

    for n in nodes:
        if n["kind"] == "root" or n["id"] in covered or n["id"] in ex_ids:
            continue
        errs.append(f"Node {n['id']} \"{n['title']}\" ({node_loc(n)}) chưa có item roadmap "
                    f"nào trỏ tới và cũng không nằm trong decisions.json.")

    # Một file = một node (mô hình phủ theo vị trí) nên file chứa nhiều màn vẫn
    # "phủ đủ" chỉ với một item. Đếm heading cấp 2 là mỏ neo rẻ để lộ chỗ đó —
    # NHƯNG đếm trần thì bắt nhầm: BRD thường có bộ mục chuẩn lặp ở mọi màn
    # ("Đối tượng tham gia", "Điều kiện thực hiện", "Thiết kế UX/UI"…), file nào
    # cũng 8 mục cấp 2 mà vẫn chỉ là MỘT màn. Nên chỉ đếm heading ĐẶC THÙ: tiêu
    # đề xuất hiện ở ≥3 file khác nhau là khuôn tài liệu, không phải tên màn.
    single = {nid: rids[0] for nid, rids in covered.items() if len(rids) == 1}
    h2_of, freq = {}, {}
    for nid in single:
        n = by_id[nid]
        f = brd_dir / n["path"] if n["path"] else None
        if f is None or not f.is_file():
            continue
        try:
            body = strip_frontmatter(f.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
        hs = [h["text"].strip().lower() for h in headings_of(body) if h["level"] == 2]
        h2_of[nid] = hs
        for t in set(hs):
            freq[t] = freq.get(t, 0) + 1
    boilerplate = {t for t, c in freq.items() if c >= BOILERPLATE_MIN_FILES}

    for nid, rid in single.items():
        n = by_id[nid]
        if n["chars"] > BIG_NODE_CHARS:
            warns.append(f"Node {nid} có {n['chars']} ký tự nhưng chỉ map vào "
                         f"{rid} — nhiều khả năng phải tách.")
            continue
        rieng = [t for t in h2_of.get(nid, []) if t not in boilerplate]
        if len(rieng) >= MANY_HEADINGS:
            warns.append(f"Node {nid} có {len(rieng)} mục cấp 2 riêng (không thuộc bộ mục "
                         f"chuẩn của tài liệu) nhưng chỉ map vào {rid} — file này nhiều "
                         f"khả năng chứa nhiều màn, cân nhắc tách item.")
    return errs, warns, ex_ids


# `\d+` (không phải `\d{3}` cố định) + `(?<!\d)`/`(?!\d)`: nuốt trọn cả chuỗi
# số, không dừng ở 3 chữ số đầu — để `RM-0012` khớp thành đúng token "RM-0012"
# (rồi bị `check_deps` báo là ID không tồn tại, vì `parsed["rows"]` chỉ có ID
# đúng 3 chữ số) thay vì bị cắt nhầm thành `RM-001` của một item khác có thật.
RM_RE = re.compile(r"(?<!\d)RM-\d+(?!\d)")


def check_deps(parsed):
    """Gác cổng cột Phụ thuộc/Wave: ID không tồn tại, chu trình (kể cả tự trỏ), wave nghịch."""
    errs = []
    waves, deps = {}, {}
    for rid, row in parsed["rows"].items():
        raw = (row["wave"] or "").strip()
        try:
            waves[rid] = int(raw)
        except ValueError:
            errs.append(f"{rid}: Wave \"{raw}\" không phải số.")
        # Không lọc bỏ tự trỏ (d == rid): một item phụ thuộc chính nó là chu
        # trình độ dài 1, phải để DFS bên dưới bắt được, không được im lặng bỏ qua.
        deps[rid] = RM_RE.findall(row["deps_raw"] or "")

    for rid, ds in deps.items():
        for d in ds:
            if d not in parsed["rows"]:
                errs.append(f"{rid} phụ thuộc {d} nhưng không có item nào mang ID đó.")
            elif rid in waves and d in waves and waves[rid] < waves[d]:
                errs.append(f"{rid} ở Wave {waves[rid]} nhưng phụ thuộc {d} ở Wave "
                            f"{waves[d]} — không build được theo thứ tự này.")

    # Chu trình: DFS lặp (không đệ quy — chuỗi phụ thuộc dài không được làm tràn
    # ngăn xếp gọi hàm) màu trắng/xám/đen, báo đúng một lần mỗi cạnh quay lui.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {rid: WHITE for rid in parsed["row_order"]}

    for root in parsed["row_order"]:
        if color[root] != WHITE:
            continue
        # Mỗi khung: (node, đường-đi-tới-node, chỉ-số-cạnh-kế-tiếp-cần-xét).
        stack = [[root, [root], 0]]
        color[root] = GRAY
        while stack:
            frame = stack[-1]
            node, path, i = frame
            children = deps.get(node, [])
            if i >= len(children):
                color[node] = BLACK
                stack.pop()
                continue
            frame[2] += 1
            nxt = children[i]
            if nxt not in parsed["rows"]:
                continue
            if color.get(nxt) == GRAY:
                cycle = path[path.index(nxt):] + [nxt]
                errs.append("Phụ thuộc có chu trình: " + " -> ".join(cycle))
            elif color.get(nxt, WHITE) == WHITE:
                color[nxt] = GRAY
                stack.append([nxt, path + [nxt], 0])
    return sorted(set(errs))


def cmd_verify(args):
    """Lệnh con `verify`: đọc roadmap + cây BRD, in báo cáo JSON, exit 1 nếu có lỗi nội dung."""
    roadmap = Path(args.roadmap)
    if not roadmap.is_file():
        _die(f"Không thấy file roadmap: {roadmap}")
    brd_dir = Path(args.brd)
    if not brd_dir.is_dir():
        _die(f"Không thấy thư mục BRD: {brd_dir}")

    try:
        text = roadmap.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        _die(f"{roadmap} không phải UTF-8, không đọc được ({e}).")
    parsed = parse_roadmap(text)
    nodes = parse_manifest(brd_dir / "brd.manifest.yml")

    warns, excluded = [], []
    dec = Path(args.decisions)
    if dec.is_file():
        try:
            dec_text = dec.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            _die(f"{dec} không phải UTF-8, không đọc được ({e}).")
        try:
            dec_data = json.loads(dec_text)
        except json.JSONDecodeError as e:
            _die(f"{dec} hỏng, không đọc được JSON ({e}).")
        if not isinstance(dec_data, dict):
            _die(f"{dec} sai định dạng: cấp cao nhất phải là object "
                 f"(vd {{\"excluded\": [...]}}), không phải {type(dec_data).__name__}.")
        excluded = dec_data.get("excluded", [])
    else:
        warns.append(f"Không thấy {dec} — coi như chưa loại node nào (decisions rỗng).")

    # Ô ID là link bấm-vào-mở-nguồn. Link trỏ khác **Nguồn** thì người đọc bấm vào
    # rơi sai chỗ, mà mọi gate phủ lại chấm theo **Nguồn** nên không ai phát hiện.
    for rid in parsed["row_order"]:
        row = parsed["rows"].get(rid, {})
        link = (row.get("id_link") or "").strip()
        nguon = parsed["details"].get(rid, {}).get("Nguồn")
        n_rel, n_anc = norm_source(nguon, args.brd_rel) if nguon else (None, None)
        if not link:
            # Chỉ nhắc khi có đích thật để trỏ tới; `Nguồn` = N/A thì text trần là đúng.
            if n_rel is not None:
                goi_y = resolve_link_suggestion(nguon, roadmap)
                warns.append(f"{rid}: ô ID trong bảng tổng chưa phải link — nên là "
                             f"`[{rid}]({goi_y})` để bấm vào mở thẳng nguồn.")
            continue
        if not nguon:
            continue
        l_rel, l_anc = norm_source(resolve_link(link, roadmap), args.brd_rel)
        if (l_rel, l_anc) != (n_rel, n_anc):
            rm_hien = str(roadmap).replace("\\", "/")
            warns.append(f"{rid}: link ở ô ID trỏ {link} (tính từ {rm_hien} ra "
                         f"{resolve_link(link, roadmap)}) nhưng **Nguồn** là {nguon} — "
                         f"hai chỗ phải cùng một đích; link đúng là "
                         f"`{resolve_link_suggestion(nguon, roadmap)}`.")

    # Roadmap do lệnh này sinh ra là roadmap mới -> mọi item phải ở `chưa`. Giá trị
    # khác gần như luôn là model tự suy từ codebase, đúng thứ nguyên tắc lõi cấm.
    for rid in parsed["row_order"]:
        st = (parsed["rows"].get(rid, {}).get("trang_thai") or "").strip().lower()
        if st and st != "chưa":
            warns.append(f"{rid}: Trạng thái = \"{st}\" — roadmap mới sinh phải để "
                         f"`chưa`; trạng thái không được suy từ codebase.")

    errs = check_ids(parsed) + check_placeholders(text) + check_deps(parsed)
    cov_errs, cov_warns, ex_ids = check_coverage(parsed, nodes, brd_dir, args.brd_rel, excluded)
    errs += cov_errs
    warns += cov_warns

    report = {
        "ok": not errs,
        "items": len(parsed["rows"]),
        "brd_nodes": sum(1 for n in nodes if n["kind"] != "root"),
        "excluded_nodes": len(ex_ids),
        "errors": errs,
        "warnings": warns,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errs:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Trích outline cây BRD và gác cổng docs/roadmap.md."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("manifest",
                       help="Dựng/hoà giải brd.manifest.yml từ cây .md có sẵn")
    m.add_argument("brd_dir")
    m.add_argument("--write", action="store_true",
                   help="Thực sự ghi file (mặc định chỉ in báo cáo, KHÔNG ghi gì)")
    m.add_argument("--out", default=None,
                   help="Đường dẫn manifest (mặc định <brd-dir>/brd.manifest.yml)")
    m.set_defaults(func=cmd_manifest)

    o = sub.add_parser("outline", help="Trích outline gọn từ cây BRD markdown")
    o.add_argument("brd_dir")
    o.add_argument("--out", default=".specify/tmp/roadmap-brd/outline.json")
    o.add_argument("--head", type=int, default=15)
    o.add_argument("--quiet", action="store_true",
                   help="Chỉ in một dòng tóm tắt ra stdout thay vì toàn bộ outline JSON "
                        "(file --out vẫn ghi đầy đủ như bình thường)")
    o.set_defaults(func=cmd_outline)

    v = sub.add_parser("verify", help="Chấm docs/roadmap.md so với cây BRD")
    v.add_argument("roadmap")
    v.add_argument("--brd", required=True)
    v.add_argument("--brd-rel", default="docs/brd",
                   help="Tiền tố đường dẫn dùng trong trường **Nguồn** của roadmap")
    v.add_argument("--decisions", default=".specify/tmp/roadmap-brd/decisions.json")
    v.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
