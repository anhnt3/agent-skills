import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brd.naming import slugify


def test_bo_dau_tieng_viet():
    assert slugify("Quản lý người dùng quản trị") == "quan-ly-nguoi-dung-quan-tri"


def test_chu_d_gach_ngang():
    assert slugify("Đăng nhập") == "dang-nhap"


def test_ky_tu_dac_biet_thanh_gach_noi():
    assert slugify("Quản lý doanh nghiệp (nhà trường/trung tâm)") == (
        "quan-ly-doanh-nghiep-nha-truong-trung-tam"
    )


def test_khong_gach_noi_lien_nhau_hay_o_hai_dau():
    assert slugify("  Giám sát:  phần cứng; phần mềm  ") == (
        "giam-sat-phan-cung-phan-mem"
    )


def test_cat_theo_maxlen_khong_de_gach_noi_o_cuoi():
    out = slugify("Báo cáo phân bổ doanh thu khách hàng theo gói dịch vụ", maxlen=20)
    assert len(out) <= 20
    assert not out.endswith("-")


def test_tieu_de_khong_con_ky_tu_hop_le_thi_tra_ve_muc():
    assert slugify("???") == "muc"
