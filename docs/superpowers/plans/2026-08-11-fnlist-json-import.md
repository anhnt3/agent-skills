# `fnlist-import` → `functions.json` — Implementation Plan (đợt 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đổi `fnlist-import` từ sinh bảng markdown phẳng `functions.md` sang sinh cây `functions.json` có ID đa cấp ổn định, với toàn bộ thao tác ghi nằm trong script Python.

**Architecture:** Tách logic thuần (dựng cây, dò kiểu phân cấp, cấp ID, so khác biệt) ra `fnlist_tree.py` để test độc lập; `fnlist_import.py` giữ vai CLI + I/O + bootstrap venv, có ba subcommand `inspect` / `write` / `update`. Đặc tả schema đặt ở `references/functions-schema.md` cho cả ba lệnh của extension cùng trỏ tới.

**Tech Stack:** Python 3 (stdlib), `openpyxl` (chỉ khi đọc `.xlsx`, script tự bootstrap venv), pytest.

**Spec:** `docs/superpowers/specs/2026-08-11-fnlist-json-design.md`

## Global Constraints

- Chỉ làm `fnlist-import`. **Không sửa** `commands/code-intel.md`, `commands/srs-from-code.md`, `scripts/srs_verify.py` trong đợt này.
- Nội dung tài liệu, thông điệp lỗi, comment code: **tiếng Việt**. Key JSON, giá trị `status`, tên hàm, flag CLI: **tiếng Anh**.
- Phụ thuộc ngoài stdlib duy nhất: `openpyxl`. Không thêm `jsonschema` hay thư viện nào khác.
- Node `functions.json` có **đúng 5 trường**: `id`, `name`, `description`, `status`, `children`. `status` bằng `pending` thì **bỏ hẳn khỏi JSON** (vắng mặt = `pending`).
- `status` chỉ nhận: `pending`, `intel`, `srs`.
- ID dạng `FN-01`, `FN-01-01`, `FN-01-01-01` — mỗi cấp hai chữ số, nối bằng `-`.
- Hệ đếm: `first_data_row`, `columns.*`, `hierarchy.column`, `hierarchy.level_columns` là **0-based**; `skip_rows` là **1-based**.
- Script là **thứ duy nhất ghi** `functions.json`. Mọi lỗi → `SystemExit` với thông điệp tiếng Việt, không ghi file dở dang.
- `name` và `description` chép **nguyên văn** ô nguồn, không tóm tắt/chuẩn hoá.
- Chạy test: `python -m pytest speckit-extension/scripts/tests/<file> -v` từ gốc repo.

## File Structure

| File | Trách nhiệm |
|---|---|
| `speckit-extension/scripts/fnlist_tree.py` | **Mới.** Logic thuần: duyệt cây, dò kiểu phân cấp, dựng cây từ lưới ô, cấp ID, khai tử ID, so khác biệt, dọn node trước khi ghi. Không I/O, không `print`. |
| `speckit-extension/scripts/fnlist_import.py` | **Sửa lớn.** CLI + đọc `.xlsx/.csv` + đọc/ghi JSON + bootstrap venv. Gỡ toàn bộ phần render markdown. |
| `speckit-extension/scripts/tests/test_fnlist_tree.py` | **Mới.** Test logic thuần. |
| `speckit-extension/scripts/tests/test_fnlist_import.py` | **Viết lại.** Test CLI/IO. |
| `speckit-extension/references/functions-schema.md` | **Mới.** Đặc tả schema `functions.json`. |
| `speckit-extension/commands/fnlist-import.md` | **Viết lại.** Quy trình theo 3 subcommand mới. |
| `speckit-extension/extension.yml` | Sửa `description` của command, bump version. |

---

### Task 1: Bộ khung `fnlist_tree.py` — duyệt cây và dọn node

**Files:**
- Create: `speckit-extension/scripts/fnlist_tree.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: (không có — task đầu tiên)
- Produces:
  - `STATUSES: tuple[str, ...]` = `("pending", "intel", "srs")`
  - `ID_RE: re.Pattern` khớp `FN-01`, `FN-01-02`, …
  - `walk(nodes: list[dict], parents: tuple = ()) -> Iterator[tuple[dict, tuple]]` — pre-order, trả `(node, tuple các node cha từ gốc)`
  - `name_path(node: dict, parents: tuple) -> tuple[str, ...]`
  - `find_by_id(nodes: list[dict], fid: str) -> dict | None`
  - `clean_node(node: dict) -> dict` — chỉ giữ 5 trường, bỏ `status == "pending"`
  - `build_document(tree: list[dict], system: str, source_file: str, sheet: str, updated: str, retired: list[str]) -> dict`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_fnlist_tree.py`:

```python
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


def test_walk_is_pre_order():
    assert [n["id"] for n, _ in ft.walk(TREE)] == [
        "FN-01", "FN-01-01", "FN-01-01-01", "FN-01-02", "FN-02"]


def test_walk_reports_ancestors():
    by_id = {n["id"]: parents for n, parents in ft.walk(TREE)}
    assert [p["id"] for p in by_id["FN-01-01-01"]] == ["FN-01", "FN-01-01"]
    assert by_id["FN-01"] == ()


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


def test_clean_node_fills_missing_description():
    out = ft.clean_node({"id": "FN-01", "name": "A", "children": []})
    assert out["description"] == ""


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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'fnlist_tree'`

- [ ] **Step 3: Viết `fnlist_tree.py` tối thiểu cho test pass**

Tạo `speckit-extension/scripts/fnlist_tree.py`:

```python
#!/usr/bin/env python3
"""Cây danh mục chức năng: dựng từ lưới ô, cấp ID đa cấp, so khác biệt.

Thuần logic — không đọc/ghi file, không in ra stdout. `fnlist_import.py` lo
phần I/O và CLI. Tách ra vì đây là phần dễ sai âm thầm nhất (dựng cây từ bảng
phẳng, cấp ID ổn định) và cần test được độc lập với Excel.
"""
from __future__ import annotations

import re

STATUSES = ("pending", "intel", "srs")
ID_RE = re.compile(r"^FN(?:-\d{2})+$")


def walk(nodes, parents=()):
    """Duyệt pre-order — đúng thứ tự dòng của file nguồn. Trả (node, tuple cha)."""
    for node in nodes:
        yield node, parents
        yield from walk(node.get("children") or [], parents + (node,))


def name_path(node, parents):
    """Đường dẫn tên từ gốc xuống. Đây là khoá khớp cũ↔mới khi cấp lại ID —
    dùng tên đơn thì hai chức năng cùng tên ở hai nhóm sẽ tranh ID nhau."""
    return tuple(p["name"] for p in parents) + (node["name"],)


def find_by_id(nodes, fid):
    for node, _ in walk(nodes):
        if node.get("id") == fid:
            return node
    return None


def clean_node(node):
    """Node nội bộ → node đúng schema: chỉ 5 trường, bỏ status mặc định.

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
    return out


def build_document(tree, system, source_file, sheet, updated, retired):
    return {
        "schema_version": 1,
        "system": system,
        "source": {"file": source_file, "sheet": sheet},
        "updated": updated,
        "retired_ids": sorted(retired),
        "functions": [clean_node(n) for n in tree],
    }
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist): bộ khung cây danh mục chức năng — walk/name_path/clean_node"
```

---

### Task 2: Dò kiểu phân cấp (`detect_hierarchy`)

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py` (thêm vào cuối)
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py` (thêm vào cuối)

**Interfaces:**
- Consumes: (không dùng gì từ Task 1)
- Produces:
  - `OUTLINE_RE: re.Pattern`
  - `detect_hierarchy(grid: list[list[str]], first_data_row: int) -> list[dict]` — trả danh sách ứng viên sắp giảm dần theo `score`. Mỗi ứng viên: `{"mode": "outline"|"level"|"columns", "score": float, "evidence": str}` cộng `"column": int` (mode `outline`/`level`) hoặc `"level_columns": list[int]` + `"style": "staircase"|"repeated"` (mode `columns`).

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_fnlist_tree.py`:

```python
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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v -k detect`
Expected: FAIL — `AttributeError: module 'fnlist_tree' has no attribute 'detect_hierarchy'`

- [ ] **Step 3: Cài đặt**

Thêm vào cuối `fnlist_tree.py`:

```python
OUTLINE_RE = re.compile(r"^\d+(?:\.\d+)*\.?$")


def _column_cells(grid, col, first_data_row):
    return [(row[col] if col < len(row) else "") for row in grid[first_data_row:]]


def detect_hierarchy(grid, first_data_row):
    """Chấm điểm cả ba kiểu phân cấp, trả ứng viên giảm dần theo score.

    Hàm này KHÔNG quyết thay người dùng — điểm số và bằng chứng chỉ để LLM
    trình ra hỏi. Trả rỗng nghĩa là không thấy dấu hiệu phân cấp nào (danh sách
    phẳng một cấp), cũng vẫn phải hỏi chứ không mặc nhiên coi là phẳng."""
    ncols = max((len(r) for r in grid), default=0)
    out = []
    for col in range(ncols):
        cells = [c for c in _column_cells(grid, col, first_data_row) if c]
        if not cells:
            continue
        codes = [c for c in cells if OUTLINE_RE.match(c)]
        depth = max((c.rstrip(".").count(".") + 1 for c in codes), default=0)
        if len(codes) / len(cells) >= 0.8 and depth >= 2:
            out.append({
                "mode": "outline", "column": col,
                "score": round(len(codes) / len(cells), 2),
                "evidence": (f"cột {col}: {len(codes)}/{len(cells)} ô dạng số mục lục "
                             f"(1.2.3), sâu nhất {depth} cấp"),
            })
        nums = [c for c in cells if c.isdigit() and 1 <= int(c) <= 4]
        distinct = sorted({int(c) for c in nums})
        # `len(nums) > len(distinct)` loại cột STT thuần: 1,2,3 không lặp lại
        # giá trị nào, còn cột cấp thật thì cấp 1 phải xuất hiện nhiều lần.
        if (len(nums) == len(cells) and len(distinct) >= 2 and distinct[0] == 1
                and len(nums) > len(distinct)):
            out.append({
                "mode": "level", "column": col, "score": 0.95,
                "evidence": (f"cột {col}: mọi ô là số 1..4, có {len(distinct)} cấp "
                             f"khác nhau {distinct}"),
            })
    out.extend(_detect_column_runs(grid, first_data_row, ncols))
    return sorted(out, key=lambda c: -c["score"])


def _has_grouping(rows, cols):
    """Kiểu 'repeated' đòi cột cha thật sự gom nhóm — giá trị phải lặp lại ở
    nhiều dòng. Không có luật này thì một danh sách phẳng hai cột
    (Tên chức năng | Mô tả) trông y hệt kiểu repeated, vì dòng nào cũng điền đủ
    cả hai cột."""
    for col in cols[:-1]:
        values = [(r[col] if col < len(r) else "") for r in rows]
        if len(set(values)) >= len(values):
            return False
    return True


def _detect_column_runs(grid, first_data_row, ncols):
    """Kiểu 'mỗi cấp một cột'. Hai style khác nhau về cách dựng cây:

      staircase — mỗi dòng chỉ điền ĐÚNG MỘT cột cấp (kiểu bậc thang)
      repeated  — mỗi dòng điền ĐỦ mọi cột cấp (tên cha lặp lại từng dòng)

    Chỉ xét các dải cột chữ liền nhau, dài ≥2. Cột mô tả cũng là cột chữ nên có
    thể lọt vào dải — vòng lặp thu ngắn dải từ dài xuống ngắn và nhận dải đầu
    tiên khớp thuần một style, nên [Nhóm, Chức năng, Mô tả] sẽ rụng xuống còn
    [Nhóm, Chức năng]. Đây chính là chỗ dò có thể sai, nên LLM luôn phải hỏi lại."""
    rows = [r for r in grid[first_data_row:] if any(r)]
    text_cols = []
    for col in range(ncols):
        cells = [c for c in _column_cells(grid, col, first_data_row) if c]
        if cells and not all(OUTLINE_RE.match(c) or c.isdigit() for c in cells):
            text_cols.append(col)

    runs, cur = [], []
    for col in text_cols:
        if cur and col == cur[-1] + 1:
            cur.append(col)
        else:
            if len(cur) >= 2:
                runs.append(cur)
            cur = [col]
    if len(cur) >= 2:
        runs.append(cur)

    out = []
    for run in runs:
        for size in range(len(run), 1, -1):
            cols = run[:size]
            filled = [sum(1 for c in cols if c < len(r) and r[c]) for r in rows]
            if not filled:
                continue
            if all(f == 1 for f in filled):
                style = "staircase"
            elif all(f == len(cols) for f in filled) and _has_grouping(rows, cols):
                style = "repeated"
            else:
                continue
            out.append({
                "mode": "columns", "level_columns": cols, "style": style,
                "score": 1.0,
                "evidence": (f"cột {cols}: mọi dòng điền "
                             f"{'đúng một' if style == 'staircase' else 'đủ'} cột cấp"),
            })
            break
    return out
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist): dò kiểu phân cấp — outline/level/columns kèm bằng chứng"
```

---

### Task 3: Dựng cây từ lưới ô (`build_tree`)

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `OUTLINE_RE` (Task 2)
- Produces:
  - `build_tree(grid: list[list[str]], mapping: dict) -> tuple[list[dict], list[dict]]` — trả `(cây, danh sách dòng bị bỏ)`. Node của cây có `name`, `description`, `children`, `row` (chưa có `id`). Mỗi phần tử `skipped`: `{"row": int (1-based), "reason": str, "raw": list[str]}`. Ném `ValueError` khi nhảy cấp hoặc thiếu cấp trung gian.

`mapping` có dạng:
```json
{"first_data_row": 1,
 "columns": {"name": 1, "description": 2},
 "hierarchy": {"mode": "outline", "column": 0},
 "skip_rows": []}
```
Mode `columns` thì `name` lấy từ cột cấp sâu nhất có giá trị, `columns.name` bị bỏ qua.

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_fnlist_tree.py`:

```python
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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v -k build_tree`
Expected: FAIL — `AttributeError: module 'fnlist_tree' has no attribute 'build_tree'`

- [ ] **Step 3: Cài đặt**

Thêm vào cuối `fnlist_tree.py`:

```python
def _cell(raw, idx):
    if idx is None or idx >= len(raw):
        return ""
    return raw[idx]


def _level_and_name(raw, mapping):
    """Một dòng → (cấp, tên). Cấp None nghĩa là không đọc được cấp của dòng."""
    h = mapping.get("hierarchy") or {}
    cols = mapping.get("columns") or {}
    mode = h.get("mode")
    if mode == "columns":
        deepest = (None, "")
        for level, col in enumerate(h["level_columns"], start=1):
            if _cell(raw, col):
                deepest = (level, _cell(raw, col))
        return deepest
    name = _cell(raw, cols.get("name"))
    if mode == "outline":
        code = _cell(raw, h["column"]).rstrip(".")
        return (code.count(".") + 1 if code else None), name
    if mode == "level":
        value = _cell(raw, h["column"])
        return (int(value) if value.isdigit() else None), name
    return 1, name      # không khai hierarchy → danh sách phẳng một cấp


def build_tree(grid, mapping):
    """Lưới ô → (cây, dòng bị bỏ). Chưa cấp ID ở bước này.

    Dòng bị bỏ KHÔNG biến mất im lặng — mọi dòng bỏ đều vào `skipped` kèm lý do
    để LLM báo lại cho người dùng."""
    h = mapping.get("hierarchy") or {}
    if h.get("mode") == "columns" and h.get("style") == "repeated":
        return _build_repeated(grid, mapping)
    return _build_leveled(grid, mapping)


def _iter_data_rows(grid, mapping, skipped):
    """Sinh (rowno 1-based, raw) cho các dòng dữ liệu thật, đẩy dòng người dùng
    khai bỏ sang `skipped`."""
    first = int(mapping.get("first_data_row", 1))
    skip = {int(x) for x in mapping.get("skip_rows", [])}
    for i, raw in enumerate(grid):
        if i < first:
            continue
        rowno = i + 1      # 1-based, khớp số dòng người dùng thấy trong Excel
        if rowno in skip:
            skipped.append({"row": rowno, "reason": "người dùng khai bỏ",
                            "raw": raw[:6]})
            continue
        yield rowno, raw


def _build_leveled(grid, mapping):
    desc_col = (mapping.get("columns") or {}).get("description")
    roots, skipped, stack = [], [], []
    for rowno, raw in _iter_data_rows(grid, mapping, skipped):
        level, name = _level_and_name(raw, mapping)
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


def _build_repeated(grid, mapping):
    """Kiểu tên cha lặp lại trên mọi dòng: mỗi dòng là một lá, tổ tiên suy từ
    tiền tố giá trị các cột cấp. Hai dòng cùng tiền tố dùng lại đúng node cha đó,
    không tạo node cha thứ hai trùng tên."""
    level_cols = mapping["hierarchy"]["level_columns"]
    desc_col = (mapping.get("columns") or {}).get("description")
    roots, skipped, index = [], [], {}
    for rowno, raw in _iter_data_rows(grid, mapping, skipped):
        values = [_cell(raw, c) for c in level_cols]
        if not values[-1]:
            skipped.append({"row": rowno, "reason": "ô tên chức năng trống",
                            "raw": raw[:6]})
            continue
        for depth, value in enumerate(values[:-1], start=1):
            if not value:
                raise ValueError(
                    f"Dòng {rowno}: cột cấp {depth} trống trong khi cấp sâu hơn "
                    "có giá trị. Kiểu 'repeated' đòi mọi cột cấp đều điền — "
                    "có thể file này thật ra là kiểu 'staircase'.")
        siblings = roots
        node = None
        for depth in range(len(values)):
            key = tuple(values[:depth + 1])
            node = index.get(key)
            if node is None:
                node = {"name": values[depth], "description": "",
                        "children": [], "row": rowno}
                index[key] = node
                siblings.append(node)
            siblings = node["children"]
        node["description"] = _cell(raw, desc_col)
    return roots, skipped
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: PASS — 26 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist): dựng cây từ lưới ô cho cả 3 kiểu phân cấp, chặn nhảy cấp"
```

---

### Task 4: Cấp ID đa cấp ổn định (`assign_ids`, `compute_retired`, `carry_status`)

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `walk`, `name_path` (Task 1)
- Produces:
  - `assign_ids(tree: list[dict], old_tree: list[dict] | None = None, retired: Iterable[str] = ()) -> None` — gắn khoá `id` vào từng node, tại chỗ
  - `compute_retired(old_tree: list[dict] | None, new_tree: list[dict], prev_retired: Iterable[str] = ()) -> list[str]`
  - `carry_status(new_tree: list[dict], old_tree: list[dict] | None) -> None` — chép `status` theo `id`, tại chỗ

Thứ tự gọi bắt buộc: `assign_ids` → `carry_status` → `compute_retired`.

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_fnlist_tree.py`:

```python
def _mk(name, children=(), description=""):
    return {"name": name, "description": description,
            "children": [dict(c) for c in children]}


def _ids(tree):
    return [n["id"] for n, _ in ft.walk(tree)]


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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v -k "assign_ids or retired or carry_status"`
Expected: FAIL — `AttributeError: module 'fnlist_tree' has no attribute 'assign_ids'`

- [ ] **Step 3: Cài đặt**

Thêm vào cuối `fnlist_tree.py`:

```python
def assign_ids(tree, old_tree=None, retired=()):
    """Cấp ID đa cấp, sửa tại chỗ.

    Bốn luật, theo đúng thứ tự ưu tiên:
      1. Node đã có ở bản cũ (khớp theo ĐƯỜNG DẪN TÊN) giữ nguyên ID.
      2. Node mới lấy số nhỏ nhất chưa dùng trong cùng cha.
      3. Số đã khai tử không bao giờ cấp lại — hai tài liệu ở hai thời điểm
         không được trỏ cùng một ID ra hai chức năng khác nhau.
      4. Node đổi cha thì đường dẫn tên đổi theo, nên tự động rơi vào luật 2 và
         nhận ID mới — đây là điểm gãy truy vết duy nhất, `diff_trees` gắn nhãn
         'chuyển nhóm' để người dùng biết mà cập nhật tài liệu cũ.
    """
    old_by_path = {}
    for node, parents in walk(old_tree or []):
        old_by_path[name_path(node, parents)] = node
    retired = set(retired)

    def recurse(nodes, parents, prefix):
        used = set()
        for node in nodes:
            old = old_by_path.get(name_path(node, parents))
            if old and old.get("id", "").rsplit("-", 1)[0] == prefix:
                node["id"] = old["id"]
                used.add(int(old["id"].rsplit("-", 1)[1]))
        seq = 1
        for node in nodes:
            if "id" not in node:
                while seq in used or f"{prefix}-{seq:02d}" in retired:
                    seq += 1
                node["id"] = f"{prefix}-{seq:02d}"
                used.add(seq)
            recurse(node["children"], parents + (node,), node["id"])

    recurse(tree, (), "FN")


def compute_retired(old_tree, new_tree, prev_retired=()):
    """ID biến mất khỏi cây mới bị khai tử vĩnh viễn. Gọi SAU assign_ids."""
    alive = {n["id"] for n, _ in walk(new_tree)}
    gone = {n["id"] for n, _ in walk(old_tree or [])} - alive
    return sorted(set(prev_retired) | gone)


def carry_status(new_tree, old_tree):
    """Chép tiến độ (`status`) từ bản cũ sang theo ID. Gọi SAU assign_ids —
    không chép thì mỗi lần import lại xoá sạch tiến độ code-intel đã ghi."""
    old = {n["id"]: n.get("status") for n, _ in walk(old_tree or [])}
    for node, _ in walk(new_tree):
        status = old.get(node["id"])
        if status and status != "pending":
            node["status"] = status
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: PASS — 34 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist): cấp ID đa cấp ổn định, khớp theo đường dẫn tên, khai tử ID đã xoá"
```

---

### Task 5: So khác biệt hai lần import (`diff_trees`)

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py`

**Interfaces:**
- Consumes: `walk`, `name_path` (Task 1)
- Produces:
  - `diff_trees(old_tree: list[dict] | None, new_tree: list[dict]) -> list[dict]`. Mỗi phần tử có khoá `loai` ∈ `{"thêm", "bỏ", "đổi mô tả", "chuyển nhóm"}`:
    - `thêm` / `bỏ`: `{"loai", "id", "ten", "duong_dan"}`
    - `đổi mô tả`: `{"loai", "id", "ten", "cu", "moi"}`
    - `chuyển nhóm`: `{"loai", "ten", "id_cu", "id_moi", "tu", "den"}`

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_fnlist_tree.py`:

```python
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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v -k diff`
Expected: FAIL — `AttributeError: module 'fnlist_tree' has no attribute 'diff_trees'`

- [ ] **Step 3: Cài đặt**

Thêm vào cuối `fnlist_tree.py`:

```python
def diff_trees(old_tree, new_tree):
    """So hai cây theo đường dẫn tên. Gọi SAU assign_ids trên cả hai cây.

    Chỉ so NODE LÁ (không có children) — node cấp cao chỉ đổi vì con của nó
    đổi chỗ/đổi tên, tự nó không phải một thay đổi chức năng cần báo cáo
    riêng. Lọc lá tránh nhiễu này, nhưng cũng có nghĩa: đổi mô tả hoặc
    xoá/thêm một chức năng KHÔNG PHẢI lá (ví dụ đổi mô tả của một node cấp 1
    có con) sẽ không hiện trong diff — chấp nhận được vì phạm vi trước mắt là
    theo dõi chức năng lá, việc dùng thật cũng tập trung ở đó."""
    old_by_path = {name_path(n, p): n for n, p in walk(old_tree or []) if not n.get("children")}
    new_by_path = {name_path(n, p): n for n, p in walk(new_tree) if not n.get("children")}
    out = []
    for path, node in new_by_path.items():
        old = old_by_path.get(path)
        if old is None:
            out.append({"loai": "thêm", "id": node["id"], "ten": path[-1],
                        "duong_dan": " / ".join(path)})
        elif (old.get("description") or "") != (node.get("description") or ""):
            out.append({"loai": "đổi mô tả", "id": node["id"], "ten": path[-1],
                        "cu": old.get("description", ""),
                        "moi": node.get("description", "")})
    for path, old in old_by_path.items():
        if path not in new_by_path:
            out.append({"loai": "bỏ", "id": old["id"], "ten": path[-1],
                        "duong_dan": " / ".join(path)})
    return _merge_moves(out)


def _merge_moves(entries):
    """Một 'bỏ' và một 'thêm' cùng tên lá → gần như chắc chắn là chuyển nhóm,
    ID đã đổi. Gộp thành một dòng để người dùng biết mà cập nhật tài liệu trỏ ID
    cũ. Chỉ gộp khi tên đó xuất hiện ĐÚNG MỘT lần ở mỗi bên — nhiều hơn thì
    không đủ căn cứ ghép cặp, trình nguyên trạng còn hơn đoán sai."""
    removed = [e for e in entries if e["loai"] == "bỏ"]
    added = [e for e in entries if e["loai"] == "thêm"]
    moved = {}
    for name in {e["ten"] for e in removed} & {e["ten"] for e in added}:
        pair_out = [e for e in removed if e["ten"] == name]
        pair_in = [e for e in added if e["ten"] == name]
        if len(pair_out) == 1 and len(pair_in) == 1:
            moved[name] = (pair_out[0], pair_in[0])
    out = [e for e in entries
           if not (e["loai"] in ("thêm", "bỏ") and e["ten"] in moved)]
    for name in sorted(moved):
        gone, came = moved[name]
        out.append({"loai": "chuyển nhóm", "ten": name,
                    "id_cu": gone["id"], "id_moi": came["id"],
                    "tu": gone["duong_dan"], "den": came["duong_dan"]})
    return out
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: PASS — tổng số test tích luỹ tới lúc này (38 từ Task 1-4 + 5 mới = 43)

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(fnlist): so khác biệt hai lần import, gắn nhãn chuyển nhóm"
```

---

### Task 6: `inspect` — thêm ứng viên phân cấp, và gỡ phần markdown khỏi `fnlist_import.py`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_import.py`
- Rewrite: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: `fnlist_tree.detect_hierarchy` (Task 2)
- Produces:
  - `cmd_inspect(a)` in JSON có thêm khoá `hierarchy_candidates` cho mỗi sheet
  - Các hàm/hằng bị **xoá khỏi** `fnlist_import.py`: `HEADER`, `FN_ID_RE`, `build_rows`, `assign_ids`, `escape_cell`, `render_markdown`, `_KEYS`, `parse_functions_md`, `diff_rows`, và cả `cmd_write` cũ cùng subparser `write` của nó (Task 7 dựng lại bản JSON). Xoá trọn gói để commit của task này là một trạng thái tự nhất quán — script chỉ còn `inspect` và chạy được — thay vì để lại một `cmd_write` gọi vào các hàm vừa bị xoá.
  - Giữ nguyên không đổi: `_force_utf8_console`, `cell_str`, `_read_csv`, `_read_xlsx`, `read_grid`, `_needs_openpyxl`, `_has_openpyxl`, `_bootstrap_and_reexec`

- [ ] **Step 1: Viết test thất bại**

Thay **toàn bộ** nội dung `speckit-extension/scripts/tests/test_fnlist_import.py` bằng:

```python
import argparse
import json
import sys
from pathlib import Path

import pytest

import fnlist_import as fi

SCRIPT = Path(__file__).resolve().parents[1] / "fnlist_import.py"


def write_csv(tmp_path, rows, name="fnlist.csv"):
    import csv
    p = tmp_path / name
    with open(p, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    return p


SAMPLE = [
    ["STT", "Tên chức năng", "Mô tả"],
    ["1", "Quản lý đơn hàng", ""],
    ["1.1", "Danh sách đơn", "Xem, tìm kiếm đơn"],
    ["1.2", "Tạo đơn mới", ""],
    ["2", "Quản lý khách hàng", ""],
]

MAPPING = {"first_data_row": 1,
           "columns": {"name": 1, "description": 2},
           "hierarchy": {"mode": "outline", "column": 0}}


def test_cell_str_normalises_numbers_and_none():
    assert fi.cell_str(None) == ""
    assert fi.cell_str(3.0) == "3"
    assert fi.cell_str(3.5) == "3.5"
    assert fi.cell_str("  x  ") == "x"


def test_read_grid_csv_returns_single_sheet(tmp_path):
    grids = fi.read_grid(write_csv(tmp_path, SAMPLE))
    assert list(grids) == ["fnlist"]
    assert len(grids["fnlist"]) == 5


def test_inspect_prints_shape_and_head(tmp_path, capsys):
    p = write_csv(tmp_path, SAMPLE)
    fi.cmd_inspect(argparse.Namespace(path=str(p), sheet=None, max_rows=3,
                                      max_cols=10, first_data_row=1))
    sheet = json.loads(capsys.readouterr().out)["sheets"][0]
    assert sheet["name"] == "fnlist"
    assert sheet["rows"] == 5
    assert len(sheet["head"]) == 3


def test_inspect_reports_hierarchy_candidates(tmp_path, capsys):
    p = write_csv(tmp_path, SAMPLE)
    fi.cmd_inspect(argparse.Namespace(path=str(p), sheet=None, max_rows=8,
                                      max_cols=12, first_data_row=1))
    sheet = json.loads(capsys.readouterr().out)["sheets"][0]
    top = sheet["hierarchy_candidates"][0]
    assert top["mode"] == "outline"
    assert top["column"] == 0
    assert "evidence" in top


def test_markdown_rendering_is_gone():
    """functions.md không còn tồn tại trong đường ống — mọi hàm render bảng
    markdown phải biến mất, không để lại đường quay về âm thầm."""
    for name in ("render_markdown", "parse_functions_md", "escape_cell",
                 "diff_rows", "build_rows", "HEADER"):
        assert not hasattr(fi, name), f"{name} còn sót lại trong fnlist_import"
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -v`
Expected: FAIL — `test_inspect_reports_hierarchy_candidates` báo `KeyError: 'hierarchy_candidates'`, và `test_markdown_rendering_is_gone` báo `render_markdown còn sót lại`

- [ ] **Step 3: Cài đặt**

Trong `speckit-extension/scripts/fnlist_import.py`:

Sửa docstring đầu file thành:

```python
#!/usr/bin/env python3
"""Function list (.xlsx/.csv) → .specify/docs/functions.json.

Kỷ luật: SCRIPT CHÉP NGUYÊN VĂN, LLM chỉ quyết ánh xạ cột và kiểu phân cấp.
Đây là văn bản hợp đồng nghiệm thu — không tóm tắt, không chuẩn hoá, không
"làm đẹp" nội dung ô. Script là thứ DUY NHẤT ghi functions.json.

Ba subcommand:
  inspect  — in cấu trúc thật của file + ứng viên kiểu phân cấp. Không đoán gì.
  write    — nhận ánh xạ cột dạng JSON, dựng cây, cấp ID, ghi functions.json.
  update   — đổi `status` của một/nhiều FN-ID (code-intel gọi khi ghi ngược).

Logic dựng cây/cấp ID nằm ở fnlist_tree.py. Tự dựng venv + openpyxl lần đầu
(chỉ khi đọc .xlsx). Chỉ cần python3.
"""
```

Ngay dưới khối `import`, thêm:

```python
import fnlist_tree as ft
```

Xoá hẳn các hằng và hàm sau (chúng chỉ phục vụ `functions.md`): `HEADER`, `FN_ID_RE`,
`build_rows`, `assign_ids`, `escape_cell`, `render_markdown`, `_KEYS`,
`parse_functions_md`, `diff_rows`, và **cả `cmd_write` cũ**.

Trong `main()`, xoá luôn khối đăng ký subparser `write` (từ dòng
`w = sub.add_parser("write", ...)` tới `w.set_defaults(func=cmd_write)`). Task 7 dựng
lại cả hàm lẫn subparser theo đường JSON. Sau task này script chỉ còn `inspect` và phải
chạy được — commit gãy giữa chừng là thứ không ai review nổi.

Giữ `XLSX_SUFFIXES`. Thay `cmd_inspect` bằng:

```python
def cmd_inspect(a) -> None:
    grids = read_grid(a.path, a.sheet)
    out = {"file": str(a.path), "sheets": []}
    for name, rows in grids.items():
        out["sheets"].append({
            "name": name,
            "rows": len(rows),
            "cols": max((len(r) for r in rows), default=0),
            "head": [r[: a.max_cols] for r in rows[: a.max_rows]],
            # Ứng viên kiểu phân cấp — chỉ là phỏng đoán kèm bằng chứng, LLM
            # BẮT BUỘC hỏi người dùng xác nhận chứ không tự chọn ứng viên đầu.
            "hierarchy_candidates": ft.detect_hierarchy(rows, a.first_data_row),
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))
```

Trong `main()`, thêm cờ cho parser `inspect` (ngay sau dòng `i.add_argument("--max-cols", ...)`):

```python
    i.add_argument("--first-data-row", type=int, default=1, dest="first_data_row",
                   help="Chỉ số 0-based của dòng dữ liệu đầu tiên, dùng khi dò phân cấp")
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -v`
Expected: PASS — 5 passed

Kiểm thêm script còn chạy được sau khi xoá:

Run: `python speckit-extension/scripts/fnlist_import.py --help`
Expected: exit 0, phần `{inspect}` chỉ liệt kê `inspect` (chưa có `write`/`update`)

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist): inspect trả ứng viên phân cấp, gỡ toàn bộ phần render markdown"
```

---

### Task 7: `write` — ghi `functions.json`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_import.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: `ft.build_tree`, `ft.assign_ids`, `ft.carry_status`, `ft.compute_retired`, `ft.diff_trees`, `ft.build_document`, `ft.walk` (Task 1–5)
- Produces:
  - `load_document(path: Path) -> dict | None` — `None` nếu file chưa tồn tại
  - `save_document(path: Path, doc: dict) -> None` — ghi nguyên tử (tmp + `os.replace`)
  - `cmd_write(a)` — in báo cáo JSON có `out`, `written`, `skipped`, `retired`, và `diff` (chỉ khi file đã tồn tại)

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_fnlist_import.py`:

```python
def run_write(tmp_path, rows=None, mapping=None, out_name="functions.json",
              system="DMS", date="2026-08-11"):
    src = write_csv(tmp_path, rows or SAMPLE)
    out = tmp_path / out_name
    mp = tmp_path / "map.json"
    mp.write_text(json.dumps(mapping or MAPPING), encoding="utf-8")
    fi.cmd_write(argparse.Namespace(
        path=str(src), mapping=str(mp), out=str(out),
        system=system, date=date, sheet="fnlist"))
    return out


def test_write_creates_json_tree(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["schema_version"] == 1
    assert doc["system"] == "DMS"
    assert doc["source"]["sheet"] == "fnlist"
    assert doc["updated"] == "2026-08-11"
    assert [f["id"] for f in doc["functions"]] == ["FN-01", "FN-02"]
    kids = doc["functions"][0]["children"]
    assert [k["id"] for k in kids] == ["FN-01-01", "FN-01-02"]
    assert kids[0]["description"] == "Xem, tìm kiếm đơn"


def test_write_omits_pending_status_and_extra_keys(tmp_path, capsys):
    doc = json.loads(run_write(tmp_path).read_text(encoding="utf-8"))
    capsys.readouterr()
    node = doc["functions"][0]
    assert set(node) == {"id", "name", "description", "children"}


def test_write_report_counts_written_and_skipped(tmp_path, capsys):
    rows = SAMPLE + [["3", "", ""]]
    run_write(tmp_path, rows=rows)
    report = json.loads(capsys.readouterr().out)
    assert report["written"] == 4
    assert report["skipped"][0]["reason"] == "ô tên chức năng trống"
    assert report["retired"] == []
    assert "diff" not in report          # lần ghi đầu thì không có gì để so


def test_write_second_run_keeps_ids_status_and_reports_diff(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    doc = json.loads(out.read_text(encoding="utf-8"))
    doc["functions"][0]["children"][0]["status"] = "intel"
    out.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    rows = SAMPLE[:3] + [["1.2", "Tạo đơn nháp", ""]] + SAMPLE[3:]
    run_write(tmp_path, rows=rows)
    report = json.loads(capsys.readouterr().out)
    doc2 = json.loads(out.read_text(encoding="utf-8"))

    kids = {k["name"]: k for k in doc2["functions"][0]["children"]}
    assert kids["Danh sách đơn"]["id"] == "FN-01-01"
    assert kids["Danh sách đơn"]["status"] == "intel"    # tiến độ không bị xoá
    assert kids["Tạo đơn mới"]["id"] == "FN-01-02"       # KHÔNG bị dịch số
    assert kids["Tạo đơn nháp"]["id"] == "FN-01-03"      # chèn giữa, số cuối
    assert any(d["loai"] == "thêm" and d["ten"] == "Tạo đơn nháp"
               for d in report["diff"])


def test_write_records_retired_ids_across_runs(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    run_write(tmp_path, rows=[r for r in SAMPLE if r[1] != "Tạo đơn mới"])
    report = json.loads(capsys.readouterr().out)
    assert report["retired"] == ["FN-01-02"]
    assert json.loads(out.read_text(encoding="utf-8"))["retired_ids"] == ["FN-01-02"]


def test_write_refuses_empty_result(tmp_path):
    rows = [["STT", "Tên chức năng", "Mô tả"]]
    with pytest.raises(SystemExit) as e:
        run_write(tmp_path, rows=rows)
    assert "không lấy được" in str(e.value).lower()


def test_write_reports_level_jump_as_clean_exit(tmp_path):
    rows = [["STT", "Tên chức năng", "Mô tả"],
            ["1", "Quản lý đơn hàng", ""],
            ["1.1.1", "Lọc trạng thái", ""]]
    with pytest.raises(SystemExit) as e:
        run_write(tmp_path, rows=rows)
    assert "nhảy" in str(e.value)


def test_write_leaves_old_file_untouched_on_failure(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    before = out.read_text(encoding="utf-8")
    bad = [["STT", "Tên chức năng", "Mô tả"],
           ["1", "Quản lý đơn hàng", ""],
           ["1.1.1", "Lọc trạng thái", ""]]
    with pytest.raises(SystemExit):
        run_write(tmp_path, rows=bad)
    assert out.read_text(encoding="utf-8") == before


def test_cli_write_survives_default_windows_console_encoding(tmp_path):
    """Regression: subprocess trên Windows mặc định stdout cp1252, không phải
    UTF-8 — in báo cáo tiếng Việt (json.dumps ensure_ascii=False) từng crash
    UnicodeEncodeError. Không truyền PYTHONIOENCODING để bài test này thật sự
    đi qua đường mặc định, không phải đường đã được env ưu ái."""
    import os
    import subprocess
    src = write_csv(tmp_path, SAMPLE + [["3", "", ""]])
    out = tmp_path / "functions.json"
    mp = tmp_path / "map.json"
    mp.write_text(json.dumps(MAPPING), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "write", str(src), "--mapping", str(mp),
         "--out", str(out), "--system", "DMS", "--date", "2026-08-11",
         "--sheet", "fnlist"],
        capture_output=True, text=True, encoding="utf-8", env=env)
    assert p.returncode == 0, p.stderr
    assert "ô tên chức năng trống" in p.stdout
    assert "Quản lý đơn hàng" in out.read_text(encoding="utf-8")
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -v -k write`
Expected: FAIL — `AttributeError: module 'fnlist_import' has no attribute 'build_rows'` (do `cmd_write` cũ còn gọi hàm đã xoá ở Task 6)

- [ ] **Step 3: Cài đặt**

Trong `fnlist_import.py`, thêm `import os` và `import tempfile` vào khối import (giữ `os` nếu đã có), rồi **thay toàn bộ** `cmd_write` cũ bằng:

```python
def load_document(path: Path):
    """Đọc functions.json đã có. Trả None nếu chưa có file."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{path} không phải JSON hợp lệ ({e}). "
                         "Sửa hoặc xoá file rồi chạy lại.")


def save_document(path: Path, doc: dict) -> None:
    """Ghi nguyên tử: dựng file tạm cùng thư mục rồi replace. Ngắt giữa chừng
    thì bản cũ còn nguyên vẹn, không có file JSON cụt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def cmd_write(a) -> None:
    grids = read_grid(a.path, a.sheet)
    name = a.sheet or next(iter(grids))
    grid = grids[name]
    mapping = json.loads(Path(a.mapping).read_text(encoding="utf-8"))

    try:
        tree, skipped = ft.build_tree(grid, mapping)
    except ValueError as e:
        # Lỗi cấu trúc file nguồn: dừng sạch, KHÔNG ghi gì — bản cũ nguyên vẹn.
        raise SystemExit(str(e))
    if not tree:
        raise SystemExit("Không lấy được chức năng nào — kiểm lại ánh xạ cột.")

    out = Path(a.out)
    old_doc = load_document(out)
    old_tree = (old_doc or {}).get("functions") or []
    prev_retired = (old_doc or {}).get("retired_ids") or []

    ft.assign_ids(tree, old_tree, prev_retired)
    ft.carry_status(tree, old_tree)
    retired = ft.compute_retired(old_tree, tree, prev_retired)

    save_document(out, ft.build_document(
        tree, a.system, str(a.path), name, a.date, retired))

    report = {
        "out": str(out),
        "written": sum(1 for _ in ft.walk(tree)),
        "skipped": skipped,
        "retired": retired,
    }
    if old_doc:
        report["diff"] = ft.diff_trees(old_tree, tree)
    print(json.dumps(report, ensure_ascii=False, indent=2))
```

Trong `main()`, dựng lại subparser `write` (Task 6 đã xoá bản cũ), đặt ngay sau khối
đăng ký `inspect`:

```python
    w = sub.add_parser("write", help="Dựng cây theo ánh xạ cột → functions.json")
    w.add_argument("path")
    w.add_argument("--mapping", required=True, help="File JSON ánh xạ cột")
    w.add_argument("--out", default=".specify/docs/functions.json")
    w.add_argument("--system", default="[TÊN HỆ THỐNG]")
    w.add_argument("--date", required=True, help="Ngày cập nhật YYYY-MM-DD")
    w.add_argument("--sheet", default=None)
    w.set_defaults(func=cmd_write)
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -v`
Expected: PASS — 14 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist): write ghi functions.json — giữ ID/tiến độ, ghi nguyên tử, báo diff"
```

---

### Task 8: `update` — đổi `status` theo FN-ID

**Files:**
- Modify: `speckit-extension/scripts/fnlist_import.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: `load_document`, `save_document` (Task 7); `ft.find_by_id`, `ft.STATUSES`, `ft.build_document`, `ft.walk` (Task 1)
- Produces: `cmd_update(a)` — CLI: `update --file <path> --set FN-01-01=intel [--set ...]`; in báo cáo JSON `{"file", "updated": [{"id", "cu", "moi"}]}`

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_fnlist_import.py`:

```python
def test_update_sets_status(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=intel"]))
    report = json.loads(capsys.readouterr().out)
    assert report["updated"] == [{"id": "FN-01-01", "cu": "pending", "moi": "intel"}]
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["functions"][0]["children"][0]["status"] == "intel"


def test_update_accepts_multiple_ids(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    fi.cmd_update(argparse.Namespace(
        file=str(out), set=["FN-01-01=intel", "FN-01-02=srs"]))
    capsys.readouterr()
    kids = json.loads(out.read_text(encoding="utf-8"))["functions"][0]["children"]
    assert [k.get("status") for k in kids] == ["intel", "srs"]


def test_update_back_to_pending_removes_key(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=intel"]))
    fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=pending"]))
    capsys.readouterr()
    node = json.loads(out.read_text(encoding="utf-8"))["functions"][0]["children"][0]
    assert "status" not in node


def test_update_rejects_unknown_id_without_writing(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    before = out.read_text(encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        fi.cmd_update(argparse.Namespace(
            file=str(out), set=["FN-01-01=intel", "FN-99=intel"]))
    assert "FN-99" in str(e.value)
    assert out.read_text(encoding="utf-8") == before   # không ghi một phần


def test_update_rejects_unknown_status(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    with pytest.raises(SystemExit) as e:
        fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01=xong"]))
    assert "xong" in str(e.value)


def test_update_rejects_malformed_set(tmp_path, capsys):
    out = run_write(tmp_path)
    capsys.readouterr()
    with pytest.raises(SystemExit):
        fi.cmd_update(argparse.Namespace(file=str(out), set=["FN-01-01"]))


def test_update_on_missing_file_stops(tmp_path):
    with pytest.raises(SystemExit) as e:
        fi.cmd_update(argparse.Namespace(
            file=str(tmp_path / "khong-co.json"), set=["FN-01=intel"]))
    assert "khong-co.json" in str(e.value)


def test_cli_update_end_to_end(tmp_path, capsys):
    import subprocess
    out = run_write(tmp_path)
    capsys.readouterr()
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "update", "--file", str(out),
         "--set", "FN-02=srs"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 0, p.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["functions"][1]["status"] == "srs"
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_import.py -v -k update`
Expected: FAIL — `AttributeError: module 'fnlist_import' has no attribute 'cmd_update'`

- [ ] **Step 3: Cài đặt**

Thêm vào `fnlist_import.py`, ngay sau `cmd_write`:

```python
def cmd_update(a) -> None:
    """Đổi `status` của một/nhiều FN-ID. Đây là đường DUY NHẤT để code-intel và
    srs-from-code ghi ngược tiến độ — không lệnh nào được sửa tay functions.json.

    Kiểm toàn bộ trước khi ghi: một ID sai là dừng sạch, không ghi phần đúng rồi
    bỏ dở phần sai."""
    path = Path(a.file)
    doc = load_document(path)
    if doc is None:
        raise SystemExit(f"Không thấy {path}. Chạy `fnlist-import` trước.")
    tree = doc.get("functions") or []

    pairs = []
    for item in a.set:
        if "=" not in item:
            raise SystemExit(f"--set '{item}' sai cú pháp, cần dạng FN-01-01=intel.")
        fid, status = item.split("=", 1)
        if status not in ft.STATUSES:
            raise SystemExit(f"Trạng thái '{status}' không hợp lệ. "
                             f"Chỉ nhận: {', '.join(ft.STATUSES)}.")
        node = ft.find_by_id(tree, fid)
        if node is None:
            raise SystemExit(f"Không có {fid} trong {path}.")
        pairs.append((node, fid, status))

    updated = []
    for node, fid, status in pairs:
        old = node.get("status") or "pending"
        if status == "pending":
            node.pop("status", None)
        else:
            node["status"] = status
        updated.append({"id": fid, "cu": old, "moi": status})

    doc["functions"] = [ft.clean_node(n) for n in tree]
    save_document(path, doc)
    print(json.dumps({"file": str(path), "updated": updated},
                     ensure_ascii=False, indent=2))
```

Trong `main()`, thêm parser thứ ba (ngay trước `a = p.parse_args(argv)`):

```python
    u = sub.add_parser("update", help="Đổi status của FN-ID trong functions.json")
    u.add_argument("--file", default=".specify/docs/functions.json")
    u.add_argument("--set", action="append", required=True, metavar="FN-ID=status",
                   help="vd --set FN-01-01=intel (lặp được nhiều lần)")
    u.set_defaults(func=cmd_update)
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/ -v`
Expected: PASS — toàn bộ test của cả hai file `test_fnlist_*.py` (61 passed), và các test khác của repo không đổi

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist): subcommand update ghi ngược status, kiểm toàn bộ trước khi ghi"
```

---

### Task 9: `references/functions-schema.md`

**Files:**
- Create: `speckit-extension/references/functions-schema.md`

**Interfaces:**
- Consumes: schema do Task 1–7 cài đặt
- Produces: tài liệu để `commands/fnlist-import.md` (Task 10) và hai lệnh của đợt sau cùng trỏ tới

- [ ] **Step 1: Viết file**

Tạo `speckit-extension/references/functions-schema.md`:

````markdown
# `functions.json` — schema danh mục chức năng

Đây là **nguồn sự thật duy nhất** về danh mục chức năng của dự án. Không có bản
markdown song song; không ai sửa tay file này. `scripts/fnlist_import.py` là
chương trình duy nhất được phép ghi — mọi lệnh khác muốn đổi gì thì gọi
subcommand `update`.

Đường dẫn mặc định: `.specify/docs/functions.json`.

## Hình dạng

```json
{
  "schema_version": 1,
  "system": "Hệ thống DMS",
  "source": { "file": "FunctionList_DMS.xlsx", "sheet": "DanhMuc" },
  "updated": "2026-08-11",
  "retired_ids": ["FN-01-04"],
  "functions": [
    {
      "id": "FN-01",
      "name": "Quản lý đơn hàng",
      "description": "",
      "children": [
        {
          "id": "FN-01-01",
          "name": "Danh sách đơn",
          "description": "Xem, tìm kiếm đơn hàng",
          "status": "intel",
          "children": []
        },
        { "id": "FN-01-02", "name": "Tạo đơn mới", "description": "", "children": [] }
      ]
    },
    { "id": "FN-02", "name": "Quản lý khách hàng", "description": "", "children": [] }
  ]
}
```

## Trường ở mức tài liệu

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `schema_version` | int | Hiện là `1`. Đọc file có số khác thì dừng, đừng đoán. |
| `system` | string | Tên hệ thống, do người dùng xác nhận lúc import. |
| `source` | object | `file` (đường dẫn file nguồn) + `sheet` (tên sheet đã dùng). |
| `updated` | string | `YYYY-MM-DD`, ngày chạy lệnh import gần nhất. |
| `retired_ids` | array | ID của chức năng đã bị xoá. **Không bao giờ cấp lại**. |
| `functions` | array | Các node gốc, theo đúng thứ tự dòng của file nguồn. |

## Trường của một node

Đúng năm trường, không hơn.

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | string | Mã đa cấp, xem dưới. |
| `name` | string | Tên chức năng, **nguyên văn** ô nguồn. |
| `description` | string | Mô tả, **nguyên văn** ô nguồn. Không có thì `""`. |
| `status` | string | `intel` hoặc `srs`. **Vắng mặt = `pending`** — giá trị mặc định không được ghi ra file. |
| `children` | array | Node con; lá thì `[]`. |

`status` nghĩa là gì:

- vắng mặt / `pending` — chưa lệnh nào xử lý chức năng này
- `intel` — đã có mặt trong một `intel.md`
- `srs` — đã có mặt trong một `srs.md`

**Không có trường `cum`.** Muốn biết một FN thuộc cụm nào thì quét
`.specify/docs/*/intel.md` — chính file đó liệt kê FN-ID mà nó phủ. Lưu thêm ở
đây là tạo bản sao dễ lạc hậu hơn bản gốc.

**Không có trường `nguon_code`.** Danh sách `file:dòng` là nội dung của
`intel.md`.

**Không có `level`, `outline`, `parent`.** Cấp bậc đọc từ độ sâu lồng của
`children`; số mục lục kiểu `1.2.3` suy từ vị trí trong mảng.

## Quy tắc ID

Dạng `FN-01`, `FN-01-01`, `FN-01-01-01` — mỗi cấp hai chữ số, nối bằng `-`. Số
cấp bằng độ sâu trong cây (2 đến 4 cấp tuỳ dự án).

Số trong ID **không phản ánh thứ tự hiển thị**, và đó là chủ ý:

1. Lần import đầu: đánh số theo vị trí trong nhóm cha, từ `01`.
2. Import lại: node đã tồn tại (khớp theo **đường dẫn tên** — chuỗi `name` từ
   gốc xuống) giữ nguyên ID.
3. Node mới chèn vào giữa: lấy số kế tiếp chưa dùng trong nhóm cha, không dịch
   số của ai. Chèn giữa `FN-01-01` và `FN-01-02` thì thành `FN-01-03`.
4. Node bị xoá: ID vào `retired_ids`, không bao giờ cấp lại.
5. Node đổi nhóm cha: đường dẫn tên đổi → nhận ID mới. `diff` của lệnh `write`
   gắn nhãn `chuyển nhóm` kèm ID cũ → mới. **Đây là điểm gãy truy vết duy
   nhất** — tài liệu nào đang trỏ ID cũ phải sửa tay.

## Đọc và ghi

```bash
# Đọc: chỉ cần json.load / jq, không có định dạng riêng nào.
# Ghi status (đường DUY NHẤT):
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json \
  --set FN-01-01=intel --set FN-01-02=srs
```

Lệnh `update` kiểm toàn bộ trước khi ghi: một ID sai hoặc một `status` lạ là
dừng với mã thoát khác 0 và **không ghi gì**.
````

- [ ] **Step 2: Kiểm nội dung khớp cài đặt**

Run: `python -c "import json,sys; sys.path.insert(0,'speckit-extension/scripts'); import fnlist_tree as ft; print(ft.STATUSES); print(ft.ID_RE.pattern)"`
Expected: in ra `('pending', 'intel', 'srs')` và `^FN(?:-\d{2})+$` — khớp phần "Quy tắc ID" và bảng `status` vừa viết. Lệch thì sửa tài liệu cho khớp code.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/references/functions-schema.md
git commit -m "docs(fnlist): đặc tả schema functions.json dùng chung cho 3 lệnh"
```

---

### Task 10: Viết lại `commands/fnlist-import.md`

**Files:**
- Rewrite: `speckit-extension/commands/fnlist-import.md`

**Interfaces:**
- Consumes: CLI của Task 6–8, schema của Task 9
- Produces: quy trình LLM chạy lệnh

- [ ] **Step 1: Viết lại file**

Thay **toàn bộ** `speckit-extension/commands/fnlist-import.md` bằng:

````markdown
---
description: Nhập function list (.xlsx/.csv) đã dùng nghiệm thu thành .specify/docs/functions.json — cây chức năng có ID đa cấp ổn định làm điểm neo truy vết cho mọi tài liệu bàn giao.
---

# Nhập function list thành functions.json

Có một file function list (`.xlsx` hoặc `.csv`) đã dùng để nghiệm thu đầu bài thầu với
khách. Nhiệm vụ: chuyển thành **`.specify/docs/functions.json`** — cây chức năng có mã
`FN-01-01` ổn định, làm điểm neo truy vết cho toàn bộ đường ống reverse tài liệu.
Toàn bộ tiếng Việt.

Schema của file đầu ra: `.specify/extensions/dft-speckit/references/functions-schema.md`.
**Đọc file đó trước khi bắt đầu** — nó là hợp đồng dữ liệu, không phải tài liệu tham khảo
tuỳ chọn.

**Nguyên tắc lõi**: **script chép, bạn chỉ quyết ánh xạ.** Bạn KHÔNG được tóm tắt, chuẩn
hoá, sửa chính tả hay "làm đẹp" nội dung ô. Đây là văn bản hợp đồng nghiệm thu — script là
thứ duy nhất ghi `functions.json`; việc của bạn là dò file, quyết cột nào là gì và cấp bậc
thể hiện ra sao, xác nhận với người dùng, chạy script, đối chiếu kết quả, báo cáo trung thực.

**Mã thoát khác 0 ở bất kỳ lệnh nào dưới đây → DỪNG, in nguyên thông điệp lỗi cho người
dùng. Không tự chữa, không tự đoán tham số khác rồi thử lại.** Ngoại lệ duy nhất:
thông điệp `Không có sheet 'X'. Sheet hiện có: […]` — quay lại bước 2 hỏi người dùng
chọn đúng tên sheet từ danh sách đó.

## User Input

`$ARGUMENTS`

Kỳ vọng: **đường dẫn tới một file `.xlsx` hoặc `.csv`**. Trống, không tồn tại, hoặc sai
đuôi → **hỏi lại**, KHÔNG tự đi tìm file trong repo.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/fnlist_import.py`.
Dùng `python3` nếu `python` không có (macOS/Linux). Lần đầu đọc `.xlsx`, script tự dựng
`.venv` + cài `openpyxl` — **cần mạng**, chỉ một lần.

### 0. Kiểm `.gitignore`

```bash
git check-ignore -q .specify/docs/functions.json && echo "BỊ IGNORE" || echo "OK"
```

In ra `BỊ IGNORE` → **cảnh báo người dùng trước khi ghi**: tài liệu bàn giao sẽ không
vào git. Không chặn — có thể là chủ ý của project. Đề nghị luôn phương án đổi `--out` ở
bước 4 sang một đường dẫn không bị ignore nếu người dùng muốn.

### 1. Dò cấu trúc

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py inspect "<đường-dẫn>"
```

Mặc định chỉ in **8 dòng đầu × 12 cột đầu** (`--max-rows`/`--max-cols`). File có nhiều
hơn 12 cột, hoặc 8 dòng đầu chưa đủ để phân biệt đâu là header/đâu là dữ liệu thật (vd
vài dòng logo/tiêu đề merge ở đầu) → **chạy lại với giới hạn lớn hơn**, không được đoán
ngoài khung nhìn đang có:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py inspect "<đường-dẫn>" \
  --max-rows 20 --max-cols 20 --first-data-row 1
```

`--first-data-row` (0-based) ảnh hưởng tới việc dò phân cấp: dò trên vùng dữ liệu, nên
đoán sai dòng bắt đầu là ứng viên phân cấp cũng lệch theo. Xác định `first_data_row`
trước, rồi chạy lại `inspect` với đúng giá trị đó nếu nó khác 1.

Nhiều sheet → mỗi sheet đều xuất hiện trong `sheets`; đọc `head` của **từng** sheet
trước khi quyết sheet nào là function list thật.

### 2. Quyết ánh xạ cột và kiểu phân cấp

Trường `hierarchy_candidates` của mỗi sheet là **phỏng đoán kèm bằng chứng, không phải
quyết định**. Ba kiểu:

- `columns` — mỗi cấp một cột (`Phân hệ | Nhóm | Chức năng`). Kèm `style`:
  `staircase` (mỗi dòng chỉ điền một cột cấp) hoặc `repeated` (tên cha lặp lại mọi dòng).
- `outline` — một cột chứa số mục lục `1`, `1.1`, `1.1.1`.
- `level` — một cột ghi thẳng số cấp 1/2/3.

**Luôn luôn hỏi người dùng xác nhận kiểu phân cấp qua AskUserQuestion**, kể cả khi chỉ có
một ứng viên và `score` bằng 1.0. Danh sách rỗng cũng phải hỏi — rỗng nghĩa là script
không thấy dấu hiệu phân cấp nào, và "danh sách phẳng một cấp" là một câu trả lời hợp lệ
cần người dùng xác nhận, không phải mặc định im lặng.

Lý do không tự chọn: cột mô tả cũng là cột chữ nên có thể lọt vào ứng viên `columns`, và
một cột "STT" dạng `1.1` của tài liệu đánh số tay có thể không phải cấu trúc chức năng
thật. Script không phân biệt được, người dùng thì có.

Ba tình huống sau cũng **bắt buộc hỏi**, không tự chọn — **không chắc một tình huống có
thuộc nhóm này hay không thì coi như thuộc**, mặc định là hỏi:

- **Nhiều sheet** — sheet nào là function list thật (không phải sheet ghi chú/phụ lục).
- **Header hai tầng** — vd dòng 0 có ô trống xen kẽ (chỉ vài cột lớn có chữ) và dòng 1
  mới điền đủ nhãn con cho từng cột. Phân biệt với **header một tầng nhưng tên cột dài**
  (dòng 0 mọi ô đều có chữ, chỉ là "Mô tả chi tiết chức năng" thay vì "Mô tả") — trường
  hợp sau KHÔNG cần hỏi, tự chọn `first_data_row` = 1 là đủ.
- **Cột mô tả mơ hồ** — không chắc cột nào là mô tả chức năng hay chỉ là ghi chú/trạng thái.

Mỗi lượt AskUserQuestion gom 1–4 câu độc lập nhau.

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

`skip_rows` (tuỳ chọn) là danh sách số dòng **1-based** — đúng số dòng người dùng nhìn
thấy trong Excel, **khác hệ đếm** với `first_data_row`/`columns`/`level_columns`/
`hierarchy.column` ở trên (0-based). Lẫn hệ đếm ở đây là bỏ nhầm một dòng khác với dòng
định bỏ, và hậu quả không lộ ra ở đâu cả.

### 3. Xác nhận trước khi ghi (checkpoint bắt buộc)

**Không được bỏ qua bước này dù cảm thấy ánh xạ đã "rõ ràng".** Tự render **cây 5 dòng
dữ liệu đầu** theo ánh xạ đã chọn, thụt lề theo cấp:

```
Quản lý đơn hàng
  Danh sách đơn — Xem, tìm kiếm đơn hàng
    Lọc theo trạng thái
  Tạo đơn mới
Quản lý khách hàng
```

Cây thụt lề chứ không phải bảng phẳng, vì thứ dễ sai nhất ở lệnh này là **cấp bậc**, và
bảng phẳng giấu đúng cái đó đi.

Hỏi qua AskUserQuestion: "Cấp bậc và ánh xạ này đúng chưa?" — **chờ phản hồi thật, cấm tự
tuyên bố người dùng đã đồng ý.** Chưa có phản hồi → DỪNG, không chạy bước 4. Sai → quay
lại bước 2 sửa ánh xạ, xác nhận lại từ đầu.

Lý do bắt buộc: mọi `FN-ID` sau này của `code-intel`/`srs-from-code` neo vào đúng lần ghi
này. Sai ở đây khó gỡ hơn nhiều so với một lượt hỏi.

`--system`/`--date` dùng ở bước 4: lấy tên hệ thống từ `$ARGUMENTS`, README, hoặc
constitution project nếu có; không chắc thì hỏi cùng lượt AskUserQuestion này. `--date`
= ngày chạy lệnh (YYYY-MM-DD). Không tự bịa tên hệ thống.

### 4. Ghi

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py write "<đường-dẫn>" \
  --mapping .specify/tmp/fnlist/mapping.json \
  --out .specify/docs/functions.json \
  --system "<tên hệ thống>" \
  --date <YYYY-MM-DD> \
  --sheet "<tên sheet đã chọn ở bước 1>"
```

**Luôn truyền `--sheet` tường minh, kể cả file chỉ có một sheet — và giá trị PHẢI lấy
đúng nguyên văn từ trường `name` của sheet đã chọn trong JSON `inspect` ở bước 1, không
tự gõ tên khác.** Với `.xlsx` đó là tên sheet thật; với `.csv` đó **không phải** "Sheet1"
hay tên bịa nào — nó là tên file bỏ đuôi (script dùng làm khoá nội bộ cho CSV). Truyền
sai tên (kể cả với CSV) làm script không tìm thấy khoá và dừng với lỗi — đây là hành vi
đúng (không âm thầm sai). Thiếu hẳn cờ `--sheet` mới là ca nguy hiểm: script âm thầm dùng
sheet đầu tiên trong file, không báo lỗi — nếu đó không phải sheet vừa xác nhận ở bước 3,
lệnh ghi ra dữ liệu của sheet sai mà không có gì tố cáo.

Script in báo cáo JSON ra stdout: `out`, `written`, `skipped`, `retired`, và (chạy lại
trên file đã có) `diff`.

Chạy lại trên `functions.json` đã có thì script **ghi đè tại chỗ** — đúng như thiết kế,
vì không ai sửa tay file này: ID cũ được giữ theo đường dẫn tên, `status` do
`code-intel`/`srs-from-code` ghi cũng được chép sang bản mới. Không có bản `.new` nào và
không cần hợp nhất tay.

### 5. Đối chiếu tính đầy đủ

Đọc báo cáo.

**Kênh mất dòng thật nằm ở phần script không hề đếm**: mọi dòng có chỉ số **trước
`first_data_row`** không xuất hiện ở `written` lẫn `skipped` — với script, chúng không
tồn tại. Luôn luôn — không có điều kiện nào để bỏ qua bước này — trình lại các dòng
`head` từ chỉ số `0` tới `first_data_row − 1` của bước 1, và với **từng dòng** nêu lý do
cụ thể vì sao nó không phải một chức năng (dòng tiêu đề nhóm, dòng logo, dòng merge).
Thường chỉ có một dòng header nên chi phí gần như bằng không; nhưng bỏ qua bước này là
đúng chỗ một chức năng thật ở đầu bảng có thể biến mất mà không một tín hiệu nào tố cáo.

Có `skipped` → **liệt kê đích danh từng dòng** (số dòng + lý do: `ô tên chức năng trống`
hoặc `người dùng khai bỏ`), hỏi qua AskUserQuestion: có dòng nào trong số này thực ra là
một chức năng thật không? **Chờ phản hồi thật, cấm tự kết luận thay người dùng** dù lý do
trông hợp lý đến đâu.

- Xác nhận có dòng bỏ nhầm → sửa `mapping.json` rồi **quay lại bước 3** (xác nhận lại,
  không nhảy thẳng bước 4). Chạy lại `write` là an toàn: script giữ ID cũ theo đường dẫn
  tên, không cần xoá gì trước.
- Xác nhận đúng là bỏ → đi tiếp bước 6.

### 6. Trình `diff` (chỉ khi chạy lại trên file đã có)

Trình bảng `diff` cho người dùng. Bốn loại và cách nói về chúng:

- `thêm` / `bỏ` — chức năng mới xuất hiện / biến mất so với lần import trước.
- `đổi mô tả` — cùng vị trí trong cây, nội dung mô tả đổi.
- `chuyển nhóm` — **loại quan trọng nhất, phải nói rõ**: chức năng đổi nhóm cha nên
  **ID đã đổi** (`id_cu` → `id_moi`). Mọi tài liệu đang trỏ `id_cu` (`intel.md`, `srs.md`
  đã sinh) sẽ trỏ trượt và **phải sửa tay** — nêu đích danh ID cũ, ID mới, và nhắc người
  dùng rà lại. Đây là điểm gãy truy vết duy nhất của thiết kế; đừng trình lẫn vào các
  thay đổi thường.

Đổi tên chức năng hiện ra dưới dạng một cặp `bỏ` + `thêm` (khớp cũ↔mới dựa trên tên, nên
tên đổi là mất dấu vết). Thấy một cặp `bỏ`/`thêm` trông giống nhau về nghiệp vụ → nói
thẳng khả năng đây là đổi tên chứ không phải thêm/bớt chức năng.

`retired` liệt kê ID vừa bị khai tử — nói cho người dùng biết các ID này sẽ không bao giờ
được cấp lại cho chức năng khác.

### 7. Kết thúc

Báo: số chức năng đã ghi (`written`), sheet đã dùng, đường dẫn file.

**Nói rõ trạng thái đường ống**: `functions.json` đã ghi, nhưng
`/speckit.dft-speckit.code-intel` và `/speckit.dft-speckit.srs-from-code` **hiện chưa đọc
được định dạng này** (chúng vẫn tìm `functions.md`) — chưa chạy tiếp được cho tới khi hai
lệnh đó được cập nhật. **KHÔNG nhắc người dùng chạy `code-intel` như bước kế tiếp** — lời
nhắc đó dẫn thẳng vào chỗ gãy.

Project đã có `.specify/docs/functions.md` từ trước → **không xoá nó**. Nói cho người dùng
biết file cũ vẫn còn để `code-intel` chạy tạm được cho tới khi hai lệnh kia được cập nhật.

## Sai lầm thường gặp

- **Tự chọn kiểu phân cấp theo `score` cao nhất mà không hỏi** → cột mô tả bị hiểu thành
  cột cấp, hoặc cột STT đánh tay bị hiểu thành cấu trúc chức năng. `hierarchy_candidates`
  là phỏng đoán, không phải quyết định.
- **Tự đoán ánh xạ cột khi header mơ hồ, hoặc bỏ qua checkpoint bước 3** → sai cột là sai
  toàn bộ `functions.json`, và mọi FN-ID sau đó neo vào dữ liệu sai.
- **Trình checkpoint dạng bảng phẳng thay vì cây thụt lề** → giấu đúng cái dễ sai nhất là
  cấp bậc.
- **Quên truyền `--sheet` ở bước 4** → script âm thầm dùng sheet đầu tiên, không báo lỗi.
- **Nhầm hệ đếm của `skip_rows` (1-based) với các trường còn lại (0-based)** → bỏ nhầm
  dòng khác với dòng định bỏ.
- **Bỏ qua việc trình các dòng trước `first_data_row`** → chức năng thật ở đầu bảng biến
  mất mà không tín hiệu nào tố cáo. Công thức đếm của script không bắt được ca này.
- **Tự viết lại / tóm tắt nội dung ô** → phá hợp đồng lõi. Script chép, bạn không chép.
- **Tự kết luận `skipped` là ổn mà không hỏi** → dòng chức năng thật bị âm thầm rơi khỏi
  tài liệu bàn giao.
- **Trình `chuyển nhóm` như một thay đổi bình thường** → người dùng không biết ID đã đổi,
  các `intel.md`/`srs.md` cũ trỏ trượt mà không ai rà.
- **Nhắc chạy `code-intel` ở bước 7** → hai lệnh đó chưa đọc được `functions.json`.
- **Sửa tay `functions.json`** → script là chương trình duy nhất được phép ghi; muốn đổi
  `status` thì gọi `fnlist_import.py update`.
````

- [ ] **Step 2: Kiểm mọi lệnh trong tài liệu chạy được thật**

Run:
```bash
cd /tmp && rm -rf fnlist-smoke && mkdir fnlist-smoke && cd fnlist-smoke && \
printf 'STT,Ten chuc nang,Mo ta\n1,Quan ly don hang,\n1.1,Danh sach don,Xem don\n2,Quan ly khach hang,\n' > fn.csv && \
python /e/agent-skills/speckit-extension/scripts/fnlist_import.py inspect fn.csv --first-data-row 1 && \
printf '{"first_data_row":1,"columns":{"name":1,"description":2},"hierarchy":{"mode":"outline","column":0}}' > map.json && \
python /e/agent-skills/speckit-extension/scripts/fnlist_import.py write fn.csv --mapping map.json --out functions.json --system SMOKE --date 2026-08-11 --sheet fn && \
python /e/agent-skills/speckit-extension/scripts/fnlist_import.py update --file functions.json --set FN-01-01=intel && \
cat functions.json
```
Expected: `inspect` in `hierarchy_candidates` với `mode: "outline"`; `write` in `written: 3`; `update` in `updated`; `functions.json` cuối cùng có `FN-01-01` mang `"status": "intel"`.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/fnlist-import.md
git commit -m "docs(fnlist): viết lại command theo functions.json — hỏi kiểu phân cấp, checkpoint cây, cảnh báo đường ống đứt"
```

---

### Task 11: Cập nhật manifest và kiểm bản đóng gói

**Files:**
- Modify: `speckit-extension/extension.yml:44-46` (description của `fnlist-import`), `speckit-extension/extension.yml:6` (version)

**Interfaces:**
- Consumes: toàn bộ Task 1–10
- Produces: bản đóng gói chạy được

- [ ] **Step 1: Sửa `extension.yml`**

Đổi `version: "0.1.0"` (dòng 6) thành:

```yaml
  version: "0.2.0"
```

Thay khối `description` của `speckit.dft-speckit.fnlist-import` (dòng 46) bằng:

```yaml
      description: "Nhập function list (.xlsx/.csv) đã dùng nghiệm thu thành .specify/docs/functions.json — cây chức năng có ID đa cấp FN-01-01 ổn định làm điểm neo truy vết. Script chép nguyên văn và độc quyền ghi file; LLM chỉ quyết ánh xạ cột + kiểu phân cấp (columns/outline/level) rồi xác nhận với người dùng qua checkpoint cây thụt lề. Chạy lại giữ nguyên ID theo đường dẫn tên và giữ tiến độ status, báo diff kèm nhãn chuyển-nhóm cho ca ID buộc phải đổi."
```

- [ ] **Step 2: Chạy toàn bộ test của repo**

Run: `python -m pytest speckit-extension/scripts/tests/ -v`
Expected: PASS — không test nào fail (test cũ của `brd_roadmap`/`srs_verify` không bị ảnh hưởng)

- [ ] **Step 3: Build zip và kiểm support dir được đóng gói**

Run:
```bash
cd /e/agent-skills && bash speckit-extension/build-zip.sh && \
unzip -l speckit-extension/dist/dft-speckit-0.2.0.zip | grep -E "fnlist_tree|fnlist_import|functions-schema"
```
Expected: cả ba đều xuất hiện — `scripts/fnlist_tree.py`, `scripts/fnlist_import.py`, `references/functions-schema.md`. Thiếu `fnlist_tree.py` là command gãy trong bản cài (script import module cạnh nó), thiếu `functions-schema.md` là command trỏ vào file không tồn tại.

- [ ] **Step 4: Chạy script từ trong zip đã giải nén**

Run:
```bash
cd /tmp && rm -rf fnlist-pkg && mkdir fnlist-pkg && \
unzip -q /e/agent-skills/speckit-extension/dist/dft-speckit-0.2.0.zip -d fnlist-pkg && \
cd fnlist-pkg && printf 'STT,Ten,Mo ta\n1,A,\n1.1,A1,x\n' > fn.csv && \
printf '{"first_data_row":1,"columns":{"name":1,"description":2},"hierarchy":{"mode":"outline","column":0}}' > map.json && \
python scripts/fnlist_import.py write fn.csv --mapping map.json --out functions.json --system PKG --date 2026-08-11 --sheet fn
```
Expected: exit 0, in `"written": 2`. Lỗi `ModuleNotFoundError: fnlist_tree` nghĩa là `build-zip.sh` chưa copy module mới — sửa `build-zip.sh` rồi chạy lại từ Step 3.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/extension.yml
git commit -m "chore(fnlist): bump 0.2.0, cập nhật description theo functions.json"
```

---

## Self-Review

**Spec coverage:**

| Mục spec | Task |
|---|---|
| §1 `functions.json` là output duy nhất, bỏ `functions.md` | Task 6 (gỡ render), Task 7 (ghi JSON) |
| §2 Schema 5 trường, bỏ `cum`/`nguon_code`/`level` | Task 1 (`clean_node`, `build_document`) |
| §3 Năm quy tắc ID | Task 4 (`assign_ids`, `compute_retired`), Task 5 (nhãn `chuyển nhóm`) |
| §4 Ba subcommand, script độc quyền ghi | Task 6 (`inspect`), Task 7 (`write`), Task 8 (`update`) |
| §5 Ba kiểu phân cấp + checkpoint cây | Task 2 (dò), Task 3 (dựng), Task 10 (checkpoint) |
| §6 `references/functions-schema.md` | Task 9, kiểm đóng gói ở Task 11 |
| §7 Tác động sang 2 lệnh kia | **Cố ý không làm** — đợt sau, theo Global Constraints |
| "Hệ quả hai đợt": không xoá `functions.md` cũ, không nhắc chạy `code-intel` | Task 10 (bước 7 + mục sai lầm) |
| Rủi ro "dựng cây dễ sai âm thầm" | Task 3 (chặn nhảy cấp, test cả 3 mode), Task 10 (checkpoint cây) |

Không có mục spec nào thiếu task.

**Trường `retired_ids` không có trong spec** — phát sinh khi cài đặt quy tắc §3.4 ("số đã
xoá bỏ trống vĩnh viễn"): không lưu lại thì số của node cuối bị xoá sẽ được cấp lại cho
node mới. Đây là trường ở **mức tài liệu**, không phải mức node, nên không phá ràng buộc
"node đúng 5 trường". Đã ghi vào `references/functions-schema.md` (Task 9).

**Type consistency:** `walk`/`name_path`/`find_by_id`/`clean_node`/`build_document`
(Task 1) → dùng lại nguyên tên ở Task 4, 5, 7, 8. `detect_hierarchy` (Task 2) → Task 6.
`build_tree` (Task 3) → Task 7. `assign_ids`/`carry_status`/`compute_retired` (Task 4) →
Task 7. `diff_trees` (Task 5) → Task 7. `load_document`/`save_document` (Task 7) → Task 8.
Khoá của `mapping.json` (`first_data_row`, `columns.name`, `columns.description`,
`hierarchy.mode`, `hierarchy.column`, `hierarchy.level_columns`, `hierarchy.style`,
`skip_rows`) dùng thống nhất từ Task 2 tới Task 10.
