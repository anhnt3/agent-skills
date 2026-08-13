#!/usr/bin/env python3
"""Chấm một `intel.md` (unit theo cây functions.json) trước khi báo xong.

Hai mức, cùng nguyên tắc với srs_verify.py:
  BLOCKING (exit 1) — chỉ thứ kiểm được TẤT ĐỊNH: placeholder còn sót, §1
                      thiếu/thừa FN-ID so với functions.json, trần §8, tỉ lệ
                      "không tìm thấy" vượt ngưỡng, no-clobber §8/§10.
  WARNING  (exit 0) — thứ cần phán đoán: cite trông không giống file:dòng, FN
                      tìm thấy nhưng không xuất hiện ở §2/§7/§8.

Chỉ cần python3 + fnlist_tree (cùng thư mục scripts/), không phụ thuộc ngoài
stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import fnlist_tree as ft


def _force_utf8_console() -> None:
    """Windows mở subprocess với stdout/stderr mã cp1252 mặc định, không phải
    UTF-8 — in tiếng Việt có dấu ra đó là crash UnicodeEncodeError. Ép lại UTF-8
    khi có thể; capsys của pytest thay stdout bằng đối tượng không có
    `reconfigure` nên phải hasattr trước."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        enc = getattr(stream, "encoding", None)
        if enc and enc.lower() != "utf-8" and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_force_utf8_console()

FN_ID_RE = re.compile(r"\bFN(?:-\d{2})+\b")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FENCE_RE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PLACEHOLDER_RE = re.compile(r"\[([^\[\]\n]{1,80})\](?!\()")
CODE_PATH_RE = re.compile(
    r"\b[\w.-]+/[\w./-]*\.\w{1,5}\b(?::\d+)?"
    r"|\b\w[\w.-]*\.(?:py|ts|tsx|js|jsx|java|cs|go|rb|php|vue|sql|kt|swift|yml|yaml)\b(?::\d+)?"
)
LABEL_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
# Bốn nhãn loại cố định của §8 — đây là nhãn phân loại, không phải chỗ điền
# nội dung, nên KHÔNG được tính là placeholder chưa điền.
KNOWN_LABEL_RE = re.compile(
    r"^(không suy được từ code|chính sách nghiệp vụ|FN không tìm thấy|"
    r"chờ trả lời từ lần trước)$")
SECTION12_HEADING_RE = re.compile(r"^###\s+(.+)$")
MAN_HINH_FIELD_RE = re.compile(r"^[-*]\s+\*\*`?Màn hình`?\*\*:\s*(.+)$")


def strip_noise(text: str) -> str:
    """Bỏ HTML comment, khối code rào, và inline code — cùng lý do với
    srs_verify.py: cả ba có thể chứa dấu [] hợp lệ (hướng dẫn khung, ví dụ)."""
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def find_placeholders(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(strip_noise(text).splitlines(), start=1):
        for m in PLACEHOLDER_RE.finditer(line):
            if KNOWN_LABEL_RE.match(m.group(1).strip()):
                continue
            out.append({"line": i, "text": m.group(0)})
    return out


def _table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def _section_body(text: str, number: int, strip: bool = True) -> str:
    """Nội dung mục '## <number>.' tới trước mục '## <số khác>.' kế tiếp.

    `strip=False` bỏ qua strip_noise (giữ nguyên inline code `...`) — dùng khi
    cần đọc GIÁ TRỊ Ô BẢNG nguyên vẹn (§2/§11 khi so tên màn hình): strip_noise
    xoá SẠCH nội dung trong cặp backtick (không chỉ bỏ dấu backtick), nên một
    tên màn hình lỡ bọc backtick sẽ biến mất hoàn toàn thay vì chỉ mất dấu —
    làm cả hai vế so sánh cùng rỗng và gate §11 im lặng vô hiệu. An toàn bỏ
    qua strip_noise ở đây vì `_table_rows`/`_table_data_rows` chỉ nhặt dòng
    bắt đầu/kết thúc bằng '|' — HTML comment và code fence không khớp mẫu đó
    nên không lọt vào dữ liệu bảng dù không được lọc riêng."""
    src = strip_noise(text) if strip else text
    lines = src.splitlines()
    start = end = None
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+(\d+)\.", ln.strip())
        if m and int(m.group(1)) == number:
            start = i + 1
        elif start is not None and re.match(r"^##\s+\d+\.", ln.strip()):
            end = i
            break
    if start is None:
        return ""
    return "\n".join(lines[start: end if end is not None else len(lines)])


def parse_section1(text: str) -> dict[str, str]:
    """§1 'Phủ chức năng' → {FN-ID: nội dung cột 'Tìm thấy ở đâu'}."""
    out = {}
    for row in _table_rows(_section_body(text, 1)):
        if row and FN_ID_RE.fullmatch(row[0]):
            out[row[0]] = row[2] if len(row) > 2 else ""
    return out


def parse_numbered_items(text: str, number: int) -> list[dict]:
    """Mục kiểu danh sách (§8): dòng '<n>. [nhãn] nội dung'. Trả cả nhãn lẫn
    nội dung để tính trần và no-clobber."""
    out = []
    for ln in _section_body(text, number).splitlines():
        m = re.match(r"^\d+\.\s+(.*)$", ln.strip())
        if not m:
            continue
        rest = m.group(1)
        lm = LABEL_RE.match(rest)
        label, content = (lm.group(1), lm.group(2)) if lm else (None, rest)
        out.append({"label": label, "content": content.strip()})
    return out


def parse_section10_rows(text: str) -> list[tuple]:
    """§10 là BẢNG, không phải danh sách — trả tuple 4 cột gốc
    (#, Loại, Mô tả, Nguồn), bỏ cột Kết luận (không tính vào so no-clobber vì
    đó là cột duy nhất `srs-from-code` được phép cập nhật sau)."""
    out = []
    for row in _table_rows(_section_body(text, 10)):
        if row and row[0].strip().isdigit():
            out.append(tuple(c.strip() for c in row[:4]))
    return out


def check_section1_coverage(text: str, expected: list[dict]) -> list[dict]:
    got = parse_section1(text)
    want_ids = {f["id"] for f in expected}
    missing = want_ids - set(got)
    extra = set(got) - want_ids
    out = []
    if missing:
        out.append({"loai": "thieu-fn-o-muc-1",
                    "thong_diep": "§1 thiếu dòng cho: " + ", ".join(sorted(missing))})
    if extra:
        out.append({"loai": "thua-fn-o-muc-1",
                    "thong_diep": "§1 có FN-ID không thuộc unit này: "
                                   + ", ".join(sorted(extra))})
    return out


def check_not_found_ratio(text: str, expected: list[dict]) -> list[dict]:
    """Miễn trừ khi `m < 3` — với unit lá đơn lẻ (M=1) hoặc 2-FN, một FN
    "không tìm thấy" đã vượt 1/3 và BLOCKING vĩnh viễn không cách nào pass,
    dù đó là hình dạng unit hợp lệ theo thiết kế (`default_units` cho phép
    node lá đứng một mình). Thống kê tỉ lệ không có ý nghĩa ở kích cỡ quá
    nhỏ; Bước 4 của code-intel.md đã có cơ chế DỪNG hỏi người dùng làm lưới
    an toàn thay thế cho các ca này."""
    got = parse_section1(text)
    m = len(expected)
    not_found = sum(1 for v in got.values() if "không tìm thấy" in v)
    if m >= 3 and not_found > m / 3:
        return [{"loai": "ti-le-khong-tim-thay-vuot-nguong",
                 "thong_diep": f"{not_found}/{m} FN không tìm thấy, vượt 1/3 — "
                                "có thể đang quét sai nhánh/sai phạm vi."}]
    return []


_GENERIC_GHI_CHU_RE = re.compile(r"^(đã tìm không thấy|không tìm thấy|-|—)\.?$", re.I)


def check_ghi_chu_evidence(text: str) -> list[dict]:
    """§1 dòng "không tìm thấy" phải có cột `Ghi chú` nêu bằng chứng đã tìm
    (code-intel.md bước 4: ≥2 pattern/từ khoá/thư mục thực sự đã chạy). Script
    KHÔNG thẩm định được nội dung bằng chứng có thật hay không (đó là việc
    của người soát) — chỉ bắt ca RÕ RÀNG thiếu bằng chứng: ô trống, hoặc chỉ
    lặp lại đúng câu "không tìm thấy" theo cách khác. WARNING, không BLOCKING:
    đây là heuristic dựa trên độ dài/chuỗi chung chung, có thể báo nhầm một ô
    ghi chú thật sự đủ nhưng ngắn."""
    out = []
    # strip=False: Ghi chú thường ghi pattern/từ khoá bọc backtick (cách tự
    # nhiên nhất để trích dẫn một chuỗi đã grep) — strip_noise (dùng ở
    # _section_body mặc định) xoá sạch NỘI DUNG bên trong backtick, không chỉ
    # dấu backtick, nên một ô Ghi chú hợp lệ kiểu `` `login` `signin` `` sẽ
    # đọc thành rỗng và bị báo oan. Dùng _strip_backtick (chỉ bỏ dấu) cho cả
    # hai cột thay vì strip_noise.
    for row in _table_rows(_section_body(text, 1, strip=False)):
        if not row or not FN_ID_RE.fullmatch(_strip_backtick(row[0])):
            continue
        found_at = _strip_backtick(row[2]) if len(row) > 2 else ""
        if "không tìm thấy" not in found_at:
            continue
        ghi_chu = _strip_backtick(row[3]) if len(row) > 3 else ""
        if not ghi_chu or ghi_chu == "—" or _GENERIC_GHI_CHU_RE.match(ghi_chu):
            out.append({
                "loai": "ghi-chu-khong-du-bang-chung",
                "thong_diep": f"{row[0]}: cột Ghi chú trống hoặc quá chung chung "
                              "cho dòng 'không tìm thấy' — nêu rõ ≥2 pattern/từ "
                              "khoá/thư mục thực sự đã thử.",
            })
    return out


def check_section8_cap(text: str, m: int) -> list[dict]:
    items = parse_numbered_items(text, 8)
    # Thiếu nhãn (label=None) tính vào trần y như "[không suy được từ code]" —
    # code-intel.md và intel-template.md đều hứa hành vi này (an toàn: bị đếm
    # trần chứ không lọt lưới); bỏ sót ca None từng là lỗ hổng thoát trần.
    labeled = [i for i in items if i["label"] in (None, "không suy được từ code")]
    cap = max(3, m / 3)
    out = []
    if len(labeled) > cap:
        out.append({"loai": "tran-muc-8-vuot-nguong",
                    "thong_diep": f"{len(labeled)} mục nhãn 'không suy được từ code', "
                                   f"vượt ngưỡng {cap:.1f}."})
    by_reason: dict[str, int] = {}
    for i in items:
        key = i["content"].split("—")[0].strip()
        by_reason[key] = by_reason.get(key, 0) + 1
    dup = [k for k, c in by_reason.items() if c >= 3]
    if dup:
        out.append({"loai": "muc-8-lap-ly-do",
                    "thong_diep": "≥3 mục dùng cùng một lý do: " + "; ".join(dup)})
    return out


def check_no_clobber_8(text: str, before: str) -> list[dict]:
    old_items = {i["content"] for i in parse_numbered_items(before, 8)}
    new_items = {i["content"] for i in parse_numbered_items(text, 8)}
    missing = old_items - new_items
    if missing:
        return [{"loai": "mat-noi-dung-muc-8",
                 "thong_diep": f"{len(missing)} mục §8 cũ không còn thấy nguyên văn "
                                "trong bản mới."}]
    return []


def check_no_clobber_10(text: str, before: str) -> list[dict]:
    old_rows = set(parse_section10_rows(before))
    new_rows = set(parse_section10_rows(text))
    missing = old_rows - new_rows
    if missing:
        return [{"loai": "mat-noi-dung-muc-10",
                 "thong_diep": f"{len(missing)} dòng §10 cũ không còn khớp nguyên văn "
                                "trong bản mới (4 cột #/Loại/Mô tả/Nguồn)."}]
    return []


_SEP_CELL_RE = re.compile(r"^:?-{3,}:?$")


def _table_data_rows(body: str) -> list[list[str]]:
    """`_table_rows` trả cả dòng tiêu đề và dòng phân cách (`| --- | --- |`) —
    hai dòng đó không phải dữ liệu và không bao giờ có cite, nên phải lọc bỏ
    trước khi chấm cite, kẻo header/separator bị chấm oan là 'cite-khong-ro'.

    §3 có thể có NHIỀU bảng liên tiếp trong cùng section (mỗi thực thể một
    bảng field riêng khi cụm ≥2 entity) — không chỉ lọc dòng phân cách ĐẦU
    TIÊN, vì header của bảng thứ hai trở đi không khớp regex phân cách và sẽ
    bị lẫn vào dữ liệu. Lấy dữ liệu theo TỪNG cặp (dòng phân cách, dòng phân
    cách kế tiếp), bỏ dòng ngay trước dòng phân cách kế tiếp (đó là header
    của bảng sau)."""
    rows = _table_rows(body)
    sep_idx = [i for i, r in enumerate(rows) if r and all(_SEP_CELL_RE.match(c) for c in r)]
    data = []
    for si in sep_idx:
        end = next((s for s in sep_idx if s > si), len(rows) + 1) - 1
        data.extend(rows[si + 1:end])
    return data


def check_cite_quality(text: str) -> list[dict]:
    """§2-§7, §9 mỗi dòng bảng có cột nguồn — cảnh báo nếu không có gì trông
    giống file:dòng và cũng không đánh dấu (suy đoán). Heuristic ở mức WARNING,
    không BLOCKING — cite hợp lệ nhưng viết khác quy ước vẫn có thể lọt qua."""
    out = []
    for section in (2, 3, 4, 5, 6, 7, 9, 11):
        for i, row in enumerate(_table_data_rows(_section_body(text, section)), start=1):
            joined = " | ".join(row)
            if not CODE_PATH_RE.search(joined) and "suy đoán" not in joined.lower():
                out.append({"loai": "cite-khong-ro",
                            "thong_diep": f"§{section} dòng {i} không thấy nguồn "
                                           "file:dòng và không đánh dấu suy đoán."})
    return out


def check_section2_anchor(text: str, expected: list[dict]) -> list[dict]:
    """Mỏ neo phủ §2: mỗi FN tìm thấy code phải xuất hiện ở §2, hoặc giải
    trình ở §7/§8 vì sao không sinh màn hình."""
    found = parse_section1(text)
    body2 = _section_body(text, 2)
    body7 = _section_body(text, 7)
    body8 = _section_body(text, 8)
    out = []
    for f in expected:
        if "không tìm thấy" in found.get(f["id"], ""):
            continue
        if f["id"] not in body2 and f["id"] not in body7 and f["id"] not in body8:
            out.append({"loai": "fn-khong-co-mat-o-muc-2",
                        "thong_diep": f"{f['id']} tìm thấy code nhưng không xuất hiện "
                                       "ở §2, §7, hay §8."})
    return out


def _strip_backtick(s: str) -> str:
    """Bỏ dấu backtick bọc quanh một giá trị ô bảng (nếu có) — LLM hay bọc tên
    kỹ thuật (route/endpoint) trong backtick theo thói quen Markdown; đây chỉ
    là trang trí, không phải một phần của tên dùng để so khớp §2↔§11."""
    s = s.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        s = s[1:-1].strip()
    return s


def parse_section11(text: str) -> list[dict]:
    """§11 'Điều khiển giao diện' → list các {"man_hinh":.., "loai":..}. Dùng
    `_table_data_rows` (không phải `_table_rows`) để tự động bỏ dòng tiêu đề/
    phân cách — cột 'Màn hình' là chuỗi tự do, không có mẫu tất định như
    FN-ID (§1) hay số thứ tự (§10) để lọc theo nội dung. `strip=False` +
    `_strip_backtick`: xem docstring `_section_body`."""
    out = []
    for row in _table_data_rows(_section_body(text, 11, strip=False)):
        if len(row) >= 3 and row[0]:
            out.append({"man_hinh": _strip_backtick(row[0]), "loai": row[2]})
    return out


def check_section11_coverage(text: str) -> list[dict]:
    """§11 liên kết với §2 qua cột 'Màn hình' (chuỗi tên, không phải FN-ID) —
    WARNING, không BLOCKING: §2 lẫn cả endpoint/job không có UI, chặn cứng sẽ
    chặn oan nhóm đó (đúng loại lỗi vòng-lặp-không-thoát mà
    check_not_found_ratio từng mắc phải với unit nhỏ)."""
    screens_2 = {_strip_backtick(row[0])
                 for row in _table_data_rows(_section_body(text, 2, strip=False))
                 if row and row[0]}
    items_11 = parse_section11(text)
    screens_11 = {i["man_hinh"] for i in items_11}

    out = []
    missing = screens_2 - screens_11
    if missing:
        out.append({"loai": "man-hinh-thieu-dieu-khien",
                    "thong_diep": "§2 có màn hình chưa có dòng nào ở §11 (kể cả "
                                   "dòng 'không-có-UI' giải trình): "
                                   + ", ".join(sorted(missing))})
    unknown = screens_11 - screens_2
    if unknown:
        out.append({"loai": "man-hinh-o-muc-11-khong-khop-muc-2",
                    "thong_diep": "§11 có tên màn hình không khớp §2 (có thể gõ sai): "
                                   + ", ".join(sorted(unknown))})
    return out


def parse_section12(text: str) -> list[dict]:
    """§12 'Kịch bản Use Case' → list các {"use_case":.., "man_hinh":..}. Khối lồng
    ### KHÔNG phải bảng — không dùng _table_rows/_table_data_rows như §11, mà quét
    từng dòng trong _section_body(text, 12, strip=False) tìm heading ### (tên use
    case) và dòng field '- **Màn hình**: ...' BẤT KỂ VỊ TRÍ trong khối (không giả
    định field Màn hình luôn là bullet đầu tiên — khác §11 dùng cột cố định).
    strip=False + _strip_backtick: cùng lý do đã ghi ở _section_body/parse_section11,
    giữ nguyên nội dung bọc backtick để so khớp §2 đúng."""
    out = []
    current_name = None
    for line in _section_body(text, 12, strip=False).splitlines():
        h = SECTION12_HEADING_RE.match(line.strip())
        if h:
            current_name = h.group(1).strip()
            continue
        m = MAN_HINH_FIELD_RE.match(line.strip())
        if m and current_name is not None:
            out.append({"use_case": current_name, "man_hinh": _strip_backtick(m.group(1))})
    return out


def check_section12_coverage(text: str) -> list[dict]:
    """§12 liên kết với §2 qua field 'Màn hình' (chuỗi tên, không phải FN-ID) — cùng
    khoá liên kết §11 đã dùng. WARNING, không BLOCKING: cùng lý do
    check_section11_coverage — §2 lẫn cả endpoint không có UI/use case thật, chặn
    cứng sẽ chặn oan nhóm đó."""
    screens_2 = {_strip_backtick(row[0])
                 for row in _table_data_rows(_section_body(text, 2, strip=False))
                 if row and row[0]}
    items_12 = parse_section12(text)
    screens_12 = {i["man_hinh"] for i in items_12}

    out = []
    missing = screens_2 - screens_12
    if missing:
        out.append({"loai": "man-hinh-thieu-usecase",
                    "thong_diep": "§2 có màn hình chưa có use case nào ở §12: "
                                   + ", ".join(sorted(missing))})
    unknown = screens_12 - screens_2
    if unknown:
        out.append({"loai": "man-hinh-o-muc-12-khong-khop-muc-2",
                    "thong_diep": "§12 có tên màn hình không khớp §2 (có thể gõ sai): "
                                   + ", ".join(sorted(unknown))})
    return out


def verify(text: str, expected: list[dict], before: str | None = None) -> dict:
    blocking: list[dict] = []
    warnings: list[dict] = []
    m = len(expected)

    for ph in find_placeholders(text):
        blocking.append({"loai": "placeholder",
                         "thong_diep": f"Còn placeholder ở dòng {ph['line']}: {ph['text']}"})

    blocking.extend(check_section1_coverage(text, expected))
    blocking.extend(check_not_found_ratio(text, expected))
    blocking.extend(check_section8_cap(text, m))
    if before is not None:
        blocking.extend(check_no_clobber_8(text, before))
        blocking.extend(check_no_clobber_10(text, before))

    warnings.extend(check_cite_quality(text))
    warnings.extend(check_section2_anchor(text, expected))
    warnings.extend(check_section11_coverage(text))
    warnings.extend(check_section12_coverage(text))
    warnings.extend(check_ghi_chu_evidence(text))

    return {"blocking": blocking, "warnings": warnings}


def main(argv=None):
    p = argparse.ArgumentParser(description="Chấm intel.md trước khi báo xong")
    p.add_argument("intel", help="Đường dẫn tới intel.md")
    p.add_argument("--functions", default=".specify/docs/functions.json")
    p.add_argument("--root", required=True,
                   help="FN-ID gốc của unit (giá trị đã dùng ở intel_tree.py units)")
    p.add_argument("--before", default=None,
                   help="File chụp bản intel.md trước khi ghi, để kiểm no-clobber")
    a = p.parse_args(argv)

    text = Path(a.intel).read_text(encoding="utf-8")
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    node = ft.find_by_id(tree, a.root)
    if node is None:
        raise SystemExit(f"Không có {a.root} trong {a.functions}.")
    expected = [{"id": n["id"], "name": n["name"]} for n in ft.subtree_leaves(node)]

    before = Path(a.before).read_text(encoding="utf-8") if a.before else None
    report = verify(text, expected, before)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    n_b, n_w = len(report["blocking"]), len(report["warnings"])
    print(f"\n{n_b} lỗi chặn, {n_w} cảnh báo.", file=sys.stderr)
    if n_b:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
