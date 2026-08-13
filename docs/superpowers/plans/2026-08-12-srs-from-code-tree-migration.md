# Đợt 3B-1: di trú srs-from-code/srs_verify.py sang mô hình cây — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Làm cho `srs-from-code` chạy được trở lại trên mô hình cây `functions.json` (thay vì `functions.md`/cụm phẳng đã không còn tồn tại từ đợt 1), tái dùng nguyên xi máy đã xây ở đợt 2 (`intel_tree.py propose`/`units`, cơ chế chống race qua báo-cáo-về-cha).

**Architecture:** Ba thay đổi độc lập nhưng phối hợp: (1) `srs_verify.py` đổi từ mô hình cụm phẳng (`--cluster` + `functions.md`) sang mô hình cây (`--root` + `functions.json`, dùng `fnlist_tree.subtree_leaves`); (2) `srs-from-code.md` đổi tham số nhận vào từ `<tên-cụm>` sang một FN-ID, thêm 3 bước chọn/xác nhận/batch unit ở đầu quy trình (mirror `code-intel.md`), thay bước cập nhật trạng thái tay bằng gọi `fnlist_import.py update`; (3) một câu ghi chú lỗi thời trong `code-intel.md` được xoá vì nay đã sai.

**Tech Stack:** Python 3.10 stdlib (`argparse`, `json`, `re`, `pathlib`), pytest, `fnlist_tree.py` (đã có, không sửa), `intel_tree.py` (đã có, không sửa), `fnlist_import.py` (đã có, không sửa).

## Global Constraints

- Toàn bộ tài liệu/thông điệp lỗi bằng tiếng Việt; tên flag/tham số CLI bằng tiếng Anh (`--root`, `--functions`, `--template`, `--set`).
- `FN_ID_RE` phải khớp `^FN(?:-\d{2})+$` (đa cấp) — không dùng lại pattern 3-chữ-số cũ (`FN-\d{3,}`).
- Tham số nhận vào của `srs-from-code.md` là **một FN-ID duy nhất** (trống = toàn dự án), giống hệt `code-intel.md`; không còn khái niệm "tên cụm gõ tay".
- Đường dẫn `srs.md` của một unit = đường dẫn `intel.md` của chính unit đó (từ `intel_tree.py units`), chỉ thay hậu tố `/intel.md` → `/srs.md`. Không gọi `intel_tree.py` với cờ nào khác, không viết logic suy path mới.
- Batch missing-`intel.md`: **≥ 2 unit đã chốt** → bỏ qua unit thiếu `intel.md`, chạy tiếp phần còn lại, báo rõ cuối. **Đúng 1 unit đã chốt** mà thiếu `intel.md` → dừng cứng ngay, không âm thầm bỏ qua.
- Chạy song song (≥ 2 unit runnable): subagent **không tự gọi** `fnlist_import.py update`; báo cặp `FN-ID=status` về agent cha; agent cha đợi hết rồi gọi `update` đúng một lần với mọi `--set` gộp lại. Đây là cơ chế **y hệt** `code-intel.md` đã dùng — không phát minh lại.
- Không đổi khuôn tài liệu `srs.md` (I–VI, N.1–N.7) trong đợt này. Không đổi `srs-template.md`, không đổi `intel_tree.py`.
- Không đụng nội dung §11 (điều khiển giao diện)/§12 (chưa tồn tại) — rót các mục đó là việc của 3B-3.

---

## Task 1: `srs_verify.py` — mô hình cây + CLI mới, cùng bộ test

**Files:**
- Modify: `speckit-extension/scripts/srs_verify.py` (toàn bộ)
- Modify: `speckit-extension/scripts/tests/test_srs_verify.py` (toàn bộ)

**Interfaces:**
- Produces: `wanted_functions(tree: list[dict], root: str) -> list[str]` — trả FN-ID lá thuộc nhánh `root` (`root` rỗng = toàn cây); raise `ValueError` nếu `root` không có trong cây. Thay thế hoàn toàn `cluster_functions(functions_md, cluster)` cũ (bị xoá).
- Produces: `verify(srs_text: str, wanted: list[str], template_text: str | None = None) -> dict` — đổi chữ ký so với bản cũ (`verify(srs_text, functions_md, cluster, template_text=None)`); tham số thứ hai giờ là danh sách FN-ID đã tính sẵn, không phải nội dung `functions.md` + tên cụm.
- Produces: CLI `srs_verify.py <srs> --functions <path đến functions.json> --root <FN-ID hoặc rỗng> [--template <path>]` — thay `--cluster <tên> --functions functions.md`.
- Consumes: `fnlist_tree.find_by_id`, `fnlist_tree.subtree_leaves` (đã có, không sửa — `speckit-extension/scripts/fnlist_tree.py`).

- [ ] **Step 1: Viết bộ test mới (thất bại) cho `test_srs_verify.py`**

Thay toàn bộ nội dung file bằng:

```python
import json
import sys
from pathlib import Path

import pytest

import srs_verify as sv

FUNCTIONS_TREE = [
    {"id": "FN-01", "name": "Xác thực", "description": "", "children": [
        {"id": "FN-01-01", "name": "Đăng nhập", "description": "", "children": []},
        {"id": "FN-01-02", "name": "Quên mật khẩu", "description": "", "children": []},
    ]},
    {"id": "FN-02", "name": "Hợp đồng", "description": "", "children": [
        {"id": "FN-02-01", "name": "Danh sách hợp đồng", "description": "", "children": []},
    ]},
]

WANTED = ["FN-01-01", "FN-01-02"]

SRS_OK = """# SRS — Quản lý tài khoản

**Hệ thống**: DMS
**Phiên bản tài liệu**: V1
**Ngày cập nhật**: 2026-08-10

# III. ĐẶC TẢ YÊU CẦU CHỨC NĂNG

## 1. Đăng nhập

Nội dung mô tả chức năng đăng nhập.

# V. MA TRẬN TRUY VẾT

| Mã chức năng | Tên chức năng | Mục SRS đặc tả |
| --- | --- | --- |
| FN-01-01 | Đăng nhập | III.1 |
| FN-01-02 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |
"""


def test_wanted_functions_filters_by_root():
    assert sv.wanted_functions(FUNCTIONS_TREE, "FN-01") == ["FN-01-01", "FN-01-02"]
    assert sv.wanted_functions(FUNCTIONS_TREE, "FN-02") == ["FN-02-01"]


def test_wanted_functions_empty_root_is_whole_tree():
    assert sv.wanted_functions(FUNCTIONS_TREE, "") == [
        "FN-01-01", "FN-01-02", "FN-02-01"]


def test_wanted_functions_unknown_root_raises():
    with pytest.raises(ValueError):
        sv.wanted_functions(FUNCTIONS_TREE, "FN-99")


def test_parse_matrix_collects_ids():
    assert sv.parse_matrix(SRS_OK) == {"FN-01-01", "FN-01-02"}


def test_clean_document_has_no_blocking():
    r = sv.verify(SRS_OK, WANTED, None)
    assert r["blocking"] == []


def test_out_of_scope_row_counts_as_covered():
    r = sv.verify(SRS_OK, WANTED, None)
    assert not any("FN-01-02" in b["thong_diep"] for b in r["blocking"])


def test_missing_function_is_blocking():
    srs = SRS_OK.replace(
        "| FN-01-02 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |\n", "")
    r = sv.verify(srs, WANTED, None)
    assert any(b["loai"] == "thieu-fn" and "FN-01-02" in b["thong_diep"]
               for b in r["blocking"])


def test_placeholder_is_blocking():
    srs = SRS_OK + "\n## Phụ lục A — [Tên phụ lục]\n"
    r = sv.verify(srs, WANTED, None)
    assert any(b["loai"] == "placeholder" for b in r["blocking"])


def test_markdown_link_is_not_a_placeholder():
    srs = SRS_OK + "\nXem [tài liệu tham khảo](https://example.com/a).\n"
    r = sv.verify(srs, WANTED, None)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_mermaid_block_is_not_a_placeholder():
    srs = SRS_OK + "\n```mermaid\nflowchart TD\n    B[Nhập thông tin]\n```\n"
    r = sv.verify(srs, WANTED, None)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_template_comment_placeholder_is_ignored():
    srs = SRS_OK + "\n<!-- điền [Tên phụ lục] vào đây -->\n"
    r = sv.verify(srs, WANTED, None)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


TEMPLATE = """# SRS — [TÊN CỤM]

# I. KIỂM SOÁT PHIÊN BẢN

# II. GIỚI THIỆU

# V. MA TRẬN TRUY VẾT
"""


def test_code_path_is_warning_not_blocking():
    srs = SRS_OK + "\nHành vi nằm ở src/auth/login.ts:42.\n"
    r = sv.verify(srs, WANTED, None)
    assert r["blocking"] == []
    assert any(w["loai"] == "nghi-duong-dan-code" for w in r["warnings"])


def test_missing_template_section_is_warning_only():
    r = sv.verify(SRS_OK, WANTED, TEMPLATE)
    assert r["blocking"] == []
    kinds = {w["loai"] for w in r["warnings"]}
    assert "thieu-muc" in kinds


def test_missing_sections_are_grouped_into_one_warning():
    r = sv.verify(SRS_OK, WANTED, TEMPLATE)
    thieu_muc = [w for w in r["warnings"] if w["loai"] == "thieu-muc"]
    assert len(thieu_muc) == 1
    assert "KIỂM SOÁT PHIÊN BẢN" in thieu_muc[0]["thong_diep"]
    assert "GIỚI THIỆU" in thieu_muc[0]["thong_diep"]


def test_empty_section_is_warning_only():
    srs = SRS_OK + "\n## 1.7. Giao tiếp hệ thống\n\n## 1.8. Khác\n\nCó nội dung.\n"
    r = sv.verify(srs, WANTED, None)
    assert r["blocking"] == []
    assert any(w["loai"] == "muc-rong" for w in r["warnings"])


def test_empty_wanted_list_warns():
    r = sv.verify(SRS_OK, [], None)
    assert any(w["loai"] == "pham-vi-rong" for w in r["warnings"])


def _run(tmp_path, srs_text, root="FN-01"):
    import subprocess
    srs = tmp_path / "srs.md"
    srs.write_text(srs_text, encoding="utf-8")
    fns = tmp_path / "functions.json"
    fns.write_text(json.dumps({"functions": FUNCTIONS_TREE}, ensure_ascii=False),
                   encoding="utf-8")
    script = Path(sv.__file__)
    return subprocess.run(
        [sys.executable, str(script), str(srs), "--functions", str(fns),
         "--root", root],
        capture_output=True, text=True, encoding="utf-8")


def test_cli_exits_zero_when_only_warnings(tmp_path):
    p = _run(tmp_path, SRS_OK + "\nXem src/auth/login.ts:42.\n")
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout)["warnings"]


def test_cli_exits_one_when_blocking(tmp_path):
    srs = SRS_OK.replace(
        "| FN-01-02 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |\n", "")
    p = _run(tmp_path, srs)
    assert p.returncode == 1
    assert json.loads(p.stdout)["blocking"]


def test_cli_empty_root_covers_whole_tree(tmp_path):
    # root rỗng => phạm vi gồm cả FN-02-01 (nhánh Hợp đồng); SRS_OK chỉ đặc tả
    # nhánh Xác thực nên thiếu dòng cho FN-02-01 phải bị chặn.
    p = _run(tmp_path, SRS_OK, root="")
    assert p.returncode == 1
    assert any(b["loai"] == "thieu-fn" and "FN-02-01" in b["thong_diep"]
               for b in json.loads(p.stdout)["blocking"])


def test_cli_reports_unknown_root(tmp_path):
    p = _run(tmp_path, SRS_OK, root="FN-99")
    assert p.returncode != 0
    assert "FN-99" in p.stderr


def test_inline_code_syntax_example_is_not_a_placeholder():
    srs = SRS_OK + "\n| `A([Bắt đầu])` | `B[Nhập thông tin]` | `D[[Quy trình con]]` |\n"
    r = sv.verify(srs, WANTED, None)
    assert r["blocking"] == []


NUMBERED_TEMPLATE = """# SRS — [TÊN CỤM]

# III. ĐẶC TẢ YÊU CẦU CHỨC NĂNG

## 1. [Tên chức năng]
"""

CUSTOM_TEMPLATE = """# SRS — [TÊN CỤM]

# Yêu cầu chức năng

## Chức năng: [Tên chức năng]
"""


def test_garbage_matrix_cell_is_blocking():
    srs = SRS_OK.replace(
        "| FN-01-02 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |",
        "| FN-01-02 | Quên mật khẩu | zzz |")
    r = sv.verify(srs, WANTED, NUMBERED_TEMPLATE)
    assert any(b["loai"] == "thieu-fn" and "FN-01-02" in b["thong_diep"]
               for b in r["blocking"])


def test_empty_function_section_with_fabricated_matrix_ref_is_blocking():
    srs = """# SRS — Quản lý tài khoản

**Hệ thống**: DMS

# III. ĐẶC TẢ YÊU CẦU CHỨC NĂNG

Không có.

# V. MA TRẬN TRUY VẾT

| Mã chức năng | Tên chức năng | Mục SRS đặc tả |
| --- | --- | --- |
| FN-01-01 | Đăng nhập | III.1 |
| FN-01-02 | Quên mật khẩu | III.2 |
"""
    r = sv.verify(srs, WANTED, NUMBERED_TEMPLATE)
    assert any(b["loai"] == "thieu-fn" for b in r["blocking"])


def test_document_title_not_compared_against_template_title():
    r = sv.verify(SRS_OK, WANTED, TEMPLATE)
    msgs = " ".join(w["thong_diep"] for w in r["warnings"])
    assert "TÊN CỤM" not in msgs
    assert "Quản lý tài khoản" not in msgs


def test_custom_heading_style_falls_back_instead_of_blocking():
    srs = """# SRS — Quản lý hợp đồng

# Yêu cầu chức năng

## Chức năng: Tạo hợp đồng

Nội dung.

# V. MA TRẬN TRUY VẾT

| Mã chức năng | Tên chức năng | Mục SRS đặc tả |
| --- | --- | --- |
| FN-01-01 | Đăng nhập | Chức năng: Tạo hợp đồng |
| FN-01-02 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |
"""
    r = sv.verify(srs, WANTED, CUSTOM_TEMPLATE)
    assert r["blocking"] == []
    assert any(w["loai"] == "khong-doi-chieu-duoc-muc" for w in r["warnings"])


def test_no_template_also_falls_back_with_warning():
    r = sv.verify(SRS_OK, WANTED, None)
    assert any(w["loai"] == "khong-doi-chieu-duoc-muc" for w in r["warnings"])


def test_garbage_cell_still_blocks_when_heading_style_recognised():
    r = sv.verify(SRS_OK, WANTED, NUMBERED_TEMPLATE)
    assert not any(w["loai"] == "khong-doi-chieu-duoc-muc" for w in r["warnings"])
```

- [ ] **Step 2: Chạy test, xác nhận thất bại vì import lỗi**

Run: `python -m pytest speckit-extension/scripts/tests/test_srs_verify.py -v` (dùng `python3` nếu `python` không trỏ đúng bản)
Expected: FAIL hàng loạt — `AttributeError: module 'srs_verify' has no attribute 'wanted_functions'` (hàm chưa tồn tại) và `TypeError` ở các lời gọi `sv.verify(srs, WANTED, ...)` (chữ ký cũ nhận `functions_md, cluster`, không phải `wanted`).

- [ ] **Step 3: Viết lại toàn bộ `srs_verify.py`**

Thay toàn bộ nội dung file bằng:

```python
#!/usr/bin/env python3
"""Chấm .specify/docs/<đường-dẫn-cây>/srs.md trước khi báo xong.

Hai mức, theo đúng nguyên tắc §3.3 của spec:
  BLOCKING (exit 1) — chỉ thứ kiểm được TẤT ĐỊNH: mã chức năng trong phạm vi
                      thiếu dòng trong ma trận truy vết, và placeholder [...] còn sót.
  WARNING  (exit 0) — thứ cần phán đoán: mục khung bị thiếu/lệch, chuỗi trông
                      giống đường dẫn code, mục con rỗng. In ra để người soát.

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
CHECKBOX_RE = re.compile(r"^[ x]$")
CODE_PATH_RE = re.compile(
    r"\b[\w.-]+/[\w./-]*\.\w{1,5}\b"
    r"|\b\w[\w.-]*\.(?:py|ts|tsx|js|jsx|java|cs|go|rb|php|vue|sql|kt|swift|yml|yaml)\b(?::\d+)?"
)
FUNC_HEADING_RE = re.compile(r"^##\s+(\d+)\.", re.M)
OUT_OF_SCOPE_RE = re.compile(r"^\s*ngoài\s*phạm\s*vi", re.I)


def strip_noise(text: str) -> str:
    """Bỏ HTML comment, khối code rào, và inline code. Cả ba chứa dấu [] hợp lệ:
    comment là hướng dẫn của khung, khối mermaid dùng B[Nhập thông tin], và bảng
    ký hiệu mermaid của srs-template.md tự nó viết cú pháp trong inline code
    (`A([Bắt đầu])`) — không lọc inline code thì chính khung ban hành cũng
    không bao giờ qua được cổng của chính nó."""
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = INLINE_CODE_RE.sub("", text)
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


def _table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def _function_numbers(text: str) -> set[str]:
    """Số của mọi mục "## N." (chức năng) thật sự có trong tài liệu."""
    return set(FUNC_HEADING_RE.findall(strip_noise(text)))


def _matrix_cell_valid(cell: str, func_numbers: set[str]) -> bool:
    """Cột "Mục SRS đặc tả" phải trỏ tới một mục có thật, hoặc khai ngoài phạm
    vi — không chấp nhận nội dung bất kỳ chỉ vì FN-ID ở cột đầu có thật. Không
    kiểm nội dung cột này thì một dòng ma trận giả (FN-ID thật, cột cuối viết
    bừa) vẫn được tính là đã phủ, biến cổng nghiệm thu thành hình thức."""
    if OUT_OF_SCOPE_RE.match(cell.strip()):
        return True
    return any(n in func_numbers for n in re.findall(r"\d+", cell))


def parse_matrix(text: str, strict: bool = True) -> set[str]:
    """Nhận diện bảng ma trận bằng TIÊU ĐỀ CỘT, không bằng số mục — dự án được
    phép thêm/đổi mục nên "mục V" không đáng tin, "Mã chức năng" thì đáng.

    `strict` quyết định có kiểm nội dung cột "Mục SRS đặc tả" hay không. Cờ
    này PHẢI được tính từ KHUNG đang dùng (xem `verify()`), KHÔNG được tính từ
    chính `text` — nếu tính từ `text`, một tài liệu bỏ trống hẳn mục chức năng
    (không có "## N." nào) sẽ tự động thành "lenient" và bất kỳ nội dung nào ở
    cột "Mục SRS đặc tả" cũng được chấp nhận, tái tạo đúng lỗ tài liệu-rỗng-
    vẫn-pass mà việc kiểm cột này sinh ra để chặn."""
    ids: set[str] = set()
    func_numbers = _function_numbers(text)
    in_matrix = False
    for row in _table_rows(text):
        joined = " ".join(row).lower()
        if "mã chức năng" in joined and "mục srs" in joined:
            in_matrix = True
            continue
        if in_matrix:
            if all(set(c) <= set("-: ") for c in row):
                continue
            m = FN_ID_RE.search(row[0]) if row else None
            if m:
                cell = row[2] if len(row) > 2 else ""
                if not strict or _matrix_cell_valid(cell, func_numbers):
                    ids.add(m.group(0))
            elif row and row[0] and not FN_ID_RE.search(row[0]):
                in_matrix = False
    return ids


def wanted_functions(tree: list[dict], root: str) -> list[str]:
    """FN-ID lá thuộc nhánh `root` trong cây functions.json — `root` rỗng
    nghĩa là toàn cây. Thay thế `cluster_functions()` của mô hình cụm phẳng cũ:
    một node cây chỉ có đúng một đường dẫn tới gốc, nên "một FN thuộc nhiều
    cụm" không còn là chuyện phải xử lý."""
    if root:
        node = ft.find_by_id(tree, root)
        if node is None:
            raise ValueError(f"Không có {root} trong cây functions.")
    else:
        node = {"children": tree}
    return [n["id"] for n in ft.subtree_leaves(node)]


def _top_headings(text: str) -> list[str]:
    """Tiêu đề cấp 1, BỎ tiêu đề đầu tiên — đó luôn là tên tài liệu (kèm tên
    cụm) hoặc placeholder tên cụm của khung, hai chuỗi này không bao giờ khớp
    nhau ở bất kỳ tài liệu thật nào nên so chúng chỉ tạo cảnh báo rác cố định
    mỗi lần chạy."""
    heads = [ln.strip().lstrip("#").strip()
             for ln in strip_noise(text).splitlines()
             if re.match(r"^#\s+\S", ln.strip())]
    return heads[1:] if heads else heads


def _empty_sections(text: str) -> list[dict]:
    lines = strip_noise(text).splitlines()
    heads = [(i, ln) for i, ln in enumerate(lines) if re.match(r"^#{1,4}\s+\S", ln.strip())]
    out = []
    for n, (i, ln) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        body = "".join(x.strip() for x in lines[i + 1:end])
        if not body.replace("-", "").strip():
            out.append({"line": i + 1, "text": ln.strip()})
    return out


def verify(srs_text: str, wanted: list[str],
           template_text: str | None = None) -> dict:
    blocking, warnings = [], []

    # strict tính từ KHUNG (template_text), không tính từ srs_text — xem docstring
    # của parse_matrix(). Không có --template, hoặc khung đó không dùng kiểu đánh
    # mục "## N.", thì không đối chiếu được nội dung cột, chỉ kiểm sự có mặt của
    # mã FN (lenient) và báo cho người soát biết qua cảnh báo bên dưới.
    template_func_numbers = _function_numbers(template_text) if template_text else set()
    strict = bool(template_func_numbers)
    covered = parse_matrix(srs_text, strict=strict)
    missing = [f for f in wanted if f not in covered]
    if missing:
        blocking.append({
            "loai": "thieu-fn",
            "thong_diep": "Thiếu dòng trong ma trận truy vết: " + ", ".join(missing),
            "goi_y": "Thêm một dòng cho mỗi mã; chức năng không đặc tả thì "
                     "cột cuối ghi 'Ngoài phạm vi — <lý do>'.",
        })
    if not strict:
        warnings.append({
            "loai": "khong-doi-chieu-duoc-muc",
            "thong_diep": "Không xác định được kiểu đánh mục '## N.' từ khung đang dùng "
                          "(không có --template, hoặc khung đó không dùng kiểu đánh mục "
                          "này) — script KHÔNG đối chiếu được cột 'Mục SRS đặc tả' có trỏ "
                          "đúng chỗ không, chỉ kiểm mã FN có mặt. Soát tay từng dòng "
                          "ma trận.",
        })
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

    if template_text:
        want = _top_headings(template_text)
        have = _top_headings(srs_text)
        thieu = [h for h in want if h not in have]
        if thieu:
            # Một dòng liệt kê đủ, không phải một warning riêng mỗi mục — tài
            # liệu còn thiếu nhiều mục dễ khiến warnings dài hàng chục dòng,
            # trong khi bước 10 buộc trình toàn bộ cho người dùng.
            warnings.append({"loai": "thieu-muc",
                             "thong_diep": "Khung có " + str(len(thieu)) + " mục mà tài "
                             "liệu không có: " + "; ".join(f"'{h}'" for h in thieu)})
        if [h for h in have if h in want] != [h for h in want if h in have]:
            warnings.append({"loai": "lech-thu-tu",
                             "thong_diep": "Thứ tự mục cấp 1 khác khung."})

    for i, line in enumerate(strip_noise(srs_text).splitlines(), start=1):
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
    p.add_argument("--template", default=None,
                   help="Khung để đối chiếu tên/thứ tự mục (cảnh báo, không chặn)")
    a = p.parse_args(argv)

    srs = Path(a.srs).read_text(encoding="utf-8")
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    try:
        wanted = wanted_functions(tree, a.root)
    except ValueError as e:
        raise SystemExit(str(e))
    tpl = Path(a.template).read_text(encoding="utf-8") if a.template else None

    report = verify(srs, wanted, tpl)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    n_b, n_w = len(report["blocking"]), len(report["warnings"])
    print(f"\n{n_b} lỗi chặn, {n_w} cảnh báo.", file=sys.stderr)
    if n_b:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Chạy lại test, xác nhận toàn bộ pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_srs_verify.py -v`
Expected: PASS toàn bộ (27 test).

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/srs_verify.py speckit-extension/scripts/tests/test_srs_verify.py
git commit -m "feat(code-intel): srs_verify.py sang mô hình cây functions.json (đợt 3B-1)"
```

---

## Task 2: `srs-from-code.md` — tham số FN-ID + batch + ghi ngược qua `fnlist_import.py`

**Files:**
- Modify: `speckit-extension/commands/srs-from-code.md` (toàn bộ)

**Interfaces:**
- Consumes: `intel_tree.py propose --functions .specify/docs/functions.json [--start <FN-ID>]` (đã có, không sửa).
- Consumes: `intel_tree.py units --functions .specify/docs/functions.json --roots <FN-ID,...>` (đã có, không sửa) — trả `path` (kết thúc `/intel.md`) và `fn_ids` cho từng unit.
- Consumes: `srs_verify.py <srs> --functions .specify/docs/functions.json --root <FN-ID> [--template <path>]` (Task 1).
- Consumes: `fnlist_import.py update --file .specify/docs/functions.json --set FN-ID=srs [--set ...]` (đã có, không sửa).

Đây là file prompt/instruction (không phải code) — không có bước TDD. Bước kiểm tra là đọc lại toàn văn, đối chiếu với spec, và chạy thử chuỗi lệnh CLI mà file mô tả trên một `functions.json`/`intel.md` mẫu để xác nhận cú pháp đúng.

- [ ] **Step 1: Viết lại toàn bộ nội dung file**

Thay toàn bộ nội dung `speckit-extension/commands/srs-from-code.md` bằng:

````markdown
---
description: Sinh .specify/docs/<đường-dẫn-cây>/srs.md theo khung ban hành từ intel.md và functions.json — nhận một FN-ID gốc (trống = toàn dự án), tái dùng intel_tree.py để đề xuất/xác nhận unit rồi sinh SRS theo batch (song song/tuần tự), chỉ ghi nội dung phản ánh đúng những gì code thật sự làm, thông tin hành chính thiếu thì ghi "Chưa có thông tin", và tổng hợp một lượt cuối cùng những phát hiện logic/bảo mật đáng chú ý để hỏi người dùng.
---

# SRS từ code intel theo cây functions.json

Rót `.specify/docs/<đường-dẫn-cây>/intel.md` (tài liệu nội bộ, kèm nguồn `file:dòng`)
thành **`.specify/docs/<đường-dẫn-cây>/srs.md`** — tài liệu **giao khách**, đúng khung ban
hành, không lộ đường dẫn mã nguồn. Toàn bộ tiếng Việt. Dùng `python3` nếu `python` không có.

**Tài liệu này tập trung vào source code** — mô tả đúng những gì hệ thống *thật sự làm*
theo `intel.md`, không phải một bản diễn giải nghiệp vụ suy đoán. Hai loại thông tin xử
lý khác nhau:

- **Thông tin hành chính/nghiệp vụ thuần mà code không thể tiết lộ** (tên người ký duyệt,
  chính sách kinh doanh chỉ người mới biết…) → ghi thẳng "Chưa có thông tin" trong tài
  liệu, không đánh dấu gì đặc biệt, không dừng lại hỏi. Cuối báo cáo chỉ nhắc gọn một
  dòng — bổ sung nếu cần, không phải một cuộc trao đổi.
- **Phát hiện đáng chú ý khi đọc code** — logic mâu thuẫn, xung đột giữa các phần code,
  dấu hiệu lỗ hổng bảo mật (đã được `code-intel` ghi vào `intel §10`) → đây mới là thứ
  đáng dừng lại. Tổng hợp **một lượt** ở cuối, hỏi người dùng: cố ý thiết kế vậy hay là
  bug. **Không ghi vào `srs.md`** — tài liệu giao khách không nêu loại phát hiện này.

## User Input

`$ARGUMENTS`

Kỳ vọng: **trống, hoặc một FN-ID** — giống hệt `code-intel`:

- Trống → điểm bắt đầu là **gốc cây** — chọn unit trong toàn bộ dự án.
- `FN-01` → chỉ xét unit trong nhánh đó.
- Một FN-ID lá → đúng một unit (chính nó).

Không còn khái niệm "tên cụm gõ tay" — thư mục sinh ra tự động từ cấu trúc
`functions.json`, không phải chuỗi tự do người dùng đặt.

`--template <đường-dẫn>` (tuỳ chọn, đặt bất kỳ đâu trong `$ARGUMENTS`) → dùng khung đó
thay `srs-template.md` mặc định (khách hàng có khung riêng).

## Validate cứng trước khi làm bất cứ gì khác

- **`.specify/docs/functions.json` không tồn tại** → DỪNG, nhắc chạy
  `/speckit.dft-speckit.fnlist-import` trước.
- **Phần FN-ID của `$ARGUMENTS` không trống và không khớp `^FN(?:-\d{2})+$`** → DỪNG, in
  cú pháp hợp lệ (`FN-01`, `FN-01-01`, …), hỏi lại. Không tự đoán/tự sửa.
- **FN-ID đúng cú pháp nhưng không có trong cây** → chạy
  `python .../scripts/intel_tree.py units --functions .specify/docs/functions.json --roots <FN-ID>`
  sẽ tự báo lỗi kèm đúng FN-ID không tìm thấy — DỪNG, in nguyên thông điệp, không tự đoán
  ID gần đúng.
- **`--template <đường-dẫn>` có trong `$ARGUMENTS` nhưng đường dẫn đó không tồn tại** →
  DỪNG, báo rõ đường dẫn sai — không âm thầm rơi về khung mặc định (người dùng tưởng đang
  dùng khung riêng nhưng thực ra không phải).

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/`. Dùng `python3` nếu
`python` không có (macOS/Linux).

### 1. Đề xuất unit + xác nhận cây

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py propose \
  --functions .specify/docs/functions.json [--start <FN-ID nếu có>]
```

In ra danh sách unit đề xuất (mặc định: node có tất cả con đều là lá, hoặc node không
có con đứng một mình) kèm cây thụt lề có đánh dấu `[UNIT]`. Trình nguyên văn cây này cho
người dùng qua AskUserQuestion: xác nhận đúng ranh giới, hay muốn gộp/tách lại?

- Điều chỉnh hợp lệ: chọn một tập node KHÁC làm root của unit (sâu hơn hoặc cao hơn đề
  xuất), miễn mỗi root vẫn là một nhánh cây hợp lệ (không lẫn hai node không phải anh em
  vào cùng một unit — điều đó không được hỗ trợ).
- Chưa có phản hồi → DỪNG, không sang bước 2.
- Có điều chỉnh → dùng danh sách root người dùng chốt (không phải danh sách đề xuất mặc
  định) cho bước 2.
- Sau khi người dùng chốt danh sách root, kiểm: không root nào là tổ tiên hoặc hậu duệ
  của root khác trong **cùng danh sách** (nếu có, một FN sẽ lọt vào hai unit chồng lấn).
  Phát hiện vi phạm → DỪNG, chỉ rõ cặp root lồng nhau, hỏi lại người dùng chọn lại.

### 2. Tính đường dẫn `srs.md` + kiểm `intel.md` đã có chưa

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py units \
  --functions .specify/docs/functions.json --roots <FN-ID,FN-ID,...>
```

Với mỗi unit trả về, `path` là đường dẫn FILE `intel.md` (đã có sẵn hậu tố `/intel.md`),
TƯƠNG ĐỐI so với `.specify/docs/`. Suy đường dẫn `srs.md` của unit bằng cách **thay hậu
tố**: `path.replace("/intel.md", "/srs.md")` — cùng thư mục với `intel.md`, không gọi lại
`intel_tree.py` với tham số khác, không viết logic suy path mới.

Đọc thêm hai trường top-level của `.specify/docs/functions.json`: `system` → điền
**Hệ thống**, `updated` → điền **Ngày cập nhật** ở đầu mỗi `srs.md` sẽ sinh (dùng chung
cho mọi unit trong lần chạy này). Không tự bịa hai giá trị này — thiếu thì ghi "Chưa có
thông tin" (giữ nguyên luật cũ ở bước 8, chỉ đổi nguồn đọc từ `functions.md` sang
`functions.json`).

Với mỗi unit đã chốt, kiểm sự tồn tại của `.specify/docs/<path unit>` (đường dẫn `intel.md`
thật, `.specify/docs/` + `path`):

- **`intel.md` tồn tại** → đưa vào danh sách **runnable**, tiếp tục.
- **`intel.md` không tồn tại**:
  - Tổng số unit đã chốt ở bước 1 là **đúng 1** → **DỪNG NGAY**, nhắc chạy
    `/speckit.dft-speckit.code-intel <FN-ID gốc của unit>` trước. Không tạo `srs.md`.
  - Tổng số unit đã chốt **≥ 2** → **bỏ qua** unit đó, ghi lại vào danh sách **đã bỏ qua**
    (FN-ID + tên), tiếp tục xét các unit còn lại — không dừng cả batch.

Danh sách **runnable** rỗng sau khi lọc (mọi unit ≥2 đều thiếu `intel.md`) → **DỪNG**,
in toàn bộ danh sách "đã bỏ qua", nhắc chạy `code-intel` trước cho các unit đó.

### 3. Chạy song song hay tuần tự?

Danh sách **runnable** có **≥ 2 unit** → hỏi qua AskUserQuestion: chạy song song (mỗi
unit một subagent độc lập qua Agent tool) hay tuần tự (xử từng unit một). **Đúng 1 unit
runnable** → chạy thẳng bước 4-12 dưới đây, không hỏi.

Chạy song song: dispatch một Agent riêng cho mỗi unit runnable, giao FN-ID gốc của unit,
đường dẫn `srs.md` đã suy ở bước 2, đường dẫn `intel.md` tương ứng, danh sách FN-ID kèm
status (từ bước 2), `system`/`updated` đã đọc, và yêu cầu subagent đọc lại chính file
lệnh này (`.specify/extensions/dft-speckit/commands/srs-from-code.md`) rồi thực hiện
đúng Bước 4–12 dưới đây cho một unit đó. Không đồng bộ giữa các subagent — hai unit dùng
chung một entity có thể diễn giải khác nhau, chấp nhận là giới hạn đã biết (giống hệt
`code-intel`).

Subagent **không tự gọi** `fnlist_import.py update` ở Bước 11 của chính nó. Thay vào đó,
sau khi Bước 10 (verify) pass sạch, subagent **báo cáo lại** cho agent cha danh sách cặp
`FN-ID=srs` cần cập nhật (không tự ghi) — tránh race: nhiều subagent cùng ghi đè
`functions.json` sẽ làm mất cập nhật của nhau. Agent cha đợi **tất cả** subagent hoàn
tất, gom toàn bộ cặp `FN-ID=srs` từ mọi subagent, rồi gọi `fnlist_import.py update`
**đúng một lần** với đầy đủ các `--set`.

Chạy tuần tự: lặp qua từng unit runnable, thực hiện Bước 4–12 cho unit đó xong mới sang
unit kế.

### 4. Lấy khung

`--template <đường-dẫn>` có trong `$ARGUMENTS` → dùng file đó (khách hàng có khung
riêng). Không có → `specify preset resolve srs-template` → không resolve được → đọc
`.specify/extensions/dft-speckit/templates/srs-template.md` → vẫn không thấy → hỏi (đây
vẫn là một câu hỏi hợp lệ — nó chặn hẳn việc chạy tiếp, không phải nội dung nghiệp vụ).

**Bước này phải kết thúc bằng một đường dẫn file cụ thể**, không phải nội dung khung nằm
trong ngữ cảnh hội thoại. `specify preset resolve` trả về nội dung thay vì đường dẫn,
hoặc người dùng dán khung trực tiếp vào lượt hỏi → ghi nội dung đó ra
`.specify/tmp/srs/<FN-ID-gốc-của-unit>-template.md` rồi dùng đường dẫn này. Bước 10 luôn
phải truyền được `--template <đường-dẫn>` cho `srs_verify.py` — thiếu nó thì cổng âm thầm
tụt xuống chế độ lỏng (xem ghi chú ở bước 10).

### 5. Kiểm `srs.md` đã tồn tại chưa (làm TRƯỚC khi rót/viết/ghi bất cứ gì)

**Chỗ duy nhất trong lệnh này ghi vào `.specify/docs/<đường-dẫn-cây>/srs.md` là bước 9
"Điền khung".** Mục này chỉ đọc và ghi nhớ, không ghi gì cả — nhưng phải làm trước các
bước 6–8, vì luật no-clobber dưới đây phải có trong đầu **trước khi** bước 9 chạm vào
file, không phải đọc ra sau khi đã ghi đè mất bản cũ.

`srs.md` **chưa tồn tại** → không có gì phải giữ, đi tiếp bước 6.

`srs.md` **đã tồn tại** → đọc toàn bộ nội dung hiện tại, ghi nhớ luật sẽ áp ở bước 9:

- `I.1` Lịch sử thay đổi: bước 9 sẽ **thêm một dòng mới**, không sửa/xoá dòng cũ.
- Mọi nội dung người dùng/BA đã sửa tay ở các mục khác (kể cả những ô trước đây ghi "Chưa
  có thông tin" mà nay đã có nội dung thật): bước 9 sẽ **giữ nguyên**, chỉ cập nhật mục
  nào có nội dung khác đi khi so trực tiếp bản `srs.md` hiện có với `intel.md` và
  `functions.json` hiện tại (không có mốc thời gian/hash nào để so — so nội dung, không so
  "đã đổi từ lần chạy trước" một cách trừu tượng).

### 6. Rót phần suy được từ intel

Đọc `intel.md` của unit và `functions.json`. Ánh xạ mục — không tự ý đổi hướng, mục nào
trong `intel.md` không có thì mục `srs.md` tương ứng cũng không có gì để rót (sẽ xử lý ở
bước 8 theo luật "thông tin hành chính thiếu"):

| Nguồn (`intel.md`) | Đích (`srs.md`) |
| --- | --- |
| §1 Phủ chức năng | II.5 bảng "Mã chức năng — Tên chức năng"; V Ma trận truy vết |
| §2 Màn hình / điểm vào | N.3 Mô tả chức năng — phần "Giao diện" |
| §3 Thực thể và trường dữ liệu | N.4 Đặc tả dữ liệu |
| §4 Kiểm tra hợp lệ và quy tắc nghiệp vụ | N.4 Đặc tả dữ liệu (ràng buộc trường) + N.5 Quy tắc nghiệp vụ (rule khác) |
| §5 Luồng nghiệp vụ | N.3 Mô tả chức năng — văn xuôi + sơ đồ luồng mermaid |
| §6 Phân quyền | N.2 Đối tượng tham gia và phân quyền |
| §7 Tích hợp ngoài, tác vụ nền, sự kiện | N.7 Giao tiếp hệ thống |
| §9 Thông báo hiển thị | N.6 Xử lý ngoại lệ và thông báo |
| §10 Phát hiện logic/bảo mật | **Không rót vào `srs.md`** — chỉ dùng ở bước 12 để hỏi người dùng |

`Hệ thống`/`Ngày cập nhật` đã đọc ở bước 2 — không đọc lại, không tự bịa nếu thiếu.

**Ba thành phần của `N.3` không có nguồn trực tiếp trong `intel.md` — xử lý riêng từng
cái, đừng bịa cho đủ hình dạng khung:**

- **Bảng "Mô tả điều khiển"**: `intel §2` chỉ cho tên màn hình/route, không cho danh sách
  control. Chỉ ghi một dòng khi control đọc được từ `intel.md` (dù ở mục nào). **Không tự
  chế** Textbox/Button/nhãn "nghe hợp lý cho một màn kiểu này" — không có căn cứ thì lược
  bỏ cả bảng.
- **Mô tả bố cục màn hình** ("Giao diện — [Tên màn hình]: khu vực nào hiển thị gì"):
  `intel.md` không quét bố cục UI, chỉ có tên màn/route. **Chỉ nêu tên màn hình/điểm vào**
  (đã có ở `intel §2`) — **không mô tả bố cục** (khu vực, layout) vì không có căn cứ nào
  cho việc đó; viết văn xuôi nghe hợp lý về bố cục là bịa, dù không dùng Textbox/Button cụ
  thể.
- **Sơ đồ luồng mermaid**: chỉ dựng khi `intel §5` có luồng cho chính chức năng đang viết.
  `intel §5` không có luồng nào ứng với chức năng này → **lược bỏ sơ đồ**, không tự suy
  luận các bước từ tên chức năng — một sơ đồ bịa trông như đã được xác minh còn nguy hiểm
  hơn văn xuôi bịa.

### 7. Chuyển hoá bắt buộc khi rót

> `intel.md` là tài liệu nội bộ, `srs.md` giao khách. Khi rót sang: **bỏ hết
> `file:dòng`, tên class, tên hàm, đường dẫn mã nguồn**. Nội dung mang dấu `(suy đoán)` ở
> intel vẫn phản ánh đúng thứ code làm (đó là suy luận có căn cứ, chỉ chưa chắc 100%) —
> rót bình thường vào `srs.md`, không cần đánh dấu gì thêm (bảng ở đây không phải chỗ để
> lộ mức độ tự tin nội bộ), **trừ ngoại lệ `N.4`/`N.5` dưới đây**.
>
> **Ngoại lệ — `N.4` Đặc tả dữ liệu VÀ `N.5` Quy tắc nghiệp vụ**: hai mục này **không
> nhận suy đoán dưới bất kỳ hình thức nào**, dù ràng buộc đó đến từ `intel §3` hay
> `intel §4` (cột "Độ chắc chắn" = `suy đoán`). Ràng buộc mang dấu `(suy đoán)` → **để ô
> đó trống** trong `N.4` (không viết gì, không `—`); quy tắc mang dấu `(suy đoán)` được
> phân vào "rule khác" (không phải ràng buộc field) → **không sinh dòng `BR` nào** trong
> `N.5` — đưa vào mục "Thông tin còn thiếu" ở bước 12.3. **Không** tự thêm dòng mới vào
> `intel §10` cho ca này — lệnh này chỉ được phép sửa cột `Kết luận` của dòng §10 đã có
> (xem bước 12.2), không có quyền thêm phát hiện mới hay điền nguồn `file:dòng` (nó không
> quay lại đọc code). Lý do áp cho cả hai: `N.4` và `N.5` đều là thứ QA dựng
> testcase (biên và nghiệp vụ) và khách đối chiếu lúc nghiệm thu — một ràng buộc/quy tắc
> suy đoán lọt vào đây thành cam kết sai, còn tệ hơn thiếu hẳn dòng đó. `—` cũng không
> dùng thay thế cho ô trống ở `N.4`: theo bảng ký hiệu `II.4` của chính khung, `—` nghĩa
> là "Không áp dụng" (một khẳng định: trường này không có ràng buộc), khác hẳn "chưa xác
> định được".

`intel §9` không có nguyên văn thông báo (câu hỏi đã bị đưa xuống `intel §8` vì không tìm
được nguồn) → `N.6` viết mô tả **ý nghĩa** của thông báo dựa trên `intel §5`/`§4` (hành vi
hệ thống khi tình huống đó xảy ra), để cột "Thông báo hiển thị" trống nếu không có nguyên
văn thật — không bịa nguyên văn giả.

### 8. Điền phần còn lại — chỉ ghi thứ chắc chắn

Không dùng AskUserQuestion ở bước này.

**Thông tin hành chính/nghiệp vụ thuần mà `intel.md` không có** — ghi thẳng, không đánh
dấu, không hỏi:

- **`I.1`/`I.2`** (người viết, người đánh giá, ma trận trách nhiệm) → "Chưa có thông
  tin". Không suy đoán tên người dưới bất kỳ hình thức nào. Cột `Phiên bản` ở `I.1` khi
  tạo mới là `V1`; khi chạy lại trên bản đã có (bước 5/9) thì tăng lên `V<n+1>` theo số
  dòng lịch sử hiện có, không tự đặt lại `V1`.
- **`II.2` Tài liệu tham khảo**: `functions.json`/`intel.md` có nêu tên tài liệu nguồn →
  liệt kê. Không có → "Không có".
- **`II.5` "Phạm vi sử dụng"/"Đối tượng áp dụng"**: lấy từ `intel §6` (danh sách vai trò ở
  bảng Phân quyền) nếu có — "áp dụng cho vai trò X, Y". `intel §6` không có gì → "Chưa có
  thông tin", không tự viết boilerplate kiểu "mọi người dùng trong hệ thống" khi không có
  căn cứ.
- **`IV` Yêu cầu phi chức năng**: mặc định "Không có yêu cầu riêng" cho **toàn bảng**.
  Chỉ ghi cụ thể khi `intel.md` có đề cập điều gì đó thuộc nhóm này (vd giới hạn tần suất
  request là một quy tắc bảo mật/hiệu năng đã thấy trong `intel §4`) — rót thẳng, không
  suy đoán thêm ngưỡng không có căn cứ.
- **Mọi câu chưa có trả lời ở `intel §8`** (chính sách nghiệp vụ thuần, không phải phát
  hiện logic/bảo mật của §10): không chèn vào `srs.md`. Gom lại, đưa vào mục "Thông tin
  còn thiếu" ở báo cáo cuối bước 12 — một dòng mỗi câu, ngắn gọn.

**Nội dung mô tả hệ thống** — viết từ dữ kiện `intel.md`/`functions.json` sẵn có, phản ánh
đúng những gì code làm:

- **`II.1` Mục đích**: liệt kê ngắn gọn các nghiệp vụ trong unit theo tên FN và mô tả ở
  `functions.json`. Không tự thêm diễn giải về "giá trị nghiệp vụ" mà không có căn cứ —
  nêu đúng những gì hệ thống làm, không suy luận vì sao nó làm vậy.
- **`II.5` Phạm vi**, mục *Ngoài phạm vi* — xem quy tắc riêng ở bước 9 (chỉ dùng khi có
  bằng chứng, không suy đoán).
- **`N.1` Mục đích chức năng** (từng chức năng): viết từ `intel §2`/`§5` + tên chức năng
  — mô tả hệ thống làm gì, không suy diễn động cơ nghiệp vụ đằng sau.

### 9. Điền khung

Đây là bước duy nhất ghi vào `srs.md`. Áp đúng luật no-clobber đã ghi nhớ ở bước 5 nếu
file đã tồn tại từ trước.

- **Chỉ `N.1`–`N.7` và các phụ lục ở `VI` được phép lược bỏ** khi không áp dụng — và chỉ
  khi có **lý do kiểm chứng được gắn FN cụ thể** (vd "FN-01-03 là chức năng chỉ đọc, không
  có thao tác ghi nên không cần N.4"), không phải "trông có vẻ không cần".
- **Mọi mục cấp I–VI khác** (`I.1`, `I.2`, `II.1`–`II.5`) — **bắt buộc giữ**, không được
  lược bỏ dù có vẻ không áp dụng; không có nội dung thật thì ghi "Không có" hoặc "Chưa có
  thông tin" theo đúng ngữ nghĩa (xem bước 8), không xoá tiêu đề.
- `II.5` bảng chức năng và `V` ma trận truy vết: mã chức năng lấy **nguyên từ
  `functions.json`** (trường `id` của node lá), không tự đánh mã mới.
- **Một dòng ma trận `V` ghi "Ngoài phạm vi" chỉ hợp lệ khi có bằng chứng trực tiếp trong
  `functions.json`/`intel.md`, và phải nêu rõ nhánh nào** (ba cách viết dưới đây mang nghĩa
  khác nhau với khách, không dùng lẫn, không được tự suy đoán để chọn nhánh):
  - `intel §1` đã ghi FN đó là "không tìm thấy" code → ghi
    `Ngoài phạm vi — chưa tìm thấy hiện thực trong mã nguồn`.
  - `functions.json`/`intel.md` ghi chú **rõ ràng** FN thuộc một tài liệu khác (vd trường
    `description`/ghi chú nêu thẳng tên tài liệu) → ghi
    `Ngoài phạm vi — thuộc tài liệu <tên tài liệu>`.
  - `functions.json`/`intel.md` ghi chú rõ ràng FN chưa thuộc giai đoạn này → ghi
    `Ngoài phạm vi — chưa thuộc giai đoạn này`.

  **Không có bằng chứng nào cho cả ba nhánh trên → KHÔNG dùng "Ngoài phạm vi".** Viết đặc
  tả bằng nội dung sẵn có cho FN đó (dù ngắn, dù nhiều mục con phải ghi "Chưa có thông
  tin") — không gán "Ngoài phạm vi" cho có dòng chỉ vì lười đặc tả. Đây là cách rẻ nhất để
  tài liệu rỗng ruột vẫn qua cổng, bị cấm tường minh.
- Vài chức năng nhỏ dùng chung một màn hình/luồng → gộp vào một khối `## N.` được, miễn
  `II.5` và `V` vẫn liệt kê đủ từng mã riêng. Đây là **trường hợp hợp lệ duy nhất** để
  nhiều dòng ma trận cùng trỏ vào một mục `## N.` — mọi trường hợp khác mà nhiều FN cùng
  trỏ một mục thì phải tự hỏi lại: mục đó có thật sự đặc tả đủ cho từng FN, hay chỉ đang
  trỏ bừa cho có dòng.

### 10. Cổng cuối — chạy trước khi báo xong

```bash
python .specify/extensions/dft-speckit/scripts/srs_verify.py \
  .specify/docs/<đường-dẫn-cây>/srs.md \
  --functions .specify/docs/functions.json \
  --root <FN-ID gốc của unit> \
  --template <đường-dẫn khung đã dùng ở bước 4>
```

Đọc JSON trả về, có hai khoá `blocking` và `warnings`.

- **`blocking` khác rỗng (mã thoát ≠ 0) → cấm báo xong.** Với mục có `goi_y` (`thieu-fn`,
  `placeholder`), sửa theo đúng gợi ý đó. Sửa xong, **chạy lại script** — không tự cho là
  đã sửa đúng mà không xác nhận lại bằng cách chạy thật. Không tự nới lỏng, không tự bỏ
  qua bằng cách sửa `srs.md` để "lách" qua kiểm tra (vd thêm một dòng ma trận trỏ tới một
  mục không thật cho có — script đối chiếu nội dung cột khi nhận ra được cách đánh mục
  `## N.` của khung, dòng giả kiểu này vẫn bị tính là thiếu).
  - Riêng cảnh báo `khong-doi-chieu-duoc-muc` ở `warnings` (không phải `blocking`) nghĩa
    là script **không nhận ra được** cách đánh mục của khung đang dùng (thường gặp khi
    dùng `--template` riêng của khách hàng với kiểu đánh mục khác `## N.`) — trong tình
    huống đó `thieu-fn` chỉ còn kiểm được sự có mặt của mã FN, không kiểm được cột "Mục
    SRS đặc tả" có trỏ đúng chỗ không. **Không được** dùng cảnh báo này làm cớ chuyển
    hàng loạt dòng sang "Ngoài phạm vi" — đó là né việc soát tay, không phải sửa lỗi.
    Tự soát: mỗi ô "Mục SRS đặc tả" có thật sự trỏ tới một mục đặc tả đúng FN đó không,
    kể cả khi script không báo blocking.
  - Thấy `khong-doi-chieu-duoc-muc` **trong khi khung đang dùng là `srs-template.md`
    mặc định** (không phải `--template` riêng của khách) → đó gần như chắc chắn là quên
    truyền `--template`, hoặc truyền sai đường dẫn — không phải "khung khách hàng đánh
    mục kiểu khác". Kiểm lại lệnh ở bước 10 đã có đúng `--template <đường-dẫn>` từ bước 4
    chưa, sửa rồi chạy lại, đừng chấp nhận cảnh báo này như một sự thật của khung mặc định.
- **`warnings` khác rỗng (mã thoát vẫn 0) → không phải lỗi, nhưng phải trình bày NGAY
  TẠI ĐÂY cho người dùng**, trước khi làm bước 11. Không phải mọi loại cảnh báo đều có
  `goi_y` — chỉ `nghi-duong-dan-code` có; các loại khác (`pham-vi-rong`, `thieu-muc`,
  `lech-thu-tu`, `muc-rong`, `khong-doi-chieu-duoc-muc`) không có, tự đọc `thong_diep` mà
  xử lý. Xem xét từng cái — cảnh báo `nghi-duong-dan-code` có thể là báo nhầm (tên file
  nghiệp vụ hợp lệ trong mô tả); chọn "đây là báo nhầm" thì phải **nêu đích danh từng
  chuỗi + lý do cụ thể**, không được kết luận gộp cho cả danh sách. Không được im lặng
  bỏ qua bất kỳ warning nào.

### 11. Ghi ngược trạng thái

**Chạy tuần tự** (hoặc chạy đơn 1 unit runnable): gọi `update` ngay sau mỗi unit, sau khi
đã trình bày xong `warnings` ở bước 10 — không cập nhật trạng thái trước khi người dùng
có cơ hội thấy những gì còn cần soát. **Chạy song song**: **không** gọi ở đây — xem
hướng dẫn gom về agent cha ở bước 3.

Mọi FN thuộc unit đã có dòng ở mục `V` (không phải dòng "Ngoài phạm vi") → đặt trạng thái
`srs`:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=srs [--set FN-01-02=srs ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate toàn bộ ID trước khi ghi (một
ID sai là dừng sạch, không ghi phần đúng rồi bỏ dở phần sai), và đổi status là hành vi có
thể lùi lại.

### 12. Kết thúc — tổng hợp một lượt, không chèn rải rác trong lúc sinh

Với mỗi unit, báo theo đúng ba phần dưới, tách bạch rõ mức độ quan trọng — đừng trộn
chung thành một danh sách phẳng:

1. **Số liệu**: đường dẫn `srs.md`, số chức năng đã đặc tả, số chức năng khai "Ngoài
   phạm vi" tách theo ba nhánh ở bước 9, và **dán nguyên văn dòng tổng kết
   `N lỗi chặn, M cảnh báo.`** của lần chạy `srs_verify.py` **cuối cùng** (bằng chứng đã
   thực sự chạy, không phải tự thuật lại bằng lời).

2. **Phát hiện cần bạn xác nhận** — chỉ liệt kê các mục `intel §10` có cột `Kết luận` =
   `đang chờ` (mục đã có kết luận `cố ý`/`bug` từ lần trước thì bỏ qua, không hỏi lại).
   Không có mục nào đang chờ → bỏ hẳn phần này, không viết "Không có" cho có đủ ba phần.
   Với mỗi mục: nêu mô tả và nguồn `file:dòng` từ `intel.md`, hỏi rõ: *"đây là cố ý thiết
   kế vậy hay là bug? (trả lời ngay ở lượt sau, hoặc tự điền cột `Kết luận` trong
   `intel.md` nếu tiện hơn)"* Đây là phần **quan trọng nhất** của báo cáo — đặt lên đầu
   nếu có, vì nó cần quyết định thật của người dùng trước khi tài liệu được xem là đáng
   tin.

   **Sau khi người dùng trả lời** (ở lượt tiếp theo): ghi kết luận **ngược lại đúng dòng
   đó** trong `intel.md` §10 — cột `Kết luận` đổi thành `cố ý — <ghi chú ngắn>` hoặc
   `bug — <ghi chú ngắn>`. Đây là lần ghi duy nhất được phép sửa một dòng §10 đã có (theo
   đúng ngoại lệ no-clobber của `code-intel`) — chỉ sửa cột này, không đổi mô tả/nguồn.
   Không làm bước này thì lần chạy `srs-from-code` sau sẽ hỏi lại y nguyên.

3. **Thông tin còn thiếu** (thấp — chỉ để biết, không cần xử lý ngay): liệt kê ngắn gọn
   ba loại, mỗi mục một dòng — (a) mục ghi "Chưa có thông tin" ở `srs.md`; (b) câu hỏi
   chính sách nghiệp vụ chưa trả lời ở `intel §8`; (c) quy tắc mang `(suy đoán)` bị loại
   khỏi `N.5` theo ngoại lệ ở bước 7 (nêu tên chức năng + tóm tắt quy tắc, để người dùng
   biết nó không biến mất im lặng). Kết một câu: *"bổ sung nếu cần, không bắt buộc phải
   xử lý ngay — chạy lại lệnh sau khi bổ sung sẽ giữ nguyên phần đã có."*

Chạy hàng loạt (**≥ 2 unit runnable**) thì tổng kết thêm ở cuối, sau báo cáo của mọi
unit: tổng số unit đã xử lý, danh sách unit **đã bỏ qua** vì thiếu `intel.md` (từ bước 2,
kèm gợi ý chạy `code-intel` cho từng unit đó), danh sách unit lỗi nếu có subagent nào
BLOCKING mà không tự sửa được.

## Sai lầm thường gặp

- **Chèn `(cần xác nhận)` hoặc bất kỳ đánh dấu tương tự nào vào `srs.md`** → tài liệu này
  chỉ chứa nội dung chắc chắn; thông tin thiếu ghi thẳng "Chưa có thông tin" không đánh
  dấu, phát hiện logic/bảo mật không đưa vào file này dưới bất kỳ hình thức nào.
- **Dừng lại hỏi AskUserQuestion ở bước 6–9** → lệnh này chủ ý không hỏi trong lúc sinh.
  Chỉ bước 1 (xác nhận cây), bước 3 (song song/tuần tự), và bước 4 (khung không resolve
  được) mới hỏi — đều là chặn hạ tầng/lựa chọn quy trình, không phải nội dung nghiệp vụ.
- **Rải phát hiện `intel §10` vào từng mục `N.x` lúc viết** → dồn hết vào bước 12, một
  lượt duy nhất, đặt lên đầu báo cáo. Rải rác làm người dùng dễ bỏ sót phát hiện quan
  trọng giữa các mục hành chính không quan trọng.
- **Coi câu hỏi `intel §8` (chính sách nghiệp vụ) ngang hàng phát hiện `intel §10`
  (logic/bảo mật)** → hai loại khác nhau: §8 là "không biết, không quan trọng lắm" (mục
  "Thông tin còn thiếu", thấp), §10 là "biết và đáng ngờ" (mục "Phát hiện cần xác nhận",
  cao). Trộn chung làm mất tín hiệu quan trọng.
- **Ghi vào `srs.md` trước khi đọc bản cũ (bỏ qua bước 5)** → đè sạch nội dung người dùng
  đã sửa tay và lịch sử `I.1`. Bước 5 phải chạy trước bước 9, không phải đọc ra sau khi
  đã ghi.
- **Ghi thẳng `file:dòng` hoặc tên class/hàm từ intel sang srs** → phá ranh giới nội bộ/
  giao khách; `srs_verify.py` sẽ cảnh báo nhưng đó là lưới an toàn cuối, không phải chỗ
  dựa để khỏi tự kiểm khi rót.
- **Điền ràng buộc suy đoán vào `N.4`** → đây là ngoại lệ duy nhất không nhận nội dung
  suy đoán dưới mọi hình thức. `N.4` chỉ nhận ràng buộc có căn cứ thật; suy đoán thì để
  ô trống, không viết gì — áp cho cả hai nguồn `intel §3` và `§4`.
- **Dùng `—` thay cho ô trống ở `N.4`** → `—` nghĩa là "Không áp dụng" theo chính bảng ký
  hiệu của khung, ghi nhầm thành một khẳng định sai (trường không có ràng buộc, trong khi
  sự thật là chưa xác định được).
- **Lược bỏ hàng loạt mục con `N.1`–`N.7` mà không nêu lý do gắn FN cụ thể**, hoặc khai
  "Ngoài phạm vi" ở ma trận `V` mà không có bằng chứng trực tiếp hay không tách nhánh →
  cách rẻ nhất để một tài liệu rỗng ruột vẫn qua cổng; đều bị cấm tường minh ở bước 9.
- **Dùng cảnh báo `khong-doi-chieu-duoc-muc` làm cớ chuyển hàng loạt FN sang "Ngoài phạm
  vi"** → né việc soát tay bằng đúng cách tạo ra tài liệu rỗng ruột mà các luật ở bước 9
  tồn tại để chặn.
- **Nhiều FN cùng trỏ một mục `## N.` mà không phải trường hợp gộp đã khai ở bước 9** →
  dấu hiệu trỏ bừa cho có dòng ma trận, không phải đặc tả thật.
- **Tự chế bảng "Mô tả điều khiển" ở `N.3`** khi `intel.md` không có gì về control → lược
  bỏ bảng đó, đừng bịa Textbox/Button nghe hợp lý.
- **`blocking` khác rỗng mà vẫn báo xong**, hoặc sửa `srs.md` chỉ để qua cổng mà không
  sửa nội dung thật → cổng nghiệm thu trở thành hình thức.
- **Trình bày `warnings` sau khi đã ghi ngược trạng thái ở bước 11** → đảo đúng thứ tự
  bắt buộc: trình bày trước, ghi ngược sau.
- **Suy diễn "vì sao" hệ thống làm vậy** (động cơ nghiệp vụ) ở `II.1`/`N.1` thay vì mô tả
  đúng "làm gì" theo code → tài liệu này phản ánh source code, không phải một bài phân
  tích nghiệp vụ suy đoán.
- **Bịa ngưỡng số ở `IV`** khi không ai nêu → thành cam kết sai lúc nghiệm thu.
- **Tự đánh mã chức năng mới** ở `II.5`/`V` thay vì lấy từ `functions.json` → mã không
  khớp với hợp đồng nghiệm thu ban đầu.
- **Chạy `srs-from-code` khi `intel.md` chưa có** (hoặc tự bỏ qua điều kiện tiên quyết) →
  viết SRS từ trí tưởng tượng.
- **Chạy song song mà để subagent tự gọi `fnlist_import.py update`** → race, cập nhật của
  subagent này đè mất cập nhật của subagent khác. Luôn báo cáo về agent cha, cha gọi
  `update` một lần duy nhất sau khi mọi subagent xong (bước 3/11).
- **Áp nhầm "hard-stop" và "skip-and-report" cho ca thiếu `intel.md`** → chỉ đúng 1 unit
  đã chốt (từ bước 1) mới hard-stop; ≥ 2 unit thì bỏ qua unit thiếu, chạy tiếp phần còn
  lại, báo rõ ở bước 12. Không được dừng cả batch chỉ vì một unit trong nhiều unit thiếu
  `intel.md`.
- **Tính "≥ 2 unit" ở bước 3 theo danh sách gốc đã chốt ở bước 1** thay vì danh sách
  **runnable** sau khi lọc ở bước 2 → nếu batch ban đầu có 3 unit nhưng 2 unit bị bỏ qua
  vì thiếu `intel.md`, chỉ còn 1 unit runnable thì phải chạy thẳng, không hỏi song
  song/tuần tự cho một unit duy nhất.
````

- [ ] **Step 2: Đọc lại toàn văn, đối chiếu spec**

Đọc lại `speckit-extension/commands/srs-from-code.md` vừa viết, đối chiếu từng điểm của
`docs/superpowers/specs/2026-08-12-srs-from-code-tree-migration-design.md` (5 quyết định
+ ghi chú §6): tham số FN-ID đơn + batch, đường dẫn `srs.md` suy từ `intel.md`, CLI
`srs_verify.py` mới, ghi ngược qua `fnlist_import.py update` với cơ chế chống race, và
xác nhận không có đoạn nào còn nhắc `functions.md`/`--cluster`/"tên cụm gõ tay".

Kiểm bằng lệnh:
```bash
grep -n "functions.md\|--cluster\|tên cụm" speckit-extension/commands/srs-from-code.md
```
Expected: không có kết quả nào (mọi tham chiếu cũ đã được thay bằng `functions.json`/
`--root`/`FN-ID`).

- [ ] **Step 3: Chạy thử chuỗi lệnh CLI mô tả trong file, trên fixture tối thiểu**

Dựng một `functions.json` + `intel.md` mẫu trong thư mục tạm, chạy đúng các lệnh mà file
vừa viết mô tả (propose → units → srs_verify → update), xác nhận không lỗi cú pháp:

```bash
mkdir -p /tmp/srs-smoke/.specify/docs
cat > /tmp/srs-smoke/.specify/docs/functions.json <<'EOF'
{"schema_version": 1, "system": "DMS", "source": {"file": "x", "sheet": "x"},
 "updated": "2026-08-12", "retired_ids": [],
 "functions": [{"id": "FN-01", "name": "Xac thuc", "description": "", "children": [
   {"id": "FN-01-01", "name": "Dang nhap", "description": "", "children": []}]}]}
EOF
mkdir -p "/tmp/srs-smoke/.specify/docs/01-xac-thuc"
cat > "/tmp/srs-smoke/.specify/docs/01-xac-thuc/srs.md" <<'EOF'
# SRS — Xac thuc

# V. MA TRẬN TRUY VẾT

| Mã chức năng | Tên chức năng | Mục SRS đặc tả |
| --- | --- | --- |
| FN-01-01 | Dang nhap | Ngoài phạm vi — chưa tìm thấy hiện thực trong mã nguồn |
EOF
cd /tmp/srs-smoke
python /e/agent-skills/speckit-extension/scripts/intel_tree.py propose \
  --functions .specify/docs/functions.json
python /e/agent-skills/speckit-extension/scripts/intel_tree.py units \
  --functions .specify/docs/functions.json --roots FN-01
python /e/agent-skills/speckit-extension/scripts/srs_verify.py \
  .specify/docs/01-xac-thuc/srs.md --functions .specify/docs/functions.json --root FN-01
python /e/agent-skills/speckit-extension/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=srs
cat .specify/docs/functions.json
rm -rf /tmp/srs-smoke
```

Expected: `propose`/`units` in JSON hợp lệ; `srs_verify.py` in JSON `{"blocking": [], ...}`
(mã thoát 0 — ma trận đã có dòng hợp lệ); `update` in JSON xác nhận `FN-01-01` đổi từ
`pending` sang `srs`; `functions.json` cuối cùng có `"status": "srs"` ở node `FN-01-01`.
Đây là bằng chứng cả 4 lệnh trong file mới hoạt động đúng cú pháp với nhau, không chỉ
đọc bằng mắt.

- [ ] **Step 4: Commit**

```bash
git add speckit-extension/commands/srs-from-code.md
git commit -m "feat(code-intel): srs-from-code.md sang tham số FN-ID + batch (đợt 3B-1)"
```

---

## Task 3: Xoá ghi chú lỗi thời trong `code-intel.md`

**Files:**
- Modify: `speckit-extension/commands/code-intel.md`

**Interfaces:** Không có — chỉ xoá một đoạn văn bản đã sai sau Task 2.

- [ ] **Step 1: Xoá đoạn "Lưu ý khoảng đứt đã biết"**

Trong mục "## Kết thúc" của `speckit-extension/commands/code-intel.md`, tìm đoạn:

```
**Lưu ý khoảng đứt đã biết**: `srs-from-code` (chưa cập nhật trong đợt này) vẫn đọc cấu
trúc "cụm" phẳng cũ (liệt kê thư mục con trực tiếp của `.specify/docs/`, đọc
`functions.md` không còn tồn tại) — với cây lồng nhiều cấp mới, chạy nó ngay bây giờ có
thể liệt kê nhầm thư mục nhóm cấp cao hoặc báo lỗi khó hiểu. Sẽ được nối trong đợt cập
nhật `srs-from-code` sau; không tự chạy thay người dùng.
```

Xoá nguyên đoạn này (bao gồm dòng trống liền trước) — đợt 3B-1 vừa cập nhật
`srs-from-code` xong nên phát biểu "chưa cập nhật" nay đã sai; không thay bằng ghi chú
nào khác, đoạn "Với mỗi unit, báo: ..." liền trước là câu kết thúc mục "Kết thúc".

- [ ] **Step 2: Xác nhận không còn tham chiếu nào tới đoạn đã xoá**

Run: `grep -n "khoảng đứt đã biết\|chưa cập nhật trong đợt này" speckit-extension/commands/code-intel.md`
Expected: không có kết quả nào.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/code-intel.md
git commit -m "docs(code-intel): xoá ghi chú lỗi thời về srs-from-code chưa cập nhật"
```
