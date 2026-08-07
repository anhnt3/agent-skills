from brd.docx_probe import count_paragraph_styles, detect_tier, heading_style_levels


def test_heading_style_levels_doc_duoc_outlinelvl(real_brd):
    levels = heading_style_levels(real_brd)
    assert levels["Heading1"] == 1
    assert levels["Heading6"] == 6
    assert levels["Heading8"] == 8


def test_count_paragraph_styles_khop_so_da_do(real_brd):
    counts = count_paragraph_styles(real_brd)
    assert counts["Heading8"] == 432
    assert counts["Heading6"] == 54
    assert counts["Heading1"] == 2


def test_detect_tier_brd_that_la_bac_1(real_brd):
    res = detect_tier(real_brd)
    assert res["tier"] == 1
    assert res["heading_count"] == 604
    assert res["needs_llm"] is False
