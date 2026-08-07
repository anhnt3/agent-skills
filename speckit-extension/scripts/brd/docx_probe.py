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
    sized = size_tier(docx)
    if sized:
        return {"tier": 5, "note": f"Suy từ cỡ chữ giảm dần, {len(sized)} mục",
                "style_levels": {}, "heading_count": len(sized), "needs_llm": False}
    return {
        "tier": 0,
        "note": "Bậc 1-5 đều mù: không Heading style, không style tự chế có outlineLvl, "
                "không mục lục, không đánh số liên tục, không phân tầng cỡ chữ",
        "style_levels": {}, "heading_count": 0, "needs_llm": True,
        "candidates": format_candidates(docx),
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


_HYPERLINK_RE = re.compile(r"<w:hyperlink\b[^>]*>(.*?)</w:hyperlink>", re.S)
_FIELD_BOUNDARY_RE = re.compile(r"<w:tab\b[^>]*/>|<w:fldChar\b|<w:instrText\b")
_LEADING_ENUM_RE = re.compile(
    r"^\s*(?:[IVXLCDM]+|[ivxlcdm]+|\d+(?:\.\d+)*|[A-Za-zĐđ])[.\)]\s+"
)


def _toc_text(block):
    """Text hiển thị của một dòng mục lục, bỏ mã trường PAGEREF/số trang.

    Mỗi mục mục lục thật nằm trong một <w:hyperlink> (liên kết tới bookmark
    heading) — đoạn chứa mục lục có thể còn giữ nguyên field code TOC gốc
    (<w:fldChar begin>, <w:instrText> TOC ...</w:instrText>, ...) đứng TRƯỚC
    <w:hyperlink> đầu tiên, nên phải tìm text bên trong <w:hyperlink> chứ
    không phải quét cả đoạn.

    Trong <w:hyperlink> đó, cấu trúc là: <tiêu đề hiển thị><tab dẫn chấm>
    <fldChar begin><instrText PAGEREF...><fldChar separate><số trang>
    <fldChar end>. Tab dẫn thực tế là <w:tab .../> có thuộc tính (kiểu
    "right"/"dot"), KHÔNG phải <w:tab/> trần — nên cắt tại điểm gặp BẤT KỲ
    trong ba mốc <w:tab .../>, <w:fldChar>, <w:instrText> (mốc nào tới
    trước), rồi mới gộp <w:t> ở phần trước mốc đó.

    TOC field còn bake sẵn số thứ tự đề mục ("I.", "1.") thành text — trong
    khi tiêu đề gốc trong thân tài liệu KHÔNG chứa số này (số đến từ
    numbering tự động, không phải nội dung heading). Bỏ tiền tố đánh số đó
    để tiêu đề khớp với heading gốc.
    """
    hyperlink = _HYPERLINK_RE.search(block)
    content = hyperlink.group(1) if hyperlink else block
    boundary = _FIELD_BOUNDARY_RE.search(content)
    head = content[:boundary.start()] if boundary else content
    text = "".join(_TEXT_RE.findall(head)).strip()
    text = _LEADING_ENUM_RE.sub("", text)
    return re.sub(r"\s*\.{2,}\s*\d*$", "", text).strip()


def toc_titles(docx):
    """[(tiêu đề, cấp)] moi từ đoạn mang style TOC1..9 / 'toc 1'..'toc 9'.

    Chỉ nhận đoạn có <w:hyperlink> bên trong: Word tự sinh mỗi mục mục lục
    thật (khi cập nhật trường TOC) thành một liên kết nội bộ tới bookmark
    heading. Một đoạn mang style TOC* nhưng KHÔNG có hyperlink — ví dụ dòng
    tiêu đề "Mục lục"/"Table of Contents" mà người soạn tự gõ và gán cùng
    style cho đồng bộ định dạng — không phải một mục lục thật do trường TOC
    sinh ra, nên bị loại. Quy tắc dựa trên cấu trúc XML, không phụ thuộc
    ngôn ngữ hiển thị.
    """
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
        if "<w:hyperlink" not in block:
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


def promotions_for(docx, outline=None):
    """[{'text','level'}] nạp cho Lua filter.

    outline: [{'index','level'}] do LLM quyết (bậc 6) — chỉ số trỏ vào
    format_candidates(docx), KHÔNG phải chỉ số đoạn trong tài liệu.
    """
    if outline:
        cands = format_candidates(docx)
        return [{"text": cands[o["index"]]["text"], "level": o["level"]}
                for o in outline if 0 <= o["index"] < len(cands)]
    res = detect_tier(docx)
    if res["tier"] == 3:
        pairs = toc_titles(docx)
    elif res["tier"] == 4:
        pairs = numbered_titles(docx)
    elif res["tier"] == 5:
        pairs = size_tier(docx)
    else:
        return []
    return [{"text": t, "level": lv} for t, lv in pairs]


_BOLD_RE = re.compile(r"<w:b(?: [^>]*)?/>|<w:b(?: [^>]*)?>(?!<w:val=\"0\")")
_SZ_RE = re.compile(r"<w:sz w:val=\"(\d+)\"")


def _paragraphs_rich(docx):
    xml = _read(docx, "word/document.xml")
    out = []
    for i, m in enumerate(_PARA_RE.finditer(xml)):
        block = m.group(0)
        sizes = [int(s) for s in _SZ_RE.findall(block)]
        out.append({
            "index": i,
            "text": "".join(_TEXT_RE.findall(block)).strip(),
            "bold": bool(_BOLD_RE.search(block)),
            "size": max(sizes) if sizes else None,
        })
    return out


def format_candidates(docx):
    """Đoạn ngắn, in đậm hoặc cỡ chữ lớn hơn cỡ phổ biến nhất, không kết thúc bằng '.'."""
    paras = _paragraphs_rich(docx)
    sizes = collections.Counter(p["size"] for p in paras if p["size"])
    body_size = sizes.most_common(1)[0][0] if sizes else None
    out = []
    for p in paras:
        text = p["text"]
        if not text or len(text) >= 120 or text.endswith("."):
            continue
        bigger = body_size is not None and p["size"] is not None and p["size"] > body_size
        if p["bold"] or bigger:
            out.append({"index": p["index"], "text": text,
                        "bold": p["bold"], "size": p["size"]})
    return out


def size_tier(docx):
    """Bậc 5: cấp suy từ cỡ chữ giảm dần trong các ứng viên."""
    cands = [c for c in format_candidates(docx) if c["size"]]
    distinct = sorted({c["size"] for c in cands}, reverse=True)
    if len(distinct) < 2 or len(cands) < 5:
        return []
    rank = {s: i + 1 for i, s in enumerate(distinct)}
    return [(c["text"], rank[c["size"]]) for c in cands]
