# Reverse SRS Commands — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm ba command vào extension `dft-speckit` để reverse tài liệu SRS từ function list (.xlsx/.csv) và codebase đã hoàn thiện.

**Architecture:** Đường ống ba bước, mỗi bước để lại một file trên đĩa cho người dùng review: `fnlist-import` → `.specify/docs/functions.md`; `code-intel` → `.specify/docs/<cụm>/intel.md` (có `file:line`, nội bộ); `srs` → `.specify/docs/<cụm>/srs.md` (theo khung ban hành, giao khách). Hai script Python làm phần tất định (đọc Excel, chấm cổng nghiệm thu), ba command `.md` là prompt điều phối và phỏng vấn.

**Tech Stack:** Python 3 stdlib + `openpyxl` (tự bootstrap `.venv` như `csv_to_xlsx.py`), pytest cho test script, Markdown cho command/template, YAML manifest `extension.yml`.

**Spec:** `docs/superpowers/specs/2026-08-10-reverse-srs-from-codebase-design.md`

## Global Constraints

- Toàn bộ nội dung người dùng nhìn thấy (mô tả command, prompt, tên mục tài liệu, thông báo script) viết **tiếng Việt**. Tên flag, tên file, slug thư mục viết **tiếng Anh** (`--deep`, `--template`, `fnlist_import.py`).
- Command mới phải khai trong `speckit-extension/extension.yml` dưới `provides.commands`; template mới khai dưới `provides.templates`. File không khai = không có tác dụng.
- Namespace command: `speckit.dft-speckit.<name>`.
- Đường dẫn dữ liệu: `.specify/docs/functions.md`, `.specify/docs/<cụm>/intel.md`, `.specify/docs/<cụm>/srs.md`.
- Script Python: chỉ cần `python3` sẵn có; phụ thuộc ngoài stdlib phải tự bootstrap `.venv` theo đúng khuôn `speckit-extension/scripts/csv_to_xlsx.py:319-332`.
- Test đặt tại `speckit-extension/scripts/tests/`, chạy bằng `pytest`. `conftest.py` đã chèn `sys.path` tới `scripts/`, không cần lặp lại.
- **Chặn cứng chỉ hai kiểm tra tất định**: mã chức năng thiếu dòng trong ma trận truy vết, và placeholder `[…]` còn sót. Mọi kiểm tra cần phán đoán → cảnh báo, `exit 0`.
- Bump `version` trong `extension.yml` trước khi release; version hiện tại `0.0.8`, plan này lên `0.1.0`.
- Không sửa `build-zip.sh`: `templates/` copy ở dòng 39, `scripts/` copy ở dòng 46–52 (đã loại `.venv`, `__pycache__`, `scripts/tests/`). Task 9 chỉ **kiểm chứng**, không sửa.

## File Structure

**Create:**
- `speckit-extension/scripts/fnlist_import.py` — đọc .xlsx/.csv, sinh `functions.md`. Hai subcommand `inspect` (dò cấu trúc, không đoán) và `write` (chép nguyên văn theo ánh xạ cột).
- `speckit-extension/scripts/srs_verify.py` — chấm `srs.md`: hai cổng chặn + ba nhóm cảnh báo.
- `speckit-extension/scripts/tests/test_fnlist_import.py`
- `speckit-extension/scripts/tests/test_srs_verify.py`
- `speckit-extension/templates/intel-template.md` — khung tám mục cho `intel.md`.
- `speckit-extension/commands/fnlist-import.md`
- `speckit-extension/commands/code-intel.md`
- `speckit-extension/commands/srs-from-code.md`

**Modify:**
- `speckit-extension/extension.yml` — khai 3 command + 2 template, bump version.
- `speckit-extension/README.md` — mục mô tả đường ống mới.

**Already exists (không sửa):**
- `speckit-extension/templates/srs-template.md` — đã tạo ở bước brainstorming.

---

### Task 1: `fnlist_import.py` — subcommand `inspect`

Đọc file .xlsx/.csv và in cấu trúc thật ra JSON. Script **không đoán** cột nào là gì; đó là việc của LLM ở bước sau. Đây là lý do `inspect` tách khỏi `write`.

**Files:**
- Create: `speckit-extension/scripts/fnlist_import.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: không có (task đầu tiên)
- Produces:
  - `cell_str(v) -> str` — chuẩn hoá một ô về chuỗi
  - `read_grid(path: str | Path, sheet: str | None = None) -> dict[str, list[list[str]]]` — trả `{tên_sheet: lưới ô}`; CSV cho đúng một sheet tên là stem của file
  - `cmd_inspect(a: argparse.Namespace) -> None` — in JSON ra stdout

- [ ] **Step 1: Write the failing test**

Tạo `speckit-extension/scripts/tests/test_fnlist_import.py`:

```python
import json
import subprocess
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
    ["STT", "Nhóm", "Tên chức năng", "Mô tả"],
    ["1", "Xác thực", "Đăng nhập", "Đăng nhập bằng tài khoản được cấp"],
    ["2", "Xác thực", "Quên mật khẩu", "Đặt lại mật khẩu qua email"],
    ["", "", "", ""],
    ["3", "Hồ sơ", "Cập nhật hồ sơ", "Sửa tên và số điện thoại"],
]


def test_cell_str_normalises_numbers_and_none():
    assert fi.cell_str(None) == ""
    assert fi.cell_str(3.0) == "3"
    assert fi.cell_str(3.5) == "3.5"
    assert fi.cell_str("  x  ") == "x"


def test_read_grid_csv_returns_single_sheet(tmp_path):
    p = write_csv(tmp_path, SAMPLE)
    grids = fi.read_grid(p)
    assert list(grids) == ["fnlist"]
    assert grids["fnlist"][0] == ["STT", "Nhóm", "Tên chức năng", "Mô tả"]
    assert len(grids["fnlist"]) == 5


def test_inspect_prints_shape_and_head(tmp_path, capsys):
    p = write_csv(tmp_path, SAMPLE)
    import argparse
    fi.cmd_inspect(argparse.Namespace(path=str(p), sheet=None, max_rows=3, max_cols=10))
    out = json.loads(capsys.readouterr().out)
    sheet = out["sheets"][0]
    assert sheet["name"] == "fnlist"
    assert sheet["rows"] == 5
    assert sheet["cols"] == 4
    assert len(sheet["head"]) == 3
    assert sheet["head"][1][2] == "Đăng nhập"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_fnlist_import.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'fnlist_import'`

- [ ] **Step 3: Write minimal implementation**

Tạo `speckit-extension/scripts/fnlist_import.py`:

```python
#!/usr/bin/env python3
"""Function list (.xlsx/.csv) → .specify/docs/functions.md.

Kỷ luật: SCRIPT CHÉP NGUYÊN VĂN, LLM chỉ quyết ánh xạ cột. Đây là văn bản hợp
đồng nghiệm thu — không tóm tắt, không chuẩn hoá, không "làm đẹp" nội dung ô.

Hai subcommand:
  inspect  — in cấu trúc thật của file (sheet, số dòng, vài dòng đầu). Không đoán gì.
  write    — nhận ánh xạ cột dạng JSON, chép nguyên văn ô, ghi functions.md.

Tự dựng venv + openpyxl lần đầu (chỉ khi đọc .xlsx). Chỉ cần python3.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HEADER = ["FN-ID", "Nhóm", "Tên chức năng", "Mô tả", "Cụm", "Nguồn code", "Trạng thái"]
FN_ID_RE = re.compile(r"^FN-(\d{3,})$")
XLSX_SUFFIXES = {".xlsx", ".xlsm"}


def cell_str(v) -> str:
    """Một ô → chuỗi. Số nguyên dạng float (openpyxl trả 3.0) về "3" cho khỏi
    lệch với bản gõ tay trong Word/Excel."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def _read_csv(path: Path) -> list[list[str]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [[cell_str(c) for c in row] for row in csv.reader(f)]


def _read_xlsx(path: Path, sheet: str | None) -> dict[str, list[list[str]]]:
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    names = [sheet] if sheet else wb.sheetnames
    out: dict[str, list[list[str]]] = {}
    for name in names:
        if name not in wb.sheetnames:
            raise SystemExit(f"Không có sheet '{name}'. Sheet hiện có: {wb.sheetnames}")
        ws = wb[name]
        rows = [[cell_str(c) for c in row] for row in ws.iter_rows(values_only=True)]
        while rows and not any(rows[-1]):
            rows.pop()
        out[name] = rows
    return out


def read_grid(path, sheet: str | None = None) -> dict[str, list[list[str]]]:
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"Không thấy file: {path}")
    if path.suffix.lower() in XLSX_SUFFIXES:
        return _read_xlsx(path, sheet)
    return {path.stem: _read_csv(path)}


def cmd_inspect(a) -> None:
    grids = read_grid(a.path, a.sheet)
    out = {"file": str(a.path), "sheets": []}
    for name, rows in grids.items():
        out["sheets"].append({
            "name": name,
            "rows": len(rows),
            "cols": max((len(r) for r in rows), default=0),
            "head": [r[: a.max_cols] for r in rows[: a.max_rows]],
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description="Function list → functions.md")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("inspect", help="In cấu trúc thật của file, không đoán cột")
    i.add_argument("path")
    i.add_argument("--sheet", default=None)
    i.add_argument("--max-rows", type=int, default=8, dest="max_rows")
    i.add_argument("--max-cols", type=int, default=12, dest="max_cols")
    i.set_defaults(func=cmd_inspect)

    a = p.parse_args(argv)
    a.func(a)


def _needs_openpyxl(argv) -> bool:
    return any(str(x).lower().endswith((".xlsx", ".xlsm")) for x in argv)


def _has_openpyxl() -> bool:
    try:
        import openpyxl  # noqa: F401
        return True
    except ImportError:
        return False


def _bootstrap_and_reexec():
    here = Path(__file__).resolve().parent
    venv = here / ".venv"
    py = venv / ("Scripts" if os.name == "nt" else "bin") / "python"
    if not py.exists():
        print("Lần đầu: đang tạo venv + cài openpyxl...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "venv", str(venv)])
        subprocess.check_call([str(py), "-m", "pip", "install", "-q", "openpyxl"])
    os.execv(str(py), [str(py), str(Path(__file__).resolve()), *sys.argv[1:]])


if __name__ == "__main__":
    if (_needs_openpyxl(sys.argv[1:]) and not _has_openpyxl()
            and os.environ.get("FNLIST_NO_BOOTSTRAP") != "1"):
        _bootstrap_and_reexec()
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_fnlist_import.py -v`
Expected: PASS — 3 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist): subcommand inspect đọc cấu trúc xlsx/csv"
```

---

### Task 2: `fnlist_import.py` — subcommand `write`

Chép nguyên văn theo ánh xạ cột, cấp `FN-ID` tăng dần, ghi `functions.md`. Đối chiếu số dòng và **báo cáo** dòng bị bỏ kèm lý do — không chặn, vì file thầu thật hay có dòng phân nhóm xen giữa.

**Files:**
- Modify: `speckit-extension/scripts/fnlist_import.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: `read_grid`, `cell_str`, `HEADER`, `FN_ID_RE` (Task 1)
- Produces:
  - `build_rows(grid: list[list[str]], mapping: dict) -> tuple[list[dict], list[dict]]` — `(kept, skipped)`; mỗi phần tử `kept` có khoá `row`, `nhom`, `ten`, `mo_ta`; mỗi `skipped` có `row`, `reason`, `raw`
  - `assign_ids(kept: list[dict], existing: dict[str, str]) -> list[dict]` — thêm khoá `id`
  - `escape_cell(s: str) -> str`
  - `render_markdown(rows: list[dict], system: str, source: str, date: str, prev: dict[str, dict]) -> str`
  - `cmd_write(a: argparse.Namespace) -> None`

Định dạng `mapping` JSON (LLM sinh sau khi đọc output `inspect`) — chỉ số cột **0-based**:

```json
{
  "sheet": "Sheet1",
  "first_data_row": 1,
  "columns": {"nhom": 1, "ten": 2, "mo_ta": 3},
  "skip_rows": [12, 30]
}
```

`first_data_row` là chỉ số 0-based của dòng dữ liệu đầu tiên (dòng header thường là 0 → `first_data_row: 1`). `skip_rows` dùng số dòng **1-based** đúng như người dùng nhìn trong Excel.

- [ ] **Step 1: Write the failing test**

Thêm vào `speckit-extension/scripts/tests/test_fnlist_import.py`:

```python
MAPPING = {"first_data_row": 1, "columns": {"nhom": 1, "ten": 2, "mo_ta": 3}}


def test_build_rows_keeps_named_rows_and_reports_skips():
    kept, skipped = fi.build_rows(SAMPLE, MAPPING)
    assert [r["ten"] for r in kept] == ["Đăng nhập", "Quên mật khẩu", "Cập nhật hồ sơ"]
    assert [r["row"] for r in kept] == [2, 3, 5]
    assert len(skipped) == 1
    assert skipped[0]["row"] == 4
    assert skipped[0]["reason"] == "ô tên chức năng trống"


def test_build_rows_honours_explicit_skip_rows():
    kept, skipped = fi.build_rows(SAMPLE, {**MAPPING, "skip_rows": [3]})
    assert [r["ten"] for r in kept] == ["Đăng nhập", "Cập nhật hồ sơ"]
    reasons = {s["row"]: s["reason"] for s in skipped}
    assert reasons[3] == "người dùng khai bỏ"


def test_assign_ids_is_sequential_from_one():
    kept, _ = fi.build_rows(SAMPLE, MAPPING)
    fi.assign_ids(kept, {})
    assert [r["id"] for r in kept] == ["FN-001", "FN-002", "FN-003"]


def test_assign_ids_reuses_existing_id_for_same_name():
    kept, _ = fi.build_rows(SAMPLE, MAPPING)
    fi.assign_ids(kept, {"Quên mật khẩu": "FN-007"})
    assert [r["id"] for r in kept] == ["FN-001", "FN-007", "FN-002"]


def test_assign_ids_gives_new_id_to_duplicate_names():
    # Dòng đầu dùng lại ID cũ; dòng trùng tên phía sau phải được cấp ID mới,
    # lấy số nhỏ nhất chưa dùng (FN-001), KHÔNG dùng chung FN-005.
    kept = [{"ten": "Đăng nhập"}, {"ten": "Đăng nhập"}]
    fi.assign_ids(kept, {"Đăng nhập": "FN-005"})
    assert kept[0]["id"] == "FN-005"
    assert kept[1]["id"] == "FN-001"


def test_escape_cell_protects_table_syntax():
    assert fi.escape_cell("a|b") == "a\\|b"
    assert fi.escape_cell("dòng1\ndòng2") == "dòng1<br>dòng2"


def test_write_creates_functions_md(tmp_path):
    src = write_csv(tmp_path, SAMPLE)
    out = tmp_path / "functions.md"
    mapping = tmp_path / "map.json"
    mapping.write_text(json.dumps(MAPPING), encoding="utf-8")
    import argparse
    fi.cmd_write(argparse.Namespace(
        path=str(src), mapping=str(mapping), out=str(out),
        system="DMS", date="2026-08-10", sheet=None))
    text = out.read_text(encoding="utf-8")
    assert "| FN-ID | Nhóm | Tên chức năng | Mô tả | Cụm | Nguồn code | Trạng thái |" in text
    assert "| FN-001 | Xác thực | Đăng nhập |" in text
    assert "**Tổng số chức năng**: 3" in text
    assert text.count("| FN-") == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_fnlist_import.py -v`
Expected: FAIL — `AttributeError: module 'fnlist_import' has no attribute 'build_rows'`

- [ ] **Step 3: Write minimal implementation**

Thêm vào `speckit-extension/scripts/fnlist_import.py`, trước `def main`:

```python
def build_rows(grid: list[list[str]], mapping: dict) -> tuple[list[dict], list[dict]]:
    """Lọc dòng dữ liệu thật khỏi lưới ô. Dòng bị bỏ KHÔNG biến mất im lặng —
    mọi dòng bỏ đều vào `skipped` kèm lý do để LLM báo lại cho người dùng."""
    cols = mapping.get("columns", {})
    first = int(mapping.get("first_data_row", 1))
    skip = {int(x) for x in mapping.get("skip_rows", [])}
    kept: list[dict] = []
    skipped: list[dict] = []
    for i, raw in enumerate(grid):
        if i < first:
            continue
        rowno = i + 1  # 1-based, khớp số dòng người dùng thấy trong Excel

        def get(key: str) -> str:
            idx = cols.get(key)
            if idx is None or idx >= len(raw):
                return ""
            return raw[idx]

        if rowno in skip:
            skipped.append({"row": rowno, "reason": "người dùng khai bỏ", "raw": raw[:6]})
            continue
        ten = get("ten")
        if not ten:
            skipped.append({"row": rowno, "reason": "ô tên chức năng trống", "raw": raw[:6]})
            continue
        kept.append({"row": rowno, "nhom": get("nhom"), "ten": ten, "mo_ta": get("mo_ta")})
    return kept, skipped


def assign_ids(kept: list[dict], existing: dict[str, str]) -> list[dict]:
    """Cấp FN-ID. Tên đã có ID cũ thì GIỮ NGUYÊN ID — domain doc và SRS cũ trỏ
    vào ID này, đánh số lại là gãy hết truy vết. Tên trùng nhau trong cùng file
    chỉ dùng lại ID cũ một lần, dòng sau cấp ID mới."""
    pool = dict(existing)
    used = {int(m.group(1)) for v in existing.values() if (m := FN_ID_RE.match(v))}
    nxt = 1
    for r in kept:
        old = pool.pop(r["ten"], None)
        if old:
            r["id"] = old
            continue
        while nxt in used:
            nxt += 1
        r["id"] = f"FN-{nxt:03d}"
        used.add(nxt)
    return kept


def escape_cell(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", "<br>")


def render_markdown(rows: list[dict], system: str, source: str, date: str,
                    prev: dict[str, dict] | None = None) -> str:
    """prev giữ ba cột do code-intel điền ngược (Cụm, Nguồn code, Trạng thái).
    Không giữ = mỗi lần import lại xoá sạch tiến độ đã làm."""
    prev = prev or {}
    lines = [
        f"# Danh mục chức năng — {system}",
        "",
        f"**Nguồn**: {source}",
        f"**Cập nhật**: {date}",
        f"**Tổng số chức năng**: {len(rows)}",
        "",
        "<!-- Cột Cụm / Nguồn code / Trạng thái do lệnh code-intel điền ngược. -->",
        "<!-- Trạng thái: chưa (mặc định) / intel / srs. Một chức năng thuộc nhiều cụm -->",
        "<!-- thì cột Cụm ghi nhiều giá trị, ngăn bằng dấu phẩy. -->",
        "",
        "| " + " | ".join(HEADER) + " |",
        "| " + " | ".join("---" for _ in HEADER) + " |",
    ]
    for r in rows:
        keep = prev.get(r["id"], {})
        lines.append("| " + " | ".join([
            r["id"],
            escape_cell(r.get("nhom", "")),
            escape_cell(r["ten"]),
            escape_cell(r.get("mo_ta", "")),
            keep.get("cum", ""),
            keep.get("nguon", ""),
            keep.get("trang_thai", "chưa"),
        ]) + " |")
    return "\n".join(lines) + "\n"


def cmd_write(a) -> None:
    grids = read_grid(a.path, a.sheet)
    name = a.sheet or next(iter(grids))
    grid = grids[name]
    mapping = json.loads(Path(a.mapping).read_text(encoding="utf-8"))
    kept, skipped = build_rows(grid, mapping)
    if not kept:
        raise SystemExit("Không lấy được dòng chức năng nào — kiểm lại ánh xạ cột.")
    assign_ids(kept, {})
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(kept, a.system, str(a.path), a.date), encoding="utf-8")
    print(json.dumps({
        "out": str(out),
        "scanned": len(grid) - int(mapping.get("first_data_row", 1)),
        "written": len(kept),
        "skipped": skipped,
    }, ensure_ascii=False, indent=2))
```

Trong `main`, thêm sau parser `inspect`:

```python
    w = sub.add_parser("write", help="Chép nguyên văn theo ánh xạ cột → functions.md")
    w.add_argument("path")
    w.add_argument("--mapping", required=True, help="File JSON ánh xạ cột")
    w.add_argument("--out", default=".specify/docs/functions.md")
    w.add_argument("--system", default="[TÊN HỆ THỐNG]")
    w.add_argument("--date", required=True, help="Ngày cập nhật YYYY-MM-DD")
    w.add_argument("--sheet", default=None)
    w.set_defaults(func=cmd_write)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_fnlist_import.py -v`
Expected: PASS — 10 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist): subcommand write sinh functions.md, ID ổn định"
```

---

### Task 3: `fnlist_import.py` — chạy lại không đè bản đã sửa tay

File đã tồn tại → ghi ra `functions.new.md` cạnh nó kèm bảng khác biệt, giữ nguyên `FN-ID` cũ theo tên và giữ ba cột `Cụm`/`Nguồn code`/`Trạng thái`.

**Files:**
- Modify: `speckit-extension/scripts/fnlist_import.py`
- Test: `speckit-extension/scripts/tests/test_fnlist_import.py`

**Interfaces:**
- Consumes: `render_markdown`, `assign_ids`, `build_rows`, `HEADER`, `FN_ID_RE` (Task 2)
- Produces:
  - `parse_functions_md(text: str) -> list[dict]` — mỗi dòng bảng thành `{"id","nhom","ten","mo_ta","cum","nguon","trang_thai"}`
  - `diff_rows(old: list[dict], new: list[dict]) -> list[dict]` — `{"loai": "thêm"|"bỏ"|"đổi tên"|"đổi mô tả", "id", "cu", "moi"}`

- [ ] **Step 1: Write the failing test**

Thêm vào `speckit-extension/scripts/tests/test_fnlist_import.py`:

```python
EXISTING_MD = """# Danh mục chức năng — DMS

**Nguồn**: cũ.csv
**Cập nhật**: 2026-08-01
**Tổng số chức năng**: 2

| FN-ID | Nhóm | Tên chức năng | Mô tả | Cụm | Nguồn code | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| FN-001 | Xác thực | Đăng nhập | mô tả cũ | user_and_authent | src/auth/ | srs |
| FN-002 | Xác thực | Quên mật khẩu | Đặt lại mật khẩu qua email |  |  | chưa |
"""


def test_parse_functions_md_reads_all_columns():
    rows = fi.parse_functions_md(EXISTING_MD)
    assert len(rows) == 2
    assert rows[0]["id"] == "FN-001"
    assert rows[0]["cum"] == "user_and_authent"
    assert rows[0]["trang_thai"] == "srs"
    assert rows[1]["mo_ta"] == "Đặt lại mật khẩu qua email"


def test_diff_rows_classifies_changes():
    old = fi.parse_functions_md(EXISTING_MD)
    new = [
        {"id": "FN-001", "ten": "Đăng nhập", "mo_ta": "mô tả mới"},
        {"id": "FN-003", "ten": "Cập nhật hồ sơ", "mo_ta": "Sửa tên"},
    ]
    kinds = {(d["loai"], d["id"]) for d in fi.diff_rows(old, new)}
    assert ("đổi mô tả", "FN-001") in kinds
    assert ("bỏ", "FN-002") in kinds
    assert ("thêm", "FN-003") in kinds


def test_write_on_existing_file_emits_new_file_and_preserves_columns(tmp_path):
    out = tmp_path / "functions.md"
    out.write_text(EXISTING_MD, encoding="utf-8")
    src = write_csv(tmp_path, SAMPLE)
    mapping = tmp_path / "map.json"
    mapping.write_text(json.dumps(MAPPING), encoding="utf-8")
    import argparse
    fi.cmd_write(argparse.Namespace(
        path=str(src), mapping=str(mapping), out=str(out),
        system="DMS", date="2026-08-10", sheet=None))

    assert out.read_text(encoding="utf-8") == EXISTING_MD  # bản cũ nguyên vẹn
    new = (tmp_path / "functions.new.md").read_text(encoding="utf-8")
    assert "| FN-001 | Xác thực | Đăng nhập |" in new
    assert "user_and_authent" in new   # giữ cột Cụm
    assert "| srs |" in new            # giữ cột Trạng thái
    assert "FN-003" in new             # chức năng mới được cấp ID kế tiếp
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_fnlist_import.py -v`
Expected: FAIL — `AttributeError: module 'fnlist_import' has no attribute 'parse_functions_md'`

- [ ] **Step 3: Write minimal implementation**

Thêm vào `speckit-extension/scripts/fnlist_import.py`:

```python
_KEYS = ["id", "nhom", "ten", "mo_ta", "cum", "nguon", "trang_thai"]


def parse_functions_md(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not FN_ID_RE.match(cells[0]):
            continue
        cells += [""] * (len(_KEYS) - len(cells))
        rows.append(dict(zip(_KEYS, cells)))
    return rows


def diff_rows(old: list[dict], new: list[dict]) -> list[dict]:
    old_by = {r["id"]: r for r in old}
    new_by = {r["id"]: r for r in new}
    out = []
    for fid, r in new_by.items():
        o = old_by.get(fid)
        if o is None:
            out.append({"loai": "thêm", "id": fid, "cu": "", "moi": r["ten"]})
        elif o["ten"] != r["ten"]:
            out.append({"loai": "đổi tên", "id": fid, "cu": o["ten"], "moi": r["ten"]})
        elif o.get("mo_ta", "") != r.get("mo_ta", ""):
            out.append({"loai": "đổi mô tả", "id": fid,
                        "cu": o.get("mo_ta", ""), "moi": r.get("mo_ta", "")})
    for fid, o in old_by.items():
        if fid not in new_by:
            out.append({"loai": "bỏ", "id": fid, "cu": o["ten"], "moi": ""})
    return out
```

Thay thân `cmd_write` từ chỗ `assign_ids(kept, {})` trở xuống bằng:

```python
    out = Path(a.out)
    old_rows: list[dict] = []
    if out.exists():
        old_rows = parse_functions_md(out.read_text(encoding="utf-8"))
    assign_ids(kept, {r["ten"]: r["id"] for r in old_rows})
    prev = {r["id"]: {"cum": r.get("cum", ""), "nguon": r.get("nguon", ""),
                      "trang_thai": r.get("trang_thai", "chưa")} for r in old_rows}
    text = render_markdown(kept, a.system, str(a.path), a.date, prev)

    target = out if not old_rows else out.with_name(out.stem + ".new" + out.suffix)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")

    report = {
        "out": str(target),
        "scanned": len(grid) - int(mapping.get("first_data_row", 1)),
        "written": len(kept),
        "skipped": skipped,
    }
    if old_rows:
        report["che_do"] = "khong-de-ban-cu"
        report["diff"] = diff_rows(old_rows, kept)
    print(json.dumps(report, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_fnlist_import.py -v`
Expected: PASS — 13 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/fnlist_import.py speckit-extension/scripts/tests/test_fnlist_import.py
git commit -m "feat(fnlist): chạy lại không đè bản cũ, giữ ID và cột tiến độ"
```

---

### Task 4: `srs_verify.py` — hai cổng chặn

Chỉ hai kiểm tra tất định mới được chặn: mã chức năng của cụm thiếu dòng trong ma trận truy vết, và placeholder `[…]` còn sót.

**Files:**
- Create: `speckit-extension/scripts/srs_verify.py`
- Test: `speckit-extension/scripts/tests/test_srs_verify.py`

**Interfaces:**
- Consumes: không có (module độc lập, không import `fnlist_import`)
- Produces:
  - `strip_noise(text: str) -> str` — bỏ HTML comment và khối code rào ```` ``` ````
  - `find_placeholders(text: str) -> list[dict]` — `{"line": int, "text": str}`
  - `parse_matrix(text: str) -> set[str]` — tập FN-ID trong bảng có cột `Mã chức năng` và `Mục SRS`
  - `cluster_functions(functions_md: str, cluster: str) -> list[str]` — FN-ID có `cluster` trong cột `Cụm`
  - `verify(srs_text: str, functions_md: str, cluster: str, template_text: str | None) -> dict` — `{"blocking": [...], "warnings": [...]}`

- [ ] **Step 1: Write the failing test**

Tạo `speckit-extension/scripts/tests/test_srs_verify.py`:

```python
import json
from pathlib import Path

import pytest

import srs_verify as sv

FUNCTIONS = """# Danh mục chức năng — DMS

| FN-ID | Nhóm | Tên chức năng | Mô tả | Cụm | Nguồn code | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| FN-001 | Xác thực | Đăng nhập | ... | user_and_authent | src/auth/ | intel |
| FN-002 | Xác thực | Quên mật khẩu | ... | user_and_authent | src/auth/ | intel |
| FN-009 | Hợp đồng | Danh sách hợp đồng | ... | contract | src/contract/ | chưa |
"""

SRS_OK = """# SRS — Quản lý tài khoản

# V. MA TRẬN TRUY VẾT

| Mã chức năng | Tên chức năng | Mục SRS đặc tả |
| --- | --- | --- |
| FN-001 | Đăng nhập | III.1 |
| FN-002 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |
"""


def test_cluster_functions_filters_by_cluster():
    assert sv.cluster_functions(FUNCTIONS, "user_and_authent") == ["FN-001", "FN-002"]
    assert sv.cluster_functions(FUNCTIONS, "contract") == ["FN-009"]


def test_parse_matrix_collects_ids():
    assert sv.parse_matrix(SRS_OK) == {"FN-001", "FN-002"}


def test_clean_document_has_no_blocking():
    r = sv.verify(SRS_OK, FUNCTIONS, "user_and_authent", None)
    assert r["blocking"] == []


def test_out_of_scope_row_counts_as_covered():
    r = sv.verify(SRS_OK, FUNCTIONS, "user_and_authent", None)
    assert not any("FN-002" in b["thong_diep"] for b in r["blocking"])


def test_missing_function_is_blocking():
    srs = SRS_OK.replace("| FN-002 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |\n", "")
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert any(b["loai"] == "thieu-fn" and "FN-002" in b["thong_diep"] for b in r["blocking"])


def test_placeholder_is_blocking():
    srs = SRS_OK + "\n## Phụ lục A — [Tên phụ lục]\n"
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert any(b["loai"] == "placeholder" for b in r["blocking"])


def test_markdown_link_is_not_a_placeholder():
    srs = SRS_OK + "\nXem [tài liệu tham khảo](https://example.com/a).\n"
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_mermaid_block_is_not_a_placeholder():
    srs = SRS_OK + "\n```mermaid\nflowchart TD\n    B[Nhập thông tin]\n```\n"
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])


def test_template_comment_placeholder_is_ignored():
    srs = SRS_OK + "\n<!-- điền [Tên phụ lục] vào đây -->\n"
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert not any(b["loai"] == "placeholder" for b in r["blocking"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_srs_verify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'srs_verify'`

- [ ] **Step 3: Write minimal implementation**

Tạo `speckit-extension/scripts/srs_verify.py`:

```python
#!/usr/bin/env python3
"""Chấm .specify/docs/<cụm>/srs.md trước khi báo xong.

Hai mức, theo đúng nguyên tắc §3.3 của spec:
  BLOCKING (exit 1) — chỉ thứ kiểm được TẤT ĐỊNH: mã chức năng của cụm thiếu
                      dòng trong ma trận truy vết, và placeholder [...] còn sót.
  WARNING  (exit 0) — thứ cần phán đoán: mục khung bị thiếu/lệch, chuỗi trông
                      giống đường dẫn code, mục con rỗng. In ra để người soát.

Chỉ cần python3, không phụ thuộc ngoài stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FN_ID_RE = re.compile(r"\bFN-\d{3,}\b")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FENCE_RE = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.S | re.M)
PLACEHOLDER_RE = re.compile(r"\[([^\[\]\n]{1,80})\](?!\()")
CHECKBOX_RE = re.compile(r"^[ x]$")
CODE_PATH_RE = re.compile(
    r"\b[\w.-]+/[\w./-]*\.\w{1,5}\b"
    r"|\b\w[\w.-]*\.(?:py|ts|tsx|js|jsx|java|cs|go|rb|php|vue|sql|kt|swift|yml|yaml)\b(?::\d+)?"
)


def strip_noise(text: str) -> str:
    """Bỏ HTML comment và khối code rào. Cả hai chứa dấu [] hợp lệ:
    comment là hướng dẫn của khung, khối mermaid dùng B[Nhập thông tin]."""
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return text


def find_placeholders(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(strip_noise(text).splitlines(), start=1):
        for m in PLACEHOLDER_RE.finditer(line):
            inner = m.group(1)
            if CHECKBOX_RE.match(inner):
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


def parse_matrix(text: str) -> set[str]:
    """Nhận diện bảng ma trận bằng TIÊU ĐỀ CỘT, không bằng số mục — dự án được
    phép thêm/đổi mục nên "mục V" không đáng tin, "Mã chức năng" thì đáng."""
    ids: set[str] = set()
    in_matrix = False
    for row in _table_rows(text):
        joined = " ".join(row).lower()
        if "mã chức năng" in joined and "mục srs" in joined:
            in_matrix = True
            continue
        if in_matrix:
            if all(set(c) <= set("-: ") for c in row):
                continue
            m = FN_ID_RE.search(row[0]) if row else None
            if m:
                ids.add(m.group(0))
            elif row and row[0] and not FN_ID_RE.search(row[0]):
                in_matrix = False
    return ids


def cluster_functions(functions_md: str, cluster: str) -> list[str]:
    out = []
    for row in _table_rows(functions_md):
        if not row or not FN_ID_RE.fullmatch(row[0]):
            continue
        cums = [c.strip() for c in (row[4] if len(row) > 4 else "").split(",")]
        if cluster in cums:
            out.append(row[0])
    return out


def _top_headings(text: str) -> list[str]:
    return [ln.strip().lstrip("#").strip()
            for ln in strip_noise(text).splitlines()
            if re.match(r"^#\s+\S", ln.strip())]


def _empty_sections(text: str) -> list[dict]:
    lines = strip_noise(text).splitlines()
    heads = [(i, ln) for i, ln in enumerate(lines) if re.match(r"^#{1,4}\s+\S", ln.strip())]
    out = []
    for n, (i, ln) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        body = "".join(x.strip() for x in lines[i + 1:end])
        if not body.replace("-", "").strip():
            out.append({"line": i + 1, "text": ln.strip()})
    return out


def verify(srs_text: str, functions_md: str, cluster: str,
           template_text: str | None = None) -> dict:
    blocking, warnings = [], []

    covered = parse_matrix(srs_text)
    wanted = cluster_functions(functions_md, cluster)
    missing = [f for f in wanted if f not in covered]
    if missing:
        blocking.append({
            "loai": "thieu-fn",
            "thong_diep": "Thiếu dòng trong ma trận truy vết: " + ", ".join(missing),
            "goi_y": "Thêm một dòng cho mỗi mã; chức năng không đặc tả thì "
                     "cột cuối ghi 'Ngoài phạm vi — <lý do>'.",
        })
    if not wanted:
        warnings.append({
            "loai": "cum-rong",
            "thong_diep": f"Không có chức năng nào mang cụm '{cluster}' trong functions.md.",
        })

    for ph in find_placeholders(srs_text):
        blocking.append({
            "loai": "placeholder",
            "thong_diep": f"Còn placeholder ở dòng {ph['line']}: {ph['text']}",
            "goi_y": "Điền nội dung, ghi 'Không có', hoặc xoá cả mục con.",
        })

    if template_text:
        want = _top_headings(template_text)
        have = _top_headings(srs_text)
        for h in want:
            if h not in have:
                warnings.append({"loai": "thieu-muc",
                                 "thong_diep": f"Khung có mục '{h}' mà tài liệu không có."})
        if [h for h in have if h in want] != [h for h in want if h in have]:
            warnings.append({"loai": "lech-thu-tu",
                             "thong_diep": "Thứ tự mục cấp 1 khác khung."})

    for i, line in enumerate(strip_noise(srs_text).splitlines(), start=1):
        for m in CODE_PATH_RE.finditer(line):
            warnings.append({
                "loai": "nghi-duong-dan-code",
                "thong_diep": f"Dòng {i} có chuỗi trông giống đường dẫn code: {m.group(0)}",
                "goi_y": "Tài liệu giao khách nên không nêu đường dẫn mã nguồn. "
                         "Nếu đây là tên file nghiệp vụ hợp lệ thì bỏ qua cảnh báo này.",
            })

    warnings.extend({"loai": "muc-rong",
                     "thong_diep": f"Mục rỗng ở dòng {e['line']}: {e['text']}"}
                    for e in _empty_sections(srs_text))

    return {"blocking": blocking, "warnings": warnings}


def main(argv=None):
    p = argparse.ArgumentParser(description="Chấm srs.md trước khi báo xong")
    p.add_argument("srs", help="Đường dẫn .specify/docs/<cụm>/srs.md")
    p.add_argument("--functions", default=".specify/docs/functions.md")
    p.add_argument("--cluster", required=True)
    p.add_argument("--template", default=None,
                   help="Khung để đối chiếu tên/thứ tự mục (cảnh báo, không chặn)")
    a = p.parse_args(argv)

    srs = Path(a.srs).read_text(encoding="utf-8")
    fns = Path(a.functions).read_text(encoding="utf-8")
    tpl = Path(a.template).read_text(encoding="utf-8") if a.template else None

    report = verify(srs, fns, a.cluster, tpl)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    n_b, n_w = len(report["blocking"]), len(report["warnings"])
    print(f"\n{n_b} lỗi chặn, {n_w} cảnh báo.", file=sys.stderr)
    if n_b:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_srs_verify.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/srs_verify.py speckit-extension/scripts/tests/test_srs_verify.py
git commit -m "feat(srs): script chấm srs.md, hai cổng chặn tất định"
```

---

### Task 5: `srs_verify.py` — cảnh báo và exit code

Xác nhận ba nhóm cảnh báo không làm `exit ≠ 0`, và cổng chặn thì có. Đây là ranh giới dễ bị cài sai nhất của cả plan.

**Files:**
- Modify: `speckit-extension/scripts/srs_verify.py` (chỉ nếu test lộ lỗi)
- Test: `speckit-extension/scripts/tests/test_srs_verify.py`

**Interfaces:**
- Consumes: `verify`, `main` (Task 4)
- Produces: không thêm hàm mới

- [ ] **Step 1: Write the failing test**

Thêm vào `speckit-extension/scripts/tests/test_srs_verify.py`:

```python
TEMPLATE = """# SRS — [TÊN CỤM]

# I. KIỂM SOÁT PHIÊN BẢN

# II. GIỚI THIỆU

# V. MA TRẬN TRUY VẾT
"""


def test_code_path_is_warning_not_blocking():
    srs = SRS_OK + "\nHành vi nằm ở src/auth/login.ts:42.\n"
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert r["blocking"] == []
    assert any(w["loai"] == "nghi-duong-dan-code" for w in r["warnings"])


def test_missing_template_section_is_warning_only():
    r = sv.verify(SRS_OK, FUNCTIONS, "user_and_authent", TEMPLATE)
    assert r["blocking"] == []
    kinds = {w["loai"] for w in r["warnings"]}
    assert "thieu-muc" in kinds


def test_empty_section_is_warning_only():
    srs = SRS_OK + "\n## 1.7. Giao tiếp hệ thống\n\n## 1.8. Khác\n\nCó nội dung.\n"
    r = sv.verify(srs, FUNCTIONS, "user_and_authent", None)
    assert r["blocking"] == []
    assert any(w["loai"] == "muc-rong" for w in r["warnings"])


def _run(tmp_path, srs_text, cluster="user_and_authent"):
    import subprocess
    srs = tmp_path / "srs.md"
    srs.write_text(srs_text, encoding="utf-8")
    fns = tmp_path / "functions.md"
    fns.write_text(FUNCTIONS, encoding="utf-8")
    script = Path(sv.__file__)
    return subprocess.run(
        [sys.executable, str(script), str(srs), "--functions", str(fns),
         "--cluster", cluster],
        capture_output=True, text=True, encoding="utf-8")


def test_cli_exits_zero_when_only_warnings(tmp_path):
    p = _run(tmp_path, SRS_OK + "\nXem src/auth/login.ts:42.\n")
    assert p.returncode == 0
    assert json.loads(p.stdout)["warnings"]


def test_cli_exits_one_when_blocking(tmp_path):
    srs = SRS_OK.replace("| FN-002 | Quên mật khẩu | Ngoài phạm vi — khách chưa nghiệm thu |\n", "")
    p = _run(tmp_path, srs)
    assert p.returncode == 1
    assert json.loads(p.stdout)["blocking"]
```

Thêm `import sys` vào đầu file test nếu chưa có.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd speckit-extension/scripts && python -m pytest tests/test_srs_verify.py -v`
Expected: FAIL ở ít nhất một test — nếu tất cả PASS ngay thì vẫn phải chạy để chứng minh, rồi ghi lại kết quả thật.

- [ ] **Step 3: Sửa cho tới khi xanh**

Chỉ sửa `srs_verify.py` nếu test đỏ. Điểm dễ sai đã biết:
- Nhánh đầu của `CODE_PATH_RE` đòi có dấu `/` nên `III.1` và `2026-08-10` không bị bắt; nhánh sau chỉ bắt đuôi trong danh sách cho trước. Nếu vẫn báo nhầm trên chuỗi nghiệp vụ thật, **thu hẹp danh sách đuôi** chứ đừng nới regex — cảnh báo thừa còn chịu được, cảnh báo sai kiểu khác thì mất tin.
- `_empty_sections` coi mục chỉ có dòng `---` là rỗng — đúng ý. Mục chỉ chứa bảng thì `body` có ký tự `|` nên không bị bắt.
- Tiêu đề tài liệu ở dòng 1 nếu đi thẳng tới heading kế sẽ ra một cảnh báo `muc-rong`. Chấp nhận được (chỉ là cảnh báo); đừng thêm ngoại lệ đặc biệt cho dòng 1 vì nó che luôn trường hợp mục đầu thật sự rỗng.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd speckit-extension/scripts && python -m pytest tests/ -v`
Expected: PASS — toàn bộ test của cả hai script mới, và không làm hỏng test cũ.

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/srs_verify.py speckit-extension/scripts/tests/test_srs_verify.py
git commit -m "test(srs): chốt ranh giới chặn/cảnh báo và exit code"
```

---

### Task 6: `intel-template.md`

Khung tám mục cho `.specify/docs/<cụm>/intel.md`. Đây là tài liệu **nội bộ** — giữ `file:line`, ngược với `srs-template.md`.

**Files:**
- Create: `speckit-extension/templates/intel-template.md`

**Interfaces:**
- Consumes: hình dạng mục thực thể của `speckit-extension/templates/domain-template.md`
- Produces: khung mà `commands/code-intel.md` (Task 8) sẽ trỏ tới

- [ ] **Step 1: Đọc khung thực thể đang có để bám hình dạng**

Run: `cat speckit-extension/templates/domain-template.md`
Mục đích: mục §3 của intel dùng lại cách mô tả entity/field/FK ở đó, để `domain-design` và `code-intel` không mâu thuẫn nhau về cách gọi tên.

- [ ] **Step 2: Viết `speckit-extension/templates/intel-template.md`**

```markdown
# Code intel — [TÊN CỤM]

**Cập nhật**: [DATE]
**Phủ chức năng**: [FN-001, FN-002, …]
**Độ sâu**: [gọn / sâu]

<!-- TÀI LIỆU NỘI BỘ. Không giao khách — chỗ giao khách là srs.md cùng thư mục.
     Mỗi khẳng định ở §2–§7 thuộc một trong ba dạng:
       - Đọc thẳng từ code   → ghi bình thường, kèm `đường/dẫn.ext:dòng`
       - Suy ra, chưa chắc   → ghi kèm nguồn gần nhất và đánh dấu (suy đoán)
       - Không căn cứ nào    → KHÔNG viết ở §2–§7; đưa xuống §8 thành câu hỏi
     Mục không áp dụng cho cụm này → ghi "Không có", giữ tiêu đề. -->

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| [FN-001] | [tên] | [đường/dẫn hoặc "không tìm thấy"] | [—] |

<!-- FN không tìm thấy code phải ghi rõ "không tìm thấy" — im lặng bỏ qua là
     cách tài liệu bàn giao thiếu chức năng mà không ai biết. -->

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| [tên] | [/route] | [file:dòng] | [FN-001] |

## 3. Thực thể và trường dữ liệu

### [TênThựcThể]

- **Nguồn**: [file:dòng]
- **Khoá chính**: [trường]
- **Quan hệ**: [FK → thực thể khác]

| Trường | Kiểu | Bắt buộc | Ràng buộc | Mặc định | Nguồn |
| --- | --- | --- | --- | --- | --- |
| [tên] | [kiểu] | [Có/Không] | [độ dài, miền giá trị, duy nhất] | [—] | [file:dòng] |

## 4. Kiểm tra hợp lệ và quy tắc nghiệp vụ

| # | Quy tắc | Nguồn | Độ chắc chắn |
| --- | --- | --- | --- |
| 1 | [điều kiện → hệ quả] | [file:dòng] | [chắc / suy đoán] |

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
     lần chạy lại sau sẽ không hỏi lại. -->

1. [Câu hỏi] — **Trả lời**: [để trống cho tới khi có]

## 9. Thông báo hiển thị

| Ngữ cảnh | Nguyên văn thông báo | Nguồn |
| --- | --- | --- |
| [tình huống] | "[nguyên văn]" | [file:dòng] |

<!-- Lấy từ file ngôn ngữ / hằng số / mã lỗi. Đây là nguồn cho mục "Xử lý ngoại
     lệ và thông báo" của srs.md — chép nguyên văn, không diễn đạt lại. -->
```

- [ ] **Step 3: Kiểm khung tự nhất quán**

Run:
```bash
grep -c '^## ' speckit-extension/templates/intel-template.md
```
Expected: `9` — tám mục theo spec cộng mục 9 (Thông báo hiển thị) tách riêng vì `srs-template.md` mục N.6 cần nguồn nguyên văn cho nó.

- [ ] **Step 4: Commit**

```bash
git add speckit-extension/templates/intel-template.md
git commit -m "feat(intel): khung intel-template cho tài liệu nội bộ"
```

---

### Task 7: Command `fnlist-import.md`

**Files:**
- Create: `speckit-extension/commands/fnlist-import.md`

**Interfaces:**
- Consumes: `scripts/fnlist_import.py` với hai subcommand `inspect` / `write` (Task 1–3)
- Produces: `.specify/docs/functions.md`; command `code-intel` (Task 8) đọc file này

- [ ] **Step 1: Viết command**

Tạo `speckit-extension/commands/fnlist-import.md` với frontmatter:

```markdown
---
description: Nhập function list (.xlsx/.csv) đã dùng nghiệm thu thành .specify/docs/functions.md — bảng markdown có FN-ID ổn định làm điểm neo truy vết cho mọi tài liệu bàn giao.
---
```

Thân command bám các mục sau, viết tiếng Việt, **mọi đường dẫn ghi nguyên văn**:

1. **Nguyên tắc mở đầu** — nêu rõ: *script chép nguyên văn, bạn chỉ quyết ánh xạ cột*. Cấm tóm tắt/chuẩn hoá/sửa chính tả nội dung ô; đây là văn bản hợp đồng nghiệm thu.
2. **User Input** — `$ARGUMENTS` là đường dẫn tới `.xlsx`/`.csv`. Trống, không tồn tại, hoặc sai đuôi → **hỏi lại**, KHÔNG tự đi tìm file trong repo.
3. **Kiểm `.gitignore`** — nếu `.specify/` bị ignore thì cảnh báo trước khi ghi: tài liệu bàn giao sẽ không vào git.
4. **Bước 1 — dò cấu trúc**: chạy
   `python3 .specify/extensions/dft-speckit/scripts/fnlist_import.py inspect "<đường-dẫn>"`
   (dùng `python` nếu `python3` không có). Đọc JSON trả về.
5. **Bước 2 — quyết ánh xạ cột**: từ `head`, xác định chỉ số 0-based của cột `nhom`, `ten`, `mo_ta` và `first_data_row`. Mơ hồ thì hỏi qua **AskUserQuestion**, mỗi lượt gom 1–4 câu độc lập. Ba tình huống bắt buộc hỏi, không tự chọn: **nhiều sheet**, **header hai tầng**, **cột mô tả không rõ là mô tả hay ghi chú**.
6. **Bước 3 — ghi**: viết mapping ra `.specify/tmp/fnlist/mapping.json` rồi chạy
   `python3 .specify/extensions/dft-speckit/scripts/fnlist_import.py write "<đường-dẫn>" --mapping .specify/tmp/fnlist/mapping.json --out .specify/docs/functions.md --system "<tên hệ thống>" --date <YYYY-MM-DD>`
7. **Bước 4 — đối chiếu**: đọc `skipped` trong JSON báo cáo. Có dòng bị bỏ → **liệt kê đích danh từng dòng kèm lý do** cho người dùng và hỏi có dòng nào thực ra là chức năng thật không. Bỏ nhầm thì thêm vào `skip_rows` ngược lại hoặc sửa `first_data_row` rồi chạy lại. **KHÔNG tự kết luận là ổn.**
8. **Bước 5 — chạy lại**: báo cáo có `che_do: khong-de-ban-cu` nghĩa là đã ghi ra `functions.new.md`, bản cũ nguyên vẹn. Trình bảng `diff` cho người dùng và để họ quyết hợp nhất; **KHÔNG tự copy đè**.
9. **Kết thúc**: báo số chức năng, đường dẫn file, và nhắc bước kế `/speckit.dft-speckit.code-intel <tên-cụm> <FN-001..FN-0xx>`.

- [ ] **Step 2: Chấm bằng skill review của repo**

Dùng skill `speckit-addon-reviewer` trên `speckit-extension/`. Sửa mọi phát hiện thuộc nhóm: đường-thoát (chỗ model có thể tự bỏ qua bước hỏi), thiếu neo đường dẫn, hoặc side-effect trước xác nhận.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/fnlist-import.md
git commit -m "feat(cmd): command fnlist-import"
```

---

### Task 8: Command `code-intel.md`

**Files:**
- Create: `speckit-extension/commands/code-intel.md`

**Interfaces:**
- Consumes: `.specify/docs/functions.md` (Task 2–3), `templates/intel-template.md` (Task 6)
- Produces: `.specify/docs/<cụm>/intel.md`; command `srs` (Task 9) đọc file này

- [ ] **Step 1: Viết command**

Frontmatter:

```markdown
---
description: Rút đặc tả từ codebase cho một cụm chức năng chỉ định bằng danh sách FN-ID, ghi .specify/docs/<cụm>/intel.md kèm nguồn file:dòng — tài liệu nội bộ làm đầu vào cho lệnh srs.
---
```

Thân command:

1. **User Input** — `$ARGUMENTS` dạng `<tên-cụm> <FN-001..FN-012 | FN-001,FN-005>` kèm cờ tuỳ chọn `--deep`.
2. **Kiểm đầu vào**:
   - Tên cụm phải khớp `[a-z0-9_-]+` (thành tên thư mục) → **chặn** nếu sai, hỏi lại.
   - Mọi FN phải có trong `.specify/docs/functions.md` → **chặn** nếu thiếu, gần như chắc chắn gõ nhầm mã.
   - FN đã có cụm khác ở cột `Cụm` → **cảnh báo, không chặn**. Chức năng nền như đăng nhập thuộc nhiều cụm là bình thường; nói rõ cho người dùng rồi đi tiếp.
   - `.specify/` bị gitignore → cảnh báo.
3. **Quét codebase**: với mỗi FN, tìm điểm vào (route/menu/controller) rồi lần theo tới service/repository/entity/validator. Ghi lại đường dẫn và số dòng của từng chỗ dùng làm căn cứ.
4. **Kỷ luật ghi — nêu nguyên văn trong command**:

   > Mỗi khẳng định ở §2–§7 thuộc một trong ba dạng: **đọc thẳng từ code** → ghi kèm `file:dòng`; **suy ra nhưng chưa chắc** → ghi kèm nguồn gần nhất và đánh dấu `(suy đoán)`; **không có căn cứ nào trong code** → KHÔNG viết ở §2–§7, đưa xuống §8 thành câu hỏi. Cấm ghi một khẳng định không nguồn, không dấu.

5. **Độ sâu**: mặc định mức gọn (§1, §2, §3 ở mức thực thể, §5, §6). Có `--deep` thì mở §3 tới từng trường (kiểu, độ dài, nullable, mặc định) và §4 tới từng quy tắc, cộng §9 thông báo hiển thị lấy nguyên văn từ file ngôn ngữ/hằng số.
6. **Lấy khung**: `specify preset resolve intel-template`; không resolve được → đọc `.specify/extensions/dft-speckit/templates/intel-template.md`; vẫn không thấy → hỏi.
7. **Ghi file**: tạo `.specify/docs/<cụm>/` nếu chưa có (có rồi thì dùng lại), ghi `intel.md`.
8. **No-clobber khi chạy lại**: đọc file hiện có trước. **Giữ nguyên mọi câu trả lời đã có ở §8** và mọi ghi chú người dùng thêm tay. Chỉ bổ sung/cập nhật phần rút mới.
9. **Ghi ngược `functions.md`**: với mỗi FN đã xử lý, thêm tên cụm vào cột `Cụm` (nối thêm bằng dấu phẩy nếu đã có giá trị khác — KHÔNG ghi đè), điền `Nguồn code`, đặt `Trạng thái` = `intel`. Sửa tại chỗ từng ô, không copy khung đè.
10. **Kiểm lại trước khi báo xong**: mỗi FN trong `$ARGUMENTS` có đúng một dòng ở §1; FN không tìm thấy code phải ghi rõ `không tìm thấy` chứ không bỏ trống; không còn placeholder `[…]`.
11. **Kết thúc**: báo số FN đã phủ, số mục §8 còn chờ trả lời, và nhắc `/speckit.dft-speckit.srs-from-code <tên-cụm>`.

- [ ] **Step 2: Chấm bằng skill review của repo**

Dùng skill `speckit-addon-reviewer`. Chú ý riêng: bước 9 (ghi ngược `functions.md`) là side-effect lên file dùng chung — xác nhận command nói rõ *nối thêm, không ghi đè*.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/code-intel.md
git commit -m "feat(cmd): command code-intel"
```

---

### Task 9: Command `srs-from-code.md`

**Files:**
- Create: `speckit-extension/commands/srs-from-code.md`

**Interfaces:**
- Consumes: `.specify/docs/<cụm>/intel.md` (Task 8), `templates/srs-template.md` (đã có), `scripts/srs_verify.py` (Task 4–5)
- Produces: `.specify/docs/<cụm>/srs.md`

- [ ] **Step 1: Viết command**

Frontmatter:

```markdown
---
description: Sinh .specify/docs/<cụm>/srs.md theo khung ban hành từ intel.md và functions.md — rót phần suy được từ code, phỏng vấn phần nghiệp vụ, chốt bằng cổng ma trận truy vết.
---
```

Thân command:

1. **User Input** — `$ARGUMENTS` dạng `<tên-cụm>` kèm cờ tuỳ chọn `--template <đường-dẫn>`.
2. **Điều kiện tiên quyết**: thiếu `.specify/docs/<cụm>/intel.md` → **DỪNG**, nhắc chạy `/speckit.dft-speckit.code-intel` trước. Nêu lý do ngay trong thông báo: SRS không có intel là viết từ trí tưởng tượng. Vẫn tạo thư mục cụm nếu chưa có, nhưng KHÔNG ghi `srs.md`.
3. **Lấy khung**: `--template` nếu có → `specify preset resolve srs-template` → `.specify/extensions/dft-speckit/templates/srs-template.md`. Không thấy → hỏi.
4. **Rót phần suy được từ intel**:
   - `intel §2` → `N.3` Mô tả chức năng (giao diện, bảng Mô tả điều khiển)
   - `intel §3` → `N.4` Đặc tả dữ liệu
   - `intel §4` → `N.5` Quy tắc nghiệp vụ
   - `intel §5` → `N.3` sơ đồ luồng (mermaid `flowchart TD`)
   - `intel §6` → `N.2` Đối tượng tham gia và phân quyền
   - `intel §7` → `N.7` Giao tiếp hệ thống
   - `intel §9` → `N.6` Xử lý ngoại lệ và thông báo, **chép nguyên văn**
   - `intel §1` → bảng `II.5` và ma trận `V`
5. **Chuyển hoá bắt buộc khi rót** — nêu nguyên văn trong command:

   > `intel.md` là tài liệu nội bộ, `srs.md` giao khách. Khi rót sang: **bỏ hết `file:dòng`, tên class, tên hàm, đường dẫn mã nguồn**. Khẳng định mang dấu `(suy đoán)` ở intel thì sang SRS đổi thành `(cần xác nhận)` — giữ dấu, đừng lặng lẽ gỡ.
   >
   > **Ngoại lệ — `N.4` Đặc tả dữ liệu**: mục này KHÔNG nhận suy đoán, kể cả có đánh dấu. Ràng buộc nào ở `intel §3` mang dấu `(suy đoán)` thì đừng rót vào `N.4`; thay vào đó hỏi người dùng ở bước 6, và điền câu trả lời của họ. Không hỏi được thì để ô đó là `—`. Lý do: `N.4` là chuẩn để QA dựng testcase biên và khách đối chiếu lúc nghiệm thu, một con số suy đoán lọt vào đây thành cam kết sai.

6. **Phỏng vấn phần code không trả lời được**: `II.1` Mục đích, `II.5` Phạm vi (đặc biệt hai mục *Ngoài phạm vi*), `IV` Yêu cầu phi chức năng, `N.1` Mục đích chức năng của từng chức năng, **mọi ràng buộc `N.4` mà `intel §3` đánh `(suy đoán)`**, cộng mọi câu chưa trả lời ở `intel §8`. Hỏi qua **AskUserQuestion**, mỗi lượt gom 1–4 câu độc lập. **Cấm bịa ngưỡng số** ở `IV` (thời gian phản hồi, số người dùng đồng thời) — không ai nêu thì ghi `Không có yêu cầu riêng`.
7. **Mục con không áp dụng thì lược bỏ** (chức năng thuần đọc không cần `N.4`, chức năng không gọi ra ngoài không cần `N.7`). Mục cấp I–VI thì giữ tiêu đề, ghi `Không có`.
8. **Cổng cuối — chạy trước khi báo xong**:
   ```
   python3 .specify/extensions/dft-speckit/scripts/srs_verify.py \
     .specify/docs/<cụm>/srs.md \
     --functions .specify/docs/functions.md \
     --cluster <tên-cụm> \
     --template <đường-dẫn khung đã dùng>
   ```
   `exit ≠ 0` là **cấm báo xong** — sửa rồi chạy lại. Cảnh báo (`exit 0`) thì **trình toàn bộ cho người dùng**, nói rõ đây là nhắc chứ không phải lỗi, và để họ quyết. **Cấm im lặng bỏ qua cảnh báo.**
9. **Cập nhật `functions.md`**: FN đã đặc tả → `Trạng thái` = `srs`.
10. **Kết thúc**: báo đường dẫn `srs.md`, số chức năng đã đặc tả, số chức năng khai ngoài phạm vi, số cảnh báo còn tồn.

- [ ] **Step 2: Chấm bằng skill review của repo**

Dùng skill `speckit-addon-reviewer`. Chú ý riêng: bước 8 là chỗ dễ có đường-thoát nhất — xác nhận command không cho phép báo xong khi `exit ≠ 0`, và không cho phép bỏ qua cảnh báo mà không trình bày.

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/srs-from-code.md
git commit -m "feat(cmd): command srs sinh tài liệu theo khung ban hành"
```

---

### Task 10: Khai manifest, README, và kiểm chứng gói cài

**Files:**
- Modify: `speckit-extension/extension.yml`
- Modify: `speckit-extension/README.md`

**Interfaces:**
- Consumes: mọi file của Task 1–9
- Produces: extension cài được qua `specify extension add`

- [ ] **Step 1: Khai 3 command + 2 template vào `extension.yml`**

Thêm vào `provides.commands` (giữ nguyên các mục có sẵn):

```yaml
    - name: "speckit.dft-speckit.fnlist-import"
      file: "commands/fnlist-import.md"
      description: "Nhập function list (.xlsx/.csv) đã dùng nghiệm thu thành .specify/docs/functions.md — script chép nguyên văn, LLM chỉ quyết ánh xạ cột. FN-ID ổn định làm điểm neo truy vết cho mọi tài liệu bàn giao; chạy lại không đè bản đã sửa tay (xuất functions.new.md kèm bảng khác biệt)."

    - name: "speckit.dft-speckit.code-intel"
      file: "commands/code-intel.md"
      description: "Rút đặc tả từ codebase cho một cụm chức năng chỉ định bằng danh sách FN-ID, ghi .specify/docs/<cụm>/intel.md kèm nguồn file:dòng. Tài liệu nội bộ: khẳng định đọc thẳng từ code ghi kèm nguồn, suy đoán đánh dấu, không căn cứ thì xuống mục câu hỏi. Cờ --deep mở tới từng trường và từng quy tắc."

    - name: "speckit.dft-speckit.srs-from-code"
      file: "commands/srs-from-code.md"
      description: "Sinh .specify/docs/<cụm>/srs.md theo khung ban hành từ intel.md và functions.md — rót phần suy được từ code (bỏ hết đường dẫn mã nguồn), phỏng vấn phần nghiệp vụ code không trả lời được, chốt bằng cổng srs_verify.py: mã chức năng thiếu dòng ma trận truy vết hoặc còn placeholder là cấm báo xong. Cờ --template để dùng khung riêng của khách."
```

Thêm vào `provides.templates`:

```yaml
    - name: "srs-template"
      file: "templates/srs-template.md"
      description: "Khung cố định cho .specify/docs/<cụm>/srs.md theo tài liệu ban hành của công ty, đẩy độ chi tiết lên mức SRS: thêm Đặc tả dữ liệu, Xử lý ngoại lệ và thông báo, Giao tiếp hệ thống, Yêu cầu phi chức năng, Ma trận truy vết. Kỷ luật một-nhà: hằng số field ở N.4, nội dung message ở N.6, mục khác trỏ tới."

    - name: "intel-template"
      file: "templates/intel-template.md"
      description: "Khung cho .specify/docs/<cụm>/intel.md — tài liệu nội bộ rút từ codebase, giữ nguồn file:dòng. Chín mục: phủ chức năng, màn hình/điểm vào, thực thể và trường, kiểm tra hợp lệ, luồng nghiệp vụ, phân quyền, tích hợp ngoài, câu hỏi chưa suy được từ code, thông báo hiển thị."
```

Bump version:

```yaml
  version: "0.1.0"
```

- [ ] **Step 2: Kiểm manifest hợp lệ và không sót file**

Run:
```bash
python3 -c "
import yaml, sys
from pathlib import Path
root = Path('speckit-extension')
m = yaml.safe_load((root/'extension.yml').read_text(encoding='utf-8'))
declared = {c['file'] for c in m['provides']['commands']} | {t['file'] for t in m['provides']['templates']}
on_disk = {str(p.relative_to(root)).replace('\\\\','/') for p in list((root/'commands').glob('*.md')) + list((root/'templates').glob('*.md'))}
missing = declared - on_disk
undeclared = on_disk - declared
print('khai mà không có file:', missing)
print('có file mà không khai:', undeclared)
sys.exit(1 if (missing or undeclared) else 0)
"
```
Expected: cả hai tập rỗng, exit 0.

- [ ] **Step 3: Cập nhật README**

Thêm mục "Reverse tài liệu từ codebase" vào `speckit-extension/README.md`, mô tả đường ống ba bước, sơ đồ file `.specify/docs/`, và một ví dụ chạy đầy đủ ba lệnh. Nêu rõ hai cổng chặn của `srs_verify.py` và việc cảnh báo không chặn.

- [ ] **Step 4: Kiểm chứng gói cài thật**

Run:
```bash
speckit-extension/build-zip.sh
unzip -l speckit-extension/dist/dft-speckit-0.1.0.zip | grep -E 'fnlist_import|srs_verify|srs-template|intel-template|fnlist-import|code-intel|commands/srs-from-code.md'
```
Expected: 7 dòng — hai script, hai template, ba command. Thiếu dòng nào nghĩa là `build-zip.sh` không copy tới, phải sửa trước khi đi tiếp (không kỳ vọng phải sửa: `templates/` copy ở dòng 39, `scripts/` ở dòng 46–52).

Run tiếp:
```bash
unzip -l speckit-extension/dist/dft-speckit-0.1.0.zip | grep -E '\.venv|__pycache__|scripts/tests'
```
Expected: không có dòng nào.

- [ ] **Step 5: Cài thử vào project vứt đi và chạy thật**

Đây là bài kiểm duy nhất bắt được lỗi "command tham chiếu đường dẫn `.specify/extensions/dft-speckit/...` mà file không có ở đó sau khi cài".

```bash
# Serve gói vừa build (--from từ chối file://, cần HTTPS hoặc localhost)
(cd speckit-extension/dist && python3 -m http.server 8799 &)

# Project vứt đi
mkdir -p /tmp/reverse-srs-smoke && cd /tmp/reverse-srs-smoke
specify init --here --integration claude
yes y | specify extension add dft-speckit --from http://localhost:8799/dft-speckit-0.1.0.zip --force

# Khẳng định các file support thật sự nằm đúng chỗ command trỏ tới
ls .specify/extensions/dft-speckit/scripts/fnlist_import.py
ls .specify/extensions/dft-speckit/scripts/srs_verify.py
ls .specify/extensions/dft-speckit/templates/srs-template.md
ls .specify/extensions/dft-speckit/templates/intel-template.md

# Script chạy được từ vị trí đã cài
printf 'STT,Nhóm,Tên chức năng,Mô tả\n1,Xác thực,Đăng nhập,Đăng nhập hệ thống\n' > fl.csv
python3 .specify/extensions/dft-speckit/scripts/fnlist_import.py inspect fl.csv
echo '{"first_data_row":1,"columns":{"nhom":1,"ten":2,"mo_ta":3}}' > map.json
python3 .specify/extensions/dft-speckit/scripts/fnlist_import.py write fl.csv \
  --mapping map.json --out .specify/docs/functions.md --system DMS --date 2026-08-10
cat .specify/docs/functions.md
```

Expected: bốn lệnh `ls` đều trả về đường dẫn (không `No such file`); `inspect` in JSON có `"rows": 2`; `functions.md` có dòng `| FN-001 | Xác thực | Đăng nhập |`.

Kiểm cổng chặn chạy được sau khi cài:
```bash
mkdir -p .specify/docs/thu
printf '# SRS\n\n| Mã chức năng | Tên chức năng | Mục SRS đặc tả |\n| --- | --- | --- |\n' \
  > .specify/docs/thu/srs.md
python3 .specify/extensions/dft-speckit/scripts/srs_verify.py \
  .specify/docs/thu/srs.md --functions .specify/docs/functions.md --cluster khong_co
echo "exit=$?"
```
Expected: `exit=0` kèm cảnh báo `cum-rong` (không FN nào thuộc cụm `khong_co` nên không có gì để chặn).

Dọn: `kill %1` cho server, `rm -rf /tmp/reverse-srs-smoke`.

- [ ] **Step 6: Chạy toàn bộ test**

Run: `cd speckit-extension/scripts && python -m pytest tests/ -q`
Expected: PASS toàn bộ, gồm cả test cũ của `brd_roadmap` và `csv_to_xlsx`.

- [ ] **Step 7: Commit**

```bash
git add speckit-extension/extension.yml speckit-extension/README.md
git commit -m "feat: khai 3 command reverse SRS vào manifest, bump 0.1.0"
```

---

## Ghi chú thực thi

**Thứ tự bắt buộc**: Task 1→2→3 chung một file, phải làm tuần tự. Task 4→5 chung một file, tuần tự. Task 6 độc lập. Task 7 cần Task 1–3; Task 8 cần Task 6; Task 9 cần Task 4–5 và Task 8. Task 10 cuối cùng.

**Chạy song song được**: nhóm (1,2,3) và nhóm (4,5) và Task 6 không đụng file nhau.

**Không có trong plan này, có chủ ý**: BRD, ADD, User Manual (spec §2 để ngoài phạm vi); test tự động cho ba file command (chúng là prompt, cổng chất lượng là skill `speckit-addon-reviewer` và bài kiểm cài đặt ở Task 10).
