import sys
from pathlib import Path

import intel_tree as it


def _mk(id_, name, children=()):
    return {"id": id_, "name": name, "children": list(children)}


def test_slugify_removes_diacritics_and_lowercases():
    assert it.slugify("Quản lý người dùng") == "quan-ly-nguoi-dung"


def test_slugify_handles_dd_specially():
    assert it.slugify("Đăng xuất") == "dang-xuat"


def test_slugify_collapses_punctuation_to_single_hyphen():
    assert it.slugify("Thêm / Sửa / Xoá") == "them-sua-xoa"


def test_slugify_truncates_long_names():
    long_name = "Quản lý " + "chức năng " * 20
    assert len(it.slugify(long_name)) <= 60


def test_slugify_empty_result_falls_back():
    assert it.slugify("...") == "khong-ten"


def test_dedupe_slugs_appends_suffix_on_collision():
    assert it.dedupe_slugs(["thanh-toan", "thanh-toan", "don-hang"]) == [
        "thanh-toan", "thanh-toan-2", "don-hang"]


def test_dedupe_slugs_leaves_unique_untouched():
    assert it.dedupe_slugs(["a", "b", "c"]) == ["a", "b", "c"]


def test_is_leaf_true_for_no_children():
    assert it.is_leaf(_mk("FN-01", "A")) is True


def test_is_leaf_false_when_has_children():
    assert it.is_leaf(_mk("FN-01", "A", [_mk("FN-01-01", "A1")])) is False


def test_is_leaf_parent_true_when_all_children_are_leaves():
    node = _mk("FN-01", "A", [_mk("FN-01-01", "A1"), _mk("FN-01-02", "A2")])
    assert it.is_leaf_parent(node) is True


def test_is_leaf_parent_false_when_a_child_has_grandchildren():
    node = _mk("FN-01", "A", [
        _mk("FN-01-01", "A1", [_mk("FN-01-01-01", "A1a")]),
    ])
    assert it.is_leaf_parent(node) is False


def test_is_leaf_parent_false_for_childless_node():
    assert it.is_leaf_parent(_mk("FN-05", "Đăng xuất")) is False


def test_default_units_on_standalone_leaf_returns_itself():
    leaf = _mk("FN-05", "Đăng xuất")
    assert it.default_units(leaf) == [leaf]


def test_default_units_on_leaf_parent_returns_itself():
    node = _mk("FN-01", "A", [_mk("FN-01-01", "A1"), _mk("FN-01-02", "A2")])
    assert it.default_units(node) == [node]


def test_default_units_recurses_past_intermediate_groups():
    tree = _mk("FN-01", "Root", [
        _mk("FN-01-01", "Nhom con 1", [
            _mk("FN-01-01-01", "La 1"), _mk("FN-01-01-02", "La 2")]),
        _mk("FN-01-02", "Nhom con 2", [_mk("FN-01-02-01", "La 3")]),
    ])
    units = it.default_units(tree)
    assert [u["id"] for u in units] == ["FN-01-01", "FN-01-02"]


def test_default_units_treats_lone_leaf_under_mixed_parent_as_own_unit():
    # "La don le" không có con và đứng cạnh "Nhom con" (có cháu) — phải tự
    # thành unit riêng, không bị gộp lên node Mixed.
    tree = _mk("FN-02", "Mixed", [
        _mk("FN-02-01", "La don le"),
        _mk("FN-02-02", "Nhom con", [_mk("FN-02-02-01", "La sau")]),
    ])
    units = it.default_units(tree)
    assert [u["id"] for u in units] == ["FN-02-01", "FN-02-02"]


def test_compute_paths_numbers_by_sibling_position():
    tree = [
        _mk("FN-01", "Quan ly don hang", [
            _mk("FN-01-01", "Danh sach don"),
            _mk("FN-01-02", "Tao don moi"),
        ]),
        _mk("FN-02", "Quan ly khach hang", []),
    ]
    paths = it.compute_paths(tree)
    assert paths["FN-01"] == "01-quan-ly-don-hang"
    assert paths["FN-01-01"] == "01-quan-ly-don-hang/01-danh-sach-don"
    assert paths["FN-01-02"] == "01-quan-ly-don-hang/02-tao-don-moi"
    assert paths["FN-02"] == "02-quan-ly-khach-hang"


def test_compute_paths_dedupes_sibling_slug_collisions():
    tree = [_mk("FN-01", "Them moi"), _mk("FN-02", "Thêm Mới")]
    paths = it.compute_paths(tree)
    assert paths["FN-01"] == "01-them-moi"
    assert paths["FN-02"] == "02-them-moi-2"


def test_render_tree_marks_unit_boundaries():
    tree = [_mk("FN-01", "A", [_mk("FN-01-01", "A1")])]
    lines = it.render_tree(tree, {"FN-01"})
    assert lines[0] == "A (FN-01)  [UNIT]"
    assert lines[1] == "  A1 (FN-01-01)"


def test_render_tree_no_marker_when_not_a_unit():
    tree = [_mk("FN-01", "A", [_mk("FN-01-01", "A1")])]
    lines = it.render_tree(tree, {"FN-01-01"})
    assert lines[0] == "A (FN-01)"
    assert lines[1] == "  A1 (FN-01-01)  [UNIT]"


def test_render_tree_shows_use_cases_with_dot_marker():
    tree = [{"id": "FN-01", "name": "A", "children": [], "use_cases": [
        {"id": "FN-01-UC-01", "name": "U1"},
        {"id": "FN-01-UC-02", "name": "U2"},
    ]}]
    lines = it.render_tree(tree, set())
    assert lines == ["A (FN-01)", "  · U1 (FN-01-UC-01)", "  · U2 (FN-01-UC-02)"]


def test_render_tree_use_cases_nest_under_children_too():
    tree = [{"id": "FN-01", "name": "A", "children": [
        {"id": "FN-01-01", "name": "A1", "children": [], "use_cases": [
            {"id": "FN-01-01-UC-01", "name": "U1"}]},
    ]}]
    lines = it.render_tree(tree, set())
    assert lines == [
        "A (FN-01)",
        "  A1 (FN-01-01)",
        "    · U1 (FN-01-01-UC-01)",
    ]


def _doc(functions):
    return {"schema_version": 1, "system": "T", "source": {}, "updated": "2026-08-12",
            "retired_ids": [], "functions": functions}


def test_cli_propose_end_to_end(tmp_path):
    import json as _json
    import subprocess
    doc = _doc([
        {"id": "FN-01", "name": "Quan ly don hang", "description": "", "children": [
            {"id": "FN-01-01", "name": "Danh sach don", "description": "", "children": []},
            {"id": "FN-01-02", "name": "Tao don moi", "description": "", "children": []},
        ]},
    ])
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(doc), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run([sys.executable, str(script), "propose", "--functions", str(fp)],
                       capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    out = _json.loads(p.stdout)
    assert out["units"] == [{"id": "FN-01", "name": "Quan ly don hang"}]
    assert "[UNIT]" in out["tree"]


def test_cli_propose_scoped_to_start_node(tmp_path):
    import json as _json
    import subprocess
    doc = _doc([
        {"id": "FN-01", "name": "A", "description": "", "children": [
            {"id": "FN-01-01", "name": "A1", "description": "", "children": []}]},
        {"id": "FN-02", "name": "B", "description": "", "children": [
            {"id": "FN-02-01", "name": "B1", "description": "", "children": []}]},
    ])
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(doc), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run(
        [sys.executable, str(script), "propose", "--functions", str(fp), "--start", "FN-02"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    out = _json.loads(p.stdout)
    assert out["units"] == [{"id": "FN-02", "name": "B"}]


def test_cli_units_end_to_end(tmp_path):
    import json as _json
    import subprocess
    doc = _doc([
        {"id": "FN-01", "name": "Quan ly don hang", "description": "", "children": [
            {"id": "FN-01-01", "name": "Danh sach don", "description": "",
             "status": "intel", "children": []},
        ]},
    ])
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(doc), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run(
        [sys.executable, str(script), "units", "--functions", str(fp), "--roots", "FN-01"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    out = _json.loads(p.stdout)
    unit = out["units"][0]
    assert unit["path"] == "01-quan-ly-don-hang/intel.md"
    assert unit["fn_ids"] == [{"id": "FN-01-01", "name": "Danh sach don", "status": "intel"}]


def test_cli_units_defaults_missing_status_to_pending(tmp_path):
    import json as _json
    import subprocess
    doc = _doc([{"id": "FN-01", "name": "A", "description": "", "children": []}])
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(doc), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run(
        [sys.executable, str(script), "units", "--functions", str(fp), "--roots", "FN-01"],
        capture_output=True, text=True, encoding="utf-8")
    out = _json.loads(p.stdout)
    assert out["units"][0]["fn_ids"][0]["status"] == "pending"


def test_cli_units_includes_use_cases_when_present(tmp_path):
    import json as _json
    import subprocess
    doc = _doc([
        {"id": "FN-01", "name": "A", "description": "", "children": [], "use_cases": [
            {"id": "FN-01-UC-01", "name": "U1", "description": "mo ta 1",
             "importance": "Cao"},
            {"id": "FN-01-UC-02", "name": "U2", "description": ""},
        ]},
    ])
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(doc), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run(
        [sys.executable, str(script), "units", "--functions", str(fp), "--roots", "FN-01"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    out = _json.loads(p.stdout)
    ucs = out["units"][0]["fn_ids"][0]["use_cases"]
    assert ucs[0] == {"id": "FN-01-UC-01", "name": "U1", "description": "mo ta 1",
                      "status": "pending", "importance": "Cao", "type": "",
                      "usage_timing": ""}
    assert ucs[1] == {"id": "FN-01-UC-02", "name": "U2", "description": "",
                      "status": "pending", "importance": "", "type": "",
                      "usage_timing": ""}


def test_cli_units_omits_use_cases_key_when_leaf_has_none(tmp_path):
    import json as _json
    import subprocess
    doc = _doc([{"id": "FN-01", "name": "A", "description": "", "children": []}])
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(doc), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run(
        [sys.executable, str(script), "units", "--functions", str(fp), "--roots", "FN-01"],
        capture_output=True, text=True, encoding="utf-8")
    out = _json.loads(p.stdout)
    assert "use_cases" not in out["units"][0]["fn_ids"][0]


def test_cli_units_reports_missing_root(tmp_path):
    import json as _json
    import subprocess
    fp = tmp_path / "functions.json"
    fp.write_text(_json.dumps(_doc([])), encoding="utf-8")
    script = Path(it.__file__)
    p = subprocess.run(
        [sys.executable, str(script), "units", "--functions", str(fp), "--roots", "FN-99"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode != 0
    assert "FN-99" in p.stderr
