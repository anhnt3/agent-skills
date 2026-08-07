"""Dựng danh sách node vật chất hoá và cắt file markdown trung gian thành cây."""

from pathlib import Path

from .naming import slugify
from .outline import HEADING_RE, iter_code_aware

# Hai dạng tham chiếu ảnh pandoc có thể sinh ra, phải xử lý CẢ HAI:
#   - dạng markdown:  ![](./media/media/image1.png)
#   - dạng HTML (gfm): <img src="./media/media/image1.png" style="..." />
MEDIA_SRC = "](./media/media/"
MEDIA_SRC_HTML = 'src="./media/media/'
MEDIA_FORMS = ((MEDIA_SRC, "]("), (MEDIA_SRC_HTML, 'src="'))


class SplitError(Exception):
    pass


class DepthError(SplitError):
    """Cấp cắt làm heading rơi ra ngoài 1..6 — lỗi chọn cấp, KHÔNG phải lỗi kiểm chứng."""


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
            "title": "(phần đầu tài liệu)", "raw": None, "path": "_index.md", "dir": "",
            "parent": None, "start": 0, "end": first_line,
        })

    # LƯỢT 1 — dựng node, đánh số anh em, xác định cha/con. Mọi node nông hơn cấp
    # cắt tạm coi là folder để `dir` (khoá đánh số của các con) đúng như cũ.
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
            "word_level": h["level"], "kind": kind, "title": h["title"], "raw": h["raw"],
            "dir": f"{base}{name}/" if kind == "folder" else base,
            "path": f"{base}{name}/_index.md" if kind == "folder" else f"{base}{name}.md",
            "parent": parent["id"] if parent else None,
            "start": h["line"], "end": None,
        }
        nodes.append(node)
        if kind == "folder":
            stack.append(node)

    # LƯỢT 2 — folder KHÔNG có node con thì gộp thành một file `NN-slug.md` thay vì
    # `NN-slug/_index.md`: thư mục chỉ chứa đúng một file là nhiễu cho người đọc.
    # An toàn vì `dir` của một folder chỉ được các con nó tiêu thụ, mà nó không có
    # con nào; số thứ tự anh em (counters) đã cấp xong ở lượt 1 nên không đổi.
    has_child = {n["parent"] for n in nodes if n["parent"]}
    for node in nodes:
        if node["kind"] == "folder" and node["id"] not in has_child:
            node["kind"] = "leaf"
            node["path"] = node["path"][: -len("/_index.md")] + ".md"

    # Segment của MỌI node kết thúc ở node vật chất hoá kế tiếp. Nhờ vậy các
    # segment nối liền nhau, phủ kín file, không hở không chồng -> ghép ngược khớp.
    for i, node in enumerate(nodes):
        node["end"] = nodes[i + 1]["start"] if i + 1 < len(nodes) else total_lines
    return nodes


def inline_lines(node):
    """Các dòng của segment DỰNG LẠI từ dữ liệu node, không đọc file nào.

    Chỉ gồm đúng dòng heading nguyên văn (`"#" * word_level + raw`) và `blanks`
    dòng trắng cuối segment — đúng hình dạng mà `mark_inline` đã chứng minh.
    """
    return ["#" * node["word_level"] + node["raw"]] + [""] * node["blanks"]


def mark_inline(nodes, md_lines):
    """Đánh dấu node folder mà segment dựng lại được NGUYÊN VĂN -> khỏi ghi `_index.md`.

    Nguyên tắc: chỉ bỏ đi thứ chứng minh được là tái tạo lại y hệt. Ứng viên tái
    tạo (`inline_lines`) được so sánh byte-for-byte với segment thật; lệch một ký
    tự — kể cả một dòng trắng thừa/thiếu ở cuối — thì node vẫn ghi file như cũ.
    Không lưu nội dung tài liệu vào manifest, không nới lỏng kiểm ghép ngược.
    """
    for node in nodes:
        node["inline"] = False
        node["blanks"] = 0
        if node["kind"] != "folder" or not node["raw"]:
            continue
        seg = md_lines[node["start"]:node["end"]]
        node["blanks"] = len(seg) - 1
        if seg == inline_lines(node):
            node["inline"] = True
        else:
            node["blanks"] = 0


def frontmatter_of(node, breadcrumb):
    """Chuỗi frontmatter CHÍNH XÁC — verify.py dựng lại đúng chuỗi này để gỡ."""
    crumbs = ", ".join(_q(c) for c in breadcrumb)
    return (
        "---\n"
        f'brd_id: {node["id"]}\n'
        f'title: {_q(node["title"])}\n'
        f"breadcrumb: [{crumbs}]\n"
        "---\n\n"
    )


def _normalize_headings(lines, root_depth, dmap):
    out = []
    for _, line, in_code in iter_code_aware(lines):
        m = None if in_code else HEADING_RE.match(line)
        if not m:
            out.append(line)
            continue
        word_level = len(m.group(1))
        if word_level not in dmap:
            raise SplitError(
                f'Heading "{m.group(2).strip()}" ở cấp Word {word_level} không có trong '
                f"bản đồ cấp — cây heading không nhất quán."
            )
        new_level = dmap[word_level] - root_depth + 1
        if not 1 <= new_level <= 6:
            raise DepthError(
                f'Heading "{m.group(2).strip()}" rơi vào cấp {new_level} sau chuẩn hoá '
                f"(hợp lệ 1..6)."
            )
        out.append("#" * new_level + m.group(2))
    return out


def rewrite_media(text, path):
    """Đổi mọi tham chiếu ảnh sang đường dẫn tương đối theo độ sâu của `path`."""
    prefix = rel_media_prefix(path)
    for src, head in MEDIA_FORMS:
        text = text.replace(src, head + prefix + "media/")
    return text


def unrewrite_media(text, path):
    """Nghịch đảo chính xác của `rewrite_media` — dùng khi ghép ngược."""
    prefix = rel_media_prefix(path)
    for src, head in MEDIA_FORMS:
        text = text.replace(head + prefix + "media/", src)
    return text


def render_file(node, md_lines, dmap, breadcrumb):
    body = _normalize_headings(md_lines[node["start"]:node["end"]], node["depth"], dmap)
    text = rewrite_media("\n".join(body), node["path"])
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
    mark_inline(nodes, md_lines)   # gắn cờ `inline`/`blanks` lên chính các node đang dùng
    for node in nodes:
        if node["inline"]:
            # Không ghi `_index.md` rỗng nội dung, nhưng thư mục vẫn phải có (chứa con).
            (dest / node["dir"]).mkdir(parents=True, exist_ok=True)
            continue
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
        # Node `inline` không có file: thay `path` bằng `inline: true` + `dir` để người
        # đọc manifest vẫn ánh xạ được tiêu đề -> thư mục.
        where = (f'inline: true, dir: {_q(n["dir"])}' if n.get("inline")
                 else f'path: {_q(n["path"])}')
        lines.append(
            f'  - {{ id: {n["id"]}, order: {n["order"]}, depth: {n["depth"]}, '
            f'word_level: {n["word_level"]}, kind: {n["kind"]}, '
            f'title: {_q(n["title"])}, {where}, '
            f'parent: {n["parent"] or "null"}, '
            f'chars: {sum(len(x) + 1 for x in md_lines[n["start"]:n["end"]])} }}'
        )
    (dest / "brd.manifest.yml").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8", newline="\n")
