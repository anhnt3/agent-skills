# `code-intel` theo cây `functions.json` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Viết lại `code-intel` để quét theo cây `functions.json` thay vì bảng phẳng `functions.md` — tham số hợp nhất (một FN-ID đánh dấu điểm bắt đầu), thư mục sinh ra đánh số theo cấu trúc cây thật, quét hàng loạt qua subagent/loop, và hai script mới đảm nhận phần tính toán/xác minh tất định.

**Architecture:** `intel_tree.py` (mới) tính unit mặc định + slug + đường dẫn thư mục từ `functions.json`, thuần logic không I/O ngoài đọc file đầu vào qua CLI. `intel_verify.py` (mới) chấm một `intel.md` đã viết theo hai mức BLOCKING/WARNING, cùng vai trò `srs_verify.py`. `fnlist_tree.py` được bổ sung một hàm dùng chung `subtree_leaves`. LLM (qua `commands/code-intel.md` đã viết lại) giữ toàn bộ phần tìm kiếm code, viết nội dung, phán đoán §10.

**Tech Stack:** Python 3 (stdlib only), pytest.

**Spec:** `docs/superpowers/specs/2026-08-12-code-intel-tree-batch-design.md`

## Global Constraints

- Nội dung tài liệu, thông điệp lỗi, comment code: **tiếng Việt**. Tên hàm, tên file, flag CLI: **tiếng Anh**.
- Không thêm phụ thuộc ngoài stdlib cho cả hai script mới.
- FN-ID khớp `ID_RE` của `fnlist_tree.py`: `^FN(?:-\d{2})+$` (nhiều cấp, mỗi cấp 2 chữ số).
- `functions.json` là nguồn sự thật duy nhất — hai script mới chỉ **đọc**, không bao giờ ghi vào nó. Ghi trạng thái luôn qua `fnlist_import.py update` (đã có sẵn từ đợt trước, không sửa trong plan này).
- Unit mặc định = node có tất cả con đều là lá, hoặc node không có con đứng một mình (xem `docs/superpowers/specs/2026-08-12-code-intel-tree-batch-design.md` §2).
- Thư mục: `<hai-chữ-số-vị-trí>-<slug>`, độ sâu = độ sâu thật của cây tại nhánh đó. Slug do Python sinh tất định, không giao LLM đặt tên.
- `srs-from-code.md` **không đổi** trong plan này.
- Chạy test từ gốc repo: `python -m pytest speckit-extension/scripts/tests/<file> -v`.

## File Structure

| File | Trách nhiệm |
|---|---|
| `speckit-extension/scripts/fnlist_tree.py` | **Sửa nhỏ.** Thêm `subtree_leaves()` — dùng chung bởi cả hai script mới. |
| `speckit-extension/scripts/intel_tree.py` | **Mới.** Tính unit mặc định, sinh slug, tính đường dẫn thư mục, CLI `propose`/`units`. |
| `speckit-extension/scripts/intel_verify.py` | **Mới.** Chấm `intel.md`: BLOCKING (placeholder, phủ §1, trần §8, tỉ lệ không-tìm-thấy, no-clobber §8/§10) + WARNING (cite mờ, mỏ neo §2). |
| `speckit-extension/scripts/tests/test_fnlist_tree.py` | **Thêm vào cuối.** Test `subtree_leaves`. |
| `speckit-extension/scripts/tests/test_intel_tree.py` | **Mới.** |
| `speckit-extension/scripts/tests/test_intel_verify.py` | **Mới.** |
| `speckit-extension/templates/intel-template.md` | **Sửa.** Bỏ cú pháp bracket cho "chưa trả lời"/"đang chờ" (tránh đâm với bộ dò placeholder), đổi tiêu đề từ cụm sang unit. |
| `speckit-extension/commands/code-intel.md` | **Viết lại toàn bộ.** Tham số hợp nhất, quy trình tính unit + xác nhận + batch, gọi hai script mới, gọi `update` trực tiếp. |
| `speckit-extension/extension.yml` | Sửa `description` của command `code-intel`, bump version. |

---

### Task 1: `subtree_leaves` trong `fnlist_tree.py`

**Files:**
- Modify: `speckit-extension/scripts/fnlist_tree.py` (thêm vào cuối)
- Test: `speckit-extension/scripts/tests/test_fnlist_tree.py` (thêm vào cuối, dùng lại `_mk`/`_prepared` đã có sẵn trong file — không định nghĩa lại)

**Interfaces:**
- Consumes: (không dùng gì mới)
- Produces: `subtree_leaves(node: dict) -> list[dict]` — mọi node lá thuộc nhánh của `node`, gồm cả chính nó nếu nó là lá.

- [ ] **Step 1: Viết test thất bại**

Thêm vào cuối `speckit-extension/scripts/tests/test_fnlist_tree.py`:

```python
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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v -k subtree_leaves`
Expected: FAIL — `AttributeError: module 'fnlist_tree' has no attribute 'subtree_leaves'`

- [ ] **Step 3: Cài đặt**

Thêm vào cuối `speckit-extension/scripts/fnlist_tree.py`:

```python
def subtree_leaves(node):
    """Mọi node lá thuộc nhánh của `node`, gồm cả CHÍNH NÓ nếu nó là lá. Dùng
    bởi code-intel để tính danh sách FN-ID một unit phải phủ, không đệ quy lại
    logic duyệt cây ở một chỗ khác."""
    children = node.get("children") or []
    if not children:
        return [node]
    out = []
    for c in children:
        out.extend(subtree_leaves(c))
    return out
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_fnlist_tree.py -v`
Expected: PASS — toàn bộ test cũ (46) + 3 test mới = 49 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_tree.py speckit-extension/scripts/tests/test_fnlist_tree.py
git commit -m "feat(code-intel): thêm subtree_leaves dùng chung cho intel_tree/intel_verify"
```

---

### Task 2: `intel_tree.py` — slug, is_leaf, default_units

**Files:**
- Create: `speckit-extension/scripts/intel_tree.py`
- Test: `speckit-extension/scripts/tests/test_intel_tree.py`

**Interfaces:**
- Consumes: (không dùng gì từ Task 1 ở phần này — `subtree_leaves` được dùng ở Task 3)
- Produces:
  - `slugify(name: str) -> str`
  - `dedupe_slugs(slugs: list[str]) -> list[str]`
  - `is_leaf(node: dict) -> bool`
  - `is_leaf_parent(node: dict) -> bool`
  - `default_units(node: dict) -> list[dict]`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_intel_tree.py`:

```python
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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'intel_tree'`

- [ ] **Step 3: Cài đặt**

Tạo `speckit-extension/scripts/intel_tree.py`:

```python
#!/usr/bin/env python3
"""Cây đơn vị rút đặc tả (unit) cho code-intel: tính node nào là "cha trực
tiếp của lá" (unit mặc định), sinh slug thư mục tất định, tính đường dẫn.

Thuần logic — không đọc/ghi file ngoài đọc functions.json qua CLI ở cuối file
này, không tìm code, không viết nội dung intel.md. `code-intel` (command) đọc
kết quả, LLM trình cây cho người dùng xác nhận, rồi gọi lại `units` với danh
sách root đã chốt để lấy đường dẫn + danh sách FN-ID.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import fnlist_tree as ft

def _force_utf8_console() -> None:
    """Windows mở subprocess với stdout/stderr mã cp1252 mặc định, không phải
    UTF-8 — in tiếng Việt có dấu ra đó là crash UnicodeEncodeError. Ép lại UTF-8
    khi có thể; capsys của pytest thay stdout bằng đối tượng không có
    `reconfigure` nên phải hasattr trước."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        enc = getattr(stream, "encoding", None)
        if enc and enc.lower() != "utf-8" and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_force_utf8_console()

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")
_MAX_SLUG_LEN = 60


def slugify(name: str) -> str:
    """Tên tiếng Việt có dấu → slug ASCII tất định, dùng làm tên thư mục.
    Tất định là bắt buộc: chạy lại phải ra đúng slug cũ để no-clobber còn
    khớp được thư mục — đây KHÔNG phải việc LLM tự đặt tên mỗi lần."""
    s = name.replace("Đ", "D").replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = _SLUG_STRIP_RE.sub("-", s.lower()).strip("-")
    if len(s) > _MAX_SLUG_LEN:
        s = s[:_MAX_SLUG_LEN].rstrip("-")
    return s or "khong-ten"


def dedupe_slugs(slugs: list[str]) -> list[str]:
    """Hai anh em trùng slug sau khi sinh (tên khác nhau, slug giống nhau) →
    hậu tố -2, -3… theo thứ tự xuất hiện."""
    seen: dict[str, int] = {}
    out = []
    for s in slugs:
        seen[s] = seen.get(s, 0) + 1
        out.append(s if seen[s] == 1 else f"{s}-{seen[s]}")
    return out


def is_leaf(node: dict) -> bool:
    return not node.get("children")


def is_leaf_parent(node: dict) -> bool:
    """Node có TẤT CẢ con đều là lá — điều kiện unit mặc định."""
    children = node.get("children") or []
    return bool(children) and all(is_leaf(c) for c in children)


def default_units(node: dict) -> list[dict]:
    """Từ một node, trả danh sách node là "unit" theo luật cha-trực-tiếp-của-
    lá. Một lá đứng lẻ dưới cha có con hỗn hợp (vài con là lá, vài con có
    cháu) tự thành unit riêng — nhánh `is_leaf` khớp trước khi xét
    `is_leaf_parent` nên nó không bị gộp lên cha."""
    if is_leaf(node) or is_leaf_parent(node):
        return [node]
    out = []
    for c in node["children"]:
        out.extend(default_units(c))
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description="Tính unit/slug/đường dẫn cho code-intel")
    a = p.parse_args(argv)


if __name__ == "__main__":
    main()
```

(CLI thật — `propose`/`units` — được thêm ở Task 3. `main()` để trống có chủ đích ở bước này, chỉ để file chạy được như một module hợp lệ.)

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_tree.py speckit-extension/scripts/tests/test_intel_tree.py
git commit -m "feat(code-intel): intel_tree.py — slug tất định, luật unit cha-trực-tiếp-của-lá"
```

---

### Task 3: `intel_tree.py` — đường dẫn, cây thụt lề, CLI `propose`/`units`

**Files:**
- Modify: `speckit-extension/scripts/intel_tree.py`
- Test: `speckit-extension/scripts/tests/test_intel_tree.py` (thêm vào cuối)

**Interfaces:**
- Consumes: `slugify`, `dedupe_slugs`, `default_units` (Task 2); `ft.find_by_id`, `ft.subtree_leaves` (Task 1, `fnlist_tree.py`)
- Produces:
  - `compute_paths(nodes: list[dict], prefix: str = "") -> dict[str, str]` — `{FN-ID: đường dẫn thư mục}` cho mọi node trong cây (đệ quy).
  - `render_tree(nodes: list[dict], unit_ids: set[str], depth: int = 0) -> list[str]`
  - CLI `propose --functions PATH [--start FN-ID]` → in JSON `{"units": [{"id","name"}], "tree": "..."}`
  - CLI `units --functions PATH --roots FN-ID[,FN-ID...]` → in JSON `{"units": [{"id","name","path","fn_ids": [{"id","name","status"}]}]}`

- [ ] **Step 1: Viết test thất bại**

Thêm vào cuối `speckit-extension/scripts/tests/test_intel_tree.py`:

```python
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
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -v -k "compute_paths or render_tree or cli"`
Expected: FAIL — `AttributeError: module 'intel_tree' has no attribute 'compute_paths'`

- [ ] **Step 3: Cài đặt**

Thêm vào `speckit-extension/scripts/intel_tree.py`, ngay sau `default_units`:

```python
def compute_paths(nodes: list[dict], prefix: str = "") -> dict[str, str]:
    """Trả {FN-ID: đường dẫn thư mục} cho MỌI node trong `nodes` (đệ quy toàn
    cây). Số thứ tự lấy theo vị trí trong `children` (khớp thứ tự dòng file
    nguồn), không phải số trong FN-ID — FN-ID có thể đổi khi cấp lại theo luật
    của fnlist-import, vị trí hiển thị thì không cần khớp theo nó."""
    slugs = dedupe_slugs([slugify(n["name"]) for n in nodes])
    out: dict[str, str] = {}
    for i, (node, slug) in enumerate(zip(nodes, slugs), start=1):
        path = f"{prefix}{i:02d}-{slug}"
        out[node["id"]] = path
        out.update(compute_paths(node.get("children") or [], path + "/"))
    return out


def render_tree(nodes: list[dict], unit_ids: set[str], depth: int = 0) -> list[str]:
    """Cây thụt lề, đánh dấu `[UNIT]` ở node là ranh giới unit đề xuất — để
    LLM trình cho người dùng xác nhận/điều chỉnh trước khi quét."""
    lines = []
    for node in nodes:
        marker = "  [UNIT]" if node["id"] in unit_ids else ""
        lines.append("  " * depth + f"{node['name']} ({node['id']}){marker}")
        lines.extend(render_tree(node.get("children") or [], unit_ids, depth + 1))
    return lines


def cmd_propose(a) -> None:
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    if a.start:
        node = ft.find_by_id(tree, a.start)
        if node is None:
            raise SystemExit(f"Không có {a.start} trong {a.functions}.")
        roots = [node]
    else:
        roots = tree
    units: list[dict] = []
    for node in roots:
        units.extend(default_units(node))
    unit_ids = {u["id"] for u in units}
    out = {
        "units": [{"id": u["id"], "name": u["name"]} for u in units],
        "tree": "\n".join(render_tree(roots, unit_ids)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_units(a) -> None:
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    paths = compute_paths(tree)
    out = {"units": []}
    for root_id in a.roots.split(","):
        root_id = root_id.strip()
        node = ft.find_by_id(tree, root_id)
        if node is None:
            raise SystemExit(f"Không có {root_id} trong {a.functions}.")
        leaves = ft.subtree_leaves(node)
        out["units"].append({
            "id": node["id"],
            "name": node["name"],
            "path": paths[node["id"]] + "/intel.md",
            "fn_ids": [{"id": lf["id"], "name": lf["name"],
                       "status": lf.get("status", "pending")} for lf in leaves],
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))
```

Thay `main()` (bản để trống ở Task 2) bằng:

```python
def main(argv=None):
    p = argparse.ArgumentParser(description="Tính unit/slug/đường dẫn cho code-intel")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("propose", help="Đề xuất unit mặc định + cây thụt lề")
    pr.add_argument("--functions", default=".specify/docs/functions.json")
    pr.add_argument("--start", default=None,
                    help="FN-ID điểm bắt đầu; trống = toàn bộ cây")
    pr.set_defaults(func=cmd_propose)

    un = sub.add_parser("units", help="Tính đường dẫn + danh sách FN-ID cho unit đã chốt")
    un.add_argument("--functions", default=".specify/docs/functions.json")
    un.add_argument("--roots", required=True,
                    help="Danh sách FN-ID, ngăn cách bằng dấu phẩy")
    un.set_defaults(func=cmd_units)

    a = p.parse_args(argv)
    a.func(a)
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -v`
Expected: PASS — 24 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_tree.py speckit-extension/scripts/tests/test_intel_tree.py
git commit -m "feat(code-intel): intel_tree.py CLI propose/units — đường dẫn + cây thụt lề"
```

---

### Task 4: `intel_verify.py` — parsing + BLOCKING checks

**Files:**
- Create: `speckit-extension/scripts/intel_verify.py`
- Test: `speckit-extension/scripts/tests/test_intel_verify.py`

**Interfaces:**
- Consumes: (không dùng gì từ Task 1-3 ở phần này — hàm đọc `functions.json` để tính `expected` được nối ở Task 5 phần CLI)
- Produces:
  - `find_placeholders(text: str) -> list[dict]`
  - `parse_section1(text: str) -> dict[str, str]` — `{FN-ID: nội dung cột "Tìm thấy ở đâu"}`
  - `parse_numbered_items(text: str, number: int) -> list[dict]` — mỗi phần tử `{"label": str|None, "content": str}`
  - `parse_section10_rows(text: str) -> list[tuple]` — tuple 4 cột gốc, bỏ cột Kết luận
  - `check_section1_coverage(text, expected: list[dict]) -> list[dict]`
  - `check_not_found_ratio(text, expected: list[dict]) -> list[dict]`
  - `check_section8_cap(text, m: int) -> list[dict]`
  - `check_no_clobber_8(text, before: str) -> list[dict]`
  - `check_no_clobber_10(text, before: str) -> list[dict]`

**Ghi chú quan trọng về khung `intel-template.md`** (Task 6 sẽ áp dụng, nhưng test ở đây phải khớp trước):
mục §8 dùng `— **Trả lời**: _(chưa có)_` cho câu chưa trả lời (KHÔNG dùng `[để trống...]` — chuỗi trong ngoặc vuông sẽ bị `find_placeholders` coi là placeholder chưa điền, chặn nhầm một tài liệu hoàn toàn hợp lệ đang có câu hỏi chưa trả lời). Nhãn loại (`[không suy được từ code]` …) vẫn giữ ngoặc vuông — đây là nhãn phân loại cố định, không phải chỗ điền nội dung, nên `find_placeholders` phải loại trừ đúng bốn nhãn này. Cột `Kết luận` ở §10 ghi `đang chờ` (không ngoặc vuông) khi chưa có kết luận.

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_intel_verify.py`:

```python
import json
import sys
from pathlib import Path

import pytest

import intel_verify as iv

EXPECTED = [
    {"id": "FN-01-01", "name": "Đăng nhập"},
    {"id": "FN-01-02", "name": "Quên mật khẩu"},
]

INTEL_OK = """# Code intel — Xác thực

**Cập nhật**: 2026-08-12
**Phủ chức năng**: FN-01-01, FN-01-02

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| FN-01-01 | Đăng nhập | src/auth/login.ts:10 | — |
| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |
| Quên mật khẩu | /forgot | src/auth/reset.ts:5 | FN-01-02 |

## 3. Thực thể và trường dữ liệu

Không có.

## 4. Kiểm tra hợp lệ và quy tắc nghiệp vụ

Không có.

## 5. Luồng nghiệp vụ

Không có.

## 6. Phân quyền

Không có.

## 7. Tích hợp ngoài, tác vụ nền, sự kiện

Không có.

## 8. Không suy được từ code — câu hỏi cho người

1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_

## 9. Thông báo hiển thị

| Ngữ cảnh | Nguyên văn thông báo | Nguồn |
| --- | --- | --- |
| Sai mật khẩu | "Email hoặc mật khẩu không đúng" | src/auth/login.ts:22 |

## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật

Không có.
"""


def test_clean_document_has_no_blocking():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert r["blocking"] == []


def test_missing_fn_in_section1_is_blocking():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n", "")
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "thieu-fn-o-muc-1" and "FN-01-02" in b["thong_diep"]
               for b in r["blocking"])


def test_extra_fn_in_section1_is_blocking():
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n",
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n"
        "| FN-99-99 | Lạc | không tìm thấy | — |\n")
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "thua-fn-o-muc-1" and "FN-99-99" in b["thong_diep"]
               for b in r["blocking"])


def test_not_found_ratio_over_one_third_is_blocking():
    text = (INTEL_OK
            .replace("src/auth/login.ts:10 | —", "không tìm thấy | —")
            .replace("src/auth/reset.ts:5 | —", "không tìm thấy | —"))
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "ti-le-khong-tim-thay-vuot-nguong" for b in r["blocking"])


def test_placeholder_left_over_is_blocking():
    text = INTEL_OK + "\n## Phụ lục — [Tên phụ lục]\n"
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "placeholder" for b in r["blocking"])


def test_known_label_bracket_is_not_a_placeholder():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_section8_cap_blocks_when_exceeded():
    items = "\n".join(
        f"{i}. [không suy được từ code] Câu hỏi số {i}? — **Trả lời**: _(chưa có)_"
        for i in range(1, 5))
    text = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        items)
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "tran-muc-8-vuot-nguong" for b in r["blocking"])


def test_section8_duplicate_reason_blocks():
    items = "\n".join(
        f"{i}. [không suy được từ code] Cùng một lý do — **Trả lời**: _(chưa có)_"
        for i in range(1, 4))
    text = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        items)
    r = iv.verify(text, EXPECTED)
    assert any(b["loai"] == "muc-8-lap-ly-do" for b in r["blocking"])


def test_no_clobber_8_blocks_when_old_item_dropped():
    before = INTEL_OK
    after = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        "1. [chính sách nghiệp vụ] Câu hỏi khác hẳn — **Trả lời**: _(chưa có)_")
    r = iv.verify(after, EXPECTED, before=before)
    assert any(b["loai"] == "mat-noi-dung-muc-8" for b in r["blocking"])


def test_no_clobber_8_passes_when_old_item_kept_and_new_added():
    before = INTEL_OK
    after = INTEL_OK.replace(
        "## 9. Thông báo hiển thị",
        "2. [không suy được từ code] Câu hỏi mới — **Trả lời**: _(chưa có)_\n\n"
        "## 9. Thông báo hiển thị")
    r = iv.verify(after, EXPECTED, before=before)
    assert not any(b["loai"] == "mat-noi-dung-muc-8" for b in r["blocking"])


def test_no_clobber_10_blocks_when_old_row_dropped():
    before = INTEL_OK.replace(
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "Không có.",
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "| # | Loại | Mô tả | Nguồn | Kết luận |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 1 | logic mâu thuẫn | Hai nhánh kiểm mật khẩu khác nhau | "
        "src/auth/login.ts:30, src/auth/reset.ts:12 | đang chờ |")
    after = INTEL_OK  # bản mới đánh mất dòng §10
    r = iv.verify(after, EXPECTED, before=before)
    assert any(b["loai"] == "mat-noi-dung-muc-10" for b in r["blocking"])


def test_no_clobber_10_ignores_ket_luan_column_changes():
    before = INTEL_OK.replace(
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "Không có.",
        "## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật\n\n"
        "| # | Loại | Mô tả | Nguồn | Kết luận |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 1 | logic mâu thuẫn | Hai nhánh kiểm mật khẩu khác nhau | "
        "src/auth/login.ts:30 | đang chờ |")
    after = before.replace("| đang chờ |", "| cố ý — đã xác nhận |")
    r = iv.verify(after, EXPECTED, before=before)
    assert not any(b["loai"] == "mat-noi-dung-muc-10" for b in r["blocking"])
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'intel_verify'`

- [ ] **Step 3: Cài đặt**

Tạo `speckit-extension/scripts/intel_verify.py`:

```python
#!/usr/bin/env python3
"""Chấm một `intel.md` (unit theo cây functions.json) trước khi báo xong.

Hai mức, cùng nguyên tắc với srs_verify.py:
  BLOCKING (exit 1) — chỉ thứ kiểm được TẤT ĐỊNH: placeholder còn sót, §1
                      thiếu/thừa FN-ID so với functions.json, trần §8, tỉ lệ
                      "không tìm thấy" vượt ngưỡng, no-clobber §8/§10.
  WARNING  (exit 0) — thứ cần phán đoán: cite trông không giống file:dòng, FN
                      tìm thấy nhưng không xuất hiện ở §2/§7/§8.

Chỉ cần python3 + fnlist_tree (cùng thư mục scripts/), không phụ thuộc ngoài
stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import fnlist_tree as ft

def _force_utf8_console() -> None:
    """Windows mở subprocess với stdout/stderr mã cp1252 mặc định, không phải
    UTF-8 — in tiếng Việt có dấu ra đó là crash UnicodeEncodeError. Ép lại UTF-8
    khi có thể; capsys của pytest thay stdout bằng đối tượng không có
    `reconfigure` nên phải hasattr trước."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        enc = getattr(stream, "encoding", None)
        if enc and enc.lower() != "utf-8" and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_force_utf8_console()

FN_ID_RE = re.compile(r"\bFN(?:-\d{2})+\b")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FENCE_RE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PLACEHOLDER_RE = re.compile(r"\[([^\[\]\n]{1,80})\](?!\()")
CODE_PATH_RE = re.compile(
    r"\b[\w.-]+/[\w./-]*\.\w{1,5}\b(?::\d+)?"
    r"|\b\w[\w.-]*\.(?:py|ts|tsx|js|jsx|java|cs|go|rb|php|vue|sql|kt|swift|yml|yaml)\b(?::\d+)?"
)
LABEL_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
# Bốn nhãn loại cố định của §8 — đây là nhãn phân loại, không phải chỗ điền
# nội dung, nên KHÔNG được tính là placeholder chưa điền.
KNOWN_LABEL_RE = re.compile(
    r"^(không suy được từ code|chính sách nghiệp vụ|FN không tìm thấy|"
    r"chờ trả lời từ lần trước)$")


def strip_noise(text: str) -> str:
    """Bỏ HTML comment, khối code rào, và inline code — cùng lý do với
    srs_verify.py: cả ba có thể chứa dấu [] hợp lệ (hướng dẫn khung, ví dụ)."""
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def find_placeholders(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(strip_noise(text).splitlines(), start=1):
        for m in PLACEHOLDER_RE.finditer(line):
            if KNOWN_LABEL_RE.match(m.group(1).strip()):
                continue
            out.append({"line": i, "text": m.group(0)})
    return out


def _table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def _section_body(text: str, number: int) -> str:
    """Nội dung mục '## <number>.' tới trước mục '## <số khác>.' kế tiếp."""
    lines = strip_noise(text).splitlines()
    start = end = None
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+(\d+)\.", ln.strip())
        if m and int(m.group(1)) == number:
            start = i + 1
        elif start is not None and re.match(r"^##\s+\d+\.", ln.strip()):
            end = i
            break
    if start is None:
        return ""
    return "\n".join(lines[start: end if end is not None else len(lines)])


def parse_section1(text: str) -> dict[str, str]:
    """§1 'Phủ chức năng' → {FN-ID: nội dung cột 'Tìm thấy ở đâu'}."""
    out = {}
    for row in _table_rows(_section_body(text, 1)):
        if row and FN_ID_RE.fullmatch(row[0]):
            out[row[0]] = row[2] if len(row) > 2 else ""
    return out


def parse_numbered_items(text: str, number: int) -> list[dict]:
    """Mục kiểu danh sách (§8): dòng '<n>. [nhãn] nội dung'. Trả cả nhãn lẫn
    nội dung để tính trần và no-clobber."""
    out = []
    for ln in _section_body(text, number).splitlines():
        m = re.match(r"^\d+\.\s+(.*)$", ln.strip())
        if not m:
            continue
        rest = m.group(1)
        lm = LABEL_RE.match(rest)
        label, content = (lm.group(1), lm.group(2)) if lm else (None, rest)
        out.append({"label": label, "content": content.strip()})
    return out


def parse_section10_rows(text: str) -> list[tuple]:
    """§10 là BẢNG, không phải danh sách — trả tuple 4 cột gốc
    (#, Loại, Mô tả, Nguồn), bỏ cột Kết luận (không tính vào so no-clobber vì
    đó là cột duy nhất `srs-from-code` được phép cập nhật sau)."""
    out = []
    for row in _table_rows(_section_body(text, 10)):
        if row and row[0].strip().isdigit():
            out.append(tuple(c.strip() for c in row[:4]))
    return out


def check_section1_coverage(text: str, expected: list[dict]) -> list[dict]:
    got = parse_section1(text)
    want_ids = {f["id"] for f in expected}
    missing = want_ids - set(got)
    extra = set(got) - want_ids
    out = []
    if missing:
        out.append({"loai": "thieu-fn-o-muc-1",
                    "thong_diep": "§1 thiếu dòng cho: " + ", ".join(sorted(missing))})
    if extra:
        out.append({"loai": "thua-fn-o-muc-1",
                    "thong_diep": "§1 có FN-ID không thuộc unit này: "
                                   + ", ".join(sorted(extra))})
    return out


def check_not_found_ratio(text: str, expected: list[dict]) -> list[dict]:
    got = parse_section1(text)
    m = len(expected)
    not_found = sum(1 for v in got.values() if "không tìm thấy" in v)
    if m and not_found > m / 3:
        return [{"loai": "ti-le-khong-tim-thay-vuot-nguong",
                 "thong_diep": f"{not_found}/{m} FN không tìm thấy, vượt 1/3 — "
                                "có thể đang quét sai nhánh/sai phạm vi."}]
    return []


def check_section8_cap(text: str, m: int) -> list[dict]:
    items = parse_numbered_items(text, 8)
    labeled = [i for i in items if i["label"] == "không suy được từ code"]
    cap = max(3, m / 3)
    out = []
    if len(labeled) > cap:
        out.append({"loai": "tran-muc-8-vuot-nguong",
                    "thong_diep": f"{len(labeled)} mục nhãn 'không suy được từ code', "
                                   f"vượt ngưỡng {cap:.1f}."})
    by_reason: dict[str, int] = {}
    for i in items:
        key = i["content"].split("—")[0].strip()
        by_reason[key] = by_reason.get(key, 0) + 1
    dup = [k for k, c in by_reason.items() if c >= 3]
    if dup:
        out.append({"loai": "muc-8-lap-ly-do",
                    "thong_diep": "≥3 mục dùng cùng một lý do: " + "; ".join(dup)})
    return out


def check_no_clobber_8(text: str, before: str) -> list[dict]:
    old_items = {i["content"] for i in parse_numbered_items(before, 8)}
    new_items = {i["content"] for i in parse_numbered_items(text, 8)}
    missing = old_items - new_items
    if missing:
        return [{"loai": "mat-noi-dung-muc-8",
                 "thong_diep": f"{len(missing)} mục §8 cũ không còn thấy nguyên văn "
                                "trong bản mới."}]
    return []


def check_no_clobber_10(text: str, before: str) -> list[dict]:
    old_rows = set(parse_section10_rows(before))
    new_rows = set(parse_section10_rows(text))
    missing = old_rows - new_rows
    if missing:
        return [{"loai": "mat-noi-dung-muc-10",
                 "thong_diep": f"{len(missing)} dòng §10 cũ không còn khớp nguyên văn "
                                "trong bản mới (4 cột #/Loại/Mô tả/Nguồn)."}]
    return []


def verify(text: str, expected: list[dict], before: str | None = None) -> dict:
    blocking: list[dict] = []
    m = len(expected)

    for ph in find_placeholders(text):
        blocking.append({"loai": "placeholder",
                         "thong_diep": f"Còn placeholder ở dòng {ph['line']}: {ph['text']}"})

    blocking.extend(check_section1_coverage(text, expected))
    blocking.extend(check_not_found_ratio(text, expected))
    blocking.extend(check_section8_cap(text, m))
    if before is not None:
        blocking.extend(check_no_clobber_8(text, before))
        blocking.extend(check_no_clobber_10(text, before))

    return {"blocking": blocking, "warnings": []}
```

(Hàm `verify()` ở bước này CHƯA có WARNING — Task 5 nối thêm `check_cite_quality`/
`check_section2_anchor` vào `warnings`. `main()`/CLI cũng được thêm ở Task 5.)

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v`
Expected: PASS — 13 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_verify.py speckit-extension/scripts/tests/test_intel_verify.py
git commit -m "feat(code-intel): intel_verify.py — cổng BLOCKING (phủ §1, trần §8, no-clobber)"
```

---

### Task 5: `intel_verify.py` — WARNING checks + CLI

**Files:**
- Modify: `speckit-extension/scripts/intel_verify.py`
- Test: `speckit-extension/scripts/tests/test_intel_verify.py` (thêm vào cuối)

**Interfaces:**
- Consumes: `_table_rows`, `_section_body`, `parse_section1`, `CODE_PATH_RE`, `verify` (Task 4); `ft.find_by_id`, `ft.subtree_leaves` (Task 1)
- Produces:
  - `check_cite_quality(text: str) -> list[dict]`
  - `check_section2_anchor(text: str, expected: list[dict]) -> list[dict]`
  - `verify()` sửa lại để gọi cả hai hàm trên, đổ vào `warnings`
  - `main(argv=None)` — CLI: `intel_verify.py <intel.md> --functions PATH --root FN-ID [--before PATH]`

- [ ] **Step 1: Viết test thất bại**

Thêm vào cuối `speckit-extension/scripts/tests/test_intel_verify.py`:

```python
def test_cite_without_source_or_suy_doan_is_warning():
    text = INTEL_OK.replace(
        "| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
        "| Đăng nhập | /login | không rõ | FN-01-01 |")
    r = iv.verify(text, EXPECTED)
    assert r["blocking"] == []
    assert any(w["loai"] == "cite-khong-ro" for w in r["warnings"])


def test_cite_marked_suy_doan_is_not_a_warning():
    text = INTEL_OK.replace(
        "| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
        "| Đăng nhập | /login | (suy đoán, gần src/auth/) | FN-01-01 |")
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "cite-khong-ro" for w in r["warnings"])


def test_fn_found_but_absent_from_section2_is_warning():
    text = INTEL_OK.replace(
        "| Quên mật khẩu | /forgot | src/auth/reset.ts:5 | FN-01-02 |\n", "")
    r = iv.verify(text, EXPECTED)
    assert any(w["loai"] == "fn-khong-co-mat-o-muc-2" and "FN-01-02" in w["thong_diep"]
               for w in r["warnings"])


def test_fn_not_found_at_section1_is_excused_from_anchor_check():
    text = (INTEL_OK
            .replace("| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |",
                     "| FN-01-02 | Quên mật khẩu | không tìm thấy | — |")
            .replace("| Quên mật khẩu | /forgot | src/auth/reset.ts:5 | FN-01-02 |\n", ""))
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "fn-khong-co-mat-o-muc-2" and "FN-01-02" in w["thong_diep"]
                   for w in r["warnings"])


def _write_functions_json(tmp_path):
    doc = {"functions": [
        {"id": "FN-01", "name": "Xac thuc", "description": "", "children": [
            {"id": "FN-01-01", "name": "Đăng nhập", "description": "", "children": []},
            {"id": "FN-01-02", "name": "Quên mật khẩu", "description": "", "children": []},
        ]},
    ]}
    fp = tmp_path / "functions.json"
    fp.write_text(json.dumps(doc), encoding="utf-8")
    return fp


def _run(tmp_path, intel_text, before_text=None):
    import subprocess
    intel = tmp_path / "intel.md"
    intel.write_text(intel_text, encoding="utf-8")
    fp = _write_functions_json(tmp_path)
    cmd = [sys.executable, str(Path(iv.__file__)), str(intel),
           "--functions", str(fp), "--root", "FN-01"]
    if before_text is not None:
        before = tmp_path / "before.md"
        before.write_text(before_text, encoding="utf-8")
        cmd += ["--before", str(before)]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def test_cli_exits_zero_when_clean(tmp_path):
    p = _run(tmp_path, INTEL_OK)
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout)["blocking"] == []


def test_cli_exits_one_when_blocking(tmp_path):
    text = INTEL_OK.replace(
        "| FN-01-02 | Quên mật khẩu | src/auth/reset.ts:5 | — |\n", "")
    p = _run(tmp_path, text)
    assert p.returncode == 1
    assert json.loads(p.stdout)["blocking"]


def test_cli_before_flag_enables_no_clobber_check(tmp_path):
    before = INTEL_OK
    after = INTEL_OK.replace(
        "1. [chính sách nghiệp vụ] Số lần đăng nhập sai tối đa trước khi khoá "
        "tài khoản là bao nhiêu? — **Trả lời**: _(chưa có)_",
        "1. [chính sách nghiệp vụ] Câu hỏi khác hẳn — **Trả lời**: _(chưa có)_")
    p = _run(tmp_path, after, before_text=before)
    assert p.returncode == 1
    assert any(b["loai"] == "mat-noi-dung-muc-8" for b in json.loads(p.stdout)["blocking"])


def test_cli_reports_missing_root(tmp_path):
    import subprocess
    intel = tmp_path / "intel.md"
    intel.write_text(INTEL_OK, encoding="utf-8")
    fp = tmp_path / "functions.json"
    fp.write_text(json.dumps({"functions": []}), encoding="utf-8")
    p = subprocess.run(
        [sys.executable, str(Path(iv.__file__)), str(intel),
         "--functions", str(fp), "--root", "FN-99"],
        capture_output=True, text=True, encoding="utf-8")
    assert p.returncode != 0
    assert "FN-99" in p.stderr
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v -k "warning or cli"`
Expected: FAIL — các test CLI báo lỗi vì `main()` chưa tồn tại; các test warning fail vì `verify()` chưa gắn `check_cite_quality`/`check_section2_anchor`

- [ ] **Step 3: Cài đặt**

Thêm vào `speckit-extension/scripts/intel_verify.py`, ngay trước hàm `verify`:

```python
def check_cite_quality(text: str) -> list[dict]:
    """§2-§7, §9 mỗi dòng bảng có cột nguồn — cảnh báo nếu không có gì trông
    giống file:dòng và cũng không đánh dấu (suy đoán). Heuristic ở mức WARNING,
    không BLOCKING — cite hợp lệ nhưng viết khác quy ước vẫn có thể lọt qua."""
    out = []
    for section in (2, 3, 4, 5, 6, 7, 9):
        for i, row in enumerate(_table_rows(_section_body(text, section)), start=1):
            joined = " | ".join(row)
            if not CODE_PATH_RE.search(joined) and "suy đoán" not in joined.lower():
                out.append({"loai": "cite-khong-ro",
                            "thong_diep": f"§{section} dòng {i} không thấy nguồn "
                                           "file:dòng và không đánh dấu suy đoán."})
    return out


def check_section2_anchor(text: str, expected: list[dict]) -> list[dict]:
    """Mỏ neo phủ §2: mỗi FN tìm thấy code phải xuất hiện ở §2, hoặc giải
    trình ở §7/§8 vì sao không sinh màn hình."""
    found = parse_section1(text)
    body2 = _section_body(text, 2)
    body7 = _section_body(text, 7)
    body8 = _section_body(text, 8)
    out = []
    for f in expected:
        if "không tìm thấy" in found.get(f["id"], ""):
            continue
        if f["id"] not in body2 and f["id"] not in body7 and f["id"] not in body8:
            out.append({"loai": "fn-khong-co-mat-o-muc-2",
                        "thong_diep": f"{f['id']} tìm thấy code nhưng không xuất hiện "
                                       "ở §2, §7, hay §8."})
    return out
```

Thay hàm `verify` (bản Task 4 chỉ trả `"warnings": []`) bằng:

```python
def verify(text: str, expected: list[dict], before: str | None = None) -> dict:
    blocking: list[dict] = []
    warnings: list[dict] = []
    m = len(expected)

    for ph in find_placeholders(text):
        blocking.append({"loai": "placeholder",
                         "thong_diep": f"Còn placeholder ở dòng {ph['line']}: {ph['text']}"})

    blocking.extend(check_section1_coverage(text, expected))
    blocking.extend(check_not_found_ratio(text, expected))
    blocking.extend(check_section8_cap(text, m))
    if before is not None:
        blocking.extend(check_no_clobber_8(text, before))
        blocking.extend(check_no_clobber_10(text, before))

    warnings.extend(check_cite_quality(text))
    warnings.extend(check_section2_anchor(text, expected))

    return {"blocking": blocking, "warnings": warnings}


def main(argv=None):
    p = argparse.ArgumentParser(description="Chấm intel.md trước khi báo xong")
    p.add_argument("intel", help="Đường dẫn tới intel.md")
    p.add_argument("--functions", default=".specify/docs/functions.json")
    p.add_argument("--root", required=True,
                   help="FN-ID gốc của unit (giá trị đã dùng ở intel_tree.py units)")
    p.add_argument("--before", default=None,
                   help="File chụp bản intel.md trước khi ghi, để kiểm no-clobber")
    a = p.parse_args(argv)

    text = Path(a.intel).read_text(encoding="utf-8")
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    node = ft.find_by_id(tree, a.root)
    if node is None:
        raise SystemExit(f"Không có {a.root} trong {a.functions}.")
    expected = [{"id": n["id"], "name": n["name"]} for n in ft.subtree_leaves(node)]

    before = Path(a.before).read_text(encoding="utf-8") if a.before else None
    report = verify(text, expected, before)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    n_b, n_w = len(report["blocking"]), len(report["warnings"])
    print(f"\n{n_b} lỗi chặn, {n_w} cảnh báo.", file=sys.stderr)
    if n_b:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v`
Expected: PASS — 22 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_verify.py speckit-extension/scripts/tests/test_intel_verify.py
git commit -m "feat(code-intel): intel_verify.py WARNING (cite mờ, mỏ neo §2) + CLI"
```

---

### Task 6: Viết lại `templates/intel-template.md`

**Files:**
- Rewrite: `speckit-extension/templates/intel-template.md`

**Interfaces:**
- Consumes: quy ước cú pháp đã cố định ở Task 4-5 (`— **Trả lời**: _(chưa có)_`, nhãn `[...]` giữ nguyên ở §8, cột Kết luận `đang chờ` không ngoặc vuông ở §10, bảng §1 3 cột đầu `FN-ID | Tên chức năng | Tìm thấy ở đâu`)
- Produces: khung để `commands/code-intel.md` (Task 7) copy khi ghi `intel.md` mới

- [ ] **Step 1: Viết lại file**

Thay **toàn bộ** `speckit-extension/templates/intel-template.md` bằng:

````markdown
# Code intel — [TÊN UNIT]

**Cập nhật**: [DATE]
**Phủ chức năng**: [FN-001, FN-002, …]

<!-- TÀI LIỆU NỘI BỘ. Không giao khách — chỗ giao khách là srs.md cùng thư mục.
     Mỗi khẳng định ở §2–§7 VÀ §9 thuộc một trong ba dạng:
       - Đọc thẳng từ code   → ghi bình thường, kèm `đường/dẫn.ext:dòng`
       - Suy ra, chưa chắc   → ghi kèm nguồn gần nhất và đánh dấu (suy đoán)
       - Không căn cứ nào    → KHÔNG viết ở §2–§7, §9; đưa xuống §8 thành câu hỏi
     Mục không áp dụng cho unit này (đã kiểm tra, thật sự không có) → ghi "Không có",
     giữ tiêu đề. Luôn rút đủ sâu (không có mức nông/sâu để chọn). -->

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| [FN-001] | [tên] | [đường/dẫn hoặc "không tìm thấy"] | [—] |

<!-- Danh sách FN-ID lấy nguyên từ `intel_tree.py units` — không tự gõ tay,
     không tự bớt/thêm. FN không tìm thấy code phải ghi rõ "không tìm thấy" —
     im lặng bỏ qua là cách tài liệu bàn giao thiếu chức năng mà không ai biết. -->

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| [tên] | [/route] | [file:dòng] | [FN-001] |

## 3. Thực thể và trường dữ liệu

<!-- Hình dạng mục này mượn từ templates/domain-template.md §1–§2 để code-intel
     và domain-design không mô tả entity theo hai kiểu khác nhau. Khác domain-
     template ở chỗ: đây là NƠI SUY, không phải nơi thiết kế — mọi dòng phải
     trỏ nguồn đọc được, không có cột "Nguồn gốc: BRD / mới". -->

### [TênThựcThể]

- **Nguồn**: [file:dòng]
- **Khoá chính**: [trường]
- **Quan hệ**: [FK → thực thể khác, kiểu 1-N/N-N/1-1]

| Trường | Kiểu | Bắt buộc | Ràng buộc | Mặc định | Nguồn |
| --- | --- | --- | --- | --- | --- |
| [tên] | [kiểu] | [Có/Không] | [độ dài, miền giá trị, duy nhất] | [—] | [file:dòng] |

## 4. Kiểm tra hợp lệ và quy tắc nghiệp vụ

| # | Quy tắc | Nguồn | Độ chắc chắn |
| --- | --- | --- | --- |
| 1 | [điều kiện → hệ quả] | [file:dòng] | [chắc / suy đoán] |

<!-- Quy tắc đánh dấu "suy đoán" ở đây KHÔNG được rót thẳng vào N.4 Đặc tả dữ liệu HAY
     N.5 Quy tắc nghiệp vụ của srs.md — lệnh srs-from-code để TRỐNG ô/không sinh dòng
     BR cho quy tắc đó, KHÔNG hỏi (lệnh đó chủ ý không hỏi trong lúc sinh), và KHÔNG tự
     tin chuyển suy đoán thành cam kết trong tài liệu giao khách. -->

## 5. Luồng nghiệp vụ

### [Tên luồng]

[Trình tự các bước, nêu rõ thành phần nào xử lý bước nào.]

- **Nguồn**: [file:dòng, file:dòng]

## 6. Phân quyền

| Vai trò | Chức năng / hành động | Điều kiện | Nguồn |
| --- | --- | --- | --- |
| [vai trò] | [hành động] | [điều kiện dữ liệu] | [file:dòng] |

## 7. Tích hợp ngoài, tác vụ nền, sự kiện

| Loại | Mô tả | Kích hoạt khi | Nguồn |
| --- | --- | --- | --- |
| [dịch vụ ngoài / job / event] | [làm gì] | [điều kiện] | [file:dòng] |

## 8. Không suy được từ code — câu hỏi cho người

<!-- Câu đã được trả lời thì ghi câu trả lời ngay dưới, GIỮ NGUYÊN, đừng xoá —
     lần chạy lại sau sẽ không hỏi lại (living doc, no-clobber mục này, giống
     §6 của domain-template).
     MỖI mục mở đầu bằng NHÃN LOẠI để đếm được (dùng đúng một trong bốn):
       [không suy được từ code]   — đã tìm mà không ra căn cứ. Loại DUY NHẤT tính vào trần.
       [chính sách nghiệp vụ]     — quyết định chỉ người mới biết, không phải thứ
                                    code có thể tiết lộ dù tìm kỹ tới đâu (kể cả
                                    ca FN không sinh màn hình nào, không có gì để
                                    ghi ở §7).
       [FN không tìm thấy]        — FN đã kết luận không tìm thấy code ở §1.
       [chờ trả lời từ lần trước] — câu hỏi mang sang từ lần chạy trước.
     Thiếu nhãn = mặc định tính là [không suy được từ code] (an toàn: bị đếm
     trần chứ không lọt lưới). Nhãn giữ nguyên dấu ngoặc vuông vĩnh viễn — đây
     là ký hiệu phân loại cố định, KHÔNG phải chỗ điền nội dung rồi xoá đi.

     Câu chưa có trả lời ghi "— **Trả lời**: _(chưa có)_" — dùng gạch dưới in
     nghiêng, KHÔNG dùng ngoặc vuông kiểu "[để trống...]": intel_verify.py coi
     mọi cặp ngoặc vuông còn sót là placeholder chưa điền và chặn báo xong;
     dùng ngoặc vuông ở đây sẽ khiến một tài liệu hợp lệ (đang có câu hỏi mở)
     không bao giờ qua được cổng. -->

1. [nhãn] [Câu hỏi] — **Trả lời**: _(chưa có)_

## 9. Thông báo hiển thị

| Ngữ cảnh | Nguyên văn thông báo | Nguồn |
| --- | --- | --- |
| [tình huống] | "[nguyên văn]" | [file:dòng] |

<!-- Lấy từ file ngôn ngữ / hằng số / mã lỗi. Đây là nguồn cho mục N.6 "Xử lý
     ngoại lệ và thông báo" của srs.md — chép nguyên văn, không diễn đạt lại. -->

## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật

| # | Loại | Mô tả | Nguồn | Kết luận |
| --- | --- | --- | --- | --- |
| 1 | [logic mâu thuẫn / lỗ hổng bảo mật] | [mô tả cụ thể: mâu thuẫn với chỗ nào, hoặc rủi ro gì] | [file:dòng, file:dòng] | đang chờ |

<!-- KHÁC HẲN §8: đây không phải "không biết", mà là "đã thấy và thấy có vấn đề".
     Chỉ ghi phát hiện THẤY ĐƯỢC trong lúc rút §2–§7 — KHÔNG chủ động mở rộng phạm vi
     quét để tìm lỗ hổng bảo mật một cách hệ thống, đó là việc của security review
     riêng, không phải mục tiêu của command này.
     Mỗi mục PHẢI kèm file:dòng và mô tả CỤ THỂ vì sao đáng ngờ — "trông không an
     toàn" hay "có vẻ sai" không đủ; phải nói rõ mâu thuẫn với dòng/quy tắc nào, hoặc
     lỗ hổng cụ thể là gì (vd "không kiểm quyền sở hữu record trước khi cho sửa",
     "mật khẩu so sánh dạng plaintext"). Không có phát hiện nào → ghi "Không có" (thay
     hẳn bảng, không để lại dòng mẫu).

     RANH GIỚI VỚI §8: mâu thuẫn/thiếu sót THẤY ĐƯỢC trong code → §10, không hạ cấp
     thành câu hỏi §8 kiểu "chính sách có cho phép..." để né việc. Thứ code hoàn toàn
     không mâu thuẫn, chỉ đơn giản không biết (vd "ngưỡng duyệt bao nhiêu tiền thì cần
     cấp trên ký") → §8. Không chắc thuộc loại nào → coi là §10.

     Cột `Kết luận`: giá trị "đang chờ" (không ngoặc vuông) mặc định khi mới ghi.
     srs-from-code đọc mục này để hỏi người dùng "cố ý hay là bug", rồi ghi kết luận
     NGƯỢC lại đúng dòng này — "cố ý — <ghi chú>" hoặc "bug — <ghi chú>". Đây là CỘT
     DUY NHẤT được phép cập nhật trên một dòng đã có (chỉ srs-from-code được ghi;
     code-intel không bao giờ tự sửa cột này); mô tả/nguồn của dòng thì không đổi.

     No-clobber khi chạy lại: chỉ được THÊM phát hiện mới; phát hiện cũ (#/Loại/Mô
     tả/Nguồn) giữ nguyên dù thấy nó nhỏ hay đã hết quan trọng — cột Kết luận là
     ngoại lệ duy nhất (và chỉ srs-from-code được sửa nó). Đây là nơi srs-from-code
     lấy để tổng kết hỏi người dùng, không rót vào srs.md (tài liệu giao khách không
     nêu phát hiện kiểu này). -->
````

- [ ] **Step 2: Kiểm khung khớp với `intel_verify.py` bằng test có sẵn**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v`
Expected: PASS — không đổi gì ở code, chỉ xác nhận lại các test đã viết ở Task 4-5 (dùng đúng cú pháp `_(chưa có)_`/nhãn giữ ngoặc vuông/`đang chờ` không ngoặc) vẫn phản ánh đúng khung thật vừa viết. Đọc lại khung và test song song bằng mắt: xác nhận §8/§10 trong khung dùng đúng cú pháp `INTEL_OK` fixture đã dùng.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/templates/intel-template.md
git commit -m "docs(code-intel): sửa khung intel-template — tránh đâm placeholder, đổi cụm sang unit"
```

---

### Task 7: Viết lại `commands/code-intel.md`

**Files:**
- Rewrite: `speckit-extension/commands/code-intel.md`

**Interfaces:**
- Consumes: CLI `intel_tree.py propose`/`units` (Task 3), CLI `intel_verify.py` (Task 5), CLI `fnlist_import.py update` (đã có sẵn từ đợt trước), khung `intel-template.md` (Task 6)
- Produces: quy trình LLM chạy lệnh

- [ ] **Step 1: Viết lại file**

Thay **toàn bộ** `speckit-extension/commands/code-intel.md` bằng:

````markdown
---
description: Rút đặc tả đủ sâu từ codebase theo cây functions.json, ghi .specify/docs/<đường-dẫn-cây>/intel.md kèm nguồn file:dòng — tài liệu nội bộ làm đầu vào cho srs-from-code. Tham số là một FN-ID đánh dấu điểm bắt đầu quét (trống = toàn dự án); tự đề xuất unit theo luật cha-trực-tiếp-của-lá, xác nhận qua cây thụt lề, rồi quét (hỏi song song/tuần tự khi có nhiều unit). Ghi thêm §10: phát hiện logic mâu thuẫn/lỗ hổng bảo mật thấy được trong lúc rút, để srs-from-code hỏi người dùng riêng.
---

# Code intel theo cây functions.json

Trước khi sinh SRS, rút **đặc tả thật** của codebase: màn hình, thực thể, quy tắc, luồng,
phân quyền, tích hợp — mỗi khẳng định kèm nguồn `file:dòng`. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: đây là tài liệu **nội bộ**, không giao khách — chỗ giao khách là
`srs.md` do lệnh `srs-from-code` sinh sau. Mỗi khẳng định ở §2–§7, §9 thuộc đúng một
trong ba dạng, không được lẫn lộn:

| Dạng | Cách ghi |
| --- | --- |
| Đọc thẳng từ code | Ghi bình thường, kèm `file:dòng` |
| Suy ra từ code, chưa chắc | Ghi kèm `file:dòng` gần nhất và đánh dấu `(suy đoán)` |
| Không có căn cứ nào trong code | **KHÔNG viết ở §2–§7, §9**; đưa xuống §8 thành câu hỏi |

**Cite không phải là dán một đường dẫn cho có — nó phải trỏ đúng chỗ đỡ được khẳng
định.** Kiểm bằng cách tự hỏi: dòng `file:dòng` đó có chứa **token cụ thể** làm căn cứ
trực tiếp cho câu vừa viết không (tên trường, regex, hằng số, annotation validation,
điều kiện `if`)? Có → **đọc thẳng**. Không có token nào, chỉ là suy luận hợp lý từ một
chỗ gần đó (vd thấy unique index rồi suy "trùng mã bị chặn" nhưng chưa thấy nhánh báo
lỗi thật) → **suy đoán**, dán đúng regex/hằng số làm nguồn đọc thẳng cho một khẳng định
suy đoán là tự đánh lừa chính lượt kiểm lại ở cuối. Ví dụ:

- Đọc thẳng: trường `MaxLength(200)` tại `Domain/User.cs:41` → "Tên tối đa 200 ký tự".
- Suy đoán: thấy `[Index(IsUnique = true)]` trên `Email` tại `Domain/User.cs:38`, chưa
  thấy nhánh xử lý lỗi trùng → "Email phải duy nhất *(suy đoán, chưa thấy message lỗi)*
  — `Domain/User.cs:38`".

Không có nguồn thì không được viết ở §2–§7, §9 — đây là luật ngăn tài liệu bàn giao sau
này chứa hành vi hệ thống không hề có.

## User Input

`$ARGUMENTS`

Kỳ vọng: **trống, hoặc một FN-ID**. FN-ID đánh dấu điểm bắt đầu quét:

- Trống → điểm bắt đầu là **gốc cây** — quét toàn bộ dự án.
- `FN-01` → chỉ quét nhánh đó.
- Một FN-ID lá → quét đúng một unit (chính nó).

Không còn khái niệm "cụm gõ tay" — thư mục sinh ra tự động từ cấu trúc `functions.json`,
không phải chuỗi tự do người dùng đặt.

## Validate cứng trước khi làm bất cứ gì khác

- **`.specify/docs/functions.json` không tồn tại** → DỪNG, nhắc chạy
  `/speckit.dft-speckit.fnlist-import` trước.
- **`$ARGUMENTS` không trống và không khớp `^FN(?:-\d{2})+$`** → DỪNG, in cú pháp hợp lệ
  (`FN-01`, `FN-01-01`, …), hỏi lại. Không tự đoán/tự sửa.
- **FN-ID đúng cú pháp nhưng không có trong cây** → chạy
  `python .../scripts/intel_tree.py units --functions .specify/docs/functions.json --roots <FN-ID>`
  sẽ tự báo lỗi kèm đúng FN-ID không tìm thấy — DỪNG, in nguyên thông điệp, không tự đoán
  ID gần đúng.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/`. Dùng `python3` nếu
`python` không có (macOS/Linux).

### 1. Đề xuất unit + xác nhận cây

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py propose \
  --functions .specify/docs/functions.json [--start <FN-ID nếu có>]
```

In ra danh sách unit đề xuất (mặc định: node có tất cả con đều là lá, hoặc node không
có con đứng một mình) kèm cây thụt lề có đánh dấu `[UNIT]`. Trình nguyên văn cây này cho
người dùng qua AskUserQuestion: xác nhận đúng ranh giới, hay muốn gộp/tách lại?

- Điều chỉnh hợp lệ: chọn một tập node KHÁC làm root của unit (sâu hơn hoặc cao hơn đề
  xuất), miễn mỗi root vẫn là một nhánh cây hợp lệ (không lẫn hai node không phải anh em
  vào cùng một unit — điều đó không được hỗ trợ).
- Chưa có phản hồi → DỪNG, không sang bước 2.
- Có điều chỉnh → dùng danh sách root người dùng chốt (không phải danh sách đề xuất mặc
  định) cho bước 2.

### 2. Tính đường dẫn + danh sách FN cho từng unit đã chốt

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py units \
  --functions .specify/docs/functions.json --roots <FN-ID,FN-ID,...>
```

Trả về, cho mỗi unit: đường dẫn thư mục đầy đủ (`intel.md` nằm ở đó) và danh sách
FN-ID lá thuộc nhánh (kèm `name`/`status` hiện tại) — đây là dữ liệu dùng để điền §1 của
`intel.md`, không tự đọc lại `functions.json` bằng mắt rồi gõ tay.

### 3. Chạy song song hay tuần tự?

Có **≥ 2 unit** → hỏi qua AskUserQuestion: chạy song song (mỗi unit một subagent độc lập
qua Agent tool) hay tuần tự (xử từng unit một). Đúng 1 unit → chạy thẳng bước 4-10 dưới
đây, không hỏi.

Chạy song song: dispatch một Agent riêng cho mỗi unit, giao FN-ID gốc của unit, đường dẫn
thư mục, danh sách FN-ID kèm status (từ bước 2), và yêu cầu subagent đọc lại chính file
lệnh này (`code-intel.md`) rồi thực hiện đúng Bước 4–10 dưới đây cho một unit đó. Không
đồng bộ giữa các subagent — hai unit dùng chung một entity có thể cite khác nhau, chấp
nhận là giới hạn đã biết.

Chạy tuần tự: lặp qua từng unit, thực hiện Bước 4–10 cho unit đó xong mới sang unit kế.

### 4. Quét codebase — theo danh sách FN của unit, không theo trí nhớ

`functions.json` chứa **tên chức năng tiếng Việt** (`name`); code gần như chắc chắn dùng
định danh tiếng Anh. Grep thẳng tên tiếng Việt vào code gần như luôn ra rỗng — đó **không
phải** bằng chứng "không tìm thấy", đó là bằng chứng "tìm sai chỗ".

**Thang tìm kiếm tối thiểu — thử ít nhất 2 nấc trước khi được kết luận "không tìm
thấy"** cho một FN:

1. Tra chuỗi tiếng Việt (tên chức năng, từ khoá trong `description`) trong file ngôn
   ngữ/hằng số UI (`*.i18n.*`, `vi.json`, resource string…) → lấy key → Grep nơi dùng key.
2. Bảng route/menu/navigation/permission-code — bất kể khai bằng file config hay code.
3. Tên bảng/entity suy từ danh từ nghiệp vụ trong tên chức năng.
4. Từ khoá tiếng Anh dịch từ tên chức năng + từ khoá `description`, Grep trực tiếp.

Không có route/controller kiểu web (ứng dụng desktop, job nền, CLI) → điểm vào là
form/command handler/scheduler entry — vẫn áp thang tìm kiếm trên, chỉ đổi nơi tìm.

Từ điểm vào tìm được, lần theo tới service/repository/entity/validator liên quan.

**Mỏ neo phủ FN**: gọi `M` = số phần tử `fn_ids` của unit (từ bước 2). Cuối bước này,
mỗi FN phải rơi vào đúng một trong hai nhóm:
- **Tìm thấy** — có ít nhất một điểm vào cụ thể (`file:dòng`).
- **Không tìm thấy** — đã thử **thang tìm kiếm ở trên (≥2 nấc)**, ghi rõ ở cột `Ghi chú`
  §1 **ít nhất 2 pattern/từ khoá/thư mục thực sự đã chạy trong phiên này**. Ô `Ghi chú`
  trống, hoặc chỉ ghi chung chung kiểu "đã tìm không thấy", coi như **chưa tìm**.

**Tỉ lệ không tìm thấy vượt 1/3 `M`** → nhiều khả năng đang tìm sai module/sai phạm vi,
không phải codebase thiếu — **DỪNG**, trình danh sách FN không tìm thấy kèm pattern đã
thử, hỏi người dùng có đúng phạm vi không. `intel_verify.py` ở bước 9 cũng chặn ca này,
nhưng dừng sớm ở đây đỡ tốn công viết trước khi biết sai phạm vi.

**Mỗi mục §8 phải gắn một nhãn loại** ở đầu dòng — nhãn nào không nêu coi như
`[không suy được từ code]`:

- `[không suy được từ code]` — đã tìm mà không ra căn cứ; **loại duy nhất tính vào trần**.
- `[chính sách nghiệp vụ]` — quyết định chỉ người mới biết, không phải thứ code có thể
  tiết lộ dù tìm kỹ tới đâu.
- `[FN không tìm thấy]` — FN đã kết luận không tìm thấy code ở §1.
- `[chờ trả lời từ lần trước]` — câu hỏi mang sang từ lần chạy trước, chưa có phản hồi.

### 5. Ghi theo kỷ luật ba dạng

Rút vào §2 (Màn hình/điểm vào), §3 (Thực thể & trường dữ liệu), §4 (Kiểm tra hợp lệ &
quy tắc nghiệp vụ), §5 (Luồng nghiệp vụ), §6 (Phân quyền), §7 (Tích hợp ngoài, tác vụ
nền, sự kiện), §9 (Thông báo hiển thị) của `intel-template`.

Mỗi FN **tìm thấy** phải xuất hiện ở cột `FN liên quan` của **ít nhất một** dòng §2. FN
tìm thấy code nhưng không sinh màn hình nào (job nền, quyền thuần backend) → ghi rõ ở §7,
hoặc ở §8 với nhãn `[chính sách nghiệp vụ]` nếu không có gì để ghi ở §7 — **không dùng
nhãn `[không suy được từ code]`** cho ca này, đây là giải trình chính đáng chứ không phải
bế tắc. **Không được** để FN đó vắng mặt hoàn toàn khỏi §2 mà không giải trình ở một
trong hai nơi trên — `intel_verify.py` cảnh báo (WARNING) ca này ở bước 9.

**Mỏ neo phân tán — chỉ áp khi `M ≥ 4`** (dưới ngưỡng đó một dòng gánh hết là chuyện bình
thường, vd unit 2–3 FN Thêm/Sửa/Xoá cùng một màn): một dòng §2 gánh quá **1/2** số `M` →
không tự động fail, nhưng **mỗi FN trên dòng đó phải cite riêng** (handler/action
`file:dòng` khác nhau cho từng FN, không dùng chung một cite cho cả nhóm).

Mỗi dòng bạn định viết, tự hỏi: cite có chứa token đỡ trực tiếp cho khẳng định không
(xem "Nguyên tắc lõi")? Có → đọc thẳng. Không → `(suy đoán)`. Không có gì để cite →
xuống §8.

**§4 tách riêng cột "Độ chắc chắn"** (`chắc` / `suy đoán`) — ràng buộc đánh `suy đoán` ở
đây sau này **không được** rót thẳng vào mục "Đặc tả dữ liệu" của `srs.md`; lệnh
`srs-from-code` để trống ô đó thay vì tự tin biến suy đoán thành cam kết trong tài liệu
giao khách.

### 6. Ghi phát hiện đáng chú ý — logic mâu thuẫn / lỗ hổng bảo mật

Trong lúc rút §2–§7, nếu **thấy rõ** một trong hai điều sau, ghi vào §10 — mục **khác
hẳn** §8: không phải "không biết", mà là "đã thấy và thấy có vấn đề":

- **Logic mâu thuẫn**: hai chỗ code xử lý cùng một nghiệp vụ nhưng theo hai quy tắc khác
  nhau, hoặc một ràng buộc tự triệt tiêu chính nó.
- **Dấu hiệu lỗ hổng bảo mật**: thiếu kiểm tra quyền sở hữu trước khi cho sửa/xoá record
  của người khác, mật khẩu/token so sánh hoặc lưu dạng plaintext, endpoint nhạy cảm không
  qua middleware xác thực đáng lẽ phải có, v.v.

**Không chủ động mở rộng phạm vi quét để tìm lỗ hổng một cách hệ thống** — đó là việc của
security review riêng. Chỉ ghi những gì **tình cờ thấy rõ** trong lúc rút đặc tả bình
thường. Mỗi mục phải kèm `file:dòng` và mô tả **cụ thể** vì sao đáng ngờ.

**Trục 1 — đây có phải một vấn đề thật không?** Không rõ ràng (chỉ là cảm giác) → **bỏ
qua, không ghi gì cả**. Không có phát hiện thật nào → ghi "Không có" ở §10.

**Trục 2 — đã chắc là vấn đề thật, nhưng thuộc §8 hay §10?** Mâu thuẫn/thiếu sót **thấy
được trong chính code** → **§10**, không viết lại thành câu hỏi kiểu `[chính sách nghiệp
vụ]` ở §8 để né việc. Thứ **code hoàn toàn không mâu thuẫn, chỉ đơn giản là không biết**
→ §8. **Đã chắc là vấn đề thật nhưng không chắc thuộc §8 hay §10 → coi là §10.**

Mỗi FN **tìm thấy** có tên chứa động từ ghi dữ liệu (Thêm/Sửa/Xoá/Cập nhật/Duyệt/Khoá…)
phải hoặc có một dòng §6 với cite chứng minh có kiểm quyền sở hữu/quyền truy cập, hoặc có
một mục §10 giải trình **nơi đã tra** (middleware/filter/policy nào đã đọc) vì sao không
kiểm được điều đó — thiếu cả hai mà vẫn ghi "Không có" ở §10 là chưa chạy bước này.

### 7. Độ sâu — luôn đầy đủ

Không có mức nông/sâu để chọn — mọi lần chạy đều rút tới:
- §3: đủ bảng field (kiểu, độ dài/miền giá trị, bắt buộc, mặc định), không chỉ tên thực thể.
- §4: đủ từng quy tắc, không chỉ liệt kê tên.
- §9: thông báo hiển thị, lấy **nguyên văn** từ file ngôn ngữ/hằng số/mã lỗi, **hoặc**
  chuỗi literal ngay trong code nếu dự án không tách riêng file ngôn ngữ. Không tìm được
  nguyên văn ở bất kỳ hai nguồn đó → không ghi ở §9, đưa câu hỏi xuống §8.

### 8. Lấy khung, ghi `intel.md`

`specify preset resolve intel-template` → không resolve được → đọc
`.specify/extensions/dft-speckit/templates/intel-template.md` → vẫn không thấy → hỏi.

Thư mục của unit (từ bước 2) chưa có → tạo (bao gồm mọi cấp cha nếu chưa có).

**`intel.md` chưa tồn tại** → copy khung, điền theo nội dung đã rút.

**`intel.md` đã tồn tại (chạy lại)** → **đọc file hiện tại trước, chụp lại nguyên văn
toàn bộ nội dung file** (dùng làm `--before` ở bước 9), rồi:

- **Header `**Phủ chức năng**`** = **hợp** của danh sách cũ và danh sách FN của unit lần
  này (thường trùng nhau, vì đường dẫn thư mục gắn với đúng một node cây — chỉ khác nếu
  cấu trúc cây đổi giữa hai lần `fnlist-import` re-import).
- **§1**: mọi dòng FN cũ **vẫn phải còn nguyên** trong bảng, cộng thêm dòng cho FN mới
  nếu có.
- **§8, §10**: **chỉ được nối thêm, không được sửa/xoá mục cũ.** Câu hỏi cũ nay đã có
  câu trả lời từ code → **giữ nguyên câu hỏi**, thêm một dòng ngay dưới:
  `— Đã rõ từ code: <file:dòng>`. Cột `Kết luận` ở §10 giữ nguyên giá trị hiện có (dù
  `đang chờ`, `cố ý — …`, hay `bug — …`) — `code-intel` không bao giờ tự sửa cột này.
- Chỉ bổ sung/cập nhật phần rút được mới ở các mục khác **trừ §8 và §10**; không copy
  khung đè lên toàn file.

### 9. Verify

```bash
python .specify/extensions/dft-speckit/scripts/intel_verify.py <đường-dẫn>/intel.md \
  --functions .specify/docs/functions.json --root <FN-ID gốc của unit> \
  [--before <file-chụp-nếu-chạy-lại>]
```

Mã thoát khác 0 → còn BLOCKING, đọc báo cáo JSON, sửa `intel.md` theo đúng lỗi nêu, chạy
lại `intel_verify.py` cho tới khi sạch. WARNING không chặn nhưng phải đọc và cân nhắc sửa
trước khi báo xong.

### 10. Ghi ngược trạng thái

Với mỗi FN-ID **tìm thấy** trong unit mà `status` hiện tại (từ bước 2) **không phải
`srs`** (không lùi trạng thái — đã qua `srs-from-code` thì không đặt lại `intel`):

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=intel [--set FN-01-02=intel ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate, và đổi status là hành vi có
thể lùi lại. FN-ID vốn đã `srs` thì bỏ qua, không đưa vào `--set`.

## Kết thúc

Với mỗi unit, báo: FN đã xử lý (tìm thấy/không tìm thấy), số mục §8 đang chờ trả lời, số
phát hiện §10 (nêu ngắn gọn từng phát hiện), đường dẫn `intel.md`. Chạy hàng loạt (≥2
unit) thì tổng kết thêm: tổng số unit đã xử lý, danh sách unit lỗi (nếu có subagent nào
BLOCKING mà không tự sửa được).

Rồi nhắc: `/speckit.dft-speckit.srs-from-code <đường-dẫn-cây-của-từng-unit>`.

## Sai lầm thường gặp

- **Grep thẳng tên tiếng Việt vào code rồi kết luận "không tìm thấy" khi rỗng** → tên
  chức năng trong `functions.json` là tiếng Việt, code gần như chắc chắn tiếng Anh. Phải
  qua thang tìm kiếm (tra file ngôn ngữ lấy key trước) trước khi kết luận.
- **Cite một file "gần đúng" cho có, để khỏi phải đánh dấu `(suy đoán)`** → cite phải
  chứa token đỡ trực tiếp khẳng định, không phải một đường dẫn hợp lý nghe qua.
- **Tự gộp hai nhánh không phải anh em vào một unit** khi điều chỉnh cây ở bước 1 → mỗi
  unit luôn ánh xạ đúng một nhánh cây, một thư mục — không được hỗ trợ.
- **Đẩy phần lớn nội dung xuống §8 mà không gắn nhãn, hoặc gắn bừa nhãn không tính vào
  trần để lách** → nhãn `[không suy được từ code]` mới bị tính trần, ba nhãn còn lại là
  lối thoát chính đáng — dùng sai nhãn để né trần là tự lừa chính `intel_verify.py`.
- **Một dòng §2 gánh gần hết `M` FN mà không cite riêng từng FN** → chỉ áp khi `M ≥ 4`.
- **Chạy lại làm rụng FN/câu hỏi §8/§10 của lần trước** → header hợp cũ+mới, §1 giữ
  nguyên dòng cũ, §8/§10 chỉ được nối thêm — `intel_verify.py --before` bắt được ca này.
- **Sửa/xoá câu hỏi §8 vì thấy nó "lỗi thời"** → giữ nguyên câu hỏi, thêm dòng "Đã rõ từ
  code: file:dòng" bên dưới, không viết đè.
- **Dùng ngoặc vuông cho "chưa trả lời" ở §8** (`[để trống...]`) → `intel_verify.py` coi
  đó là placeholder chưa điền, chặn báo xong dù tài liệu hợp lệ. Dùng `_(chưa có)_`.
- **Ghi status `intel` cho FN đã là `srs`** → lùi trạng thái, mất dấu FN đã qua
  `srs-from-code`. Kiểm `status` hiện tại (từ `intel_tree.py units`) trước khi `--set`.
- **Chủ động đi quét toàn bộ codebase tìm lỗ hổng bảo mật** → §10 chỉ ghi thứ tình cờ
  thấy rõ trong lúc rút §2–§7, không phải một security audit.
- **Ghi vào §10 một nghi ngờ mơ hồ không kèm lý do cụ thể** → không đủ căn cứ để người
  dùng phán đoán cố ý hay bug; không rõ ràng thì bỏ qua, không đoán.
````

- [ ] **Step 2: Kiểm mọi lệnh trong tài liệu chạy được thật**

Run:
```bash
cd /tmp && rm -rf code-intel-smoke && mkdir code-intel-smoke && cd code-intel-smoke && \
mkdir -p .specify/docs && cat > .specify/docs/functions.json << 'EOF'
{
  "schema_version": 1, "system": "SMOKE", "source": {}, "updated": "2026-08-12",
  "retired_ids": [],
  "functions": [
    {"id": "FN-01", "name": "Xac thuc", "description": "", "children": [
      {"id": "FN-01-01", "name": "Dang nhap", "description": "", "children": []},
      {"id": "FN-01-02", "name": "Quen mat khau", "description": "", "children": []}
    ]}
  ]
}
EOF
python /e/agent-skills/speckit-extension/scripts/intel_tree.py propose --functions .specify/docs/functions.json && \
python /e/agent-skills/speckit-extension/scripts/intel_tree.py units --functions .specify/docs/functions.json --roots FN-01 && \
mkdir -p .specify/docs/01-xac-thuc && \
python /e/agent-skills/speckit-extension/scripts/fnlist_import.py update --file .specify/docs/functions.json --set FN-01-01=intel
```
Expected: `propose` in `units: [{"id":"FN-01",...}]` và cây có `[UNIT]`; `units` in
`path: "01-xac-thuc/intel.md"` kèm `fn_ids` 2 phần tử; `update` chạy thành công, in
`FN-01-01` đổi `pending → intel`.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/code-intel.md
git commit -m "docs(code-intel): viết lại command theo cây functions.json — unit, batch, verify"
```

---

### Task 8: Cập nhật manifest và kiểm bản đóng gói

**Files:**
- Modify: `speckit-extension/extension.yml`

**Interfaces:**
- Consumes: toàn bộ Task 1-7
- Produces: bản đóng gói chạy được

- [ ] **Step 1: Sửa `extension.yml`**

Đổi `version: "0.2.0"` (dòng 6) thành:

```yaml
  version: "0.3.0"
```

Thay khối `description` của `speckit.dft-speckit.code-intel` bằng:

```yaml
      description: "Rút đặc tả đủ sâu từ codebase theo cây functions.json, ghi .specify/docs/<đường-dẫn-cây>/intel.md kèm nguồn file:dòng. Tham số là một FN-ID đánh dấu điểm bắt đầu quét (trống = toàn dự án); intel_tree.py đề xuất unit theo luật cha-trực-tiếp-của-lá, LLM trình cây thụt lề xác nhận, rồi quét (hỏi song song qua subagent hay tuần tự khi có nhiều unit). intel_verify.py chấm gate BLOCKING (phủ §1, trần §8, no-clobber §8/§10) trước khi ghi ngược status qua fnlist_import.py update. Tài liệu nội bộ: khẳng định đọc thẳng từ code ghi kèm nguồn, suy đoán đánh dấu, không căn cứ thì xuống mục câu hỏi. Ghi thêm §10: phát hiện logic mâu thuẫn/lỗ hổng bảo mật thấy được trong lúc rút, để srs-from-code hỏi người dùng riêng."
```

Thay khối `description` của template `intel-template` bằng:

```yaml
      description: "Khung cho .specify/docs/<đường-dẫn-cây>/intel.md — tài liệu nội bộ rút từ codebase theo một unit của cây functions.json, giữ nguồn file:dòng. Mười mục: phủ chức năng, màn hình/điểm vào, thực thể và trường, kiểm tra hợp lệ, luồng nghiệp vụ, phân quyền, tích hợp ngoài, câu hỏi chưa suy được từ code (gắn nhãn loại), thông báo hiển thị, và phát hiện logic mâu thuẫn/lỗ hổng bảo mật cần người quyết định."
```

- [ ] **Step 2: Chạy toàn bộ test của repo**

Run: `python -m pytest speckit-extension/scripts/tests/ -v`
Expected: PASS — không test nào fail (test của `fnlist_*`/`srs_verify`/`brd_roadmap`
không bị ảnh hưởng; tổng số test tăng thêm 3 (Task 1) + 24 (Task 2-3) + 22 (Task 4-5) so
với trước plan này)

- [ ] **Step 3: Build zip và kiểm hai script mới được đóng gói**

Run:
```bash
cd /e/agent-skills && bash speckit-extension/build-zip.sh && \
unzip -l speckit-extension/dist/dft-speckit-0.3.0.zip | grep -E "intel_tree|intel_verify|intel-template"
```
Expected: cả ba đều xuất hiện — `scripts/intel_tree.py`, `scripts/intel_verify.py`,
`templates/intel-template.md`. Thiếu `intel_tree.py`/`intel_verify.py` là command gãy
trong bản cài (command import lẫn nhau qua `fnlist_tree`, và gọi CLI của cả hai).

- [ ] **Step 4: Chạy thử script từ trong zip đã giải nén**

Run:
```bash
cd /tmp && rm -rf code-intel-pkg && mkdir code-intel-pkg && \
unzip -q /e/agent-skills/speckit-extension/dist/dft-speckit-0.3.0.zip -d code-intel-pkg && \
cd code-intel-pkg/dft-speckit && \
printf '{"schema_version":1,"system":"T","source":{},"updated":"2026-08-12","retired_ids":[],"functions":[{"id":"FN-01","name":"A","description":"","children":[]}]}' > functions.json && \
python scripts/intel_tree.py propose --functions functions.json
```
Expected: exit 0, in `units: [{"id": "FN-01", "name": "A"}]`. Lỗi
`ModuleNotFoundError: fnlist_tree` nghĩa là thiếu module phụ thuộc trong zip — không nên
xảy ra vì `build-zip.sh` đã copy toàn bộ `scripts/*.py` từ trước; nếu xảy ra, kiểm lại
`find scripts -type f ...` trong `build-zip.sh` có loại nhầm gì không.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/extension.yml
git commit -m "chore(code-intel): bump 0.3.0, cập nhật description theo cây functions.json"
```

---

## Self-Review

**Spec coverage:**

| Mục spec | Task |
|---|---|
| §1 Tham số hợp nhất (FN-ID điểm bắt đầu, trống = gốc) | Task 7 (User Input, Bước 1) |
| §2 Unit = cha-trực-tiếp-của-lá, đề xuất rồi xác nhận | Task 2 (`default_units`), Task 7 (Bước 1) |
| §3 Thư mục lồng đúng độ sâu, đánh số theo vị trí, slug tất định | Task 2 (`slugify`/`dedupe_slugs`), Task 3 (`compute_paths`) |
| §4 Phân Python/LLM: `intel_tree.py` tính toán, `intel_verify.py` xác minh | Task 2-3 (`intel_tree.py`), Task 4-5 (`intel_verify.py`) |
| §5 Ghi ngược không xác nhận riêng, không lùi trạng thái | Task 7 (Bước 10) |
| §6 Batch hỏi song song/tuần tự tại thời điểm chạy | Task 7 (Bước 3) |
| §7 Giữ nguyên lõi (3 dạng, thang tìm kiếm, §10, no-clobber); rút gọn Validate cứng + bỏ bước 7 cũ | Task 7 (toàn bộ, đặc biệt Bước 4-6, 8 giữ nguyên nội dung; "Validate cứng" rút gọn) |
| Rủi ro "ranh giới unit không ổn định qua re-import" | Task 7 (Bước 8, xử lý header hợp cũ+mới) — không tự động di trú, đúng như "Không làm trong phạm vi này" của spec |
| Rủi ro "subagent song song không đồng bộ" | Task 7 (Bước 3, ghi rõ chấp nhận giới hạn) |
| `srs-from-code.md` không đổi | Không có task nào đụng file này — đúng phạm vi |

Không có mục spec nào thiếu task.

**Placeholder scan:** không còn `TBD`/`TODO`/mô tả suông không kèm code. Mọi step có code
thật hoặc lệnh chạy thật kèm expected output cụ thể.

**Type consistency:** `slugify`/`dedupe_slugs`/`is_leaf`/`is_leaf_parent`/`default_units`
(Task 2) → dùng nguyên trong `compute_paths`/`render_tree`/CLI (Task 3). `subtree_leaves`
(Task 1, `fnlist_tree.py`) → dùng trong `cmd_units` (Task 3) và `main()` của
`intel_verify.py` (Task 5). Các hàm `check_*`/`parse_*`/`find_placeholders` (Task 4) →
dùng nguyên trong `verify()` hoàn chỉnh (Task 5), không đổi tên. CLI flags
(`--functions`, `--start`, `--roots`, `--root`, `--before`) nhất quán xuyên Task 3, 5, 7.
