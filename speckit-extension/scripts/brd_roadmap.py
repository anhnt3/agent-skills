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
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        _die(f"{path} không phải UTF-8, không đọc được ({e}).")
    nodes = []
    for line in raw.split("\n"):
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


LINK_RE = re.compile(r"^\[[^\]]*\]\((.+?)\)$")
BIG_NODE_CHARS = 40_000


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
    prefix = brd_rel.replace("\\", "/").rstrip("/") + "/"
    if v.startswith(prefix):
        return v[len(prefix):], anchor
    if v.endswith(".md") or v.endswith("/"):
        return v, anchor
    return None, None


def check_coverage(parsed, nodes, brd_dir, brd_rel, excluded):
    """Mọi node BRD phải hoặc được một item trỏ tới, hoặc nằm trong `excluded` kèm lý do."""
    brd_dir = Path(brd_dir)
    errs, warns = [], []

    by_loc, by_id = {}, {}
    for n in nodes:
        by_id[n["id"]] = n
        if n["kind"] != "root":
            by_loc.setdefault(node_loc(n).rstrip("/"), []).append(n["id"])

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
            errs.append(f"{rid}: **Nguồn** trỏ tới {raw} — không có node BRD nào ở vị trí đó.")
            continue
        nids = by_loc[key]
        for nid in nids:
            covered.setdefault(nid, []).append(rid)
        if anchor:
            f = brd_dir / rel
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

    for n in nodes:
        if n["kind"] == "root" or n["id"] in covered or n["id"] in ex_ids:
            continue
        errs.append(f"Node {n['id']} \"{n['title']}\" ({node_loc(n)}) chưa có item roadmap "
                    f"nào trỏ tới và cũng không nằm trong decisions.json.")

    for nid, rids in covered.items():
        if len(rids) == 1 and by_id[nid]["chars"] > BIG_NODE_CHARS:
            warns.append(f"Node {nid} có {by_id[nid]['chars']} ký tự nhưng chỉ map vào "
                         f"{rids[0]} — nhiều khả năng phải tách.")
    return errs, warns


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

    errs = check_ids(parsed) + check_placeholders(text) + check_deps(parsed)
    cov_errs, cov_warns = check_coverage(parsed, nodes, brd_dir, args.brd_rel, excluded)
    errs += cov_errs
    warns += cov_warns

    report = {
        "ok": not errs,
        "items": len(parsed["rows"]),
        "brd_nodes": sum(1 for n in nodes if n["kind"] != "root"),
        "excluded_nodes": len(excluded),
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
