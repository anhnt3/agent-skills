"""Đọc XML bên trong .docx để xác định bậc dò cấu trúc TRƯỚC khi gọi pandoc."""

import collections
import re
import zipfile
from pathlib import Path

_STYLE_BLOCK_RE = re.compile(r"<w:style [^>]*w:styleId=\"([^\"]+)\".*?</w:style>", re.S)
_OUTLINE_RE = re.compile(r"<w:outlineLvl w:val=\"(\d+)\"")
_PSTYLE_RE = re.compile(r"<w:pStyle w:val=\"([^\"]+)\"")
_HEADING_ID_RE = re.compile(r"^Heading(\d)$")


def _read(docx, name):
    with zipfile.ZipFile(Path(docx)) as z:
        try:
            return z.read(name).decode("utf-8")
        except KeyError:
            return ""


def heading_style_levels(docx):
    """styleId -> cấp Word (1-based), suy từ w:outlineLvl trong styles.xml."""
    styles_xml = _read(docx, "word/styles.xml")
    used = set(count_paragraph_styles(docx))
    out = {}
    for m in _STYLE_BLOCK_RE.finditer(styles_xml):
        style_id = m.group(1)
        if style_id not in used:
            continue
        lvl = _OUTLINE_RE.search(m.group(0))
        if lvl:
            out[style_id] = int(lvl.group(1)) + 1
    return out


def count_paragraph_styles(docx):
    """styleId -> số đoạn văn dùng style đó."""
    return collections.Counter(_PSTYLE_RE.findall(_read(docx, "word/document.xml")))


def detect_tier(docx):
    counts = count_paragraph_styles(docx)
    heading_count = sum(n for sid, n in counts.items() if _HEADING_ID_RE.match(sid))
    if heading_count >= 5:
        used = sorted(
            {int(_HEADING_ID_RE.match(s).group(1)) for s in counts if _HEADING_ID_RE.match(s)}
        )
        return {
            "tier": 1,
            "note": f"Heading style chuẩn, {heading_count} heading, cấp Word {used}",
            "style_levels": {s: int(_HEADING_ID_RE.match(s).group(1))
                             for s in counts if _HEADING_ID_RE.match(s)},
            "heading_count": heading_count,
            "needs_llm": False,
        }
    custom = {sid: lvl for sid, lvl in heading_style_levels(docx).items()
              if not _HEADING_ID_RE.match(sid)}
    if len(custom) >= 2:
        n = sum(counts[s] for s in custom)
        return {
            "tier": 2,
            "note": f"Style tự chế có outlineLvl: {sorted(custom)}, {n} đoạn",
            "style_levels": custom,
            "heading_count": n,
            "needs_llm": False,
        }
    return {
        "tier": 0,
        "note": "Không thấy Heading style, cũng không thấy style tự chế có outlineLvl",
        "style_levels": {},
        "heading_count": 0,
        "needs_llm": True,
    }
