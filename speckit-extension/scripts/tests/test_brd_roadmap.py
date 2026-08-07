import json
import subprocess
import sys
from pathlib import Path

import pytest

from brd_roadmap import breadcrumbs, node_loc, parse_manifest
from brd_roadmap import head_lines, headings_of, signals_of, strip_frontmatter
from brd_roadmap import build_outline, tree_diff
from brd_roadmap import check_ids, check_placeholders, parse_roadmap
from brd_roadmap import check_coverage, norm_source, slugify_anchor

SCRIPT = Path(__file__).resolve().parents[1] / "brd_roadmap.py"

MANIFEST = """schema_version: "1.0"
source:
  file: "x.docx"
  sha256: "abc"
  imported_at: "2026-08-07"
  pandoc: "3.9"
cut_depth: 2
detection: { tier: 1, note: "test" }
depth_map: {1: 1, 3: 2}
nodes:
  - { id: BRD-0000, order: 0, depth: 0, word_level: 0, kind: root, title: "(phần đầu tài liệu)", path: "_index.md", parent: null, chars: 12 }
  - { id: BRD-0001, order: 1, depth: 1, word_level: 1, kind: folder, title: "Nhóm A, phần \\"chính\\"", inline: true, dir: "01-nhom-a/", parent: null, chars: 10 }
  - { id: BRD-0002, order: 2, depth: 2, word_level: 3, kind: leaf, title: "Màn danh sách", path: "01-nhom-a/01-man-danh-sach.md", parent: BRD-0001, chars: 320 }
  - { id: BRD-0003, order: 3, depth: 2, word_level: 3, kind: leaf, title: "Thuật ngữ", path: "01-nhom-a/02-thuat-ngu.md", parent: BRD-0001, chars: 40 }
"""

ROOT_MD = """---
brd_id: BRD-0000
title: "(phần đầu tài liệu)"
breadcrumb: []
---

Trang bìa tài liệu.
"""

MAN_MD = """---
brd_id: BRD-0002
title: "Màn danh sách"
breadcrumb: ["Nhóm A, phần \\"chính\\""]
---

# Màn danh sách

Màn hiển thị danh sách hợp đồng, cho phép Thêm, Sửa, Xoá và Tìm kiếm.
Người dùng có quyền Quản trị mới được Duyệt.

## Bộ lọc

| Trường | Kiểu | Bắt buộc |
|--------|------|----------|
| Mã hợp đồng | text | có |
| Ngày ký | date | không |

<img src="../media/image1.png" />

## Quy tắc

Chỉ vai trò Quản trị được Xoá.
"""

TERM_MD = """---
brd_id: BRD-0003
title: "Thuật ngữ"
breadcrumb: ["Nhóm A, phần \\"chính\\""]
---

# Thuật ngữ

BRD: Business Requirement Document.
"""


@pytest.fixture
def brd(tmp_path):
    """Cây BRD nhỏ, đúng định dạng brd-import sinh ra."""
    root = tmp_path / "docs" / "brd"
    (root / "01-nhom-a").mkdir(parents=True)
    (root / "brd.manifest.yml").write_text(MANIFEST, encoding="utf-8")
    (root / "_index.md").write_text(ROOT_MD, encoding="utf-8")
    (root / "01-nhom-a" / "01-man-danh-sach.md").write_text(MAN_MD, encoding="utf-8")
    (root / "01-nhom-a" / "02-thuat-ngu.md").write_text(TERM_MD, encoding="utf-8")
    return root


def test_parse_manifest_doc_du_node(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert [n["id"] for n in nodes] == ["BRD-0000", "BRD-0001", "BRD-0002", "BRD-0003"]
    assert nodes[0]["kind"] == "root"
    assert nodes[0]["parent"] is None
    assert nodes[2]["parent"] == "BRD-0001"
    assert nodes[2]["chars"] == 320


def test_parse_manifest_title_co_dau_phay_va_ngoac_kep_escape(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert nodes[1]["title"] == 'Nhóm A, phần "chính"'


def test_parse_manifest_node_inline_khong_co_path(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert nodes[1]["inline"] is True
    assert nodes[1]["path"] is None
    assert nodes[1]["dir"] == "01-nhom-a/"
    assert node_loc(nodes[1]) == "01-nhom-a/"
    assert node_loc(nodes[2]) == "01-nhom-a/01-man-danh-sach.md"


def test_breadcrumbs_theo_chuoi_cha(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    crumbs = breadcrumbs(nodes)
    assert crumbs["BRD-0002"] == ['Nhóm A, phần "chính"']
    assert crumbs["BRD-0001"] == []


def test_strip_frontmatter_go_dung_khoi_dau(brd):
    text = (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    body = strip_frontmatter(text)
    assert not body.startswith("---")
    assert body.lstrip().startswith("# Màn danh sách")


def test_headings_of_lay_du_cap(brd):
    text = strip_frontmatter(
        (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    )
    assert headings_of(text) == [
        {"level": 1, "text": "Màn danh sách"},
        {"level": 2, "text": "Bộ lọc"},
        {"level": 2, "text": "Quy tắc"},
    ]


def test_headings_of_bo_qua_heading_trong_khoi_code():
    text = "# Thật\n\n```\n# Giả\n```\n\n## Thật 2\n"
    assert headings_of(text) == [
        {"level": 1, "text": "Thật"},
        {"level": 2, "text": "Thật 2"},
    ]


def test_head_lines_bo_dong_trang_va_heading(brd):
    text = strip_frontmatter(
        (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    )
    head = head_lines(text, 2)
    assert head == [
        "Màn hiển thị danh sách hợp đồng, cho phép Thêm, Sửa, Xoá và Tìm kiếm.",
        "Người dùng có quyền Quản trị mới được Duyệt.",
    ]


def test_signals_of_dem_dung(brd):
    text = strip_frontmatter(
        (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    )
    sig = signals_of(text)
    assert sig["tables"] == 1
    assert sig["table_rows"] == 4
    assert sig["images"] == 1
    assert sig["field_table"] is True
    assert sig["permission_words"] >= 2      # "quyền" x2 + "vai trò" x1
    assert sig["action_words"] >= 5          # Thêm/Sửa/Xoá/Tìm kiếm/Duyệt/Xoá


def test_signals_of_file_khong_co_gi(brd):
    text = strip_frontmatter((brd / "01-nhom-a" / "02-thuat-ngu.md").read_text(encoding="utf-8"))
    sig = signals_of(text)
    assert sig["tables"] == 0
    assert sig["images"] == 0
    assert sig["field_table"] is False


def test_tree_diff_bao_file_thua_va_node_mat(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    (brd / "01-nhom-a" / "03-ba-them-tay.md").write_text("# BA thêm tay\n", encoding="utf-8")
    (brd / "01-nhom-a" / "02-thuat-ngu.md").unlink()
    extra, missing = tree_diff(brd, nodes)
    assert extra == ["01-nhom-a/03-ba-them-tay.md"]
    assert missing == ["01-nhom-a/02-thuat-ngu.md"]


def test_tree_diff_cay_nguyen_ven_thi_rong(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert tree_diff(brd, nodes) == ([], [])


def test_build_outline_moi_node_co_du_khoa(brd):
    out = build_outline(brd, head=15)
    assert out["node_count"] == 4
    man = next(n for n in out["nodes"] if n["id"] == "BRD-0002")
    assert man["breadcrumb"] == ['Nhóm A, phần "chính"']
    assert man["path"] == "01-nhom-a/01-man-danh-sach.md"
    assert {"level": 2, "text": "Bộ lọc"} in man["headings"]
    assert man["head"]
    assert man["signals"]["images"] == 1


def test_build_outline_node_inline_khong_doc_file(brd):
    out = build_outline(brd, head=15)
    grp = next(n for n in out["nodes"] if n["id"] == "BRD-0001")
    assert grp["inline"] is True
    assert grp["dir"] == "01-nhom-a/"
    assert grp["headings"] == []
    assert grp["signals"] is None


def test_cli_outline_ghi_file_va_in_stdout(brd, tmp_path):
    dest = tmp_path / "out" / "outline.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(brd), "--out", str(dest)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    assert dest.is_file()
    assert json.loads(proc.stdout)["node_count"] == 4


def test_cli_outline_thu_muc_khong_co_manifest_thi_chet(tmp_path):
    (tmp_path / "trong").mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(tmp_path / "trong")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert "brd.manifest.yml" in proc.stderr


ROADMAP_OK = """# Roadmap Build — Dự án X

**Mục tiêu**: thứ tự build/hoàn thiện từng màn/chức năng.
**Cập nhật**: 2026-08-07
**Trạng thái item**: `chưa` (mặc định) / `đang` / `xong`.

## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
| RM-001 | Đăng nhập | auth | 0 | N/A | chưa |
| RM-002 | Màn danh sách | hop-dong | 1 | RM-001 | chưa |

## Chi tiết

### RM-001 — Đăng nhập (auth, Wave 0)

- **Mô tả**: đăng nhập hệ thống
- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md#Quy tắc
- **Thực thể/CRUD**: User
- **Phụ thuộc**: N/A
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống)

### RM-002 — Màn danh sách (hop-dong, Wave 1)

- **Mô tả**: danh sách hợp đồng
- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md
- **Thực thể/CRUD**: HopDong
- **Phụ thuộc**: RM-001
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống)
"""


def test_parse_roadmap_doc_bang_tong_va_chi_tiet():
    p = parse_roadmap(ROADMAP_OK)
    assert p["row_order"] == ["RM-001", "RM-002"]
    assert p["rows"]["RM-002"]["module"] == "hop-dong"
    assert p["rows"]["RM-002"]["wave"] == "1"
    assert p["rows"]["RM-002"]["deps_raw"] == "RM-001"
    assert p["details"]["RM-002"]["Nguồn"] == "docs/brd/01-nhom-a/01-man-danh-sach.md"


def test_check_ids_khop_hai_chieu_thi_khong_loi():
    assert check_ids(parse_roadmap(ROADMAP_OK)) == []


def test_check_ids_bat_id_trung():
    text = ROADMAP_OK.replace("| RM-002 | Màn danh sách", "| RM-001 | Màn danh sách")
    errs = check_ids(parse_roadmap(text))
    assert any("trùng" in e for e in errs)


def test_check_ids_bat_item_thieu_khoi_chi_tiet():
    text = ROADMAP_OK.replace("### RM-002 — Màn danh sách (hop-dong, Wave 1)",
                              "### RM-009 — Màn danh sách (hop-dong, Wave 1)")
    errs = check_ids(parse_roadmap(text))
    assert any("RM-002" in e and "khối chi tiết" in e for e in errs)
    assert any("RM-009" in e and "bảng tổng" in e for e in errs)


def test_check_placeholders_sach_thi_khong_loi():
    assert check_placeholders(ROADMAP_OK) == []


def test_check_placeholders_bat_date_va_ngoac_vuong():
    text = ROADMAP_OK.replace("2026-08-07", "[DATE]").replace("auth | 0", "[module] | 0")
    errs = check_placeholders(text)
    assert any("[DATE]" in e for e in errs)
    assert any("[module]" in e for e in errs)


def test_check_placeholders_khong_bat_link_markdown():
    assert check_placeholders("xem [tài liệu](docs/a.md)\n") == []


def test_check_placeholders_khong_bat_checkbox_task_list():
    text = ROADMAP_OK.replace("  - (trống)", "  - [ ] dời sang RM-005")
    assert check_placeholders(text) == []


def test_check_placeholders_checkbox_kem_placeholder_that_van_bi_bat():
    text = ROADMAP_OK.replace("  - (trống)", "  - [ ] chuyển sang [module]")
    errs = check_placeholders(text)
    assert any("[module]" in e for e in errs)


def test_check_placeholders_dung_so_dong_that_sau_khoi_code():
    text = ROADMAP_OK + "\n```\nkhông phải placeholder [x]\n```\n\n[DATE]\n"
    errs = check_placeholders(text)
    target_line = text.split("\n").index("[DATE]") + 1
    assert any(e.startswith(f"Dòng {target_line}:") for e in errs)


def _cover(brd, roadmap_text, excluded=()):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    return check_coverage(parse_roadmap(roadmap_text), nodes, brd,
                          "docs/brd", list(excluded))


ROADMAP_PHU = """## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
| RM-001 | Nhóm A | nhom-a | 0 | N/A | chưa |
| RM-002 | Màn danh sách | hop-dong | 1 | RM-001 | chưa |

## Chi tiết

### RM-001 — Nhóm A (nhom-a, Wave 0)

- **Nguồn**: docs/brd/01-nhom-a/

### RM-002 — Màn danh sách (hop-dong, Wave 1)

- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md
"""


def test_slugify_anchor_giu_dau_tieng_viet():
    assert slugify_anchor("Bộ lọc") == "bộ-lọc"
    assert slugify_anchor("Quy tắc & điều kiện") == "quy-tắc-điều-kiện"


def test_norm_source_cat_tien_to_thu_muc_brd_va_anchor():
    assert norm_source("docs/brd/01-a/02-b.md#Bộ lọc", "docs/brd") == ("01-a/02-b.md", "Bộ lọc")
    assert norm_source("01-a/02-b.md", "docs/brd") == ("01-a/02-b.md", None)
    assert norm_source("`docs/brd/01-a/`", "docs/brd") == ("01-a/", None)
    assert norm_source("[xem](docs/brd/01-a/02-b.md)", "docs/brd") == ("01-a/02-b.md", None)


def test_norm_source_ngoai_cay_brd_thi_tra_none():
    assert norm_source("src/app/login.ts", "docs/brd") == (None, None)
    assert norm_source("N/A", "docs/brd") == (None, None)


def test_check_coverage_thieu_node_thi_loi(brd):
    errs, _ = _cover(brd, ROADMAP_PHU)
    assert any("BRD-0003" in e and "Thuật ngữ" in e for e in errs)
    assert not any("BRD-0002" in e for e in errs)
    assert not any("BRD-0000" in e for e in errs)      # node gốc không tính phủ


def test_check_coverage_node_bi_loai_co_ly_do_thi_qua(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển, không phải màn"}])
    assert errs == []


def test_check_coverage_ly_do_rong_thi_loi(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "   "}])
    assert any("BRD-0003" in e and "lý do" in e for e in errs)


def test_check_coverage_node_id_loai_khong_co_that_thi_loi(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"},
                      {"node_id": "BRD-9999", "title": "Ma", "reason": "ok"}])
    assert any("BRD-9999" in e for e in errs)


def test_check_coverage_nguon_tro_file_khong_ton_tai(brd):
    text = ROADMAP_PHU.replace("01-man-danh-sach.md", "99-khong-co.md")
    errs, _ = _cover(brd, text)
    assert any("99-khong-co.md" in e for e in errs)


def test_check_coverage_anchor_khop_text_hoac_slug(brd):
    ok_text = ROADMAP_PHU.replace("01-man-danh-sach.md\n", "01-man-danh-sach.md#Bộ lọc\n")
    errs, _ = _cover(brd, ok_text,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert errs == []
    slug_text = ROADMAP_PHU.replace("01-man-danh-sach.md\n", "01-man-danh-sach.md#bộ-lọc\n")
    errs, _ = _cover(brd, slug_text,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert errs == []


def test_check_coverage_anchor_khong_co_thi_loi(brd):
    text = ROADMAP_PHU.replace("01-man-danh-sach.md\n", "01-man-danh-sach.md#Không có mục này\n")
    errs, _ = _cover(brd, text)
    assert any("Không có mục này" in e for e in errs)


def test_check_coverage_item_khong_co_nguon_thi_canh_bao(brd):
    text = ROADMAP_PHU.replace("- **Nguồn**: docs/brd/01-nhom-a/\n", "")
    _, warns = _cover(brd, text, [{"node_id": "BRD-0001", "title": "Nhóm A", "reason": "ok"},
                                  {"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert any("RM-001" in w and "Nguồn" in w for w in warns)


def test_check_coverage_node_lon_map_mot_item_thi_canh_bao(brd):
    manifest = (brd / "brd.manifest.yml").read_text(encoding="utf-8")
    (brd / "brd.manifest.yml").write_text(manifest.replace("chars: 320", "chars: 50000"),
                                          encoding="utf-8")
    _, warns = _cover(brd, ROADMAP_PHU, [{"node_id": "BRD-0003", "title": "T", "reason": "ok"}])
    assert any("BRD-0002" in w and "tách" in w for w in warns)
