"""Đặt tên thư mục/file từ tiêu đề mục trong tài liệu."""

import re
import unicodedata

# NFD không tách được đ/Đ nên phải thay tay trước khi chuẩn hoá.
_D_MAP = str.maketrans({"đ": "d", "Đ": "D"})


def slugify(title: str, maxlen: int = 60) -> str:
    """Tiêu đề tiếng Việt -> slug [a-z0-9-], tối đa maxlen ký tự."""
    s = title.translate(_D_MAP)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).lower().strip("-")
    if len(s) > maxlen:
        s = s[:maxlen].rstrip("-")
    return s or "muc"
