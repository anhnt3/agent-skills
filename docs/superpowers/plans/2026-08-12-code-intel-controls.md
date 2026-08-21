# `code-intel`: rút điều khiển giao diện (§11) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm mục §11 "Điều khiển giao diện" vào `intel.md` — code-intel quét control thật
(textbox/button/…) từ code UI, liên kết với §2 qua tên màn hình, có gate WARNING kiểm phủ.

**Architecture:** Thuần thêm mục, không đụng cơ chế unit/đường dẫn (`intel_tree.py`) hay
`srs-*`. `intel-template.md` thêm §11 ở cuối (không đánh số lại — `intel_verify.py`
hardcode số mục). `intel_verify.py` thêm một cặp hàm `parse_section11`/
`check_section11_coverage`, tái dùng `_table_data_rows` đã có sẵn (xử lý đúng nhiều-bảng,
đã qua 1 vòng fix ở đợt trước). `code-intel.md` thêm hướng dẫn quét control vào Step 5 đã
có, không tạo bước đánh số mới (tránh renumbering toàn bộ tham chiếu chéo `bước N` rải
khắp file).

**Tech Stack:** Python 3 (stdlib), pytest, Markdown.

**Spec:** `docs/superpowers/specs/2026-08-12-code-intel-controls-design.md`

## Global Constraints

- Nội dung tài liệu, thông điệp lỗi, comment code: **tiếng Việt**. Tên hàm: **tiếng Anh**.
- **Không đánh số lại** bất kỳ mục `## N.` nào đã có trong `intel-template.md` (§1–§10) —
  `intel_verify.py` hardcode số mục qua `_section_body(text, N)`.
- **Không thêm bước đánh số mới** vào `code-intel.md` (giữ nguyên 10 bước hiện có) — file
  có rất nhiều tham chiếu chéo dạng "bước N" giữa các phần, renumbering rủi ro cao so với
  lợi ích.
- Gate mới ở `intel_verify.py` cho §11 là **WARNING**, không BLOCKING (xem spec §4 — tránh
  lặp lỗi vòng-lặp-không-thoát mà `check_not_found_ratio` từng mắc phải với unit nhỏ).
- Cột `Loại` ở §11 tái dùng nguyên bộ từ vựng đã có ở `srs-template.md` §II.4: `Textbox`,
  `Passwordbox`, `Checkbox`, `Dropdown`, `Datepicker`, `Button`, `Link`,
  `Label (chỉ xem)`, cộng giá trị đặc biệt `không-có-UI`.
- Không đụng `srs-*`, không đụng `intel_tree.py` trong plan này.
- Chạy test từ gốc repo: `python -m pytest speckit-extension/scripts/tests/<file> -v`.

## File Structure

| File | Trách nhiệm |
|---|---|
| `speckit-extension/templates/intel-template.md` | **Sửa.** Thêm §11 vào cuối. |
| `speckit-extension/scripts/intel_verify.py` | **Sửa.** Thêm `parse_section11`, `check_section11_coverage`, gắn vào `verify()`. |
| `speckit-extension/scripts/tests/test_intel_verify.py` | **Sửa.** Thêm test cho §11. |
| `speckit-extension/commands/code-intel.md` | **Sửa.** Thêm hướng dẫn quét control vào Step 5, thêm 2 mục "Sai lầm thường gặp". |
| `speckit-extension/extension.yml` | Bump version, cập nhật 2 `description`. |

---

### Task 1: Thêm §11 vào `intel-template.md`

**Files:**
- Modify: `speckit-extension/templates/intel-template.md` (thêm vào cuối, sau §10)

**Interfaces:**
- Consumes: cú pháp/quy ước đã cố định ở đợt trước (`_(chưa có)_` cho §8, nhãn `[...]`
  giữ ngoặc vuông, `đang chờ` không ngoặc vuông ở §10) — không đụng các mục đó.
- Produces: cấu trúc bảng §11 mà Task 2 (`intel_verify.py`) và Task 3 (`code-intel.md`)
  đều tham chiếu: cột thứ nhất `Màn hình`, cột thứ ba `Loại`.

- [ ] **Step 1: Thêm §11 vào cuối file**

Mở `speckit-extension/templates/intel-template.md`. File hiện kết thúc bằng đoạn comment
HTML giải thích §10 (dòng 118–143), sau đó là dấu đóng comment `-->`. Thêm nội dung sau
vào **cuối file**, ngay sau dòng `-->` cuối cùng:

````markdown

## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| [tên màn hình đúng như §2] | [nhãn hiển thị] | [Textbox/Button/…] | [hành vi, ràng buộc] | [file:dòng] |

<!-- Cột `Màn hình` PHẢI khớp nguyên văn cột "Màn hình / endpoint" của §2 — đây là khoá
     liên kết duy nhất giữa hai mục, dùng bởi srs-from-code (đợt sau) để lọc ra bảng điều
     khiển cho từng màn hình. Sai một ký tự là mất liên kết.

     Cột `Loại` dùng lại đúng bộ từ vựng "Loại trường điều khiển" đã có ở srs-template.md
     §II.4 (Textbox, Passwordbox, Checkbox, Dropdown, Datepicker, Button, Link,
     Label (chỉ xem)) — không đặt bộ mới. Loại thật không nằm trong danh sách đó thì ghi
     tên loại đó nguyên văn, đợt sau sẽ bổ sung vào bảng quy ước.

     Màn hình/điểm vào ở §2 thật sự không có giao diện (endpoint REST thuần, job nền,
     CLI, message consumer) → ghi ĐÚNG MỘT dòng với Loại = không-có-UI, cột Mô tả nêu rõ
     lý do cụ thể (loại điểm vào là gì), kèm cite. Đây là giải trình có căn cứ, không
     phải ô trống — cùng tinh thần với nhãn [chính sách nghiệp vụ] ở §8.

     Giữ nguyên kỷ luật ba dạng đang áp cho §2–§7, §9 — không nới riêng cho §11: đọc
     thẳng từ khai báo control → ghi bình thường kèm cite; suy đoán → đánh dấu (suy
     đoán); không có căn cứ → không ghi, đưa xuống §8. -->
````

- [ ] **Step 2: Kiểm bằng mắt — không đánh số lại mục nào khác**

Run: `grep -n "^## " speckit-extension/templates/intel-template.md`
Expected: đúng 11 dòng, từ `## 1. Phủ chức năng` tới `## 11. Điều khiển giao diện`, các
mục 1–10 giữ nguyên số và tiêu đề như trước khi sửa (không dòng nào đổi số).

- [ ] **Step 3: Commit**

```bash
git add speckit-extension/templates/intel-template.md
git commit -m "feat(code-intel): thêm §11 Điều khiển giao diện vào intel-template"
```

---

### Task 2: `check_section11_coverage` trong `intel_verify.py`

**Files:**
- Modify: `speckit-extension/scripts/intel_verify.py`
- Test: `speckit-extension/scripts/tests/test_intel_verify.py`

**Interfaces:**
- Consumes: `_table_data_rows`, `_section_body` (đã có sẵn trong file, không đổi)
- Produces:
  - `parse_section11(text: str) -> list[dict]` — mỗi phần tử `{"man_hinh": str, "loai": str}`
  - `check_section11_coverage(text: str) -> list[dict]` — WARNING, không nhận `expected`
    (khác các `check_*` khác — §11 liên kết qua TÊN màn hình, không qua FN-ID)
  - `verify()` sửa lại để gọi thêm `check_section11_coverage`, đổ vào `warnings`

- [ ] **Step 1: Viết test thất bại**

Mở `speckit-extension/scripts/tests/test_intel_verify.py`. File đã có sẵn hằng số
`EXPECTED` và `INTEL_OK` (fixture `intel.md` hợp lệ, 2 FN "Đăng nhập"/"Quên mật khẩu",
kết thúc bằng `## 10. Phát hiện cần người quyết định...\n\nKhông có.\n"""`). Thêm vào
**cuối file** (dùng lại `EXPECTED`/`INTEL_OK`, không định nghĩa lại):

```python
INTEL_WITH_11 = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc, tối đa 50 ký tự | src/auth/login.ts:24 |
| Đăng nhập | Mật khẩu | Passwordbox | bắt buộc | src/auth/login.ts:31 |
| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |
"""


def test_section11_no_warning_when_all_screens_covered():
    r = iv.verify(INTEL_WITH_11, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-dieu-khien" for w in r["warnings"])


def test_section11_warns_when_screen_missing_controls():
    # INTEL_OK không có §11 nào cả -> cả 2 màn hình đều thiếu.
    r = iv.verify(INTEL_OK, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-dieu-khien")
    assert "Đăng nhập" in w["thong_diep"] and "Quên mật khẩu" in w["thong_diep"]


def test_section11_partial_coverage_warns_only_for_missing_screen():
    text = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc | src/auth/login.ts:24 |
"""
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-thieu-dieu-khien")
    assert "Quên mật khẩu" in w["thong_diep"]
    assert "Đăng nhập" not in w["thong_diep"]


def test_section11_khong_co_ui_counts_as_covered():
    text = INTEL_OK + """
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Đăng nhập | Tên đăng nhập | Textbox | bắt buộc | src/auth/login.ts:24 |
| Quên mật khẩu | — | không-có-UI | Endpoint REST thuần, không có view | src/auth/reset.ts:5 |
"""
    r = iv.verify(text, EXPECTED)
    assert not any(w["loai"] == "man-hinh-thieu-dieu-khien" for w in r["warnings"])


def test_section11_warns_on_unknown_screen_name():
    text = INTEL_WITH_11.replace(
        "| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |",
        "| Quên mật khẩu | Email | Textbox | bắt buộc, định dạng email | src/auth/reset.ts:12 |\n"
        "| Man hinh la | Nut la | Button | khong ton tai o muc 2 | src/x.ts:1 |")
    r = iv.verify(text, EXPECTED)
    w = next(w for w in r["warnings"] if w["loai"] == "man-hinh-o-muc-11-khong-khop-muc-2")
    assert "Man hinh la" in w["thong_diep"]


def test_section11_absent_entirely_does_not_crash():
    r = iv.verify(INTEL_OK, EXPECTED)
    assert not any(w["loai"] == "man-hinh-o-muc-11-khong-khop-muc-2" for w in r["warnings"])
```

- [ ] **Step 2: Chạy test để chắc chắn nó fail**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v -k section11`
Expected: FAIL — `AttributeError: module 'intel_verify' has no attribute 'parse_section11'`

- [ ] **Step 3: Cài đặt**

Thêm vào `speckit-extension/scripts/intel_verify.py`, ngay sau hàm `check_section2_anchor`
(trước hàm `verify`):

```python
def parse_section11(text: str) -> list[dict]:
    """§11 'Điều khiển giao diện' → list các {"man_hinh":.., "loai":..}. Dùng
    `_table_data_rows` (không phải `_table_rows`) để tự động bỏ dòng tiêu đề/
    phân cách — cột 'Màn hình' là chuỗi tự do, không có mẫu tất định như
    FN-ID (§1) hay số thứ tự (§10) để lọc theo nội dung."""
    out = []
    for row in _table_data_rows(_section_body(text, 11)):
        if len(row) >= 3 and row[0]:
            out.append({"man_hinh": row[0], "loai": row[2]})
    return out


def check_section11_coverage(text: str) -> list[dict]:
    """§11 liên kết với §2 qua cột 'Màn hình' (chuỗi tên, không phải FN-ID) —
    WARNING, không BLOCKING: §2 lẫn cả endpoint/job không có UI, chặn cứng sẽ
    chặn oan nhóm đó (đúng loại lỗi vòng-lặp-không-thoát mà
    check_not_found_ratio từng mắc phải với unit nhỏ)."""
    screens_2 = {row[0] for row in _table_data_rows(_section_body(text, 2)) if row and row[0]}
    items_11 = parse_section11(text)
    screens_11 = {i["man_hinh"] for i in items_11}

    out = []
    missing = screens_2 - screens_11
    if missing:
        out.append({"loai": "man-hinh-thieu-dieu-khien",
                    "thong_diep": "§2 có màn hình chưa có dòng nào ở §11 (kể cả "
                                   "dòng 'không-có-UI' giải trình): "
                                   + ", ".join(sorted(missing))})
    unknown = screens_11 - screens_2
    if unknown:
        out.append({"loai": "man-hinh-o-muc-11-khong-khop-muc-2",
                    "thong_diep": "§11 có tên màn hình không khớp §2 (có thể gõ sai): "
                                   + ", ".join(sorted(unknown))})
    return out
```

Sửa hàm `verify` — thêm một dòng vào cuối khối `warnings.extend(...)` (giữ nguyên mọi
dòng khác của hàm):

```python
    warnings.extend(check_cite_quality(text))
    warnings.extend(check_section2_anchor(text, expected))
    warnings.extend(check_section11_coverage(text))
```

- [ ] **Step 4: Chạy test để xác nhận pass**

Run: `python -m pytest speckit-extension/scripts/tests/test_intel_verify.py -v`
Expected: PASS — toàn bộ test cũ (24) + 6 test mới = 30 passed

- [ ] **Step 5: Commit**

```bash
git add speckit-extension/scripts/intel_verify.py speckit-extension/scripts/tests/test_intel_verify.py
git commit -m "feat(code-intel): gate WARNING kiểm phủ §11 theo tên màn hình ở §2"
```

---

### Task 3: Hướng dẫn quét control trong `code-intel.md`

**Files:**
- Modify: `speckit-extension/commands/code-intel.md`

**Interfaces:**
- Consumes: cấu trúc §11 (Task 1), gate WARNING mới (Task 2) — không cần đổi lệnh CLI nào
  (`check_section11_coverage` tự động chạy trong `verify()`, không thêm flag).
- Produces: quy trình cho LLM chạy lệnh

- [ ] **Step 1: Mở rộng đoạn giới thiệu kỷ luật ba dạng**

Trong `speckit-extension/commands/code-intel.md`, tìm dòng (khoảng dòng 11):

```
**Nguyên tắc lõi**: đây là tài liệu **nội bộ**, không giao khách — chỗ giao khách là
`srs.md` do lệnh `srs-from-code` sinh sau. Mỗi khẳng định ở §2–§7, §9 thuộc đúng một
trong ba dạng, không được lẫn lộn:
```

Sửa thành:

```
**Nguyên tắc lõi**: đây là tài liệu **nội bộ**, không giao khách — chỗ giao khách là
`srs.md` do lệnh `srs-from-code` sinh sau. Mỗi khẳng định ở §2–§7, §9, §11 thuộc đúng một
trong ba dạng, không được lẫn lộn:
```

- [ ] **Step 2: Mở rộng đoạn liệt kê mục ở đầu Step 5**

Tìm đoạn (khoảng dòng 162-166):

```
### 5. Ghi theo kỷ luật ba dạng

Rút vào §2 (Màn hình/điểm vào), §3 (Thực thể & trường dữ liệu), §4 (Kiểm tra hợp lệ &
quy tắc nghiệp vụ), §5 (Luồng nghiệp vụ), §6 (Phân quyền), §7 (Tích hợp ngoài, tác vụ
nền, sự kiện), §9 (Thông báo hiển thị) của `intel-template`.
```

Sửa thành:

```
### 5. Ghi theo kỷ luật ba dạng

Rút vào §2 (Màn hình/điểm vào), §3 (Thực thể & trường dữ liệu), §4 (Kiểm tra hợp lệ &
quy tắc nghiệp vụ), §5 (Luồng nghiệp vụ), §6 (Phân quyền), §7 (Tích hợp ngoài, tác vụ
nền, sự kiện), §9 (Thông báo hiển thị), §11 (Điều khiển giao diện — xem hướng dẫn riêng
cuối bước này) của `intel-template`.
```

- [ ] **Step 3: Thêm hướng dẫn quét control vào cuối Step 5**

Tìm đoạn kết thúc Step 5 (khoảng dòng 184-187):

```
**§4 tách riêng cột "Độ chắc chắn"** (`chắc` / `suy đoán`) — ràng buộc đánh `suy đoán` ở
đây sau này **không được** rót thẳng vào mục "Đặc tả dữ liệu" của `srs.md`; lệnh
`srs-from-code` để trống ô đó thay vì tự tin biến suy đoán thành cam kết trong tài liệu
giao khách.

### 6. Ghi phát hiện đáng chú ý — logic mâu thuẫn / lỗ hổng bảo mật
```

Chèn đoạn mới vào giữa (giữ nguyên cả hai đoạn trên, không xoá gì, không tạo mục `### N`
mới):

```
**§4 tách riêng cột "Độ chắc chắn"** (`chắc` / `suy đoán`) — ràng buộc đánh `suy đoán` ở
đây sau này **không được** rót thẳng vào mục "Đặc tả dữ liệu" của `srs.md`; lệnh
`srs-from-code` để trống ô đó thay vì tự tin biến suy đoán thành cam kết trong tài liệu
giao khách.

**Điều khiển giao diện (§11)** — sau khi §2 đã có đủ tên màn hình + cite điểm vào, với
mỗi màn hình đó: mở file component/template/view mà cột `Nguồn` của §2 trỏ tới (lần theo
cả component con nếu màn hình tách nhiều file), liệt kê control thật khai báo trong đó
(input, button, checkbox, dropdown, link…) vào bảng §11. Giữ nguyên kỷ luật ba dạng —
không nới riêng cho §11: đọc thẳng từ khai báo control → ghi bình thường kèm cite đúng
dòng khai báo; suy đoán (vd đoán nhãn hiển thị vì nhãn nằm ở file ngôn ngữ chưa tìm ra) →
đánh dấu `(suy đoán)`; không có căn cứ → không ghi, đưa xuống §8.

Cột `Màn hình` của §11 phải khớp **nguyên văn** giá trị cột `Màn hình / endpoint` tương
ứng ở §2 — đây là khoá liên kết duy nhất giữa hai mục mà `srs-from-code` đợt sau dùng để
dựng bảng điều khiển cho từng màn hình. Sai một ký tự là mất liên kết.

Cột `Loại` dùng lại đúng bộ từ vựng đã có ở `srs-template.md` §II.4 (`Textbox`,
`Passwordbox`, `Checkbox`, `Dropdown`, `Datepicker`, `Button`, `Link`,
`Label (chỉ xem)`); loại thật không nằm trong danh sách thì ghi tên loại đó nguyên văn.

Màn hình/điểm vào ở §2 **thật sự không có giao diện** (endpoint REST thuần, job nền, CLI,
message consumer) → ghi **đúng một dòng** §11 với `Loại = không-có-UI`, cột `Mô tả` nêu
rõ **lý do cụ thể** (loại điểm vào là gì), kèm cite — đây là giải trình có căn cứ, không
phải ô trống. `intel_verify.py` ở bước 9 cảnh báo (WARNING) nếu một màn hình ở §2 không
có dòng §11 nào (kể cả dòng `không-có-UI`), hoặc nếu §11 có tên màn hình không khớp §2.

### 6. Ghi phát hiện đáng chú ý — logic mâu thuẫn / lỗ hổng bảo mật
```

- [ ] **Step 4: Thêm 2 mục vào "Sai lầm thường gặp"**

Tìm dòng cuối cùng của mục "Sai lầm thường gặp" (khoảng dòng 336-337):

```
- **Ghi vào §10 một nghi ngờ mơ hồ không kèm lý do cụ thể** → không đủ căn cứ để người
  dùng phán đoán cố ý hay bug; không rõ ràng thì bỏ qua, không đoán.
```

Thêm 2 bullet mới ngay sau (là dòng cuối file):

```
- **Ghi vào §10 một nghi ngờ mơ hồ không kèm lý do cụ thể** → không đủ căn cứ để người
  dùng phán đoán cố ý hay bug; không rõ ràng thì bỏ qua, không đoán.
- **Bỏ trống §11 cho một màn hình có giao diện thật** → mục lớn nhất của tài liệu giao
  khách (đợt `srs-from-code` sau) sẽ thiếu bảng điều khiển cho màn đó. Không có giao diện
  thật thì phải ghi dòng `không-có-UI` kèm lý do, không phải bỏ trống.
- **Cột `Màn hình` ở §11 không khớp nguyên văn cột `Màn hình / endpoint` ở §2** (gõ khác
  một chữ, viết tắt khác) → đứt liên kết mà đợt sau dựa vào để dựng bảng điều khiển từng
  màn; `intel_verify.py` cảnh báo (WARNING) ca này nhưng không chặn, dễ bị bỏ qua.
```

- [ ] **Step 5: Kiểm không có mục `### N` nào bị đánh số lại**

Run: `grep -n "^### " speckit-extension/commands/code-intel.md`
Expected: đúng 10 dòng, từ `### 1. Đề xuất unit...` tới `### 10. Ghi ngược trạng thái`,
số thứ tự y hệt trước khi sửa (không dòng nào đổi số, không có `### 11` hay `### 5.5`).

- [ ] **Step 6: Smoke test — xác nhận `intel_verify.py` chạy được với §11 thật**

Run (Bash, dùng thư mục tạm; nếu `/tmp` không ghi được trên Windows Git Bash thì dùng
`/e/agent-skills/.tmp-scratch/` hoặc scratchpad, dọn sạch sau khi xong):

```bash
mkdir -p /tmp/code-intel-11-smoke && cd /tmp/code-intel-11-smoke && \
mkdir -p .specify/docs && cat > .specify/docs/functions.json << 'EOF'
{
  "schema_version": 1, "system": "SMOKE", "source": {}, "updated": "2026-08-12",
  "retired_ids": [],
  "functions": [
    {"id": "FN-01", "name": "Xac thuc", "description": "", "children": [
      {"id": "FN-01-01", "name": "Dang nhap", "description": "", "children": []}
    ]}
  ]
}
EOF
cat > intel.md << 'EOF'
# Code intel — Xac thuc

**Cập nhật**: 2026-08-12
**Phủ chức năng**: FN-01-01

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| FN-01-01 | Dang nhap | src/login.ts:1 | — |

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| Dang nhap | /login | src/login.ts:1 | FN-01-01 |

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

Không có.

## 9. Thông báo hiển thị

Không có.

## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật

Không có.

## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| Dang nhap | Ten dang nhap | Textbox | bat buoc | src/login.ts:5 |
EOF
python /e/agent-skills/speckit-extension/scripts/intel_verify.py intel.md \
  --functions .specify/docs/functions.json --root FN-01-01
```

Expected: exit 0, `"blocking": []`, `"warnings": []` (§11 phủ đủ màn hình duy nhất ở §2,
không có tên lạ). Xoá `intel.md` §11 rồi chạy lại → `warnings` phải có đúng 1 phần tử
`loai: "man-hinh-thieu-dieu-khien"` nhắc "Dang nhap".

- [ ] **Step 7: Commit**

```bash
git add speckit-extension/commands/code-intel.md
git commit -m "docs(code-intel): hướng dẫn quét điều khiển giao diện cho §11"
```

---

### Task 4: Cập nhật manifest

**Files:**
- Modify: `speckit-extension/extension.yml`

**Interfaces:**
- Consumes: Task 1-3
- Produces: bản đóng gói phản ánh đúng tính năng mới

- [ ] **Step 1: Bump version**

Đổi dòng 6 từ:

```yaml
  version: "0.3.0"
```

thành:

```yaml
  version: "0.4.0"
```

- [ ] **Step 2: Sửa description của command `code-intel`**

Tìm dòng 50 (giá trị `description` của `speckit.dft-speckit.code-intel`, nguyên văn hiện
tại):

```yaml
      description: "Rút đặc tả đủ sâu từ codebase theo cây functions.json, ghi .specify/docs/<đường-dẫn-cây>/intel.md kèm nguồn file:dòng. Tham số là một FN-ID đánh dấu điểm bắt đầu quét (trống = toàn dự án); intel_tree.py đề xuất unit theo luật cha-trực-tiếp-của-lá, LLM trình cây thụt lề xác nhận, rồi quét (hỏi song song qua subagent hay tuần tự khi có nhiều unit). intel_verify.py chấm gate BLOCKING (phủ §1, trần §8, no-clobber §8/§10) trước khi ghi ngược status qua fnlist_import.py update. Tài liệu nội bộ: khẳng định đọc thẳng từ code ghi kèm nguồn, suy đoán đánh dấu, không căn cứ thì xuống mục câu hỏi. Ghi thêm §10: phát hiện logic mâu thuẫn/lỗ hổng bảo mật thấy được trong lúc rút, để srs-from-code hỏi người dùng riêng."
```

Thay bằng:

```yaml
      description: "Rút đặc tả đủ sâu từ codebase theo cây functions.json, ghi .specify/docs/<đường-dẫn-cây>/intel.md kèm nguồn file:dòng. Tham số là một FN-ID đánh dấu điểm bắt đầu quét (trống = toàn dự án); intel_tree.py đề xuất unit theo luật cha-trực-tiếp-của-lá, LLM trình cây thụt lề xác nhận, rồi quét (hỏi song song qua subagent hay tuần tự khi có nhiều unit). intel_verify.py chấm gate BLOCKING (phủ §1, trần §8, no-clobber §8/§10) + WARNING (phủ §2↔§11) trước khi ghi ngược status qua fnlist_import.py update. Tài liệu nội bộ: khẳng định đọc thẳng từ code ghi kèm nguồn, suy đoán đánh dấu, không căn cứ thì xuống mục câu hỏi. Ghi thêm §10 (phát hiện logic mâu thuẫn/lỗ hổng bảo mật) và §11 (điều khiển giao diện từng màn hình, liên kết §2 qua tên) để srs-from-code đợt sau dùng."
```

- [ ] **Step 3: Sửa description của template `intel-template`**

Tìm dòng 71 (nguyên văn hiện tại):

```yaml
      description: "Khung cho .specify/docs/<đường-dẫn-cây>/intel.md — tài liệu nội bộ rút từ codebase theo một unit của cây functions.json, giữ nguồn file:dòng. Mười mục: phủ chức năng, màn hình/điểm vào, thực thể và trường, kiểm tra hợp lệ, luồng nghiệp vụ, phân quyền, tích hợp ngoài, câu hỏi chưa suy được từ code (gắn nhãn loại), thông báo hiển thị, và phát hiện logic mâu thuẫn/lỗ hổng bảo mật cần người quyết định."
```

Thay bằng:

```yaml
      description: "Khung cho .specify/docs/<đường-dẫn-cây>/intel.md — tài liệu nội bộ rút từ codebase theo một unit của cây functions.json, giữ nguồn file:dòng. Mười một mục: phủ chức năng, màn hình/điểm vào, thực thể và trường, kiểm tra hợp lệ, luồng nghiệp vụ, phân quyền, tích hợp ngoài, câu hỏi chưa suy được từ code (gắn nhãn loại), thông báo hiển thị, phát hiện logic mâu thuẫn/lỗ hổng bảo mật cần người quyết định, và điều khiển giao diện từng màn hình (liên kết mục màn hình qua tên)."
```

- [ ] **Step 4: Chạy toàn bộ test của repo**

Run: `python -m pytest speckit-extension/scripts/tests/ -v`
Expected: PASS — không test nào fail (284 + 6 test mới của Task 2 = 290 passed, cộng số
skip cũ không đổi)

- [ ] **Step 5: Build zip và kiểm nội dung không đổi bất thường**

Run:
```bash
cd /e/agent-skills && bash speckit-extension/build-zip.sh && \
unzip -l speckit-extension/dist/dft-speckit-0.4.0.zip | grep -E "intel_verify.py|intel-template.md|code-intel.md"
```
Expected: cả ba file đều có mặt trong `dft-speckit-0.4.0.zip` (không có file mới cần
thêm vào `build-zip.sh` ở plan này — chỉ sửa file đã có sẵn, không tạo file mới nào).

- [ ] **Step 6: Commit**

```bash
git add speckit-extension/extension.yml
git commit -m "chore(code-intel): bump 0.4.0, cập nhật description theo §11"
```

---

## Self-Review

**Spec coverage:**

| Mục spec | Task |
|---|---|
| §1 §11 thêm vào cuối `intel-template.md`, không đánh số lại | Task 1 |
| §1 cột `Màn hình` khớp §2, cột `Loại` tái dùng từ vựng `srs-template.md` §II.4 | Task 1 (comment trong template), Task 3 (hướng dẫn LLM) |
| §2 quét control từ code, giữ kỷ luật ba dạng | Task 3 |
| §3 dòng giải trình `không-có-UI` | Task 1 (bảng mẫu), Task 3 (hướng dẫn) |
| §4 gate WARNING có miễn trừ, không BLOCKING | Task 2 |
| "Không làm trong phạm vi này": không đụng `srs-*`/`intel_tree.py` | Không có task nào chạm hai phạm vi đó — đúng |
| "Rủi ro": liên kết dạng chuỗi tên, không phải ID | Task 2 (`check_section11_coverage` dùng tên, ghi rõ trong docstring); Task 3 (cảnh báo "Sai lầm thường gặp") |

Không có mục spec nào thiếu task.

**Placeholder scan:** không còn `TBD`/`TODO`. Mọi step có nội dung/lệnh thật, kèm expected
output cụ thể.

**Type consistency:** `parse_section11`/`check_section11_coverage` (Task 2) dùng đúng tên
và chữ ký trong cả phần cài đặt lẫn phần gọi ở `verify()`. `_table_data_rows`/
`_section_body` (đã có sẵn từ trước, không đổi) được Task 2 gọi đúng chữ ký hiện có
(`_section_body(text, 11)`, `_table_data_rows(body)`). Cột `Loại` (`row[2]` trong
`parse_section11`) khớp đúng vị trí cột thứ 3 trong bảng §11 mà Task 1 định nghĩa
(`Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn` — 0-based index 2 = `Loại`). Giá trị
đặc biệt `không-có-UI` dùng nhất quán ở Task 1 (comment + bảng mẫu), Task 2 (test), Task 3
(hướng dẫn + sai lầm thường gặp).
