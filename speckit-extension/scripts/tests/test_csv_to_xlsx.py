"""Test cho csv_to_xlsx.py.

Trọng tâm: cổng chống mất dữ liệu tester (cột 13-16). Trước đây script chỉ in
WARNING ra stderr rồi VẪN ghi đè — luật "gặp WARNING thì dừng" nằm ở tài liệu và
hoàn toàn trông chờ agent tự giác. Đây là lớp cưỡng chế cơ học thay cho luật đó.
"""
import json

import pytest

import csv_to_xlsx as mod

openpyxl = pytest.importorskip("openpyxl", reason="csv_to_xlsx cần openpyxl")

H = mod.EXPECTED_HEADER


def case(id_, **over):
    """Một case hợp lệ, đủ mọi key của hợp đồng."""
    row = {h: "" for h in H}
    row.update({
        "ID": id_,
        "Tiêu đề": f"Case {id_}",
        "Nhóm": "Đăng nhập",
        "Ưu tiên": "P1",
        "Loại": "Happy path",
        "Tiền điều kiện": "Đã có tài khoản",
        "Dữ liệu test": "user/pass",
        "Các bước thực hiện": "1. Bấm Đăng nhập",
        "Kết quả mong đợi": "1. Vào trang chủ",
        "Truy vết": "FR-01",
        "Test tự động": "manual-only",
        "Nguồn BRD": "docs/brd/01-dang-nhap.md#mo-ta-dieu-khien",
    })
    row.update(over)
    return row


def write_json(tmp_path, cases, name="in.json"):
    p = tmp_path / name
    p.write_text(json.dumps(cases, ensure_ascii=False), encoding="utf-8")
    return p


def fill_as_tester(xlsx, id_, ket_qua="Đúng như mong đợi", trang_thai="Pass"):
    """Giả lập tester mở file lên điền tay cột 13-14."""
    wb = openpyxl.load_workbook(xlsx)
    ws = wb["Testcases"]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == id_:
            row[12].value = ket_qua
            row[13].value = trang_thai
    wb.save(xlsx)


def read_col(xlsx, id_, idx):
    wb = openpyxl.load_workbook(xlsx)
    ws = wb["Testcases"]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] == id_:
            return row[idx]
    return None


# --- hợp đồng cột -----------------------------------------------------------

def test_header_co_dung_17_cot_va_nguon_brd_o_cuoi():
    assert len(H) == 17
    assert H[-1] == "Nguồn BRD"
    # Cột tester PHẢI giữ nguyên vị trí 13-16; đổi là vỡ merge + file cũ.
    assert H[12:16] == ["Kết quả thực tế", "Trạng thái", "Bug ID", "Ghi chú"]
    assert mod.EXEC_COL_IDX == (12, 13, 14, 15)


def test_json_thieu_key_nguon_brd_bi_tu_choi(tmp_path):
    bad = case("TC-A-001")
    del bad["Nguồn BRD"]
    p = write_json(tmp_path, [bad])
    with pytest.raises(ValueError, match="Nguồn BRD"):
        mod.read_cases_json(p)


def test_nguon_brd_duoc_ghi_ra_xlsx(tmp_path):
    out = tmp_path / "out.xlsx"
    p = write_json(tmp_path, [case("TC-A-001")])
    assert mod.main([str(p), str(out)]) == 0
    assert read_col(out, "TC-A-001", mod.COL_BRD) == "docs/brd/01-dang-nhap.md#mo-ta-dieu-khien"


def test_nguon_brd_cho_phep_dau_phay_khong_lam_vo_ma_tran(tmp_path):
    """Cột 17 là hiển thị, KHÔNG bị parse như cột Truy vết."""
    out = tmp_path / "out.xlsx"
    c = case("TC-A-001", **{"Nguồn BRD": "docs/brd/x.md#Tạo, sửa, xoá"})
    p = write_json(tmp_path, [c])
    assert mod.main([str(p), str(out)]) == 0
    wb = openpyxl.load_workbook(out)
    assert wb["Ma trận truy vết"].max_row == 2  # header + đúng 1 dòng FR-01


# --- cổng chống mất dữ liệu tester ------------------------------------------

def test_doi_id_lam_mat_du_lieu_tester_thi_dung_va_khong_ghi(tmp_path):
    out = tmp_path / "out.xlsx"
    p1 = write_json(tmp_path, [case("TC-A-001")], "in1.json")
    assert mod.main([str(p1), str(out)]) == 0
    fill_as_tester(out, "TC-A-001")
    before = out.read_bytes()

    # Renumber (đúng kịch bản mất dữ liệu): TC-A-001 -> TC-A-002
    p2 = write_json(tmp_path, [case("TC-A-002")], "in2.json")
    assert mod.main([str(p2), str(out)]) == 2
    assert out.read_bytes() == before, "file phải KHÔNG bị chạm khi cổng chặn"


def test_allow_id_loss_cho_phep_ghi_de(tmp_path):
    out = tmp_path / "out.xlsx"
    p1 = write_json(tmp_path, [case("TC-A-001")], "in1.json")
    mod.main([str(p1), str(out)])
    fill_as_tester(out, "TC-A-001")

    p2 = write_json(tmp_path, [case("TC-A-002")], "in2.json")
    assert mod.main([str(p2), str(out), "--allow-id-loss"]) == 0
    assert read_col(out, "TC-A-001", 12) is None
    assert read_col(out, "TC-A-002", 0) == "TC-A-002"


def test_giu_id_thi_du_lieu_tester_duoc_merge_nguyen_ven(tmp_path):
    out = tmp_path / "out.xlsx"
    p1 = write_json(tmp_path, [case("TC-A-001")], "in1.json")
    mod.main([str(p1), str(out)])
    fill_as_tester(out, "TC-A-001", "Vào được trang chủ", "Pass")

    # Chạy lại để cập nhật cột 12 (Kết quả tự động) — kịch bản Pha 8.
    p2 = write_json(
        tmp_path,
        [case("TC-A-001", **{"Kết quả tự động": "Pass @ a1b2c3d"})],
        "in2.json",
    )
    assert mod.main([str(p2), str(out)]) == 0
    assert read_col(out, "TC-A-001", 12) == "Vào được trang chủ"
    assert read_col(out, "TC-A-001", 13) == "Pass"
    assert read_col(out, "TC-A-001", 11) == "Pass @ a1b2c3d"


def test_id_bien_mat_nhung_tester_chua_dien_thi_khong_chan(tmp_path):
    """Không có gì để mất thì không được cản trở."""
    out = tmp_path / "out.xlsx"
    p1 = write_json(tmp_path, [case("TC-A-001")], "in1.json")
    mod.main([str(p1), str(out)])
    p2 = write_json(tmp_path, [case("TC-A-002")], "in2.json")
    assert mod.main([str(p2), str(out)]) == 0


def test_doc_duoc_file_cu_16_cot(tmp_path):
    """File xlsx sinh trước khi thêm cột 17 vẫn phải merge đúng, không mất dữ liệu."""
    out = tmp_path / "old.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Testcases"
    ws.append(H[:16])
    old = [""] * 16
    old[0] = "TC-A-001"
    old[12] = "Kết quả cũ của tester"
    old[13] = "Pass"
    ws.append(old)
    wb.save(out)

    p = write_json(tmp_path, [case("TC-A-001")])
    assert mod.main([str(p), str(out)]) == 0
    assert read_col(out, "TC-A-001", 12) == "Kết quả cũ của tester"
    assert read_col(out, "TC-A-001", 13) == "Pass"
