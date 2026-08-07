from brd.outline import depth_map, parse_headings
from brd.splitter import (
    frontmatter_of,
    plan_nodes,
    rel_media_prefix,
    render_file,
    write_tree,
)

MD = "\n".join(
    [
        "trang bìa",            # 0
        "",                     # 1
        "# Nhóm A",             # 2
        "thân A",               # 3
        "### Module A1",        # 4
        "thân A1",              # 5
        "###### Màn 1",         # 6
        "![](./media/media/image1.png)",  # 7
        "######## Mục con",     # 8
        "thân mục con",         # 9
        "###### Màn 2",         # 10
        "thân màn 2",           # 11
    ]
)


def _plan(cut_depth=3):
    hs = parse_headings(MD)
    return hs, depth_map(hs), plan_nodes(hs, depth_map(hs), cut_depth, len(MD.split("\n")))


def test_plan_nodes_co_node_goc_giu_phan_truoc_heading_dau():
    _, _, nodes = _plan()
    root = nodes[0]
    assert root["id"] == "BRD-0000"
    assert root["kind"] == "root"
    assert root["path"] == "_index.md"
    assert (root["start"], root["end"]) == (0, 2)


def test_plan_nodes_phan_loai_folder_va_leaf():
    _, _, nodes = _plan()
    kinds = [(n["title"], n["kind"]) for n in nodes[1:]]
    assert kinds == [
        ("Nhóm A", "folder"),
        ("Module A1", "folder"),
        ("Màn 1", "leaf"),
        ("Màn 2", "leaf"),
    ]


def test_plan_nodes_duong_dan_long_theo_cay_va_co_tien_to_so():
    _, _, nodes = _plan()
    paths = [n["path"] for n in nodes[1:]]
    assert paths == [
        "01-nhom-a/_index.md",
        "01-nhom-a/01-module-a1/_index.md",
        "01-nhom-a/01-module-a1/01-man-1.md",
        "01-nhom-a/01-module-a1/02-man-2.md",
    ]


def test_plan_nodes_segment_ke_tiep_nhau_khong_ho_khong_chong():
    _, _, nodes = _plan()
    spans = [(n["start"], n["end"]) for n in nodes]
    assert spans == [(0, 2), (2, 4), (4, 6), (6, 10), (10, 12)]


def test_heading_sau_hon_cap_cat_nam_trong_file_la():
    _, dmap, nodes = _plan()
    leaf = nodes[3]
    body = render_file(leaf, MD.split("\n"), dmap, ["Nhóm A", "Module A1"])
    assert "\n# Màn 1" in body
    assert "\n## Mục con" in body


def test_render_file_doi_duong_dan_anh_theo_do_sau():
    _, dmap, nodes = _plan()
    leaf = nodes[3]
    body = render_file(leaf, MD.split("\n"), dmap, ["Nhóm A", "Module A1"])
    assert "](../../media/image1.png)" in body


def test_rel_media_prefix():
    assert rel_media_prefix("_index.md") == ""
    assert rel_media_prefix("01-a/_index.md") == "../"
    assert rel_media_prefix("01-a/01-b/02-man-2.md") == "../../"


def test_frontmatter_of_co_dung_ba_khoa():
    _, _, nodes = _plan()
    fm = frontmatter_of(nodes[3], ["Nhóm A", "Module A1"])
    assert fm.startswith("---\n")
    assert "brd_id: BRD-0003\n" in fm
    assert 'title: "Màn 1"\n' in fm
    assert 'breadcrumb: ["Nhóm A", "Module A1"]\n' in fm
    assert fm.endswith("---\n\n")


def test_write_tree_ghi_du_file_va_manifest(tmp_path):
    _, dmap, nodes = _plan()
    write_tree(nodes, MD.split("\n"), dmap, tmp_path,
               {"source_file": "x.docx", "sha256": "abc", "imported_at": "2026-08-07",
                "pandoc": "3.9", "cut_depth": 3, "tier": 1, "tier_note": "test"})
    assert (tmp_path / "brd.manifest.yml").exists()
    assert (tmp_path / "01-nhom-a" / "01-module-a1" / "01-man-1.md").exists()
    manifest = (tmp_path / "brd.manifest.yml").read_text(encoding="utf-8")
    assert "cut_depth: 3" in manifest
    assert "depth_map: {1: 1, 2: 3, 3: 6, 4: 8}" in manifest
