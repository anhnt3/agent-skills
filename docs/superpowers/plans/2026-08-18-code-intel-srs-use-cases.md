# Code-intel/srs-from-code use_cases[] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `code-intel` treat a leaf's `use_cases[]` (BA-declared, already in `functions.json`
since the prior plan) as the mandatory `S-n` framework for its intel §12 "Kịch bản Use Case",
and make `srs-from-code` stop hard-coding the three business-classification fields once
`code-intel` can populate them from a matched `use_cases[]` item.

**Architecture:** `intel_tree.py` gets a small, additive extension (no change to `is_leaf`/
`compute_paths`/`propose`/`units`' existing contract) that surfaces `use_cases[]` per leaf —
in the confirmation tree (`render_tree`, a new `·`-marked line under a node) and in the
per-unit data (`cmd_units`'s `fn_ids`, a new optional `use_cases` key). `commands/code-intel.md`
reads this to (a) show the use-case breakdown in its existing bước-1 confirmation checkpoint
and (b) drive §12 generation: one `###` block per `use_cases[]` item when present (fixed
identity + order, code search per item, "not found" written inline instead of dropped or
deferred to §8), falling back to today's self-discovery when a leaf has none.
`commands/srs-from-code.md` gets a small, mechanical change: rót the three fields from
`intel §12` instead of always writing "Chưa có thông tin".

**Tech Stack:** Python 3 (stdlib only), pytest, Markdown (agent-instruction prompt files).

**Spec:** [docs/superpowers/specs/2026-08-18-code-intel-srs-use-cases-design.md](../specs/2026-08-18-code-intel-srs-use-cases-design.md)

## Global Constraints

- Vietnamese content throughout every user-facing string/doc; English identifiers in code.
- `intel_tree.py`'s existing contract (`is_leaf`, `is_leaf_parent`, `default_units`,
  `compute_paths`, `propose`/`units` CLI shape) is UNCHANGED — this plan only adds a new,
  optional `use_cases` key to `cmd_units`'s `fn_ids` entries and new `·`-marked lines to
  `render_tree`'s output. Every existing test in `test_intel_tree.py` must keep passing
  UNMODIFIED (only additions allowed) — this is the proof default behavior (leaves without
  `use_cases[]`) is untouched.
- `use_cases` key in `cmd_units`'s output is **absent** (not `[]`) on a leaf with no
  `use_cases[]` — mirrors `functions.json`'s own "vắng mặt = không có" convention and is what
  keeps the existing exact-dict-equality tests in `test_intel_tree.py` passing unmodified.
- `code-intel §12`'s "kỷ luật ba dạng" (đọc thẳng / suy đoán / không có căn cứu → §8) stays
  intact for every field EXCEPT `Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng`, which are the
  one long-standing, deliberate exception (business classification code cannot answer) — this
  plan does not relax that exception into "read từ mô tả Excel của use_cases[] khi không tìm
  thấy code": a `use_cases[]`-driven branch with no code evidence still gets
  "Chưa tìm thấy hiện thực trong mã nguồn." for its descriptive fields, exactly like the
  existing FN-level convention, never text invented from the Excel description.
- Neither `code-intel` nor `srs-from-code` gains a NEW mid-generation `AskUserQuestion` call —
  both files have an existing, explicit "does not ask during bước 5-8/5-9" principle. The
  extra-branches-found-after-scanning case is folded into the EXISTING end-of-run report
  (bước 11), not a new blocking prompt.
- Scope is **only** `speckit-extension/scripts/intel_tree.py`,
  `speckit-extension/commands/code-intel.md`, `speckit-extension/commands/srs-from-code.md`,
  and `speckit-extension/scripts/tests/test_intel_tree.py`. Do **not** touch
  `scripts/intel_verify.py` or `scripts/srs_verify.py` (per spec's "Ngoài phạm vi") or change
  what `intel_tree.py propose`/`units` considers a "unit" (still FN-tree-only, `use_cases[]`
  never affects unit boundaries).
- Run tests with `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -q`
  from the repo root (`e:\agent-skills`) — no venv/openpyxl needed (this test file never
  touches `.xlsx`).

---

### Task 1: `intel_tree.py` exposes `use_cases[]` — checkpoint tree + `cmd_units`

**Files:**
- Modify: `speckit-extension/scripts/intel_tree.py:100-108` (`render_tree`),
  `speckit-extension/scripts/intel_tree.py:132-150` (`cmd_units`)
- Test: `speckit-extension/scripts/tests/test_intel_tree.py`

**Interfaces:**
- Produces: `it.render_tree(nodes, unit_ids, depth=0)` — now also emits, immediately after a
  node's own line and its `children` subtree, one line per `use_cases[]` item on that node:
  `"  " * (depth + 1) + f"· {uc['name']} ({uc['id']})"`. `it.cmd_units`'s JSON output gains an
  optional `use_cases` key on each `fn_ids` entry (present only when the leaf has
  `use_cases[]`), each item shaped
  `{"id", "name", "description", "status", "importance", "type", "usage_timing"}` — the last
  three default to `""` when the source `functions.json` doesn't carry them (mirrors how
  `status` already defaults to `"pending"`).
- Consumes: `functions.json` nodes' `use_cases[]` field (already produced by `fnlist_tree.py`'s
  `clean_use_case`, from the prior plan) — no new dependency, this task only reads a key that
  already exists in the file format.

- [ ] **Step 1: Write the failing tests**

Add to `speckit-extension/scripts/tests/test_intel_tree.py`, after
`test_render_tree_no_marker_when_not_a_unit` (after line 129):

```python
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
```

Add near the end of the file, after `test_cli_units_defaults_missing_status_to_pending`
(after line 210):

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -k "use_case" -v`
Expected: FAIL — `render_tree` tests fail because no `·` lines are emitted yet (assertion
mismatch); `test_cli_units_includes_use_cases_when_present` fails with `KeyError:
'use_cases'` (key doesn't exist yet in the CLI output);
`test_cli_units_omits_use_cases_key_when_leaf_has_none` should already PASS (regression
check — confirm it does, since today's `cmd_units` never adds this key at all).

- [ ] **Step 3: Implement**

Replace `speckit-extension/scripts/intel_tree.py:100-108` (`render_tree`):

```python
def render_tree(nodes: list[dict], unit_ids: set[str], depth: int = 0) -> list[str]:
    """Cây thụt lề, đánh dấu `[UNIT]` ở node là ranh giới unit đề xuất — để
    LLM trình cho người dùng xác nhận/điều chỉnh trước khi quét."""
    lines = []
    for node in nodes:
        marker = "  [UNIT]" if node["id"] in unit_ids else ""
        lines.append("  " * depth + f"{node['name']} ({node['id']}){marker}")
        lines.extend(render_tree(node.get("children") or [], unit_ids, depth + 1))
    return lines
```

with:

```python
def render_tree(nodes: list[dict], unit_ids: set[str], depth: int = 0) -> list[str]:
    """Cây thụt lề, đánh dấu `[UNIT]` ở node là ranh giới unit đề xuất — để
    LLM trình cho người dùng xác nhận/điều chỉnh trước khi quét. Use-case con
    (`use_cases[]`, nếu leaf có) in thêm ngay dưới, đánh dấu `·` — cùng quy
    ước đã dùng ở checkpoint của `fnlist-import` — để người dùng xác nhận
    luôn cả khung `S-n` trước khi `code-intel` bắt đầu tìm bằng chứng."""
    lines = []
    for node in nodes:
        marker = "  [UNIT]" if node["id"] in unit_ids else ""
        lines.append("  " * depth + f"{node['name']} ({node['id']}){marker}")
        lines.extend(render_tree(node.get("children") or [], unit_ids, depth + 1))
        for uc in node.get("use_cases") or []:
            lines.append("  " * (depth + 1) + f"· {uc['name']} ({uc['id']})")
    return lines
```

Replace `speckit-extension/scripts/intel_tree.py:132-150` (`cmd_units`):

```python
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

with:

```python
UC_FIELDS = ("importance", "type", "usage_timing")


def _fn_entry(lf: dict) -> dict:
    """Một leaf FN → mục trong `fn_ids`. Khoá `use_cases` chỉ thêm khi leaf
    thật sự có — vắng mặt khi không có, đúng quy ước "vắng mặt = không có"
    của `functions.json`, để không phá lệnh gọi cũ chỉ mong đúng ba khoá
    `id`/`name`/`status`."""
    entry = {"id": lf["id"], "name": lf["name"], "status": lf.get("status", "pending")}
    use_cases = lf.get("use_cases")
    if use_cases:
        entry["use_cases"] = [
            {"id": uc["id"], "name": uc["name"],
             "description": uc.get("description", ""),
             "status": uc.get("status", "pending"),
             **{k: uc.get(k, "") for k in UC_FIELDS}}
            for uc in use_cases
        ]
    return entry


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
            "fn_ids": [_fn_entry(lf) for lf in leaves],
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -q`
Expected: PASS, all tests green (24 pre-existing + 5 new).

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_tree.py speckit-extension/scripts/tests/test_intel_tree.py
git commit -m "feat(code-intel): intel_tree.py exposes use_cases[] in checkpoint tree and units output"
```

---

### Task 2: `commands/code-intel.md` — confirm use_cases[] up front, drive §12 from it

**Files:**
- Modify: `speckit-extension/commands/code-intel.md`

**Interfaces:** None (prompt content only, no code). Consumes Task 1's `intel_tree.py`
output shape (`fn_ids[].use_cases`, `render_tree`'s `·` lines) — described, not called, by
this Markdown file.

This task has no automated test — verification is a manual read-through against the spec's
§3/§4/§6, checked in Step 2 below.

- [ ] **Step 1a: Bước 1 — note the use-case breakdown is part of what gets confirmed**

Find (currently around line 72-74):

```
In ra danh sách unit đề xuất (mặc định: node có tất cả con đều là lá, hoặc node không
có con đứng một mình) kèm cây thụt lề có đánh dấu `[UNIT]`. Trình nguyên văn cây này cho
người dùng qua AskUserQuestion: xác nhận đúng ranh giới, hay muốn gộp/tách lại?
```

Replace with:

```markdown
In ra danh sách unit đề xuất (mặc định: node có tất cả con đều là lá, hoặc node không
có con đứng một mình) kèm cây thụt lề có đánh dấu `[UNIT]` — leaf nào có `use_cases[]`
(BA đã khai từ Excel) thì cây này in thêm các dòng `·` ngay dưới, đó chính là khung `S-n`
sẽ dùng ở bước 5 §12. Trình nguyên văn cây này cho người dùng qua AskUserQuestion: xác
nhận đúng ranh giới unit, VÀ đúng khung use-case của từng leaf (dòng `·`) — đây là cấu
trúc đã biết trước (đọc thẳng từ `functions.json`, không phụ thuộc code), nên xác nhận
được ngay ở đây, trước khi bắt đầu quét.
```

- [ ] **Step 1b: Bước 5 — rewrite the "Kịch bản Use Case (§12)" subsection**

Find the block starting at "**Kịch bản Use Case (§12)**" and ending right before
"### 6. Ghi phát hiện đáng chú ý" (currently lines 221-266 — the whole subsection covering
the field-by-field rules, the "Ranh giới rõ" bullets, and the "Gộp câu hỏi §8 theo unit"
paragraph):

```
**Kịch bản Use Case (§12)** — sau khi §2 và §5 đã ghi xong (mục này phụ thuộc cả hai),
với mỗi màn hình đã có ở §2: dựng một khối `### [Tên Use Case]` trong §12, KHÔNG quét
code lần hai — tái dùng đúng bằng chứng đã thu:

- **Màn hình**: lấy nguyên văn từ cột "Màn hình / endpoint" của §2 — đây là khoá liên
  kết, phải khớp chính xác.
- **`Người dùng`**: suy từ §6 (bảng Phân quyền, cột Vai trò) nếu có dòng khớp màn hình
  này; không có → suy từ đối tượng dùng màn hình đó ở §2, đánh dấu `(suy đoán)`.
- **`Người sử dụng và yêu cầu`**, **`Mô tả tóm tắt`**: viết từ chính bằng chứng của §5
  (mô tả luồng) + §2 (tên màn hình) — một câu/đoạn tóm gọn, cite trỏ về cùng `file:dòng`
  đã dùng ở §5 cho luồng tương ứng.
- **`Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`**: viết lại đúng bằng chứng của §5 theo
  khuôn đánh số/nhánh `S-n` của Use Case, KHÔNG suy luận bước mới ngoài những gì §5 đã
  có. §5 không có luồng nào ứng với màn hình này → xem ranh giới và cách gộp câu hỏi §8
  ngay dưới đây.
- **`Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng`**: LUÔN ghi cố định "Chưa có thông
  tin" — đây là phân loại nghiệp vụ thuần, không có căn cứ code nào trả lời được.
  **Không đưa ba field này xuống §8** — khác kỷ luật ba dạng đang áp cho các field còn
  lại, vì đây không phải "chưa tìm ra" mà là "cấu trúc không thể tìm ra"; đưa xuống §8
  sẽ cộng thêm 3 câu hỏi vô nghĩa cho MỖI use case vào trần `§8`.

**Ranh giới rõ trước khi quyết định viết gì** — hai tình huống "không có gì để viết cho
màn này" dễ bị lẫn, phải tách đúng ngay từ đầu:

- **Màn hình/điểm vào không có use case thật nào** (endpoint kỹ thuật thuần — webhook
  nội bộ, health-check, cron trigger, không gắn với luồng người dùng nào) → **không viết
  khối `###`** cho nó, và **không đưa gì xuống §8** (khác §11 — §12 không có dòng giải
  trình `không-có-UI` riêng). Đây là lối thoát WARNING-only của `check_section12_coverage`:
  `intel_verify.py` ở bước 9 chỉ cảnh báo chứ không chặn nếu bỏ sót, người soát tự quyết
  có bổ sung hay không — cùng tinh thần với cách các mục khác của pipeline này xử lý thứ
  không có bằng chứng để rút.
- **Màn hình này CÓ use case thật, chỉ là §5 hiện chưa ghi luồng nào ứng với nó** → vẫn
  viết khối `###` bình thường (các field khác vẫn rút được từ §2/§6); riêng
  `Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ` không viết được có căn cứ → đưa xuống §8 với
  nhãn `[không suy được từ code]`, KHÔNG bỏ khối `###`.

**Gộp câu hỏi §8 theo unit, không theo từng màn hình**: khi nhiều màn hình trong cùng
một unit đều rơi vào ca thứ hai ở trên (có use case thật nhưng thiếu luồng §5), không
tạo một mục §8 riêng cho mỗi màn — gộp thành **một** mục duy nhất liệt kê tên các màn
hình đó, vd: "`[không suy được từ code]` Các màn hình sau chưa có luồng nghiệp vụ ở §5 để
dựng Luồng sự kiện chuẩn: <Màn A>, <Màn B>, …". Lý do: nhãn `[không suy được từ code]` là
nhãn duy nhất tính vào trần `check_section8_cap` (`max(3, M/3)`); một unit có nhiều màn
cùng thiếu luồng §5 mà tạo mỗi màn một mục riêng dễ đẩy tổng số mục §8 vượt trần và
BLOCKING, trong khi ca này (thiếu luồng §5 cho một use case có thật) là ca duy nhất ở §12
vẫn phải xuống §8 — ba field phân loại nghiệp vụ ở trên đã được chặn khỏi §8 hoàn toàn,
nên càng cần gộp ca còn lại để không tự đẩy unit vào chặn cứng.
```

Replace with:

```markdown
**Kịch bản Use Case (§12)** — sau khi §2 và §5 đã ghi xong (mục này phụ thuộc cả hai).
Leaf đang xử lý **có `use_cases[]`** (đã xác nhận ở bước 1, lấy từ `fn_ids[].use_cases`
của `intel_tree.py units`) hay **không** quyết định hẳn cách dựng §12 — hai đường tách
biệt, không trộn:

**A. Leaf có `use_cases[]`** — khung `S-n` CỐ ĐỊNH theo đúng tên/thứ tự các item đó,
không tự khám phá cách chia khác:

Với MỖI item trong `use_cases[]` (đúng thứ tự), dựng một khối `### [Tên item]` (tên lấy
nguyên văn từ `use_cases[].name`, không phải tên màn hình). Tìm bằng chứng code khớp use
case này: áp lại thang tìm kiếm ở bước 4 (tra tên/từ khoá tiếng Việt qua file ngôn ngữ lấy
key trước, rồi Grep), khoanh vùng trong §2/§5 đã rút của leaf này — KHÔNG quét code lần
hai ngoài phạm vi đó.

- **Tìm thấy** màn hình/luồng khớp → field như đường B dưới đây: `Màn hình` nguyên văn từ
  §2, `Người dùng` suy từ §6/§2, `Người sử dụng và yêu cầu`/`Mô tả tóm tắt`/`Luồng sự kiện
  chuẩn`/`Luồng sự kiện nhỏ` từ §5, cite đầy đủ.
- **Không tìm thấy** → `Màn hình` VÀ bốn field còn lại (`Người sử dụng và yêu cầu`/`Mô tả
  tóm tắt`/`Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`) đều ghi đúng nguyên văn "Chưa tìm
  thấy hiện thực trong mã nguồn." — **KHÔNG bịa nội dung từ mô tả `use_cases[].description`
  của Excel** (kỷ luật ba dạng vẫn áp dụng nguyên vẹn: không có căn cứ code thì không
  viết, mô tả Excel không phải một nguồn hợp lệ để thay). **KHÔNG đưa xuống §8** — đây là
  kết luận "chưa hiện thực", không phải câu hỏi, cùng tinh thần với "Chưa tìm thấy hiện
  thực trong mã nguồn." đã dùng ở cấp FN.
- **`Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng`**: lấy TRỰC TIẾP từ
  `importance`/`type`/`usage_timing` của đúng item `use_cases[]` này nếu có giá trị — đây
  vẫn là ngoại lệ hợp lý duy nhất dùng dữ liệu Excel không qua code (ba field này VỐN LÀ
  phân loại nghiệp vụ thuần, đã miễn trừ khỏi kỷ luật ba dạng từ trước). Không có giá trị
  (Excel không khai cột đó) → vẫn ghi "Chưa có thông tin" như cũ. **Không đưa ba field này
  xuống §8** trong mọi trường hợp (tìm thấy hay không) — lý do như đường B dưới đây.
- **Không có khái niệm "màn hình không có use case thật nào" ở đường này** — `use_cases[]`
  đã xác nhận CÓ use case thật (BA đã khai từ Excel), nên LUÔN viết đủ khối `###` cho MỌI
  item, không có nhánh bỏ qua.
- Quét thấy MỘT màn hình/luồng thật có use case rõ ràng nhưng KHÔNG khớp bất kỳ
  `use_cases[]` nào đã khai (code làm nhiều hơn Excel liệt kê) → vẫn dựng thêm khối
  `### [Tên tự đặt từ màn hình/luồng đó]` như đường B (tự khám phá), đặt SAU các khối
  theo `use_cases[]`, và ghi nhớ đây là nhánh phát sinh thêm — bước 11 sẽ gộp báo cáo toàn
  bộ nhánh phát sinh thêm của unit thành **một lượt hỏi duy nhất** ở cuối, KHÔNG dừng lại
  hỏi ngay tại đây (mâu thuẫn với "bước 5-8 không AskUserQuestion").

**B. Leaf không có `use_cases[]`** — giữ nguyên hành vi hiện tại, không đổi gì: với mỗi
màn hình đã có ở §2, dựng một khối `### [Tên Use Case]`, KHÔNG quét code lần hai — tái
dùng đúng bằng chứng đã thu:

- **Màn hình**: lấy nguyên văn từ cột "Màn hình / endpoint" của §2 — đây là khoá liên
  kết, phải khớp chính xác.
- **`Người dùng`**: suy từ §6 (bảng Phân quyền, cột Vai trò) nếu có dòng khớp màn hình
  này; không có → suy từ đối tượng dùng màn hình đó ở §2, đánh dấu `(suy đoán)`.
- **`Người sử dụng và yêu cầu`**, **`Mô tả tóm tắt`**: viết từ chính bằng chứng của §5
  (mô tả luồng) + §2 (tên màn hình) — một câu/đoạn tóm gọn, cite trỏ về cùng `file:dòng`
  đã dùng ở §5 cho luồng tương ứng.
- **`Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`**: viết lại đúng bằng chứng của §5 theo
  khuôn đánh số/nhánh `S-n` của Use Case, KHÔNG suy luận bước mới ngoài những gì §5 đã
  có. §5 không có luồng nào ứng với màn hình này → xem ranh giới và cách gộp câu hỏi §8
  ngay dưới đây.
- **`Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng`**: LUÔN ghi cố định "Chưa có thông
  tin" — đây là phân loại nghiệp vụ thuần, không có căn cứ code nào trả lời được.
  **Không đưa ba field này xuống §8** — khác kỷ luật ba dạng đang áp cho các field còn
  lại, vì đây không phải "chưa tìm ra" mà là "cấu trúc không thể tìm ra"; đưa xuống §8
  sẽ cộng thêm 3 câu hỏi vô nghĩa cho MỖI use case vào trần `§8`.

**Ranh giới rõ trước khi quyết định viết gì (chỉ áp cho đường B)** — hai tình huống
"không có gì để viết cho màn này" dễ bị lẫn, phải tách đúng ngay từ đầu:

- **Màn hình/điểm vào không có use case thật nào** (endpoint kỹ thuật thuần — webhook
  nội bộ, health-check, cron trigger, không gắn với luồng người dùng nào) → **không viết
  khối `###`** cho nó, và **không đưa gì xuống §8** (khác §11 — §12 không có dòng giải
  trình `không-có-UI` riêng). Đây là lối thoát WARNING-only của `check_section12_coverage`:
  `intel_verify.py` ở bước 9 chỉ cảnh báo chứ không chặn nếu bỏ sót, người soát tự quyết
  có bổ sung hay không — cùng tinh thần với cách các mục khác của pipeline này xử lý thứ
  không có bằng chứng để rút.
- **Màn hình này CÓ use case thật, chỉ là §5 hiện chưa ghi luồng nào ứng với nó** → vẫn
  viết khối `###` bình thường (các field khác vẫn rút được từ §2/§6); riêng
  `Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ` không viết được có căn cứ → đưa xuống §8 với
  nhãn `[không suy được từ code]`, KHÔNG bỏ khối `###`.

**Gộp câu hỏi §8 theo unit, không theo từng màn hình (chỉ áp cho đường B)**: khi nhiều
màn hình trong cùng một unit đều rơi vào ca thứ hai ở trên (có use case thật nhưng thiếu
luồng §5), không tạo một mục §8 riêng cho mỗi màn — gộp thành **một** mục duy nhất liệt
kê tên các màn hình đó, vd: "`[không suy được từ code]` Các màn hình sau chưa có luồng
nghiệp vụ ở §5 để dựng Luồng sự kiện chuẩn: <Màn A>, <Màn B>, …". Lý do: nhãn `[không suy
được từ code]` là nhãn duy nhất tính vào trần `check_section8_cap` (`max(3, M/3)`); một
unit có nhiều màn cùng thiếu luồng §5 mà tạo mỗi màn một mục riêng dễ đẩy tổng số mục §8
vượt trần và BLOCKING, trong khi ca này (thiếu luồng §5 cho một use case có thật) là ca
duy nhất ở §12 vẫn phải xuống §8 — ba field phân loại nghiệp vụ ở trên đã được chặn khỏi
§8 hoàn toàn, nên càng cần gộp ca còn lại để không tự đẩy unit vào chặn cứng. Đường A
không có ca này (không tìm thấy → ghi ngay tại nhánh, không xuống §8 — xem trên).
```

- [ ] **Step 1c: Bước 10 — set status on the matched `use_cases[]` item too**

Find (currently around lines 369-378):

```
Với mỗi FN-ID **tìm thấy** trong unit mà `status` hiện tại (từ bước 2) **không phải
`srs`** (không lùi trạng thái — đã qua `srs-from-code` thì không đặt lại `intel`):

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=intel [--set FN-01-02=intel ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate, và đổi status là hành vi có
thể lùi lại. FN-ID vốn đã `srs` thì bỏ qua, không đưa vào `--set`.
```

Replace with:

```markdown
Với mỗi FN-ID **tìm thấy** trong unit mà `status` hiện tại (từ bước 2) **không phải
`srs`** (không lùi trạng thái — đã qua `srs-from-code` thì không đặt lại `intel`), **và**
với mỗi item `use_cases[]` đã xử lý ở §12 đường A (khối `###` dựng từ nó, dù tìm thấy code
hay không — cả hai đều tính là "đã xử lý" nhánh đó) mà `status` hiện tại không phải `srs`:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=intel --set FN-01-01-UC-01=intel \
  [--set FN-01-02=intel ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate, và đổi status là hành vi có
thể lùi lại. FN-ID hoặc ID `use_cases[]` vốn đã `srs` thì bỏ qua, không đưa vào `--set`.
Nhánh `S-n` tự khám phá từ code (đường B, hoặc nhánh phát sinh thêm ở đường A không khớp
`use_cases[]` nào) không có ID `use_cases[]` nào để set — chỉ set FN-ID leaf như cũ.
```

- [ ] **Step 1d: "Sai lầm thường gặp" — add entries for the new §12 rules**

Append these bullets to the end of the existing list (after the last bullet, about §11/§12
name-matching mismatches):

```markdown
- **Tự khám phá cách chia `S-n` từ code khi leaf đã có `use_cases[]`** → khung `S-n` CỐ
  ĐỊNH theo đúng tên/thứ tự `use_cases[]`, không tự phát minh cách chia khác cho leaf đó.
- **Bịa nội dung `Người sử dụng và yêu cầu`/`Mô tả tóm tắt`/`Luồng sự kiện` từ mô tả
  `use_cases[].description` (Excel) khi không tìm thấy code** → phá kỷ luật ba dạng; ghi
  đúng "Chưa tìm thấy hiện thực trong mã nguồn." như quy định, không dùng Excel thay code.
- **Đưa nhánh `use_cases[]` không tìm thấy code xuống §8** → đây là kết luận "chưa hiện
  thực", không phải câu hỏi chờ trả lời; ghi ngay tại nhánh, không đưa xuống §8.
- **Dừng lại hỏi AskUserQuestion ngay khi thấy nhánh `S-n` phát sinh thêm (code nhiều hơn
  Excel khai)** → gộp vào đúng một lượt ở bước 11 cuối cùng, không hỏi giữa lúc sinh.
- **Quên set status cho ID `use_cases[]` item ở bước 10, chỉ set FN-ID leaf** → tiến độ
  của riêng use-case đó không được ghi nhận dù đã xử lý xong ở §12.
```

- [ ] **Step 2: Manual verification**

Re-read the whole file top to bottom, checking against
`docs/superpowers/specs/2026-08-18-code-intel-srs-use-cases-design.md` §3-4-6:

- Bước 1's confirmation text mentions the `·` lines and that they're part of what gets
  confirmed.
- Bước 5's §12 subsection cleanly separates đường A (has `use_cases[]`) from đường B
  (fallback, unchanged from before this task) — no leftover text that conflates the two.
- Bước 10 sets both FN-ID and matched `use_cases[]` IDs.
- "Sai lầm thường gặp" covers the new failure modes.

Confirm no stray `{CORE_TEMPLATE}` token or broken Markdown (unclosed code fence):

```bash
grep -c '```' speckit-extension/commands/code-intel.md
```

Expected: an even count (every fence opened is closed).

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/code-intel.md
git commit -m "docs(code-intel): use_cases[] drives §12 S-n framework, confirmed up front"
```

---

### Task 3: `commands/srs-from-code.md` — rót the three fields, set use-case status

**Files:**
- Modify: `speckit-extension/commands/srs-from-code.md`

**Interfaces:** None (prompt content only). Consumes intel §12 content that Task 2 makes
possibly-non-hardcoded.

This task has no automated test — verification is a manual read-through, checked in Step 2.

- [ ] **Step 1a: Bước 5 — stop hard-coding the three fields when rót to `d.`**

Find (currently around lines 220-223):

```
**Ba field của §12 luôn ghi cố định "Chưa có thông tin" khi rót sang `d. Kịch bản trường
hợp sử dụng`**: `Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng` — đây là phân loại
nghiệp vụ thuần, `intel §12` (theo đúng thiết kế của nó) cũng luôn ghi "Chưa có thông
tin" cho ba field này, rót nguyên văn sang, không tự suy đoán giá trị khác.
```

Replace with:

```markdown
**Ba field `Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng` khi rót sang `d. Kịch bản
trường hợp sử dụng`: rót NGUYÊN VĂN giá trị `intel §12` đã ghi cho use case này** — có
thể là giá trị thật (khi `code-intel` tìm được khớp `use_cases[]` có giá trị Excel cho
field đó) hoặc vẫn "Chưa có thông tin" (khi không khớp được, hoặc `intel §12` sinh theo
đường tự khám phá không có `use_cases[]` nguồn). `srs-from-code` không tự tra
`functions.json` để lấy ba field này — chỉ rót đúng những gì `intel.md` đã ghi, giữ
nguyên ranh giới nội bộ/giao khách hiện có (không tự suy đoán giá trị khác với những gì
`intel §12` đã kết luận).
```

- [ ] **Step 1b: Bước 10 — set status on the matched `use_cases[]` item too**

Find (currently around lines 586-591):

```
Mọi FN thuộc unit đã xuất hiện trong ít nhất một `<!-- FN: ... -->` → đặt trạng thái `srs`:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=srs [--set FN-01-02=srs ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate toàn bộ ID trước khi ghi.
```

Replace with:

```markdown
Mọi FN thuộc unit đã xuất hiện trong ít nhất một `<!-- FN: ... -->` → đặt trạng thái
`srs`. **Cùng lúc**, với mỗi khối `###` ở `intel §12` (đường A, dựng từ `use_cases[]`) đã
rót thành một nhánh `S-n` trong `srs.md` — dù tìm thấy code hay "Chưa tìm thấy hiện thực
trong mã nguồn." — đặt luôn `srs` cho đúng ID `use_cases[]` item đó:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=srs --set FN-01-01-UC-01=srs \
  [--set FN-01-02=srs ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate toàn bộ ID trước khi ghi.
Nhánh `S-n` tự khám phá từ code (không có `use_cases[]` nguồn) không có ID nào để set —
chỉ set FN-ID leaf như cũ.
```

- [ ] **Step 1c: "Sai lầm thường gặp" — add entries for the new rules**

Append these bullets to the end of the existing list (after the last bullet, about
subagent not reporting warnings back):

```markdown
- **Tự bịa lại "Chưa có thông tin" cho `Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng` dù
  `intel §12` đã ghi giá trị thật** → rót nguyên văn những gì `intel.md` có, không tự ý
  ghi đè bằng "Chưa có thông tin" theo thói quen cũ.
- **Quên set status cho ID `use_cases[]` item ở bước 10, chỉ set FN-ID leaf** → tiến độ
  của riêng use-case đó không được ghi nhận dù đã rót xong vào `srs.md`.
```

- [ ] **Step 2: Manual verification**

Re-read bước 5 và bước 10 against
`docs/superpowers/specs/2026-08-18-code-intel-srs-use-cases-design.md` §5-6. Confirm no
stray `{CORE_TEMPLATE}` token or broken Markdown (unclosed code fence):

```bash
grep -c '```' speckit-extension/commands/srs-from-code.md
```

Expected: an even count.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/srs-from-code.md
git commit -m "docs(srs-from-code): rót use_cases[] fields instead of hard-coding, set use-case status"
```

---

### Task 4: End-to-end smoke check of the new `intel_tree.py` contract

**Files:** none modified — verification only, using a synthetic `functions.json` shaped
like the real `Fnclist.xlsx`-derived data (the actual file's `use_cases[]` were produced by
the prior plan's Task 8 smoke test, not persisted anywhere in this repo, so this task builds
a small representative fixture instead of depending on that ephemeral state).

- [ ] **Step 1: Run the full `intel_tree.py` test suite**

```bash
python -m pytest speckit-extension/scripts/tests/test_intel_tree.py -v
```

Expected: PASS, every test (24 pre-existing + 5 new from Task 1) green.

- [ ] **Step 2: Build a synthetic functions.json matching the real absorb shape and run `units`**

```bash
SCRATCH=$(python -c "import tempfile; print(tempfile.mkdtemp())")
python - "$SCRATCH" <<'PY'
import json, pathlib, sys
doc = {
    "schema_version": 1, "system": "DMS", "source": {}, "updated": "2026-08-18",
    "retired_ids": [], "functions": [
        {"id": "FN-01", "name": "Quan ly tai lieu", "description": "", "children": [
            {"id": "FN-01-01", "name": "Quan tri he thong va Nguoi dung",
             "description": "", "children": [], "use_cases": [
                {"id": "FN-01-01-UC-01", "name": "Quan ly danh sach nguoi dung",
                 "description": "..."},
                {"id": "FN-01-01-UC-02", "name": "Quan ly co cau phong ban",
                 "description": "..."},
                {"id": "FN-01-01-UC-03", "name": "Quan ly phan quyen va vai tro",
                 "description": "..."},
                {"id": "FN-01-01-UC-04", "name": "Quan ly tai khoan va xac thuc",
                 "description": "..."},
            ]},
        ]},
    ],
}
(pathlib.Path(sys.argv[1]) / "functions.json").write_text(
    json.dumps(doc, ensure_ascii=False), encoding="utf-8")
PY
python speckit-extension/scripts/intel_tree.py propose \
  --functions "$SCRATCH/functions.json"
python speckit-extension/scripts/intel_tree.py units \
  --functions "$SCRATCH/functions.json" --roots FN-01-01
```

Expected: `propose`'s `tree` field contains 4 lines starting with `· ` under
`Quan tri he thong va Nguoi dung (FN-01-01)` (one per `use_cases[]` item). `units`'s output
has `units[0].fn_ids[0].use_cases` as a 4-item array, each with `id`/`name`/`description`/
`status`/`importance`/`type`/`usage_timing` (the last three all `""` since this fixture
doesn't set them).

- [ ] **Step 3: Clean up the scratch directory**

```bash
rm -rf "$SCRATCH"
```

No commit for this task — verification only, confirming Task 1's script contract holds
end-to-end for the exact shape `code-intel`/`srs-from-code` (Tasks 2-3) will consume.
