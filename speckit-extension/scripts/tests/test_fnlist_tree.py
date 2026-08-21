import pytest

import fnlist_tree as ft


TREE = [
    {"id": "FN-01", "name": "Quản lý đơn hàng", "description": "", "children": [
        {"id": "FN-01-01", "name": "Danh sách đơn", "description": "Xem đơn",
         "status": "intel", "children": [
            {"id": "FN-01-01-01", "name": "Lọc trạng thái", "description": "",
             "children": []},
        ]},
        {"id": "FN-01-02", "name": "Tạo đơn mới", "description": "", "children": []},
    ]},
    {"id": "FN-02", "name": "Quản lý khách hàng", "description": "", "children": []},
]

TREE_WITH_UC = [
    {"id": "FN-01", "name": "Nhóm A", "description": "", "children": [
        {"id": "FN-01-01", "name": "Lá gộp", "description": "", "children": [],
         "use_cases": [
             {"id": "FN-01-01-UC-01", "name": "UC1", "description": "mô tả 1"},
             {"id": "FN-01-01-UC-02", "name": "UC2", "description": "mô tả 2"},
         ]},
    ]},
]


def test_walk_is_pre_order():
    assert [n["id"] for n, _ in ft.walk(TREE)] == [
        "FN-01", "FN-01-01", "FN-01-01-01", "FN-01-02", "FN-02"]


def test_walk_reports_ancestors():
    by_id = {n["id"]: parents for n, parents in ft.walk(TREE)}
    assert [p["id"] for p in by_id["FN-01-01-01"]] == ["FN-01", "FN-01-01"]
    assert by_id["FN-01"] == ()


def test_walk_descends_into_use_cases():
    ids = [n["id"] for n, _ in ft.walk(TREE_WITH_UC)]
    assert ids == ["FN-01", "FN-01-01", "FN-01-01-UC-01", "FN-01-01-UC-02"]


def test_walk_reports_ancestors_for_use_case():
    by_id = {n["id"]: parents for n, parents in ft.walk(TREE_WITH_UC)}
    parent_ids = [p["id"] for p in by_id["FN-01-01-UC-01"]]
    assert parent_ids == ["FN-01", "FN-01-01"]


def test_name_path_includes_use_case_name():
    node, parents = next((n, p) for n, p in ft.walk(TREE_WITH_UC)
                          if n["id"] == "FN-01-01-UC-01")
    assert ft.name_path(node, parents) == ("Nhóm A", "Lá gộp", "UC1")


def test_is_use_case_distinguishes_fn_node_from_use_case_item():
    fn_node = next(n for n, _ in ft.walk(TREE_WITH_UC) if n["id"] == "FN-01-01")
    uc_item = next(n for n, _ in ft.walk(TREE_WITH_UC) if n["id"] == "FN-01-01-UC-01")
    assert ft.is_use_case(fn_node) is False
    assert ft.is_use_case(uc_item) is True


def test_name_path_joins_ancestor_names():
    node, parents = next((n, p) for n, p in ft.walk(TREE) if n["id"] == "FN-01-01-01")
    assert ft.name_path(node, parents) == (
        "Quản lý đơn hàng", "Danh sách đơn", "Lọc trạng thái")


def test_find_by_id_returns_node_or_none():
    assert ft.find_by_id(TREE, "FN-01-02")["name"] == "Tạo đơn mới"
    assert ft.find_by_id(TREE, "FN-99") is None


def test_clean_node_drops_extra_keys_and_pending_status():
    raw = {"id": "FN-01", "name": "A", "description": "d", "status": "pending",
           "row": 7, "children": [
               {"id": "FN-01-01", "name": "B", "description": "", "status": "srs",
                "row": 8, "children": []}]}
    out = ft.clean_node(raw)
    assert set(out) == {"id", "name", "description", "children"}   # pending bị bỏ
    assert "row" not in out
    assert out["children"][0]["status"] == "srs"                   # status thật thì giữ
    assert set(out["children"][0]) == {"id", "name", "description", "status", "children"}


def test_clean_node_fills_missing_description():
    out = ft.clean_node({"id": "FN-01", "name": "A", "children": []})
    assert out["description"] == ""


def test_clean_use_case_keeps_only_schema_fields():
    raw = {"id": "FN-01-01-UC-01", "name": "U1", "description": "d",
           "row": 5, "status": "pending", "importance": "", "type": "Chính"}
    out = ft.clean_use_case(raw)
    assert out == {"id": "FN-01-01-UC-01", "name": "U1", "description": "d",
                    "type": "Chính"}


def test_clean_node_includes_cleaned_use_cases_when_present():
    raw = {"id": "FN-01", "name": "A", "description": "", "children": [],
           "use_cases": [{"id": "FN-01-UC-01", "name": "U1", "description": "",
                          "row": 3}]}
    out = ft.clean_node(raw)
    assert out["use_cases"] == [{"id": "FN-01-UC-01", "name": "U1", "description": ""}]


def test_clean_node_omits_use_cases_key_when_absent():
    out = ft.clean_node({"id": "FN-01", "name": "A", "children": []})
    assert "use_cases" not in out


def test_build_document_shape():
    doc = ft.build_document(TREE, "DMS", "fn.xlsx", "Sheet1", "2026-08-11", ["FN-03"])
    assert doc["schema_version"] == 1
    assert doc["system"] == "DMS"
    assert doc["source"] == {"file": "fn.xlsx", "sheet": "Sheet1"}
    assert doc["updated"] == "2026-08-11"
    assert doc["retired_ids"] == ["FN-03"]
    assert doc["functions"][0]["id"] == "FN-01"
    assert "row" not in doc["functions"][0]


def test_id_re_matches_multi_level_ids():
    assert ft.ID_RE.match("FN-01")
    assert ft.ID_RE.match("FN-01-02-03")
    assert not ft.ID_RE.match("FN-001")     # định dạng cũ, không còn hợp lệ
    assert not ft.ID_RE.match("FN01")


GRID_OUTLINE = [
    ["STT", "Tên chức năng", "Mô tả"],
    ["1", "Quản lý đơn hàng", ""],
    ["1.1", "Danh sách đơn", "Xem đơn"],
    ["1.1.1", "Lọc trạng thái", ""],
    ["2", "Quản lý khách hàng", ""],
]

GRID_LEVEL = [
    ["Cấp", "Tên chức năng", "Mô tả"],
    ["1", "Quản lý đơn hàng", ""],
    ["2", "Danh sách đơn", "Xem đơn"],
    ["3", "Lọc trạng thái", ""],
    ["1", "Quản lý khách hàng", ""],
]

GRID_STAIRCASE = [
    ["Phân hệ", "Nhóm", "Chức năng", "Mô tả"],
    ["Quản lý đơn hàng", "", "", ""],
    ["", "Danh sách đơn", "", "Xem đơn"],
    ["", "", "Lọc trạng thái", ""],
    ["Quản lý khách hàng", "", "", ""],
]

GRID_REPEATED = [
    ["Phân hệ", "Chức năng", "Mô tả"],
    ["Quản lý đơn hàng", "Danh sách đơn", "Xem đơn"],
    ["Quản lý đơn hàng", "Tạo đơn mới", ""],
    ["Quản lý khách hàng", "Danh sách khách", ""],
]


def _top(grid):
    return ft.detect_hierarchy(grid, 1)[0]


def test_detect_outline_column():
    c = _top(GRID_OUTLINE)
    assert c["mode"] == "outline" and c["column"] == 0
    assert "3 cấp" in c["evidence"]


def test_detect_level_column():
    c = _top(GRID_LEVEL)
    assert c["mode"] == "level" and c["column"] == 0


def test_detect_columns_staircase():
    c = _top(GRID_STAIRCASE)
    assert c["mode"] == "columns"
    assert c["level_columns"] == [0, 1, 2]
    assert c["style"] == "staircase"


def test_detect_columns_repeated():
    c = _top(GRID_REPEATED)
    assert c["mode"] == "columns"
    assert c["level_columns"] == [0, 1]
    assert c["style"] == "repeated"


def test_detect_returns_empty_for_flat_list():
    grid = [["Tên chức năng", "Mô tả"],
            ["Đăng nhập", "Đăng nhập bằng tài khoản"],
            ["Quên mật khẩu", "Đặt lại qua email"]]
    assert ft.detect_hierarchy(grid, 1) == []


def test_detect_ignores_outline_column_with_one_level_only():
    # Cột STT 1,2,3 không có dấu chấm — là số thứ tự, KHÔNG phải phân cấp.
    grid = [["STT", "Tên chức năng"], ["1", "A"], ["2", "B"], ["3", "C"]]
    assert [c["mode"] for c in ft.detect_hierarchy(grid, 1)] == []


def test_detect_sorts_candidates_by_score_desc():
    cands = ft.detect_hierarchy(GRID_STAIRCASE, 1)
    assert cands == sorted(cands, key=lambda c: -c["score"])


def test_detect_columns_window_skips_noise_column_at_start():
    # Cột nhiễu "Mô tả" nằm ở ĐẦU dải (không phải cuối) — dò phải bỏ nó và
    # nhận đúng hai cột cấp thật [Phân hệ, Chức năng] = [1, 2].
    grid = [
        ["Mô tả", "Phân hệ", "Chức năng"],
        ["Xem đơn", "Quản lý đơn hàng", ""],
        ["Tạo đơn", "", "Danh sách đơn"],
        ["Xem KH", "Quản lý khách hàng", ""],
    ]
    c = _top(grid)
    assert c["mode"] == "columns"
    assert c["level_columns"] == [1, 2]
    assert c["style"] == "staircase"


def test_detect_outline_outranks_weak_columns_evidence():
    # Cột mã mục lục khớp 5/6 ô (một ô "X" hỏng, ratio 0.83 — không tuyệt
    # đối), còn dải cột cấp chỉ khớp 6/9 dòng do 3 dòng trống xen giữa (ratio
    # 0.67). Dưới công thức HẰNG SỐ CŨ (level 0.95 / columns 1.0 cố định),
    # columns (1.0) sẽ vượt outline (0.83) và đứng đầu sau khi sort — bug.
    # Dưới công thức MỚI (theo tỉ lệ bằng chứng thật), outline phải thắng rõ
    # ràng vì bằng chứng của nó mạnh hơn thực sự. So điểm trực tiếp, không chỉ
    # dựa vào vị trí đầu danh sách (vị trí có thể bị tie-break của stable sort
    # che khuất bug khi hai score hằng số trùng nhau).
    grid = [
        ["Mã", "Nhóm", "Chức năng"],
        ["1", "A", ""],
        ["1.1", "", "B"],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["X", "C", ""],
        ["2.1", "", "D"],
        ["3", "E", ""],
        ["3.1", "", "F"],
    ]
    cands = ft.detect_hierarchy(grid, 1)
    assert cands == sorted(cands, key=lambda c: -c["score"])
    outline = next(c for c in cands if c["mode"] == "outline")
    columns = next(c for c in cands if c["mode"] == "columns")
    assert cands[0] is outline
    assert outline["score"] > columns["score"]
    assert outline["score"] == round(5 / 6, 2)
    assert columns["score"] == round(6 / 9, 2)


MAP_OUTLINE = {"first_data_row": 1, "columns": {"name": 1, "description": 2},
               "hierarchy": {"mode": "outline", "column": 0}}
MAP_LEVEL = {"first_data_row": 1, "columns": {"name": 1, "description": 2},
             "hierarchy": {"mode": "level", "column": 0}}
MAP_STAIRCASE = {"first_data_row": 1, "columns": {"description": 3},
                 "hierarchy": {"mode": "columns", "level_columns": [0, 1, 2],
                               "style": "staircase"}}
MAP_REPEATED = {"first_data_row": 1, "columns": {"description": 2},
                "hierarchy": {"mode": "columns", "level_columns": [0, 1],
                              "style": "repeated"}}


def _shape(nodes):
    """Cây → list lồng (tên, [con]) để so sánh gọn trong test."""
    return [(n["name"], _shape(n["children"])) for n in nodes]


EXPECTED_SHAPE = [
    ("Quản lý đơn hàng", [
        ("Danh sách đơn", [("Lọc trạng thái", [])]),
    ]),
    ("Quản lý khách hàng", []),
]


def test_build_tree_outline_mode():
    tree, skipped = ft.build_tree(GRID_OUTLINE, MAP_OUTLINE)
    assert _shape(tree) == EXPECTED_SHAPE
    assert skipped == []
    assert tree[0]["children"][0]["description"] == "Xem đơn"


def test_build_tree_level_mode():
    tree, _ = ft.build_tree(GRID_LEVEL, MAP_LEVEL)
    assert _shape(tree) == EXPECTED_SHAPE


def test_build_tree_columns_staircase():
    tree, _ = ft.build_tree(GRID_STAIRCASE, MAP_STAIRCASE)
    assert _shape(tree) == EXPECTED_SHAPE
    assert tree[0]["children"][0]["description"] == "Xem đơn"


def test_build_tree_columns_repeated_reuses_parent():
    tree, _ = ft.build_tree(GRID_REPEATED, MAP_REPEATED)
    assert _shape(tree) == [
        ("Quản lý đơn hàng", [("Danh sách đơn", []), ("Tạo đơn mới", [])]),
        ("Quản lý khách hàng", [("Danh sách khách", [])]),
    ]
    # Node cha lặp ở hai dòng chỉ được tạo MỘT lần.
    assert len(tree) == 2


def test_build_tree_records_row_numbers_one_based():
    tree, _ = ft.build_tree(GRID_OUTLINE, MAP_OUTLINE)
    assert tree[0]["row"] == 2                      # dòng Excel thứ 2
    assert tree[0]["children"][0]["row"] == 3


def test_build_tree_skips_empty_name_with_reason():
    grid = GRID_OUTLINE + [["3", "", ""]]
    tree, skipped = ft.build_tree(grid, MAP_OUTLINE)
    assert len(skipped) == 1
    assert skipped[0]["row"] == 6
    assert skipped[0]["reason"] == "ô tên chức năng trống"


def test_build_tree_honours_skip_rows_one_based():
    tree, skipped = ft.build_tree(GRID_OUTLINE, {**MAP_OUTLINE, "skip_rows": [5]})
    assert _shape(tree) == [("Quản lý đơn hàng", [
        ("Danh sách đơn", [("Lọc trạng thái", [])])])]
    assert skipped[0]["row"] == 5
    assert skipped[0]["reason"] == "người dùng khai bỏ"


def test_build_tree_rejects_level_jump():
    grid = [["STT", "Tên chức năng", "Mô tả"],
            ["1", "Quản lý đơn hàng", ""],
            ["1.1.1", "Lọc trạng thái", ""]]      # nhảy từ cấp 1 xuống cấp 3
    with pytest.raises(ValueError) as e:
        ft.build_tree(grid, MAP_OUTLINE)
    msg = str(e.value)
    assert "nhảy" in msg and "Dòng 3" in msg


def test_build_tree_rejects_first_row_not_top_level():
    grid = [["STT", "Tên chức năng", "Mô tả"], ["1.1", "Danh sách đơn", ""]]
    with pytest.raises(ValueError):
        ft.build_tree(grid, MAP_OUTLINE)


def test_build_tree_repeated_rejects_empty_middle_column():
    grid = [["Phân hệ", "Chức năng", "Mô tả"], ["", "Danh sách đơn", ""]]
    with pytest.raises(ValueError) as e:
        ft.build_tree(grid, MAP_REPEATED)
    assert "trống" in str(e.value)


def test_build_tree_without_hierarchy_is_flat():
    grid = [["Tên chức năng", "Mô tả"], ["Đăng nhập", "x"], ["Quên mật khẩu", "y"]]
    tree, _ = ft.build_tree(grid, {"first_data_row": 1,
                                   "columns": {"name": 0, "description": 1}})
    assert _shape(tree) == [("Đăng nhập", []), ("Quên mật khẩu", [])]


def test_build_tree_staircase_rejects_multiple_filled_columns():
    grid = [["Phân hệ", "Nhóm", "Chức năng", "Mô tả"],
            ["Quản lý đơn hàng", "", "Lọc trạng thái", ""]]   # cột 0 và 2 cùng điền
    with pytest.raises(ValueError) as e:
        ft.build_tree(grid, MAP_STAIRCASE)
    assert "nhiều hơn một cột" in str(e.value)


GRID_OUTLINE_WITH_CONTENT = [
    ["STT", "Tên", "Mô tả", "Mức quan trọng"],
    ["1", "Nhóm A", "", ""],
    ["1.1", "Lá gộp", "", ""],
    ["uc001", "UC1", "mô tả 1", "Cao"],
    ["uc002", "UC2", "mô tả 2", ""],
    ["1.2", "Lá đơn", "mô tả riêng", ""],
]

MAP_ABSORB = {
    "first_data_row": 1,
    "columns": {"name": 1, "description": 2, "importance": 3},
    "hierarchy": {"mode": "outline", "column": 0, "unmatched_rows": "absorb"},
}


def test_build_tree_absorbs_unmatched_rows_as_use_cases():
    tree, skipped = ft.build_tree(GRID_OUTLINE_WITH_CONTENT, MAP_ABSORB)
    assert skipped == []
    la_gop = tree[0]["children"][0]
    assert la_gop["name"] == "Lá gộp"
    assert [u["name"] for u in la_gop["use_cases"]] == ["UC1", "UC2"]
    assert la_gop["use_cases"][0]["description"] == "mô tả 1"
    assert la_gop["use_cases"][0]["importance"] == "Cao"
    assert "importance" not in la_gop["use_cases"][1]     # ô trống -> không ghi
    la_don = tree[0]["children"][1]
    assert la_don.get("use_cases") is None
    assert la_don["description"] == "mô tả riêng"


def test_build_tree_unmatched_rows_default_is_error():
    grid = [["STT", "Tên", "Mô tả"],
            ["1", "Nhóm A", ""],
            ["uc001", "UC1", ""]]
    mapping = {"first_data_row": 1, "columns": {"name": 1, "description": 2},
               "hierarchy": {"mode": "outline", "column": 0}}   # không khai unmatched_rows
    with pytest.raises(ValueError) as e:
        ft.build_tree(grid, mapping)
    assert "không đọc được cấp" in str(e.value)


def test_build_tree_absorb_without_open_group_errors_clearly():
    grid = [["STT", "Tên", "Mô tả"], ["uc001", "UC1", ""]]
    mapping = {"first_data_row": 1, "columns": {"name": 1, "description": 2},
               "hierarchy": {"mode": "outline", "column": 0, "unmatched_rows": "absorb"}}
    with pytest.raises(ValueError) as e:
        ft.build_tree(grid, mapping)
    assert "không có nhóm cha" in str(e.value)


def test_build_tree_node_can_have_both_children_and_use_cases():
    grid = [
        ["STT", "Tên", "Mô tả"],
        ["1", "Nhóm A", ""],
        ["uc001", "UC rời", "mô tả rời"],
        ["1.1", "Nhóm con", ""],
    ]
    mapping = {"first_data_row": 1, "columns": {"name": 1, "description": 2},
               "hierarchy": {"mode": "outline", "column": 0, "unmatched_rows": "absorb"}}
    tree, _ = ft.build_tree(grid, mapping)
    node = tree[0]
    assert [u["name"] for u in node["use_cases"]] == ["UC rời"]
    assert [c["name"] for c in node["children"]] == ["Nhóm con"]


def _mk(name, children=(), description=""):
    return {"name": name, "description": description,
            "children": [dict(c) for c in children]}


def _ids(tree):
    return [n["id"] for n, _ in ft.walk(tree)]


def _mk_uc(name, description="", **extra):
    d = {"name": name, "description": description}
    d.update(extra)
    return d


def test_assign_ids_numbers_per_parent():
    tree = [_mk("A", [_mk("A1", [_mk("A1a")]), _mk("A2")]), _mk("B")]
    ft.assign_ids(tree)
    assert _ids(tree) == ["FN-01", "FN-01-01", "FN-01-01-01", "FN-01-02", "FN-02"]


def test_assign_ids_reuses_id_for_same_name_path():
    old = [_mk("A", [_mk("A1"), _mk("A2")])]
    ft.assign_ids(old)
    new = [_mk("A", [_mk("A1"), _mk("A2")])]
    ft.assign_ids(new, old)
    assert _ids(new) == _ids(old)


def test_assign_ids_gives_next_free_number_to_inserted_row():
    old = [_mk("A", [_mk("A1"), _mk("A2")])]
    ft.assign_ids(old)                        # A1=FN-01-01, A2=FN-01-02
    new = [_mk("A", [_mk("A1"), _mk("Amoi"), _mk("A2")])]
    ft.assign_ids(new, old)
    got = {n["name"]: n["id"] for n, _ in ft.walk(new)}
    assert got["A1"] == "FN-01-01"            # giữ nguyên
    assert got["A2"] == "FN-01-02"            # KHÔNG bị dịch số
    assert got["Amoi"] == "FN-01-03"          # chèn giữa nhưng mang số cuối


def test_assign_ids_distinguishes_same_name_in_different_parents():
    # Cùng tên "Thêm mới" ở hai nhóm — bản cũ khớp theo tên đơn sẽ tranh ID.
    old = [_mk("A", [_mk("Thêm mới")]), _mk("B", [_mk("Thêm mới")])]
    ft.assign_ids(old)
    new = [_mk("A", [_mk("Thêm mới")]), _mk("B", [_mk("Thêm mới")])]
    ft.assign_ids(new, old)
    assert _ids(new) == ["FN-01", "FN-01-01", "FN-02", "FN-02-01"]


def test_assign_ids_never_reuses_retired_number():
    old = [_mk("A", [_mk("A1")])]
    ft.assign_ids(old)                        # A1 = FN-01-01
    new = [_mk("A", [_mk("Amoi")])]
    ft.assign_ids(new, old, retired=["FN-01-01"])
    assert ft.find_by_id(new, "FN-01-01") is None
    assert [n["id"] for n, _ in ft.walk(new)][1] == "FN-01-02"


def test_assign_ids_treats_moved_node_as_new():
    old = [_mk("A", [_mk("X")]), _mk("B")]
    ft.assign_ids(old)                        # X = FN-01-01
    new = [_mk("A"), _mk("B", [_mk("X")])]    # X chuyển sang nhóm B
    ft.assign_ids(new, old)
    assert {n["name"]: n["id"] for n, _ in ft.walk(new)}["X"] == "FN-02-01"


def test_assign_ids_does_not_collide_duplicate_names_under_same_parent():
    # Hai node cùng tên "Thêm mới" dưới cùng cha "A" — cả cây cũ và cây mới.
    # Nếu old_by_path không tiêu thụ entry sau khi khớp, cả hai node mới sẽ
    # cùng tra trúng một old node và bị đâm chung ID.
    old = [_mk("A", [_mk("Thêm mới"), _mk("Thêm mới")])]
    ft.assign_ids(old)
    new = [_mk("A", [_mk("Thêm mới"), _mk("Thêm mới")])]
    ft.assign_ids(new, old)
    ids = [n["id"] for n, _ in ft.walk(new) if n["name"] == "Thêm mới"]
    assert len(ids) == 2
    assert ids[0] != ids[1]


def test_assign_ids_does_not_reassign_id_retired_within_same_run():
    # A2 bị xoá và C (tên khác hoàn toàn, node MỚI) được thêm trong CÙNG một
    # lần import. compute_retired chạy SAU assign_ids nên ID của A2 chưa nằm
    # trong `retired` lúc assign_ids chạy — nếu assign_ids chỉ tránh
    # `retired`/`prev_retired` thì C sẽ bị cấp đúng ID vừa chết của A2.
    old = [_mk("A", [_mk("A1"), _mk("A2")])]
    ft.assign_ids(old)                        # A1=FN-01-01, A2=FN-01-02
    a2_id = next(n["id"] for n, _ in ft.walk(old) if n["name"] == "A2")
    new = [_mk("A", [_mk("A1"), _mk("C")])]   # A2 xoá, C là node MỚI
    ft.assign_ids(new, old)
    c_id = next(n["id"] for n, _ in ft.walk(new) if n["name"] == "C")
    assert c_id != a2_id
    assert a2_id in ft.compute_retired(old, new)


def test_assign_ids_move_plus_insert_same_run_no_id_collision_or_status_leak():
    # Ca verify được trong review: X chuyển từ A sang B, đồng thời Y (node
    # MỚI) được thêm vào đúng vị trí X vừa bỏ lại ở A — trong CÙNG một lần
    # import. Y không được thừa hưởng ID (và do đó status) cũ của X.
    old = [_mk("A", [_mk("X")]), _mk("B")]
    ft.assign_ids(old)                        # X = FN-01-01
    ft.find_by_id(old, "FN-01-01")["status"] = "srs"
    new = [_mk("A", [_mk("Y")]), _mk("B", [_mk("X")])]
    ft.assign_ids(new, old)
    ft.carry_status(new, old)
    y_id = next(n["id"] for n, _ in ft.walk(new) if n["name"] == "Y")
    x_id = next(n["id"] for n, _ in ft.walk(new) if n["name"] == "X")
    assert y_id != x_id
    assert y_id != "FN-01-01"                 # cấm tái dùng ID vừa chết trong cùng lần
    assert x_id == "FN-02-01"
    assert "status" not in next(n for n, _ in ft.walk(new) if n["name"] == "Y")


def test_assign_ids_stable_across_reimport_when_fn_child_and_use_case_share_name():
    # Cha "A" có cả một node FN con tên "U1" LẪN một use-case con cùng tên
    # "U1" — khớp shape mà spec §2 yêu cầu hỗ trợ (một node vừa có `children`
    # vừa có `use_cases`). Nếu old_by_path chỉ khoá theo tên (không phân biệt
    # namespace FN/use-case), entry use-case ghi đè âm thầm lên entry FN cùng
    # tên (walk() trả children trước use_cases), và ở lần import lại node FN
    # con tra trúng entry use-case (khác tiền tố ID), khớp thất bại, ID bị cấp
    # lại dù nguồn không đổi gì. Chạy hai lần liên tiếp trên cùng một shape
    # phải cho đúng cùng ID cả hai bên.
    old = [_mk("A", [_mk("U1")])]
    old[0]["use_cases"] = [_mk_uc("U1")]
    ft.assign_ids(old)
    fn_id_before = old[0]["children"][0]["id"]
    uc_id_before = old[0]["use_cases"][0]["id"]
    assert fn_id_before != uc_id_before        # tiền tố khác nhau (FN-.. vs FN-..-UC-..)

    new = [_mk("A", [_mk("U1")])]
    new[0]["use_cases"] = [_mk_uc("U1")]
    ft.assign_ids(new, old)

    assert new[0]["children"][0]["id"] == fn_id_before
    assert new[0]["use_cases"][0]["id"] == uc_id_before


def test_assign_ids_assigns_use_case_ids_scoped_to_parent():
    tree = [_mk("A", [_mk("A1")])]
    tree[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("U2")]
    ft.assign_ids(tree)
    a1 = tree[0]["children"][0]
    assert a1["id"] == "FN-01-01"
    assert [u["id"] for u in a1["use_cases"]] == ["FN-01-01-UC-01", "FN-01-01-UC-02"]


def test_assign_ids_reuses_use_case_id_across_reimport():
    old = [_mk("A", [_mk("A1")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("U2")]
    ft.assign_ids(old)
    new = [_mk("A", [_mk("A1")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("Umoi"), _mk_uc("U2")]
    ft.assign_ids(new, old)
    a1 = new[0]["children"][0]
    got = {u["name"]: u["id"] for u in a1["use_cases"]}
    assert got["U1"] == "FN-01-01-UC-01"
    assert got["U2"] == "FN-01-01-UC-02"          # KHÔNG bị dịch số
    assert got["Umoi"] == "FN-01-01-UC-03"        # chèn giữa, mang số cuối


def test_assign_ids_never_reuses_retired_use_case_number():
    old = [_mk("A", [_mk("A1")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1")]
    ft.assign_ids(old)
    uc_id = old[0]["children"][0]["use_cases"][0]["id"]
    new = [_mk("A", [_mk("A1")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("Umoi")]
    ft.assign_ids(new, old, retired=[uc_id])
    got_id = new[0]["children"][0]["use_cases"][0]["id"]
    assert got_id != uc_id
    assert got_id == "FN-01-01-UC-02"


def test_carry_status_copies_use_case_status_by_id():
    old = [_mk("A", [_mk("A1")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1")]
    ft.assign_ids(old)
    old[0]["children"][0]["use_cases"][0]["status"] = "intel"
    new = [_mk("A", [_mk("A1")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("U2")]
    ft.assign_ids(new, old)
    ft.carry_status(new, old)
    ucs = {u["name"]: u for u in new[0]["children"][0]["use_cases"]}
    assert ucs["U1"]["status"] == "intel"
    assert "status" not in ucs["U2"]


def test_compute_retired_includes_removed_use_case_ids():
    old = [_mk("A", [_mk("A1")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("U2")]
    ft.assign_ids(old)
    u2_id = old[0]["children"][0]["use_cases"][1]["id"]
    new = [_mk("A", [_mk("A1")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("U1")]
    ft.assign_ids(new, old)
    assert u2_id in ft.compute_retired(old, new)


def test_compute_retired_accumulates():
    old = [_mk("A", [_mk("A1"), _mk("A2")])]
    ft.assign_ids(old)
    new = [_mk("A", [_mk("A1")])]             # A2 bị xoá
    ft.assign_ids(new, old)
    assert ft.compute_retired(old, new, ["FN-09"]) == ["FN-01-02", "FN-09"]


def test_carry_status_copies_by_id():
    old = [_mk("A", [_mk("A1")])]
    ft.assign_ids(old)
    ft.find_by_id(old, "FN-01-01")["status"] = "srs"
    new = [_mk("A", [_mk("A1"), _mk("A2")])]
    ft.assign_ids(new, old)
    ft.carry_status(new, old)
    assert ft.find_by_id(new, "FN-01-01")["status"] == "srs"
    assert "status" not in ft.find_by_id(new, "FN-01-02")


def _prepared(shape):
    ft.assign_ids(shape)
    return shape


def test_diff_reports_added_and_removed():
    old = _prepared([_mk("A", [_mk("A1"), _mk("A2")])])
    new = _prepared([_mk("A", [_mk("A1"), _mk("A3")])])
    kinds = {(d["loai"], d["ten"]) for d in ft.diff_trees(old, new)}
    assert ("bỏ", "A2") in kinds
    assert ("thêm", "A3") in kinds


def test_diff_reports_description_change():
    old = _prepared([_mk("A", [_mk("A1", description="cũ")])])
    new = _prepared([_mk("A", [_mk("A1", description="mới")])])
    entry = next(d for d in ft.diff_trees(old, new) if d["loai"] == "đổi mô tả")
    assert entry["ten"] == "A1" and entry["cu"] == "cũ" and entry["moi"] == "mới"


def test_diff_labels_move_between_parents():
    old = _prepared([_mk("A", [_mk("X")]), _mk("B")])
    new = _prepared([_mk("A"), _mk("B", [_mk("X")])])
    entries = ft.diff_trees(old, new)
    move = next(d for d in entries if d["loai"] == "chuyển nhóm")
    assert move["ten"] == "X"
    assert move["id_cu"] == "FN-01-01" and move["id_moi"] == "FN-02-01"
    assert move["tu"] == "A / X" and move["den"] == "B / X"
    # Đã gộp thì không còn trình như một cặp thêm+bỏ rời rạc.
    assert not any(d["loai"] in ("thêm", "bỏ") and d["ten"] == "X" for d in entries)


def test_diff_does_not_guess_move_when_name_is_ambiguous():
    # Hai node cùng tên "X" bị bỏ, một node "X" được thêm — không đủ căn cứ để
    # nói cái nào chuyển sang đâu, phải trình nguyên trạng thêm/bỏ.
    old = _prepared([_mk("A", [_mk("X")]), _mk("B", [_mk("X")])])
    new = _prepared([_mk("C", [_mk("X")])])
    kinds = [d["loai"] for d in ft.diff_trees(old, new)]
    assert "chuyển nhóm" not in kinds
    assert kinds.count("bỏ") == 2


def test_diff_against_empty_old_tree_is_all_additions():
    new = _prepared([_mk("A", [_mk("A1")])])
    assert {d["loai"] for d in ft.diff_trees(None, new)} == {"thêm"}


def test_diff_move_does_not_leak_group_status_change_noise():
    # Case gốc của test_diff_labels_move_between_parents: B rỗng con ở cây cũ
    # (tính là lá), có con ở cây mới (không còn là lá) — không được sinh entry
    # "bỏ"/"thêm" giả cho A/B, chỉ có đúng một entry "chuyển nhóm" cho X.
    old = _prepared([_mk("A", [_mk("X")]), _mk("B")])
    new = _prepared([_mk("A"), _mk("B", [_mk("X")])])
    entries = ft.diff_trees(old, new)
    assert not any(d["loai"] in ("thêm", "bỏ") and d["ten"] in ("A", "B") for d in entries)
    assert len([d for d in entries if d["loai"] == "chuyển nhóm"]) == 1


def test_diff_move_with_description_change_reports_both():
    old = _prepared([_mk("A", [_mk("X", description="cũ")]), _mk("B")])
    new = _prepared([_mk("A"), _mk("B", [_mk("X", description="mới")])])
    entries = ft.diff_trees(old, new)
    move = next(d for d in entries if d["loai"] == "chuyển nhóm")
    assert move["cu"] == "cũ" and move["moi"] == "mới"


def test_diff_move_without_description_change_has_no_extra_keys():
    old = _prepared([_mk("A", [_mk("X", description="giữ nguyên")]), _mk("B")])
    new = _prepared([_mk("A"), _mk("B", [_mk("X", description="giữ nguyên")])])
    entries = ft.diff_trees(old, new)
    move = next(d for d in entries if d["loai"] == "chuyển nhóm")
    assert "cu" not in move and "moi" not in move


def test_diff_reports_use_case_added_and_removed():
    old = [_mk("A", [_mk("A1")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("U2")]
    old = _prepared(old)
    new = [_mk("A", [_mk("A1")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("U1"), _mk_uc("U3")]
    new = _prepared(new)
    entries = ft.diff_trees(old, new)
    kinds = {(d["loai"], d["ten"]) for d in entries}
    assert ("use-case bỏ", "U2") in kinds
    assert ("use-case thêm", "U3") in kinds
    assert not any(d["loai"] in ("thêm", "bỏ") for d in entries)   # không lẫn nhãn FN


def test_diff_reports_use_case_description_change():
    old = [_mk("A", [_mk("A1")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1", description="cũ")]
    old = _prepared(old)
    new = [_mk("A", [_mk("A1")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("U1", description="mới")]
    new = _prepared(new)
    entry = next(d for d in ft.diff_trees(old, new)
                 if d["loai"] == "use-case đổi mô tả")
    assert entry["ten"] == "U1" and entry["cu"] == "cũ" and entry["moi"] == "mới"


def test_diff_reports_use_case_promoted_to_fn_child_as_flip_not_swallowed():
    # Cùng một dòng nguồn, "Lá gộp" giữ nguyên vị trí, nhưng U1 đổi VAI TRÒ:
    # ở bản cũ nó là use-case con (không mã outline), ở bản mới nó có mã
    # outline riêng nên trở thành node FN con thật sự. Danh tính cũ (use-case)
    # và danh tính mới (FN) phải cùng hiện ra — không được "biến mất" chỉ vì
    # đường dẫn tên đó vẫn tồn tại ở namespace khác trong cây kia.
    old = [_mk("A", [_mk("Lá gộp")])]
    old[0]["children"][0]["use_cases"] = [_mk_uc("U1")]
    old = _prepared(old)
    new = [_mk("A", [_mk("Lá gộp", [_mk("U1")])])]
    new = _prepared(new)
    entries = ft.diff_trees(old, new)
    kinds = {(d["loai"], d["ten"]) for d in entries}
    assert ("use-case bỏ", "U1") in kinds     # danh tính cũ (use-case) mất đi
    assert ("thêm", "U1") in kinds            # danh tính mới (node FN) xuất hiện


def test_diff_reports_fn_child_demoted_to_use_case_as_flip_not_swallowed():
    # Chiều ngược lại: U1 là node FN con ở bản cũ, mất mã outline riêng ở bản
    # mới nên bị gộp thành use-case con của "Lá gộp".
    old = [_mk("A", [_mk("Lá gộp", [_mk("U1")])])]
    old = _prepared(old)
    new = [_mk("A", [_mk("Lá gộp")])]
    new[0]["children"][0]["use_cases"] = [_mk_uc("U1")]
    new = _prepared(new)
    entries = ft.diff_trees(old, new)
    kinds = {(d["loai"], d["ten"]) for d in entries}
    assert ("bỏ", "U1") in kinds              # danh tính cũ (node FN) mất đi
    assert ("use-case thêm", "U1") in kinds   # danh tính mới (use-case) xuất hiện


def test_subtree_leaves_returns_self_when_no_children():
    node = _prepared([_mk("Đăng xuất")])[0]
    assert ft.subtree_leaves(node) == [node]


def test_subtree_leaves_collects_all_descendant_leaves():
    tree = _prepared([_mk("A", [_mk("A1", [_mk("A1a"), _mk("A1b")]), _mk("A2")])])[0]
    leaves = ft.subtree_leaves(tree)
    assert [n["name"] for n in leaves] == ["A1a", "A1b", "A2"]


def test_subtree_leaves_on_a_leaf_node_itself():
    tree = _prepared([_mk("Tạo đơn mới")])[0]
    assert ft.subtree_leaves(tree) == [tree]
