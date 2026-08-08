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
from brd_roadmap import check_deps
from brd_roadmap import build_manifest, scan_tree
from brd_roadmap import resolve_link, resolve_link_suggestion

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


def test_cli_outline_mac_dinh_khong_quiet_ghi_file_va_in_du_json(brd, tmp_path):
    """Mặc định (không có --quiet): ghi đủ file --out, và stdout vẫn là JSON đầy đủ."""
    dest = tmp_path / "out" / "outline.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(brd), "--out", str(dest)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    assert dest.is_file()
    stdout_json = json.loads(proc.stdout)
    assert stdout_json["node_count"] == 4
    assert "nodes" in stdout_json and len(stdout_json["nodes"]) == 4


def test_cli_outline_quiet_in_tom_tat_khong_phai_json_day_du(brd, tmp_path):
    """Có --quiet: stdout chỉ là dòng tóm tắt ngắn, KHÔNG parse được thành outline JSON
    đầy đủ, nhưng --out vẫn ghi đầy đủ JSON như bình thường."""
    dest = tmp_path / "out" / "outline.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(brd), "--out", str(dest), "--quiet"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    assert dest.is_file()
    full = json.loads(dest.read_text(encoding="utf-8"))
    assert full["node_count"] == 4
    assert len(full["nodes"]) == 4

    stdout = proc.stdout.strip()
    assert stdout, "stdout không được rỗng"
    try:
        parsed = json.loads(stdout)
        is_full_outline = isinstance(parsed, dict) and "nodes" in parsed
    except json.JSONDecodeError:
        is_full_outline = False
    assert not is_full_outline, "stdout ở chế độ --quiet không được là outline JSON đầy đủ"
    assert "4" in stdout
    assert str(dest) in stdout or dest.name in stdout


def test_cli_outline_thu_muc_khong_co_manifest_thi_chet(tmp_path):
    (tmp_path / "trong").mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(tmp_path / "trong")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert "brd.manifest.yml" in proc.stderr


def test_cli_outline_node_hong_thieu_truong_thi_exit_2_khong_traceback(brd):
    """Dòng node bị sửa tay hỏng (thiếu `chars`) -> exit 2 một dòng stderr, không traceback."""
    manifest = (brd / "brd.manifest.yml").read_text(encoding="utf-8")
    broken = manifest.replace(
        '{ id: BRD-0003, order: 3, depth: 2, word_level: 3, kind: leaf, '
        'title: "Thuật ngữ", path: "01-nhom-a/02-thuat-ngu.md", parent: BRD-0001, chars: 40 }',
        '{ id: BRD-0003, order: 3, depth: 2, word_level: 3, kind: leaf, '
        'title: "Thuật ngữ", path: "01-nhom-a/02-thuat-ngu.md", parent: BRD-0001 }',
    )
    assert broken != manifest
    (brd / "brd.manifest.yml").write_text(broken, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(brd)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    lines = [l for l in proc.stderr.splitlines() if l.strip()]
    assert len(lines) == 1
    assert "BRD-0003" in lines[0]


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


def _cover(brd, roadmap_text, excluded=(), brd_rel="docs/brd"):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    errs, warns, _ = check_coverage(parse_roadmap(roadmap_text), nodes, brd,
                                    brd_rel, list(excluded))
    return errs, warns


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


def test_check_coverage_tat_ca_da_phu_khong_loai_thi_sach(brd):
    """Happy path thật: roadmap phủ hết node non-root, không cần decisions.json."""
    text = ROADMAP_PHU + "\n### RM-003 — Thuật ngữ (nhom-a, Wave 0)\n\n" \
                          "- **Nguồn**: docs/brd/01-nhom-a/02-thuat-ngu.md\n"
    text = text.replace(
        "| RM-002 | Màn danh sách | hop-dong | 1 | RM-001 | chưa |\n",
        "| RM-002 | Màn danh sách | hop-dong | 1 | RM-001 | chưa |\n"
        "| RM-003 | Thuật ngữ | nhom-a | 0 | N/A | chưa |\n",
    )
    assert _cover(brd, text) == ([], [])


def test_check_coverage_nguon_khong_tro_vao_cay_brd_thi_canh_bao(brd):
    """Nguồn nhìn giống đường dẫn nhưng không có tiền tố `docs/brd/`, không đuôi `.md`/`/`
    (vd BA gõ tắt tên thư mục, thiếu cả tiền tố lẫn dấu `/` cuối) -> cảnh báo, không im lặng."""
    text = ROADMAP_PHU.replace("- **Nguồn**: docs/brd/01-nhom-a/\n",
                               "- **Nguồn**: 01-nhom-a\n")
    _, warns = _cover(brd, text, [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert any("RM-001" in w and "01-nhom-a" in w for w in warns)


def test_check_coverage_nguon_na_thi_im_lang(brd):
    """`N/A` (mọi cách viết hoa) là giá trị hợp lệ cố ý ngoài cây BRD — không cảnh báo."""
    text = ROADMAP_PHU.replace("- **Nguồn**: docs/brd/01-nhom-a/\n", "- **Nguồn**: n/a\n")
    _, warns = _cover(brd, text, [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert not any("RM-001" in w for w in warns)


def test_check_coverage_nguon_na_co_backtick_thi_im_lang(brd):
    """`` `N/A` `` (backtick, đúng quy ước ô nhập của template) vẫn được xem là N/A hợp lệ."""
    text = ROADMAP_PHU.replace("- **Nguồn**: docs/brd/01-nhom-a/\n", "- **Nguồn**: `N/A`\n")
    _, warns = _cover(brd, text, [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert not any("RM-001" in w for w in warns)


def test_check_coverage_excluded_node_id_khong_phai_chuoi_thi_loi_khong_crash(brd):
    """`node_id` là số/list thay vì chuỗi -> lỗi tiếng Việt, không AttributeError."""
    errs, _ = _cover(brd, ROADMAP_PHU, [{"node_id": 123, "title": "x", "reason": "ok"}])
    assert any("node_id" in e and "123" in e for e in errs)


def test_check_coverage_excluded_reason_khong_phai_chuoi_thi_loi_khong_crash(brd):
    """`reason` là list thay vì chuỗi -> lỗi tiếng Việt, không AttributeError."""
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": ["x"]}])
    assert any("reason" in e for e in errs)


def test_check_coverage_hai_node_inline_chung_dir_deu_duoc_phu(brd):
    """Hai node inline cùng chia sẻ một `dir:` — một item trỏ vào dir đó phải phủ cả hai."""
    manifest = (brd / "brd.manifest.yml").read_text(encoding="utf-8")
    extra_node = ('\n  - { id: BRD-0004, order: 4, depth: 1, word_level: 1, kind: folder, '
                  'title: "Nhóm A phụ", inline: true, dir: "01-nhom-a/", parent: null, chars: 5 }')
    (brd / "brd.manifest.yml").write_text(manifest.rstrip("\n") + extra_node + "\n",
                                          encoding="utf-8")
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert not any("BRD-0001" in e for e in errs)
    assert not any("BRD-0004" in e for e in errs)


def test_check_coverage_anchor_gfm_hai_gach_lien_tiep_van_khop(brd):
    """Anchor GFM thật (nhiều khoảng trắng -> nhiều gạch liên tiếp) vẫn phải khớp."""
    text = ROADMAP_PHU.replace("01-man-danh-sach.md\n",
                               "01-man-danh-sach.md#quy-tắc--điều-kiện\n")
    man_md = (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    man_md = man_md.replace("## Quy tắc\n", "## Quy tắc  điều kiện\n")
    (brd / "01-nhom-a" / "01-man-danh-sach.md").write_text(man_md, encoding="utf-8")
    errs, _ = _cover(brd, text, [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert not any("anchor" in e for e in errs)


def test_check_coverage_excluded_phan_tu_khong_phai_dict_thi_loi_khong_crash(brd):
    """`decisions.json` có phần tử không phải object (vd chuỗi thô) -> báo lỗi, không crash."""
    errs, _ = _cover(brd, ROADMAP_PHU, ["BRD-0003"])
    assert any("BRD-0003" in e for e in errs)
    assert any("node_id" in e for e in errs)


def test_check_coverage_nguon_tro_vao_node_goc_thi_loi_ro_nguyen_nhan(brd):
    """**Nguồn** trỏ đúng vị trí node gốc (`_index.md`, phần đầu tài liệu) -> vẫn là lỗi
    (node gốc không tính coverage), nhưng thông điệp phải giải thích rõ, không phải
    thông điệp chung chung "không có node BRD nào ở vị trí đó" dễ gây hiểu lầm."""
    text = ROADMAP_PHU.replace("- **Nguồn**: docs/brd/01-nhom-a/\n",
                               "- **Nguồn**: docs/brd/_index.md\n")
    errs, _ = _cover(brd, text, [{"node_id": "BRD-0001", "title": "Nhóm A", "reason": "ok"},
                                 {"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert any("RM-001" in e and "gốc" in e for e in errs)


def test_norm_source_brd_rel_co_tien_to_cham_gach_cheo_van_khop():
    """`--brd-rel "./docs/brd"` (plausible: agent truyền nguyên tham số người dùng gõ) không
    được làm gãy so khớp tiền tố với `Nguồn` viết `docs/brd/...` (không có `./`)."""
    assert norm_source("docs/brd/01-a/02-b.md", "./docs/brd") == ("01-a/02-b.md", None)


def test_check_coverage_brd_rel_co_tien_to_cham_gach_cheo_van_phu(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}],
                     brd_rel="./docs/brd")
    assert errs == []


def test_check_coverage_excluded_thieu_node_id_thi_loi_ro_rang(brd):
    """`decisions.json` có object nhưng thiếu `node_id` -> lỗi rõ ràng, không để trống rỗng."""
    errs, _ = _cover(brd, ROADMAP_PHU, [{"title": "Thuật ngữ", "reason": "ok"}])
    assert any("node_id" in e and "loại node  không có trong manifest" not in e for e in errs)


DEPS_HEAD = """## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
"""

DEPS_TAIL = """
## Chi tiết

### RM-001 — A (m, Wave 0)

- **Nguồn**: docs/brd/01-nhom-a/

### RM-002 — B (m, Wave 1)

- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md
"""


def _deps(rows):
    return check_deps(parse_roadmap(DEPS_HEAD + rows + DEPS_TAIL))


def test_check_deps_hop_le_thi_khong_loi():
    assert _deps("| RM-001 | A | m | 0 | N/A | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n") == []


def test_check_deps_bat_id_khong_ton_tai():
    errs = _deps("| RM-001 | A | m | 0 | RM-777 | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n")
    assert any("RM-777" in e for e in errs)


def test_check_deps_bat_chu_trinh():
    errs = _deps("| RM-001 | A | m | 0 | RM-002 | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n")
    assert any("chu trình" in e for e in errs)


def test_check_deps_bat_wave_nghich():
    errs = _deps("| RM-001 | A | m | 0 | RM-002 | chưa |\n"
                 "| RM-002 | B | m | 1 | N/A | chưa |\n")
    assert any("Wave" in e and "RM-001" in e for e in errs)


def test_check_deps_bat_wave_khong_phai_so():
    errs = _deps("| RM-001 | A | m | sau | N/A | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n")
    assert any("Wave" in e and "số" in e for e in errs)


def _run_verify(brd, roadmap_text, tmp_path, excluded=()):
    rm = tmp_path / "roadmap.md"
    rm.write_text(roadmap_text, encoding="utf-8")
    dec = tmp_path / "decisions.json"
    dec.write_text(json.dumps({"brd_dir": "docs/brd", "excluded": list(excluded)},
                              ensure_ascii=False), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm),
         "--brd", str(brd), "--brd-rel", "docs/brd", "--decisions", str(dec)],
        capture_output=True, text=True, encoding="utf-8",
    )


def test_cli_verify_happy_path_exit_0(brd, tmp_path):
    proc = _run_verify(brd, ROADMAP_PHU, tmp_path,
                       [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển"}])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    rep = json.loads(proc.stdout)
    assert rep["ok"] is True
    assert rep["errors"] == []
    assert rep["items"] == 2


def test_cli_verify_thieu_phu_thi_exit_1(brd, tmp_path):
    proc = _run_verify(brd, ROADMAP_PHU, tmp_path)
    assert proc.returncode == 1
    rep = json.loads(proc.stdout)
    assert rep["ok"] is False
    assert any("BRD-0003" in e for e in rep["errors"])


def test_cli_verify_thieu_decisions_van_chay_va_canh_bao(brd, tmp_path):
    rm = tmp_path / "roadmap.md"
    rm.write_text(ROADMAP_PHU, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm), "--brd", str(brd),
         "--brd-rel", "docs/brd", "--decisions", str(tmp_path / "khong-co.json")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 1
    rep = json.loads(proc.stdout)
    assert any("decisions" in w for w in rep["warnings"])


def test_check_deps_tu_tro_thi_bao_chu_trinh():
    """Một item phụ thuộc chính nó là chu trình độ dài 1 — không được lọt qua sạch."""
    errs = _deps("| RM-001 | A | m | 0 | RM-001 | chưa |\n"
                 "| RM-002 | B | m | 1 | N/A | chưa |\n")
    assert any("chu trình" in e and "RM-001" in e for e in errs)


def test_check_deps_id_dai_hon_khong_bi_nham_thanh_id_ngan_hon():
    """`RM-0012` không được đọc nhầm thành `RM-001` — phải báo là ID không tồn tại."""
    errs = _deps("| RM-001 | A | m | 0 | N/A | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-0012 | chưa |\n")
    assert any("RM-0012" in e and "không có item nào mang ID đó" in e for e in errs)


def test_check_deps_chuoi_phu_thuoc_dai_khong_tran_ngan_xep():
    """Chuỗi phụ thuộc dài phải qua bằng DFS lặp, không đệ quy — không được raise RecursionError.

    `ROW_RE` (parse dòng bảng tổng) chỉ chấp nhận ID đúng 3 chữ số (`RM-\\d{3}`),
    nên dựng qua văn bản roadmap thật tối đa được ~1000 dòng — không chắc vượt
    giới hạn đệ quy mặc định của CPython (1000, đã có sẵn margin từ các stack
    frame khác của pytest/subprocess). Ở đây dựng thẳng cấu trúc `parsed` (bỏ
    qua `parse_roadmap`/`ROW_RE`, vốn không phải thứ `check_deps` phụ thuộc —
    hàm chỉ cần dict có khóa "rows"/"row_order") với ID 4 chữ số để có chuỗi
    2000 mắt xích, đủ sâu để bản đệ quy cũ (mỗi bước một lời gọi hàm `walk`)
    chắc chắn tràn ngăn xếp; DFS lặp của bản sửa thì không.
    """
    n = 2000
    rows, row_order = {}, []
    for i in range(1, n + 1):
        rid = f"RM-{i:04d}"
        dep = f"RM-{i - 1:04d}" if i > 1 else "N/A"
        rows[rid] = {"man": "X", "module": "m", "wave": "0", "deps_raw": dep,
                     "trang_thai": "chưa"}
        row_order.append(rid)
    parsed = {"rows": rows, "row_order": row_order, "details": {}, "detail_order": []}
    errs = check_deps(parsed)
    assert errs == []


def test_check_deps_chu_trinh_chi_thay_duoc_tu_root_sau():
    """Chu trình nằm ngoài hẳn nhánh của root đầu tiên vẫn phải bị bắt khi vòng ngoài
    khởi động DFS ở root sau — RM-001 cô lập, chu trình thật ở RM-002 <-> RM-003."""
    errs = _deps("| RM-001 | A | m | 0 | N/A | chưa |\n"
                 "| RM-002 | B | m | 0 | RM-003 | chưa |\n"
                 "| RM-003 | C | m | 0 | RM-002 | chưa |\n")
    assert any("chu trình" in e and "RM-002" in e and "RM-003" in e for e in errs)


def test_check_deps_hinh_thoi_khong_bi_bao_chu_trinh_gia():
    """Đồ thị hình thoi (A phụ thuộc B và C, cả hai cùng phụ thuộc D) — D bị hai
    đường khác nhau chạm tới nhưng không phải chu trình, không được báo giả."""
    errs = _deps("| RM-001 | A | m | 2 | RM-002,RM-003 | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-004 | chưa |\n"
                 "| RM-003 | C | m | 1 | RM-004 | chưa |\n"
                 "| RM-004 | D | m | 0 | N/A | chưa |\n")
    assert not any("chu trình" in e for e in errs)


def test_cli_verify_decisions_json_la_mang_thi_exit_2_stderr_mot_dong(brd, tmp_path):
    """`decisions.json` cấp cao nhất là mảng JSON (sai định dạng) -> exit 2, không phải exit 1."""
    rm = tmp_path / "roadmap.md"
    rm.write_text(ROADMAP_PHU, encoding="utf-8")
    dec = tmp_path / "decisions.json"
    dec.write_text(json.dumps(["BRD-0003"], ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm), "--brd", str(brd),
         "--brd-rel", "docs/brd", "--decisions", str(dec)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert proc.stdout == ""
    lines = [l for l in proc.stderr.splitlines() if l.strip()]
    assert len(lines) == 1


def test_cli_verify_roadmap_khong_phai_utf8_thi_exit_2(brd, tmp_path):
    """Roadmap không phải UTF-8 -> lỗi vận hành, exit 2 với một dòng stderr, không exit 1."""
    rm = tmp_path / "roadmap.md"
    rm.write_bytes("## Bảng tổng\n".encode("utf-16"))
    dec = tmp_path / "decisions.json"
    dec.write_text(json.dumps({"excluded": []}, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm), "--brd", str(brd),
         "--brd-rel", "docs/brd", "--decisions", str(dec)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert proc.stdout == ""
    lines = [l for l in proc.stderr.splitlines() if l.strip()]
    assert len(lines) == 1


def test_cli_verify_manifest_khong_phai_utf8_thi_exit_2(tmp_path):
    """`brd.manifest.yml` không phải UTF-8 -> lỗi vận hành, exit 2, không exit 1 stdout rỗng.

    `parse_manifest` được gọi từ `cmd_verify` (và `cmd_outline`) — đọc file này
    phải qua cùng hàng rào `_die` như roadmap/decisions.json, không được để
    `UnicodeDecodeError` lọt ra ngoài không kiểm soát.
    """
    brd_dir = tmp_path / "brd"
    brd_dir.mkdir()
    (brd_dir / "brd.manifest.yml").write_bytes("nodes:\n".encode("utf-16"))
    rm = tmp_path / "roadmap.md"
    rm.write_text(ROADMAP_PHU, encoding="utf-8")
    dec = tmp_path / "decisions.json"
    dec.write_text(json.dumps({"excluded": []}, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm), "--brd", str(brd_dir),
         "--brd-rel", "docs/brd", "--decisions", str(dec)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert proc.stdout == ""
    lines = [l for l in proc.stderr.splitlines() if l.strip()]
    assert len(lines) == 1


# ------------------------------------------------------------ lệnh manifest --

def _handmade(tmp_path):
    """Cây BRD BA viết tay: không manifest, thư mục thuần gom nhóm, có file index gốc."""
    brd = tmp_path / "brd"
    (brd / "01-nhom-a").mkdir(parents=True)
    (brd / "media").mkdir()
    (brd / "_index.md").write_text("# Tài liệu BRD\n\nGiới thiệu.\n", encoding="utf-8")
    (brd / "01-nhom-a" / "01-man-danh-sach.md").write_text(
        "# Màn danh sách\n\nNội dung.\n", encoding="utf-8")
    (brd / "01-nhom-a" / "02-thuat-ngu.md").write_text(
        "Không có heading nào ở đây.\n", encoding="utf-8")
    (brd / "media" / "note.md").write_text("# Bỏ qua\n", encoding="utf-8")
    return brd


def test_manifest_cay_tay_moi_file_mot_node_thu_muc_khong_thanh_node(tmp_path):
    """Mô hình B: mỗi file .md = đúng một node; thư mục chỉ là đường dẫn.

    Thư mục thành node thì mọi thư mục gom nhóm đều phải bị khai loại kèm lý do
    trong decisions.json — đẻ ra hàng chục mục loại trừ giả.
    """
    brd = _handmade(tmp_path)
    lines, report = build_manifest(brd, brd / "brd.manifest.yml")
    assert report["total"] == 3          # _index + 2 file, KHÔNG có node cho 01-nhom-a/
    assert len(report["added"]) == 3
    assert report["kept"] == 0
    locs = [n["loc"] for n in report["nodes"]]
    assert "01-nhom-a" not in locs and "01-nhom-a/" not in locs
    assert "media/note.md" not in locs   # media/ bị loại khỏi lượt duyệt
    assert all(l.startswith("  - { ") for l in lines)


def test_manifest_title_uu_tien_frontmatter_roi_heading_roi_ten_file(tmp_path):
    brd = _handmade(tmp_path)
    (brd / "01-nhom-a" / "03-co-fm.md").write_text(
        '---\ntitle: "Tên từ frontmatter"\n---\n\n# Heading khác\n', encoding="utf-8")
    _, report = build_manifest(brd, brd / "brd.manifest.yml")
    by_loc = {n["loc"]: n["title"] for n in report["nodes"]}
    assert by_loc["01-nhom-a/03-co-fm.md"] == "Tên từ frontmatter"
    assert by_loc["01-nhom-a/01-man-danh-sach.md"] == "Màn danh sách"   # H1
    assert by_loc["01-nhom-a/02-thuat-ngu.md"] == "Thuat ngu"           # de-slug tên file


def test_manifest_parent_theo_file_index_va_node_goc(tmp_path):
    brd = _handmade(tmp_path)
    (brd / "01-nhom-a" / "_index.md").write_text("# Nhóm A\n", encoding="utf-8")
    lines, _ = build_manifest(brd, brd / "brd.manifest.yml")
    (brd / "brd.manifest.yml").write_text("nodes:\n" + "\n".join(lines) + "\n",
                                          encoding="utf-8")
    nodes = parse_manifest(brd / "brd.manifest.yml")
    by_path = {n["path"]: n for n in nodes}
    root = by_path["_index.md"]
    assert root["kind"] == "root" and root["parent"] is None
    nhom_a = by_path["01-nhom-a/_index.md"]
    assert nhom_a["parent"] == root["id"]           # index thư mục con -> cha là root
    assert by_path["01-nhom-a/01-man-danh-sach.md"]["parent"] == nhom_a["id"]


def test_manifest_ghi_file_chi_khi_write(tmp_path):
    """Dry-run là mặc định: manifest là nền của mọi thứ phía sau, không ghi trước khi user duyệt."""
    brd = _handmade(tmp_path)
    out = brd / "brd.manifest.yml"
    proc = subprocess.run([sys.executable, str(SCRIPT), "manifest", str(brd)],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["written"] is None
    assert not out.exists()

    proc = subprocess.run([sys.executable, str(SCRIPT), "manifest", str(brd), "--write"],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["written"]
    assert out.is_file()
    assert len(parse_manifest(out)) == 3


def test_manifest_merge_giu_id_cu_them_id_moi_go_node_mat_file(tmp_path):
    """Hoà giải: id ổn định, vì decisions.json và trường Nguồn của roadmap trỏ theo id/path."""
    brd = _handmade(tmp_path)
    out = brd / "brd.manifest.yml"
    lines, _ = build_manifest(brd, out)
    out.write_text("nodes:\n" + "\n".join(lines) + "\n", encoding="utf-8")
    truoc = {n["path"]: n["id"] for n in parse_manifest(out)}

    (brd / "01-nhom-a" / "02-thuat-ngu.md").unlink()
    (brd / "01-nhom-a" / "03-man-moi.md").write_text("# Màn mới\n", encoding="utf-8")

    lines, report = build_manifest(brd, out)
    out.write_text("nodes:\n" + "\n".join(lines) + "\n", encoding="utf-8")
    sau = {n["path"]: n["id"] for n in parse_manifest(out)}

    assert sau["01-nhom-a/01-man-danh-sach.md"] == truoc["01-nhom-a/01-man-danh-sach.md"]
    assert sau["_index.md"] == truoc["_index.md"]
    assert report["added"] == ["01-nhom-a/03-man-moi.md"]
    assert [r["path"] for r in report["removed"]] == ["01-nhom-a/02-thuat-ngu.md"]
    # KHÔNG tái dùng id của node đã gỡ: id mới phải khác mọi id cũ.
    assert sau["01-nhom-a/03-man-moi.md"] not in truoc.values()


def test_manifest_idempotent_tren_cay_import_giu_nguyen_thu_tu(tmp_path, brd):
    """Chạy trên cây do brd-import sinh: không được xáo id/thứ tự, không mất node thư mục."""
    out = brd / "brd.manifest.yml"
    truoc = parse_manifest(out)
    lines, report = build_manifest(brd, out)
    out.write_text("nodes:\n" + "\n".join(lines) + "\n", encoding="utf-8")
    sau = parse_manifest(out)
    assert [n["id"] for n in truoc] == [n["id"] for n in sau]
    assert [n["title"] for n in truoc] == [n["title"] for n in sau]
    assert report["added"] == [] and report["removed"] == []
    assert any(n["inline"] for n in sau)          # node thư mục của bản import còn nguyên


def test_manifest_thu_muc_khong_co_md_thi_exit_2(tmp_path):
    brd = tmp_path / "rong"
    brd.mkdir()
    proc = subprocess.run([sys.executable, str(SCRIPT), "manifest", str(brd)],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 2
    assert proc.stdout == ""


def test_check_coverage_canh_bao_file_nhieu_heading_chi_mot_item(tmp_path, brd):
    """File nhiều mục cấp 2 mà chỉ 1 item -> mô hình phủ theo vị trí vẫn xanh, phải cảnh báo.

    Đây là chỗ "một file = một node" mất màn im lặng: item duy nhất phủ cả node,
    gate không có cách nào biết bên trong file có 12 màn.
    """
    f = brd / "01-nhom-a" / "01-man-danh-sach.md"
    f.write_text(f.read_text(encoding="utf-8")
                 + "\n" + "\n".join(f"## Màn {i}\n\nNội dung.\n" for i in range(6)),
                 encoding="utf-8")
    _, warns = _cover(brd, ROADMAP_PHU,
                      [{"node_id": "BRD-0001", "title": "Nhóm A", "reason": "gom nhóm"},
                       {"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển"}])
    assert any("mục cấp 2" in w and "BRD-0002" in w for w in warns)


# ------------------------------------------------- ô ID là link tới nguồn --

def test_parse_roadmap_o_id_dang_link_van_doc_duoc_hang():
    """Khuôn mới để ô ID là link. Regex hàng phải nhận cả link lẫn text trần."""
    text = ROADMAP_PHU.replace("| RM-001 |", "| [RM-001](docs/brd/01-nhom-a/01-man-danh-sach.md) |")
    parsed = parse_roadmap(text)
    goc = parse_roadmap(ROADMAP_PHU)["rows"]["RM-001"]
    assert "RM-001" in parsed["rows"]
    row = parsed["rows"]["RM-001"]
    assert row["id_link"] == "docs/brd/01-nhom-a/01-man-danh-sach.md"
    assert row["wave"] == goc["wave"]
    assert row["deps_raw"] == goc["deps_raw"]
    assert row["trang_thai"] == goc["trang_thai"]


def test_cli_verify_canh_bao_khi_link_o_id_lech_nguon(tmp_path, brd):
    """Link ô ID trỏ khác **Nguồn** -> bấm vào rơi sai chỗ mà gate phủ vẫn xanh."""
    text = ROADMAP_PHU.replace("| RM-001 |", "| [RM-001](docs/brd/01-nhom-a/02-thuat-ngu.md) |")
    rm = tmp_path / "roadmap.md"
    rm.write_text(text, encoding="utf-8")
    dec = tmp_path / "decisions.json"
    dec.write_text(json.dumps({"excluded": [
        {"node_id": "BRD-0001", "title": "Nhóm A", "reason": "gom nhóm"},
        {"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển"}]},
        ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm), "--brd", str(brd),
         "--brd-rel", "docs/brd", "--decisions", str(dec)],
        capture_output=True, text=True, encoding="utf-8",
    )
    report = json.loads(proc.stdout)
    assert any("RM-001" in w and "ô ID" in w for w in report["warnings"])


def test_check_placeholders_bo_qua_o_id_dang_link():
    """`[RM-001](…)` là link markdown, không phải placeholder chưa điền."""
    assert check_placeholders("| [RM-001](docs/brd/a.md#x) | Màn | m | 0 | N/A | chưa |") == []


def test_resolve_link_quy_ve_goc_repo_theo_cho_roadmap_dung():
    """Link markdown resolve theo thư mục chứa file, `**Nguồn**` viết theo gốc repo.

    Roadmap ở `docs/roadmap.md` thì link bấm được là `brd/x.md`; copy nguyên
    `docs/brd/x.md` vào link sẽ ra `docs/docs/brd/x.md` -> 404.
    """
    assert resolve_link("brd/x.md", "docs/roadmap.md") == "docs/brd/x.md"
    assert resolve_link("docs/brd/x.md", "docs/roadmap.md") == "docs/docs/brd/x.md"
    assert resolve_link("brd/x.md#muc", "docs/roadmap.md") == "docs/brd/x.md#muc"
    assert resolve_link("brd/thu-muc/", "docs/roadmap.md") == "docs/brd/thu-muc/"
    assert resolve_link("../src/app/", "docs/roadmap.md") == "src/app/"
    assert resolve_link("brd/x.md", "roadmap.md") == "brd/x.md"      # roadmap ở gốc repo
    assert resolve_link("https://x/y", "docs/roadmap.md") == "https://x/y"


def test_resolve_link_suggestion_la_nghich_dao():
    assert resolve_link_suggestion("docs/brd/x.md", "docs/roadmap.md") == "brd/x.md"
    assert resolve_link_suggestion("docs/brd/x.md", "roadmap.md") == "docs/brd/x.md"


def test_cli_verify_link_o_id_dung_he_quy_chieu_thi_khong_canh_bao(tmp_path, brd):
    """Gate KHÔNG được ép dạng link 404: `brd/…` (đúng) phải sạch, `docs/brd/…` mới bị bắt."""
    docs = brd.parent
    (tmp_path / "decisions.json").write_text(json.dumps({"excluded": [
        {"node_id": "BRD-0001", "title": "Nhóm A", "reason": "gom nhóm"},
        {"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển"}]},
        ensure_ascii=False), encoding="utf-8")

    def chay(link):
        text = ROADMAP_PHU.replace("| RM-001 |", f"| [RM-001]({link}) |")
        (docs / "roadmap.md").write_text(text, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "verify", "docs/roadmap.md",
             "--brd", str(brd), "--brd-rel", "docs/brd",
             "--decisions", str(tmp_path / "decisions.json")],
            capture_output=True, text=True, encoding="utf-8", cwd=tmp_path,
        )
        return [w for w in json.loads(proc.stdout)["warnings"] if "RM-001" in w and "ô ID" in w]

    # RM-001 có **Nguồn** = docs/brd/01-nhom-a/ (gốc repo) -> link đúng là brd/01-nhom-a/.
    assert chay("brd/01-nhom-a/") == []
    assert len(chay("docs/brd/01-nhom-a/")) == 1


def test_check_coverage_bo_muc_chuan_lap_o_moi_file_khong_bi_coi_la_nhieu_man(tmp_path):
    """8 mục cấp 2 lặp y hệt ở mọi file là KHUÔN tài liệu, không phải 8 màn.

    Đếm heading trần làm mọi file BRD kiểu "Đối tượng tham gia / Điều kiện thực
    hiện / Thiết kế UX/UI…" đều bị cảnh báo -> phần lớn cảnh báo là giả, người
    dùng bỏ qua cả cảnh báo thật.
    """
    root = tmp_path / "docs" / "brd"
    root.mkdir(parents=True)
    man = ['schema_version: "1.0"', "nodes:"]
    for i in range(1, 4):
        man.append(f'  - {{ id: BRD-000{i}, order: {i}, depth: 1, kind: leaf, '
                   f'title: "Màn {i}", path: "man-{i}.md", parent: null, chars: 100 }}')
    nl = chr(10)
    (root / "brd.manifest.yml").write_text(nl.join(man) + nl, encoding="utf-8")

    chuan = nl.join(f"## Mục chuẩn {j}{nl}{nl}Nội dung.{nl}" for j in range(6))
    for i in range(1, 4):
        (root / f"man-{i}.md").write_text(f"# Màn {i}{nl}{nl}{chuan}", encoding="utf-8")

    rows = nl.join(f"| RM-00{i} | Màn {i} | m | 0 | N/A | chưa |" for i in range(1, 4))
    details = nl.join(f"### RM-00{i} — Màn {i} (m, Wave 0){nl}{nl}"
                      f"- **Nguồn**: docs/brd/man-{i}.md{nl}" for i in range(1, 4))
    roadmap = ("| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |" + nl
               + "|--|--|--|--|--|--|" + nl + rows + nl + nl
               + "## Chi tiết" + nl + nl + details)

    _, warns = _cover(root, roadmap)
    assert not any("mục cấp 2" in w for w in warns)

    # Một file có 6 mục RIÊNG (không lặp ở file khác) -> vẫn phải cảnh báo.
    rieng = nl.join(f"## Màn con {j}{nl}{nl}Nội dung.{nl}" for j in range(6))
    (root / "man-2.md").write_text(f"# Màn 2{nl}{nl}{chuan}{nl}{rieng}", encoding="utf-8")
    _, warns = _cover(root, roadmap)
    assert any("mục cấp 2 riêng" in w and "BRD-0002" in w for w in warns)
