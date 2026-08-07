# brd-import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm command `speckit.dft-speckit.brd-import` bẻ một file BRD `.docx` lớn thành cây markdown phản chiếu navigation pane của Word, kiểm chứng không mất một byte nào bằng phép ghép ngược.

**Architecture:** Command `.md` mỏng chỉ chủ trì lượt hỏi và gọi script; toàn bộ việc đọc/cắt/kiểm nằm trong package Python `scripts/brd/`. `pandoc` chuyển `.docx` → một file markdown trung gian; script phân tích heading, hỏi người dùng cấp cắt, cắt thành cây thư mục + `brd.manifest.yml`, rồi **dựng ngược** file trung gian từ chính các mảnh vừa cắt và đòi giống byte-for-byte trước khi cho phép ghi ra đích.

**Tech Stack:** Python 3.11 stdlib thuần (`zipfile`, `re`, `json`, `subprocess`, `unicodedata`, `shutil`, `hashlib`) — không venv, không `pip install`. `pandoc` 3.x là phụ thuộc ngoài duy nhất. Lua filter cho pandoc. `pytest` chỉ dùng lúc phát triển.

Spec: [docs/superpowers/specs/2026-08-07-brd-import-design.md](../specs/2026-08-07-brd-import-design.md)

## Global Constraints

- **Ngôn ngữ**: mọi nội dung hướng người dùng (command `.md`, README, thông báo lỗi của script) viết **tiếng Việt**. Tên hàm/biến/khoá JSON tiếng Anh.
- **Runtime không phụ thuộc**: `scripts/brd_import.py` và `scripts/brd/*.py` chỉ dùng thư viện chuẩn Python. Không venv, không PyYAML — manifest được ghi bằng emitter YAML tự viết, và **không bao giờ cần đọc lại bằng parser**.
- **pandoc**: luôn dùng `-t markdown` (flavor riêng của pandoc, sinh grid table). **Cấm `-t gfm`** — nó sinh 270 bảng HTML thô và làm mất bảng khi ghép ngược ra docx.
- **Hợp đồng lõi**: LLM chỉ quyết ranh giới; **script là thứ duy nhất ghi nội dung file markdown**. Không có bước nào cho model viết lại nội dung tài liệu.
- **Ghi ra đĩa**: luôn ghi vào thư mục tạm rồi `os.replace`/`shutil.move` vào đích. Không có trạng thái nửa vời.
- **Kiểm thử**: `python -m pytest speckit-extension/scripts/tests -q` từ gốc repo. Test đụng BRD thật phải `pytest.skip` khi thiếu file — thư mục `refs/` **không** được commit.
- **BRD thật để test**: `refs/5. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Mobifone.docx`. Số liệu mốc đã đo: 604 heading, cấp Word `[1,3,4,5,6,8]`, 54 node ở cấp 5, 386 file ảnh (387 lượt nhúng), md trung gian 1.510.046 ký tự.
- **Commit**: mỗi task commit riêng, message tiếng Việt theo mẫu repo (`feat(dft-speckit): …`, `test(dft-speckit): …`), kết thúc bằng trailer:
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`
- **Version**: chỉ bump `extension.yml` `0.0.5` → `0.1.0` ở task cuối, không bump rải rác.

---

## File Structure

| File | Trách nhiệm |
|---|---|
| `speckit-extension/scripts/brd_import.py` | CLI mỏng: `probe` / `split`, in JSON ra stdout, mã thoát |
| `speckit-extension/scripts/brd/__init__.py` | rỗng, đánh dấu package |
| `speckit-extension/scripts/brd/naming.py` | `slugify` — bỏ dấu tiếng Việt, đặt tên thư mục/file |
| `speckit-extension/scripts/brd/outline.py` | phân tích heading trong markdown, thống kê theo cấp, luật chọn cấp cắt |
| `speckit-extension/scripts/brd/docx_probe.py` | đọc XML trong `.docx`: xác định bậc dò, bảng style→cấp, ứng viên tiêu đề |
| `speckit-extension/scripts/brd/convert.py` | gọi `pandoc`, dựng `reference.docx` rút gọn |
| `speckit-extension/scripts/brd/splitter.py` | dựng danh sách node, cắt, ghi cây + manifest |
| `speckit-extension/scripts/brd/verify.py` | ghép ngược byte-for-byte + kiểm phụ |
| `speckit-extension/scripts/promote_headings.lua` | Lua filter: nâng đoạn thành Header cho bậc 2–6 |
| `speckit-extension/commands/brd-import.md` | quy trình command (tiếng Việt) |
| `speckit-extension/scripts/tests/` | pytest |

Chia thành package thay vì một file như `csv_to_xlsx.py` vì tổng khối lượng ~800 dòng với 6 trách nhiệm tách bạch. `build-zip.sh` đã dùng `find scripts -type f` giữ nguyên cây con nên **không cần sửa** — task cuối xác nhận bằng `unzip -l`.

---

### Task 1: `naming.slugify` — đặt tên thư mục/file từ tiêu đề tiếng Việt

**Files:**
- Create: `speckit-extension/scripts/brd/__init__.py`
- Create: `speckit-extension/scripts/brd/naming.py`
- Test: `speckit-extension/scripts/tests/test_naming.py`

**Interfaces:**
- Consumes: không
- Produces: `slugify(title: str, maxlen: int = 60) -> str`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_naming.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brd.naming import slugify


def test_bo_dau_tieng_viet():
    assert slugify("Quản lý người dùng quản trị") == "quan-ly-nguoi-dung-quan-tri"


def test_chu_d_gach_ngang():
    assert slugify("Đăng nhập") == "dang-nhap"


def test_ky_tu_dac_biet_thanh_gach_noi():
    assert slugify("Quản lý doanh nghiệp (nhà trường/trung tâm)") == (
        "quan-ly-doanh-nghiep-nha-truong-trung-tam"
    )


def test_khong_gach_noi_lien_nhau_hay_o_hai_dau():
    assert slugify("  Giám sát:  phần cứng; phần mềm  ") == (
        "giam-sat-phan-cung-phan-mem"
    )


def test_cat_theo_maxlen_khong_de_gach_noi_o_cuoi():
    out = slugify("Báo cáo phân bổ doanh thu khách hàng theo gói dịch vụ", maxlen=20)
    assert len(out) <= 20
    assert not out.endswith("-")


def test_tieu_de_khong_con_ky_tu_hop_le_thi_tra_ve_muc():
    assert slugify("???") == "muc"
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_naming.py -q`
Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'brd'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd/__init__.py` (file rỗng).

Tạo `speckit-extension/scripts/brd/naming.py`:

```python
"""Đặt tên thư mục/file từ tiêu đề mục trong tài liệu."""

import re
import unicodedata

# NFD không tách được đ/Đ nên phải thay tay trước khi chuẩn hoá.
_D_MAP = str.maketrans({"đ": "d", "Đ": "D"})


def slugify(title: str, maxlen: int = 60) -> str:
    """Tiêu đề tiếng Việt -> slug [a-z0-9-], tối đa maxlen ký tự."""
    s = title.translate(_D_MAP)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).lower().strip("-")
    if len(s) > maxlen:
        s = s[:maxlen].rstrip("-")
    return s or "muc"
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_naming.py -q`
Kỳ vọng: 6 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd/__init__.py speckit-extension/scripts/brd/naming.py speckit-extension/scripts/tests/test_naming.py
git commit -m "feat(dft-speckit): slugify tiêu đề tiếng Việt cho brd-import"
```

---

### Task 2: `outline` — phân tích heading, thống kê cấp, luật chọn cấp cắt

**Files:**
- Create: `speckit-extension/scripts/brd/outline.py`
- Test: `speckit-extension/scripts/tests/test_outline.py`

**Interfaces:**
- Consumes: không
- Produces:
  - `parse_headings(md: str) -> list[dict]` — mỗi phần tử `{"line": int, "level": int, "title": str}`, `line` đánh số từ 0
  - `depth_map(headings: list[dict]) -> dict[int, int]` — cấp Word thưa → độ sâu liên tục từ 1
  - `segment_ends(headings: list[dict], total_lines: int) -> list[int]` — dòng kết thúc (loại trừ) của segment mỗi heading, theo quy tắc "heading kế tiếp có `level` ≤ level hiện tại"
  - `level_stats(headings, md_lines, dmap) -> list[dict]` — `{"depth", "word_level", "count", "median", "min", "max"}` theo từng độ sâu, tăng dần
  - `recommend_depth(stats: list[dict], min_median: int = 3000) -> int`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_outline.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brd.outline import (
    depth_map,
    level_stats,
    parse_headings,
    recommend_depth,
    segment_ends,
)

MD = "\n".join(
    [
        "mở đầu",             # 0
        "",                   # 1
        "# Nhóm A",           # 2
        "thân A",             # 3
        "### Phân hệ A1",     # 4
        "thân A1",            # 5
        "###### Màn 1",       # 6
        "thân màn 1",         # 7
        "######## Mục con",   # 8
        "thân mục con",       # 9
        "###### Màn 2",       # 10
        "thân màn 2",         # 11
    ]
)


def test_parse_headings_bat_dung_cap_va_dong():
    hs = parse_headings(MD)
    assert [(h["line"], h["level"], h["title"]) for h in hs] == [
        (2, 1, "Nhóm A"),
        (4, 3, "Phân hệ A1"),
        (6, 6, "Màn 1"),
        (8, 8, "Mục con"),
        (10, 6, "Màn 2"),
    ]


def test_parse_headings_bo_qua_khoi_code():
    md = "```\n# không phải heading\n```\n# thật"
    assert [h["title"] for h in parse_headings(md)] == ["thật"]


def test_parse_headings_bo_qua_thang_khong_co_dau_cach():
    assert parse_headings("#khong-phai-heading") == []


def test_depth_map_nen_cap_thua_thanh_lien_tuc():
    assert depth_map(parse_headings(MD)) == {1: 1, 3: 2, 6: 3, 8: 4}


def test_segment_ends_dung_ket_thuc_theo_cap():
    hs = parse_headings(MD)
    total = len(MD.split("\n"))
    # Nhóm A -> hết file; Phân hệ A1 -> hết file; Màn 1 -> dòng 10; Mục con -> dòng 10
    assert segment_ends(hs, total) == [total, total, 10, 10, total]


def test_level_stats_dem_va_do_kich_thuoc():
    hs = parse_headings(MD)
    lines = MD.split("\n")
    stats = level_stats(hs, lines, depth_map(hs))
    by_depth = {s["depth"]: s for s in stats}
    assert by_depth[1]["count"] == 1
    assert by_depth[3]["count"] == 2
    assert by_depth[3]["word_level"] == 6
    assert by_depth[3]["min"] > 0


def test_recommend_depth_lay_cap_sau_nhat_dat_nguong():
    stats = [
        {"depth": 1, "median": 900_000},
        {"depth": 2, "median": 200_000},
        {"depth": 3, "median": 30_000},
        {"depth": 4, "median": 305},      # trượt
        {"depth": 5, "median": 23_808},   # đạt, sâu hơn -> phải chọn cái này
        {"depth": 6, "median": 174},
    ]
    assert recommend_depth(stats, min_median=3000) == 5


def test_recommend_depth_khong_cap_nao_dat_thi_tra_ve_1():
    assert recommend_depth([{"depth": 1, "median": 10}], min_median=3000) == 1
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_outline.py -q`
Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'brd.outline'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd/outline.py`:

```python
"""Phân tích cây heading trong file markdown trung gian do pandoc sinh."""

import re
import statistics

HEADING_RE = re.compile(r"^(#{1,9}) +(\S.*?)\s*$")


def parse_headings(md):
    """[{line, level, title}] theo thứ tự xuất hiện. Bỏ qua nội dung trong khối code."""
    out = []
    fence = None
    for i, line in enumerate(md.split("\n")):
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                continue
        else:
            if stripped.startswith(fence):
                fence = None
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append({"line": i, "level": len(m.group(1)), "title": m.group(2)})
    return out


def depth_map(headings):
    """Cấp Word thưa (vd 1,3,4,5,6,8) -> độ sâu liên tục 1..n."""
    levels = sorted({h["level"] for h in headings})
    return {lv: i + 1 for i, lv in enumerate(levels)}


def segment_ends(headings, total_lines):
    """Dòng kết thúc (loại trừ) của segment mỗi heading."""
    ends = []
    for k, h in enumerate(headings):
        end = total_lines
        for nxt in headings[k + 1:]:
            if nxt["level"] <= h["level"]:
                end = nxt["line"]
                break
        ends.append(end)
    return ends


def level_stats(headings, md_lines, dmap):
    """Thống kê kích thước segment theo từng độ sâu, tăng dần."""
    ends = segment_ends(headings, len(md_lines))
    buckets = {}
    for h, end in zip(headings, ends):
        size = sum(len(x) + 1 for x in md_lines[h["line"]:end])
        buckets.setdefault(dmap[h["level"]], {"word_level": h["level"], "sizes": []})
        buckets[dmap[h["level"]]]["sizes"].append(size)
    stats = []
    for depth in sorted(buckets):
        sizes = buckets[depth]["sizes"]
        stats.append({
            "depth": depth,
            "word_level": buckets[depth]["word_level"],
            "count": len(sizes),
            "median": int(statistics.median(sizes)),
            "min": min(sizes),
            "max": max(sizes),
        })
    return stats


def recommend_depth(stats, min_median=3000):
    """Cấp SÂU NHẤT còn có trung vị >= nguong.

    Luật KHÔNG đơn điệu: ở BRD Mobifone cấp 4 có trung vị 305 (trượt) nhưng
    cấp 5 có 23.808 (đạt). Phải duyệt HẾT rồi lấy max — dừng sớm ở cấp trượt
    đầu tiên sẽ chọn nhầm cấp 3.
    """
    ok = [s["depth"] for s in stats if s["median"] >= min_median]
    return max(ok) if ok else 1
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_outline.py -q`
Kỳ vọng: 8 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd/outline.py speckit-extension/scripts/tests/test_outline.py
git commit -m "feat(dft-speckit): phân tích cây heading và luật chọn cấp cắt"
```

---

### Task 3: `convert` — gọi pandoc và dựng `reference.docx` rút gọn

**Files:**
- Create: `speckit-extension/scripts/brd/convert.py`
- Test: `speckit-extension/scripts/tests/conftest.py`
- Test: `speckit-extension/scripts/tests/test_convert.py`

**Interfaces:**
- Consumes: không
- Produces:
  - `class ConvertError(Exception)`
  - `check_pandoc() -> str` — trả chuỗi version, ném `ConvertError` kèm hướng dẫn cài nếu thiếu
  - `run_pandoc(docx: Path, workdir: Path, lua_filter: Path | None = None, metadata: dict | None = None) -> Path` — trả đường dẫn `workdir/brd.md`, ảnh nằm ở `workdir/media/media/`. `metadata` được ghi ra `workdir/metadata.json` và nạp bằng `--metadata-file` (KHÔNG dùng `-M`, vì `-M` chỉ truyền được chuỗi phẳng còn Lua filter cần danh sách bản ghi)
  - `build_reference_docx(docx: Path, dest: Path) -> Path`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/conftest.py`:

```python
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_BRD = REPO_ROOT / "refs" / "5. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Mobifone.docx"


@pytest.fixture(scope="session")
def real_brd():
    if not REAL_BRD.exists():
        pytest.skip(f"Không có BRD thật tại {REAL_BRD} (thư mục refs/ không được commit)")
    return REAL_BRD


@pytest.fixture(scope="session", autouse=True)
def require_pandoc():
    if shutil.which("pandoc") is None:
        pytest.skip("Không tìm thấy pandoc trên PATH")
```

Tạo `speckit-extension/scripts/tests/test_convert.py`:

```python
import subprocess
from pathlib import Path

import pytest

from brd.convert import ConvertError, build_reference_docx, check_pandoc, run_pandoc


def test_check_pandoc_tra_ve_version():
    assert check_pandoc().startswith("3.")


def test_run_pandoc_sinh_md_va_tach_anh(real_brd, tmp_path):
    md_path = run_pandoc(real_brd, tmp_path)
    assert md_path == tmp_path / "brd.md"
    text = md_path.read_text(encoding="utf-8")
    assert "<table>" not in text, "phải dùng -t markdown (grid table), không phải gfm"
    assert text.count("](./media/media/") == 387
    assert len(list((tmp_path / "media" / "media").iterdir())) == 386


def test_build_reference_docx_nho_va_pandoc_chap_nhan(real_brd, tmp_path):
    ref = build_reference_docx(real_brd, tmp_path / "reference.docx")
    assert ref.stat().st_size < 1_000_000, "phải bỏ word/media/ nên chỉ còn vài chục KB"
    src = tmp_path / "h.md"
    src.write_text("# H1\n\ntext\n\n## H2\n\ntext2\n", encoding="utf-8")
    out = tmp_path / "h.docx"
    subprocess.run(
        ["pandoc", str(src), f"--reference-doc={ref}", "-o", str(out)],
        check=True, capture_output=True,
    )
    import re
    import zipfile
    xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf-8")
    styles = re.findall(r'w:pStyle w:val="(Heading\d)"', xml)
    assert styles == ["Heading1", "Heading2"]


def test_run_pandoc_bao_loi_ro_khi_file_khong_ton_tai(tmp_path):
    with pytest.raises(ConvertError):
        run_pandoc(tmp_path / "khong-co.docx", tmp_path)
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_convert.py -q`
Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'brd.convert'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd/convert.py`:

```python
"""Gọi pandoc và dựng reference.docx rút gọn từ file BRD gốc."""

import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

PANDOC_MISSING = (
    "Không tìm thấy pandoc trên PATH. Cài đặt:\n"
    "  Windows: winget install --id JohnMacFarlane.Pandoc\n"
    "  macOS:   brew install pandoc\n"
    "  Linux:   sudo apt install pandoc\n"
    "Yêu cầu pandoc >= 3.0."
)

# Body rỗng cho reference.docx: giữ nguyên styles.xml/theme/header/footer của
# tài liệu gốc, vứt toàn bộ nội dung và ảnh.
_EMPTY_BODY = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body><w:p/><w:sectPr/></w:body></w:document>"
)


class ConvertError(Exception):
    pass


def check_pandoc():
    if shutil.which("pandoc") is None:
        raise ConvertError(PANDOC_MISSING)
    out = subprocess.run(["pandoc", "--version"], capture_output=True, text=True).stdout
    m = re.search(r"pandoc\s+(\d+\.\d+[^\s]*)", out)
    if not m:
        raise ConvertError("Không đọc được version của pandoc: " + out.splitlines()[0])
    if int(m.group(1).split(".")[0]) < 3:
        raise ConvertError(f"Cần pandoc >= 3.0, đang có {m.group(1)}.")
    return m.group(1)


def run_pandoc(docx, workdir, lua_filter=None, metadata=None):
    """docx -> workdir/brd.md, ảnh tách vào workdir/media/media/."""
    docx, workdir = Path(docx), Path(workdir)
    if not docx.is_file():
        raise ConvertError(f"Không thấy file: {docx}")
    check_pandoc()
    workdir.mkdir(parents=True, exist_ok=True)
    md_path = workdir / "brd.md"
    src_fmt = "docx+styles" if lua_filter else "docx"
    cmd = ["pandoc", str(docx.resolve()), "-f", src_fmt, "-t", "markdown",
           "--extract-media=./media", "-o", "brd.md"]
    if lua_filter:
        cmd += [f"--lua-filter={Path(lua_filter).resolve()}"]
    if metadata:
        # --metadata-file chứ không phải -M: -M chỉ truyền được chuỗi phẳng,
        # còn filter cần cả một danh sách bản ghi {text, level}.
        (workdir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        cmd += ["--metadata-file=metadata.json"]
    proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ConvertError(f"pandoc thất bại (mã {proc.returncode}):\n{proc.stderr}")
    return md_path


def build_reference_docx(docx, dest):
    """Bản sao docx gốc: bỏ word/media/, thay document.xml bằng body rỗng.

    Giữ styles.xml/theme/header/footer để brd-export sau này xuất đúng trình bày.
    72MB -> ~36KB trên BRD Mobifone.
    """
    docx, dest = Path(docx), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.startswith("word/media/"):
                continue
            data = _EMPTY_BODY.encode("utf-8") if item.filename == "word/document.xml" \
                else zin.read(item.filename)
            zout.writestr(item, data)
    return dest
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_convert.py -q`
Kỳ vọng: 4 passed (mất ~30 giây do convert BRD thật)

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd/convert.py speckit-extension/scripts/tests/conftest.py speckit-extension/scripts/tests/test_convert.py
git commit -m "feat(dft-speckit): gọi pandoc và dựng reference.docx rút gọn"
```

---

### Task 4: `docx_probe` — xác định bậc dò cấu trúc (bậc 1 và 2)

**Files:**
- Create: `speckit-extension/scripts/brd/docx_probe.py`
- Test: `speckit-extension/scripts/tests/test_docx_probe.py`

**Interfaces:**
- Consumes: không
- Produces:
  - `heading_style_levels(docx: Path) -> dict[str, int]` — `styleId` → cấp Word (1-based), lấy từ `word/styles.xml` qua `w:outlineLvl` (cấp = outlineLvl + 1); chỉ nhận style thực sự dùng trong `document.xml`
  - `count_paragraph_styles(docx: Path) -> dict[str, int]` — `styleId` → số đoạn dùng style đó
  - `detect_tier(docx: Path) -> dict` — `{"tier": int, "note": str, "style_levels": dict, "heading_count": int, "needs_llm": bool}`. Bậc 1 khi có ≥5 đoạn dùng style `Heading\d`; bậc 2 khi không có Heading nhưng có style tự chế mang `outlineLvl`; ngược lại `tier=0`, `needs_llm=True` (bậc 3–6 làm ở Task 8–9)

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_docx_probe.py`:

```python
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
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_docx_probe.py -q`
Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'brd.docx_probe'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd/docx_probe.py`:

```python
"""Đọc XML bên trong .docx để xác định bậc dò cấu trúc TRƯỚC khi gọi pandoc."""

import collections
import re
import zipfile
from pathlib import Path

_STYLE_BLOCK_RE = re.compile(r"<w:style [^>]*w:styleId=\"([^\"]+)\".*?</w:style>", re.S)
_OUTLINE_RE = re.compile(r"<w:outlineLvl w:val=\"(\d+)\"")
_PSTYLE_RE = re.compile(r"<w:pStyle w:val=\"([^\"]+)\"")
_HEADING_ID_RE = re.compile(r"^Heading(\d)$")


def _read(docx, name):
    with zipfile.ZipFile(Path(docx)) as z:
        try:
            return z.read(name).decode("utf-8")
        except KeyError:
            return ""


def heading_style_levels(docx):
    """styleId -> cấp Word (1-based), suy từ w:outlineLvl trong styles.xml."""
    styles_xml = _read(docx, "word/styles.xml")
    used = set(count_paragraph_styles(docx))
    out = {}
    for m in _STYLE_BLOCK_RE.finditer(styles_xml):
        style_id = m.group(1)
        if style_id not in used:
            continue
        lvl = _OUTLINE_RE.search(m.group(0))
        if lvl:
            out[style_id] = int(lvl.group(1)) + 1
    return out


def count_paragraph_styles(docx):
    """styleId -> số đoạn văn dùng style đó."""
    return collections.Counter(_PSTYLE_RE.findall(_read(docx, "word/document.xml")))


def detect_tier(docx):
    counts = count_paragraph_styles(docx)
    heading_count = sum(n for sid, n in counts.items() if _HEADING_ID_RE.match(sid))
    if heading_count >= 5:
        used = sorted(
            {int(_HEADING_ID_RE.match(s).group(1)) for s in counts if _HEADING_ID_RE.match(s)}
        )
        return {
            "tier": 1,
            "note": f"Heading style chuẩn, {heading_count} heading, cấp Word {used}",
            "style_levels": {s: int(_HEADING_ID_RE.match(s).group(1))
                             for s in counts if _HEADING_ID_RE.match(s)},
            "heading_count": heading_count,
            "needs_llm": False,
        }
    custom = {sid: lvl for sid, lvl in heading_style_levels(docx).items()
              if not _HEADING_ID_RE.match(sid)}
    if len(custom) >= 2:
        n = sum(counts[s] for s in custom)
        return {
            "tier": 2,
            "note": f"Style tự chế có outlineLvl: {sorted(custom)}, {n} đoạn",
            "style_levels": custom,
            "heading_count": n,
            "needs_llm": False,
        }
    return {
        "tier": 0,
        "note": "Không thấy Heading style, cũng không thấy style tự chế có outlineLvl",
        "style_levels": {},
        "heading_count": 0,
        "needs_llm": True,
    }
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_docx_probe.py -q`
Kỳ vọng: 3 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd/docx_probe.py speckit-extension/scripts/tests/test_docx_probe.py
git commit -m "feat(dft-speckit): dò bậc cấu trúc docx từ styles.xml (bậc 1-2)"
```

---

### Task 5: `splitter` — dựng danh sách node và cắt cây

**Files:**
- Create: `speckit-extension/scripts/brd/splitter.py`
- Test: `speckit-extension/scripts/tests/test_splitter.py`

**Interfaces:**
- Consumes: `brd.naming.slugify`, `brd.outline.parse_headings`, `brd.outline.depth_map`
- Produces:
  - `class SplitError(Exception)`
  - `plan_nodes(headings, dmap, cut_depth, total_lines) -> list[dict]` — node vật chất hoá, mỗi node có khoá `id, order, depth, word_level, kind, title, path, parent, start, end`. Phần tử đầu **luôn** là node gốc `BRD-0000` (`kind="root"`, `depth=0`, `path="_index.md"`) giữ nội dung trước heading đầu tiên; `kind` còn lại là `"folder"` (depth < cut_depth) hoặc `"leaf"` (depth == cut_depth). Heading sâu hơn `cut_depth` **không** thành node — nó nằm trong file lá.
  - `render_file(node, md_lines, dmap, breadcrumb) -> str` — nội dung file hoàn chỉnh (frontmatter + thân đã chuẩn hoá heading + đã đổi đường dẫn ảnh)
  - `frontmatter_of(node, breadcrumb) -> str` — chuỗi frontmatter chính xác, dùng lại được khi ghép ngược
  - `rel_media_prefix(path: str) -> str` — `"../" * số-thư-mục-cha`
  - `write_tree(nodes, md_lines, dmap, dest: Path, meta: dict) -> None` — ghi toàn bộ file + `brd.manifest.yml`

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_splitter.py`:

```python
from brd.outline import depth_map, parse_headings
from brd.splitter import (
    frontmatter_of,
    plan_nodes,
    rel_media_prefix,
    render_file,
    write_tree,
)

MD = "\n".join(
    [
        "trang bìa",            # 0
        "",                     # 1
        "# Nhóm A",             # 2
        "thân A",               # 3
        "### Module A1",        # 4
        "thân A1",              # 5
        "###### Màn 1",         # 6
        "![](./media/media/image1.png)",  # 7
        "######## Mục con",     # 8
        "thân mục con",         # 9
        "###### Màn 2",         # 10
        "thân màn 2",           # 11
    ]
)


def _plan(cut_depth=3):
    hs = parse_headings(MD)
    return hs, depth_map(hs), plan_nodes(hs, depth_map(hs), cut_depth, len(MD.split("\n")))


def test_plan_nodes_co_node_goc_giu_phan_truoc_heading_dau():
    _, _, nodes = _plan()
    root = nodes[0]
    assert root["id"] == "BRD-0000"
    assert root["kind"] == "root"
    assert root["path"] == "_index.md"
    assert (root["start"], root["end"]) == (0, 2)


def test_plan_nodes_phan_loai_folder_va_leaf():
    _, _, nodes = _plan()
    kinds = [(n["title"], n["kind"]) for n in nodes[1:]]
    assert kinds == [
        ("Nhóm A", "folder"),
        ("Module A1", "folder"),
        ("Màn 1", "leaf"),
        ("Màn 2", "leaf"),
    ]


def test_plan_nodes_duong_dan_long_theo_cay_va_co_tien_to_so():
    _, _, nodes = _plan()
    paths = [n["path"] for n in nodes[1:]]
    assert paths == [
        "01-nhom-a/_index.md",
        "01-nhom-a/01-module-a1/_index.md",
        "01-nhom-a/01-module-a1/01-man-1.md",
        "01-nhom-a/01-module-a1/02-man-2.md",
    ]


def test_plan_nodes_segment_ke_tiep_nhau_khong_ho_khong_chong():
    _, _, nodes = _plan()
    spans = [(n["start"], n["end"]) for n in nodes]
    assert spans == [(0, 2), (2, 4), (4, 6), (6, 10), (10, 12)]


def test_heading_sau_hon_cap_cat_nam_trong_file_la():
    _, dmap, nodes = _plan()
    leaf = nodes[3]
    body = render_file(leaf, MD.split("\n"), dmap, ["Nhóm A", "Module A1"])
    assert "\n# Màn 1" in body
    assert "\n## Mục con" in body


def test_render_file_doi_duong_dan_anh_theo_do_sau():
    _, dmap, nodes = _plan()
    leaf = nodes[3]
    body = render_file(leaf, MD.split("\n"), dmap, ["Nhóm A", "Module A1"])
    assert "](../../media/image1.png)" in body


def test_rel_media_prefix():
    assert rel_media_prefix("_index.md") == ""
    assert rel_media_prefix("01-a/_index.md") == "../"
    assert rel_media_prefix("01-a/01-b/02-man-2.md") == "../../"


def test_frontmatter_of_co_dung_ba_khoa():
    _, _, nodes = _plan()
    fm = frontmatter_of(nodes[3], ["Nhóm A", "Module A1"])
    assert fm.startswith("---\n")
    assert "brd_id: BRD-0003\n" in fm
    assert 'title: "Màn 1"\n' in fm
    assert 'breadcrumb: ["Nhóm A", "Module A1"]\n' in fm
    assert fm.endswith("---\n\n")


def test_write_tree_ghi_du_file_va_manifest(tmp_path):
    _, dmap, nodes = _plan()
    write_tree(nodes, MD.split("\n"), dmap, tmp_path,
               {"source_file": "x.docx", "sha256": "abc", "imported_at": "2026-08-07",
                "pandoc": "3.9", "cut_depth": 3, "tier": 1, "tier_note": "test"})
    assert (tmp_path / "brd.manifest.yml").exists()
    assert (tmp_path / "01-nhom-a" / "01-module-a1" / "01-man-1.md").exists()
    manifest = (tmp_path / "brd.manifest.yml").read_text(encoding="utf-8")
    assert "cut_depth: 3" in manifest
    assert "depth_map: {1: 1, 2: 3, 3: 6, 4: 8}" in manifest
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_splitter.py -q`
Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'brd.splitter'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd/splitter.py`:

```python
"""Dựng danh sách node vật chất hoá và cắt file markdown trung gian thành cây."""

from pathlib import Path

from .naming import slugify
from .outline import HEADING_RE, segment_ends

MEDIA_SRC = "](./media/media/"


class SplitError(Exception):
    pass


def rel_media_prefix(path):
    """Số bậc '../' để từ file đó trỏ về thư mục media/ ở gốc."""
    return "../" * (len(Path(path).parts) - 1)


def plan_nodes(headings, dmap, cut_depth, total_lines):
    """Node vật chất hoá, theo thứ tự tài liệu. Phần tử đầu luôn là node gốc."""
    mat = [h for h in headings if dmap[h["level"]] <= cut_depth]
    first_line = mat[0]["line"] if mat else total_lines
    nodes = [{
        "id": "BRD-0000", "order": 0, "depth": 0, "word_level": 0, "kind": "root",
        "title": "(phần đầu tài liệu)", "path": "_index.md", "dir": "",
        "parent": None, "start": 0, "end": first_line,
    }]

    stack = []          # node folder đang mở, theo depth tăng dần
    counters = {}       # path thư mục cha -> số con đã cấp
    for order, h in enumerate(mat, start=1):
        depth = dmap[h["level"]]
        while stack and stack[-1]["depth"] >= depth:
            stack.pop()
        parent = stack[-1] if stack else None
        base = parent["dir"] if parent else ""
        counters[base] = counters.get(base, 0) + 1
        name = f'{counters[base]:02d}-{slugify(h["title"])}'
        kind = "leaf" if depth == cut_depth else "folder"
        node = {
            "id": f"BRD-{order:04d}", "order": order, "depth": depth,
            "word_level": h["level"], "kind": kind, "title": h["title"],
            "dir": f"{base}{name}/" if kind == "folder" else base,
            "path": f"{base}{name}/_index.md" if kind == "folder" else f"{base}{name}.md",
            "parent": parent["id"] if parent else None,
            "start": h["line"], "end": None,
        }
        nodes.append(node)
        if kind == "folder":
            stack.append(node)

    # Segment của MỌI node kết thúc ở node vật chất hoá kế tiếp. Nhờ vậy các
    # segment nối liền nhau, phủ kín file, không hở không chồng -> ghép ngược khớp.
    for i, node in enumerate(nodes):
        node["end"] = nodes[i + 1]["start"] if i + 1 < len(nodes) else total_lines
    return nodes


def frontmatter_of(node, breadcrumb):
    """Chuỗi frontmatter CHÍNH XÁC — verify.py dựng lại đúng chuỗi này để gỡ."""
    crumbs = ", ".join(f'"{c}"' for c in breadcrumb)
    return (
        "---\n"
        f'brd_id: {node["id"]}\n'
        f'title: "{node["title"]}"\n'
        f"breadcrumb: [{crumbs}]\n"
        "---\n\n"
    )


def _normalize_headings(lines, root_depth, dmap):
    out = []
    for line in lines:
        m = HEADING_RE.match(line)
        if not m:
            out.append(line)
            continue
        new_level = dmap[len(m.group(1))] - root_depth + 1
        if not 1 <= new_level <= 6:
            raise SplitError(
                f'Heading "{m.group(2)}" rơi vào cấp {new_level} sau chuẩn hoá '
                f"(hợp lệ 1..6). Chọn cấp cắt sâu hơn."
            )
        out.append("#" * new_level + " " + m.group(2))
    return out


def render_file(node, md_lines, dmap, breadcrumb):
    body = _normalize_headings(md_lines[node["start"]:node["end"]], node["depth"], dmap)
    text = "\n".join(body)
    text = text.replace(MEDIA_SRC, "](" + rel_media_prefix(node["path"]) + "media/")
    return frontmatter_of(node, breadcrumb) + text


def _breadcrumbs(nodes):
    by_id = {n["id"]: n for n in nodes}
    out = {}
    for n in nodes:
        crumbs, cur = [], n["parent"]
        while cur:
            crumbs.append(by_id[cur]["title"])
            cur = by_id[cur]["parent"]
        out[n["id"]] = list(reversed(crumbs))
    return out


def _q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_tree(nodes, md_lines, dmap, dest, meta):
    dest = Path(dest)
    crumbs = _breadcrumbs(nodes)
    for node in nodes:
        target = dest / node["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_file(node, md_lines, dmap, crumbs[node["id"]]),
                          encoding="utf-8", newline="\n")

    inv = ", ".join(f"{d}: {lv}" for lv, d in sorted(dmap.items(), key=lambda kv: kv[1]))
    lines = [
        'schema_version: "1.0"',
        "source:",
        f'  file: {_q(meta["source_file"])}',
        f'  sha256: {_q(meta["sha256"])}',
        f'  imported_at: {_q(meta["imported_at"])}',
        f'  pandoc: {_q(meta["pandoc"])}',
        f'cut_depth: {meta["cut_depth"]}',
        f'detection: {{ tier: {meta["tier"]}, note: {_q(meta["tier_note"])} }}',
        f"depth_map: {{{inv}}}",
        "nodes:",
    ]
    for n in nodes:
        lines.append(
            f'  - {{ id: {n["id"]}, order: {n["order"]}, depth: {n["depth"]}, '
            f'word_level: {n["word_level"]}, kind: {n["kind"]}, '
            f'title: {_q(n["title"])}, path: {_q(n["path"])}, '
            f'parent: {n["parent"] or "null"}, '
            f'chars: {sum(len(x) + 1 for x in md_lines[n["start"]:n["end"]])} }}'
        )
    (dest / "brd.manifest.yml").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8", newline="\n")
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_splitter.py -q`
Kỳ vọng: 9 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd/splitter.py speckit-extension/scripts/tests/test_splitter.py
git commit -m "feat(dft-speckit): cắt markdown trung gian thành cây thư mục + manifest"
```

---

### Task 6: `verify` — ghép ngược byte-for-byte và kiểm phụ

**Files:**
- Create: `speckit-extension/scripts/brd/verify.py`
- Test: `speckit-extension/scripts/tests/test_verify.py`

**Interfaces:**
- Consumes: `brd.splitter.frontmatter_of`, `brd.splitter.rel_media_prefix`, `brd.outline.HEADING_RE`
- Produces:
  - `class VerifyError(Exception)`
  - `reassemble(nodes, dest: Path, dmap: dict, breadcrumbs: dict) -> str` — dựng lại nội dung file trung gian từ các mảnh đã ghi
  - `check_roundtrip(nodes, dest, dmap, breadcrumbs, original_md: str) -> None` — ném `VerifyError` kèm số dòng lệch đầu tiên và 2 dòng hai phía
  - `secondary_checks(nodes, dest, media_dir: Path, heading_count: int) -> list[str]` — danh sách cảnh báo (không chặn)

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_verify.py`:

```python
import pytest

from brd.outline import depth_map, parse_headings
from brd.splitter import _breadcrumbs, plan_nodes, write_tree
from brd.verify import VerifyError, check_roundtrip, reassemble, secondary_checks

MD = "\n".join(
    [
        "trang bìa",
        "",
        "# Nhóm A",
        "thân A",
        "### Module A1",
        "thân A1",
        "###### Màn 1",
        "![](./media/media/image1.png)",
        "######## Mục con",
        "thân mục con",
        "###### Màn 2",
        "thân màn 2",
    ]
)

META = {"source_file": "x.docx", "sha256": "abc", "imported_at": "2026-08-07",
        "pandoc": "3.9", "cut_depth": 3, "tier": 1, "tier_note": "test"}


def _prepare(tmp_path):
    hs = parse_headings(MD)
    dmap = depth_map(hs)
    nodes = plan_nodes(hs, dmap, 3, len(MD.split("\n")))
    write_tree(nodes, MD.split("\n"), dmap, tmp_path, META)
    return nodes, dmap, _breadcrumbs(nodes)


def test_reassemble_khop_byte_for_byte(tmp_path):
    nodes, dmap, crumbs = _prepare(tmp_path)
    assert reassemble(nodes, tmp_path, dmap, crumbs) == MD


def test_check_roundtrip_khong_nem_khi_khop(tmp_path):
    nodes, dmap, crumbs = _prepare(tmp_path)
    check_roundtrip(nodes, tmp_path, dmap, crumbs, MD)


def test_check_roundtrip_nem_khi_co_nguoi_sua_mot_file(tmp_path):
    nodes, dmap, crumbs = _prepare(tmp_path)
    victim = tmp_path / "01-nhom-a" / "01-module-a1" / "01-man-1.md"
    victim.write_text(victim.read_text(encoding="utf-8") + "\nthừa ra\n", encoding="utf-8")
    with pytest.raises(VerifyError) as e:
        check_roundtrip(nodes, tmp_path, dmap, crumbs, MD)
    assert "dòng" in str(e.value)


def test_secondary_checks_bao_anh_khong_ton_tai(tmp_path):
    nodes, _, _ = _prepare(tmp_path)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", heading_count=5)
    assert any("image1.png" in w for w in warnings)


def test_secondary_checks_bao_lech_so_heading(tmp_path):
    nodes, _, _ = _prepare(tmp_path)
    (tmp_path / "media").mkdir()
    warnings = secondary_checks(nodes, tmp_path, tmp_path / "media", heading_count=99)
    assert any("heading" in w.lower() for w in warnings)
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_verify.py -q`
Kỳ vọng: FAIL — `ModuleNotFoundError: No module named 'brd.verify'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd/verify.py`:

```python
"""Ghép ngược cây markdown về file trung gian và đòi giống byte-for-byte."""

import re
from pathlib import Path

from .outline import HEADING_RE
from .splitter import MEDIA_SRC, frontmatter_of, rel_media_prefix

_IMG_RE = re.compile(r"\]\((?:\.\./)*media/([^)]+)\)")


class VerifyError(Exception):
    pass


def _denormalize(lines, root_depth, depth_to_level):
    out = []
    for line in lines:
        m = HEADING_RE.match(line)
        if not m:
            out.append(line)
            continue
        depth = root_depth + len(m.group(1)) - 1
        if depth not in depth_to_level:
            raise VerifyError(f"Không suy được cấp Word cho heading: {m.group(2)}")
        out.append("#" * depth_to_level[depth] + " " + m.group(2))
    return out


def reassemble(nodes, dest, dmap, breadcrumbs):
    """Dựng lại file trung gian từ các mảnh đã ghi, hoàn tác đúng 3 phép biến đổi."""
    dest = Path(dest)
    depth_to_level = {d: lv for lv, d in dmap.items()}
    chunks = []
    for node in nodes:
        text = (dest / node["path"]).read_text(encoding="utf-8")
        # 1. gỡ frontmatter — dựng lại đúng chuỗi đã ghi rồi cắt tiền tố
        fm = frontmatter_of(node, breadcrumbs[node["id"]])
        if not text.startswith(fm):
            raise VerifyError(f'Frontmatter của {node["path"]} không khớp bản đã sinh.')
        text = text[len(fm):]
        # 2. trả đường dẫn ảnh về dạng chuẩn
        text = text.replace("](" + rel_media_prefix(node["path"]) + "media/", MEDIA_SRC)
        # 3. trả heading về cấp Word gốc
        chunks.append("\n".join(_denormalize(text.split("\n"), node["depth"], depth_to_level)))
    return "\n".join(chunks)


def check_roundtrip(nodes, dest, dmap, breadcrumbs, original_md):
    got = reassemble(nodes, dest, dmap, breadcrumbs)
    if got == original_md:
        return
    a, b = original_md.split("\n"), got.split("\n")
    for i in range(max(len(a), len(b))):
        av = a[i] if i < len(a) else "<hết file>"
        bv = b[i] if i < len(b) else "<hết file>"
        if av != bv:
            lo = max(0, i - 2)
            ctx = "\n".join(f"    {j}: {a[j]}" for j in range(lo, min(i + 3, len(a))))
            raise VerifyError(
                f"Ghép ngược lệch ở dòng {i}:\n"
                f"  bản gốc:   {av!r}\n"
                f"  ghép ngược:{bv!r}\n"
                f"  ngữ cảnh bản gốc:\n{ctx}"
            )
    raise VerifyError(f"Ghép ngược lệch độ dài: gốc {len(a)} dòng, ghép ngược {len(b)} dòng.")


def secondary_checks(nodes, dest, media_dir, heading_count):
    """Kiểm phụ — trả về danh sách cảnh báo, KHÔNG chặn việc ghi."""
    dest, media_dir = Path(dest), Path(media_dir)
    warnings = []
    referenced = set()
    for node in nodes:
        text = (dest / node["path"]).read_text(encoding="utf-8")
        for name in _IMG_RE.findall(text):
            referenced.add(name)
            if not (media_dir / name).is_file():
                warnings.append(f'Ảnh không tồn tại: media/{name} (tham chiếu ở {node["path"]})')
        size = sum(len(line) + 1 for line in text.split("\n"))
        if size > 60_000:
            warnings.append(f'File lớn {size:,} ký tự: {node["path"]} — cân nhắc cắt sâu hơn')
    if media_dir.is_dir():
        for f in sorted(media_dir.iterdir()):
            if f.is_file() and f.name not in referenced:
                warnings.append(f"Ảnh mồ côi, không ai tham chiếu: media/{f.name}")
    if len(nodes) - 1 > heading_count:
        warnings.append(
            f"Số node ({len(nodes) - 1}) nhiều hơn số heading đếm từ docx ({heading_count})"
        )
    titles = {}
    for node in nodes:
        titles.setdefault(node["title"], []).append(node["path"])
    for title, paths in titles.items():
        if len(paths) > 1:
            warnings.append(f'Trùng tiêu đề "{title}" ở {len(paths)} chỗ: {", ".join(paths)}')
    return warnings
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_verify.py -q`
Kỳ vọng: 5 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/brd/verify.py speckit-extension/scripts/tests/test_verify.py
git commit -m "feat(dft-speckit): ghép ngược byte-for-byte và kiểm phụ"
```

---

### Task 7: CLI `brd_import.py` + chạy trọn vòng trên BRD thật

**Files:**
- Create: `speckit-extension/scripts/brd_import.py`
- Test: `speckit-extension/scripts/tests/test_end_to_end.py`

**Interfaces:**
- Consumes: mọi module `brd.*` ở Task 1–6
- Produces: CLI
  - `python brd_import.py probe <docx> --work <dir>` → ghi `<dir>/probe.json`, in JSON ra stdout
  - `python brd_import.py split --work <dir> --depth N --dest <dir>` → ghi cây, in `report.json` ra stdout
  - Mã thoát: `0` thành công, `2` lỗi có thông điệp tiếng Việt trên stderr

`probe.json`:
```json
{"tier": 1, "note": "...", "needs_llm": false, "recommend_depth": 5,
 "levels": [{"depth": 1, "word_level": 1, "count": 2, "median": 752651, "min": 435555, "max": 1069748}],
 "warnings": [], "candidates": []}
```

`report.json`:
```json
{"dest": "docs/brd", "files": 98, "folders": 43, "cut_depth": 5, "tier": 1,
 "roundtrip": "OK", "media": 386, "warnings": ["..."]}
```

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/test_end_to_end.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "brd_import.py"


def _run(*args):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, encoding="utf-8")
    return proc


def test_probe_brd_that_ra_bac_1_va_de_xuat_cap_5(real_brd, tmp_path):
    proc = _run("probe", str(real_brd), "--work", str(tmp_path / "w"))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["tier"] == 1
    assert data["needs_llm"] is False
    assert data["recommend_depth"] == 5
    by_depth = {lv["depth"]: lv for lv in data["levels"]}
    assert by_depth[5]["count"] == 54
    assert by_depth[6]["count"] == 432


def test_split_brd_that_ghep_nguoc_khop_va_ra_54_file_la(real_brd, tmp_path):
    work, dest = tmp_path / "w", tmp_path / "out"
    assert _run("probe", str(real_brd), "--work", str(work)).returncode == 0
    proc = _run("split", "--work", str(work), "--depth", "5", "--dest", str(dest))
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["roundtrip"] == "OK"
    assert report["media"] == 386
    assert (dest / "brd.manifest.yml").exists()
    assert (dest / "reference.docx").stat().st_size < 1_000_000
    leaves = [p for p in dest.rglob("*.md") if p.name != "_index.md"]
    assert len(leaves) == 54


def test_split_tu_choi_de_len_thu_muc_da_co_manifest(real_brd, tmp_path):
    work, dest = tmp_path / "w", tmp_path / "out"
    _run("probe", str(real_brd), "--work", str(work))
    _run("split", "--work", str(work), "--depth", "5", "--dest", str(dest))
    proc = _run("split", "--work", str(work), "--depth", "5", "--dest", str(dest))
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["dest"].endswith("out.new")
    assert "diff" in report


def test_probe_bao_loi_ro_khi_khong_phai_docx(tmp_path):
    bad = tmp_path / "x.txt"
    bad.write_text("không phải docx", encoding="utf-8")
    proc = _run("probe", str(bad), "--work", str(tmp_path / "w"))
    assert proc.returncode == 2
    assert ".docx" in proc.stderr
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_end_to_end.py -q`
Kỳ vọng: FAIL — `can't open file 'brd_import.py'`

- [ ] **Step 3: Cài đặt tối thiểu**

Tạo `speckit-extension/scripts/brd_import.py`:

```python
#!/usr/bin/env python3
"""brd-import — bẻ file BRD .docx thành cây markdown.

    probe <docx> --work <dir>                    dò cấu trúc, thống kê cấp
    split --work <dir> --depth N --dest <dir>    cắt cây + kiểm chứng
"""

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brd.convert import ConvertError, build_reference_docx, check_pandoc, run_pandoc
from brd.docx_probe import detect_tier
from brd.outline import depth_map, level_stats, parse_headings, recommend_depth
from brd.splitter import SplitError, _breadcrumbs, plan_nodes, write_tree
from brd.verify import VerifyError, check_roundtrip, secondary_checks


def _die(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_probe(args):
    docx = Path(args.docx)
    if docx.suffix.lower() != ".docx":
        _die(f"Chỉ nhận file .docx, nhận được: {docx.name}")
    if not docx.is_file():
        _die(f"Không thấy file: {docx}")
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)

    tier = detect_tier(docx)
    if tier["needs_llm"]:
        _die("Chưa dò được cấu trúc bằng bậc 1-2. Bậc 3-6 chưa cài đặt.")

    md_path = run_pandoc(docx, work)
    md = md_path.read_text(encoding="utf-8")
    headings = parse_headings(md)
    if not headings:
        _die("Markdown sau khi convert không có heading nào — không cắt được.")
    dmap = depth_map(headings)
    stats = level_stats(headings, md.split("\n"), dmap)

    result = {
        "tier": tier["tier"], "note": tier["note"], "needs_llm": False,
        "recommend_depth": recommend_depth(stats), "levels": stats,
        "warnings": [], "candidates": [],
        "source": {"file": docx.name, "sha256": _sha256(docx),
                   "pandoc": check_pandoc(), "path": str(docx.resolve())},
    }
    (work / "probe.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


def _diff_trees(old, new):
    def snap(root):
        return {str(p.relative_to(root)).replace("\\", "/"): _sha256(p)
                for p in sorted(root.rglob("*")) if p.is_file()}
    a, b = snap(old), snap(new)
    return {
        "them": sorted(set(b) - set(a)),
        "mat": sorted(set(a) - set(b)),
        "doi": sorted(k for k in set(a) & set(b) if a[k] != b[k]),
    }


def cmd_split(args):
    work = Path(args.work)
    probe_file = work / "probe.json"
    if not probe_file.is_file():
        _die(f"Chưa có {probe_file} — chạy `probe` trước.")
    probe = json.loads(probe_file.read_text(encoding="utf-8"))
    md = (work / "brd.md").read_text(encoding="utf-8")
    md_lines = md.split("\n")

    headings = parse_headings(md)
    dmap = depth_map(headings)
    if args.depth not in set(dmap.values()):
        _die(f"Cấp cắt {args.depth} không tồn tại. Các cấp có thật: {sorted(set(dmap.values()))}")

    dest = Path(args.dest)
    diff = None
    final_dest = dest
    if (dest / "brd.manifest.yml").is_file():
        final_dest = dest.with_name(dest.name + ".new")

    staging = work / "staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    try:
        nodes = plan_nodes(headings, dmap, args.depth, len(md_lines))
        write_tree(nodes, md_lines, dmap, staging, {
            "source_file": probe["source"]["file"], "sha256": probe["source"]["sha256"],
            "imported_at": dt.date.today().isoformat(), "pandoc": probe["source"]["pandoc"],
            "cut_depth": args.depth, "tier": probe["tier"], "tier_note": probe["note"],
        })
        crumbs = _breadcrumbs(nodes)
        check_roundtrip(nodes, staging, dmap, crumbs, md)
    except (SplitError, VerifyError) as e:
        _die(f"Kiểm chứng thất bại — KHÔNG ghi gì ra {final_dest}.\n{e}")

    media_src = work / "media" / "media"
    media_dst = staging / "media"
    if media_src.is_dir():
        shutil.copytree(media_src, media_dst)
    else:
        media_dst.mkdir()
    build_reference_docx(probe["source"]["path"], staging / "reference.docx")
    warnings = secondary_checks(nodes, staging, media_dst,
                                sum(lv["count"] for lv in probe["levels"]))

    if final_dest.exists():
        shutil.rmtree(final_dest)
    final_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staging), str(final_dest))
    if final_dest != dest:
        diff = _diff_trees(dest, final_dest)

    report = {
        "dest": str(final_dest), "cut_depth": args.depth, "tier": probe["tier"],
        "files": sum(1 for _ in final_dest.rglob("*.md")),
        "folders": sum(1 for p in final_dest.rglob("*") if p.is_dir() and p.name != "media"),
        "roundtrip": "OK",
        "media": sum(1 for _ in (final_dest / "media").iterdir()),
        "warnings": warnings,
    }
    if diff is not None:
        report["diff"] = diff
    print(json.dumps(report, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Bẻ file BRD .docx thành cây markdown.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe", help="Dò cấu trúc và thống kê cấp")
    p.add_argument("docx")
    p.add_argument("--work", required=True)
    p.set_defaults(func=cmd_probe)

    s = sub.add_parser("split", help="Cắt cây và kiểm chứng")
    s.add_argument("--work", required=True)
    s.add_argument("--depth", type=int, required=True)
    s.add_argument("--dest", required=True)
    s.set_defaults(func=cmd_split)

    args = parser.parse_args()
    try:
        args.func(args)
    except ConvertError as e:
        _die(str(e))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_end_to_end.py -q`
Kỳ vọng: 4 passed (mất ~2 phút — mỗi test convert lại BRD thật)

- [ ] **Step 5: Chạy toàn bộ test**

Chạy: `python -m pytest speckit-extension/scripts/tests -q`
Kỳ vọng: 39 passed

- [ ] **Step 6: Commit**

```bash
git add speckit-extension/scripts/brd_import.py speckit-extension/scripts/tests/test_end_to_end.py
git commit -m "feat(dft-speckit): CLI brd_import với probe/split, chạy trọn vòng BRD thật"
```

---

### Task 8: Lua filter + bậc 3–4 (mục lục, đánh số gõ tay)

**Files:**
- Create: `speckit-extension/scripts/promote_headings.lua`
- Modify: `speckit-extension/scripts/brd/docx_probe.py` — thêm `toc_titles`, `numbered_titles`, mở rộng `detect_tier`
- Modify: `speckit-extension/scripts/brd_import.py` — truyền filter + metadata khi tier ≥ 2
- Create: `speckit-extension/scripts/tests/fixtures/make_fixtures.py`
- Test: `speckit-extension/scripts/tests/test_tiers.py`

**Interfaces:**
- Consumes: `brd.convert.run_pandoc(docx, workdir, lua_filter, metadata)`
- Produces:
  - `toc_titles(docx) -> list[tuple[str, int]]` — `(tiêu đề, cấp)` moi từ đoạn style `TOC\d`/`toc \d`
  - `numbered_titles(docx) -> list[tuple[str, int]]` — đoạn khớp `^\s*(\d+(\.\d+)*)\.?\s+\S`, cấp = số nhóm số; chỉ nhận khi dãy **liên tục** (mọi tiền tố của một số hiệu đều xuất hiện trước nó)
  - `promotions_for(docx) -> list[dict]` — `[{"text": str, "level": int}]` để nạp vào Lua filter
  - Lua filter đọc `meta.promotions` (nạp qua `--metadata-file`): `Para` có text khớp `text` (so sau khi gộp khoảng trắng) → thành `Header level`; mọi `Div`/`Span` mang `custom-style` bị gỡ vỏ. Cuối tài liệu, nếu số lần nâng ≠ số mục trong `promotions` thì `error()` để pandoc thoát khác 0.

- [ ] **Step 1: Viết test thất bại**

Tạo `speckit-extension/scripts/tests/fixtures/make_fixtures.py`:

```python
"""Sinh docx fixture bằng pandoc. Chạy: python make_fixtures.py"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Dấu \\. là BẮT BUỘC: viết "1. Chương một" trong markdown thì pandoc dựng ra
# DANH SÁCH ĐÁNH SỐ trong docx chứ không phải đoạn văn, và fixture sẽ vô dụng.
NUMBERED = """1\\. Chương một

thân chương một

1.1 Mục một một

thân mục một một

1.2 Mục một hai

thân mục một hai

2\\. Chương hai

thân chương hai

2.1 Mục hai một

thân mục hai một
"""

PLAIN = """chỉ toàn đoạn văn thường

không có tiêu đề nào cả

đoạn thứ ba cũng vậy
"""


def build(name, text):
    src = HERE / (name + ".md")
    src.write_text(text, encoding="utf-8")
    subprocess.run(["pandoc", str(src), "-o", str(HERE / (name + ".docx"))], check=True)
    src.unlink()


if __name__ == "__main__":
    build("numbered", NUMBERED)
    build("plain", PLAIN)
    print("OK", file=sys.stderr)
```

Tạo `speckit-extension/scripts/tests/test_tiers.py`:

```python
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
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_tiers.py -q`
Kỳ vọng: FAIL — `ImportError: cannot import name 'toc_titles'`

- [ ] **Step 3: Cài đặt — thêm vào `docx_probe.py`**

Thêm vào cuối `speckit-extension/scripts/brd/docx_probe.py`:

```python
_PARA_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)
_TEXT_RE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
_TOC_STYLE_RE = re.compile(r"^(?:TOC|toc ?)(\d)$")
_NUM_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+\S")


def _paragraphs(docx):
    """[(styleId hoặc '', text)] theo thứ tự tài liệu."""
    xml = _read(docx, "word/document.xml")
    out = []
    for m in _PARA_RE.finditer(xml):
        block = m.group(0)
        style = _PSTYLE_RE.search(block)
        text = "".join(_TEXT_RE.findall(block)).strip()
        out.append((style.group(1) if style else "", text))
    return out


def _toc_text(block):
    """Text của một dòng mục lục, bỏ phần số trang sau dấu tab cuối cùng.

    Word đặt số trang sau <w:tab/>; ký tự tab KHÔNG nằm trong <w:t> nên nếu
    gộp thẳng mọi <w:t> sẽ ra "Tiêu đề12" — dính số trang vào tiêu đề.
    """
    head = block.rsplit("<w:tab/>", 1)[0] if "<w:tab/>" in block else block
    text = "".join(_TEXT_RE.findall(head)).strip()
    return re.sub(r"\s*\.{2,}\s*\d*$", "", text).strip()


def toc_titles(docx):
    """[(tiêu đề, cấp)] moi từ đoạn mang style TOC1..9 / 'toc 1'..'toc 9'."""
    xml = _read(docx, "word/document.xml")
    out = []
    for m in _PARA_RE.finditer(xml):
        block = m.group(0)
        style = _PSTYLE_RE.search(block)
        if not style:
            continue
        lvl = _TOC_STYLE_RE.match(style.group(1))
        if not lvl:
            continue
        text = _toc_text(block)
        if text:
            out.append((text, int(lvl.group(1))))
    return out


def numbered_titles(docx):
    """[(text, cấp)] cho đoạn gõ số tay, chỉ nhận khi dãy số LIÊN TỤC."""
    hits = []
    for _, text in _paragraphs(docx):
        m = _NUM_RE.match(text)
        if m and len(text) < 200:
            hits.append((text, m.group(1), len(m.group(1).split("."))))
    seen = set()
    out = []
    for text, num, level in hits:
        parts = num.split(".")
        prefixes = [".".join(parts[:i]) for i in range(1, len(parts))]
        if all(p in seen for p in prefixes):
            seen.add(num)
            out.append((text, level))
    return out


def promotions_for(docx):
    """[{'text','level'}] nạp cho Lua filter, theo bậc mà detect_tier chọn."""
    res = detect_tier(docx)
    if res["tier"] == 3:
        pairs = toc_titles(docx)
    elif res["tier"] == 4:
        pairs = numbered_titles(docx)
    else:
        return []
    return [{"text": t, "level": lv} for t, lv in pairs]
```

Sửa `detect_tier`: thay khối `return {... "tier": 0 ...}` cuối hàm bằng:

```python
    toc = toc_titles(docx)
    if len({lv for _, lv in toc}) >= 2 and len(toc) >= 5:
        return {"tier": 3, "note": f"Suy từ mục lục sẵn có, {len(toc)} mục",
                "style_levels": {}, "heading_count": len(toc), "needs_llm": False}
    numbered = numbered_titles(docx)
    if len({lv for _, lv in numbered}) >= 2 and len(numbered) >= 5:
        return {"tier": 4, "note": f"Suy từ đánh số gõ tay, {len(numbered)} mục",
                "style_levels": {}, "heading_count": len(numbered), "needs_llm": False}
    return {
        "tier": 0,
        "note": "Không thấy Heading style, style tự chế có outlineLvl, mục lục, hay đánh số liên tục",
        "style_levels": {}, "heading_count": 0, "needs_llm": True,
    }
```

- [ ] **Step 4: Cài đặt — Lua filter**

Tạo `speckit-extension/scripts/promote_headings.lua`:

```lua
-- Nâng đoạn văn thành Header theo danh sách nạp qua --metadata-file,
-- và gỡ vỏ Div/Span mang custom-style do `-f docx+styles` sinh ra.
-- KHÔNG dùng pandoc.json (chỉ có ở bản pandoc mới): --metadata-file đã tự
-- phân giải JSON thành MetaList/MetaMap sẵn.
local promotions = {}
local expected = 0
local promoted = 0

local function normalize(s)
  return (s:gsub("%s+", " "):gsub("^%s*(.-)%s*$", "%1"))
end

function Meta(meta)
  if meta.promotions == nil then return nil end
  for _, item in ipairs(meta.promotions) do
    local text = pandoc.utils.stringify(item.text)
    local level = math.tointeger(tonumber(pandoc.utils.stringify(item.level)))
    promotions[normalize(text)] = level
    expected = expected + 1
  end
  return nil
end

function Para(el)
  local key = normalize(pandoc.utils.stringify(el))
  local level = promotions[key]
  if level then
    promoted = promoted + 1
    return pandoc.Header(level, el.content)
  end
  return nil
end

function Div(el)
  if el.attributes["custom-style"] then return el.content end
  return nil
end

function Span(el)
  if el.attributes["custom-style"] then return el.content end
  return nil
end

function Pandoc(doc)
  if expected > 0 and promoted ~= expected then
    error(string.format(
      "promote_headings: nâng được %d/%d tiêu đề — danh sách promotions không khớp tài liệu",
      promoted, expected))
  end
  return doc
end

return {
  { Meta = Meta },
  { Div = Div, Span = Span, Para = Para },
  { Pandoc = Pandoc },
}
```

- [ ] **Step 5: Cài đặt — nối vào CLI**

Trong `speckit-extension/scripts/brd_import.py`, sửa `cmd_probe`: thay hai dòng

```python
    if tier["needs_llm"]:
        _die("Chưa dò được cấu trúc bằng bậc 1-2. Bậc 3-6 chưa cài đặt.")

    md_path = run_pandoc(docx, work)
```

thành

```python
    if tier["needs_llm"]:
        _die("Chưa dò được cấu trúc bằng bậc 1-4. Bậc 5-6 chưa cài đặt.")

    if tier["tier"] == 1:
        md_path = run_pandoc(docx, work)
    else:
        from brd.docx_probe import promotions_for
        lua = Path(__file__).resolve().parent / "promote_headings.lua"
        md_path = run_pandoc(docx, work, lua_filter=lua,
                             metadata={"promotions": promotions_for(docx)})
```

Bậc 2 dùng `promotions_for` trả về `[]` nên filter chỉ gỡ vỏ Div — đúng ý, vì `-f docx+styles` đã cho style tự chế thành `Header` sẵn khi style có `outlineLvl`.

- [ ] **Step 6: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_tiers.py -q`
Kỳ vọng: 6 passed

Chạy: `python -m pytest speckit-extension/scripts/tests -q`
Kỳ vọng: 45 passed — **bậc 1 phải không đổi hành vi**, `test_end_to_end.py` vẫn đạt.

- [ ] **Step 7: Commit**

```bash
git add speckit-extension/scripts/promote_headings.lua speckit-extension/scripts/brd/docx_probe.py speckit-extension/scripts/brd_import.py speckit-extension/scripts/tests/fixtures/make_fixtures.py speckit-extension/scripts/tests/test_tiers.py
git commit -m "feat(dft-speckit): dò cấu trúc bậc 3-4 qua mục lục và đánh số, Lua filter nâng heading"
```

---

### Task 9: Bậc 5–6 — heuristic định dạng và ứng viên cho LLM

**Files:**
- Modify: `speckit-extension/scripts/brd/docx_probe.py` — thêm `format_candidates`, mở rộng `detect_tier` và `promotions_for`
- Modify: `speckit-extension/scripts/brd_import.py` — `probe --outline` nhận quyết định của LLM
- Modify: `speckit-extension/scripts/tests/test_tiers.py` — thêm test bậc 5–6 và fixture âm

**Interfaces:**
- Consumes: `brd.docx_probe._paragraphs`
- Produces:
  - `format_candidates(docx) -> list[dict]` — `[{"index": int, "text": str, "bold": bool, "size": int|None}]`, chỉ đoạn `text` không rỗng, `len(text) < 120`, không kết thúc bằng `.`, và (in đậm **hoặc** cỡ chữ lớn hơn cỡ phổ biến nhất)
  - `detect_tier` trả `tier=5` khi suy được ≥2 cấp từ cỡ chữ giảm dần; trả `tier=0, needs_llm=True, candidates=[...]` khi không
  - CLI `probe <docx> --work <dir> --outline <file.json>` — `file.json` là `[{"index": int, "level": int}]` do LLM quyết; script chuyển thành `promotions` rồi convert lại **không** chạy pandoc lần đầu tiên nữa

- [ ] **Step 1: Viết test thất bại**

Thêm vào `speckit-extension/scripts/tests/fixtures/make_fixtures.py` (trước khối `if __name__`):

```python
BOLD = """**Chương một**

thân chương một

**Chương hai**

thân chương hai

**Chương ba**

thân chương ba

**Chương bốn**

thân chương bốn

**Chương năm**

thân chương năm
"""
```

và thêm `build("bold", BOLD)` vào khối `if __name__ == "__main__":`.

Thêm vào `speckit-extension/scripts/tests/test_tiers.py`:

```python
def test_format_candidates_bat_doan_in_dam_ngan():
    cands = format_candidates(FIXTURES / "bold.docx")
    assert [c["text"] for c in cands] == [
        "Chương một", "Chương hai", "Chương ba", "Chương bốn", "Chương năm",
    ]
    assert all(c["bold"] for c in cands)


def test_detect_tier_docx_toan_doan_thuong_thi_can_llm():
    res = detect_tier(FIXTURES / "plain.docx")
    assert res["tier"] == 0
    assert res["needs_llm"] is True


def test_probe_tra_ve_candidates_khi_can_llm(tmp_path):
    import json
    import subprocess
    import sys
    script = Path(__file__).resolve().parents[1] / "brd_import.py"
    proc = subprocess.run(
        [sys.executable, str(script), "probe", str(FIXTURES / "bold.docx"),
         "--work", str(tmp_path / "w")],
        capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["needs_llm"] is True
    assert len(data["candidates"]) == 5


def test_probe_voi_outline_do_llm_quyet_thi_cat_duoc(tmp_path):
    import json
    import subprocess
    import sys
    script = Path(__file__).resolve().parents[1] / "brd_import.py"
    work = tmp_path / "w"
    subprocess.run([sys.executable, str(script), "probe", str(FIXTURES / "bold.docx"),
                    "--work", str(work)], capture_output=True, text=True)
    outline = work / "outline.json"
    outline.write_text(json.dumps(
        [{"index": i, "level": 1 if i % 2 == 0 else 2} for i in range(5)]),
        encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(script), "probe", str(FIXTURES / "bold.docx"),
         "--work", str(work), "--outline", str(outline)],
        capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["needs_llm"] is False
    assert data["tier"] == 6
    assert sum(lv["count"] for lv in data["levels"]) == 5
```

và thêm `format_candidates` vào dòng import ở đầu file:

```python
from brd.docx_probe import (
    detect_tier, format_candidates, numbered_titles, promotions_for, toc_titles,
)
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `python -m pytest speckit-extension/scripts/tests/test_tiers.py -q`
Kỳ vọng: FAIL — `ImportError: cannot import name 'format_candidates'`

- [ ] **Step 3: Cài đặt — heuristic định dạng**

Thêm vào cuối `speckit-extension/scripts/brd/docx_probe.py`:

```python
_BOLD_RE = re.compile(r"<w:b(?: [^>]*)?/>|<w:b(?: [^>]*)?>(?!<w:val=\"0\")")
_SZ_RE = re.compile(r"<w:sz w:val=\"(\d+)\"")


def _paragraphs_rich(docx):
    xml = _read(docx, "word/document.xml")
    out = []
    for i, m in enumerate(_PARA_RE.finditer(xml)):
        block = m.group(0)
        sizes = [int(s) for s in _SZ_RE.findall(block)]
        out.append({
            "index": i,
            "text": "".join(_TEXT_RE.findall(block)).strip(),
            "bold": bool(_BOLD_RE.search(block)),
            "size": max(sizes) if sizes else None,
        })
    return out


def format_candidates(docx):
    """Đoạn ngắn, in đậm hoặc cỡ chữ lớn hơn cỡ phổ biến nhất, không kết thúc bằng '.'."""
    paras = _paragraphs_rich(docx)
    sizes = collections.Counter(p["size"] for p in paras if p["size"])
    body_size = sizes.most_common(1)[0][0] if sizes else None
    out = []
    for p in paras:
        text = p["text"]
        if not text or len(text) >= 120 or text.endswith("."):
            continue
        bigger = body_size is not None and p["size"] is not None and p["size"] > body_size
        if p["bold"] or bigger:
            out.append({"index": p["index"], "text": text,
                        "bold": p["bold"], "size": p["size"]})
    return out


def size_tier(docx):
    """Bậc 5: cấp suy từ cỡ chữ giảm dần trong các ứng viên."""
    cands = [c for c in format_candidates(docx) if c["size"]]
    distinct = sorted({c["size"] for c in cands}, reverse=True)
    if len(distinct) < 2 or len(cands) < 5:
        return []
    rank = {s: i + 1 for i, s in enumerate(distinct)}
    return [(c["text"], rank[c["size"]]) for c in cands]
```

Sửa `detect_tier`: chèn ngay **trước** khối `return {"tier": 0, …}`:

```python
    sized = size_tier(docx)
    if sized:
        return {"tier": 5, "note": f"Suy từ cỡ chữ giảm dần, {len(sized)} mục",
                "style_levels": {}, "heading_count": len(sized), "needs_llm": False}
```

và sửa khối `tier: 0` để mang theo ứng viên:

```python
    return {
        "tier": 0,
        "note": "Bậc 1-5 đều mù: không Heading style, không style tự chế có outlineLvl, "
                "không mục lục, không đánh số liên tục, không phân tầng cỡ chữ",
        "style_levels": {}, "heading_count": 0, "needs_llm": True,
        "candidates": format_candidates(docx),
    }
```

Sửa `promotions_for` để nhận bậc 5 và quyết định của LLM:

```python
def promotions_for(docx, outline=None):
    """[{'text','level'}] nạp cho Lua filter.

    outline: [{'index','level'}] do LLM quyết (bậc 6) — chỉ số trỏ vào
    format_candidates(docx), KHÔNG phải chỉ số đoạn trong tài liệu.
    """
    if outline:
        cands = format_candidates(docx)
        return [{"text": cands[o["index"]]["text"], "level": o["level"]}
                for o in outline if 0 <= o["index"] < len(cands)]
    res = detect_tier(docx)
    if res["tier"] == 3:
        pairs = toc_titles(docx)
    elif res["tier"] == 4:
        pairs = numbered_titles(docx)
    elif res["tier"] == 5:
        pairs = size_tier(docx)
    else:
        return []
    return [{"text": t, "level": lv} for t, lv in pairs]
```

- [ ] **Step 4: Cài đặt — CLI nhận `--outline`**

Trong `speckit-extension/scripts/brd_import.py`, thay toàn bộ khối chọn nhánh convert trong `cmd_probe` bằng:

```python
    from brd.docx_probe import promotions_for

    outline = None
    if args.outline:
        outline = json.loads(Path(args.outline).read_text(encoding="utf-8"))

    if tier["needs_llm"] and not outline:
        result = {
            "tier": 0, "note": tier["note"], "needs_llm": True,
            "recommend_depth": None, "levels": [], "warnings": [],
            "candidates": tier.get("candidates", []),
            "source": {"file": docx.name, "sha256": _sha256(docx),
                       "pandoc": check_pandoc(), "path": str(docx.resolve())},
        }
        (work / "probe.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return

    promos = promotions_for(docx, outline=outline)
    if tier["tier"] == 1 and not promos:
        md_path = run_pandoc(docx, work)
    else:
        lua = Path(__file__).resolve().parent / "promote_headings.lua"
        md_path = run_pandoc(docx, work, lua_filter=lua,
                             metadata={"promotions": promos})
    effective_tier = 6 if outline else tier["tier"]
```

và trong `result` cuối `cmd_probe`, thay `"tier": tier["tier"]` bằng `"tier": effective_tier`,
`"note"` bằng `tier["note"] if not outline else "Ranh giới do LLM quyết từ ứng viên bậc 5"`.

Thêm tham số vào parser:

```python
    p.add_argument("--outline", default=None,
                   help="JSON [{index, level}] do LLM quyết khi bậc 1-5 mù")
```

- [ ] **Step 5: Chạy test, xác nhận đạt**

Chạy: `python -m pytest speckit-extension/scripts/tests -q`
Kỳ vọng: 49 passed

- [ ] **Step 6: Commit**

```bash
git add speckit-extension/scripts/brd/docx_probe.py speckit-extension/scripts/brd_import.py speckit-extension/scripts/tests/
git commit -m "feat(dft-speckit): dò cấu trúc bậc 5-6 (cỡ chữ, ứng viên cho LLM)"
```

---

### Task 10: Command `.md`, manifest extension, README, kiểm tra bản đóng gói

**Files:**
- Create: `speckit-extension/commands/brd-import.md`
- Modify: `speckit-extension/extension.yml` — thêm command, bump `0.0.5` → `0.1.0`
- Modify: `speckit-extension/README.md` — thêm mục command mới

**Interfaces:**
- Consumes: CLI `brd_import.py probe|split`
- Produces: command `speckit.dft-speckit.brd-import`

- [ ] **Step 1: Viết command**

Tạo `speckit-extension/commands/brd-import.md`:

````markdown
---
description: Bẻ một file BRD .docx lớn thành cây markdown nhỏ phản chiếu navigation pane của Word — mỗi màn hình một file, kèm manifest và kiểm chứng ghép ngược không mất một byte.
---

# Nhập BRD .docx thành cây markdown

BA giao một file BRD `.docx`. Nhiệm vụ: chuyển thành **cây markdown** dưới `docs/brd/`,
mỗi mục ở cấp đã chọn là **một file**, để `/speckit.specify` đọc trọn vẹn một màn mà
không phải đoán khoảng dòng. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: **script chép, bạn chỉ quyết ranh giới**. Bạn KHÔNG được viết lại,
tóm tắt, chuẩn hoá hay "làm đẹp" bất kỳ nội dung nào của tài liệu. Script là thứ duy nhất
ghi nội dung file markdown; việc của bạn là chạy script, đọc kết quả, hỏi người dùng
đúng chỗ cần quyết định, và báo cáo trung thực.

## User Input

`$ARGUMENTS`

Kỳ vọng: **đường dẫn tới một file `.docx`**. Trống, không tồn tại, hoặc không phải `.docx`
→ **hỏi lại**, KHÔNG tự đi tìm file trong repo.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/brd_import.py`.
Thư mục làm việc tạm: `.specify/tmp/brd-import/`.

### 1. Dò cấu trúc

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py probe "<đường-dẫn-docx>" \
  --work .specify/tmp/brd-import
```

Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp lỗi cho người dùng. Không tự chữa,
không thử lệnh khác.

### 2. Bậc 1–5 mù (`needs_llm: true`) — phán đoán ranh giới

`probe.json` trả về `candidates`: danh sách đoạn ứng viên, mỗi mục có `index` và `text`.

Nhiệm vụ của bạn: quyết **đoạn nào là tiêu đề mục, và ở cấp mấy**. Chỉ nhìn `text`,
`bold`, `size` — KHÔNG đọc thân bài, KHÔNG chép nội dung. Ghi kết quả ra
`.specify/tmp/brd-import/outline.json` dạng `[{"index": 0, "level": 1}, …]`:

- `level` bắt đầu từ 1, tăng dần theo độ sâu; cấp phải **liên tục** (có cấp 3 thì phải có cấp 2).
- Ứng viên KHÔNG phải tiêu đề thì **bỏ khỏi danh sách**, đừng gán cấp bừa.
- Không đủ căn cứ để phân cấp (mọi ứng viên trông như nhau) → **DỪNG**, báo người dùng
  rằng tài liệu không có tín hiệu cấu trúc nào và đề nghị BA áp Heading style rồi gửi lại.

Rồi chạy lại:

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py probe "<đường-dẫn-docx>" \
  --work .specify/tmp/brd-import --outline .specify/tmp/brd-import/outline.json
```

### 3. Chốt cấp cắt (interview)

Trình cho người dùng **bảng `levels`** từ `probe.json` — mỗi dòng: cấp, cấp Word gốc,
số mục, trung vị / nhỏ nhất / lớn nhất (ký tự). Rồi hỏi qua **AskUserQuestion**:
cắt ở cấp nào.

- Đánh `(Recommended)` cho `recommend_depth`, và **nêu thẳng con số trung vị làm căn cứ**
  ngay trong option (vd "cấp 5 — 54 mục, trung vị 23.808 ký tự, mọi mục 4k–76k").
- Đưa thêm 1–2 cấp lân cận làm option, kèm lý do vì sao kém hơn (vd "cấp 3 — 35 mục nhưng
  có mục 275k ký tự, lệch nhau quá xa").
- **Chờ phản hồi thật của người dùng.** Cấm tự tuyên bố người dùng đã đồng ý.
  Chưa có phản hồi → DỪNG, không chạy bước 4.

### 4. Cắt và kiểm chứng

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py split \
  --work .specify/tmp/brd-import --depth <cấp-đã-chọn> --dest docs/brd
```

- Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp. Script đã tự bảo đảm KHÔNG ghi gì
  ra đích khi kiểm chứng thất bại — đừng cố chạy lại với cấp khác để "cho qua".
- `docs/brd/` đã có `brd.manifest.yml` → script tự đổi đích sang `docs/brd.new/` và
  trả thêm khoá `diff`. Đây là **cố ý**: markdown là nguồn sự thật, BA có thể đã sửa tay.
  Trình bảng `diff` (thêm / mất / đổi) cho người dùng tự quyết cách hợp nhất.
  **KHÔNG tự merge, KHÔNG tự xoá `docs/brd/`.**

### 5. Báo cáo

Từ `report.json`, báo: đường dẫn đích, số file, số thư mục, cấp đã cắt, bậc dò đã dùng,
số ảnh, `roundtrip: OK`, và **liệt kê đầy đủ `warnings`** (file quá lớn, ảnh mồ côi,
trùng tiêu đề). Cảnh báo không được im lặng bỏ qua.

Nhắc bước tiếp: đọc `docs/brd/brd.manifest.yml` để biết màn nào nằm ở file nào.

## Sai lầm thường gặp

- **Tự viết lại / tóm tắt nội dung docx** → phá hợp đồng lõi. Script chép, bạn không chép.
- **Tự chọn cấp cắt rồi chạy luôn** → cấp cắt là quyết định của người dùng, phải hỏi thật.
- **Kiểm chứng fail rồi thử cấp khác cho qua** → che lỗi. Fail nghĩa là có bug, phải báo.
- **Tự merge `docs/brd.new/` vào `docs/brd/`** → xoá công BA đã sửa tay. Chỉ trình diff.
- **Bỏ qua `warnings` cho gọn báo cáo** → người dùng mất thông tin cần để quyết.
- **Gán cấp bừa cho ứng viên ở bước 2 để chạy tiếp** → cây sai, cắt sai. Không chắc thì DỪNG.
````

- [ ] **Step 2: Khai báo trong manifest**

Trong `speckit-extension/extension.yml`, sửa `version: "0.0.5"` thành `version: "0.1.0"`,
và thêm vào cuối `provides.commands`:

```yaml
    - name: "speckit.dft-speckit.brd-import"
      file: "commands/brd-import.md"
      description: "Bẻ một file BRD .docx lớn thành cây markdown nhỏ phản chiếu navigation pane của Word — mỗi mục ở cấp đã chọn là một file, kèm brd.manifest.yml, media/ và reference.docx. Dò cấu trúc 6 bậc (Heading style, style tự chế có outlineLvl, mục lục, đánh số gõ tay, cỡ chữ, LLM phán đoán); LLM chỉ quyết ranh giới, script chép nguyên văn. Kiểm chứng bằng ghép ngược byte-for-byte — lệch 1 byte là không ghi gì. Chạy lại khi đã có docs/brd/ thì xuất ra docs/brd.new/ kèm bảng khác biệt, không đè lên bản BA đã sửa."
```

- [ ] **Step 3: Cập nhật README**

Trong `speckit-extension/README.md`, thêm một mục cho `speckit.dft-speckit.brd-import`
theo đúng thể loại và giọng văn của các mục command đã có trong file (đọc file trước
khi thêm để khớp cấu trúc — mỗi mục thường có tên command, một đoạn mô tả, ví dụ dùng).
Ví dụ dùng:

```
/speckit.dft-speckit.brd-import refs/BRD-khach-hang.docx
```

- [ ] **Step 4: Chạy lại toàn bộ test**

Chạy: `python -m pytest speckit-extension/scripts/tests -q`
Kỳ vọng: 49 passed

- [ ] **Step 5: Kiểm bản đóng gói thật sự chứa script**

```bash
speckit-extension/build-zip.sh
unzip -l speckit-extension/dist/dft-speckit-0.1.0.zip | grep -E "brd_import|brd/|promote_headings|brd-import.md"
```

Kỳ vọng: liệt kê đủ `commands/brd-import.md`, `scripts/brd_import.py`,
`scripts/promote_headings.lua`, và cả 7 file trong `scripts/brd/`.
**Thiếu bất kỳ file nào → sửa `build-zip.sh`** rồi chạy lại (manifest `provides` chỉ khai
command/template, nó KHÔNG quyết định file nào được đóng gói).

Kỳ vọng phụ: zip **không** chứa `scripts/tests/` — nếu có thì thêm loại trừ vào
`build-zip.sh` giống cách nó đã loại `.venv`/`__pycache__`.

- [ ] **Step 6: Commit**

```bash
git add speckit-extension/commands/brd-import.md speckit-extension/extension.yml speckit-extension/README.md speckit-extension/build-zip.sh
git commit -m "feat(dft-speckit): command brd-import (0.1.0)"
```

---

## Self-Review

Đối chiếu kế hoạch với spec:

| Yêu cầu trong spec | Task |
|---|---|
| Command `speckit.dft-speckit.brd-import` | 10 |
| 3 lệnh con `probe` / `probe --outline` / `split` | 7, 9 |
| Luật chọn cấp cắt + bẫy không đơn điệu | 2 |
| Thang dò bậc 1–2 | 4 |
| Thang dò bậc 3–4 + Lua filter | 8 |
| Thang dò bậc 5–6 | 9 |
| Dừng khi mù cả 6 bậc | 9 (script), 10 (command) |
| Bố cục lồng, tiền tố số, `_index.md`, slug bỏ dấu | 1, 5 |
| Node gốc `BRD-0000` giữ phần trước heading đầu | 5 |
| Chuẩn hoá heading tương đối trong file | 5 |
| Frontmatter 3 khoá | 5 |
| `brd.manifest.yml` + `depth_map` | 5 |
| `reference.docx` rút gọn | 3 |
| Ghép ngược byte-for-byte, hoàn tác 3 phép biến đổi | 6 |
| Kiểm phụ: ảnh mồ côi, số node, file > 60k, trùng tiêu đề | 6 |
| Ghi qua thư mục tạm rồi rename | 7 |
| Chạy lại → `docs/brd.new/` + bảng diff | 7, 10 |
| Kiểm thử BRD thật / fixture bậc 2–4 / fixture âm | 7, 8, 9 |
| Đóng gói, bump `0.1.0`, xác nhận bằng `unzip -l` | 10 |

Ba điểm kế hoạch **bổ sung** so với spec, đều là lỗ hổng thật:

1. **Node gốc `BRD-0000`** — spec không nói phần trước heading đầu tiên (trang bìa + mục lục,
   6.340 ký tự) đi đâu. Không có nó thì phép ghép ngược không bao giờ khớp.
2. **`depth_map` trong manifest** — spec chỉ nói lưu `word_style` từng node, nhưng heading
   *bên trong* file lá không có node nào. Bảng `depth_map` toàn cục là thứ làm phép chuẩn hoá
   heading khả nghịch.
3. **Bậc 2 dùng đường khác bậc 3–5** — `-f docx+styles` đã tự cho style có `outlineLvl`
   thành `Header`, nên bậc 2 chỉ cần Lua filter gỡ vỏ `Div`, không cần danh sách `promotions`.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-08-07-brd-import.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
