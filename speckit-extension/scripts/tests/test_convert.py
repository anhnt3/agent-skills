import subprocess
from pathlib import Path

import pytest

from brd.convert import ConvertError, build_reference_docx, check_pandoc, run_pandoc


def test_check_pandoc_tra_ve_version(require_pandoc):
    assert check_pandoc().startswith("3.")


def test_run_pandoc_sinh_md_va_tach_anh(real_brd, tmp_path):
    md_path = run_pandoc(real_brd, tmp_path)
    assert md_path == tmp_path / "brd.md"
    text = md_path.read_text(encoding="utf-8")
    # Hợp đồng MỚI: dùng -t gfm để người đọc xem được bản xem trước markdown.
    assert "+---" not in text, "gfm không được sinh grid table của -t markdown"
    assert text.count("<table>") == 270, "bảng ra dạng HTML thô — VSCode/GitHub dựng được"
    assert text.count('src="./media/media/') == 387
    assert text.count("](./media/media/") == 0
    assert len(list((tmp_path / "media" / "media").iterdir())) == 386
    # Cây heading của gfm phải giống hệt bản -t markdown cũ.
    from brd.outline import parse_headings
    assert len(parse_headings(text)) == 604


def test_build_reference_docx_nho_va_pandoc_chap_nhan(real_brd, tmp_path):
    ref = build_reference_docx(real_brd, tmp_path / "reference.docx")
    assert ref.stat().st_size < 1_000_000, "phải bỏ word/media/ nên chỉ còn vài chục KB"
    src = tmp_path / "h.md"
    src.write_text("# H1\n\ntext\n\n## H2\n\ntext2\n", encoding="utf-8")
    out = tmp_path / "h.docx"
    subprocess.run(
        ["pandoc", str(src), f"--reference-doc={ref}", "-o", str(out)],
        check=True, capture_output=True,
    )
    import re
    import zipfile
    xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf-8")
    styles = re.findall(r'w:pStyle w:val="(Heading\d)"', xml)
    assert styles == ["Heading1", "Heading2"]


def test_run_pandoc_bao_loi_ro_khi_file_khong_ton_tai(require_pandoc, tmp_path):
    with pytest.raises(ConvertError):
        run_pandoc(tmp_path / "khong-co.docx", tmp_path)
