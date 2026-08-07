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
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", shallow_heading_count=4)
    assert any("image1.png" in w for w in warnings)


def test_secondary_checks_im_lang_khi_so_node_khop_so_heading_nong(tmp_path):
    nodes, _, _ = _prepare(tmp_path)
    (tmp_path / "media").mkdir()
    # MD có 4 heading ở độ sâu <= 3 (Nhóm A, Module A1, Màn 1, Màn 2)
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", shallow_heading_count=4)
    assert not any("node" in w.lower() for w in warnings)


def test_secondary_checks_bao_lech_so_heading(tmp_path):
    nodes, _, _ = _prepare(tmp_path)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", shallow_heading_count=1)
    assert any("heading" in w.lower() for w in warnings)


def test_khoi_code_co_dau_thang_khong_bi_viet_lai(tmp_path):
    """Dòng giống heading nằm trong khối code phải đi qua nguyên vẹn cả hai chiều."""
    md = "\n".join([
        "### A",
        "",
        "```",
        "# not a heading",
        "###### cũng không phải",
        "```",
        "",
        "#### B",
        "thân B",
    ])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 1, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    crumbs = _breadcrumbs(nodes)
    on_disk = (tmp_path / nodes[0]["path"]).read_text(encoding="utf-8")
    assert "\n# not a heading\n" in on_disk
    assert "\n###### cũng không phải\n" in on_disk
    assert reassemble(nodes, tmp_path, dmap, crumbs) == md


def test_anh_dang_html_va_markdown_deu_ghep_nguoc_khop_byte_for_byte(tmp_path):
    """gfm sinh ảnh dạng <img src=...>; cả hai dạng phải nghịch đảo chính xác."""
    md = "\n".join([
        "trang bìa",
        '<img src="./media/media/image0.png" style="width:5in" />',
        "# Nhóm A",
        "![](./media/media/image1.png)",
        "### Màn 1",
        '<img src="./media/media/image2.png" style="width:2in;height:1in" />',
        "### Màn 2",
        "![](./media/media/image3.png)",
    ])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 2, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    crumbs = _breadcrumbs(nodes)
    leaf = tmp_path / "01-nhom-a" / "01-man-1.md"
    assert 'src="../media/image2.png"' in leaf.read_text(encoding="utf-8")
    root = tmp_path / "_index.md"
    assert 'src="media/image0.png"' in root.read_text(encoding="utf-8")
    assert reassemble(nodes, tmp_path, dmap, crumbs) == md


def test_secondary_checks_thay_anh_dang_html(tmp_path):
    md = "\n".join([
        "# Nhóm A",
        '<img src="./media/media/image1.png" style="width:5in" />',
        "### Màn 1",
        "thân",
    ])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 2, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", shallow_heading_count=2)
    assert any("image1.png" in w and "không tồn tại" in w for w in warnings)


def test_check_roundtrip_nem_khi_nguon_da_co_san_duong_dan_media_tuong_doi(tmp_path):
    """Cạnh sắc ở node gốc: tiền tố rỗng nên nghịch đảo bắt trượt -> PHẢI nổ to.

    Khoá tính chất "fail loud" này lại để một lần tái cấu trúc sau không âm thầm
    biến nó thành làm hỏng nội dung.
    """
    md = "\n".join([
        'trang bìa <img src="media/x.png" />',
        "# Nhóm A",
        "thân A",
        "### Màn 1",
        "thân màn 1",
    ])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 2, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    crumbs = _breadcrumbs(nodes)
    with pytest.raises(VerifyError):
        check_roundtrip(nodes, tmp_path, dmap, crumbs, md)


def test_secondary_checks_bao_heading_nam_trong_khoi_table(tmp_path):
    md = "\n".join([
        "# Nhóm A",
        "<table>",
        "<tr><td>",
        "##### lẽ ra không phải heading",
        "</td></tr>",
        "</table>",
        "### Màn 1",
        "thân",
    ])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 2, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media",
                                shallow_heading_count=len(hs))
    assert any("<table>" in w for w in warnings)


def test_secondary_checks_im_lang_khi_table_khong_chua_heading(tmp_path):
    md = "\n".join([
        "# Nhóm A",
        "<table>",
        "<tr><td>ô bình thường</td></tr>",
        "</table>",
        "### Màn 1",
        "thân",
    ])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 2, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media",
                                shallow_heading_count=len(hs))
    assert not any("<table>" in w for w in warnings)


def _parse_frontmatter(text):
    """Bộ đọc frontmatter tí hon (không thêm phụ thuộc YAML)."""
    assert text.startswith("---\n")
    body = text[4:]
    end = body.index("\n---\n")
    out = {}
    for line in body[:end].split("\n"):
        key, _, val = line.partition(": ")
        out[key] = val
    return out


def _unquote(val):
    assert val.startswith('"') and val.endswith('"'), val
    inner, res, i = val[1:-1], [], 0
    while i < len(inner):
        if inner[i] == "\\":
            i += 1
            assert i < len(inner), "dấu \\ treo lơ lửng -> YAML hỏng"
            res.append(inner[i])
        else:
            assert inner[i] != '"', "dấu \" chưa escape -> YAML hỏng"
            res.append(inner[i])
        i += 1
    return "".join(res)


def test_frontmatter_escape_dau_nhay_va_backslash(tmp_path):
    title = 'Màn "Đăng nhập" C:\\path'
    md = "\n".join(["# " + title, "thân A", "### Con", "thân con"])
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 2, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    crumbs = _breadcrumbs(nodes)

    root_fm = _parse_frontmatter((tmp_path / nodes[0]["path"]).read_text(encoding="utf-8"))
    assert _unquote(root_fm["title"]) == title
    child_fm = _parse_frontmatter((tmp_path / nodes[1]["path"]).read_text(encoding="utf-8"))
    assert child_fm["breadcrumb"].startswith("[") and child_fm["breadcrumb"].endswith("]")
    assert _unquote(child_fm["breadcrumb"][1:-1]) == title

    assert reassemble(nodes, tmp_path, dmap, crumbs) == md


def test_reassemble_khop_byte_for_byte_khi_heading_co_khoang_trang_le(tmp_path):
    md = "\n".join(
        [
            "#  Nhóm A {#section .TOC-Heading}",
            "thân A",
            "### Module A1 ",
            "thân A1",
        ]
    )
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 3, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    crumbs = _breadcrumbs(nodes)
    assert reassemble(nodes, tmp_path, dmap, crumbs) == md


def test_reassemble_khop_byte_for_byte_khi_heading_o_dau_file(tmp_path):
    md = "\n".join(
        [
            "# Nhóm A",
            "thân A",
            "### Module A1",
            "thân A1",
        ]
    )
    hs = parse_headings(md)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 3, len(md.split("\n")))
    write_tree(nodes, md.split("\n"), dmap, tmp_path, META)
    crumbs = _breadcrumbs(nodes)
    assert reassemble(nodes, tmp_path, dmap, crumbs) == md
