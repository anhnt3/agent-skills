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
    toc = toc_titles(docx)
    if len({lv for _, lv in toc}) >= 2 and len(toc) >= 5:
        return {"tier": 3, "note": f"Suy từ mục lục sẵn có, {len(toc)} mục",
                "style_levels": {}, "heading_count": len(toc), "needs_llm": False}
    numbered = numbered_titles(docx)
    if len({lv for _, lv in numbered}) >= 2 and len(numbered) >= 5:
        return {"tier": 4, "note": f"Suy từ đánh số gõ tay, {len(numbered)} mục",
                "style_levels": {}, "heading_count": len(numbered), "needs_llm": False}
    return {
        "tier": 0,
        "note": "Không thấy Heading style, style tự chế có outlineLvl, mục lục, hay đánh số liên tục",
        "style_levels": {}, "heading_count": 0, "needs_llm": True,
    }


_PARA_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)
_TEXT_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
_TOC_STYLE_RE = re.compile(r"^(?:TOC|toc ?)(\d)$")
_NUM_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+\S")


def _paragraphs(docx):
    """[(styleId hoặc '', text)] theo thứ tự tài liệu."""
    xml = _read(docx, "word/document.xml")
    out = []
    for m in _PARA_RE.finditer(xml):
        block = m.group(0)
        style = _PSTYLE_RE.search(block)
        text = "".join(_TEXT_RE.findall(block)).strip()
        out.append((style.group(1) if style else "", text))
    return out


def _toc_text(block):
    """Text của một dòng mục lục, bỏ phần số trang sau dấu tab cuối cùng.

    Word đặt số trang sau <w:tab/>; ký tự tab KHÔNG nằm trong <w:t> nên nếu
    gộp thẳng mọi <w:t> sẽ ra "Tiêu đề12" — dính số trang vào tiêu đề.
    """
    head = block.rsplit("<w:tab/>", 1)[0] if "<w:tab/>" in block else block
    text = "".join(_TEXT_RE.findall(head)).strip()
    return re.sub(r"\s*\.{2,}\s*\d*$", "", text).strip()


def toc_titles(docx):
    """[(tiêu đề, cấp)] moi từ đoạn mang style TOC1..9 / 'toc 1'..'toc 9'."""
    xml = _read(docx, "word/document.xml")
    out = []
    for m in _PARA_RE.finditer(xml):
        block = m.group(0)
        style = _PSTYLE_RE.search(block)
        if not style:
            continue
        lvl = _TOC_STYLE_RE.match(style.group(1))
        if not lvl:
            continue
        text = _toc_text(block)
        if text:
            out.append((text, int(lvl.group(1))))
    return out


def numbered_titles(docx):
    """[(text, cấp)] cho đoạn gõ số tay, chỉ nhận khi dãy số LIÊN TỤC."""
    hits = []
    for _, text in _paragraphs(docx):
        m = _NUM_RE.match(text)
        if m and len(text) < 200:
            hits.append((text, m.group(1), len(m.group(1).split("."))))
    seen = set()
    out = []
    for text, num, level in hits:
        parts = num.split(".")
        prefixes = [".".join(parts[:i]) for i in range(1, len(parts))]
        if all(p in seen for p in prefixes):
            seen.add(num)
            out.append((text, level))
    return out


def promotions_for(docx):
    """[{'text','level'}] nạp cho Lua filter, theo bậc mà detect_tier chọn."""
    res = detect_tier(docx)
    if res["tier"] == 3:
        pairs = toc_titles(docx)
    elif res["tier"] == 4:
        pairs = numbered_titles(docx)
    else:
        return []
    return [{"text": t, "level": lv} for t, lv in pairs]
