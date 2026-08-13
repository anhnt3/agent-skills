import json
import sys
from pathlib import Path

import pytest

import intel_verify as iv

EXPECTED = [
    {"id": "FN-01-01", "name": "Đăng nhập"},
    {"id": "FN-01-02", "name": "Quên mật khẩu"},
]

INTEL_OK = """# Code intel — Xác thực

**Cập nhật**: 2026-08-12
**Phủ chức năng**: FN-01-01, FN-01-02

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| FN-01-01 | Đăng nhập | src/auth/login.ts:10 | — |
| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |
| Quên mật khẩu | /forgot | src/auth/reset.ts:5 | FN-01-02 |

## 3. Thực thể và trường dữ liệu

Không có.

## 4. Kiểm tra hợp lệ và quy tắc nghiệp vụ

Không có.

## 5. Luồng nghiệp vụ

Không có.

## 6. Phân quyền

Không có.

## 7. Tích hợp ngoài, tác vụ nền, sự kiện

Không có.

## 8. Không suy được từ code — câu hỏi cho người

1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_

## 9. Thông báo hiển thị

| Ngữ cảnh | Nguyên văn thông báo | Nguồn |
| --- | --- | --- |
| Sai mật khẩu | "Email hoặc mật khẩu không đúng" | src/auth/login.ts:22 |

## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật

Không có.
"""


def test_clean_document_has_no_blocking():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert r["blocking"] == []


def test_missing_fn_in_section1_is_blocking():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n", "")
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "thieu-fn-o-muc-1" and "FN-01-02" in b["thong_diep"]
               for b in r["blocking"])


def test_extra_fn_in_section1_is_blocking():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n",
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n"
        "| FN-99-99 | Lạc | không tìm thấy | — |\n")
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "thua-fn-o-muc-1" and "FN-99-99" in b["thong_diep"]
               for b in r["blocking"])


def test_not_found_ratio_excused_when_m_is_1():
    expected = [{"id": "FN-01-01", "name": "Đăng nhập"}]
    text = INTEL_OK.replace("src/auth/login.ts:10 | —", "không tìm thấy | —")
    r = iv.verify(text, expected)
    assert not any(b["loai"] == "ti-le-khong-tim-thay-vuot-nguong" for b in r["blocking"])


def test_not_found_ratio_excused_when_m_is_2():
    text = (INTEL_OK
            .replace("src/auth/login.ts:10 | —", "không tìm thấy | —")
            .replace("src/auth/reset.ts:5 | —", "không tìm thấy | —"))
    r = iv.verify(text, EXPECTED)
    assert not any(b["loai"] == "ti-le-khong-tim-thay-vuot-nguong" for b in r["blocking"])


def test_not_found_ratio_still_blocks_when_m_is_3():
    expected = EXPECTED + [{"id": "FN-01-03", "name": "Đổi mật khẩu"}]
    text = INTEL_OK.replace(
        "## 1. Phủ chức năng\n\n"
        "| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |\n"
        "| --- | --- | --- | --- |\n"
        "| FN-01-01 | Đăng nhập | src/auth/login.ts:10 | — |\n"
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
        "## 1. Phủ chức năng\n\n"
        "| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |\n"
        "| --- | --- | --- | --- |\n"
        "| FN-01-01 | Đăng nhập | src/auth/login.ts:10 | — |\n"
        "| FN-01-02 | Quên mật khẩu | không tìm thấy | thử ≥2 nấc |\n"
        "| FN-01-03 | Đổi mật khẩu | không tìm thấy | thử ≥2 nấc |")
    r = iv.verify(text, expected)
    assert any(b["loai"] == "ti-le-khong-tim-thay-vuot-nguong" for b in r["blocking"])


def test_section8_cap_counts_unlabeled_items_toward_cap():
    items = "\n".join(
        f"{i}. Câu hỏi không nhãn số {i}? — **Trả lời**: _(chưa có)_"
        for i in range(1, 5))
    text = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        items)
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "tran-muc-8-vuot-nguong" for b in r["blocking"])


def test_placeholder_left_over_is_blocking():
    text = INTEL_OK + "\n## Phụ lục — [Tên phụ lục]\n"
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "placeholder" for b in r["blocking"])


def test_known_label_bracket_is_not_a_placeholder():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_section8_cap_blocks_when_exceeded():
    items = "\n".join(
        f"{i}. [không suy được từ code] Câu hỏi số {i}? — **Trả lời**: _(chưa có)_"
        for i in range(1, 5))
    text = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        items)
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "tran-muc-8-vuot-nguong" for b in r["blocking"])


def test_section8_duplicate_reason_blocks():
    items = "\n".join(
        f"{i}. [không suy được từ code] Cùng một lý do — **Trả lời**: _(chưa có)_"
        for i in range(1, 4))
    text = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        items)
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "muc-8-lap-ly-do" for b in r["blocking"])


def test_no_clobber_8_blocks_when_old_item_dropped():
    before = INTEL_OK
    after = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        "1. [chính sách nghiệp vụ] Câu hỏi khác hẳn — **Trả lời**: _(chưa có)_")
    r = iv.verify(after, EXPECTED, before=before)
    assert any(b["loai"] == "mat-noi-dung-muc-8" for b in r["blocking"])


def test_no_clobber_8_passes_when_old_item_kept_and_new_added():
    before = INTEL_OK
    after = INTEL_OK.replace(
        "## 9. Thông báo hiển thị",
        "2. [không suy được từ code] Câu hỏi mới — **Trả lời**: _(chưa có)_\n\n"
        "## 9. Thông báo hiển thị")
    r = iv.verify(after, EXPECTED, before=before)
    assert not any(b["loai"] == "mat-noi-dung-muc-8" for b in r["blocking"])


def test_no_clobber_10_blocks_when_old_row_dropped():
    before = INTEL_OK.replace(
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "Không có.",
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "| # | Loại | Mô tả | Nguồn | Kết luận |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 1 | logic mâu thuẫn | Hai nhánh kiểm mật khẩu khác nhau | "
        "src/auth/login.ts:30, src/auth/reset.ts:12 | đang chờ |")
    after = INTEL_OK  # bản mới đánh mất dòng §10
    r = iv.verify(after, EXPECTED, before=before)
    assert any(b["loai"] == "mat-noi-dung-muc-10" for b in r["blocking"])


def test_no_clobber_10_ignores_ket_luan_column_changes():
    before = INTEL_OK.replace(
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "Không có.",
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "| # | Loại | Mô tả | Nguồn | Kết luận |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 1 | logic mâu thuẫn | Hai nhánh kiểm mật khẩu khác nhau | "
        "src/auth/login.ts:30 | đang chờ |")
    after = before.replace("| đang chờ |", "| cố ý — đã xác nhận |")
    r = iv.verify(after, EXPECTED, before=before)
    assert not any(b["loai"] == "mat-noi-dung-muc-10" for b in r["blocking"])


def test_cite_without_source_or_suy_doan_is_warning():
    text = INTEL_OK.replace(
        "| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
        "| Đăng nhập | /login | không rõ | FN-01-01 |")
    r = iv.verify(text, EXPECTED)
    assert r["blocking"] == []
    assert any(w["loai"] == "cite-khong-ro" for w in r["warnings"])


def test_cite_marked_suy_doan_is_not_a_warning():
    text = INTEL_OK.replace(
        "| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
        "| Đăng nhập | /login | (suy đoán, gần src/auth/) | FN-01-01 |")
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "cite-khong-ro" for w in r["warnings"])


def test_fn_found_but_absent_from_section2_is_warning():
    text = INTEL_OK.replace(
        "| Quên mật khẩu | /forgot | src/auth/reset.ts:5 | FN-01-02 |\n", "")
    r = iv.verify(text, EXPECTED)
    assert any(w["loai"] == "fn-khong-co-mat-o-muc-2" and "FN-01-02" in w["thong_diep"]
               for w in r["warnings"])


def test_fn_not_found_at_section1_is_excused_from_anchor_check():
    text = (INTEL_OK
            .replace("| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
                     "| FN-01-02 | Quên mật khẩu | không tìm thấy | — |")
            .replace("| Quên mật khẩu | /forgot | src/auth/reset.ts:5 | FN-01-02 |\n", ""))
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "fn-khong-co-mat-o-muc-2" and "FN-01-02" in w["thong_diep"]
                   for w in r["warnings"])


def _write_functions_json(tmp_path):
    doc = {"functions": [
        {"id": "FN-01", "name": "Xac thuc", "description": "", "children": [
            {"id": "FN-01-01", "name": "Đăng nhập", "description": "", "children": []},
            {"id": "FN-01-02", "name": "Quên mật khẩu", "description": "", "children": []},
        ]},
    ]}
    fp = tmp_path / "functions.json"
    fp.write_text(json.dumps(doc), encoding="utf-8")
    return fp


def _run(tmp_path, intel_text, before_text=None):
    import subprocess
    intel = tmp_path / "intel.md"
    intel.write_text(intel_text, encoding="utf-8")
    fp = _write_functions_json(tmp_path)
    cmd = [sys.executable, str(Path(iv.__file__)), str(intel),
           "--functions", str(fp), "--root", "FN-01"]
    if before_text is not None:
        before = tmp_path / "before.md"
        before.write_text(before_text, encoding="utf-8")
        cmd += ["--before", str(before)]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def test_cli_exits_zero_when_clean(tmp_path):
    p = _run(tmp_path, INTEL_OK)
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout)["blocking"] == []


def test_cli_exits_one_when_blocking(tmp_path):
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n", "")
    p = _run(tmp_path, text)
    assert p.returncode == 1
    assert json.loads(p.stdout)["blocking"]


def test_cli_before_flag_enables_no_clobber_check(tmp_path):
    before = INTEL_OK
    after = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        "1. [chính sách nghiệp vụ] Câu hỏi khác hẳn — **Trả lời**: _(chưa có)_")
    p = _run(tmp_path, after, before_text=before)
    assert p.returncode == 1
    assert any(b["loai"] == "mat-noi-dung-muc-8" for b in json.loads(p.stdout)["blocking"])


def test_cli_reports_missing_root(tmp_path):
    import subprocess
    intel = tmp_path / "intel.md"
    intel.write_text(INTEL_OK, encoding="utf-8")
    fp = tmp_path / "functions.json"
    fp.write_text(json.dumps({"functions": []}), encoding="utf-8")
    p = subprocess.run(
        [sys.executable, str(Path(iv.__file__)), str(intel),
         "--functions", str(fp), "--root", "FN-99"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode != 0
    assert "FN-99" in p.stderr


def test_section3_multiple_entity_tables_headers_not_mistaken_for_data():
    # §3 có thể có NHIỀU bảng liên tiếp (mỗi entity một bảng field riêng khi
    # cụm có ≥2 entity) — header của bảng thứ hai không được lẫn vào dữ liệu.
    text = INTEL_OK.replace(
        "## 3. Thực thể và trường dữ liệu\n\nKhông có.",
        "## 3. Thực thể và trường dữ liệu\n\n"
        "### KhachHang\n\n"
        "| Trường | Kiểu | Ràng buộc | Nguồn |\n"
        "| --- | --- | --- | --- |\n"
        "| ten | string | required | src/models/khach_hang.ts:5 |\n\n"
        "### DonHang\n\n"
        "| Trường | Kiểu | Ràng buộc | Nguồn |\n"
        "| --- | --- | --- | --- |\n"
        "| ma_don | string | required | không rõ |\n")
    r = iv.verify(text, EXPECTED)
    section3_warnings = [w for w in r["warnings"]
                          if w["loai"] == "cite-khong-ro" and "§3" in w["thong_diep"]]
    # Chỉ dòng field thật thiếu cite (ma_don, dòng dữ liệu thứ 2 của §3) mới
    # được cảnh báo — header "Trường | Kiểu | ..." của bảng DonHang KHÔNG
    # được tính là một dòng dữ liệu riêng bị chấm oan.
    assert len(section3_warnings) == 1
    assert "dòng 2" in section3_warnings[0]["thong_diep"]


INTEL_WITH_11 = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc, tối đa 50 ký tự | src/auth/login.ts:24 |
| Đăng nhập | Mật khẩu | Passwordbox | bắt buộc | src/auth/login.ts:31 |
| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |
"""


def test_section11_no_warning_when_all_screens_covered():
    r = iv.verify(INTEL_WITH_11, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-dieu-khien" for w in r["warnings"])


def test_section11_warns_when_screen_missing_controls():
    # INTEL_OK không có §11 nào cả -> cả 2 màn hình đều thiếu.
    r = iv.verify(INTEL_OK, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-dieu-khien")
    assert "Đăng nhập" in w["thong_diep"] and "Quên mật khẩu" in w["thong_diep"]


def test_section11_partial_coverage_warns_only_for_missing_screen():
    text = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc | src/auth/login.ts:24 |
"""
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-dieu-khien")
    assert "Quên mật khẩu" in w["thong_diep"]
    assert "Đăng nhập" not in w["thong_diep"]


def test_section11_khong_co_ui_counts_as_covered():
    text = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc | src/auth/login.ts:24 |
| Quên mật khẩu | — | không-có-UI | Endpoint REST thuần, không có view | src/auth/reset.ts:5 |
"""
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-dieu-khien" for w in r["warnings"])


def test_section11_warns_on_unknown_screen_name():
    text = INTEL_WITH_11.replace(
        "| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |",
        "| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |\n"
        "| Man hinh la | Nut la | Button | khong ton tai o muc 2 | src/x.ts:1 |")
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-o-muc-11-khong-khop-muc-2")
    assert "Man hinh la" in w["thong_diep"]


def test_section11_absent_entirely_does_not_crash():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert not any(w["loai"] == "man-hinh-o-muc-11-khong-khop-muc-2" for w in r["warnings"])


def test_section11_backtick_wrapped_screen_name_still_matches_section2():
    # strip_noise xoá SẠCH nội dung trong cặp backtick (không chỉ bỏ dấu) —
    # nếu §2 và §11 cùng bọc tên màn hình trong backtick, cả hai ô đều biến
    # thành rỗng trước khi _strip_backtick chạy nếu strip không được tắt
    # đúng chỗ. Ở đây tên thực chất khớp nhau (chỉ khác cách trang trí) nên
    # không được có cảnh báo nào.
    text = (INTEL_OK
            .replace("| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
                     "| `POST /api/orders` | /login | src/auth/login.ts:10 | FN-01-01 |")
            + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| `POST /api/orders` | Tên đăng nhập | Textbox | bắt buộc | src/auth/login.ts:24 |
| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |
""")
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-dieu-khien" for w in r["warnings"])
    assert not any(w["loai"] == "man-hinh-o-muc-11-khong-khop-muc-2" for w in r["warnings"])


def test_parse_section11_reads_correct_columns():
    r = iv.parse_section11(INTEL_WITH_11)
    assert r == [
        {"man_hinh": "Đăng nhập", "loai": "Textbox"},
        {"man_hinh": "Đăng nhập", "loai": "Passwordbox"},
        {"man_hinh": "Quên mật khẩu", "loai": "Textbox"},
    ]


def test_cite_quality_covers_section11():
    text = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc | không rõ |
"""
    r = iv.verify(text, EXPECTED)
    assert any(w["loai"] == "cite-khong-ro" and "§11" in w["thong_diep"]
               for w in r["warnings"])


INTEL_WITH_12 = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **Màn hình**: Đăng nhập
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để đăng nhập vào hệ thống.
- **Mô tả tóm tắt**: Người dùng nhập tài khoản, hệ thống xác thực và cấp phiên đăng nhập.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập tài khoản và mật khẩu — src/auth/login.ts:10
2. Hệ thống xác thực và cấp phiên — src/auth/login.ts:15

**Luồng sự kiện nhỏ**:
- S-1: Sai mật khẩu — src/auth/login.ts:22
  1. Hệ thống hiển thị lỗi "Email hoặc mật khẩu không đúng"

### Quên mật khẩu

- **Màn hình**: Quên mật khẩu
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để khôi phục mật khẩu.
- **Mô tả tóm tắt**: Người dùng yêu cầu đặt lại mật khẩu qua email.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập email — src/auth/reset.ts:5
2. Hệ thống gửi email đặt lại mật khẩu — src/auth/reset.ts:9
"""


def test_parse_section12_reads_correct_screens():
    r = iv.parse_section12(INTEL_WITH_12)
    assert r == [
        {"use_case": "Đăng nhập", "man_hinh": "Đăng nhập"},
        {"use_case": "Quên mật khẩu", "man_hinh": "Quên mật khẩu"},
    ]


def test_parse_section12_does_not_assume_man_hinh_is_first_bullet():
    text = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **Mức quan trọng**: Chưa có thông tin
- **Màn hình**: Đăng nhập
- **Người dùng**: Người dùng hệ thống
"""
    r = iv.parse_section12(text)
    assert r == [{"use_case": "Đăng nhập", "man_hinh": "Đăng nhập"}]


def test_parse_section12_accepts_backtick_wrapped_field_name():
    # Prose ở code-intel.md từng render field này bọc backtick quanh tên field
    # ("- **`Màn hình`**: ...") — regex phải chấp nhận cả dạng đó, không chỉ dạng
    # canonical không backtick mà intel-template.md dùng.
    text = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **`Màn hình`**: Đăng nhập
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
"""
    r = iv.parse_section12(text)
    assert r == [{"use_case": "Đăng nhập", "man_hinh": "Đăng nhập"}]


def test_section12_no_warning_when_all_screens_covered():
    r = iv.verify(INTEL_WITH_12, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-usecase" for w in r["warnings"])


def test_section12_warns_when_screen_missing_usecase():
    # INTEL_OK không có §12 nào cả -> cả 2 màn hình đều thiếu.
    r = iv.verify(INTEL_OK, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-usecase")
    assert "Đăng nhập" in w["thong_diep"] and "Quên mật khẩu" in w["thong_diep"]


def test_section12_partial_coverage_warns_only_for_missing_screen():
    text = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **Màn hình**: Đăng nhập
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để đăng nhập vào hệ thống.
- **Mô tả tóm tắt**: Người dùng nhập tài khoản, hệ thống xác thực.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập tài khoản và mật khẩu — src/auth/login.ts:10
"""
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-usecase")
    assert "Quên mật khẩu" in w["thong_diep"]
    assert "Đăng nhập" not in w["thong_diep"]


def test_section12_warns_on_unknown_screen_name():
    text = INTEL_WITH_12 + """
### Màn hình lạ

- **Màn hình**: Man hinh la
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Chưa có thông tin
- **Mô tả tóm tắt**: Không tồn tại ở §2.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Bước lạ — src/x.ts:1
"""
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-o-muc-12-khong-khop-muc-2")
    assert "Man hinh la" in w["thong_diep"]


def test_section12_absent_entirely_does_not_crash():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert not any(w["loai"] == "man-hinh-o-muc-12-khong-khop-muc-2" for w in r["warnings"])


def test_section12_backtick_wrapped_screen_name_still_matches_section2():
    # strip_noise xoá SẠCH nội dung trong cặp backtick — nếu §2 và §12 cùng bọc tên
    # màn hình trong backtick, cả hai phải vẫn khớp nhau (cùng cơ chế đã kiểm ở §11).
    text = (INTEL_OK
            .replace("| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
                     "| `POST /api/orders` | /login | src/auth/login.ts:10 | FN-01-01 |")
            + """
## 12. Kịch bản Use Case

### Đặt hàng

- **Màn hình**: `POST /api/orders`
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Chưa có thông tin
- **Mô tả tóm tắt**: Gọi API tạo đơn hàng.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Client gọi API — src/orders.ts:1

### Quên mật khẩu

- **Màn hình**: Quên mật khẩu
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Chưa có thông tin
- **Mô tả tóm tắt**: Khôi phục mật khẩu.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập email — src/auth/reset.ts:5
""")
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-usecase" for w in r["warnings"])
    assert not any(w["loai"] == "man-hinh-o-muc-12-khong-khop-muc-2" for w in r["warnings"])


def test_chua_co_thong_tin_is_not_a_placeholder():
    # "Chưa có thông tin" không có ngoặc vuông — không được bị bắt là placeholder
    # chưa điền (rủi ro đã ghi trong spec §12).
    r = iv.verify(INTEL_WITH_12, EXPECTED)
    assert r["blocking"] == []


def test_ghi_chu_evidence_clean_when_note_present():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
        "| FN-01-02 | Quên mật khẩu | không tìm thấy | thử tên tiếng Việt + key i18n, "
        "thư mục src/auth không có route tương ứng |")
    out = iv.check_ghi_chu_evidence(text)
    assert out == []


def test_ghi_chu_evidence_warns_when_note_empty():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
        "| FN-01-02 | Quên mật khẩu | không tìm thấy | — |")
    out = iv.check_ghi_chu_evidence(text)
    assert any(w["loai"] == "ghi-chu-khong-du-bang-chung" and "FN-01-02" in w["thong_diep"]
               for w in out)


def test_ghi_chu_evidence_warns_when_note_just_repeats_not_found():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
        "| FN-01-02 | Quên mật khẩu | không tìm thấy | đã tìm không thấy |")
    out = iv.check_ghi_chu_evidence(text)
    assert any(w["loai"] == "ghi-chu-khong-du-bang-chung" for w in out)


def test_ghi_chu_evidence_short_but_specific_note_is_accepted():
    # "thử ≥2 nấc" (ngắn nhưng cụ thể, quy ước đã có sẵn trong codebase) không
    # bị chặn bởi heuristic độ dài — chỉ chặn ô trống/chung chung.
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
        "| FN-01-02 | Quên mật khẩu | không tìm thấy | thử ≥2 nấc |")
    out = iv.check_ghi_chu_evidence(text)
    assert out == []


def test_ghi_chu_evidence_ignores_rows_that_were_found():
    # Dòng đã tìm thấy code không cần Ghi chú gì cả -> không cảnh báo dù cột
    # Ghi chú là "—" (chỉ áp cho dòng "không tìm thấy").
    out = iv.check_ghi_chu_evidence(INTEL_OK)
    assert out == []


def test_ghi_chu_evidence_backtick_wrapped_pattern_is_accepted():
    # Ghi chú TOÀN BỘ là các token bọc backtick (không còn chữ nào ngoài
    # backtick) — strip_noise (dùng nếu bug strip=True còn tồn tại) xoá sạch
    # NỘI DUNG bên trong backtick chứ không chỉ dấu, nên ô này sẽ đọc thành
    # rỗng nếu bug đó tái xuất hiện. strip=False + _strip_backtick giữ được
    # nội dung thật, không báo cảnh báo oan.
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
        "| FN-01-02 | Quên mật khẩu | không tìm thấy | `login` `signin` `forgot-password` |")
    out = iv.check_ghi_chu_evidence(text)
    assert out == []
