# Fnlist-import content-rows + use_cases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `fnlist-import` correctly read function lists where only group-header rows
carry a hierarchy code and individual use-case rows don't (like `Fnclist.xlsx` sheet `UC`),
collapsing those use-case rows into a `use_cases` array on the nearest open leaf node instead
of crashing or losing them — and capture three optional BA fields (mức quan trọng/loại
UC/thời điểm sử dụng) per use-case so they stop being silently dropped.

**Architecture:** Add one new orthogonal concept, "dòng nội dung" (content row), to the
existing hierarchy-detection code in `fnlist_tree.py`: a row that doesn't resolve to a level
under the chosen mode is no longer always a hard error — under
`mapping.json:hierarchy.unmatched_rows = "absorb"` it becomes an item in `use_cases[]` on the
currently-open parent node. `use_cases` items get stable IDs (`<parent-id>-UC-nn`) via the
exact same `assign_ids` mechanism already used for FN nodes, just re-entered with a different
prefix — so `walk()`, `carry_status()`, `compute_retired()` generalize almost for free once
they traverse `use_cases` alongside `children`; `diff_trees()` gets a small refactor to keep
FN-level and use-case-level diff entries under separate labels.

**Tech Stack:** Python 3 (stdlib only for `fnlist_tree.py`; `fnlist_import.py` uses
`openpyxl` for `.xlsx`), pytest for tests, Markdown for the command/schema doc.

**Spec:** [docs/superpowers/specs/2026-08-18-fnlist-import-content-rows-design.md](../specs/2026-08-18-fnlist-import-content-rows-design.md)

## Global Constraints

- Vietnamese content throughout every user-facing string/doc; English keys in JSON
  (`use_cases`, `importance`, `type`, `usage_timing`, `unmatched_rows`) — matches the
  existing convention in `functions-schema.md`.
- "Script chép nguyên văn — LLM không tự tóm tắt/chuẩn hoá nội dung ô" stays true: this
  plan only changes what the script CAPTURES (extra columns) and how it STRUCTURES rows
  (absorb into `use_cases`), never how it transforms cell text.
- `functions.json` nodes keep "5 trường, không hơn" (`id`/`name`/`description`/`status`/
  `children`) as the default shape; `use_cases` is an additional, optional 6th key present
  only on nodes that actually have content rows underneath.
- Default behavior for files that don't opt in (`unmatched_rows` absent) must stay byte-for-
  byte identical to today — every existing test in `test_fnlist_tree.py` /
  `test_fnlist_import.py` must keep passing unmodified.
- Scope is **only** `speckit-extension/scripts/fnlist_tree.py`,
  `speckit-extension/scripts/fnlist_import.py`,
  `speckit-extension/commands/fnlist-import.md`,
  `speckit-extension/references/functions-schema.md`, and their tests under
  `speckit-extension/scripts/tests/`. Do **not** touch `commands/code-intel.md` or
  `commands/srs-from-code.md` — reading/using `use_cases` downstream is a later, separate
  spec (see design doc's "Ngoài phạm vi").
- Run tests with `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py
  speckit-extension/scripts/tests/test_fnlist_import.py -q` from the repo root
  (`e:\agent-skills`) — `conftest.py` adds `scripts/` to `sys.path`, no venv activation
  needed for these two files (they don't touch `.xlsx`/`openpyxl`).

---

### Task 1: `walk()` traverses `use_cases`; add `is_use_case()`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py:16-20` (the `walk()` function)
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Produces: `ft.walk(nodes, parents=())` — now also yields `use_cases` items (pre-order,
  after a node's own `children`). `ft.is_use_case(node) -> bool` — `True` iff `"children"
  not in node` (the one and only signal that distinguishes a use-case item dict from an FN
  tree-node dict; FN nodes always carry a `"children"` key, even `[]`).
- Consumes: nothing new — pure addition to existing `walk()`.

- [ ] **Step 1: Write the failing tests**

Add near the top of `speckit-extension/scripts/tests/test_fnlist_tree.py`, right after the
existing `TREE` constant (after line 16):

```python
TREE_WITH_UC = [
    {"id": "FN-01", "name": "Nhóm A", "description": "", "children": [
        {"id": "FN-01-01", "name": "Lá gộp", "description": "", "children": [],
         "use_cases": [
             {"id": "FN-01-01-UC-01", "name": "UC1", "description": "mô tả 1"},
             {"id": "FN-01-01-UC-02", "name": "UC2", "description": "mô tả 2"},
         ]},
    ]},
]


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -k "use_case or walk_descends" -v`
Expected: FAIL — `test_walk_descends_into_use_cases` / `test_walk_reports_ancestors_for_use_case`
/ `test_name_path_includes_use_case_name` fail because `walk()` doesn't yet descend into
`use_cases` (their IDs/paths are missing); `test_is_use_case_distinguishes_fn_node_from_use_case_item`
fails with `AttributeError: module 'fnlist_tree' has no attribute 'is_use_case'`.

- [ ] **Step 3: Implement**

Replace `speckit-extension/scripts/fnlist_tree.py:16-20`:

```python
def walk(nodes, parents=()):
    """Duyệt pre-order — đúng thứ tự dòng của file nguồn. Trả (node, tuple cha)."""
    for node in nodes:
        yield node, parents
        yield from walk(node.get("children") or [], parents + (node,))
```

with:

```python
def walk(nodes, parents=()):
    """Duyệt pre-order — đúng thứ tự dòng của file nguồn. Trả (node, tuple cha).

    Đi qua cả `children` (node cây FN) lẫn `use_cases` (mục use-case con của
    một node lá) — use-case item không có khoá `children`/`use_cases` của
    riêng nó nên đệ quy tự dừng, không cần điều kiện chặn riêng."""
    for node in nodes:
        yield node, parents
        yield from walk(node.get("children") or [], parents + (node,))
        yield from walk(node.get("use_cases") or [], parents + (node,))


def is_use_case(node):
    """True nếu node là một mục use-case con (không phải node cây FN).

    Phân biệt bằng sự VẮNG MẶT của khoá `children` — mọi node cây FN đều có
    khoá này (kể cả khi rỗng `[]`), còn use-case item thì không bao giờ có."""
    return "children" not in node
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -q`
Expected: PASS, all tests (old + new) green.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist-import): walk() traverses use_cases, add is_use_case()"
```

---

### Task 2: `_build_leveled` absorbs unmatched rows into `use_cases`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py:249-272` (`_build_leveled`), add new
  `UC_EXTRA_FIELDS` constant + `_use_case_extra` helper right before it
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `is_use_case` from Task 1 (not directly needed here, but this task's output
  shape — `use_cases` dicts without `"children"` — is what makes `is_use_case` meaningful).
- Produces: `mapping.json` gains `hierarchy.unmatched_rows` (`"error"` default | `"absorb"`)
  and `columns.importance` / `columns.type` / `columns.usage_timing` (all optional column
  indices). A node built by `_build_leveled` may now carry a `use_cases` list (each item:
  `{"name", "description", "row", ...optional extra fields}` — no `"id"` yet, assigned
  later by `assign_ids` in Task 3).

- [ ] **Step 1: Write the failing tests**

Add to `speckit-extension/scripts/tests/test_fnlist_tree.py`, after
`test_build_tree_staircase_rejects_multiple_filled_columns` (after line 311):

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -k absorb -v`
Expected: FAIL — `test_build_tree_absorbs_unmatched_rows_as_use_cases` and
`test_build_tree_node_can_have_both_children_and_use_cases` raise `ValueError: ... không đọc
được cấp của dòng ...` (current hard-error behavior); `test_build_tree_absorb_without_open_group_errors_clearly`
fails because the error message doesn't match yet (same generic message, not the
stack-empty one). `test_build_tree_unmatched_rows_default_is_error` should already PASS
(it's a regression check for existing behavior) — confirm it does.

- [ ] **Step 3: Implement**

Insert before `_build_leveled` (i.e., right after `_iter_data_rows`, before line 249):

```python
UC_EXTRA_FIELDS = ("importance", "type", "usage_timing")


def _use_case_extra(raw, mapping):
    """Các trường bổ sung (Mức quan trọng/Loại UC/Thời điểm sử dụng) cho một
    dòng use-case — chỉ ghi khi mapping có khai cột VÀ ô đó có giá trị."""
    cols = mapping.get("columns") or {}
    out = {}
    for key in UC_EXTRA_FIELDS:
        col = cols.get(key)
        if col is None:
            continue
        val = _cell(raw, col)
        if val:
            out[key] = val
    return out
```

Replace `speckit-extension/scripts/fnlist_tree.py:249-272` (`_build_leveled`):

```python
def _build_leveled(grid, mapping):
    desc_col = (mapping.get("columns") or {}).get("description")
    roots, skipped, stack = [], [], []
    for rowno, raw in _iter_data_rows(grid, mapping, skipped):
        level, name = _level_and_name(raw, mapping, rowno)
        if not name:
            skipped.append({"row": rowno, "reason": "ô tên chức năng trống",
                            "raw": raw[:6]})
            continue
        if level is None:
            raise ValueError(
                f"Dòng {rowno} ('{name}'): không đọc được cấp của dòng — "
                "kiểm lại khối hierarchy trong mapping.")
        if level > len(stack) + 1:
            raise ValueError(
                f"Dòng {rowno} ('{name}'): nhảy từ cấp {len(stack)} xuống cấp "
                f"{level}. Cấp bậc trong file nguồn không liên tục — sửa file "
                "nguồn hoặc chọn lại kiểu phân cấp.")
        node = {"name": name, "description": _cell(raw, desc_col),
                "children": [], "row": rowno}
        del stack[level - 1:]
        (stack[-1]["children"] if stack else roots).append(node)
        stack.append(node)
    return roots, skipped
```

with:

```python
def _build_leveled(grid, mapping):
    desc_col = (mapping.get("columns") or {}).get("description")
    h = mapping.get("hierarchy") or {}
    unmatched = h.get("unmatched_rows", "error")
    roots, skipped, stack = [], [], []
    for rowno, raw in _iter_data_rows(grid, mapping, skipped):
        level, name = _level_and_name(raw, mapping, rowno)
        if not name:
            skipped.append({"row": rowno, "reason": "ô tên chức năng trống",
                            "raw": raw[:6]})
            continue
        if level is None:
            if unmatched == "absorb":
                if not stack:
                    raise ValueError(
                        f"Dòng {rowno} ('{name}'): không có nhóm cha nào đang "
                        "mở để gắn làm use-case con — kiểm lại dòng đầu file "
                        "nguồn hoặc mapping.")
                stack[-1].setdefault("use_cases", []).append({
                    "name": name, "description": _cell(raw, desc_col),
                    "row": rowno, **_use_case_extra(raw, mapping),
                })
                continue
            raise ValueError(
                f"Dòng {rowno} ('{name}'): không đọc được cấp của dòng — "
                "kiểm lại khối hierarchy trong mapping.")
        if level > len(stack) + 1:
            raise ValueError(
                f"Dòng {rowno} ('{name}'): nhảy từ cấp {len(stack)} xuống cấp "
                f"{level}. Cấp bậc trong file nguồn không liên tục — sửa file "
                "nguồn hoặc chọn lại kiểu phân cấp.")
        node = {"name": name, "description": _cell(raw, desc_col),
                "children": [], "row": rowno}
        del stack[level - 1:]
        (stack[-1]["children"] if stack else roots).append(node)
        stack.append(node)
    return roots, skipped
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -q`
Expected: PASS, all tests green (73 + the new ones from Task 1 and this task).

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist-import): absorb unmatched rows into use_cases[] on the open parent"
```

---

### Task 3: `assign_ids` assigns stable `-UC-nn` IDs to `use_cases`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py:309-358` (`assign_ids`, specifically the
  nested `recurse` function's final loop)
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `use_cases` lists produced by Task 2 (items without `"id"`).
- Produces: after `assign_ids(tree, old_tree=None, retired=())` runs, every `use_cases` item
  has a stable `"id"` of the form `f"{parent_id}-UC-{seq:02d}"`, matched/renumbered by the
  same four rules as FN nodes (§3 of the spec), scoped to the parent node instead of the
  whole tree. `carry_status(new_tree, old_tree)` and `compute_retired(old_tree, new_tree,
  prev_retired)` need **no code change** — they already generalize via `walk()` from Task 1
  — this task adds regression-locking tests for that.

- [ ] **Step 1: Write the failing tests**

Add to `speckit-extension/scripts/tests/test_fnlist_tree.py`, after
`_mk`/`_ids` helpers (after line 321), a small use-case builder helper, then the new tests
— place them after `test_assign_ids_move_plus_insert_same_run_no_id_collision_or_status_leak`
(after line 417):

```python
def _mk_uc(name, description="", **extra):
    d = {"name": name, "description": description}
    d.update(extra)
    return d
```

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -k "use_case" -v`
Expected: FAIL — `assign_ids`-related tests raise `KeyError: 'id'` (use_cases items never get
an `"id"` today); `carry_status`/`compute_retired` tests fail because those use-case items
were never visited by `assign_ids`/`walk` in the first place, so lookups by id come up empty
or raise.

- [ ] **Step 3: Implement**

In `speckit-extension/scripts/fnlist_tree.py`, inside `assign_ids` (around line 336-356),
replace the `recurse` function's final loop:

```python
        seq = 1
        for node in nodes:
            if "id" not in node:
                while (seq in used or f"{prefix}-{seq:02d}" in retired
                       or f"{prefix}-{seq:02d}" in old_ids):
                    seq += 1
                node["id"] = f"{prefix}-{seq:02d}"
                used.add(seq)
            recurse(node["children"], parents + (node,), node["id"])
```

with:

```python
        seq = 1
        for node in nodes:
            if "id" not in node:
                while (seq in used or f"{prefix}-{seq:02d}" in retired
                       or f"{prefix}-{seq:02d}" in old_ids):
                    seq += 1
                node["id"] = f"{prefix}-{seq:02d}"
                used.add(seq)
            if "children" in node:
                recurse(node["children"], parents + (node,), node["id"])
            if node.get("use_cases"):
                recurse(node["use_cases"], parents + (node,), f"{node['id']}-UC")
```

Also update the `assign_ids` docstring — replace:

```python
    """Cấp ID đa cấp, sửa tại chỗ.

    Bốn luật, theo đúng thứ tự ưu tiên:
      1. Node đã có ở bản cũ (khớp theo ĐƯỜNG DẪN TÊN) giữ nguyên ID.
      2. Node mới lấy số nhỏ nhất chưa dùng trong cùng cha.
      3. Số đã khai tử không bao giờ cấp lại — hai tài liệu ở hai thời điểm
         không được trỏ cùng một ID ra hai chức năng khác nhau.
      4. Node đổi cha thì đường dẫn tên đổi theo, nên tự động rơi vào luật 2 và
         nhận ID mới — đây là điểm gãy truy vết duy nhất, `diff_trees` gắn nhãn
         'chuyển nhóm' để người dùng biết mà cập nhật tài liệu cũ.

    Hai node MỚI trùng tên dưới cùng cha: chỉ node gặp trước trong duyệt được
    khớp/tiêu thụ ID cũ theo đường dẫn tên; node trùng tên còn lại rơi vào luật
    2 và nhận số mới — tránh hai chức năng khác nhau đâm chung một ID.
    """
```

with:

```python
    """Cấp ID đa cấp, sửa tại chỗ.

    Bốn luật, theo đúng thứ tự ưu tiên:
      1. Node đã có ở bản cũ (khớp theo ĐƯỜNG DẪN TÊN) giữ nguyên ID.
      2. Node mới lấy số nhỏ nhất chưa dùng trong cùng cha.
      3. Số đã khai tử không bao giờ cấp lại — hai tài liệu ở hai thời điểm
         không được trỏ cùng một ID ra hai chức năng khác nhau.
      4. Node đổi cha thì đường dẫn tên đổi theo, nên tự động rơi vào luật 2 và
         nhận ID mới — đây là điểm gãy truy vết duy nhất, `diff_trees` gắn nhãn
         'chuyển nhóm' để người dùng biết mà cập nhật tài liệu cũ.

    Hai node MỚI trùng tên dưới cùng cha: chỉ node gặp trước trong duyệt được
    khớp/tiêu thụ ID cũ theo đường dẫn tên; node trùng tên còn lại rơi vào luật
    2 và nhận số mới — tránh hai chức năng khác nhau đâm chung một ID.

    `use_cases` trên một node lá dùng LẠI đúng bốn luật trên, chỉ đổi phạm vi
    từ "toàn cây" thành "trong một node cha" — tiền tố ID là `<id-cha>-UC`
    thay vì `FN`.
    """
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -q`
Expected: PASS, all tests green.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist-import): stable UC-nn ids for use_cases via existing assign_ids"
```

---

### Task 4: `clean_node`/`clean_use_case` — final output shape

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py:36-50` (`clean_node`), add
  `clean_use_case` right before it
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `UC_EXTRA_FIELDS` constant from Task 2.
- Produces: `ft.clean_use_case(uc) -> dict` — strips to `id`/`name`/`description` (+
  `status` if not `pending`, + any of `importance`/`type`/`usage_timing` present and
  truthy). `ft.clean_node(node)` now also emits a cleaned `use_cases` key when the node has
  one, omitting it entirely otherwise. `build_document`/`save_document` (unchanged callers)
  pick this up automatically since they call `clean_node` per root.

- [ ] **Step 1: Write the failing tests**

Add to `speckit-extension/scripts/tests/test_fnlist_tree.py`, after
`test_clean_node_fills_missing_description` (after line 56):

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -k clean -v`
Expected: `test_clean_use_case_keeps_only_schema_fields` fails with
`AttributeError: module 'fnlist_tree' has no attribute 'clean_use_case'`;
`test_clean_node_includes_cleaned_use_cases_when_present` fails because `use_cases` is
silently dropped by today's `clean_node`; `test_clean_node_omits_use_cases_key_when_absent`
should already pass (regression check).

- [ ] **Step 3: Implement**

Replace `speckit-extension/scripts/fnlist_tree.py:36-50` (`clean_node`) with:

```python
def clean_use_case(uc):
    """Mục use-case con → đúng schema: id/name/description bắt buộc, status và
    3 trường bổ sung (importance/type/usage_timing) chỉ ghi khi có giá trị
    thật — không có `children` (use-case không lồng cấp con nào cả)."""
    out = {
        "id": uc["id"],
        "name": uc["name"],
        "description": uc.get("description", ""),
    }
    status = uc.get("status")
    if status and status != "pending":
        out["status"] = status
    for key in UC_EXTRA_FIELDS:
        val = uc.get(key)
        if val:
            out[key] = val
    return out


def clean_node(node):
    """Node nội bộ → node đúng schema: chỉ 5 trường (+ `use_cases` nếu có),
    bỏ status mặc định.

    Node lúc dựng cây có mang thêm `row` (số dòng nguồn) để báo cáo; trường đó
    không thuộc schema nên phải rơi lại ở đây, không lọt vào file."""
    out = {
        "id": node["id"],
        "name": node["name"],
        "description": node.get("description", ""),
    }
    status = node.get("status")
    if status and status != "pending":
        out["status"] = status
    out["children"] = [clean_node(c) for c in node.get("children") or []]
    use_cases = node.get("use_cases")
    if use_cases:
        out["use_cases"] = [clean_use_case(u) for u in use_cases]
    return out
```

Note: `UC_EXTRA_FIELDS` is defined earlier in the file (Task 2) — `clean_use_case` reuses it
directly, no new constant needed. `clean_use_case` must be defined **before** `clean_node` in
the file only because that matches the existing top-to-bottom reading order (helper before
its caller-adjacent sibling); Python doesn't require the ordering since both are
module-level, but keep it for readability.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -q`
Expected: PASS, all tests green.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist-import): clean_node emits use_cases with schema-only fields"
```

---

### Task 5: `diff_trees` reports use-case changes under separate labels

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py:378-408` (`diff_trees`), add
  `_diff_leaves` helper right before it
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `is_use_case` from Task 1.
- Produces: `ft.diff_trees(old_tree, new_tree)` return value gains entries with
  `loai` in `{"use-case thêm", "use-case bỏ", "use-case đổi mô tả"}` for changes inside
  `use_cases`, on top of the existing `{"thêm", "bỏ", "đổi mô tả", "chuyển nhóm"}` for FN
  nodes. Use-case entries are **not** run through `_merge_moves` (no "use-case chuyển nhóm"
  label this phase — see spec "Ngoài phạm vi"). `_merge_moves` itself is unchanged.

- [ ] **Step 1: Write the failing tests**

Add to `speckit-extension/scripts/tests/test_fnlist_tree.py`, after
`test_diff_move_without_description_change_has_no_extra_keys` (after line 510):

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -k "diff_reports_use_case" -v`
Expected: FAIL — today's `diff_trees` only compares nodes where `not n.get("children")`,
which use-case items also satisfy (they have no `"children"` key), so they currently get
mixed in under the **FN** labels `"thêm"`/`"bỏ"`/`"đổi mô tả"` instead of the new
`"use-case ..."` ones — the assertions on exact label strings fail.

- [ ] **Step 3: Implement**

Insert before `diff_trees` (before line 378), a shared helper:

```python
def _diff_leaves(old_leaf, new_leaf, old_all_paths, new_all_paths,
                  added, removed, changed):
    """So một tầng lá (FN hoặc use-case) giữa hai cây — dùng chung logic
    thêm/bớt/đổi mô tả, chỉ khác nhãn `loai` truyền vào."""
    out = []
    for path, node in new_leaf.items():
        old = old_leaf.get(path)
        if old is None:
            if path not in old_all_paths:
                out.append({"loai": added, "id": node["id"], "ten": path[-1],
                            "duong_dan": " / ".join(path), "_node": node})
        elif (old.get("description") or "") != (node.get("description") or ""):
            out.append({"loai": changed, "id": node["id"], "ten": path[-1],
                        "cu": old.get("description", ""),
                        "moi": node.get("description", "")})
    for path, old in old_leaf.items():
        if path not in new_leaf and path not in new_all_paths:
            out.append({"loai": removed, "id": old["id"], "ten": path[-1],
                        "duong_dan": " / ".join(path), "_node": old})
    return out
```

Replace `speckit-extension/scripts/fnlist_tree.py:378-408` (`diff_trees` body — keep its
existing docstring's first two paragraphs, extend with the note below) with:

```python
def diff_trees(old_tree, new_tree):
    """So hai cây theo đường dẫn tên. Gọi SAU assign_ids trên cả hai cây.

    Chỉ so node lá (không có con) — đó mới là "chức năng" thật; node nhóm chỉ
    là tiêu đề tổ chức, nhóm biến mất/xuất hiện do các lá bên trong đổi chỗ
    không phải là một thay đổi chức năng độc lập cần báo cáo.

    So RIÊNG hai tầng: node lá FN và mục use-case con — nhãn khác nhau
    (`"use-case thêm"`/`"use-case bỏ"`/`"use-case đổi mô tả"`) để người đọc
    không lẫn "chức năng thêm/bớt" với "use-case con bên trong một chức năng
    không đổi". Use-case KHÔNG chạy qua `_merge_moves` (không có nhãn
    "use-case chuyển nhóm" ở đợt này — xem spec "Ngoài phạm vi").

    Một node đổi trạng thái lá giữa hai lần import (từ có con → hết con, hoặc
    ngược lại) không phải là "bỏ"/"thêm" thật — node đó vẫn tồn tại, chỉ đổi
    vai trò. Vì vậy trước khi báo "bỏ"/"thêm" phải kiểm đường dẫn đó có mặt ở
    TOÀN BỘ cây bên kia không (kể cả node không phải lá), có thì bỏ qua."""
    old_all_paths = {name_path(n, p) for n, p in walk(old_tree or [])}
    new_all_paths = {name_path(n, p) for n, p in walk(new_tree)}

    old_fn_leaf = {name_path(n, p): n for n, p in walk(old_tree or [])
                   if not is_use_case(n) and not n["children"]}
    new_fn_leaf = {name_path(n, p): n for n, p in walk(new_tree)
                   if not is_use_case(n) and not n["children"]}
    fn_entries = _diff_leaves(old_fn_leaf, new_fn_leaf, old_all_paths,
                               new_all_paths, "thêm", "bỏ", "đổi mô tả")

    old_uc = {name_path(n, p): n for n, p in walk(old_tree or []) if is_use_case(n)}
    new_uc = {name_path(n, p): n for n, p in walk(new_tree) if is_use_case(n)}
    uc_entries = _diff_leaves(old_uc, new_uc, old_all_paths, new_all_paths,
                              "use-case thêm", "use-case bỏ", "use-case đổi mô tả")

    return _merge_moves(fn_entries) + [
        {k: v for k, v in e.items() if k != "_node"} for e in uc_entries]
```

Note the `and`-short-circuit in `not is_use_case(n) and not n["children"]`: when
`is_use_case(n)` is `True` (no `"children"` key), `not is_use_case(n)` is `False` and Python
never evaluates `n["children"]` — no `KeyError` on use-case items.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -q`
Expected: PASS, all tests green — including every pre-existing `test_diff_*` test
(`test_diff_reports_added_and_removed`, `test_diff_labels_move_between_parents`, etc.),
confirming the FN-level diff path is byte-for-byte unchanged.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist-import): diff_trees reports use-case changes under separate labels"
```

---

### Task 6: `fnlist_import.py` report splits `written`/`written_use_cases`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_import.py:155-160` (inside `cmd_write`)
- Test: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: `ft.is_use_case` from Task 1.
- Produces: `write` report JSON gains `"written_use_cases": <int>`; `"written"` now counts
  only FN tree nodes (was: all nodes via bare `walk()`, which today is the same number since
  no use_cases existed — this task's fixture is the first to exercise the split).

- [ ] **Step 1: Write the failing test**

Add to `speckit-extension/scripts/tests/test_fnlist_import.py`, after
`test_write_second_run_keeps_ids_status_and_reports_diff` (after line 137):

```python
GRID_WITH_CONTENT = [
    ["STT", "Tên chức năng", "Mô tả", "Mức quan trọng"],
    ["1", "Quản lý đơn hàng", "", ""],
    ["1.1", "Danh sách đơn", "", ""],
    ["uc001", "Xem đơn", "Xem chi tiết đơn", "Cao"],
    ["uc002", "Tìm đơn", "Tìm theo mã", ""],
    ["1.2", "Tạo đơn mới", "Điền form tạo đơn", ""],
]

MAPPING_ABSORB = {"first_data_row": 1,
                  "columns": {"name": 1, "description": 2, "importance": 3},
                  "hierarchy": {"mode": "outline", "column": 0,
                                "unmatched_rows": "absorb"}}


def test_write_reports_written_use_cases_separately(tmp_path, capsys):
    out = run_write(tmp_path, rows=GRID_WITH_CONTENT, mapping=MAPPING_ABSORB)
    report = json.loads(capsys.readouterr().out)
    assert report["written"] == 3            # FN-01, FN-01-01, FN-01-02
    assert report["written_use_cases"] == 2   # 2 use-case gộp trong FN-01-01
    doc = json.loads(out.read_text(encoding="utf-8"))
    la = doc["functions"][0]["children"][0]
    assert la["use_cases"][0]["importance"] == "Cao"
    assert "importance" not in la["use_cases"][1]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -k written_use_cases -v`
Expected: FAIL with `KeyError: 'written_use_cases'` — the report doesn't have this key yet.

- [ ] **Step 3: Implement**

In `speckit-extension/scripts/fnlist_import.py`, inside `cmd_write` (around line 155-160),
replace:

```python
    report = {
        "out": str(out),
        "written": sum(1 for _ in ft.walk(tree)),
        "skipped": skipped,
        "retired": retired,
    }
```

with:

```python
    report = {
        "out": str(out),
        "written": sum(1 for n, _ in ft.walk(tree) if not ft.is_use_case(n)),
        "written_use_cases": sum(1 for n, _ in ft.walk(tree) if ft.is_use_case(n)),
        "skipped": skipped,
        "retired": retired,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -q`
Expected: PASS, all tests green (existing `test_write_report_counts_written_and_skipped`
still asserts `report["written"] == 4` with plain no-use-case data — unaffected since
`written_use_cases` would be `0` there and isn't checked by that test).

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist-import): report written_use_cases separately from written"
```

---

### Task 7: Update `commands/fnlist-import.md` and `references/functions-schema.md`

**Files:**
- Modify: `speckit-extension/commands/fnlist-import.md`
- Modify: `speckit-extension/references/functions-schema.md`

**Interfaces:** None (prompt/doc content only, no code).

This task has no automated test — verification is a manual read-through against the spec's
§"Phần 3" / §4-6, checked in Step 2 below.

- [ ] **Step 1a: Edit `commands/fnlist-import.md` — mapping.json examples (step 2)**

Find the block (currently around line 103-119):

```
Ghi ánh xạ đã chốt ra `.specify/tmp/fnlist/mapping.json`:

```json
{
  "first_data_row": 1,
  "columns": { "name": 1, "description": 2 },
  "hierarchy": { "mode": "outline", "column": 0 },
  "skip_rows": []
}
```

Với `mode: "columns"` thì khai `level_columns` + `style` thay cho `column`, và **bỏ hẳn
`columns.name`** (tên lấy từ cột cấp sâu nhất có giá trị trên dòng đó):

```json
{ "hierarchy": { "mode": "columns", "level_columns": [0, 1, 2], "style": "staircase" } }
```
```

Insert a new paragraph + example right after that (before the `skip_rows` explanation
paragraph that currently follows):

```markdown
Gặp file mà mã phân cấp chỉ đánh ở dòng tiêu đề nhóm, còn dòng nội dung (từng use-case,
từng giao dịch cụ thể) không mang mã nào — dòng nội dung đó không phải lỗi, nó gộp thành
một mục trong `use_cases` của nhóm cha gần nhất đang mở. Khai `unmatched_rows: "absorb"`
trong khối `hierarchy`:

```json
{
  "first_data_row": 1,
  "columns": { "name": 1, "description": 2, "importance": 3 },
  "hierarchy": { "mode": "outline", "column": 0, "unmatched_rows": "absorb" },
  "skip_rows": []
}
```

Mặc định (`unmatched_rows` vắng mặt) là `"error"` — dòng không đọc được cấp vẫn dừng cứng
như trước, dùng cho file mà MỌI dòng đều tự khai cấp. Ba khoá tuỳ chọn khác trong `columns`
— `importance` (Mức quan trọng), `type` (Loại UC), `usage_timing` (Thời điểm sử dụng) —
chỉ khai khi sheet thật sự có cột tương ứng; xem mục dưới đây về cách hỏi.
```

- [ ] **Step 1b: Edit `commands/fnlist-import.md` — new mandatory-ask situation (step 2)**

Find the block (currently around line 91-101):

```
Ba tình huống sau cũng **bắt buộc hỏi**, không tự chọn — **không chắc một tình huống có
thuộc nhóm này hay không thì coi như thuộc**, mặc định là hỏi:

- **Nhiều sheet** — sheet nào là function list thật (không phải sheet ghi chú/phụ lục).
- **Header hai tầng** — vd dòng 0 có ô trống xen kẽ (chỉ vài cột lớn có chữ) và dòng 1
  mới điền đủ nhãn con cho từng cột. Phân biệt với **header một tầng nhưng tên cột dài**
  (dòng 0 mọi ô đều có chữ, chỉ là "Mô tả chi tiết chức năng" thay vì "Mô tả") — trường
  hợp sau KHÔNG cần hỏi, tự chọn `first_data_row` = 1 là đủ.
- **Cột mô tả mơ hồ** — không chắc cột nào là mô tả chức năng hay chỉ là ghi chú/trạng thái.

Mỗi lượt AskUserQuestion gom 1–4 câu độc lập nhau.
```

Replace with (adds a 4th situation and renumbers "Ba" → "Bốn"):

```markdown
Bốn tình huống sau cũng **bắt buộc hỏi**, không tự chọn — **không chắc một tình huống có
thuộc nhóm này hay không thì coi như thuộc**, mặc định là hỏi:

- **Nhiều sheet** — sheet nào là function list thật (không phải sheet ghi chú/phụ lục).
- **Header hai tầng** — vd dòng 0 có ô trống xen kẽ (chỉ vài cột lớn có chữ) và dòng 1
  mới điền đủ nhãn con cho từng cột. Phân biệt với **header một tầng nhưng tên cột dài**
  (dòng 0 mọi ô đều có chữ, chỉ là "Mô tả chi tiết chức năng" thay vì "Mô tả") — trường
  hợp sau KHÔNG cần hỏi, tự chọn `first_data_row` = 1 là đủ.
- **Cột mô tả mơ hồ** — không chắc cột nào là mô tả chức năng hay chỉ là ghi chú/trạng thái.
- **Có dòng không khớp kiểu phân cấp đã chọn** — hỏi đây có phải "dòng nội dung", gộp vào
  nhóm cha làm use-case con (`unmatched_rows: "absorb"`), hay đó thật ra là lỗi cấu trúc
  file (thiếu mã phân cấp ở một dòng đáng ra phải là nhóm) cần người dùng sửa nguồn trước
  khi import tiếp. Không tự suy luận theo hướng nào — hai khả năng đều hợp lý và hậu quả
  chọn sai khác nhau hoàn toàn (một bên mất use-case thật, một bên nuốt nhầm lỗi nhập liệu).

Mỗi lượt AskUserQuestion gom 1–4 câu độc lập nhau.

Sau khi chốt cột `name`/`description`/hierarchy, **quét nốt các cột còn lại** trong `head`
đã in ở bước 1 (không giới hạn ở cột đã dùng) và hỏi có cột nào khớp 1 trong 3 loại: Mức
quan trọng use case, Loại UC, Thời điểm sử dụng UC. Đây là thông tin nghiệp vụ thuần mà
không giai đoạn nào sau này của đường ống (đọc code) suy ra lại được — bỏ qua ở đây là mất
vĩnh viễn, không có cơ hội thứ hai. Không tự đoán tên cột khớp nghĩa gì — `inspect` đã in
header + N dòng đầu cho mọi cột, việc còn lại là đọc và hỏi xác nhận qua AskUserQuestion,
không cần thuật toán chấm điểm nào (khác với hierarchy — đây là phân loại ngữ nghĩa tên
cột, không phải pattern đếm được).
```

- [ ] **Step 1c: Edit `commands/fnlist-import.md` — checkpoint cây (step 3)**

Find the paragraph (currently around line 128-133):

```
**Không được bỏ qua bước này dù cảm thấy ánh xạ đã "rõ ràng".** Tự render **cây 5 dòng
dữ liệu đầu** theo ánh xạ đã chọn, thụt lề theo cấp:

```
Quản lý đơn hàng
  Danh sách đơn — Xem, tìm kiếm đơn hàng
    Lọc theo trạng thái
  Tạo đơn mới
Quản lý khách hàng
```
```

Replace with:

```markdown
**Không được bỏ qua bước này dù cảm thấy ánh xạ đã "rõ ràng".** Tự render **cây 5 dòng
dữ liệu đầu** theo ánh xạ đã chọn, thụt lề theo cấp. Node lá có use-case con (khi
`unmatched_rows: "absorb"`) thì in thêm các dòng con thụt sâu hơn, đánh dấu bằng `·` để
phân biệt trực quan với nhóm/lá:

```
Quản lý đơn hàng
  Danh sách đơn — Xem, tìm kiếm đơn hàng
    · Xem đơn — Xem chi tiết đơn (Mức quan trọng: Cao)
    · Tìm đơn — Tìm theo mã
  Tạo đơn mới
Quản lý khách hàng
```

Đây là đúng chỗ dễ sai nhất của trường hợp gộp use-case: gộp nhầm nhiều use-case khác nhau
thành một, hoặc ngược lại tách nhầm một use-case thành nhiều node lá. Cây có `·` phải cho
người dùng thấy rõ NHÓM nào gộp bao nhiêu use-case.
```

- [ ] **Step 1d: Edit `commands/fnlist-import.md` — report bước 5**

Find the paragraph right after the write command block (currently around line 172-174):

```
Script in báo cáo JSON ra stdout: `out`, `written`, `skipped`, `retired`, và (chạy lại
trên file đã có) `diff`.
```

Replace with:

```markdown
Script in báo cáo JSON ra stdout: `out`, `written` (số node cây FN), `written_use_cases`
(số use-case đã gộp — có thể lớn hơn nhiều `written` nếu phần lớn dữ liệu là dòng nội
dung), `skipped`, `retired`, và (chạy lại trên file đã có) `diff`. Đọc cả hai con số —
`written` nhỏ không có nghĩa là thiếu dữ liệu nếu `written_use_cases` bù lại đủ.
```

- [ ] **Step 1e: Edit `commands/fnlist-import.md` — diff bước 6**

Find the bullet list of 4 diff types (currently around line 205-215, the `thêm`/`bỏ`/`đổi
mô tả`/`chuyển nhóm` list) and append one bullet right after it, before the "Đổi tên chức
năng hiện ra..." paragraph:

```markdown
- `use-case thêm` / `use-case bỏ` / `use-case đổi mô tả` — cùng ý nghĩa như trên nhưng cho
  một use-case con BÊN TRONG một node lá không đổi, tách nhãn riêng để không lẫn với thay
  đổi ở cấp chức năng. Không có `use-case chuyển nhóm` — use-case đổi node cha hiện ra như
  một cặp `use-case bỏ` + `use-case thêm` rời rạc, không gộp.
```

- [ ] **Step 1f: Edit `commands/fnlist-import.md` — "Sai lầm thường gặp"**

Append these bullets to the end of the existing list (after the last bullet, "Sửa tay
`functions.json`..."):

```markdown
- **Coi dòng nội dung là lỗi cấu trúc khi thật ra file cố ý phân tầng kiểu "chỉ nhóm có
  mã"** → chọn `unmatched_rows: "error"` sai, dừng nhầm một file hợp lệ.
- **Ngược lại: chọn `"absorb"` cho một file mà dòng không khớp cấp thật sự là lỗi nhập
  liệu** → nuốt luôn dòng lỗi vào làm use-case, không ai phát hiện.
- **Bỏ qua quét cột bổ sung (Mức quan trọng/Loại UC/Thời điểm sử dụng)** → thông tin có sẵn
  trong Excel nhưng không bao giờ được hỏi, xuống `srs-from-code` lại thành "Chưa có thông
  tin" — đúng lỗ hổng đang sửa.
- **Trình checkpoint cây bước 3 mà không hiện use-case con** → giấu đúng chỗ dễ sai nhất
  của trường hợp gộp.
```

- [ ] **Step 2a: Edit `references/functions-schema.md` — add `use_cases` section**

Find the block ending with (currently around line 76-82):

```
**Không có `level`, `outline`, `parent`.** Cấp bậc đọc từ độ sâu lồng của
`children`; số mục lục kiểu `1.2.3` suy từ vị trí trong mảng.

**`diff` của lệnh `write` chỉ so sánh node lá (`children` rỗng).** Thay đổi tên/mô tả,
thêm, hoặc xoá một node có con (nhóm cấp cao) không hiện trong `diff` — chỉ các thay đổi
ở node lá mới được báo cáo.

## Quy tắc ID
```

Insert a new section between the `diff` paragraph and `## Quy tắc ID`:

```markdown
## `use_cases` — use-case con trong node lá

Một node lá có thể gộp nhiều dòng nội dung (use-case, giao dịch cụ thể — không tự khai cấp
riêng trong file nguồn) thành mảng `use_cases`. **Vắng mặt** ở node không có dòng nội dung
nào; một node có thể vừa có `children` vừa có `use_cases`.

```json
{
  "id": "FN-01-01",
  "name": "Nhóm chức năng Quản trị hệ thống và Người dùng",
  "description": "",
  "children": [],
  "use_cases": [
    {
      "id": "FN-01-01-UC-01",
      "name": "Quản lý danh sách người dùng",
      "description": "1. Quản trị hệ thống thao tác tạo mới...",
      "importance": "",
      "type": "",
      "usage_timing": ""
    }
  ]
}
```

Trường của một mục `use_cases`:

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | string | `<id-node-cha>-UC-nn`, xem quy tắc ID bên dưới. |
| `name` | string | Tên use-case, nguyên văn ô nguồn. |
| `description` | string | Mô tả, nguyên văn ô nguồn. Không có thì `""`. |
| `status` | string | Giống `status` của node FN. Vắng mặt = `pending`. |
| `importance` | string | Mức quan trọng — chỉ ghi khi file nguồn có cột này. |
| `type` | string | Loại UC theo quy ước BA — chỉ ghi khi file nguồn có cột này. |
| `usage_timing` | string | Thời điểm sử dụng — chỉ ghi khi file nguồn có cột này. |

`importance`/`type`/`usage_timing` vắng mặt hoàn toàn (không ghi `""`) khi mapping không
khai cột tương ứng hoặc ô nguồn trống.

`diff` của lệnh `write` cũng so sánh `use_cases` — dưới nhãn riêng `use-case thêm`/
`use-case bỏ`/`use-case đổi mô tả`, tách khỏi diff cấp node FN.

## Quy tắc ID
```

- [ ] **Step 2b: Edit `references/functions-schema.md` — extend "Quy tắc ID" section**

Find the end of the ID rules list (currently around line 83-98, ending with rule 5 about
"Node đổi nhóm cha... Đây là điểm gãy truy vết duy nhất"). Append immediately after that
paragraph, before `## Đọc và ghi`:

```markdown
`use_cases` dùng LẠI đúng 5 luật trên, chỉ đổi phạm vi: đánh số/khớp lại theo **đường dẫn
tên trong phạm vi node cha** (không phải toàn cây), tiền tố ID là `<id-cha>-UC` thay vì
`FN`. Không dùng thẳng mã use-case trong file nguồn (nếu có, ví dụ `uc001`) làm `id` — mã
đó do người nhập tay, không đảm bảo ổn định giữa các lần sửa file nguồn.
```

- [ ] **Step 3: Manual verification**

Re-read both edited files top to bottom, checking against
`docs/superpowers/specs/2026-08-18-fnlist-import-content-rows-design.md` §4-6 and the
"Sai lầm thường gặp" list: every new mapping key (`unmatched_rows`, `importance`, `type`,
`usage_timing`), every new mandatory-ask situation, and every schema field must appear in
both the command and the schema doc with consistent field names. Confirm no stray
`{CORE_TEMPLATE}` token or broken Markdown (unclosed code fence) was introduced — run:

```bash
grep -c '```' speckit-extension/commands/fnlist-import.md speckit-extension/references/functions-schema.md
```

Expected: an even count in both files (every fence opened is closed).

- [ ] **Step 4: Commit**

```bash
git add speckit-extension/commands/fnlist-import.md speckit-extension/references/functions-schema.md
git commit -m "docs(fnlist-import): document unmatched_rows absorb + use_cases + extra BA columns"
```

---

### Task 8: Full regression run + smoke test against the real `Fnclist.xlsx`

**Files:** none modified — verification only.

- [ ] **Step 1: Run the full test suite for the touched files**

```bash
python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_import.py -v
```

Expected: PASS, every test (pre-existing + all added in Tasks 1-6) green. Count should be
73 (baseline) + roughly 20 new tests.

- [ ] **Step 2: Smoke-test against the real `Fnclist.xlsx` that motivated this fix**

The file lives at repo root (`e:\agent-skills\Fnclist.xlsx`, sheet `UC`). Use a Python-managed
temp directory (portable, outside the repo, no `/tmp` hardcoding) to hold the scratch mapping
and output, then run `write` end-to-end — this is the exact scenario that crashed before
Task 2:

```bash
SCRATCH=$(python -c "import tempfile; print(tempfile.mkdtemp())")
python - "$SCRATCH" <<'PY'
import json, pathlib, sys
mapping = {
    "first_data_row": 1,
    "columns": {"name": 1, "description": 3},
    "hierarchy": {"mode": "outline", "column": 0, "unmatched_rows": "absorb"},
}
(pathlib.Path(sys.argv[1]) / "mapping.json").write_text(json.dumps(mapping), encoding="utf-8")
PY
python speckit-extension/scripts/fnlist_import.py write "Fnclist.xlsx" \
  --mapping "$SCRATCH/mapping.json" \
  --out "$SCRATCH/functions.json" \
  --system "DMS/Chatbot AI/Dịch chuyên ngành" \
  --date 2026-08-18 \
  --sheet "UC"
```

Expected: exits 0, prints a JSON report with `written` around 30 (group nodes) and
`written_use_cases` around 112 (the `uc001`-`uc112` rows), `skipped` empty or near-empty.

- [ ] **Step 3: Spot-check the output shape**

```bash
python -c "
import json
doc = json.load(open('$SCRATCH/functions.json', encoding='utf-8'))
fn01 = doc['functions'][0]
grp = fn01['children'][0]
print(grp['id'], grp['name'], len(grp.get('use_cases', [])))
print([u['id'] for u in grp.get('use_cases', [])][:2])
"
```

Expected: prints `FN-01-01 Nhóm chức năng Quản trị hệ thống và Người dùng 4` (4 use-cases:
`uc001`-`uc004`) and `['FN-01-01-UC-01', 'FN-01-01-UC-02']`. This confirms the exact
`Fnclist.xlsx` shape from the design doc's investigation now imports cleanly instead of
raising `ValueError`.

- [ ] **Step 4: Clean up the scratch directory**

```bash
rm -rf "$SCRATCH"
```

No commit for this task — it's verification only, confirming Tasks 1-7 together close the
original bug report.
