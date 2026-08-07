"""Dựng danh sách node vật chất hoá và cắt file markdown trung gian thành cây."""

from pathlib import Path

from .naming import slugify
from .outline import HEADING_RE, segment_ends

MEDIA_SRC = "](./media/media/"


class SplitError(Exception):
    pass


def rel_media_prefix(path):
    """Số bậc '../' để từ file đó trỏ về thư mục media/ ở gốc."""
    return "../" * (len(Path(path).parts) - 1)


def plan_nodes(headings, dmap, cut_depth, total_lines):
    """Node vật chất hoá, theo thứ tự tài liệu. Phần tử đầu là node gốc, TRỪ KHI
    heading vật chất hoá đầu tiên đã nằm ở dòng 0 (không có phần đầu tài liệu)."""
    mat = [h for h in headings if dmap[h["level"]] <= cut_depth]
    first_line = mat[0]["line"] if mat else total_lines
    nodes = []
    if first_line > 0:
        nodes.append({
            "id": "BRD-0000", "order": 0, "depth": 0, "word_level": 0, "kind": "root",
            "title": "(phần đầu tài liệu)", "path": "_index.md", "dir": "",
            "parent": None, "start": 0, "end": first_line,
        })

    stack = []          # node folder đang mở, theo depth tăng dần
    counters = {}       # path thư mục cha -> số con đã cấp
    for order, h in enumerate(mat, start=1):
        depth = dmap[h["level"]]
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()
        parent = stack[-1] if stack else None
        base = parent["dir"] if parent else ""
        counters[base] = counters.get(base, 0) + 1
        name = f'{counters[base]:02d}-{slugify(h["title"])}'
        kind = "leaf" if depth == cut_depth else "folder"
        node = {
            "id": f"BRD-{order:04d}", "order": order, "depth": depth,
            "word_level": h["level"], "kind": kind, "title": h["title"],
            "dir": f"{base}{name}/" if kind == "folder" else base,
            "path": f"{base}{name}/_index.md" if kind == "folder" else f"{base}{name}.md",
            "parent": parent["id"] if parent else None,
            "start": h["line"], "end": None,
        }
        nodes.append(node)
        if kind == "folder":
            stack.append(node)

    # Segment của MỌI node kết thúc ở node vật chất hoá kế tiếp. Nhờ vậy các
    # segment nối liền nhau, phủ kín file, không hở không chồng -> ghép ngược khớp.
    for i, node in enumerate(nodes):
        node["end"] = nodes[i + 1]["start"] if i + 1 < len(nodes) else total_lines
    return nodes


def frontmatter_of(node, breadcrumb):
    """Chuỗi frontmatter CHÍNH XÁC — verify.py dựng lại đúng chuỗi này để gỡ."""
    crumbs = ", ".join(f'"{c}"' for c in breadcrumb)
    return (
        "---\n"
        f'brd_id: {node["id"]}\n'
        f'title: "{node["title"]}"\n'
        f"breadcrumb: [{crumbs}]\n"
        "---\n\n"
    )


def _normalize_headings(lines, root_depth, dmap):
    out = []
    for line in lines:
        m = HEADING_RE.match(line)
        if not m:
            out.append(line)
            continue
        new_level = dmap[len(m.group(1))] - root_depth + 1
        if not 1 <= new_level <= 6:
            raise SplitError(
                f'Heading "{m.group(2).strip()}" rơi vào cấp {new_level} sau chuẩn hoá '
                f"(hợp lệ 1..6). Chọn cấp cắt sâu hơn."
            )
        out.append("#" * new_level + m.group(2))
    return out


def render_file(node, md_lines, dmap, breadcrumb):
    body = _normalize_headings(md_lines[node["start"]:node["end"]], node["depth"], dmap)
    text = "\n".join(body)
    text = text.replace(MEDIA_SRC, "](" + rel_media_prefix(node["path"]) + "media/")
    return frontmatter_of(node, breadcrumb) + text


def _breadcrumbs(nodes):
    by_id = {n["id"]: n for n in nodes}
    out = {}
    for n in nodes:
        crumbs, cur = [], n["parent"]
        while cur:
            crumbs.append(by_id[cur]["title"])
            cur = by_id[cur]["parent"]
        out[n["id"]] = list(reversed(crumbs))
    return out


def _q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_tree(nodes, md_lines, dmap, dest, meta):
    dest = Path(dest)
    crumbs = _breadcrumbs(nodes)
    for node in nodes:
        target = dest / node["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_file(node, md_lines, dmap, crumbs[node["id"]]),
                          encoding="utf-8", newline="\n")

    inv = ", ".join(f"{d}: {lv}" for lv, d in sorted(dmap.items(), key=lambda kv: kv[1]))
    lines = [
        'schema_version: "1.0"',
        "source:",
        f'  file: {_q(meta["source_file"])}',
        f'  sha256: {_q(meta["sha256"])}',
        f'  imported_at: {_q(meta["imported_at"])}',
        f'  pandoc: {_q(meta["pandoc"])}',
        f'cut_depth: {meta["cut_depth"]}',
        f'detection: {{ tier: {meta["tier"]}, note: {_q(meta["tier_note"])} }}',
        f"depth_map: {{{inv}}}",
        "nodes:",
    ]
    for n in nodes:
        lines.append(
            f'  - {{ id: {n["id"]}, order: {n["order"]}, depth: {n["depth"]}, '
            f'word_level: {n["word_level"]}, kind: {n["kind"]}, '
            f'title: {_q(n["title"])}, path: {_q(n["path"])}, '
            f'parent: {n["parent"] or "null"}, '
            f'chars: {sum(len(x) + 1 for x in md_lines[n["start"]:n["end"]])} }}'
        )
    (dest / "brd.manifest.yml").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8", newline="\n")
