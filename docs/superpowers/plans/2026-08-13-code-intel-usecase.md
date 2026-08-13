# Đợt 3B-2: thêm §12 "Kịch bản Use Case" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm mục §12 "Kịch bản Use Case" vào `intel-template.md`, hướng dẫn `code-intel.md` rút dữ liệu cho mục đó từ bằng chứng đã có (§2/§5/§6, không quét code lần hai), và thêm gate WARNING `check_section12_coverage` vào `intel_verify.py` để bắt màn hình thiếu use case / use case trỏ sai tên màn hình.

**Architecture:** §12 dùng khối lồng `### [Tên Use Case]` (như §3/§5 hiện có), không phải bảng phẳng như §11 — vì nội dung nhiều dòng (luồng sự kiện đánh số + nhánh phụ) không vừa một ô bảng. `intel_verify.py` cần một parser mới (`parse_section12`) quét dòng bullet-field trong khối lồng, khác hẳn `parse_section11`'s table-row parsing; gate mới liên kết với §2 qua field `Màn hình`, cùng khoá liên kết §11 đã dùng.

**Tech Stack:** Python 3.10 stdlib (`re`, `argparse`, `json`), pytest — giống hệt `intel_verify.py` hiện có, không thêm phụ thuộc.

## Global Constraints

- Đặt §12 **sau §11**, không đánh số lại mục cũ (`intel_verify.py` hardcode số mục qua `_section_body(text, N)`).
- Giữ nguyên cả 9 field của docx (Tên Use Case/Mức quan trọng/Người dùng/Loại UC/Người sử dụng và yêu cầu/Mô tả tóm tắt/Thời điểm sử dụng/Luồng sự kiện chuẩn/Luồng sự kiện nhỏ), đúng tên/thứ tự — không lược bớt.
- Ba field `Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng` **luôn ghi cố định "Chưa có thông tin"** ngay trong §12 — **không đưa xuống §8** (tránh thủng trần `check_section8_cap`).
- Field `Màn hình` của mỗi khối `###` phải khớp **nguyên văn** cột "Màn hình / endpoint" của §2 — cùng khoá liên kết §11 đã dùng, không đặt khoá thứ ba.
- Nguồn dữ liệu §12 là bằng chứng ĐÃ CÓ ở §2/§5/§6 — không quét code lần hai; bước rút §12 trong `code-intel.md` đặt SAU khi §2 và §5 đã ghi xong.
- Gate mới (`check_section12_coverage`) là **WARNING, không BLOCKING** — cùng lý do `check_section11_coverage`: §2 lẫn cả endpoint không có use case thật.
- **Không** thêm `12` vào danh sách section của `check_cite_quality` (hiện quét `(2,3,4,5,6,7,9,11)`) — §12 không dùng bảng nên `_table_data_rows` luôn trả rỗng cho nó, thêm vào sẽ tưởng "sạch" trong khi thực ra không quét được gì.
- Không đụng `speckit-extension/commands/srs-from-code.md`, `speckit-extension/scripts/srs_verify.py`, `speckit-extension/scripts/intel_tree.py`, và không đụng nội dung §11 đã có.

---

## Task 1: Thêm §12 vào `intel-template.md`

**Files:**
- Modify: `speckit-extension/templates/intel-template.md` (thêm vào cuối file, sau §11)

**Interfaces:**
- Produces: cấu trúc §12 mà Task 2 (`parse_section12`) và Task 3 (`code-intel.md`'s hướng dẫn rút dữ liệu) phải khớp chính xác — heading `## 12. Kịch bản Use Case`, khối con `### [Tên Use Case]`, field `- **Màn hình**: ...` (bullet, không nhất thiết là bullet đầu tiên trong khối).

Đây là file prompt/scaffold (không phải code) — không có bước TDD. Bước kiểm tra là đọc lại và đối chiếu với spec.

- [ ] **Step 1: Thêm §12 vào cuối `intel-template.md`**

Đọc file hiện tại — kết thúc ở dòng 168 với đoạn comment giải thích §11 (`... không phải ô trống — cùng tinh thần với nhãn [chính sách nghiệp vụ] ở §8.\n\n     Giữ nguyên kỷ luật ba dạng đang áp cho §2–§7, §9 — không nới riêng cho §11: đọc\n     thẳng từ khai báo control → ghi bình thường kèm cite; suy đoán → đánh dấu (suy\n     đoán); không có căn cứ → không ghi, đưa xuống §8. -->`). Thêm nội dung sau vào cuối file (nối tiếp ngay sau dòng cuối hiện có, giữ nguyên một dòng trống ngăn cách):

```markdown

## 12. Kịch bản Use Case

### [Tên Use Case]

- **Màn hình**: [tên màn hình đúng như §2]
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: [vai trò, từ §6 hoặc suy từ §2]
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: [câu tóm tắt mục đích sử dụng]
- **Mô tả tóm tắt**: [đoạn văn tóm lược toàn luồng]
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. [bước] — [file:dòng]
2. [bước] — [file:dòng]

**Luồng sự kiện nhỏ**:
- S-1: [tên nhánh] — [file:dòng]
  1. [bước]
  2. [bước]

<!-- Field `Màn hình` PHẢI khớp nguyên văn cột "Màn hình / endpoint" của §2 — cùng khoá
     liên kết §11 đã dùng, dùng bởi một đợt sau để nối use case với màn hình. Sai một ký
     tự là mất liên kết.

     Giữ nguyên cả 9 field theo đúng tên/thứ tự của tài liệu ban hành, không lược bớt.
     Ba field `Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng` là phân loại nghiệp vụ
     thuần — không có căn cứ code nào trả lời được dù tìm kỹ tới đâu. Đây KHÔNG phải
     "chưa tìm ra" (không đưa xuống §8), mà là "cấu trúc không thể tìm ra" — luôn ghi cố
     định "Chưa có thông tin" ngay tại đây. Đưa ba field này xuống §8 sẽ cộng thêm 3 mục
     "vô nghĩa" cho MỖI use case vào trần câu hỏi (`check_section8_cap`), dễ đẩy unit
     nhiều use case vượt trần chỉ vì ba field không bao giờ trả lời được.

     Các field còn lại (`Người dùng`, `Người sử dụng và yêu cầu`, `Mô tả tóm tắt`,
     `Luồng sự kiện chuẩn`, `Luồng sự kiện nhỏ`) áp đúng kỷ luật ba dạng đang dùng cho
     §2–§7, §9, §11: đọc thẳng → ghi kèm cite; suy đoán → đánh dấu (suy đoán); không căn
     cứ → không ghi field đó (hoặc lược cả use case nếu không còn gì để viết), đưa câu
     hỏi xuống §8 với nhãn [không suy được từ code].

     KHÔNG quét code lần hai để rút mục này — tái dùng đúng bằng chứng đã thu ở §2 (tên
     màn hình), §5 (luồng nghiệp vụ, viết lại theo khuôn đánh số/nhánh S-n của Use Case),
     và §6 (vai trò phân quyền) nếu có dòng khớp màn hình này. §5 không có luồng nào ứng
     với màn hình này → không viết được `Luồng sự kiện chuẩn` có căn cứ, đưa xuống §8. -->
```

- [ ] **Step 2: Đọc lại toàn văn, xác nhận đúng vị trí và không đụng §1–§11**

Run:
```bash
grep -n "^## " speckit-extension/templates/intel-template.md
```
Expected: đúng 12 dòng, từ `## 1. Phủ chức năng` tới `## 12. Kịch bản Use Case`, thứ tự số tăng dần liên tục, không dòng nào bị đổi số so với trước khi sửa (§1–§11 giữ nguyên văn bản, đối chiếu bằng mắt với bản gốc nếu cần).

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/templates/intel-template.md
git commit -m "feat(code-intel): thêm §12 Kịch bản Use Case vào intel-template.md (đợt 3B-2)"
```

---

## Task 2: `intel_verify.py` — `parse_section12` + `check_section12_coverage`

**Files:**
- Modify: `speckit-extension/scripts/intel_verify.py`
- Modify: `speckit-extension/scripts/tests/test_intel_verify.py`

**Interfaces:**
- Consumes: `_section_body(text, number, strip=True)`, `_table_data_rows(body)`, `_strip_backtick(s)` (đã có, không sửa — xem `speckit-extension/scripts/intel_verify.py` hiện tại, các hàm này được `parse_section11`/`check_section11_coverage` dùng theo đúng khuôn sẽ tái dùng ở đây).
- Produces: `parse_section12(text: str) -> list[dict]` — trả `[{"use_case": <tên khối ###>, "man_hinh": <giá trị field Màn hình>}, ...]`.
- Produces: `check_section12_coverage(text: str) -> list[dict]` — trả danh sách warning dict `{"loai": ..., "thong_diep": ...}`, hai loại: `"man-hinh-thieu-usecase"` và `"man-hinh-o-muc-12-khong-khop-muc-2"`.
- Produces: `verify()` gọi thêm `warnings.extend(check_section12_coverage(text))`.

- [ ] **Step 1: Viết test thất bại cho `parse_section12`/`check_section12_coverage`**

Thêm vào cuối `speckit-extension/scripts/tests/test_intel_verify.py`:

```python
INTEL_WITH_12 = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **Màn hình**: Đăng nhập
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để đăng nhập vào hệ thống.
- **Mô tả tóm tắt**: Người dùng nhập tài khoản, hệ thống xác thực và cấp phiên đăng nhập.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập tài khoản và mật khẩu — src/auth/login.ts:10
2. Hệ thống xác thực và cấp phiên — src/auth/login.ts:15

**Luồng sự kiện nhỏ**:
- S-1: Sai mật khẩu — src/auth/login.ts:22
  1. Hệ thống hiển thị lỗi "Email hoặc mật khẩu không đúng"

### Quên mật khẩu

- **Màn hình**: Quên mật khẩu
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để khôi phục mật khẩu.
- **Mô tả tóm tắt**: Người dùng yêu cầu đặt lại mật khẩu qua email.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập email — src/auth/reset.ts:5
2. Hệ thống gửi email đặt lại mật khẩu — src/auth/reset.ts:9
"""


def test_parse_section12_reads_correct_screens():
    r = iv.parse_section12(INTEL_WITH_12)
    assert r == [
        {"use_case": "Đăng nhập", "man_hinh": "Đăng nhập"},
        {"use_case": "Quên mật khẩu", "man_hinh": "Quên mật khẩu"},
    ]


def test_parse_section12_does_not_assume_man_hinh_is_first_bullet():
    text = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **Mức quan trọng**: Chưa có thông tin
- **Màn hình**: Đăng nhập
- **Người dùng**: Người dùng hệ thống
"""
    r = iv.parse_section12(text)
    assert r == [{"use_case": "Đăng nhập", "man_hinh": "Đăng nhập"}]


def test_section12_no_warning_when_all_screens_covered():
    r = iv.verify(INTEL_WITH_12, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-usecase" for w in r["warnings"])


def test_section12_warns_when_screen_missing_usecase():
    # INTEL_OK không có §12 nào cả -> cả 2 màn hình đều thiếu.
    r = iv.verify(INTEL_OK, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-usecase")
    assert "Đăng nhập" in w["thong_diep"] and "Quên mật khẩu" in w["thong_diep"]


def test_section12_partial_coverage_warns_only_for_missing_screen():
    text = INTEL_OK + """
## 12. Kịch bản Use Case

### Đăng nhập

- **Màn hình**: Đăng nhập
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Người dùng hệ thống
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để đăng nhập vào hệ thống.
- **Mô tả tóm tắt**: Người dùng nhập tài khoản, hệ thống xác thực.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập tài khoản và mật khẩu — src/auth/login.ts:10
"""
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-usecase")
    assert "Quên mật khẩu" in w["thong_diep"]
    assert "Đăng nhập" not in w["thong_diep"]


def test_section12_warns_on_unknown_screen_name():
    text = INTEL_WITH_12 + """
### Màn hình lạ

- **Màn hình**: Man hinh la
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Chưa có thông tin
- **Mô tả tóm tắt**: Không tồn tại ở §2.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Bước lạ — src/x.ts:1
"""
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-o-muc-12-khong-khop-muc-2")
    assert "Man hinh la" in w["thong_diep"]


def test_section12_absent_entirely_does_not_crash():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert not any(w["loai"] == "man-hinh-o-muc-12-khong-khop-muc-2" for w in r["warnings"])


def test_section12_backtick_wrapped_screen_name_still_matches_section2():
    # strip_noise xoá SẠCH nội dung trong cặp backtick — nếu §2 và §12 cùng bọc tên
    # màn hình trong backtick, cả hai phải vẫn khớp nhau (cùng cơ chế đã kiểm ở §11).
    text = (INTEL_OK
            .replace("| Đăng nhập | /login | src/auth/login.ts:10 | FN-01-01 |",
                     "| `POST /api/orders` | /login | src/auth/login.ts:10 | FN-01-01 |")
            + """
## 12. Kịch bản Use Case

### Đặt hàng

- **Màn hình**: `POST /api/orders`
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Chưa có thông tin
- **Mô tả tóm tắt**: Gọi API tạo đơn hàng.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Client gọi API — src/orders.ts:1

### Quên mật khẩu

- **Màn hình**: Quên mật khẩu
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Chưa có thông tin
- **Mô tả tóm tắt**: Khôi phục mật khẩu.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập email — src/auth/reset.ts:5
""")
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-usecase" for w in r["warnings"])
    assert not any(w["loai"] == "man-hinh-o-muc-12-khong-khop-muc-2" for w in r["warnings"])


def test_chua_co_thong_tin_is_not_a_placeholder():
    # "Chưa có thông tin" không có ngoặc vuông — không được bị bắt là placeholder
    # chưa điền (rủi ro đã ghi trong spec §12).
    r = iv.verify(INTEL_WITH_12, EXPECTED)
    assert r["blocking"] == []
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v -k "section12 or chua_co_thong_tin"`
(dùng `/c/Python/Python310/python.exe -m pytest ...` nếu `python`/`python3` không có trên PATH)
Expected: FAIL — `AttributeError: module 'intel_verify' has no attribute 'parse_section12'` (hàm chưa tồn tại).

- [ ] **Step 3: Thêm `parse_section12` và `check_section12_coverage` vào `intel_verify.py`**

Trong `speckit-extension/scripts/intel_verify.py`, ngay sau hàm `check_section11_coverage` (kết thúc ở dòng `return out` trước dòng `def verify(...)`), thêm hai regex ở đầu file cùng khối với các regex hiện có (ngay sau dòng `LABEL_RE = re.compile(...)`, trước `KNOWN_LABEL_RE`), rồi hai hàm mới:

```python
SECTION12_HEADING_RE = re.compile(r"^###\s+(.+)$")
MAN_HINH_FIELD_RE = re.compile(r"^-\s+\*\*Màn hình\*\*:\s*(.+)$")
```

```python
def parse_section12(text: str) -> list[dict]:
    """§12 'Kịch bản Use Case' → list các {"use_case":.., "man_hinh":..}. Khối lồng
    ### KHÔNG phải bảng — không dùng _table_rows/_table_data_rows như §11, mà quét
    từng dòng trong _section_body(text, 12, strip=False) tìm heading ### (tên use
    case) và dòng field '- **Màn hình**: ...' BẤT KỂ VỊ TRÍ trong khối (không giả
    định field Màn hình luôn là bullet đầu tiên — khác §11 dùng cột cố định).
    strip=False + _strip_backtick: cùng lý do đã ghi ở _section_body/parse_section11,
    giữ nguyên nội dung bọc backtick để so khớp §2 đúng."""
    out = []
    current_name = None
    for line in _section_body(text, 12, strip=False).splitlines():
        h = SECTION12_HEADING_RE.match(line.strip())
        if h:
            current_name = h.group(1).strip()
            continue
        m = MAN_HINH_FIELD_RE.match(line.strip())
        if m and current_name is not None:
            out.append({"use_case": current_name, "man_hinh": _strip_backtick(m.group(1))})
    return out


def check_section12_coverage(text: str) -> list[dict]:
    """§12 liên kết với §2 qua field 'Màn hình' (chuỗi tên, không phải FN-ID) — cùng
    khoá liên kết §11 đã dùng. WARNING, không BLOCKING: cùng lý do
    check_section11_coverage — §2 lẫn cả endpoint không có UI/use case thật, chặn
    cứng sẽ chặn oan nhóm đó."""
    screens_2 = {_strip_backtick(row[0])
                 for row in _table_data_rows(_section_body(text, 2, strip=False))
                 if row and row[0]}
    items_12 = parse_section12(text)
    screens_12 = {i["man_hinh"] for i in items_12}

    out = []
    missing = screens_2 - screens_12
    if missing:
        out.append({"loai": "man-hinh-thieu-usecase",
                    "thong_diep": "§2 có màn hình chưa có use case nào ở §12: "
                                   + ", ".join(sorted(missing))})
    unknown = screens_12 - screens_2
    if unknown:
        out.append({"loai": "man-hinh-o-muc-12-khong-khop-muc-2",
                    "thong_diep": "§12 có tên màn hình không khớp §2 (có thể gõ sai): "
                                   + ", ".join(sorted(unknown))})
    return out
```

Trong hàm `verify()`, ngay sau dòng `warnings.extend(check_section11_coverage(text))`, thêm:

```python
    warnings.extend(check_section12_coverage(text))
```

- [ ] **Step 4: Chạy lại test, xác nhận toàn bộ pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v`
Expected: PASS toàn bộ (tổng số test cũ + 9 test mới).

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_verify.py speckit-extension/scripts/tests/test_intel_verify.py
git commit -m "feat(code-intel): parse_section12 + check_section12_coverage trong intel_verify.py (đợt 3B-2)"
```

---

## Task 3: Hướng dẫn rút §12 trong `code-intel.md`

**Files:**
- Modify: `speckit-extension/commands/code-intel.md`

**Interfaces:**
- Consumes: cấu trúc §12 từ Task 1, `check_section12_coverage` từ Task 2 (bước 9 "Verify" của `code-intel.md` đã gọi `intel_verify.py` không đổi — gate mới tự động chạy theo, không cần sửa lệnh CLI).

Đây là file prompt/instruction — không có bước TDD. Bước kiểm tra là đọc lại và chạy thử `intel_verify.py` trên một `intel.md` mẫu có §12.

- [ ] **Step 1: Thêm đoạn hướng dẫn §12 vào cuối Bước 5 "Ghi theo kỷ luật ba dạng"**

Trong `speckit-extension/commands/code-intel.md`, Bước 5 kết thúc bằng đoạn hướng dẫn §11 (bắt đầu `**Điều khiển giao diện (§11)** — sau khi §2 đã có đủ tên màn hình + cite điểm vào, ...` và kết thúc `... nếu một màn hình ở §2 không có dòng §11 nào (kể cả dòng không-có-UI), hoặc nếu §11 có tên màn hình không khớp §2.`). Thêm đoạn sau ngay sau đó (trước dòng `### 6. Ghi phát hiện đáng chú ý...`):

```markdown

**Kịch bản Use Case (§12)** — sau khi §2 và §5 đã ghi xong (mục này phụ thuộc cả hai),
với mỗi màn hình đã có ở §2: dựng một khối `### [Tên Use Case]` trong §12, KHÔNG quét
code lần hai — tái dùng đúng bằng chứng đã thu:

- **`Màn hình`**: lấy nguyên văn từ cột "Màn hình / endpoint" của §2 — đây là khoá liên
  kết, phải khớp chính xác.
- **`Người dùng`**: suy từ §6 (bảng Phân quyền, cột Vai trò) nếu có dòng khớp màn hình
  này; không có → suy từ đối tượng dùng màn hình đó ở §2, đánh dấu `(suy đoán)`.
- **`Người sử dụng và yêu cầu`**, **`Mô tả tóm tắt`**: viết từ chính bằng chứng của §5
  (mô tả luồng) + §2 (tên màn hình) — một câu/đoạn tóm gọn, cite trỏ về cùng `file:dòng`
  đã dùng ở §5 cho luồng tương ứng.
- **`Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`**: viết lại đúng bằng chứng của §5 theo
  khuôn đánh số/nhánh `S-n` của Use Case, KHÔNG suy luận bước mới ngoài những gì §5 đã
  có. §5 không có luồng nào ứng với màn hình này → không viết được `Luồng sự kiện chuẩn`
  có căn cứ, đưa xuống §8 với nhãn `[không suy được từ code]`.
- **`Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng`**: LUÔN ghi cố định "Chưa có thông
  tin" — đây là phân loại nghiệp vụ thuần, không có căn cứ code nào trả lời được.
  **Không đưa ba field này xuống §8** — khác kỷ luật ba dạng đang áp cho các field còn
  lại, vì đây không phải "chưa tìm ra" mà là "cấu trúc không thể tìm ra"; đưa xuống §8
  sẽ cộng thêm 3 câu hỏi vô nghĩa cho MỖI use case vào trần `§8`.

Màn hình/điểm vào ở §2 thật sự không có use case nào ứng với nó (endpoint kỹ thuật thuần
— webhook nội bộ, health-check, cron trigger) → không bắt buộc phải có khối `###` cho nó
(khác §11 — §12 không có dòng giải trình `không-có-UI` riêng); `intel_verify.py` ở bước
9 chỉ cảnh báo (WARNING) chứ không chặn nếu bỏ sót, người soát tự quyết có bổ sung hay
không.
```

- [ ] **Step 2: Đọc lại toàn văn, đối chiếu**

Đọc lại `speckit-extension/commands/code-intel.md`, xác nhận đoạn mới nằm đúng trong Bước
5 (không tạo bước số mới), không đụng nội dung §11 liền trước, và văn phong khớp phần
còn lại của file (tiếng Việt, `**bold**` cho thuật ngữ, `code` cho tên field/mục).

Kiểm bằng lệnh:
```bash
grep -n "^### " speckit-extension/commands/code-intel.md
```
Expected: vẫn đúng 10 dòng `### 1.` tới `### 10.` như trước khi sửa — không bước số mới
nào được thêm.

- [ ] **Step 3: Chạy thử `intel_verify.py` trên fixture có §12, xác nhận gate mới hoạt động**

```bash
mkdir -p /tmp/usecase-smoke
cat > /tmp/usecase-smoke/functions.json <<'EOF'
{"functions": [{"id": "FN-01", "name": "Xac thuc", "description": "", "children": [
  {"id": "FN-01-01", "name": "Dang nhap", "description": "", "children": []},
  {"id": "FN-01-02", "name": "Quen mat khau", "description": "", "children": []}]}]}
EOF
cat > /tmp/usecase-smoke/intel.md <<'EOF'
# Code intel — Xac thuc

**Cập nhật**: 2026-08-13
**Phủ chức năng**: FN-01-01, FN-01-02

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| FN-01-01 | Dang nhap | src/auth/login.ts:10 | — |
| FN-01-02 | Quen mat khau | src/auth/reset.ts:5 | — |

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| Dang nhap | /login | src/auth/login.ts:10 | FN-01-01 |
| Quen mat khau | /forgot | src/auth/reset.ts:5 | FN-01-02 |

## 3. Thực thể và trường dữ liệu

Không có.

## 4. Kiểm tra hợp lệ và quy tắc nghiệp vụ

Không có.

## 5. Luồng nghiệp vụ

### Dang nhap

Người dùng nhập tài khoản, hệ thống xác thực.

- **Nguồn**: src/auth/login.ts:10

## 6. Phân quyền

Không có.

## 7. Tích hợp ngoài, tác vụ nền, sự kiện

Không có.

## 8. Không suy được từ code — câu hỏi cho người

Không có.

## 9. Thông báo hiển thị

Không có.

## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật

Không có.

## 11. Điều khiển giao diện

Không có.

## 12. Kịch bản Use Case

### Dang nhap

- **Màn hình**: Dang nhap
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: Chưa có thông tin
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: Dùng để đăng nhập.
- **Mô tả tóm tắt**: Người dùng nhập tài khoản, hệ thống xác thực.
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. Người dùng nhập tài khoản — src/auth/login.ts:10
EOF
cd /tmp/usecase-smoke
python /e/agent-skills/speckit-extension/scripts/intel_verify.py intel.md \
  --functions functions.json --root FN-01
cd /e/agent-skills
rm -rf /tmp/usecase-smoke
```

Expected: JSON có `"blocking": []`; `warnings` chứa đúng một mục `"loai":
"man-hinh-thieu-usecase"` nêu `Quen mat khau` (màn hình đó không có khối `###` nào ở
§12) — bằng chứng gate mới thực sự chạy trên một `intel.md` thật, không chỉ qua test đơn
vị.

- [ ] **Step 4: Commit**

```bash
git add speckit-extension/commands/code-intel.md
git commit -m "feat(code-intel): hướng dẫn rút §12 Kịch bản Use Case trong code-intel.md (đợt 3B-2)"
```
