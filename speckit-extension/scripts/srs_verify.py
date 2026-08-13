#!/usr/bin/env python3
"""Chấm .specify/docs/<đường-dẫn-cây>/srs.md trước khi báo xong.

Hai mức:
  BLOCKING (exit 1) — chỉ thứ kiểm được TẤT ĐỊNH: FN-ID trong phạm vi thiếu
                      mặt trong mọi <!-- FN: ... -->, và placeholder [...] còn sót.
  WARNING  (exit 0) — thứ cần phán đoán: Chức năng/Màn hình thiếu mục con, chuỗi
                      trông giống đường dẫn code, mục rỗng. In ra để người soát.

Tài liệu mô phỏng đúng cấu trúc 4 cấp của bản ban hành thật (Nhóm > Chức năng >
Sơ đồ/Mục đích/Mô tả chức năng > Màn hình khi ≥2 > a.-h.) — không còn khuôn I-VI
tự đặt trước đây, nên không còn "ma trận truy vết" hay "--template" khách hàng để
đối chiếu. FN-ID được kiểm qua comment ẩn <!-- FN: ... --> thay cho ma trận.

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
FN_COMMENT_RE = re.compile(r"<!--\s*FN:(.*?)-->", re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FENCE_RE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PLACEHOLDER_RE = re.compile(r"\[([^\[\]\n]{1,80})\](?!\()")
CHECKBOX_RE = re.compile(r"^[ x]$")
CODE_PATH_RE = re.compile(
    r"\b[\w.-]+/[\w./-]*\.\w{1,5}\b"
    r"|\b\w[\w.-]*\.(?:py|ts|tsx|js|jsx|java|cs|go|rb|php|vue|sql|kt|swift|yml|yaml)\b(?::\d+)?"
)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
NUM_PREFIX_RE = re.compile(r"^[\d.]+\s*")


def _strip_num_prefix(title: str) -> str:
    """Bỏ tiền tố số vị trí kiểu `2.1.3. ` khỏi tiêu đề đã parse trước khi so
    khớp tên mục cố định. `#### Sơ đồ chức năng`/`Mục đích chức năng`/`Mô tả
    chức năng` và `###### a.`-`h.` là mục CỐ ĐỊNH, TÊN CỐ ĐỊNH — không đánh số vị
    trí — nhưng đây là phòng vệ chiều sâu (defense-in-depth) phòng khi agent lỡ
    đánh số nhầm, để cổng kiểm cấu trúc không âm thầm tắt hẳn."""
    return NUM_PREFIX_RE.sub("", title).strip()

LETTER_ITEMS = [
    "a. Đối tượng tham gia", "b. Điều kiện thực hiện", "c. Mô hình Usecase",
    "d. Kịch bản trường hợp sử dụng", "e. Thiết kế mô hình nghiệp vụ",
    "f. Thiết kế UX/UI", "g. Mô tả điều khiển", "h. Yêu cầu nghiệp vụ",
]
CHUC_NANG_MUC = ["Sơ đồ chức năng", "Mục đích chức năng", "Mô tả chức năng"]


def strip_noise(text: str) -> str:
    """Bỏ HTML comment, khối code rào, và inline code. Cả ba chứa dấu [] hợp lệ:
    comment là hướng dẫn của khung, khối mermaid dùng B[Nhập thông tin], và bảng
    ký hiệu mermaid tự viết cú pháp trong inline code — không lọc inline code thì
    chính khung ban hành cũng không bao giờ qua được cổng của chính nó."""
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def _preserve_inline_code(text: str) -> str:
    """Giống `strip_noise` nhưng chỉ bỏ DẤU backtick, GIỮ nguyên nội dung inline
    code — dùng riêng cho quét đường dẫn code (`nghi-duong-dan-code`). Bọc một
    đường dẫn thật trong backtick không được né cảnh báo này; khác placeholder
    (`find_placeholders`, vẫn dùng `strip_noise`), nơi nội dung trong backtick cố
    ý bị bỏ qua vì đó thường là ví dụ cú pháp mermaid, không phải nội dung tài
    liệu thật."""
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = INLINE_CODE_RE.sub(lambda m: m.group(0).strip("`"), text)
    return text


def find_placeholders(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(strip_noise(text).splitlines(), start=1):
        for m in PLACEHOLDER_RE.finditer(line):
            inner = m.group(1)
            if CHECKBOX_RE.match(inner):
                continue
            out.append({"line": i, "text": m.group(0)})
    return out


def parse_fn_comments(text: str) -> set[str]:
    """Tập FN-ID trong mọi `<!-- FN: FN-ID, FN-ID... -->` — đọc trên TEXT GỐC
    (chưa strip_noise), vì strip_noise xoá sạch mọi HTML comment. Đây là cơ chế
    thay thế ma trận truy vết cũ: mỗi Chức năng mang một comment ẩn liệt kê FN-ID
    nó phủ, không hiện khi xem tài liệu."""
    ids: set[str] = set()
    for m in FN_COMMENT_RE.finditer(text):
        ids.update(FN_ID_RE.findall(m.group(1)))
    return ids


def _sections_at_level(text: str, level: int) -> list[tuple[str, str]]:
    """[(tiêu đề, nội dung)] cho mọi heading đúng `level` dấu `#`, nội dung tới
    trước heading cùng cấp hoặc cao hơn (ít dấu `#` hơn) kế tiếp. Hàm tổng quát
    thay cho các parser ad-hoc theo số mục "## N." cũ — khuôn mới đặt tên mục
    bằng chữ (Chức năng, Màn hình, a.-h.), không còn đánh số cố định để bám vào."""
    src = strip_noise(text)
    lines = src.splitlines()
    marks = []
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln.strip())
        if m:
            marks.append((i, len(m.group(1)), m.group(2).strip()))
    out = []
    for idx, (i, lvl, title) in enumerate(marks):
        if lvl != level:
            continue
        end = len(lines)
        for j in range(idx + 1, len(marks)):
            if marks[j][1] <= level:
                end = marks[j][0]
                break
        out.append((title, "\n".join(lines[i + 1:end])))
    return out


def wanted_functions(tree: list[dict], root: str) -> list[str]:
    """FN-ID lá thuộc nhánh `root` trong cây functions.json — `root` rỗng
    nghĩa là toàn cây."""
    if not root and not tree:
        return []
    if root:
        node = ft.find_by_id(tree, root)
        if node is None:
            raise ValueError(f"Không có {root} trong cây functions.")
    else:
        node = {"children": tree}
    return [n["id"] for n in ft.subtree_leaves(node)]


def check_fn_coverage(text: str, wanted: list[str]) -> list[dict]:
    """Mọi FN trong phạm vi phải xuất hiện trong ít nhất một
    `<!-- FN: ... -->` — thay thế hoàn toàn vai trò `thieu-fn` của ma trận truy
    vết cũ."""
    covered = parse_fn_comments(text)
    missing = [f for f in wanted if f not in covered]
    if not missing:
        return []
    return [{
        "loai": "thieu-fn",
        "thong_diep": "Thiếu FN-ID trong mọi <!-- FN: ... --> của tài liệu: "
                      + ", ".join(missing),
        "goi_y": "Thêm FN-ID đó vào comment <!-- FN: ... --> của Chức năng tương ứng.",
    }]


def check_chuc_nang_structure(text: str) -> list[dict]:
    """Mỗi Chức năng (`###`) phải có đủ 3 mục con Sơ đồ chức năng/Mục đích chức
    năng/Mô tả chức năng — WARNING (không BLOCKING) vì gate này chỉ soát HEADING
    có mặt hay không, không soát nội dung rỗng/đầy (nội dung rỗng thuộc gate
    khác — `_empty_sections`/`check_content_density`)."""
    out = []
    for cn_title, cn_body in _sections_at_level(text, 3):
        have = {_strip_num_prefix(t) for t, _ in _sections_at_level(cn_body, 4)}
        missing = [m for m in CHUC_NANG_MUC if m not in have]
        if missing:
            out.append({
                "loai": "chuc-nang-thieu-muc",
                "thong_diep": f"Chức năng '{cn_title}' thiếu mục: " + ", ".join(missing),
            })
    return out


def check_man_hinh_structure(text: str) -> list[dict]:
    """Trong mỗi 'Mô tả chức năng' của một Chức năng, cả 8 mục a.-h. phải có mặt
    Ở ĐÂU ĐÓ trong toàn bộ mục đó — kiểm gộp theo Chức năng, KHÔNG tách riêng
    từng khối `#####` (một Chức năng có nhiều khối `#####`, mỗi khối ứng với một
    leaf FN-ID; tách đúng theo từng khối đòi một parser phức tạp hơn nhiều cho
    một gate chỉ ở mức WARNING — chấp nhận: nếu Chức năng có 2 khối mà một khối
    thiếu mục X còn khối kia có mục X, gate này không phát hiện được, chỉ bắt ca
    thiếu mục X ở TẤT CẢ khối `#####` của Chức năng đó)."""
    out = []
    for cn_title, cn_body in _sections_at_level(text, 3):
        for mt_title, mt_body in _sections_at_level(cn_body, 4):
            if _strip_num_prefix(mt_title) != "Mô tả chức năng":
                continue
            have = {_strip_num_prefix(t) for t, _ in _sections_at_level(mt_body, 6)}
            missing = [it for it in LETTER_ITEMS if it not in have]
            if missing:
                out.append({
                    "loai": "man-hinh-thieu-muc",
                    "thong_diep": f"Chức năng '{cn_title}': thiếu mục "
                                  + ", ".join(missing)
                                  + " (có thể thiếu ở một hoặc nhiều màn hình).",
                })
    return out


def _fence_sentinel(text: str) -> str:
    """Giống `strip_noise` nhưng KHÔNG xoá trắng nội dung khối rào (```...```) —
    thay bằng một ký tự sentinel không rỗng, giữ nguyên số dòng. Dùng riêng cho
    kiểm tra "mục rỗng": một mục chỉ chứa sơ đồ mermaid (không có văn xuôi) vẫn
    phải được coi là CÓ nội dung, dù `strip_noise` (dùng cho các kiểm tra khác,
    nơi nội dung khối rào không liên quan) xoá sạch fence."""
    def repl(m: re.Match) -> str:
        return "x" + "\n" * m.group(0).count("\n")

    out = FENCE_RE.sub(repl, text)
    out = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), out)
    out = INLINE_CODE_RE.sub("", out)
    return out


_EMPTY_ITEM_RE = re.compile(
    r"^-?\s*(chưa có thông tin|không có|_\(cần chèn ảnh — không tự sinh\)_)\.?$", re.I)


def _all_headings(text: str) -> list[tuple[int, int, str]]:
    """[(dòng, cấp, tiêu đề)] cho MỌI heading trong toàn văn bản (theo bản đã
    `strip_noise`, để không nhầm heading giả trong comment/fence)."""
    lines = strip_noise(text).splitlines()
    marks = []
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln.strip())
        if m:
            marks.append((i, len(m.group(1)), m.group(2).strip()))
    return marks


def check_content_density(text: str) -> list[dict]:
    """Chức năng mà TẤT CẢ mục a.-h. (gộp mọi màn hình) đều rỗng hoặc chỉ ghi
    "Chưa có thông tin"/"Không có" → BLOCKING. `check_fn_coverage` một mình
    không bắt được ca này: comment `<!-- FN: ... -->` đủ FN nhưng tài liệu rỗng
    ruột vẫn qua được gate FN. Dùng bản giữ nguyên khối mermaid (`_fence_sentinel`)
    để không tính oan một mục chỉ có sơ đồ (không văn xuôi) là rỗng — cùng lý do
    `_empty_sections` đã phải xử lý riêng ca này."""
    marks = _all_headings(text)
    fill_lines = _fence_sentinel(text).splitlines()

    def body_of(idx: int) -> str:
        end = len(fill_lines)
        for j in range(idx + 1, len(marks)):
            if marks[j][1] <= marks[idx][1]:
                end = marks[j][0]
                break
        return "".join(x.strip() for x in fill_lines[marks[idx][0] + 1:end])

    out = []
    for idx, (i, lvl, title) in enumerate(marks):
        if lvl != 3:
            continue
        end = len(marks)
        for j in range(idx + 1, len(marks)):
            if marks[j][1] <= 3:
                end = j
                break
        item_idx = [j for j in range(idx + 1, end)
                    if marks[j][1] == 6 and _strip_num_prefix(marks[j][2]) in LETTER_ITEMS]
        if not item_idx:
            continue
        has_content = any(
            body_of(j) and not _EMPTY_ITEM_RE.match(body_of(j)) for j in item_idx
        )
        if not has_content:
            out.append({
                "loai": "chuc-nang-rong-ruot",
                "thong_diep": f"Chức năng '{title}': mọi mục a.-h. đều rỗng hoặc "
                              "'Chưa có thông tin' — tài liệu chưa thật sự đặc tả.",
                "goi_y": "Rót lại từ intel.md; nếu unit này thật sự không có căn cứ "
                         "nào thì kiểm tra lại phạm vi FN đã chọn có đúng không.",
            })
    return out


_CHUC_NANG_HEADING_RE = re.compile(r"^###\s+(.+)$", re.M)


def _chuc_nang_fn_list(text: str) -> list[tuple[str, frozenset]]:
    """[(tiêu đề Chức năng đã bỏ số vị trí, tập FN-ID nó phủ), ...] — MỘT MỤC
    cho MỖI khối `###`, kể cả khi hai khối trùng tên (hai Chức năng khác Nhóm
    có thể trùng tên hiển thị, vd cả hai đều tên "Danh sách"). Trả `list`,
    KHÔNG phải `dict` theo tên: gom vào dict sẽ để khối trùng tên sau đè mất
    FN-ID của khối trùng tên trước, tự tạo lại đúng loại lỗi no-clobber này
    được viết ra để bắt. Đọc trên TEXT GỐC (không strip_noise, để giữ được
    `<!-- FN: ... -->` — strip_noise xoá sạch mọi HTML comment)."""
    out: list[tuple[str, frozenset]] = []
    marks = list(_CHUC_NANG_HEADING_RE.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        title = _strip_num_prefix(m.group(1).strip())
        out.append((title, frozenset(parse_fn_comments(body))))
    return out


def check_no_clobber_chuc_nang(text: str, before: str | None) -> list[dict]:
    """Chạy lại không được làm MẤT HẲN nội dung của một Chức năng đã có trong
    bản trước — dấu hiệu rõ nhất của việc ghi đè nội dung BA đã sửa tay mà
    không giữ lại. So theo TẬP FN-ID mỗi Chức năng phủ, KHÔNG so theo tên/số
    thứ tự: tên có thể đổi hợp lệ khi `intel.md` đổi tên hiển thị, số thứ tự
    LUÔN đổi mỗi lần chạy theo thiết kế (bước 8 của `srs-from-code.md`: đánh số
    theo vị trí, không lưu cố định) — so theo tên/số nguyên văn sẽ báo giả mỗi
    khi có Chức năng mới chen vào giữa, dù nội dung không hề mất.

    Một Chức năng ở bản trước được coi là "còn" nếu CÓ ÍT NHẤT MỘT FN-ID của
    nó vẫn được một khối Chức năng bất kỳ ở bản mới phủ — đòi khớp NGUYÊN cả
    tập sẽ tự gãy ngay khi `intel.md` thêm/bớt một FN trong cùng Chức năng,
    một thay đổi hợp lệ hoàn toàn bình thường giữa hai lần chạy."""
    if before is None:
        return []
    old_list = _chuc_nang_fn_list(before)
    new_ids: set[str] = set()
    for _, ids in _chuc_nang_fn_list(text):
        new_ids |= ids
    out = []
    for title, ids in old_list:
        if ids and not (ids & new_ids):
            out.append({
                "loai": "mat-chuc-nang",
                "thong_diep": f"Chức năng '{title}' (phủ {', '.join(sorted(ids))}) "
                              "có ở bản trước nhưng không FN-ID nào của nó còn được "
                              "phủ ở bản mới.",
                "goi_y": "Kiểm lại có phải bị ghi đè nhầm không — FN-ID đó vẫn còn "
                         "trong phạm vi thì phải có mặt ở MỘT khối Chức năng nào đó, "
                         "dù đổi tên hay đổi số thứ tự.",
            })
    return out


def _empty_sections(text: str) -> list[dict]:
    """Mục có heading nhưng thân rỗng. Hai ca KHÔNG được coi là rỗng dù thân trực
    tiếp trống trơn:

    - Heading container (heading kế tiếp NGAY SAU nó sâu hơn, vd `## Nhóm` ngay
      trước `### Chức năng`) — nội dung của nó nằm hoàn toàn ở các heading con
      sâu hơn, tự thân nó không bao giờ có "thân" riêng.
    - Mục chỉ chứa khối mermaid (không văn xuôi) — kiểm bằng `_fence_sentinel`
      thay vì `strip_noise`, để fence không bị xoá thành rỗng oan.
    """
    marked = strip_noise(text)
    lines = marked.splitlines()
    fill_lines = _fence_sentinel(text).splitlines()
    heads = []
    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln.strip())
        if m:
            heads.append((i, len(m.group(1)), ln.strip()))
    out = []
    for n, (i, lvl, ln) in enumerate(heads):
        if n + 1 < len(heads) and heads[n + 1][1] > lvl:
            continue  # container: heading kế tiếp sâu hơn -> không có thân riêng
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        body = "".join(x.strip() for x in fill_lines[i + 1:end])
        if not body.replace("-", "").strip():
            out.append({"line": i + 1, "text": ln})
    return out


def verify(srs_text: str, wanted: list[str], before: str | None = None) -> dict:
    blocking, warnings = [], []

    blocking.extend(check_fn_coverage(srs_text, wanted))
    blocking.extend(check_content_density(srs_text))
    blocking.extend(check_no_clobber_chuc_nang(srs_text, before))

    if not wanted:
        warnings.append({
            "loai": "pham-vi-rong",
            "thong_diep": "Không có chức năng lá nào trong phạm vi đang kiểm.",
        })

    for ph in find_placeholders(srs_text):
        blocking.append({
            "loai": "placeholder",
            "thong_diep": f"Còn placeholder ở dòng {ph['line']}: {ph['text']}",
            "goi_y": "Điền nội dung, ghi 'Không có', hoặc xoá cả mục con.",
        })

    warnings.extend(check_chuc_nang_structure(srs_text))
    warnings.extend(check_man_hinh_structure(srs_text))

    for i, line in enumerate(_preserve_inline_code(srs_text).splitlines(), start=1):
        for m in CODE_PATH_RE.finditer(line):
            warnings.append({
                "loai": "nghi-duong-dan-code",
                "thong_diep": f"Dòng {i} có chuỗi trông giống đường dẫn code: {m.group(0)}",
                "goi_y": "Tài liệu giao khách nên không nêu đường dẫn mã nguồn. "
                         "Nếu đây là tên file nghiệp vụ hợp lệ thì bỏ qua cảnh báo này.",
            })

    warnings.extend({"loai": "muc-rong",
                     "thong_diep": f"Mục rỗng ở dòng {e['line']}: {e['text']}"}
                    for e in _empty_sections(srs_text))

    return {"blocking": blocking, "warnings": warnings}


def main(argv=None):
    p = argparse.ArgumentParser(description="Chấm srs.md trước khi báo xong")
    p.add_argument("srs", help="Đường dẫn .specify/docs/<đường-dẫn-cây>/srs.md")
    p.add_argument("--functions", default=".specify/docs/functions.json")
    p.add_argument("--root", default="",
                   help="FN-ID gốc của phạm vi; rỗng = toàn cây")
    p.add_argument("--before", default=None,
                   help="File chụp bản srs.md trước khi ghi, để kiểm no-clobber")
    a = p.parse_args(argv)

    srs = Path(a.srs).read_text(encoding="utf-8")
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    try:
        wanted = wanted_functions(tree, a.root)
    except ValueError as e:
        raise SystemExit(str(e))
    before = Path(a.before).read_text(encoding="utf-8") if a.before else None

    report = verify(srs, wanted, before)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    n_b, n_w = len(report["blocking"]), len(report["warnings"])
    print(f"\n{n_b} lỗi chặn, {n_w} cảnh báo.", file=sys.stderr)
    if n_b:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
