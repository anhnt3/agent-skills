#!/usr/bin/env python3
"""Chấm .specify/docs/<đường-dẫn-cây>/srs.md trước khi báo xong.

Hai mức:
  BLOCKING (exit 1) — chỉ thứ kiểm được TẤT ĐỊNH: FN-ID trong phạm vi thiếu
                      mặt trong mọi <!-- FN: ... -->, và placeholder [...] còn sót.
  WARNING  (exit 0) — thứ cần phán đoán: Chức năng/Màn hình thiếu mục con, chuỗi
                      trông giống đường dẫn code, mục rỗng. In ra để người soát.

Tài liệu mô phỏng đúng cấu trúc 4 cấp của bản ban hành thật (Nhóm > Chức năng >
Sơ đồ/Mục đích/Mô tả chức năng > khối leaf theo FN-ID > a.-g.) — không còn khuôn I-VI
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
    chức năng` và `###### a.`-`g.` là mục CỐ ĐỊNH, TÊN CỐ ĐỊNH — không đánh số vị
    trí — nhưng đây là phòng vệ chiều sâu (defense-in-depth) phòng khi agent lỡ
    đánh số nhầm, để cổng kiểm cấu trúc không âm thầm tắt hẳn."""
    return NUM_PREFIX_RE.sub("", title).strip()

# BẢY mục (không phải tám): khuôn CỐ Ý gộp hai mục "f. Thiết kế UX/UI" và
# "g. Mô tả điều khiển" của docx ban hành làm một, để ảnh màn và bảng điều
# khiển của CÙNG một màn nằm cạnh nhau (tách rời thì phải xem hết ảnh của mọi
# use case rồi mới tới bảng điều khiển — phản ánh thật từ người đọc tài liệu).
# "Yêu cầu nghiệp vụ" vì vậy lùi từ `h.` xuống `g.`.
LETTER_ITEMS = [
    "a. Đối tượng tham gia", "b. Điều kiện thực hiện", "c. Mô hình Usecase",
    "d. Kịch bản trường hợp sử dụng", "e. Thiết kế mô hình nghiệp vụ",
    "f. Thiết kế UX/UI và Mô tả điều khiển", "g. Yêu cầu nghiệp vụ",
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


def _strip_fences_keep_comments(text: str) -> str:
    """Bỏ khối code rào (```` ``` ````) nhưng GIỮ NGUYÊN HTML comment — dùng
    cho các hàm phải đọc `<!-- FN: ... -->`/`<!-- FN-leaf: ... -->` trên text
    gốc (không thể dùng `strip_noise`, nó xoá cả comment) nhưng vẫn cần loại
    bỏ heading giả (`### `, `##### `) nằm trong ví dụ minh hoạ bọc trong khối
    rào — một khối ```` ```markdown ```` minh hoạ khung có dòng `### ...`/
    `##### ...` sẽ bị hàm quét heading thô coi là heading thật nếu không lọc
    trước, làm lệch ranh giới Chức năng/khối leaf."""
    return FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


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
    bằng chữ (Chức năng, Màn hình, a.-g.), không còn đánh số cố định để bám vào."""
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
    """Trong mỗi 'Mô tả chức năng' của một Chức năng, cả 7 mục a.-g. phải có mặt
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
    r"^(?:[-*+]|\d+[.)])?\s*\**"
    r"(chưa có thông tin|không có|_\(cần chèn ảnh — không tự sinh\)_)"
    r"\.?\**$", re.I)


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


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_STRUCTURED_ITEM_LABEL_RE = re.compile(
    r"(tên use case|mức quan trọng|người dùng|loại uc|"
    r"người sử dụng và yêu cầu|mô tả tóm tắt|thời điểm sử dụng|"
    r"luồng sự kiện chuẩn|luồng sự kiện nhỏ|tên điều khiển|mô tả điều khiển)\s*:?",
    re.I,
)
_STRUCTURED_ITEMS = {"d. Kịch bản trường hợp sử dụng",
                     "f. Thiết kế UX/UI và Mô tả điều khiển"}
_TEN_USE_CASE_FIELD_RE = re.compile(r"<b>\s*tên use case\s*:?\s*</b>[^<]*", re.I)


def _structured_item_is_empty(body: str) -> bool:
    """`d.`/`f.` LUÔN có khung bảng (HTML thô cho `d.`, markdown + placeholder
    ảnh cho `f.`) ngay cả khi rỗng nội dung —
    `_EMPTY_ITEM_RE` (khớp toàn chuỗi) không bao giờ khớp
    cả khối vì thẻ HTML/cú pháp bảng/nhãn field không phải "Chưa có thông tin"
    nhưng cũng không phải nội dung thật, khiến check_content_density coi nhầm
    MỌI Chức năng có `d.`/`f.` là không rỗng dù các mục còn lại rỗng thật (bị bắt
    quả tang: EMPTY_CHUC_NANG dùng khung `d.` mới vẫn `blocking: []`). Bóc hết
    boilerplate (thẻ HTML, nhãn field cố định, cú pháp bảng `|`/`---`), phần
    còn lại phải CHỈ là chuỗi rỗng cố định lặp lại (hoặc trắng hẳn) mới coi là
    mục thật sự rỗng.

    Field `Tên Use Case` được XOÁ CẢ LABEL LẪN VALUE (không chỉ label như các
    field khác) — value của nó suy thẳng từ tên khối `#####`/`Tên Use Case`
    (bước 5 của srs-from-code.md), tự nó không mang thông tin gì mới, nên nếu
    coi value đó là "nội dung thật" thì một `d.` chỉ điền mỗi field này (7
    field còn lại "Chưa có thông tin") vẫn cứu cả Chức năng khỏi bị chặn dù
    thực chất chưa đặc tả gì (đã xác nhận bằng agent chạy thật).

    Cùng lý do đó, placeholder ảnh cố định `_(cần chèn ảnh — không tự sinh)_`
    của mục `f.` cũng bị bóc: mục `f.` (sau khi gộp UX/UI + Mô tả điều khiển)
    LUÔN mang chuỗi này dù chưa có gì, nên coi nó là "nội dung thật" thì mọi
    `f.` đều tự cứu chính nó khỏi gate rỗng — đúng lỗi mà fix `Tên Use Case`
    vừa vá ở `d.`."""
    s = _TEN_USE_CASE_FIELD_RE.sub(" ", body)
    s = _HTML_TAG_RE.sub(" ", s)
    s = _STRUCTURED_ITEM_LABEL_RE.sub(" ", s)
    s = re.sub(r"^\s*\|[\s|:-]*\|?\s*$", " ", s, flags=re.M)
    s = s.replace("|", " ")
    s = s.replace("_(cần chèn ảnh — không tự sinh)_", " ")
    # Bỏ mọi cụm in đậm `**...**`: ở `f.` đó là tên use case (suy từ mục `d.`,
    # không mang thông tin mới — cùng lý do với `Tên Use Case`) và tên điều
    # khiển; phần MÔ TẢ điều khiển là văn xuôi thường nên vẫn sống sót, một
    # bảng có dòng dữ liệu thật vẫn được tính là có nội dung.
    s = re.sub(r"\*\*[^*]*\*\*", " ", s)
    s = re.sub(r"-?\s*(chưa có thông tin|không có)\.?", " ", s, flags=re.I)
    return not s.strip(" \t\r\n.:-")


def _heading_body(marks: list, fill_lines: list, idx: int) -> str:
    """Thân (đã fence-sentinel hoá) của heading `marks[idx]`, tới heading cùng
    cấp hoặc cao hơn kế tiếp. Dùng chung cho mọi gate soát theo cấp heading."""
    end = len(fill_lines)
    for j in range(idx + 1, len(marks)):
        if marks[j][1] <= marks[idx][1]:
            end = marks[j][0]
            break
    return "".join(x.strip() for x in fill_lines[marks[idx][0] + 1:end])


def _item_has_content(title: str, body: str) -> bool:
    """Một mục a.-g. có "nội dung thật" không — `d.`/`f.` dùng
    `_structured_item_is_empty` (bảng/HTML luôn có boilerplate dù rỗng), các
    mục còn lại so khớp `_EMPTY_ITEM_RE` toàn chuỗi."""
    if not body:
        return False
    if _strip_num_prefix(title) in _STRUCTURED_ITEMS:
        return not _structured_item_is_empty(body)
    return not _EMPTY_ITEM_RE.match(body)


def _empty_letter_blocks(text: str, level: int) -> list[str]:
    """Tiêu đề của mọi heading cấp `level` mà TẤT CẢ mục a.-g. bên trong đều
    rỗng/"Chưa có thông tin" — hàm dùng chung cho `check_content_density`
    (cấp 3, gộp theo Chức năng) và `check_leaf_content_density` (cấp 5, theo
    từng khối `#####`)."""
    marks = _all_headings(text)
    fill_lines = _fence_sentinel(text).splitlines()
    out = []
    for idx, (i, lvl, title) in enumerate(marks):
        if lvl != level:
            continue
        end = len(marks)
        for j in range(idx + 1, len(marks)):
            if marks[j][1] <= level:
                end = j
                break
        item_idx = [j for j in range(idx + 1, end)
                    if marks[j][1] == 6 and _strip_num_prefix(marks[j][2]) in LETTER_ITEMS]
        if not item_idx:
            continue
        has_content = any(
            _item_has_content(marks[j][2], _heading_body(marks, fill_lines, j))
            for j in item_idx
        )
        if not has_content:
            out.append(title)
    return out


def check_content_density(text: str) -> list[dict]:
    """Chức năng mà TẤT CẢ mục a.-g. (gộp mọi khối `#####`) đều rỗng hoặc chỉ
    ghi "Chưa có thông tin"/"Không có" → BLOCKING. `check_fn_coverage` một mình
    không bắt được ca này: comment `<!-- FN: ... -->` đủ FN nhưng tài liệu rỗng
    ruột vẫn qua được gate FN. Dùng bản giữ nguyên khối mermaid (`_fence_sentinel`)
    để không tính oan một mục chỉ có sơ đồ (không văn xuôi) là rỗng — cùng lý do
    `_empty_sections` đã phải xử lý riêng ca này. Mục `d.`/`f.` dùng
    `_structured_item_is_empty` thay vì so khớp toàn chuỗi thẳng (xem docstring
    của hàm đó). GỘP theo Chức năng (`###`) — một khối `#####` rỗng riêng lẻ
    trong khi khối khác cùng Chức năng có nội dung KHÔNG bị gate này bắt, xem
    `check_leaf_content_density` cho gate theo từng khối `#####`."""
    return [{
        "loai": "chuc-nang-rong-ruot",
        "thong_diep": f"Chức năng '{title}': mọi mục a.-g. đều rỗng hoặc "
                      "'Chưa có thông tin' — tài liệu chưa thật sự đặc tả.",
        "goi_y": "Rót lại từ intel.md; nếu unit này thật sự không có căn cứ "
                 "nào thì kiểm tra lại phạm vi FN đã chọn có đúng không.",
    } for title in _empty_letter_blocks(text, 3)]


def check_leaf_content_density(text: str) -> list[dict]:
    """Cùng luật với `check_content_density` nhưng soát RIÊNG từng khối
    `#####` (một leaf FN-ID) thay vì gộp cả Chức năng. Không có gate này thì
    thiết kế "mỗi leaf một khối, lặp nguyên vẹn a.-g. khi chung màn hình" (xem
    srs-from-code.md bước 8) có đường thoát rẻ nhất: `check_leaf_blocks` chỉ
    ép đủ SỐ khối, không ép khối nào cũng có NỘI DUNG — N-1 khối có thể là
    stub trống (chỉ heading + comment FN-leaf) mà `check_content_density` gộp
    ở cấp Chức năng không bắt được (khối 1 có nội dung là đủ để cả Chức năng
    "sạch"). Đã xác nhận bằng agent chạy thật: stub 2/3 khối rỗng vẫn
    `blocking: []` nếu chỉ có gate cấp Chức năng."""
    return [{
        "loai": "khoi-leaf-rong-ruot",
        "thong_diep": f"Khối ##### '{title}': mọi mục a.-g. đều rỗng hoặc "
                      "'Chưa có thông tin' — leaf này chưa thật sự được đặc tả "
                      "(dù Chức năng cha có thể đã đủ điều kiện qua "
                      "chuc-nang-rong-ruot nhờ khối leaf khác).",
        "goi_y": "Rót nội dung thật cho khối leaf này, hoặc nếu nó dùng chung "
                 "màn hình với một leaf khác đã viết đủ thì LẶP NGUYÊN VẸN "
                 "a.-g. của leaf đó sang đây (đúng luật bước 8).",
    } for title in _empty_letter_blocks(text, 5)]


_CHUC_NANG_HEADING_RE = re.compile(r"^###\s+(.+)$", re.M)
_MUC_HEADING_RE = re.compile(r"^#####\s+(.+)$", re.M)
LEAF_COMMENT_RE = re.compile(r"<!--\s*FN-leaf:\s*(.*?)\s*-->", re.S)


def check_leaf_blocks(text: str) -> list[dict]:
    """Thiết kế leaf-based (đợt "5 đầu mục khớp function list"): mỗi Chức năng
    (`###`) phải có MỘT khối `##### ` cho MỖI FN-ID lá nó phủ — không còn nhóm
    theo màn hình. Không có gate này thì `check_fn_coverage` một mình không
    bắt được việc model lặng lẽ quay lại gộp-theo-màn-hình (ít khối `#####`
    hơn số leaf thật) hay bỏ sót/làm sai comment `<!-- FN-leaf: ... -->` — cả
    hai đều KHÔNG ảnh hưởng tới comment `<!-- FN: ... -->` cấp Chức năng nên
    lọt qua mọi gate khác. Đọc trên TEXT ĐÃ GỠ FENCE nhưng GIỮ COMMENT (không
    `strip_noise` — nó xoá cả `<!-- FN: ... -->` lẫn `<!-- FN-leaf: ... -->`),
    để một khối ```` ``` ```` minh hoạ khung có dòng `### `/`##### ` mẫu không
    bị coi là heading thật và làm lệch ranh giới Chức năng/khối leaf."""
    text = _strip_fences_keep_comments(text)
    out = []
    # Scan mọi heading cấp <=3 (`#`, `##`, `###`) để ranh giới cuối một khối
    # `###` dừng đúng chỗ (không dừng nhầm ở `####`/`#####` con) — GIỮ cả mốc
    # cấp 1/2 để tính ranh giới, chỉ LẶP qua các mốc cấp 3 bên dưới.
    all_marks = [(mm.start(), mm.end(), len(mm.group(1)), mm.group(2).strip())
                 for mm in re.finditer(r"^(#{1,3})\s+(.+)$", text, re.M)]
    for i, (start, body_start, lvl, raw_title) in enumerate(all_marks):
        if lvl != 3:
            continue
        body_end = len(text)
        for j in range(i + 1, len(all_marks)):
            if all_marks[j][2] <= 3:
                body_end = all_marks[j][0]
                break
        cn_body = text[body_start:body_end]
        cn_title = _strip_num_prefix(raw_title)
        wanted_ids = parse_fn_comments(cn_body)
        if not wanted_ids:
            continue  # check_fn_coverage lo ca thiếu hẳn <!-- FN: ... -->

        leaf_marks = list(_MUC_HEADING_RE.finditer(cn_body))
        seen_ids: list[str] = []
        blocks_missing = []
        for k, lm in enumerate(leaf_marks):
            lend = leaf_marks[k + 1].start() if k + 1 < len(leaf_marks) else len(cn_body)
            leaf_body = cn_body[lm.end():lend]
            ids = LEAF_COMMENT_RE.findall(leaf_body)
            if len(ids) != 1:
                blocks_missing.append(lm.group(1).strip())
            else:
                seen_ids.append(ids[0].strip())

        if blocks_missing:
            out.append({
                "loai": "thieu-fn-leaf",
                "thong_diep": f"Chức năng '{cn_title}': khối ##### "
                              + ", ".join(blocks_missing)
                              + " thiếu hoặc sai comment <!-- FN-leaf: ... --> "
                                "(phải có đúng một).",
                "goi_y": "Thêm đúng một comment <!-- FN-leaf: <FN-ID> --> ngay "
                         "dưới heading của khối này.",
            })

        dup = sorted({x for x in seen_ids if seen_ids.count(x) > 1})
        if dup:
            out.append({
                "loai": "trung-fn-leaf",
                "thong_diep": f"Chức năng '{cn_title}': FN-leaf trùng lặp "
                              "giữa nhiều khối #####: " + ", ".join(dup),
                "goi_y": "Mỗi leaf FN-ID chỉ được có ĐÚNG MỘT khối ##### .",
            })

        seen_set = set(seen_ids)
        missing_blocks = sorted(wanted_ids - seen_set)
        if missing_blocks:
            out.append({
                "loai": "thieu-khoi-leaf",
                "thong_diep": f"Chức năng '{cn_title}': FN-ID "
                              + ", ".join(missing_blocks)
                              + " có trong <!-- FN: ... --> nhưng không có khối "
                                "##### FN-leaf tương ứng.",
                "goi_y": "Thêm khối ##### riêng cho từng FN-ID còn thiếu — "
                         "leaf-based nghĩa là MỖI leaf một khối, kể cả khi "
                         "trùng màn hình với leaf khác (lặp nguyên vẹn a.-g.).",
            })

        extra_blocks = sorted(seen_set - wanted_ids)
        if extra_blocks:
            out.append({
                "loai": "fn-leaf-la",
                "thong_diep": f"Chức năng '{cn_title}': khối ##### có "
                              "FN-leaf " + ", ".join(extra_blocks)
                              + " không nằm trong <!-- FN: ... --> của chính "
                                "Chức năng này.",
                "goi_y": "Kiểm lại FN-leaf có gõ đúng ID không, hoặc FN-ID đó "
                         "có bị bỏ sót khỏi comment <!-- FN: ... --> không.",
            })
    return out


def _chuc_nang_fn_list(text: str) -> list[tuple[str, frozenset]]:
    """[(tiêu đề Chức năng đã bỏ số vị trí, tập FN-ID nó phủ), ...] — MỘT MỤC
    cho MỖI khối `###`, kể cả khi hai khối trùng tên (hai Chức năng khác Nhóm
    có thể trùng tên hiển thị, vd cả hai đều tên "Danh sách"). Trả `list`,
    KHÔNG phải `dict` theo tên: gom vào dict sẽ để khối trùng tên sau đè mất
    FN-ID của khối trùng tên trước, tự tạo lại đúng loại lỗi no-clobber này
    được viết ra để bắt. Đọc trên text đã gỡ fence nhưng GIỮ comment (không
    `strip_noise` — xoá sạch mọi HTML comment, kể cả `<!-- FN: ... -->` cần
    giữ; nhưng một khối rào minh hoạ có dòng `### ` mẫu vẫn phải bị gỡ, không
    thì bị coi là heading Chức năng thật)."""
    text = _strip_fences_keep_comments(text)
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


_HTML_TABLE_BLOCK_RE = re.compile(r"<table>(.*?)</table>", re.S)
_HTML_TABLE_INNER_TAGS = ("tr", "td", "ol", "li", "div")


YCNV_SOFT_CAP = 15


def check_yeu_cau_nghiep_vu_length(text: str) -> list[dict]:
    """WARNING khi mục `g. Yêu cầu nghiệp vụ` của một khối leaf dài quá
    `YCNV_SOFT_CAP` gạch đầu dòng. Mục này là NƠI CHỐT NGHIỆP VỤ, không phải
    bản kê mọi thứ code làm — bản đã gặp thật có 38 dòng mà quá nửa là ràng
    buộc validate từng trường (đã có ở cột `Mô tả điều khiển` mục `f.`) và
    nguyên văn thông báo. Chỉ WARNING, KHÔNG BLOCKING: ranh giới "quy tắc
    quan trọng" là phán đoán, một Chức năng phức tạp thật sự có thể vượt
    ngưỡng chính đáng — cổng này chỉ buộc người soát nhìn lại, không tự quyết
    thay."""
    marks = _all_headings(text)
    fill_lines = _fence_sentinel(text).splitlines()
    out = []
    for idx, (i, lvl, title) in enumerate(marks):
        if lvl != 6 or _strip_num_prefix(title) != "g. Yêu cầu nghiệp vụ":
            continue
        end = len(fill_lines)
        for j in range(idx + 1, len(marks)):
            if marks[j][1] <= lvl:
                end = marks[j][0]
                break
        n = sum(1 for ln in fill_lines[i + 1:end] if ln.lstrip().startswith("- "))
        if n > YCNV_SOFT_CAP:
            out.append({
                "loai": "yeu-cau-nghiep-vu-dai",
                "thong_diep": f"Mục 'g. Yêu cầu nghiệp vụ' ở dòng {i + 1} có {n} gạch "
                              f"đầu dòng (ngưỡng mềm {YCNV_SOFT_CAP}).",
                "goi_y": "Soát lại và bỏ những dòng thuộc nhóm ĐÃ CÓ CHỖ KHÁC hoặc hiển "
                         "nhiên: ràng buộc định dạng/độ dài từng trường và 'trường bắt "
                         "buộc' (đã ở cột Mô tả điều khiển mục f.), nguyên văn câu thông "
                         "báo, hành vi CRUD/UI thông thường. GIỮ nguyên quy tắc phân "
                         "quyền, quy tắc trạng thái và quy tắc có ngưỡng/con số nghiệp vụ "
                         "dù trông đơn giản. Chức năng phức tạp thật sự vượt ngưỡng là "
                         "hợp lệ — nêu rõ lý do khi trình bày warning này.",
            })
    return out


def check_html_table_integrity(text: str) -> list[dict]:
    """Mục `d.` bắt buộc một khối `<table>...</table>` HTML thô liền mạch —
    một dòng trống ở giữa làm nhiều bộ render (kể cả nhiều đường xuất Word)
    coi khối HTML đã kết thúc sớm, phần còn lại rơi ra ngoài bảng thành văn
    bản thô lộ thiên (srs-from-code.md bước 8 đã cảnh báo hậu quả này, nhưng
    trước đây không cổng nào kiểm — BLOCKING vì tất định 100%, đọc y nguyên
    text gốc, không phụ thuộc phán đoán). Cũng bắt thẻ mở/đóng lệch cặp trong
    cùng khối (dấu hiệu HTML viết tay bị gõ thiếu)."""
    out = []

    # Cặp <table>/</table> ở CẢ VĂN BẢN trước, vì _HTML_TABLE_BLOCK_RE (đòi có
    # đủ cả mở lẫn đóng để match) im lặng bỏ qua ca lệch nặng nhất — 1 thẻ
    # <table> không bao giờ đóng (hoặc 1 </table> mồ côi) — chính là ca gây
    # hỏng cấu trúc nặng nhất khi xuất Word (nuốt toàn bộ phần sau vào bảng
    # hoặc ngược lại), đã bị bắt quả tang lọt qua bản đếm theo-từng-khối.
    open_positions = [mm.start() for mm in re.finditer(r"<table>", text)]
    close_positions = [mm.start() for mm in re.finditer(r"</table>", text)]
    if len(open_positions) != len(close_positions):
        extra_opens = len(open_positions) - len(close_positions)
        if extra_opens > 0:
            bad_line = text.count("\n", 0, open_positions[-1]) + 1
            detail = f"thừa {extra_opens} <table> chưa đóng (thẻ cuối ở dòng {bad_line})"
        else:
            bad_line = text.count("\n", 0, close_positions[-1]) + 1
            detail = f"thừa {-extra_opens} </table> mồ côi (thẻ cuối ở dòng {bad_line})"
        out.append({
            "loai": "html-bang-hong",
            "thong_diep": f"Số thẻ <table> ({len(open_positions)}) và </table> "
                          f"({len(close_positions)}) trong toàn văn bản không khớp — {detail}.",
            "goi_y": "Mỗi <table> phải có đúng một </table> đóng — kiểm lại toàn bộ "
                     "mục d. trong tài liệu, không chỉ khối gần vị trí báo lỗi.",
        })

    for m in _HTML_TABLE_BLOCK_RE.finditer(text):
        block, inner = m.group(0), m.group(1)
        line_no = text.count("\n", 0, m.start()) + 1
        if re.search(r"\n[ \t]*\n", inner):
            out.append({
                "loai": "html-bang-hong",
                "thong_diep": f"Bảng <table> ở dòng {line_no}: có dòng trống bên trong "
                              "— làm hỏng parser HTML thô, phần sau dòng trống có thể "
                              "rơi ra ngoài bảng thành văn bản thô khi xuất Word.",
                "goi_y": "Xoá mọi dòng trống bên trong khối <table>...</table>.",
            })
        for tag in _HTML_TABLE_INNER_TAGS:
            opens = len(re.findall(rf"<{tag}(?:\s[^>]*)?>", block))
            closes = len(re.findall(rf"</{tag}>", block))
            if opens != closes:
                out.append({
                    "loai": "html-bang-hong",
                    "thong_diep": f"Bảng <table> ở dòng {line_no}: thẻ <{tag}> không "
                                  f"cân ({opens} mở, {closes} đóng).",
                    "goi_y": f"Kiểm lại mọi <{tag}> đều có </{tag}> đóng tương ứng.",
                })
    return out


def verify(srs_text: str, wanted: list[str], before: str | None = None) -> dict:
    blocking, warnings = [], []

    blocking.extend(check_fn_coverage(srs_text, wanted))
    blocking.extend(check_content_density(srs_text))
    blocking.extend(check_leaf_content_density(srs_text))
    blocking.extend(check_no_clobber_chuc_nang(srs_text, before))
    blocking.extend(check_leaf_blocks(srs_text))
    blocking.extend(check_html_table_integrity(srs_text))

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
    warnings.extend(check_yeu_cau_nghiep_vu_length(srs_text))

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
