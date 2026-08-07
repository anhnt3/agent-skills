import pytest

from brd.outline import depth_map, parse_headings
from brd.splitter import _breadcrumbs, plan_nodes, write_tree
from brd.verify import VerifyError, check_roundtrip, reassemble, secondary_checks

MD = "\n".join(
    [
        "trang bìa",
        "",
        "# Nhóm A",
        "thân A",
        "### Module A1",
        "thân A1",
        "###### Màn 1",
        "![](./media/media/image1.png)",
        "######## Mục con",
        "thân mục con",
        "###### Màn 2",
        "thân màn 2",
    ]
)

META = {"source_file": "x.docx", "sha256": "abc", "imported_at": "2026-08-07",
        "pandoc": "3.9", "cut_depth": 3, "tier": 1, "tier_note": "test"}


def _prepare(tmp_path):
    hs = parse_headings(MD)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 3, len(MD.split("\n")))
    write_tree(nodes, MD.split("\n"), dmap, tmp_path, META)
    return nodes, dmap, _breadcrumbs(nodes)


def test_reassemble_khop_byte_for_byte(tmp_path):
    nodes, dmap, crumbs = _prepare(tmp_path)
    assert reassemble(nodes, tmp_path, dmap, crumbs) == MD


def test_check_roundtrip_khong_nem_khi_khop(tmp_path):
    nodes, dmap, crumbs = _prepare(tmp_path)
    check_roundtrip(nodes, tmp_path, dmap, crumbs, MD)


def test_check_roundtrip_nem_khi_co_nguoi_sua_mot_file(tmp_path):
    nodes, dmap, crumbs = _prepare(tmp_path)
    victim = tmp_path / "01-nhom-a" / "01-module-a1" / "01-man-1.md"
    victim.write_text(victim.read_text(encoding="utf-8") + "\nthừa ra\n", encoding="utf-8")
    with pytest.raises(VerifyError) as e:
        check_roundtrip(nodes, tmp_path, dmap, crumbs, MD)
    assert "dòng" in str(e.value)


def test_secondary_checks_bao_anh_khong_ton_tai(tmp_path):
    nodes, _, _ = _prepare(tmp_path)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", heading_count=5)
    assert any("image1.png" in w for w in warnings)


def test_secondary_checks_bao_lech_so_heading(tmp_path):
    nodes, _, _ = _prepare(tmp_path)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", heading_count=99)
    assert any("heading" in w.lower() for w in warnings)
