import subprocess
import sys
from pathlib import Path

import pytest

from brd.convert import run_pandoc
from brd.docx_probe import detect_tier, numbered_titles, promotions_for, toc_titles
from brd.outline import parse_headings

FIXTURES = Path(__file__).resolve().parent / "fixtures"
LUA = Path(__file__).resolve().parents[1] / "promote_headings.lua"


@pytest.fixture(scope="session", autouse=True)
def build_fixtures():
    subprocess.run([sys.executable, str(FIXTURES / "make_fixtures.py")], check=True)


def test_toc_titles_moi_duoc_muc_luc_cua_brd_that(real_brd):
    titles = toc_titles(real_brd)
    assert len(titles) == 44          # 3 x TOC1 + 6 x TOC3 + 35 x TOC4
    assert titles[0][1] == 1
    # không dính số trang vào đuôi tiêu đề
    assert titles[0][0].startswith("Nhóm chức năng dịch vụ hệ thống")
    assert not titles[0][0][-1].isdigit()


def test_numbered_titles_nhan_day_lien_tuc():
    got = numbered_titles(FIXTURES / "numbered.docx")
    assert got == [
        ("1. Chương một", 1), ("1.1 Mục một một", 2), ("1.2 Mục một hai", 2),
        ("2. Chương hai", 1), ("2.1 Mục hai một", 2),
    ]


def test_detect_tier_docx_danh_so_go_tay_la_bac_4():
    res = detect_tier(FIXTURES / "numbered.docx")
    assert res["tier"] == 4
    assert res["needs_llm"] is False


def test_lua_filter_nang_dung_so_heading(tmp_path):
    docx = FIXTURES / "numbered.docx"
    md_path = run_pandoc(docx, tmp_path, lua_filter=LUA,
                         metadata={"promotions": promotions_for(docx)})
    hs = parse_headings(md_path.read_text(encoding="utf-8"))
    assert [(h["level"], h["title"]) for h in hs] == [
        (1, "1. Chương một"), (2, "1.1 Mục một một"), (2, "1.2 Mục một hai"),
        (1, "2. Chương hai"), (2, "2.1 Mục hai một"),
    ]


def test_lua_filter_nem_loi_khi_promotions_khong_khop_tai_lieu(tmp_path):
    from brd.convert import ConvertError
    with pytest.raises(ConvertError):
        run_pandoc(FIXTURES / "numbered.docx", tmp_path, lua_filter=LUA,
                   metadata={"promotions": [{"text": "không có thật", "level": 1}]})


def test_lua_filter_khong_de_lai_vo_div_custom_style(tmp_path):
    docx = FIXTURES / "numbered.docx"
    md = run_pandoc(docx, tmp_path, lua_filter=LUA,
                    metadata={"promotions": promotions_for(docx)}
                    ).read_text(encoding="utf-8")
    assert "custom-style" not in md
    assert ":::" not in md
