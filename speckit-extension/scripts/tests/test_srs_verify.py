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

SRS_OK = """## Đăng ký đăng nhập

### Đăng nhập

<!-- FN: FN-01-01 -->

#### Sơ đồ chức năng

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Nhập tài khoản]
```

#### Mục đích chức năng

Xác thực danh tính người dùng trước khi cho phép truy cập hệ thống.

#### Mô tả chức năng

##### Đăng nhập

<!-- FN-leaf: FN-01-01 -->

###### a. Đối tượng tham gia

Người dùng hệ thống.

###### b. Điều kiện thực hiện

Người dùng đã có tài khoản.

###### c. Mô hình Usecase

```mermaid
flowchart LR
    A([Người dùng]) --> UC([Đăng nhập])
```

###### d. Kịch bản trường hợp sử dụng

Tên Use Case: Đăng nhập

###### e. Thiết kế mô hình nghiệp vụ

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Xác thực]
```

###### f. Thiết kế UX/UI và Mô tả điều khiển

_(cần chèn ảnh — không tự sinh)_

| Tên điều khiển | Mô tả điều khiển |
| --- | --- |
| Textbox "Tên đăng nhập" | Trường bắt buộc. |

###### g. Yêu cầu nghiệp vụ

Khi người dùng nhấn nút đăng nhập, hệ thống kiểm tra thông tin.

### Quên mật khẩu

<!-- FN: FN-01-02 -->

#### Sơ đồ chức năng

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Yêu cầu đặt lại mật khẩu]
```

#### Mục đích chức năng

Khôi phục quyền truy cập khi người dùng quên mật khẩu.

#### Mô tả chức năng

##### Quên mật khẩu

<!-- FN-leaf: FN-01-02 -->

###### a. Đối tượng tham gia

Người dùng hệ thống.

###### b. Điều kiện thực hiện

Người dùng đã có tài khoản.

###### c. Mô hình Usecase

```mermaid
flowchart LR
    A([Người dùng]) --> UC([Quên mật khẩu])
```

###### d. Kịch bản trường hợp sử dụng

Tên Use Case: Quên mật khẩu

###### e. Thiết kế mô hình nghiệp vụ

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Gửi email đặt lại mật khẩu]
```

###### f. Thiết kế UX/UI và Mô tả điều khiển

_(cần chèn ảnh — không tự sinh)_

Không có.

###### g. Yêu cầu nghiệp vụ

Hệ thống gửi email đặt lại mật khẩu.
"""


def test_parse_fn_comments_collects_ids():
    assert sv.parse_fn_comments(SRS_OK) == {"FN-01-01", "FN-01-02"}


def test_parse_fn_comments_handles_multiple_ids_in_one_comment():
    text = "<!-- FN: FN-01-01, FN-01-02 -->"
    assert sv.parse_fn_comments(text) == {"FN-01-01", "FN-01-02"}


def test_check_fn_coverage_clean():
    assert sv.check_fn_coverage(SRS_OK, WANTED) == []


def test_check_fn_coverage_blocking_when_missing():
    srs = SRS_OK.replace("<!-- FN: FN-01-02 -->", "<!-- FN: -->")
    out = sv.check_fn_coverage(srs, WANTED)
    assert any(b["loai"] == "thieu-fn" and "FN-01-02" in b["thong_diep"] for b in out)


_UC_TABLE = (
    "<table>\n"
    "<tr><td><b>Tên Use Case:</b> {name}</td>"
    "<td><b>Mức quan trọng:</b> Cao</td></tr>\n"
    "</table>"
)


def test_check_one_usecase_per_leaf_clean_with_single_table():
    srs = SRS_OK.replace(
        "###### d. Kịch bản trường hợp sử dụng\n\nTên Use Case: Đăng nhập",
        "###### d. Kịch bản trường hợp sử dụng\n\n"
        + _UC_TABLE.format(name="Đăng nhập"))
    assert sv.check_one_usecase_per_leaf(srs) == []


def test_check_one_usecase_per_leaf_blocks_multiple_tables():
    # Lỗi đã gặp thật: một leaf bị bẻ thành 6 use case -> 6 bảng liên tiếp.
    # Mọi gate khác im lặng vì tài liệu vẫn đầy nội dung, chỉ sai cấu trúc.
    srs = SRS_OK.replace(
        "###### d. Kịch bản trường hợp sử dụng\n\nTên Use Case: Đăng nhập",
        "###### d. Kịch bản trường hợp sử dụng\n\n"
        + _UC_TABLE.format(name="Đăng nhập bằng Username") + "\n\n"
        + _UC_TABLE.format(name="Đăng nhập bằng Google"))
    out = sv.check_one_usecase_per_leaf(srs)
    assert any(b["loai"] == "nhieu-use-case-mot-leaf" for b in out)


def test_check_one_usecase_per_leaf_allows_zero_table():
    # `d.` ghi "Chưa có thông tin" (0 bảng) vẫn hợp lệ với gate này.
    assert sv.check_one_usecase_per_leaf(SRS_OK) == []


def _ycnv_srs(n_bullets: int) -> str:
    bullets = "\n".join(
        f"- Khi người dùng thực hiện thao tác {k}, hệ thống phản hồi tương ứng."
        for k in range(n_bullets))
    return SRS_OK.replace(
        "###### g. Yêu cầu nghiệp vụ\n\nKhi người dùng nhấn nút đăng nhập, "
        "hệ thống kiểm tra thông tin.",
        f"###### g. Yêu cầu nghiệp vụ\n\n{bullets}")


def test_check_yeu_cau_nghiep_vu_length_quiet_at_cap():
    assert sv.check_yeu_cau_nghiep_vu_length(_ycnv_srs(sv.YCNV_SOFT_CAP)) == []


def test_check_yeu_cau_nghiep_vu_length_warns_above_cap():
    out = sv.check_yeu_cau_nghiep_vu_length(_ycnv_srs(sv.YCNV_SOFT_CAP + 1))
    assert any(w["loai"] == "yeu-cau-nghiep-vu-dai" for w in out)


def test_check_yeu_cau_nghiep_vu_length_is_warning_not_blocking():
    # Ngưỡng "quy tắc quan trọng" là phán đoán — Chức năng phức tạp thật sự
    # có thể vượt chính đáng, nên gate này KHÔNG được chặn báo xong.
    r = sv.verify(_ycnv_srs(sv.YCNV_SOFT_CAP + 10), WANTED)
    assert r["blocking"] == []
    assert any(w["loai"] == "yeu-cau-nghiep-vu-dai" for w in r["warnings"])


def test_check_html_table_integrity_clean_on_real_table():
    text = (
        "<table>\n"
        "<tr><td><b>Tên Use Case:</b> Đăng nhập</td>"
        "<td><b>Mức quan trọng:</b> Cao</td></tr>\n"
        "<tr><td colspan=\"2\"><b>Luồng sự kiện chuẩn:</b>\n"
        "<ol>\n<li>Bước 1</li>\n</ol>\n</td></tr>\n"
        "</table>\n"
    )
    assert sv.check_html_table_integrity(text) == []


def test_check_html_table_integrity_catches_blank_line_inside_table():
    # M5 (đợt review "trước khi hoàn thành"): critic chạy thật cho thấy một
    # dòng trống giữa hai <tr> lọt qua mọi gate — không cả warning.
    text = (
        "<table>\n"
        "<tr><td><b>Tên Use Case:</b> Đăng nhập</td>"
        "<td><b>Mức quan trọng:</b> Cao</td></tr>\n"
        "\n"
        "<tr><td colspan=\"2\"><b>Mô tả tóm tắt:</b> ...</td></tr>\n"
        "</table>\n"
    )
    out = sv.check_html_table_integrity(text)
    assert any(b["loai"] == "html-bang-hong" and "dòng trống" in b["thong_diep"]
               for b in out)


def test_check_html_table_integrity_catches_unbalanced_tag():
    text = (
        "<table>\n"
        "<tr><td><b>Tên Use Case:</b> Đăng nhập</td>"
        "<td><b>Mức quan trọng:</b> Cao</td></tr>\n"
        "<tr><td colspan=\"2\"><b>Luồng sự kiện chuẩn:</b>\n"
        "<ol>\n<li>Bước 1\n</ol>\n</td></tr>\n"  # <li> thiếu </li>
        "</table>\n"
    )
    out = sv.check_html_table_integrity(text)
    assert any(b["loai"] == "html-bang-hong" and "<li>" in b["thong_diep"] for b in out)


def test_check_leaf_blocks_clean_on_srs_ok():
    assert sv.check_leaf_blocks(SRS_OK) == []


def test_check_leaf_blocks_catches_fewer_blocks_than_leaves():
    # C2 (đợt review "trước khi hoàn thành"): thiết kế leaf-based bắt MỖI leaf
    # FN-ID một khối ##### riêng. Nếu model lặng lẽ quay lại gộp-theo-màn-hình
    # (2 leaf nhưng comment <!-- FN: --> vẫn liệt đủ 2 ID, chỉ viết 1 khối
    # ##### ), check_fn_coverage một mình KHÔNG bắt được (đã xác nhận qua
    # agent) — check_leaf_blocks phải bắt.
    srs = SRS_OK.replace("<!-- FN: FN-01-02 -->", "<!-- FN: FN-01-01, FN-01-02 -->")
    out = sv.check_leaf_blocks(srs)
    # Chức năng "Quên mật khẩu" giờ khai phủ cả FN-01-01 (thật ra thuộc khối
    # ##### của Chức năng "Đăng nhập" khác) nhưng tự thân nó chỉ có 1 khối
    # ##### (FN-01-02) -> thiếu khối cho FN-01-01.
    assert any(b["loai"] == "thieu-khoi-leaf" and "FN-01-01" in b["thong_diep"]
               for b in out)


def test_check_leaf_blocks_catches_missing_fn_leaf_comment():
    srs = SRS_OK.replace("<!-- FN-leaf: FN-01-01 -->\n\n", "")
    out = sv.check_leaf_blocks(srs)
    assert any(b["loai"] == "thieu-fn-leaf" for b in out)
    # thiếu comment FN-leaf -> cũng không thấy khối leaf khớp FN-01-01
    assert any(b["loai"] == "thieu-khoi-leaf" and "FN-01-01" in b["thong_diep"]
               for b in out)


DUP_LEAF_SRS = """### Quản lý người dùng

<!-- FN: FN-01-01, FN-01-02 -->

#### Sơ đồ chức năng

#### Mục đích chức năng

Quản lý tài khoản người dùng.

#### Mô tả chức năng

##### Tạo mới người dùng

<!-- FN-leaf: FN-01-01 -->

###### a. Đối tượng tham gia

Quản trị viên.

###### g. Yêu cầu nghiệp vụ

Hệ thống tạo tài khoản mới.

##### Xoá người dùng

<!-- FN-leaf: FN-01-01 -->

###### a. Đối tượng tham gia

Quản trị viên.

###### g. Yêu cầu nghiệp vụ

Hệ thống xoá tài khoản.
"""


def test_check_leaf_blocks_catches_duplicate_fn_leaf():
    # Hai khối ##### khác nhau trong CÙNG một Chức năng dùng trùng FN-leaf
    # FN-01-01 (lẽ ra khối thứ hai phải là FN-01-02) -> FN-01-02 thiếu khối
    # riêng, VÀ FN-01-01 bị gắn trùng ở 2 khối.
    out = sv.check_leaf_blocks(DUP_LEAF_SRS)
    assert any(b["loai"] == "trung-fn-leaf" and "FN-01-01" in b["thong_diep"]
               for b in out)
    assert any(b["loai"] == "thieu-khoi-leaf" and "FN-01-02" in b["thong_diep"]
               for b in out)


def test_check_leaf_blocks_catches_fn_leaf_not_in_fn_comment():
    srs = SRS_OK.replace("<!-- FN-leaf: FN-01-01 -->", "<!-- FN-leaf: FN-99-99 -->")
    out = sv.check_leaf_blocks(srs)
    assert any(b["loai"] == "fn-leaf-la" and "FN-99-99" in b["thong_diep"] for b in out)
    assert any(b["loai"] == "thieu-khoi-leaf" and "FN-01-01" in b["thong_diep"]
               for b in out)


def test_check_leaf_blocks_no_finding_when_fn_comment_missing_entirely():
    # Ca "thiếu hẳn <!-- FN: ... -->" đã có check_fn_coverage lo — check_leaf_blocks
    # không được tự ý báo thêm khi wanted_ids rỗng (tránh trùng finding).
    srs = SRS_OK.replace("<!-- FN: FN-01-01 -->", "<!-- FN: -->")
    out = sv.check_leaf_blocks(srs)
    assert not any("Đăng nhập" in b["thong_diep"] for b in out)


def test_clean_document_has_no_blocking():
    r = sv.verify(SRS_OK, WANTED)
    assert r["blocking"] == []


def test_missing_fn_comment_is_blocking():
    srs = SRS_OK.replace("<!-- FN: FN-01-02 -->", "<!-- FN: -->")
    r = sv.verify(srs, WANTED)
    assert any(b["loai"] == "thieu-fn" and "FN-01-02" in b["thong_diep"]
               for b in r["blocking"])


def test_placeholder_is_blocking():
    srs = SRS_OK + "\n[Tên phụ lục]\n"
    r = sv.verify(srs, WANTED)
    assert any(b["loai"] == "placeholder" for b in r["blocking"])


def test_markdown_link_is_not_a_placeholder():
    srs = SRS_OK + "\nXem [tài liệu tham khảo](https://example.com/a).\n"
    r = sv.verify(srs, WANTED)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_mermaid_block_is_not_a_placeholder():
    srs = SRS_OK + "\n```mermaid\nflowchart TD\n    B[Nhập thông tin]\n```\n"
    r = sv.verify(srs, WANTED)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_inline_code_syntax_example_is_not_a_placeholder():
    srs = SRS_OK + "\n| `A([Bắt đầu])` | `B[Nhập thông tin]` |\n"
    r = sv.verify(srs, WANTED)
    assert r["blocking"] == []


def test_fn_comment_itself_is_not_a_placeholder():
    # <!-- FN: FN-01-01, FN-01-02 --> không có dấu [] nào, nhưng xác nhận comment
    # HTML ẩn nói chung (bất kỳ nội dung nào) không lẫn vào placeholder detection.
    srs = SRS_OK + "\n<!-- ghi chú nội bộ [không phải placeholder] -->\n"
    r = sv.verify(srs, WANTED)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_empty_wanted_list_warns():
    r = sv.verify(SRS_OK, [])
    assert any(w["loai"] == "pham-vi-rong" for w in r["warnings"])


def test_check_chuc_nang_structure_clean():
    assert sv.check_chuc_nang_structure(SRS_OK) == []


def test_check_chuc_nang_structure_warns_when_missing_muc():
    srs = SRS_OK.replace("#### Mục đích chức năng\n\nXác thực danh tính người dùng "
                          "trước khi cho phép truy cập hệ thống.\n\n", "")
    out = sv.check_chuc_nang_structure(srs)
    assert any(w["loai"] == "chuc-nang-thieu-muc" and "Đăng nhập" in w["thong_diep"]
               and "Mục đích chức năng" in w["thong_diep"] for w in out)


def test_check_man_hinh_structure_clean():
    assert sv.check_man_hinh_structure(SRS_OK) == []


_DROP_F_SECTION = (
    "###### f. Thiết kế UX/UI và Mô tả điều khiển\n\n"
    "_(cần chèn ảnh — không tự sinh)_\n\n"
    "| Tên điều khiển | Mô tả điều khiển |\n"
    "| --- | --- |\n| Textbox \"Tên đăng nhập\" | Trường bắt buộc. |\n\n")


def test_check_man_hinh_structure_warns_when_missing_letter():
    srs = SRS_OK.replace(_DROP_F_SECTION, "")
    assert srs != SRS_OK  # fixture đúng khuôn -> phép xoá thật sự có hiệu lực
    out = sv.check_man_hinh_structure(srs)
    assert any(w["loai"] == "man-hinh-thieu-muc" and "Đăng nhập" in w["thong_diep"]
               and "f. Thiết kế UX/UI và Mô tả điều khiển" in w["thong_diep"]
               for w in out)


def test_check_man_hinh_structure_tolerates_numbered_heading():
    # Agent lỡ đánh số vị trí vào heading cố định "Mô tả chức năng" (vd
    # "2.1.3. Mô tả chức năng") -- cổng 7 mục a.-g. vẫn phải chạy, không được
    # âm thầm tắt hẳn vì so khớp chuỗi chính xác thất bại.
    srs = SRS_OK.replace("#### Mô tả chức năng", "#### 2.1.3. Mô tả chức năng", 1)
    srs = srs.replace(_DROP_F_SECTION, "")
    out = sv.check_man_hinh_structure(srs)
    assert any(w["loai"] == "man-hinh-thieu-muc" and "Đăng nhập" in w["thong_diep"]
               and "f. Thiết kế UX/UI và Mô tả điều khiển" in w["thong_diep"]
               for w in out)


def test_check_man_hinh_structure_ignores_missing_optional_mermaid():
    # Bỏ trống mermaid ở "c. Mô hình Usecase" và "e. Thiết kế mô hình nghiệp vụ" của
    # "Quên mật khẩu" (vẫn giữ heading) -- không được coi là thiếu mục, vì heading
    # vẫn có mặt. Dùng biến thể riêng (không phải SRS_OK) vì SRS_OK giờ là tài liệu
    # điền đủ hoàn toàn, dùng cho test_correct_document_has_zero_empty_section_warnings.
    srs = SRS_OK.replace(
        "###### c. Mô hình Usecase\n\n```mermaid\nflowchart LR\n"
        "    A([Người dùng]) --> UC([Quên mật khẩu])\n```\n\n",
        "###### c. Mô hình Usecase\n\n")
    srs = srs.replace(
        "###### e. Thiết kế mô hình nghiệp vụ\n\n```mermaid\nflowchart TD\n"
        "    A([Bắt đầu]) --> B[Gửi email đặt lại mật khẩu]\n```\n\n",
        "###### e. Thiết kế mô hình nghiệp vụ\n\n")
    out = sv.check_man_hinh_structure(srs)
    assert not any("Quên mật khẩu" in w["thong_diep"] for w in out)


def test_code_path_is_warning_not_blocking():
    srs = SRS_OK + "\nHành vi nằm ở src/auth/login.ts:42.\n"
    r = sv.verify(srs, WANTED)
    assert r["blocking"] == []
    assert any(w["loai"] == "nghi-duong-dan-code" for w in r["warnings"])


def test_empty_section_is_warning_only():
    srs = SRS_OK + "\n###### i. Mục thừa\n\n"
    r = sv.verify(srs, WANTED)
    assert r["blocking"] == []
    assert any(w["loai"] == "muc-rong" for w in r["warnings"])


def test_correct_document_has_zero_empty_section_warnings():
    # SRS_OK là tài liệu điền đủ, đúng cấu trúc 4 cấp: heading chứa (## Nhóm,
    # ### Chức năng, #### Mô tả chức năng) chỉ là container (con là heading sâu
    # hơn), không phải "mục rỗng"; mục có mermaid (Sơ đồ chức năng, c., e.) có nội
    # dung thật dù strip_noise xoá sạch fence. Không được có warning muc-rong nào.
    assert not any(w["loai"] == "muc-rong" for w in sv.verify(SRS_OK, WANTED)["warnings"])


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
    srs = SRS_OK.replace("<!-- FN: FN-01-02 -->", "<!-- FN: -->")
    p = _run(tmp_path, srs)
    assert p.returncode == 1
    assert json.loads(p.stdout)["blocking"]


def test_cli_empty_root_covers_whole_tree(tmp_path):
    p = _run(tmp_path, SRS_OK, root="")
    assert p.returncode == 1
    assert any(b["loai"] == "thieu-fn" and "FN-02-01" in b["thong_diep"]
               for b in json.loads(p.stdout)["blocking"])


def test_cli_reports_unknown_root(tmp_path):
    p = _run(tmp_path, SRS_OK, root="FN-99")
    assert p.returncode != 0
    assert "FN-99" in p.stderr


def test_cli_has_no_template_flag(tmp_path):
    import subprocess
    srs = tmp_path / "srs.md"
    srs.write_text(SRS_OK, encoding="utf-8")
    fns = tmp_path / "functions.json"
    fns.write_text(json.dumps({"functions": FUNCTIONS_TREE}, ensure_ascii=False),
                   encoding="utf-8")
    script = Path(sv.__file__)
    p = subprocess.run(
        [sys.executable, str(script), str(srs), "--functions", str(fns),
         "--root", "FN-01", "--template", "nope.md"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode != 0
    assert "unrecognized arguments" in p.stderr or "unrecognized arguments" in p.stdout


EMPTY_CHUC_NANG = """## Đăng ký đăng nhập

### Đăng nhập

<!-- FN: FN-01-01 -->

#### Sơ đồ chức năng

#### Mục đích chức năng

Chưa có thông tin.

#### Mô tả chức năng

###### a. Đối tượng tham gia

Chưa có thông tin.

###### b. Điều kiện thực hiện

Chưa có thông tin

###### c. Mô hình Usecase

###### d. Kịch bản trường hợp sử dụng

Chưa có thông tin.

###### e. Thiết kế mô hình nghiệp vụ

###### f. Thiết kế UX/UI và Mô tả điều khiển

_(cần chèn ảnh — không tự sinh)_

Không có.

###### g. Yêu cầu nghiệp vụ

Chưa có thông tin.
"""


EMPTY_CHUC_NANG_HTML_TABLE = """## Đăng ký đăng nhập

### Đăng nhập

<!-- FN: FN-01-01 -->

#### Sơ đồ chức năng

#### Mục đích chức năng

Chưa có thông tin.

#### Mô tả chức năng

###### a. Đối tượng tham gia

- Chưa có thông tin.

###### b. Điều kiện thực hiện

- Chưa có thông tin.

###### c. Mô hình Usecase

###### d. Kịch bản trường hợp sử dụng

<table>
<tr><td><b>Tên Use Case:</b> Chưa có thông tin</td><td><b>Mức quan trọng:</b> Chưa có thông tin</td></tr>
<tr><td><b>Người dùng:</b> Chưa có thông tin</td><td><b>Loại UC:</b> Chưa có thông tin</td></tr>
<tr><td colspan="2"><b>Người sử dụng và yêu cầu:</b> Chưa có thông tin</td></tr>
<tr><td colspan="2"><b>Mô tả tóm tắt:</b> Chưa có thông tin</td></tr>
<tr><td colspan="2"><b>Thời điểm sử dụng:</b> Chưa có thông tin</td></tr>
<tr><td colspan="2"><b>Luồng sự kiện chuẩn:</b> Chưa có thông tin</td></tr>
<tr><td colspan="2"><b>Luồng sự kiện nhỏ:</b> Chưa có thông tin</td></tr>
</table>

###### e. Thiết kế mô hình nghiệp vụ

###### f. Thiết kế UX/UI và Mô tả điều khiển

_(cần chèn ảnh — không tự sinh)_

| Tên điều khiển | Mô tả điều khiển |
| --- | --- |

###### g. Yêu cầu nghiệp vụ

Chưa có thông tin.
"""


def test_check_content_density_clean_on_srs_ok():
    assert sv.check_content_density(SRS_OK) == []


def test_check_content_density_blocks_empty_chuc_nang():
    out = sv.check_content_density(EMPTY_CHUC_NANG)
    assert any(b["loai"] == "chuc-nang-rong-ruot" and "Đăng nhập" in b["thong_diep"]
               for b in out)


def test_check_content_density_mermaid_only_item_counts_as_content():
    # Chức năng mà mọi mục a.-g. đều "Chưa có thông tin" TRỪ một mục chỉ có
    # mermaid (không văn xuôi) -> KHÔNG bị chặn, vì mục đó có nội dung thật.
    text = EMPTY_CHUC_NANG.replace(
        "###### c. Mô hình Usecase\n\n###### d.",
        "###### c. Mô hình Usecase\n\n```mermaid\nflowchart LR\n"
        "    A([Người dùng]) --> UC([Đăng nhập])\n```\n\n###### d.")
    out = sv.check_content_density(text)
    assert out == []


def test_check_content_density_not_found_evidence_phrase_is_not_empty():
    # V1 (fix round 2): Chức năng chưa tìm thấy code viết đúng câu quy định ở
    # mục g. (khác "Chưa có thông tin") -> KHÔNG bị chặn rỗng ruột, dù mọi mục
    # còn lại đều "Chưa có thông tin" (đúng luật bước 8 của srs-from-code.md).
    text = EMPTY_CHUC_NANG.replace(
        "###### g. Yêu cầu nghiệp vụ\n\nChưa có thông tin.",
        "###### g. Yêu cầu nghiệp vụ\n\nChưa tìm thấy hiện thực trong mã nguồn.")
    out = sv.check_content_density(text)
    assert out == []


def test_check_content_density_blocks_empty_html_table_d_and_empty_table_g():
    # C1 (đợt review "trước khi hoàn thành"): khung mới bắt `d.` LUÔN là một
    # khối <table> HTML thô, và `g.` là bảng markdown — cả hai không bao giờ
    # khớp _EMPTY_ITEM_RE (so khớp toàn chuỗi) dù mọi field bên trong đều
    # "Chưa có thông tin"/bảng không có dòng dữ liệu. Trước fix, ca này lọt
    # qua chuc-nang-rong-ruot hoàn toàn (đã xác nhận bằng agent chạy thật).
    out = sv.check_content_density(EMPTY_CHUC_NANG_HTML_TABLE)
    assert any(b["loai"] == "chuc-nang-rong-ruot" for b in out)


def test_check_content_density_real_html_table_d_counts_as_content():
    # Đối chứng: bảng <table> có nội dung THẬT (không phải toàn "Chưa có
    # thông tin") vẫn phải được tính là có nội dung — _structured_item_is_empty
    # không được chặn nhầm ca thật.
    text = EMPTY_CHUC_NANG_HTML_TABLE.replace(
        "<tr><td colspan=\"2\"><b>Mô tả tóm tắt:</b> Chưa có thông tin</td></tr>",
        "<tr><td colspan=\"2\"><b>Mô tả tóm tắt:</b> Người dùng nhập tài khoản "
        "và mật khẩu, hệ thống xác thực rồi tạo phiên đăng nhập.</td></tr>")
    out = sv.check_content_density(text)
    assert out == []


def test_structured_item_image_placeholder_alone_is_empty():
    # Mục f. (đã gộp UX/UI + Mô tả điều khiển) LUÔN mang placeholder ảnh cố
    # định; nếu coi chuỗi đó là "nội dung thật" thì mọi f. tự cứu chính nó khỏi
    # gate rỗng — đúng lỗi mà fix "Tên Use Case" vừa vá ở d.
    body = ("_(cần chèn ảnh — không tự sinh)_"
            "| Tên điều khiển | Mô tả điều khiển || --- | --- |")
    assert sv._structured_item_is_empty(body) is True


def test_structured_item_usecase_headings_alone_are_empty():
    # f. giờ chia theo từng use case bằng dòng in đậm `**[Tên use case]**`.
    # Tên đó suy từ mục d., không mang thông tin mới — một f. chỉ có các đầu
    # mục use case + placeholder ảnh + bảng rỗng vẫn phải bị coi là rỗng.
    body = ("**Tạo mới người dùng**_(cần chèn ảnh — không tự sinh)_"
            "| Tên điều khiển | Mô tả điều khiển || --- | --- |"
            "**Cập nhật người dùng**_(cần chèn ảnh — không tự sinh)_"
            "| Tên điều khiển | Mô tả điều khiển || --- | --- |")
    assert sv._structured_item_is_empty(body) is True


def test_structured_item_real_control_row_is_not_empty():
    body = ("_(cần chèn ảnh — không tự sinh)_"
            "| Tên điều khiển | Mô tả điều khiển || --- | --- |"
            "| **Button \"Lưu\"** | Nút cuối form, lưu thay đổi. |")
    assert sv._structured_item_is_empty(body) is False


def test_check_content_density_blocks_when_only_ten_use_case_is_filled():
    # Vòng verify 2 (đợt review "trước khi hoàn thành"): value của "Tên Use
    # Case" suy thẳng từ tên khối, tự nó không mang thông tin — một `d.` chỉ
    # điền mỗi field này (7 field còn lại "Chưa có thông tin", 7 mục a.-g.
    # còn lại cũng rỗng) KHÔNG được coi là Chức năng đã có nội dung.
    text = EMPTY_CHUC_NANG_HTML_TABLE.replace(
        "<tr><td><b>Tên Use Case:</b> Chưa có thông tin</td>",
        "<tr><td><b>Tên Use Case:</b> Đăng nhập</td>")
    out = sv.check_content_density(text)
    assert any(b["loai"] == "chuc-nang-rong-ruot" for b in out)


def test_check_leaf_content_density_catches_stub_leaf_block_hidden_by_sibling():
    # Vòng verify 2: check_content_density gộp theo Chức năng (###) — một
    # khối ##### rỗng bên cạnh một khối khác có nội dung thật KHÔNG bị bắt ở
    # cấp Chức năng (đã xác nhận: blocking rỗng trơn). check_leaf_content_density
    # phải bắt riêng khối rỗng đó.
    stub_srs = SRS_OK + """

##### Đổi mật khẩu

<!-- FN-leaf: FN-01-03 -->

###### a. Đối tượng tham gia

Chưa có thông tin.

###### b. Điều kiện thực hiện

Chưa có thông tin.

###### c. Mô hình Usecase

###### d. Kịch bản trường hợp sử dụng

Chưa có thông tin.

###### e. Thiết kế mô hình nghiệp vụ

###### f. Thiết kế UX/UI và Mô tả điều khiển

_(cần chèn ảnh — không tự sinh)_

Chưa có thông tin.

###### g. Yêu cầu nghiệp vụ

Chưa có thông tin.
"""
    # Chức năng cha "Quên mật khẩu" vẫn "sạch" ở cấp gộp vì khối FN-01-02 có
    # nội dung thật — xác nhận đúng như mô tả (không phải giả định):
    assert sv.check_content_density(stub_srs) == []
    out = sv.check_leaf_content_density(stub_srs)
    assert any(b["loai"] == "khoi-leaf-rong-ruot" and "Đổi mật khẩu" in b["thong_diep"]
               for b in out)


def test_check_html_table_integrity_catches_unclosed_table_tag():
    # Vòng verify 2: <table> không bao giờ đóng — ca lệch nặng nhất khi xuất
    # Word — trước đây _HTML_TABLE_BLOCK_RE đòi đủ cặp mở/đóng nên im lặng bỏ
    # qua hoàn toàn.
    text = "<table>\n<tr><td>Chưa có thông tin</td></tr>\n"  # thiếu </table>
    out = sv.check_html_table_integrity(text)
    assert any(b["loai"] == "html-bang-hong" and "không khớp" in b["thong_diep"]
               for b in out)


def test_check_leaf_blocks_ignores_mock_headings_inside_fenced_example():
    # Vòng verify 2: một khối rào minh hoạ khung (```markdown) có dòng
    # `### `/`##### ` mẫu bên trong KHÔNG được coi là heading thật, kẻo lệch
    # ranh giới Chức năng/khối leaf và báo oan thiếu khối.
    srs = SRS_OK.replace(
        "###### a. Đối tượng tham gia\n\nNgười dùng hệ thống.",
        "###### a. Đối tượng tham gia\n\n"
        "Người dùng hệ thống.\n\n"
        "```markdown\n### Ví dụ minh hoạ\n\n##### Một leaf giả\n```",
    )
    out = sv.check_leaf_blocks(srs)
    assert out == []


def test_check_content_density_blocks_empty_even_with_stray_dash_prefix():
    # M7 (đợt bổ sung "h. dạng list gạch đầu dòng"): nếu agent lỡ thêm "- " vào
    # trước câu rỗng cố định (đáng lẽ phải giữ plain sentence khi mục g. thật sự
    # không có gì để ghi) -> vẫn phải bị coi là rỗng, không được lọt qua cổng nhờ
    # dấu gạch đầu dòng thừa.
    text = EMPTY_CHUC_NANG.replace(
        "###### g. Yêu cầu nghiệp vụ\n\nChưa có thông tin.",
        "###### g. Yêu cầu nghiệp vụ\n\n- Chưa có thông tin.")
    out = sv.check_content_density(text)
    assert any(b["loai"] == "chuc-nang-rong-ruot" for b in out)


@pytest.mark.parametrize("variant", [
    "* Chưa có thông tin.",
    "+ Chưa có thông tin.",
    "1. Chưa có thông tin.",
    "2) Chưa có thông tin.",
    "**Chưa có thông tin.**",
])
def test_check_content_density_blocks_empty_with_other_bullet_or_emphasis_variants(variant):
    # m1 (đợt review "trước khi hoàn thành"): critic chạy thật cho thấy
    # _EMPTY_ITEM_RE cũ chỉ chặn đúng ký tự "-", ba biến thể bullet/số/in đậm
    # khác đều lọt qua (chuc-nang-rong-ruot không bắt được).
    text = EMPTY_CHUC_NANG.replace(
        "###### g. Yêu cầu nghiệp vụ\n\nChưa có thông tin.",
        f"###### g. Yêu cầu nghiệp vụ\n\n{variant}")
    out = sv.check_content_density(text)
    assert any(b["loai"] == "chuc-nang-rong-ruot" for b in out)


def test_verify_blocks_empty_chuc_nang_document():
    r = sv.verify(EMPTY_CHUC_NANG, ["FN-01-01"])
    assert any(b["loai"] == "chuc-nang-rong-ruot" for b in r["blocking"])


def test_check_no_clobber_chuc_nang_none_before_is_clean():
    assert sv.check_no_clobber_chuc_nang(SRS_OK, None) == []


def test_check_no_clobber_chuc_nang_passes_when_unchanged():
    assert sv.check_no_clobber_chuc_nang(SRS_OK, SRS_OK) == []


def test_check_no_clobber_chuc_nang_blocks_when_chuc_nang_dropped():
    before = SRS_OK
    after = SRS_OK.split("### Quên mật khẩu")[0]
    out = sv.check_no_clobber_chuc_nang(after, before)
    assert any(b["loai"] == "mat-chuc-nang" and "Quên mật khẩu" in b["thong_diep"]
               for b in out)


def test_check_no_clobber_chuc_nang_tolerates_position_number_prefix():
    # V2 (fix round 2): số thứ tự vị trí (thêm bởi bước 8 khi ghi khung, KHÔNG
    # có trong fixture SRS_OK) không được coi là mất Chức năng, chỉ so theo
    # tập FN-ID phủ -- không so theo tên/số nguyên văn.
    before = SRS_OK
    after = (SRS_OK
             .replace("### Đăng nhập", "### 1.1. Đăng nhập")
             .replace("### Quên mật khẩu", "### 1.2. Quên mật khẩu"))
    assert sv.check_no_clobber_chuc_nang(after, before) == []


def test_check_no_clobber_chuc_nang_tolerates_rename_when_fn_kept():
    # Đổi TÊN Chức năng (không đổi FN-ID nó phủ) -- hợp lệ khi intel.md đổi
    # tên hiển thị -- không được tính là mất.
    before = SRS_OK
    after = SRS_OK.replace("### Đăng nhập", "### Đăng nhập vào hệ thống")
    assert sv.check_no_clobber_chuc_nang(after, before) == []


def test_check_no_clobber_chuc_nang_still_blocks_when_fn_id_truly_gone():
    # Đổi tên VÀ đổi luôn FN-ID phủ (không FN-ID nào của khối cũ còn ở bản
    # mới) -- đây mới là ca mất thật, phải chặn dù tên đổi.
    before = SRS_OK
    after = (SRS_OK
             .replace("### Đăng nhập", "### Đăng nhập lại")
             .replace("<!-- FN: FN-01-01 -->", "<!-- FN: FN-09-09 -->"))
    out = sv.check_no_clobber_chuc_nang(after, before)
    assert any(b["loai"] == "mat-chuc-nang" and "FN-01-01" in b["thong_diep"]
               for b in out)


def test_check_no_clobber_chuc_nang_does_not_collapse_duplicate_titles():
    # Hai Chức năng khác Nhóm trùng tên hiển thị ("Danh sách") không được gộp
    # thành một mục trong bản đồ nội bộ -- gộp sẽ làm FN-ID của khối trùng tên
    # ĐẦU bị khối trùng tên SAU đè mất, tự tạo lại đúng lỗi no-clobber này
    # sinh ra để bắt (round 3 finding M-A).
    before = """## Nhom A

### Danh sách

<!-- FN: FN-01-01 -->

#### Sơ đồ chức năng

#### Mục đích chức năng

Xem danh sách A.

#### Mô tả chức năng

###### a. Đối tượng tham gia

Người dùng.

###### g. Yêu cầu nghiệp vụ

Hiển thị danh sách A.

## Nhom B

### Danh sách

<!-- FN: FN-02-01 -->

#### Sơ đồ chức năng

#### Mục đích chức năng

Xem danh sách B.

#### Mô tả chức năng

###### a. Đối tượng tham gia

Người dùng.

###### g. Yêu cầu nghiệp vụ

Hiển thị danh sách B.
"""
    # Chạy lại: cả hai khối "Danh sách" vẫn giữ nguyên -- không được báo mất.
    assert sv.check_no_clobber_chuc_nang(before, before) == []

    # Xoá hẳn khối "Danh sách" đầu tiên (FN-01-01) -- PHẢI báo mất, dù khối
    # "Danh sách" thứ hai (tên trùng, FN-ID khác) vẫn còn nguyên.
    after = before.replace(
        """### Danh sách

<!-- FN: FN-01-01 -->

#### Sơ đồ chức năng

#### Mục đích chức năng

Xem danh sách A.

#### Mô tả chức năng

###### a. Đối tượng tham gia

Người dùng.

###### g. Yêu cầu nghiệp vụ

Hiển thị danh sách A.

## Nhom B""", "## Nhom B")
    out = sv.check_no_clobber_chuc_nang(after, before)
    assert any(b["loai"] == "mat-chuc-nang" and "FN-01-01" in b["thong_diep"]
               for b in out)


def test_verify_blocks_when_before_loses_a_chuc_nang():
    before = SRS_OK
    after = SRS_OK.split("### Quên mật khẩu")[0]
    r = sv.verify(after, ["FN-01-01"], before)
    assert any(b["loai"] == "mat-chuc-nang" for b in r["blocking"])


def test_backtick_wrapped_code_path_is_still_a_warning():
    # M1: bọc đường dẫn trong backtick không được né cảnh báo nghi-duong-dan-code.
    srs = SRS_OK + "\nHành vi nằm ở `src/auth/login.ts:42`.\n"
    r = sv.verify(srs, WANTED)
    assert any(w["loai"] == "nghi-duong-dan-code" and "login.ts" in w["thong_diep"]
               for w in r["warnings"])


def test_backtick_mermaid_syntax_example_still_not_a_placeholder():
    # Xác nhận M1 không phá lại hành vi cũ: ví dụ cú pháp mermaid trong backtick
    # vẫn không bị tính là placeholder chưa điền.
    srs = SRS_OK + "\n| `A([Bắt đầu])` | `B[Nhập thông tin]` |\n"
    r = sv.verify(srs, WANTED)
    assert r["blocking"] == []


def test_cli_before_flag_enables_no_clobber_check(tmp_path):
    before = SRS_OK
    after = SRS_OK.split("### Quên mật khẩu")[0]
    before_path = tmp_path / "before.md"
    before_path.write_text(before, encoding="utf-8")
    # _run() không truyền --before mặc định; ghi srs.md/functions.json qua _run
    # rồi gọi subprocess trực tiếp thêm cờ --before.
    _run(tmp_path, after, root="FN-01")
    import subprocess
    srs = tmp_path / "srs.md"
    fns = tmp_path / "functions.json"
    script = Path(sv.__file__)
    p = subprocess.run(
        [sys.executable, str(script), str(srs), "--functions", str(fns),
         "--root", "FN-01", "--before", str(before_path)],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 1
    assert any(b["loai"] == "mat-chuc-nang" for b in json.loads(p.stdout)["blocking"])
