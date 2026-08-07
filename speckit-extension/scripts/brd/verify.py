"""Ghép ngược cây markdown về file trung gian và đòi giống byte-for-byte."""

import re
from pathlib import Path

from .outline import HEADING_RE
from .splitter import MEDIA_SRC, frontmatter_of, rel_media_prefix

_IMG_RE = re.compile(r"\]\((?:\.\./)*media/([^)]+)\)")


class VerifyError(Exception):
    pass


def _denormalize(lines, root_depth, depth_to_level):
    out = []
    for line in lines:
        m = HEADING_RE.match(line)
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
        text = (dest / node["path"]).read_text(encoding="utf-8")
        # 1. gỡ frontmatter — dựng lại đúng chuỗi đã ghi rồi cắt tiền tố
        fm = frontmatter_of(node, breadcrumbs[node["id"]])
        if not text.startswith(fm):
            raise VerifyError(f'Frontmatter của {node["path"]} không khớp bản đã sinh.')
        text = text[len(fm):]
        # 2. trả đường dẫn ảnh về dạng chuẩn
        text = text.replace("](" + rel_media_prefix(node["path"]) + "media/", MEDIA_SRC)
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


def secondary_checks(nodes, dest, media_dir, heading_count):
    """Kiểm phụ — trả về danh sách cảnh báo, KHÔNG chặn việc ghi."""
    dest, media_dir = Path(dest), Path(media_dir)
    warnings = []
    referenced = set()
    for node in nodes:
        text = (dest / node["path"]).read_text(encoding="utf-8")
        for name in _IMG_RE.findall(text):
            referenced.add(name)
            if not (media_dir / name).is_file():
                warnings.append(f'Ảnh không tồn tại: media/{name} (tham chiếu ở {node["path"]})')
        size = sum(len(line) + 1 for line in text.split("\n"))
        if size > 60_000:
            warnings.append(f'File lớn {size:,} ký tự: {node["path"]} — cân nhắc cắt sâu hơn')
    if media_dir.is_dir():
        for f in sorted(media_dir.iterdir()):
            if f.is_file() and f.name not in referenced:
                warnings.append(f"Ảnh mồ côi, không ai tham chiếu: media/{f.name}")
    if len(nodes) - 1 > heading_count:
        warnings.append(
            f"Số node ({len(nodes) - 1}) nhiều hơn số heading đếm từ docx ({heading_count})"
        )
    titles = {}
    for node in nodes:
        titles.setdefault(node["title"], []).append(node["path"])
    for title, paths in titles.items():
        if len(paths) > 1:
            warnings.append(f'Trùng tiêu đề "{title}" ở {len(paths)} chỗ: {", ".join(paths)}')
    return warnings
