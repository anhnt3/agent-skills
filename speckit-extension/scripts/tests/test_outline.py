import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brd.outline import (
    depth_map,
    level_stats,
    parse_headings,
    recommend_depth,
    segment_ends,
)

MD = "\n".join(
    [
        "mở đầu",             # 0
        "",                   # 1
        "# Nhóm A",           # 2
        "thân A",             # 3
        "### Phân hệ A1",     # 4
        "thân A1",            # 5
        "###### Màn 1",       # 6
        "thân màn 1",         # 7
        "######## Mục con",   # 8
        "thân mục con",       # 9
        "###### Màn 2",       # 10
        "thân màn 2",         # 11
    ]
)


def test_parse_headings_bat_dung_cap_va_dong():
    hs = parse_headings(MD)
    assert [(h["line"], h["level"], h["title"]) for h in hs] == [
        (2, 1, "Nhóm A"),
        (4, 3, "Phân hệ A1"),
        (6, 6, "Màn 1"),
        (8, 8, "Mục con"),
        (10, 6, "Màn 2"),
    ]


def test_parse_headings_bo_qua_khoi_code():
    md = "```\n# không phải heading\n```\n# thật"
    assert [h["title"] for h in parse_headings(md)] == ["thật"]


def test_parse_headings_bo_qua_thang_khong_co_dau_cach():
    assert parse_headings("#khong-phai-heading") == []


def test_parse_headings_giu_title_da_strip_du_co_khoang_trang_thua():
    md = "#  Tiêu đề  {#section .TOC-Heading}  \n#### Mục con "
    hs = parse_headings(md)
    assert [h["title"] for h in hs] == [
        "Tiêu đề  {#section .TOC-Heading}",
        "Mục con",
    ]


def test_depth_map_nen_cap_thua_thanh_lien_tuc():
    assert depth_map(parse_headings(MD)) == {1: 1, 3: 2, 6: 3, 8: 4}


def test_segment_ends_dung_ket_thuc_theo_cap():
    hs = parse_headings(MD)
    total = len(MD.split("\n"))
    # Nhóm A -> hết file; Phân hệ A1 -> hết file; Màn 1 -> dòng 10; Mục con -> dòng 10
    assert segment_ends(hs, total) == [total, total, 10, 10, total]


def test_level_stats_dem_va_do_kich_thuoc():
    hs = parse_headings(MD)
    lines = MD.split("\n")
    stats = level_stats(hs, lines, depth_map(hs))
    by_depth = {s["depth"]: s for s in stats}
    assert by_depth[1]["count"] == 1
    assert by_depth[3]["count"] == 2
    assert by_depth[3]["word_level"] == 6
    assert by_depth[3]["min"] > 0


def test_recommend_depth_lay_cap_sau_nhat_dat_nguong():
    stats = [
        {"depth": 1, "median": 900_000},
        {"depth": 2, "median": 200_000},
        {"depth": 3, "median": 30_000},
        {"depth": 4, "median": 305},      # trượt
        {"depth": 5, "median": 23_808},   # đạt, sâu hơn -> phải chọn cái này
        {"depth": 6, "median": 174},
    ]
    assert recommend_depth(stats, min_median=3000) == 5


def test_recommend_depth_khong_cap_nao_dat_thi_tra_ve_1():
    assert recommend_depth([{"depth": 1, "median": 10}], min_median=3000) == 1
