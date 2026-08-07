# Kế hoạch hiện thực `road-map-from-brd`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm lệnh `/speckit.dft-speckit.road-map-from-brd` sinh `docs/roadmap.md` từ cây markdown `docs/brd/`, với một script gác cổng phủ 1-1 giữa node BRD và item roadmap.

**Architecture:** Script `scripts/brd_roadmap.py` (stdlib thuần, hai lệnh con `outline` | `verify`) làm phần cơ học: đọc `brd.manifest.yml` + các file `.md` để trích outline gọn, và đọc ngược `docs/roadmap.md` để chấm phủ/ID/phụ thuộc. LLM làm phần quyết định: phân loại node, chốt wave qua interview, ghi file theo `roadmap-template`. `verify` exit ≠ 0 là cấm báo xong.

**Tech Stack:** Python 3 stdlib (`argparse`, `re`, `json`, `pathlib`), pytest cho test, markdown cho command/template, YAML cho manifest extension.

**Spec:** [docs/superpowers/specs/2026-08-07-road-map-from-brd-design.md](../specs/2026-08-07-road-map-from-brd-design.md)

## Global Constraints

- Thư mục làm việc của mọi lệnh trong kế hoạch này: `speckit-extension/`.
- Script **không được thêm dependency**: stdlib thuần, không PyYAML. `brd.manifest.yml` do `scripts/brd/splitter.py` ghi theo định dạng flow một dòng mỗi node — parser nhắm đúng định dạng đó.
- Script mới đứng riêng ở `scripts/brd_roadmap.py`, **không** nhét vào package `scripts/brd/` (package đó đã có `outline.py` với ý nghĩa khác — outline của tài liệu Word).
- Toàn bộ nội dung command, template, thông điệp lỗi, docstring, tên test: **tiếng Việt**.
- Thông điệp lỗi thao tác: in một dòng ra stderr rồi exit 2 (theo hàm `_die` của `scripts/brd_import.py`). `verify` phát hiện lỗi nội dung thì exit 1 và in báo cáo JSON ra stdout.
- ID node BRD là **chuỗi** `BRD-%04d`; node gốc là `BRD-0000`, `kind: root`.
- ID item roadmap là `RM-\d{3}`.
- `build-zip.sh` **không sửa** — nó đã copy `scripts/` đệ quy và loại `scripts/tests/`.
- Chạy test: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`.

## Cấu trúc file

| File | Trách nhiệm |
|---|---|
| `speckit-extension/scripts/brd_roadmap.py` | **Tạo mới.** CLI + toàn bộ logic cơ học: parse manifest, trích outline, parse `roadmap.md`, chấm phủ/ID/phụ thuộc. Một file duy nhất (~350 dòng) vì hai lệnh con dùng chung parser manifest và chuẩn hoá đường dẫn; tách package chỉ để chia đôi sẽ làm nặng import mà không tăng rõ ràng. |
| `speckit-extension/scripts/tests/test_brd_roadmap.py` | **Tạo mới.** Test cho cả `outline` và `verify`, dựng fixture cây BRD nhỏ bằng tay. |
| `speckit-extension/commands/road-map-from-brd.md` | **Tạo mới.** Prompt lệnh: quy trình 7 bước, 2 lượt interview, mục "Sai lầm thường gặp". |
| `speckit-extension/templates/roadmap-template.md` | **Sửa.** Thêm dòng `- **Nguồn**:` vào khối chi tiết. |
| `speckit-extension/commands/road-map-from-codebase.md` | **Sửa.** Dạy nó điền `**Nguồn**` bằng đường dẫn code / `N/A`. |
| `speckit-extension/extension.yml` | **Sửa.** Khai command mới, bump `0.0.6` → `0.0.7`. |
| `speckit-extension/README.md` | **Sửa.** Thêm dòng bảng command + cây thư mục. |

---

### Task 1: Parse manifest + khung CLI `outline`

**Files:**
- Create: `speckit-extension/scripts/brd_roadmap.py`
- Test: `speckit-extension/scripts/tests/test_brd_roadmap.py`

**Interfaces:**
- Consumes: định dạng `brd.manifest.yml` do `scripts/brd/splitter.py::write_tree` ghi.
- Produces:
  - `parse_manifest(path: Path) -> list[dict]` — mỗi node có khoá `id, order, depth, kind, title, path (str|None), dir (str|None), inline (bool), parent (str|None), chars (int)`
  - `breadcrumbs(nodes: list[dict]) -> dict[str, list[str]]` — id → danh sách tiêu đề cha, gốc trước
  - `node_loc(node: dict) -> str` — `path` nếu có file, ngược lại `dir`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_brd_roadmap.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

import pytest

from brd_roadmap import breadcrumbs, node_loc, parse_manifest

SCRIPT = Path(__file__).resolve().parents[1] / "brd_roadmap.py"

MANIFEST = """schema_version: "1.0"
source:
  file: "x.docx"
  sha256: "abc"
  imported_at: "2026-08-07"
  pandoc: "3.9"
cut_depth: 2
detection: { tier: 1, note: "test" }
depth_map: {1: 1, 3: 2}
nodes:
  - { id: BRD-0000, order: 0, depth: 0, word_level: 0, kind: root, title: "(phần đầu tài liệu)", path: "_index.md", parent: null, chars: 12 }
  - { id: BRD-0001, order: 1, depth: 1, word_level: 1, kind: folder, title: "Nhóm A, phần \\"chính\\"", inline: true, dir: "01-nhom-a/", parent: null, chars: 10 }
  - { id: BRD-0002, order: 2, depth: 2, word_level: 3, kind: leaf, title: "Màn danh sách", path: "01-nhom-a/01-man-danh-sach.md", parent: BRD-0001, chars: 320 }
  - { id: BRD-0003, order: 3, depth: 2, word_level: 3, kind: leaf, title: "Thuật ngữ", path: "01-nhom-a/02-thuat-ngu.md", parent: BRD-0001, chars: 40 }
"""

ROOT_MD = """---
brd_id: BRD-0000
title: "(phần đầu tài liệu)"
breadcrumb: []
---

Trang bìa tài liệu.
"""

MAN_MD = """---
brd_id: BRD-0002
title: "Màn danh sách"
breadcrumb: ["Nhóm A, phần \\"chính\\""]
---

# Màn danh sách

Màn hiển thị danh sách hợp đồng, cho phép Thêm, Sửa, Xoá và Tìm kiếm.
Người dùng có quyền Quản trị mới được Duyệt.

## Bộ lọc

| Trường | Kiểu | Bắt buộc |
|--------|------|----------|
| Mã hợp đồng | text | có |
| Ngày ký | date | không |

<img src="../media/image1.png" />

## Quy tắc

Chỉ vai trò Quản trị được Xoá.
"""

TERM_MD = """---
brd_id: BRD-0003
title: "Thuật ngữ"
breadcrumb: ["Nhóm A, phần \\"chính\\""]
---

# Thuật ngữ

BRD: Business Requirement Document.
"""


@pytest.fixture
def brd(tmp_path):
    """Cây BRD nhỏ, đúng định dạng brd-import sinh ra."""
    root = tmp_path / "docs" / "brd"
    (root / "01-nhom-a").mkdir(parents=True)
    (root / "brd.manifest.yml").write_text(MANIFEST, encoding="utf-8")
    (root / "_index.md").write_text(ROOT_MD, encoding="utf-8")
    (root / "01-nhom-a" / "01-man-danh-sach.md").write_text(MAN_MD, encoding="utf-8")
    (root / "01-nhom-a" / "02-thuat-ngu.md").write_text(TERM_MD, encoding="utf-8")
    return root


def test_parse_manifest_doc_du_node(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert [n["id"] for n in nodes] == ["BRD-0000", "BRD-0001", "BRD-0002", "BRD-0003"]
    assert nodes[0]["kind"] == "root"
    assert nodes[0]["parent"] is None
    assert nodes[2]["parent"] == "BRD-0001"
    assert nodes[2]["chars"] == 320


def test_parse_manifest_title_co_dau_phay_va_ngoac_kep_escape(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert nodes[1]["title"] == 'Nhóm A, phần "chính"'


def test_parse_manifest_node_inline_khong_co_path(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert nodes[1]["inline"] is True
    assert nodes[1]["path"] is None
    assert nodes[1]["dir"] == "01-nhom-a/"
    assert node_loc(nodes[1]) == "01-nhom-a/"
    assert node_loc(nodes[2]) == "01-nhom-a/01-man-danh-sach.md"


def test_breadcrumbs_theo_chuoi_cha(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    crumbs = breadcrumbs(nodes)
    assert crumbs["BRD-0002"] == ['Nhóm A, phần "chính"']
    assert crumbs["BRD-0001"] == []
```

- [ ] **Step 2: Chạy test để chắc chắn nó thất bại**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'brd_roadmap'`

- [ ] **Step 3: Hiện thực tối thiểu**

Tạo `speckit-extension/scripts/brd_roadmap.py`:

```python
#!/usr/bin/env python3
"""brd-roadmap — trích outline từ cây BRD markdown và gác cổng docs/roadmap.md.

    outline <brd-dir> [--out <json>] [--head N]
    verify <roadmap.md> --brd <dir> [--decisions <json>]
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

NODE_RE = re.compile(r"^\s*-\s*\{(.*)\}\s*$")


def _die(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def _scan_flow(body):
    """Tách các cặp `k: v` của một flow mapping một dòng, tôn trọng chuỗi có escape.

    Không dùng được `split(",")`: `title` có thể chứa dấu phẩy và `\\"` bên trong.
    """
    out, i, n = {}, 0, len(body)
    while i < n:
        while i < n and body[i] in " ,":
            i += 1
        j = body.find(":", i)
        if j < 0:
            break
        key = body[i:j].strip()
        i = j + 1
        while i < n and body[i] == " ":
            i += 1
        if i < n and body[i] == '"':
            i += 1
            buf = []
            while i < n:
                c = body[i]
                if c == "\\" and i + 1 < n:
                    buf.append(body[i + 1])
                    i += 2
                    continue
                if c == '"':
                    i += 1
                    break
                buf.append(c)
                i += 1
            val = "".join(buf)
        else:
            k = i
            while i < n and body[i] != ",":
                i += 1
            val = body[k:i].strip()
        out[key] = val
    return out


def parse_manifest(path):
    """Đọc `brd.manifest.yml` -> danh sách node theo thứ tự tài liệu."""
    path = Path(path)
    if not path.is_file():
        _die(f"Không thấy {path} — thư mục này không phải cây BRD do brd-import sinh ra.")
    nodes = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = NODE_RE.match(line)
        if not m:
            continue
        f = _scan_flow(m.group(1))
        parent = f.get("parent")
        nodes.append({
            "id": f["id"],
            "order": int(f["order"]),
            "depth": int(f["depth"]),
            "kind": f["kind"],
            "title": f["title"],
            "path": f.get("path"),
            "dir": f.get("dir"),
            "inline": f.get("inline") == "true",
            "parent": None if parent in (None, "null", "") else parent,
            "chars": int(f["chars"]),
        })
    if not nodes:
        _die(f"{path} không có node nào — manifest hỏng hoặc rỗng.")
    return nodes


def node_loc(node):
    """Vị trí của node trong cây: đường dẫn file, hoặc thư mục nếu node inline."""
    return node["path"] or node["dir"] or ""


def breadcrumbs(nodes):
    by_id = {n["id"]: n for n in nodes}
    out = {}
    for n in nodes:
        crumbs, cur = [], n["parent"]
        while cur and cur in by_id:
            crumbs.append(by_id[cur]["title"])
            cur = by_id[cur]["parent"]
        out[n["id"]] = list(reversed(crumbs))
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Trích outline cây BRD và gác cổng docs/roadmap.md."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("outline", help="Trích outline gọn từ cây BRD markdown")
    o.add_argument("brd_dir")
    o.add_argument("--out", default=".specify/tmp/roadmap-brd/outline.json")
    o.add_argument("--head", type=int, default=15)
    o.set_defaults(func=cmd_outline)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

`cmd_outline` chưa tồn tại — Task 2 viết. Task 1 chỉ cần import module chạy được, nên tạm thêm ngay trên `main()`:

```python
def cmd_outline(args):
    raise NotImplementedError
```

- [ ] **Step 4: Chạy test để chắc chắn nó qua**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: PASS — 4 test qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd_roadmap.py speckit-extension/scripts/tests/test_brd_roadmap.py
git commit -m "feat(dft-speckit): parser brd.manifest.yml cho brd_roadmap"
```

---

### Task 2: `outline` — headings, head, signals

**Files:**
- Modify: `speckit-extension/scripts/brd_roadmap.py`
- Test: `speckit-extension/scripts/tests/test_brd_roadmap.py`

**Interfaces:**
- Consumes: `parse_manifest`, `breadcrumbs`, `node_loc` (Task 1)
- Produces:
  - `strip_frontmatter(text: str) -> str`
  - `headings_of(text: str) -> list[dict]` — `{"level": int, "text": str}`, bỏ qua khối code
  - `head_lines(text: str, n: int) -> list[str]` — `n` dòng đầu phi-rỗng, không phải heading
  - `signals_of(text: str) -> dict` — khoá `tables, table_rows, images, action_words, permission_words, field_table, words`

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_brd_roadmap.py`:

```python
from brd_roadmap import head_lines, headings_of, signals_of, strip_frontmatter


def test_strip_frontmatter_go_dung_khoi_dau(brd):
    text = (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    body = strip_frontmatter(text)
    assert not body.startswith("---")
    assert body.lstrip().startswith("# Màn danh sách")


def test_headings_of_lay_du_cap(brd):
    text = strip_frontmatter(
        (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    )
    assert headings_of(text) == [
        {"level": 1, "text": "Màn danh sách"},
        {"level": 2, "text": "Bộ lọc"},
        {"level": 2, "text": "Quy tắc"},
    ]


def test_headings_of_bo_qua_heading_trong_khoi_code():
    text = "# Thật\n\n```\n# Giả\n```\n\n## Thật 2\n"
    assert headings_of(text) == [
        {"level": 1, "text": "Thật"},
        {"level": 2, "text": "Thật 2"},
    ]


def test_head_lines_bo_dong_trang_va_heading(brd):
    text = strip_frontmatter(
        (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    )
    head = head_lines(text, 2)
    assert head == [
        "Màn hiển thị danh sách hợp đồng, cho phép Thêm, Sửa, Xoá và Tìm kiếm.",
        "Người dùng có quyền Quản trị mới được Duyệt.",
    ]


def test_signals_of_dem_dung(brd):
    text = strip_frontmatter(
        (brd / "01-nhom-a" / "01-man-danh-sach.md").read_text(encoding="utf-8")
    )
    sig = signals_of(text)
    assert sig["tables"] == 1
    assert sig["table_rows"] == 4
    assert sig["images"] == 1
    assert sig["field_table"] is True
    assert sig["permission_words"] >= 2      # "quyền" x2 + "vai trò" x1
    assert sig["action_words"] >= 5          # Thêm/Sửa/Xoá/Tìm kiếm/Duyệt/Xoá


def test_signals_of_file_khong_co_gi(brd):
    text = strip_frontmatter((brd / "01-nhom-a" / "02-thuat-ngu.md").read_text(encoding="utf-8"))
    sig = signals_of(text)
    assert sig["tables"] == 0
    assert sig["images"] == 0
    assert sig["field_table"] is False
```

- [ ] **Step 2: Chạy test để chắc chắn nó thất bại**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: FAIL — `ImportError: cannot import name 'head_lines' from 'brd_roadmap'`

- [ ] **Step 3: Hiện thực tối thiểu**

Thêm vào `brd_roadmap.py`, ngay dưới `breadcrumbs`:

```python
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
PIPE_SEP_RE = re.compile(r"^\s*\|[\s|:-]*-{2,}[\s|:-]*\|?\s*$")
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(")

ACTION_WORDS = ("thêm", "sửa", "xoá", "xóa", "tìm kiếm", "lưu", "duyệt",
                "xuất", "nhập", "phê duyệt", "cập nhật", "tra cứu")
PERM_WORDS = ("quyền", "vai trò", "phân quyền", "nhóm người dùng")
FIELD_HEADERS = ("| trường", "| tên trường", "| tham số")


def strip_frontmatter(text):
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 3)
    if end < 0:
        return text
    return text[end + len("\n---\n"):]


def _iter_outside_code(text):
    in_code = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        yield line


def headings_of(text):
    out = []
    for line in _iter_outside_code(text):
        m = HEADING_RE.match(line)
        if m:
            out.append({"level": len(m.group(1)), "text": m.group(2)})
    return out


def head_lines(text, n):
    """`n` dòng đầu phi-rỗng, bỏ heading — đủ để nhận ra mục nói về cái gì."""
    out = []
    for line in _iter_outside_code(text):
        s = line.strip()
        if not s or HEADING_RE.match(line):
            continue
        out.append(s)
        if len(out) >= n:
            break
    return out


def signals_of(text):
    """Đếm cơ học các dấu hiệu 'đây là một màn' — LLM đọc số, không đọc toàn văn."""
    low = text.lower()
    lines = text.split("\n")
    return {
        "tables": low.count("<table") + sum(1 for l in lines if PIPE_SEP_RE.match(l)),
        "table_rows": low.count("<tr") + sum(1 for l in lines if l.lstrip().startswith("|")),
        "images": low.count("<img") + len(MD_IMG_RE.findall(text)),
        "action_words": sum(low.count(w) for w in ACTION_WORDS),
        "permission_words": sum(low.count(w) for w in PERM_WORDS),
        "field_table": any(h in low for h in FIELD_HEADERS),
        "words": len(low.split()),
    }
```

- [ ] **Step 4: Chạy test để chắc chắn nó qua**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: PASS — 10 test qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd_roadmap.py speckit-extension/scripts/tests/test_brd_roadmap.py
git commit -m "feat(dft-speckit): trích heading/head/signals từ file BRD"
```

---

### Task 3: `outline` — lệnh con hoàn chỉnh + hai danh sách lệch

**Files:**
- Modify: `speckit-extension/scripts/brd_roadmap.py`
- Test: `speckit-extension/scripts/tests/test_brd_roadmap.py`

**Interfaces:**
- Consumes: mọi thứ từ Task 1–2
- Produces:
  - `tree_diff(brd_dir: Path, nodes: list[dict]) -> tuple[list[str], list[str]]` — `(files_without_node, nodes_without_file)`
  - `build_outline(brd_dir: Path, head: int) -> dict` — JSON gốc có khoá `brd_dir, node_count, files_without_node, nodes_without_file, nodes`
  - `cmd_outline(args)` — ghi `args.out` và in JSON ra stdout

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_brd_roadmap.py`:

```python
from brd_roadmap import build_outline, tree_diff


def test_tree_diff_bao_file_thua_va_node_mat(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    (brd / "01-nhom-a" / "03-ba-them-tay.md").write_text("# BA thêm tay\n", encoding="utf-8")
    (brd / "01-nhom-a" / "02-thuat-ngu.md").unlink()
    extra, missing = tree_diff(brd, nodes)
    assert extra == ["01-nhom-a/03-ba-them-tay.md"]
    assert missing == ["01-nhom-a/02-thuat-ngu.md"]


def test_tree_diff_cay_nguyen_ven_thi_rong(brd):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    assert tree_diff(brd, nodes) == ([], [])


def test_build_outline_moi_node_co_du_khoa(brd):
    out = build_outline(brd, head=15)
    assert out["node_count"] == 4
    man = next(n for n in out["nodes"] if n["id"] == "BRD-0002")
    assert man["breadcrumb"] == ['Nhóm A, phần "chính"']
    assert man["path"] == "01-nhom-a/01-man-danh-sach.md"
    assert {"level": 2, "text": "Bộ lọc"} in man["headings"]
    assert man["head"]
    assert man["signals"]["images"] == 1


def test_build_outline_node_inline_khong_doc_file(brd):
    out = build_outline(brd, head=15)
    grp = next(n for n in out["nodes"] if n["id"] == "BRD-0001")
    assert grp["inline"] is True
    assert grp["dir"] == "01-nhom-a/"
    assert grp["headings"] == []
    assert grp["signals"] is None


def test_cli_outline_ghi_file_va_in_stdout(brd, tmp_path):
    dest = tmp_path / "out" / "outline.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(brd), "--out", str(dest)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    assert dest.is_file()
    assert json.loads(proc.stdout)["node_count"] == 4


def test_cli_outline_thu_muc_khong_co_manifest_thi_chet(tmp_path):
    (tmp_path / "trong").mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "outline", str(tmp_path / "trong")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert "brd.manifest.yml" in proc.stderr
```

- [ ] **Step 2: Chạy test để chắc chắn nó thất bại**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: FAIL — `ImportError: cannot import name 'build_outline' from 'brd_roadmap'`

- [ ] **Step 3: Hiện thực tối thiểu**

Thay hàm `cmd_outline` tạm ở Task 1 bằng:

```python
def tree_diff(brd_dir, nodes):
    """(file .md có trên đĩa mà manifest không khai, node khai mà file đã mất).

    BA sửa tay `docs/brd/` sau khi import là chuyện thường — hai danh sách này là
    cảnh báo, không chặn, nhưng lệnh phải báo ra.
    """
    brd_dir = Path(brd_dir)
    known = {n["path"] for n in nodes if n["path"]}
    on_disk = {str(p.relative_to(brd_dir)).replace("\\", "/")
               for p in brd_dir.rglob("*.md")}
    missing = sorted(p for p in known if not (brd_dir / p).is_file())
    extra = sorted(on_disk - known)
    return extra, missing


def build_outline(brd_dir, head):
    brd_dir = Path(brd_dir)
    nodes = parse_manifest(brd_dir / "brd.manifest.yml")
    crumbs = breadcrumbs(nodes)
    extra, missing = tree_diff(brd_dir, nodes)

    out_nodes = []
    for n in nodes:
        item = {
            "id": n["id"], "order": n["order"], "depth": n["depth"],
            "kind": n["kind"], "title": n["title"], "breadcrumb": crumbs[n["id"]],
            "path": n["path"], "dir": n["dir"], "inline": n["inline"],
            "parent": n["parent"], "chars": n["chars"],
            "headings": [], "head": [], "signals": None,
        }
        f = brd_dir / n["path"] if n["path"] else None
        if f is not None and f.is_file():
            body = strip_frontmatter(f.read_text(encoding="utf-8"))
            item["headings"] = headings_of(body)
            item["head"] = head_lines(body, head)
            item["signals"] = signals_of(body)
        out_nodes.append(item)

    return {
        "brd_dir": str(brd_dir).replace("\\", "/"),
        "node_count": len(out_nodes),
        "files_without_node": extra,
        "nodes_without_file": missing,
        "nodes": out_nodes,
    }


def cmd_outline(args):
    brd_dir = Path(args.brd_dir)
    if not brd_dir.is_dir():
        _die(f"Không thấy thư mục BRD: {brd_dir}")
    result = build_outline(brd_dir, args.head)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                   encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False))
```

- [ ] **Step 4: Chạy test để chắc chắn nó qua**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: PASS — 16 test qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd_roadmap.py speckit-extension/scripts/tests/test_brd_roadmap.py
git commit -m "feat(dft-speckit): lệnh con outline cho brd_roadmap"
```

---

### Task 4: `verify` — parse `roadmap.md`, ID và placeholder

**Files:**
- Modify: `speckit-extension/scripts/brd_roadmap.py`
- Test: `speckit-extension/scripts/tests/test_brd_roadmap.py`

**Interfaces:**
- Consumes: `_die`, `HEADING_RE`, `_iter_outside_code`
- Produces:
  - `parse_roadmap(text: str) -> dict` — `{"rows": {id: {"man","module","wave","deps_raw"}}, "details": {id: {field: value}}, "row_order": [id], "detail_order": [id]}`
  - `check_ids(parsed) -> list[str]` — lỗi ID trùng / bảng tổng ↔ chi tiết lệch
  - `check_placeholders(text: str) -> list[str]` — lỗi placeholder còn sót

Quy ước dữ liệu: `Wave` và `Phụ thuộc` lấy từ **bảng tổng**; `Nguồn` lấy từ **khối chi tiết**.

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_brd_roadmap.py`:

```python
from brd_roadmap import check_ids, check_placeholders, parse_roadmap

ROADMAP_OK = """# Roadmap Build — Dự án X

**Mục tiêu**: thứ tự build/hoàn thiện từng màn/chức năng.
**Cập nhật**: 2026-08-07
**Trạng thái item**: `chưa` (mặc định) / `đang` / `xong`.

## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
| RM-001 | Đăng nhập | auth | 0 | N/A | chưa |
| RM-002 | Màn danh sách | hop-dong | 1 | RM-001 | chưa |

## Chi tiết

### RM-001 — Đăng nhập (auth, Wave 0)

- **Mô tả**: đăng nhập hệ thống
- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md#Quy tắc
- **Thực thể/CRUD**: User
- **Phụ thuộc**: N/A
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống)

### RM-002 — Màn danh sách (hop-dong, Wave 1)

- **Mô tả**: danh sách hợp đồng
- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md
- **Thực thể/CRUD**: HopDong
- **Phụ thuộc**: RM-001
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống)
"""


def test_parse_roadmap_doc_bang_tong_va_chi_tiet():
    p = parse_roadmap(ROADMAP_OK)
    assert p["row_order"] == ["RM-001", "RM-002"]
    assert p["rows"]["RM-002"]["module"] == "hop-dong"
    assert p["rows"]["RM-002"]["wave"] == "1"
    assert p["rows"]["RM-002"]["deps_raw"] == "RM-001"
    assert p["details"]["RM-002"]["Nguồn"] == "docs/brd/01-nhom-a/01-man-danh-sach.md"


def test_check_ids_khop_hai_chieu_thi_khong_loi():
    assert check_ids(parse_roadmap(ROADMAP_OK)) == []


def test_check_ids_bat_id_trung():
    text = ROADMAP_OK.replace("| RM-002 | Màn danh sách", "| RM-001 | Màn danh sách")
    errs = check_ids(parse_roadmap(text))
    assert any("trùng" in e for e in errs)


def test_check_ids_bat_item_thieu_khoi_chi_tiet():
    text = ROADMAP_OK.replace("### RM-002 — Màn danh sách (hop-dong, Wave 1)",
                              "### RM-009 — Màn danh sách (hop-dong, Wave 1)")
    errs = check_ids(parse_roadmap(text))
    assert any("RM-002" in e and "khối chi tiết" in e for e in errs)
    assert any("RM-009" in e and "bảng tổng" in e for e in errs)


def test_check_placeholders_sach_thi_khong_loi():
    assert check_placeholders(ROADMAP_OK) == []


def test_check_placeholders_bat_date_va_ngoac_vuong():
    text = ROADMAP_OK.replace("2026-08-07", "[DATE]").replace("auth | 0", "[module] | 0")
    errs = check_placeholders(text)
    assert any("[DATE]" in e for e in errs)
    assert any("[module]" in e for e in errs)


def test_check_placeholders_khong_bat_link_markdown():
    assert check_placeholders("xem [tài liệu](docs/a.md)\n") == []
```

- [ ] **Step 2: Chạy test để chắc chắn nó thất bại**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: FAIL — `ImportError: cannot import name 'check_ids' from 'brd_roadmap'`

- [ ] **Step 3: Hiện thực tối thiểu**

Thêm vào `brd_roadmap.py`:

```python
ROW_RE = re.compile(r"^\|\s*(RM-\d{3})\s*\|(.*)$")
DETAIL_RE = re.compile(r"^###\s+(RM-\d{3})\b")
FIELD_RE = re.compile(r"^\s*-\s*\*\*(.+?)\*\*\s*:\s*(.*)$")
# Placeholder = span trong ngoặc vuông KHÔNG phải link markdown (`](`) và không
# phải checkbox. Nội dung đã điền thật gần như không bao giờ còn ngoặc vuông trần.
BRACKET_RE = re.compile(r"\[[^\]\n]{1,120}\](?!\()")


def parse_roadmap(text):
    rows, row_order, details, detail_order = {}, [], {}, []
    cur = None
    for line in text.split("\n"):
        m = ROW_RE.match(line)
        if m:
            rid = m.group(1)
            cells = [c.strip() for c in m.group(2).split("|")]
            cells += [""] * (5 - len(cells))
            rows.setdefault(rid, {
                "man": cells[0], "module": cells[1], "wave": cells[2],
                "deps_raw": cells[3], "trang_thai": cells[4],
            })
            row_order.append(rid)
            continue
        d = DETAIL_RE.match(line)
        if d:
            cur = d.group(1)
            details.setdefault(cur, {})
            detail_order.append(cur)
            continue
        if cur:
            f = FIELD_RE.match(line)
            if f:
                details[cur].setdefault(f.group(1).strip(), f.group(2).strip())
    return {"rows": rows, "row_order": row_order,
            "details": details, "detail_order": detail_order}


def _dups(seq):
    seen, dup = set(), []
    for x in seq:
        if x in seen and x not in dup:
            dup.append(x)
        seen.add(x)
    return dup


def check_ids(parsed):
    errs = []
    for rid in _dups(parsed["row_order"]):
        errs.append(f"ID {rid} trùng trong bảng tổng.")
    for rid in _dups(parsed["detail_order"]):
        errs.append(f"ID {rid} trùng ở khối chi tiết.")
    for rid in parsed["row_order"]:
        if rid not in parsed["details"]:
            errs.append(f"{rid} có trong bảng tổng nhưng thiếu khối chi tiết.")
    for rid in parsed["detail_order"]:
        if rid not in parsed["rows"]:
            errs.append(f"{rid} có khối chi tiết nhưng thiếu dòng trong bảng tổng.")
    return sorted(set(errs))


def check_placeholders(text):
    errs = []
    for i, line in enumerate(_iter_outside_code(text), start=1):
        if line.lstrip().startswith("<!--"):
            continue
        for hit in BRACKET_RE.findall(line):
            errs.append(f"Dòng {i}: còn placeholder chưa điền {hit}")
    return errs
```

- [ ] **Step 4: Chạy test để chắc chắn nó qua**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: PASS — 23 test qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd_roadmap.py speckit-extension/scripts/tests/test_brd_roadmap.py
git commit -m "feat(dft-speckit): parse roadmap.md + kiểm ID/placeholder"
```

---

### Task 5: `verify` — phủ 1-1 và `**Nguồn**`

**Files:**
- Modify: `speckit-extension/scripts/brd_roadmap.py`
- Test: `speckit-extension/scripts/tests/test_brd_roadmap.py`

**Interfaces:**
- Consumes: `parse_manifest`, `node_loc`, `headings_of`, `strip_frontmatter`, `parse_roadmap`
- Produces:
  - `slugify_anchor(text: str) -> str`
  - `norm_source(raw: str, brd_rel: str) -> tuple[str|None, str|None]` — `(đường dẫn tương đối brd_dir, anchor)`; `(None, None)` khi giá trị không trỏ vào cây BRD
  - `check_coverage(parsed, nodes, brd_dir, brd_rel, excluded) -> tuple[list[str], list[str]]` — `(errors, warnings)`

Quy ước: node `kind == "root"` (`BRD-0000`, phần đầu tài liệu) **không** tính vào phủ.

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_brd_roadmap.py`:

```python
from brd_roadmap import check_coverage, norm_source, slugify_anchor


def _cover(brd, roadmap_text, excluded=()):
    nodes = parse_manifest(brd / "brd.manifest.yml")
    return check_coverage(parse_roadmap(roadmap_text), nodes, brd,
                          "docs/brd", list(excluded))


ROADMAP_PHU = """## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
| RM-001 | Nhóm A | nhom-a | 0 | N/A | chưa |
| RM-002 | Màn danh sách | hop-dong | 1 | RM-001 | chưa |

## Chi tiết

### RM-001 — Nhóm A (nhom-a, Wave 0)

- **Nguồn**: docs/brd/01-nhom-a/

### RM-002 — Màn danh sách (hop-dong, Wave 1)

- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md
"""


def test_slugify_anchor_giu_dau_tieng_viet():
    assert slugify_anchor("Bộ lọc") == "bộ-lọc"
    assert slugify_anchor("Quy tắc & điều kiện") == "quy-tắc-điều-kiện"


def test_norm_source_cat_tien_to_thu_muc_brd_va_anchor():
    assert norm_source("docs/brd/01-a/02-b.md#Bộ lọc", "docs/brd") == ("01-a/02-b.md", "Bộ lọc")
    assert norm_source("01-a/02-b.md", "docs/brd") == ("01-a/02-b.md", None)
    assert norm_source("`docs/brd/01-a/`", "docs/brd") == ("01-a/", None)
    assert norm_source("[xem](docs/brd/01-a/02-b.md)", "docs/brd") == ("01-a/02-b.md", None)


def test_norm_source_ngoai_cay_brd_thi_tra_none():
    assert norm_source("src/app/login.ts", "docs/brd") == (None, None)
    assert norm_source("N/A", "docs/brd") == (None, None)


def test_check_coverage_thieu_node_thi_loi(brd):
    errs, _ = _cover(brd, ROADMAP_PHU)
    assert any("BRD-0003" in e and "Thuật ngữ" in e for e in errs)
    assert not any("BRD-0002" in e for e in errs)
    assert not any("BRD-0000" in e for e in errs)      # node gốc không tính phủ


def test_check_coverage_node_bi_loai_co_ly_do_thi_qua(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển, không phải màn"}])
    assert errs == []


def test_check_coverage_ly_do_rong_thi_loi(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "   "}])
    assert any("BRD-0003" in e and "lý do" in e for e in errs)


def test_check_coverage_node_id_loai_khong_co_that_thi_loi(brd):
    errs, _ = _cover(brd, ROADMAP_PHU,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"},
                      {"node_id": "BRD-9999", "title": "Ma", "reason": "ok"}])
    assert any("BRD-9999" in e for e in errs)


def test_check_coverage_nguon_tro_file_khong_ton_tai(brd):
    text = ROADMAP_PHU.replace("01-man-danh-sach.md", "99-khong-co.md")
    errs, _ = _cover(brd, text)
    assert any("99-khong-co.md" in e for e in errs)


def test_check_coverage_anchor_khop_text_hoac_slug(brd):
    ok_text = ROADMAP_PHU.replace("01-man-danh-sach.md\n", "01-man-danh-sach.md#Bộ lọc\n")
    errs, _ = _cover(brd, ok_text,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert errs == []
    slug_text = ROADMAP_PHU.replace("01-man-danh-sach.md\n", "01-man-danh-sach.md#bộ-lọc\n")
    errs, _ = _cover(brd, slug_text,
                     [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert errs == []


def test_check_coverage_anchor_khong_co_thi_loi(brd):
    text = ROADMAP_PHU.replace("01-man-danh-sach.md\n", "01-man-danh-sach.md#Không có mục này\n")
    errs, _ = _cover(brd, text)
    assert any("Không có mục này" in e for e in errs)


def test_check_coverage_item_khong_co_nguon_thi_canh_bao(brd):
    text = ROADMAP_PHU.replace("- **Nguồn**: docs/brd/01-nhom-a/\n", "")
    _, warns = _cover(brd, text, [{"node_id": "BRD-0001", "title": "Nhóm A", "reason": "ok"},
                                  {"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "ok"}])
    assert any("RM-001" in w and "Nguồn" in w for w in warns)


def test_check_coverage_node_lon_map_mot_item_thi_canh_bao(brd):
    manifest = (brd / "brd.manifest.yml").read_text(encoding="utf-8")
    (brd / "brd.manifest.yml").write_text(manifest.replace("chars: 320", "chars: 50000"),
                                          encoding="utf-8")
    _, warns = _cover(brd, ROADMAP_PHU, [{"node_id": "BRD-0003", "title": "T", "reason": "ok"}])
    assert any("BRD-0002" in w and "tách" in w for w in warns)
```

- [ ] **Step 2: Chạy test để chắc chắn nó thất bại**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: FAIL — `ImportError: cannot import name 'check_coverage' from 'brd_roadmap'`

- [ ] **Step 3: Hiện thực tối thiểu**

Thêm vào `brd_roadmap.py`:

```python
LINK_RE = re.compile(r"^\[[^\]]*\]\((.+?)\)$")
BIG_NODE_CHARS = 40_000


def slugify_anchor(text):
    """Slug kiểu GFM: thường hoá, bỏ ký tự không phải chữ/số, khoảng trắng -> gạch."""
    s = text.strip().lower()
    s = "".join(ch for ch in s if ch.isalnum() or ch in " -_")
    return re.sub(r"\s+", "-", s.strip())


def norm_source(raw, brd_rel):
    """Giá trị `**Nguồn**` -> (đường dẫn tương đối brd_dir, anchor).

    Trả (None, None) khi giá trị không trỏ vào cây BRD (đường dẫn code, `N/A`).
    """
    v = (raw or "").strip().strip("`").strip()
    m = LINK_RE.match(v)
    if m:
        v = m.group(1).strip()
    v = v.replace("\\", "/")
    anchor = None
    if "#" in v:
        v, anchor = v.split("#", 1)
        anchor = anchor.strip() or None
    v = v.strip()
    prefix = brd_rel.replace("\\", "/").rstrip("/") + "/"
    if v.startswith(prefix):
        return v[len(prefix):], anchor
    if v.endswith(".md") or v.endswith("/"):
        return v, anchor
    return None, None


def check_coverage(parsed, nodes, brd_dir, brd_rel, excluded):
    """Mọi node BRD phải hoặc được một item trỏ tới, hoặc nằm trong `excluded` kèm lý do."""
    brd_dir = Path(brd_dir)
    errs, warns = [], []

    by_loc, by_id = {}, {}
    for n in nodes:
        by_id[n["id"]] = n
        if n["kind"] != "root":
            by_loc[node_loc(n).rstrip("/")] = n["id"]

    covered = {}
    for rid in parsed["row_order"]:
        raw = parsed["details"].get(rid, {}).get("Nguồn")
        if not raw:
            warns.append(f"{rid} không có trường **Nguồn** — không truy vết được về BRD.")
            continue
        rel, anchor = norm_source(raw, brd_rel)
        if rel is None:
            continue
        key = rel.rstrip("/")
        if key not in by_loc:
            errs.append(f"{rid}: **Nguồn** trỏ tới {raw} — không có node BRD nào ở vị trí đó.")
            continue
        nid = by_loc[key]
        covered.setdefault(nid, []).append(rid)
        if anchor:
            f = brd_dir / rel
            if not f.is_file():
                errs.append(f"{rid}: **Nguồn** có anchor nhưng {rel} không phải file.")
                continue
            hs = headings_of(strip_frontmatter(f.read_text(encoding="utf-8")))
            found = any(h["text"].strip().lower() == anchor.lower()
                        or slugify_anchor(h["text"]) == slugify_anchor(anchor)
                        for h in hs)
            if not found:
                errs.append(f"{rid}: anchor #{anchor} không khớp heading nào trong {rel}.")

    ex_ids = set()
    for e in excluded:
        nid = (e or {}).get("node_id", "")
        if nid not in by_id:
            errs.append(f"decisions.json loại node {nid} không có trong manifest.")
            continue
        if not (e.get("reason") or "").strip():
            errs.append(f"decisions.json loại node {nid} nhưng bỏ trống lý do.")
            continue
        ex_ids.add(nid)
        if nid in covered:
            warns.append(f"{nid} vừa bị loại trong decisions.json vừa được "
                         f"{', '.join(covered[nid])} trỏ tới — mâu thuẫn.")

    for n in nodes:
        if n["kind"] == "root" or n["id"] in covered or n["id"] in ex_ids:
            continue
        errs.append(f"Node {n['id']} \"{n['title']}\" ({node_loc(n)}) chưa có item roadmap "
                    f"nào trỏ tới và cũng không nằm trong decisions.json.")

    for nid, rids in covered.items():
        if len(rids) == 1 and by_id[nid]["chars"] > BIG_NODE_CHARS:
            warns.append(f"Node {nid} có {by_id[nid]['chars']} ký tự nhưng chỉ map vào "
                         f"{rids[0]} — nhiều khả năng phải tách.")
    return errs, warns
```

- [ ] **Step 4: Chạy test để chắc chắn nó qua**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: PASS — 35 test qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd_roadmap.py speckit-extension/scripts/tests/test_brd_roadmap.py
git commit -m "feat(dft-speckit): gác cổng phủ 1-1 node BRD ↔ item roadmap"
```

---

### Task 6: `verify` — phụ thuộc, wave, CLI và báo cáo

**Files:**
- Modify: `speckit-extension/scripts/brd_roadmap.py`
- Test: `speckit-extension/scripts/tests/test_brd_roadmap.py`

**Interfaces:**
- Consumes: `check_ids`, `check_placeholders`, `check_coverage`, `parse_roadmap`, `parse_manifest`
- Produces:
  - `check_deps(parsed) -> list[str]` — ID phụ thuộc không tồn tại, chu trình, wave nghịch
  - `cmd_verify(args)` — in báo cáo JSON `{ok, items, errors, warnings}` ra stdout, exit 1 khi có lỗi

- [ ] **Step 1: Viết test thất bại**

Thêm vào `test_brd_roadmap.py`:

```python
from brd_roadmap import check_deps

DEPS_HEAD = """## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
"""

DEPS_TAIL = """
## Chi tiết

### RM-001 — A (m, Wave 0)

- **Nguồn**: docs/brd/01-nhom-a/

### RM-002 — B (m, Wave 1)

- **Nguồn**: docs/brd/01-nhom-a/01-man-danh-sach.md
"""


def _deps(rows):
    return check_deps(parse_roadmap(DEPS_HEAD + rows + DEPS_TAIL))


def test_check_deps_hop_le_thi_khong_loi():
    assert _deps("| RM-001 | A | m | 0 | N/A | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n") == []


def test_check_deps_bat_id_khong_ton_tai():
    errs = _deps("| RM-001 | A | m | 0 | RM-777 | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n")
    assert any("RM-777" in e for e in errs)


def test_check_deps_bat_chu_trinh():
    errs = _deps("| RM-001 | A | m | 0 | RM-002 | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n")
    assert any("chu trình" in e for e in errs)


def test_check_deps_bat_wave_nghich():
    errs = _deps("| RM-001 | A | m | 0 | RM-002 | chưa |\n"
                 "| RM-002 | B | m | 1 | N/A | chưa |\n")
    assert any("Wave" in e and "RM-001" in e for e in errs)


def test_check_deps_bat_wave_khong_phai_so():
    errs = _deps("| RM-001 | A | m | sau | N/A | chưa |\n"
                 "| RM-002 | B | m | 1 | RM-001 | chưa |\n")
    assert any("Wave" in e and "số" in e for e in errs)


def _run_verify(brd, roadmap_text, tmp_path, excluded=()):
    rm = tmp_path / "roadmap.md"
    rm.write_text(roadmap_text, encoding="utf-8")
    dec = tmp_path / "decisions.json"
    dec.write_text(json.dumps({"brd_dir": "docs/brd", "excluded": list(excluded)},
                              ensure_ascii=False), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm),
         "--brd", str(brd), "--brd-rel", "docs/brd", "--decisions", str(dec)],
        capture_output=True, text=True, encoding="utf-8",
    )


def test_cli_verify_happy_path_exit_0(brd, tmp_path):
    proc = _run_verify(brd, ROADMAP_PHU, tmp_path,
                       [{"node_id": "BRD-0003", "title": "Thuật ngữ", "reason": "từ điển"}])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    rep = json.loads(proc.stdout)
    assert rep["ok"] is True
    assert rep["errors"] == []
    assert rep["items"] == 2


def test_cli_verify_thieu_phu_thi_exit_1(brd, tmp_path):
    proc = _run_verify(brd, ROADMAP_PHU, tmp_path)
    assert proc.returncode == 1
    rep = json.loads(proc.stdout)
    assert rep["ok"] is False
    assert any("BRD-0003" in e for e in rep["errors"])


def test_cli_verify_thieu_decisions_van_chay_va_canh_bao(brd, tmp_path):
    rm = tmp_path / "roadmap.md"
    rm.write_text(ROADMAP_PHU, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "verify", str(rm), "--brd", str(brd),
         "--brd-rel", "docs/brd", "--decisions", str(tmp_path / "khong-co.json")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 1
    rep = json.loads(proc.stdout)
    assert any("decisions" in w for w in rep["warnings"])
```

- [ ] **Step 2: Chạy test để chắc chắn nó thất bại**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: FAIL — `ImportError: cannot import name 'check_deps' from 'brd_roadmap'`

- [ ] **Step 3: Hiện thực tối thiểu**

Thêm vào `brd_roadmap.py`:

```python
RM_RE = re.compile(r"RM-\d{3}")


def check_deps(parsed):
    errs = []
    waves, deps = {}, {}
    for rid, row in parsed["rows"].items():
        raw = (row["wave"] or "").strip()
        try:
            waves[rid] = int(raw)
        except ValueError:
            errs.append(f"{rid}: Wave \"{raw}\" không phải số.")
        deps[rid] = [d for d in RM_RE.findall(row["deps_raw"] or "") if d != rid]

    for rid, ds in deps.items():
        for d in ds:
            if d not in parsed["rows"]:
                errs.append(f"{rid} phụ thuộc {d} nhưng không có item nào mang ID đó.")
            elif rid in waves and d in waves and waves[rid] < waves[d]:
                errs.append(f"{rid} ở Wave {waves[rid]} nhưng phụ thuộc {d} ở Wave "
                            f"{waves[d]} — không build được theo thứ tự này.")

    # Chu trình: DFS màu trắng/xám/đen, báo đúng một lần mỗi cạnh quay lui.
    color = {}

    def walk(node, stack):
        color[node] = 1
        for nxt in deps.get(node, []):
            if nxt not in parsed["rows"]:
                continue
            if color.get(nxt) == 1:
                cycle = stack[stack.index(nxt):] + [nxt] if nxt in stack else [node, nxt]
                errs.append("Phụ thuộc có chu trình: " + " -> ".join(cycle))
            elif color.get(nxt, 0) == 0:
                walk(nxt, stack + [nxt])
        color[node] = 2

    for rid in parsed["row_order"]:
        if color.get(rid, 0) == 0:
            walk(rid, [rid])
    return sorted(set(errs))


def cmd_verify(args):
    roadmap = Path(args.roadmap)
    if not roadmap.is_file():
        _die(f"Không thấy file roadmap: {roadmap}")
    brd_dir = Path(args.brd)
    if not brd_dir.is_dir():
        _die(f"Không thấy thư mục BRD: {brd_dir}")

    text = roadmap.read_text(encoding="utf-8")
    parsed = parse_roadmap(text)
    nodes = parse_manifest(brd_dir / "brd.manifest.yml")

    warns, excluded = [], []
    dec = Path(args.decisions)
    if dec.is_file():
        try:
            excluded = json.loads(dec.read_text(encoding="utf-8")).get("excluded", [])
        except json.JSONDecodeError as e:
            _die(f"{dec} hỏng, không đọc được JSON ({e}).")
    else:
        warns.append(f"Không thấy {dec} — coi như chưa loại node nào (decisions rỗng).")

    errs = check_ids(parsed) + check_placeholders(text) + check_deps(parsed)
    cov_errs, cov_warns = check_coverage(parsed, nodes, brd_dir, args.brd_rel, excluded)
    errs += cov_errs
    warns += cov_warns

    report = {
        "ok": not errs,
        "items": len(parsed["rows"]),
        "brd_nodes": sum(1 for n in nodes if n["kind"] != "root"),
        "excluded_nodes": len(excluded),
        "errors": errs,
        "warnings": warns,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errs:
        raise SystemExit(1)
```

Và khai lệnh con trong `main()`, ngay dưới parser `outline`:

```python
    v = sub.add_parser("verify", help="Chấm docs/roadmap.md so với cây BRD")
    v.add_argument("roadmap")
    v.add_argument("--brd", required=True)
    v.add_argument("--brd-rel", default="docs/brd",
                   help="Tiền tố đường dẫn dùng trong trường **Nguồn** của roadmap")
    v.add_argument("--decisions", default=".specify/tmp/roadmap-brd/decisions.json")
    v.set_defaults(func=cmd_verify)
```

- [ ] **Step 4: Chạy test để chắc chắn nó qua**

Run: `cd speckit-extension && python -m pytest scripts/tests/test_brd_roadmap.py -v`
Expected: PASS — 43 test qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd_roadmap.py speckit-extension/scripts/tests/test_brd_roadmap.py
git commit -m "feat(dft-speckit): lệnh con verify — phụ thuộc, wave, báo cáo JSON"
```

---

### Task 7: Thêm trường `**Nguồn**` vào template và lệnh cũ

**Files:**
- Modify: `speckit-extension/templates/roadmap-template.md`
- Modify: `speckit-extension/commands/road-map-from-codebase.md:25-31`

**Interfaces:**
- Produces: khối chi tiết roadmap có trường `**Nguồn**` — khoá mà `check_coverage` (Task 5) đọc.

- [ ] **Step 1: Sửa template**

Trong `speckit-extension/templates/roadmap-template.md`, thêm một dòng ngay dưới `- **Mô tả**:` ở **cả hai** khối `RM-001` và `RM-002`.

Khối `RM-001` thành:

```markdown
### RM-001 — [Tên màn] ([module], Wave 0)

- **Mô tả**: [ngắn gọn chức năng làm gì]
- **Nguồn**: [docs/brd/…md#heading / đường dẫn code / N/A]
- **Thực thể/CRUD**: [entity chính + thao tác]
- **Phụ thuộc**: [ID khác / auth / permission / N/A]
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)
```

Khối `RM-002` thành:

```markdown
### RM-002 — [Tên màn] ([module], Wave 1)

- **Mô tả**: [...]
- **Nguồn**: [docs/brd/…md#heading / đường dẫn code / N/A]
- **Thực thể/CRUD**: [...]
- **Phụ thuộc**: [RM-001 / …]
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống)
```

- [ ] **Step 2: Sửa `road-map-from-codebase.md`**

Trong mục `## 4. Ghi docs/roadmap.md theo khung CỐ ĐỊNH`, thêm một gạch đầu dòng ngay sau gạch đầu dòng **File CHƯA tồn tại**:

```markdown
- **Trường `Nguồn`**: điền đường dẫn file/thư mục code là căn cứ nhận ra màn đó (vd `src/app/hop-dong/list/`). Không xác định được nguồn rõ ràng → ghi `N/A`, KHÔNG bỏ trống và KHÔNG để nguyên placeholder.
```

- [ ] **Step 3: Kiểm bằng mắt là template không còn khác biệt nào khác**

Run: `git diff speckit-extension/templates/roadmap-template.md`
Expected: đúng 2 dòng thêm vào, không dòng nào bị xoá hay đổi.

- [ ] **Step 4: Chạy lại toàn bộ test để chắc chắn không hỏng gì**

Run: `cd speckit-extension && python -m pytest scripts/tests/ -q`
Expected: PASS — mọi test cũ và mới đều qua

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/templates/roadmap-template.md speckit-extension/commands/road-map-from-codebase.md
git commit -m "feat(dft-speckit): thêm trường Nguồn vào roadmap-template"
```

---

### Task 8: Viết `commands/road-map-from-brd.md`

**Files:**
- Create: `speckit-extension/commands/road-map-from-brd.md`

**Interfaces:**
- Consumes: `scripts/brd_roadmap.py` (Task 1–6), `templates/roadmap-template.md` (Task 7)
- Produces: file lệnh mà `extension.yml` sẽ khai ở Task 9.

- [ ] **Step 1: Tạo file lệnh**

Tạo `speckit-extension/commands/road-map-from-brd.md` với đúng nội dung sau:

````markdown
---
description: Lập roadmap build từ cây BRD markdown (docs/brd/) — xếp thứ tự làm từng màn, ghi docs/roadmap.md, gác cổng phủ 1-1 bằng script.
---

# Roadmap build từ BRD

BA đã giao BRD và `/speckit.dft-speckit.brd-import` đã bẻ thành cây markdown `docs/brd/`.
Nhiệm vụ: sinh **`docs/roadmap.md`** xếp **thứ tự làm** từng màn/chức năng. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: **BRD là nguồn chốt danh sách** — mọi node BRD phải hoặc có ít nhất một
item roadmap trỏ tới, hoặc được khai là "không phải màn" kèm lý do. Codebase (nếu có) **chỉ**
dùng để suy thứ tự; nó KHÔNG được thêm hay bớt item, KHÔNG đụng cột `Trạng thái`.

## User Input

`$ARGUMENTS`

Kỳ vọng: **đường dẫn thư mục BRD**, mặc định `docs/brd` khi để trống.
Thư mục không tồn tại, hoặc không có `brd.manifest.yml` → **hỏi lại**, KHÔNG tự đi tìm
thư mục khác trong repo.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/brd_roadmap.py`.
Thư mục làm việc tạm: `.specify/tmp/roadmap-brd/`.

### 0. Chặn đầu vào

`docs/roadmap.md` **đã tồn tại** → **DỪNG NGAY**. In đường dẫn file cũ và nói rõ: lệnh này
KHÔNG merge vào roadmap có sẵn; muốn sinh lại thì người dùng tự đổi tên hoặc xoá file cũ.
Không hỏi "có muốn ghi đè không" — không ghi đè là quyết định đã chốt.

### 1. Trích outline

```bash
python .specify/extensions/dft-speckit/scripts/brd_roadmap.py outline "<thư-mục-brd>" \
  --out .specify/tmp/roadmap-brd/outline.json
```

Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp lỗi. Không tự chữa, không thử lệnh khác.

Đọc `outline.json`. Báo: số node, và **liệt kê đầy đủ** `files_without_node` (file BA thêm tay,
manifest chưa biết) + `nodes_without_file` (file đã bị xoá). Hai danh sách này không chặn nhưng
**không được im lặng bỏ qua** — chúng đổi cách hiểu cây.

### 2. Quét codebase — CHỈ để suy phụ thuộc

Tìm trong codebase: auth/đăng nhập, phân quyền, entity/service dùng chung, module đã dựng.
Ghi nhận cái gì **đã có** để biết cái gì chặn cái gì.

- Không có codebase (repo mới, chỉ có `docs/`) → **bỏ qua bước này và nói thẳng**
  "chưa có codebase, phụ thuộc suy hoàn toàn từ BRD". KHÔNG hỏi vòng vo, KHÔNG dừng.
- **CẤM** dùng codebase để thêm item, bớt item, hay đặt cột `Trạng thái`. Màn có trong code
  mà không có trong BRD → chỉ **báo miệng** cho người dùng biết, KHÔNG ghi vào file.

### 3. Phân loại ứng viên

Mỗi node trong `outline.json` (bỏ qua node `kind: root`) rơi vào đúng một nhóm:

- **là màn** → một item roadmap
- **chứa k màn** → tách thành k item, mỗi item trỏ về cùng file kèm `#heading` khác nhau
- **không phải màn** → ghi vào `decisions.json` kèm **lý do cụ thể** (vd "từ điển thuật ngữ",
  "yêu cầu phi chức năng", "mục giới thiệu phạm vi")

Căn cứ: `signals` (bảng trường, nút thao tác, phân quyền, ảnh), `headings`, `head`, `chars`.
Outline chưa đủ để quyết một node → **`Read` thẳng file đó** theo `path`. CẤM đoán.

Ghi `.specify/tmp/roadmap-brd/decisions.json`:

```json
{
  "brd_dir": "docs/brd",
  "excluded": [
    {"node_id": "BRD-0003", "title": "Thuật ngữ và từ viết tắt", "reason": "từ điển thuật ngữ, không phải màn"}
  ]
}
```

### 4. Interview #1 — chốt phân loại

Trình cho người dùng **ĐẦY ĐỦ, không cắt bớt** hai bảng:

1. **Node bị loại** — mỗi dòng: id, tiêu đề, lý do loại.
2. **Node bị tách** — mỗi dòng: id, tiêu đề, tách thành mấy item, tên từng item.

Rồi hỏi qua **AskUserQuestion**, mỗi lượt gom **1–4 câu độc lập nhau**. Hỏi theo **nhóm quyết
định** (vd "nhóm 5 mục phi chức năng này loại hết hay giữ lại làm item hạ tầng?"), **KHÔNG hỏi
từng node một** — người dùng sửa trực tiếp trên bảng nếu muốn đổi lẻ tẻ.

**Chờ phản hồi thật.** Cấm tự tuyên bố người dùng đã đồng ý. Chưa có phản hồi → DỪNG, không đi
tiếp. Người dùng đổi quyết định → **cập nhật lại `decisions.json`** trước khi sang bước 5.

### 5. Đề xuất wave rồi Interview #2 — chốt thứ tự

Xếp build theo phụ thuộc:

- **Wave 0 — nền tảng**: auth, phân quyền, danh mục/thực thể mà màn khác tham chiếu.
- **Wave sau**: chức năng phụ thuộc wave trước.

Trình bảng đề xuất kèm **lý do thứ tự** (cái gì chặn cái gì), nêu rõ căn cứ đến từ BRD hay từ
codebase. Thứ tự tài liệu BRD chỉ dùng để phá hoà khi hai item không ràng buộc nhau.

Rồi hỏi qua **AskUserQuestion**: **ranh giới wave** và **các cặp thứ tự có ràng buộc phụ thuộc**
là quyết định trọng yếu — phải hỏi. Vị trí tương đối trong cùng một wave đã nằm trong bảng đề
xuất — người dùng chỉnh trực tiếp, không tốn mỗi item một lượt hỏi.

Mỗi câu 2–4 option kèm lý do + trade-off; `(Recommended)` CHỈ khi có căn cứ và nêu căn cứ ngay
trong option. **Thứ tự là quyết định của người dùng** — chờ **phản hồi thật**; chưa có phản hồi
→ DỪNG, **KHÔNG ghi file**.

### 6. Ghi `docs/roadmap.md` theo khung CỐ ĐỊNH

**Dùng khung cố định, KHÔNG tự chế cấu trúc:**

- Lấy khung: chạy `specify preset resolve roadmap-template` để lấy đường dẫn file khung; không
  resolve được → đọc `.specify/extensions/dft-speckit/templates/roadmap-template.md`; vẫn không
  thấy → hỏi.
- Copy đúng cấu trúc khung (bảng tổng + khối chi tiết mỗi item), chỉ **điền** placeholder `[…]`,
  thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **ID ổn định** `RM-001`, `RM-002`, … cấp tăng dần theo thứ tự trong bảng tổng, khớp giữa bảng
  tổng và khối chi tiết.
- **Trường `Nguồn`** của mỗi item: đường dẫn tương đối từ gốc repo tới file BRD nguồn
  (`docs/brd/03-quan-ly/05-danh-sach.md`), thêm `#<tiêu đề mục>` khi nhiều item cùng trỏ về một
  file. Node không có file riêng (`inline`) thì trỏ vào thư mục của nó (`docs/brd/03-quan-ly/`).
- **KHÔNG để sót ngoặc vuông trần** ở bất cứ đâu — `verify` coi mọi `[...]` không phải link
  markdown là placeholder chưa điền và sẽ báo lỗi.

### 7. Chấm bằng script — cổng cuối

```bash
python .specify/extensions/dft-speckit/scripts/brd_roadmap.py verify docs/roadmap.md \
  --brd "<thư-mục-brd>" --brd-rel "<thư-mục-brd>" \
  --decisions .specify/tmp/roadmap-brd/decisions.json
```

- Exit 1 (`ok: false`) → **sửa `docs/roadmap.md` cho đúng rồi chạy lại**. **CẤM báo xong khi
  chưa exit 0.** Cấm "chữa" bằng cách nhét node vào `decisions.json` với lý do bịa — loại một
  node là quyết định phân loại, phải quay lại bước 4 hỏi người dùng.
- Exit 2 → lỗi thao tác (sai đường dẫn, JSON hỏng). In nguyên thông điệp, DỪNG.
- **Liệt kê đầy đủ `warnings`** cho người dùng, kể cả khi `ok: true`.

Kết thúc: báo số item, thứ tự wave, danh sách node đã loại kèm lý do, rồi nhắc
`/speckit.dft-speckit.domain-design <module>` và `/speckit.specify <ID>` để bắt đầu từng mục.

Nhắc dọn dẹp: `.specify/tmp/roadmap-brd/` giữ `outline.json` và `decisions.json` — cần cho lần
chấm lại, xoá được khi đã hài lòng với `docs/roadmap.md`.

## Sai lầm thường gặp

- **Tự chốt phân loại rồi chạy tiếp** → phân loại là quyết định của người dùng, phải hỏi thật.
- **Dùng codebase để thêm/bớt item hoặc đặt `Trạng thái`** → phá nguyên tắc lõi: BRD là nguồn
  chốt danh sách.
- **Loại node mà không ghi lý do vào `decisions.json`** → `verify` fail, và người dùng mất dấu
  vì sao một mục BRD biến mất.
- **Ghi đè `docs/roadmap.md` có sẵn** → xoá `Trạng thái` và `Nợ phát sinh` người khác đã ghi.
- **`verify` fail rồi vẫn báo xong**, hoặc nhét node vào `decisions.json` cho qua cổng → che lỗi.
- **Nuốt `warnings` cho gọn báo cáo** → người dùng mất thông tin cần để quyết.
- **Đọc toàn văn mọi file BRD** → vỡ context rồi bỏ sót mục cuối. Đọc `outline.json` trước,
  chỉ `Read` thêm file nào thật sự chưa quyết được.
````

- [ ] **Step 2: Kiểm file đúng chỗ và có frontmatter**

Run: `head -3 speckit-extension/commands/road-map-from-brd.md`
Expected: dòng 1 là `---`, dòng 2 bắt đầu bằng `description:`

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/commands/road-map-from-brd.md
git commit -m "feat(dft-speckit): command road-map-from-brd"
```

---

### Task 9: Khai trong manifest, bump version, cập nhật README

**Files:**
- Modify: `speckit-extension/extension.yml:6`, `speckit-extension/extension.yml:36-38`
- Modify: `speckit-extension/README.md:13`, `speckit-extension/README.md:33`, `speckit-extension/README.md:53`, `speckit-extension/README.md:57`

**Interfaces:**
- Consumes: `commands/road-map-from-brd.md` (Task 8)
- Produces: extension cài được, lệnh xuất hiện trong danh sách của `specify`.

- [ ] **Step 1: Bump version**

Trong `speckit-extension/extension.yml`, đổi `version: "0.0.6"` thành `version: "0.0.7"`.

- [ ] **Step 2: Khai command**

Thêm vào `provides.commands`, ngay **trước** mục `speckit.dft-speckit.brd-import`:

```yaml
    - name: "speckit.dft-speckit.road-map-from-brd"
      file: "commands/road-map-from-brd.md"
      description: "Lập roadmap build từ cây BRD markdown docs/brd/ (đầu ra của brd-import) — script trích outline gọn từ brd.manifest.yml, LLM phân loại node (là màn / tách k màn / không phải màn kèm lý do), quét codebase CHỈ để suy phụ thuộc, chốt wave qua 2 lượt interview rồi ghi docs/roadmap.md theo roadmap-template. Cổng cuối là `brd_roadmap.py verify`: mọi node BRD phải có item trỏ tới qua trường Nguồn hoặc bị khai loại kèm lý do, cộng kiểm ID/placeholder/chu trình phụ thuộc/wave nghịch — exit ≠ 0 là cấm báo xong. Dừng nếu docs/roadmap.md đã tồn tại (không merge)."
```

- [ ] **Step 3: Cập nhật README**

Thêm dòng vào bảng `## Danh sách command`, ngay dưới dòng `road-map-from-codebase`:

```markdown
| `speckit.dft-speckit.road-map-from-brd` | Lập roadmap build từ cây BRD markdown `docs/brd/` — phủ 1-1 node BRD ↔ item, gác cổng bằng script. |
```

Trong cây thư mục `## Cấu trúc`, thêm dưới dòng `│   ├── road-map-from-codebase.md`:

```
│   ├── road-map-from-brd.md   # roadmap từ cây BRD docs/brd/
```

và dưới dòng `│   ├── brd_import.py          # CLI probe|split cho brd-import`:

```
│   ├── brd_roadmap.py         # CLI outline|verify cho road-map-from-brd
```

Sửa dòng mô tả `roadmap-template.md` thành:

```
│   ├── roadmap-template.md    # khung docs/roadmap.md cho road-map-from-codebase và road-map-from-brd
```

- [ ] **Step 4: Kiểm manifest khai đủ và zip đóng gói được**

Run:
```bash
cd speckit-extension && grep -n "road-map-from-brd" extension.yml README.md && ./build-zip.sh && unzip -l dist/dft-speckit-0.0.7.zip | grep -E "road-map-from-brd|brd_roadmap"
```
Expected: `extension.yml` và `README.md` đều có; zip chứa `dft-speckit/commands/road-map-from-brd.md` và `dft-speckit/scripts/brd_roadmap.py`, KHÔNG chứa `scripts/tests/`.

- [ ] **Step 5: Chạy lại toàn bộ test**

Run: `cd speckit-extension && python -m pytest scripts/tests/ -q`
Expected: PASS — toàn bộ test qua

- [ ] **Step 6: Commit**

```bash
git add speckit-extension/extension.yml speckit-extension/README.md
git commit -m "feat(dft-speckit): khai road-map-from-brd, bump 0.0.7"
```

---

## Sau khi xong

Chạy skill `speckit-addon-reviewer` trên `speckit-extension/` để soát chất lượng prompt của
command mới (đường thoát, hook conflict, chi phí lượt hỏi) trước khi `release.sh`.

Release là thao tác thủ công, **chỉ chạy khi người dùng yêu cầu**:

```bash
speckit-extension/release.sh
```
