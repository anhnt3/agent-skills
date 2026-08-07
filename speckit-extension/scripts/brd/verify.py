"""Ghép ngược cây markdown về file trung gian và đòi giống byte-for-byte."""

import re
from pathlib import Path

from .outline import HEADING_RE, iter_code_aware
from .splitter import frontmatter_of, inline_lines, unrewrite_media

# Bắt cả hai dạng tham chiếu ảnh: `](../media/x.png)` và `<img src="../media/x.png"`.
# Thiếu dạng HTML thì kiểm ảnh mồ côi / ảnh thiếu sẽ im lặng ngừng hoạt động.
_IMG_RE = re.compile(r'(?:\]\(|src=")(?:\.\./)*media/([^)"]+)')


class VerifyError(Exception):
    pass


def _headings_inside_table(text):
    """Số dòng heading nằm giữa `<table>` và `</table>` của chính nó.

    CHỈ để cảnh báo. Không đụng vào việc phân tích heading hay số đếm heading:
    `iter_code_aware` cố ý không biết tới khối HTML (xem docstring của nó), nên
    một dòng `#` lọt vào trong bảng sẽ bị coi là heading thật — làm lệch
    `depth_map`/`recommend_depth`, hoặc tệ hơn là cắt đôi một `<table>` sang hai
    file khiến cả hai dựng ra HTML hỏng. Hàm này phát hiện để báo cho người dùng.
    """
    depth, hits = 0, 0
    for line in text.split("\n"):
        low = line.lower()
        if depth > 0 and HEADING_RE.match(line):
            hits += 1
        depth += low.count("<table")
        depth -= low.count("</table>")
        depth = max(depth, 0)
    return hits


def _denormalize(lines, root_depth, depth_to_level):
    out = []
    for _, line, in_code in iter_code_aware(lines):
        m = None if in_code else HEADING_RE.match(line)
        if not m:
            out.append(line)
            continue
        depth = root_depth + len(m.group(1)) - 1
        if depth not in depth_to_level:
            raise VerifyError(f"Không suy được cấp Word cho heading: {m.group(2).strip()}")
        out.append("#" * depth_to_level[depth] + m.group(2))
    return out


def reassemble(nodes, dest, dmap, breadcrumbs):
    """Dựng lại file trung gian từ các mảnh đã ghi, hoàn tác đúng 3 phép biến đổi."""
    dest = Path(dest)
    depth_to_level = {d: lv for lv, d in dmap.items()}
    chunks = []
    for node in nodes:
        if node.get("inline"):
            # Không có file: dựng lại segment từ dữ liệu node, đã ở cấp Word gốc nên
            # không phải hoàn tác phép biến đổi nào.
            chunks.append("\n".join(inline_lines(node)))
            continue
        text = (dest / node["path"]).read_text(encoding="utf-8")
        # 1. gỡ frontmatter — dựng lại đúng chuỗi đã ghi rồi cắt tiền tố
        fm = frontmatter_of(node, breadcrumbs[node["id"]])
        if not text.startswith(fm):
            raise VerifyError(f'Frontmatter của {node["path"]} không khớp bản đã sinh.')
        text = text[len(fm):]
        # 2. trả đường dẫn ảnh về dạng chuẩn
        text = unrewrite_media(text, node["path"])
        # 3. trả heading về cấp Word gốc
        chunks.append("\n".join(_denormalize(text.split("\n"), node["depth"], depth_to_level)))
    return "\n".join(chunks)


def check_roundtrip(nodes, dest, dmap, breadcrumbs, original_md):
    got = reassemble(nodes, dest, dmap, breadcrumbs)
    if got == original_md:
        return
    a, b = original_md.split("\n"), got.split("\n")
    for i in range(max(len(a), len(b))):
        av = a[i] if i < len(a) else "<hết file>"
        bv = b[i] if i < len(b) else "<hết file>"
        if av != bv:
            lo = max(0, i - 2)
            ctx = "\n".join(f"    {j}: {a[j]}" for j in range(lo, min(i + 3, len(a))))
            raise VerifyError(
                f"Ghép ngược lệch ở dòng {i}:\n"
                f"  bản gốc:   {av!r}\n"
                f"  ghép ngược:{bv!r}\n"
                f"  ngữ cảnh bản gốc:\n{ctx}"
            )
    raise VerifyError(f"Ghép ngược lệch độ dài: gốc {len(a)} dòng, ghép ngược {len(b)} dòng.")


def secondary_checks(nodes, dest, media_dir, shallow_heading_count):
    """Kiểm phụ — trả về danh sách cảnh báo, KHÔNG chặn việc ghi.

    `shallow_heading_count` là số heading ở các độ sâu <= cấp cắt, tức đúng số node
    vật chất hoá (không kể node gốc). So sánh cùng một đơn vị nên cảnh báo mới có
    thể kích hoạt thật; so với TỔNG heading mọi cấp thì không bao giờ nổ.
    """
    dest, media_dir = Path(dest), Path(media_dir)
    warnings = []
    referenced = set()
    for node in nodes:
        if node.get("inline"):
            continue        # không có file để kiểm; nội dung chỉ là dòng heading
        text = (dest / node["path"]).read_text(encoding="utf-8")
        for name in _IMG_RE.findall(text):
            referenced.add(name)
            if not (media_dir / name).is_file():
                warnings.append(f'Ảnh không tồn tại: media/{name} (tham chiếu ở {node["path"]})')
        n_bad = _headings_inside_table(text)
        if n_bad:
            warnings.append(
                f'{n_bad} dòng heading nằm bên trong khối <table> ở {node["path"]} — '
                "chúng bị tính là heading thật, có thể làm lệch cấp cắt đề xuất và cắt "
                "đôi bảng sang hai file (bảng sẽ dựng hỏng). Hãy kiểm lại chỗ này."
            )
        size = sum(len(line) + 1 for line in text.split("\n"))
        if size > 60_000:
            warnings.append(f'File lớn {size:,} ký tự: {node["path"]} — cân nhắc cắt sâu hơn')
    if media_dir.is_dir():
        for f in sorted(media_dir.iterdir()):
            if f.is_file() and f.name not in referenced:
                warnings.append(f"Ảnh mồ côi, không ai tham chiếu: media/{f.name}")
    materialised = sum(1 for n in nodes if n["kind"] != "root")
    if materialised != shallow_heading_count:
        warnings.append(
            f"Số node vật chất hoá ({materialised}) lệch số heading ở cấp <= cấp cắt "
            f"({shallow_heading_count})"
        )
    titles = {}
    for node in nodes:
        titles.setdefault(node["title"], []).append(
            node["dir"] if node.get("inline") else node["path"])
    for title, paths in titles.items():
        if len(paths) > 1:
            warnings.append(f'Trùng tiêu đề "{title}" ở {len(paths)} chỗ: {", ".join(paths)}')
    return warnings
