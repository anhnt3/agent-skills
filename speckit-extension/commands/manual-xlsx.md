---
description: "Sinh testcase kiểm thử thủ công cho tester từ spec/acceptance criteria, xuất ra CSV rồi XLSX với cấu trúc cột và format cố định (giống hệt nhau mọi lần chạy)."
---

# Manual Testcase → XLSX (định dạng cố định)

Sinh testcase kiểm thử **thủ công** cho tester từ spec/acceptance criteria, xuất ra
**CSV rồi XLSX** với cấu trúc cột và format **giống hệt nhau mọi lần chạy**. Đây là
testcase cho người chạy tay — KHÔNG phải test code tự động.

Nguyên tắc lõi: **nội dung do bạn viết theo cấu trúc cố định, format do script
`scripts/csv_to_xlsx.py` áp — không tự chế lại style.**

## User Input

$ARGUMENTS

Kỳ vọng: đường dẫn tới spec / user story / acceptance criteria / FR (hoặc thư mục
feature). Nếu trống, hỏi người dùng nguồn spec trước khi tiếp tục.

## Khi nào dùng

- "Sinh testcase cho tester", "testcase thủ công", "test case CSV/Excel", "kịch bản kiểm thử".
- Nguồn là spec / user story / acceptance criteria / FR.

KHÔNG dùng cho: sinh test code tự động (Playwright/unit).

## Quy trình (bắt buộc theo thứ tự)

1. **Đọc spec.** Tách MỖI acceptance scenario / business rule thành **1 testcase riêng**
   (không gộp nhiều rule vào 1 case).
2. **Viết CSV** đúng cấu trúc cố định bên dưới, lưu `<thư mục spec>/testcases-manual.csv`.
3. **Chạy script** để sinh XLSX (format tự động, cố định). Chỉ cần `python3` —
   script **tự dựng venv + cài openpyxl** lần đầu (tránh lỗi PEP 668), team không phải cài gì:
   ```bash
   python3 .specify/extensions/dft-speckit/scripts/csv_to_xlsx.py \
     specs/<feature>/testcases-manual.csv \
     specs/<feature>/testcases-manual.xlsx --sheet "<Tên feature>"
   ```
   > Nếu chạy trực tiếp từ repo extension (chưa cài qua `specify`), dùng đường dẫn
   > `speckit-extension/scripts/csv_to_xlsx.py`.
   > Lần đầu sẽ in "đang tạo venv..." rồi tạo `scripts/.venv` (đã ignore) — các lần sau chạy ngay.
   > `--sheet` KHÔNG được chứa `: \ / ? * [ ]` (Excel cấm). Script tự thay bằng khoảng
   > trắng nếu lỡ có, nhưng nên đặt tên không dấu gạch chéo ngay từ đầu (vd `"Auth Login"`,
   > không phải `"Auth / Login"`).
4. **Verify** (mục Verification) trước khi báo xong.

## Cấu trúc cột CỐ ĐỊNH (đúng 14 cột, đúng thứ tự)

```
ID | Tiêu đề | Nhóm | Ưu tiên | Loại | Tiền điều kiện | Dữ liệu test | Các bước thực hiện | Kết quả mong đợi | Truy vết | Kết quả thực tế | Trạng thái | Bug ID | Ghi chú
```

**10 cột đầu = THIẾT KẾ** (bạn viết một lần, versioned). **4 cột cuối = THỰC THI**
(tester điền mỗi test run) — trong file nguồn **để TRỐNG** (`""`), chỉ điền khi chạy thật.

| Cột | Quy tắc |
|-----|---------|
| ID | `TC-<PREFIX>-001` tăng dần; PREFIX = viết tắt feature (vd AUTH). |
| Tiêu đề | Feature — kịch bản — kết quả, một dòng. |
| Nhóm | Theo user story / nhóm chức năng. |
| Ưu tiên | Chỉ `P1` / `P2` / `P3`. |
| Loại | Happy path / Negative / Boundary / Security / State transition / Edge case. |
| Tiền điều kiện | Trạng thái giả định (đã seed, đang ở trang X...). |
| Dữ liệu test | Giá trị cụ thể (username, mật khẩu, endpoint...). Không có thì `-`. |
| Các bước thực hiện | Đánh số `1. 2. 3.`, mỗi bước 1 hành động, xuống dòng. |
| Kết quả mong đợi | Đánh số khớp 1-1 với bước; mỗi ý **kiểm chứng được** (giá trị/thông báo/HTTP status). |
| Truy vết | Mã FR/AC trong spec. |
| Kết quả thực tế | THỰC THI — để trống; tester ghi cái thực sự xảy ra khi Fail. |
| Trạng thái | THỰC THI — để trống; dropdown Pass/Fail/Blocked/N/A/Chưa chạy (script tự gắn). |
| Bug ID | THỰC THI — để trống; link ticket khi Fail (vd JIRA AUTH-123). |
| Ghi chú | THỰC THI — để trống; note môi trường/browser/observation. |

## Quy tắc chất lượng nội dung

- **Một expected phải kiểm chứng được**: nêu giá trị chính xác, tên phần tử + trạng thái,
  thông báo cụ thể, HTTP status, hoặc số đếm. **Cấm**: "hoạt động tốt", "ổn",
  "hiển thị đúng", "chờ một lúc".
- **Một assertion mỗi bước**; nhiều kiểm tra thì tách bước.
- **Một rule = một case**; không gộp.
- Phủ đủ loại: happy + negative + boundary + security + edge case.
- CSV: cell nhiều dòng phải bọc trong dấu `"`, escape `""` cho dấu nháy bên trong.

## Verification (trước khi báo xong)

```bash
# 1. Lint expected mơ hồ — phải RỖNG
grep -niE "hoạt động tốt|ổn|hiển thị đúng|chờ một lúc|verify it works|looks right|everything works" testcases-manual.csv

# 2. Header + đếm case (parse chuẩn CSV)
python3 -c "import csv;r=list(csv.reader(open('testcases-manual.csv')));print(r[0]);print(len(r)-1,'cases',len(r[0]),'cols')"
```
Script tự chặn nếu header sai 14 cột. Có `MISSING`/mơ hồ → sửa trước khi giao. Mỗi dòng
phải đúng 14 field (4 field execution cuối để trống `""`).

## Sai lầm thường gặp

- Tự viết code format XLSX mỗi lần → format lệch. **Luôn dùng script**, đừng chế lại.
- Cài openpyxl vào python hệ thống → lỗi PEP 668. Script **tự dựng venv** — cứ chạy bằng
  `python3`, đừng `pip install` tay.
- Gộp nhiều acceptance scenario vào 1 case → pass/fail mập mờ.
- Expected chung chung không kiểm chứng được.
- **Dấu phẩy thừa/thiếu ở cuối dòng CSV → cột ma.** Mỗi dòng phải đúng 14 field; script nay
  chặn và báo dòng sai. Nếu thêm cột execution bằng script phụ, đảm bảo append đúng 4 field
  rỗng cho MỌI dòng (kể cả dòng cuối).
- **`--sheet` có `/` (hay `: \ ? * [ ]`) → openpyxl crash.** Đặt tên sheet không chứa các ký
  tự này; script tự làm sạch nhưng đừng dựa dẫm.
- **Lint bắt nhầm cụm hợp lệ**: `"hiển thị đúng"` bị cấm vì thường mơ hồ, nhưng
  `"hiển thị đúng tên X và email Y"` lại kiểm chứng được → khi bị bắt, đổi từ (vd
  `"hiển thị chính xác ..."`) chứ đừng bỏ phần kiểm chứng.
