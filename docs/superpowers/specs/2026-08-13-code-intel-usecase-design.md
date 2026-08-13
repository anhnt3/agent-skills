# Đợt 3B-2: thêm §12 "Kịch bản Use Case" vào `code-intel`

**Ngày**: 2026-08-13
**Phạm vi**: `speckit-extension` — `templates/intel-template.md`, `commands/code-intel.md`,
`scripts/intel_verify.py`.

Đây là **đợt 3B-2**, tiếp theo đợt 3B-1 (di trú `srs-from-code`/`srs_verify.py` sang mô
hình cây). Không đụng `srs-*`, không đụng `intel_tree.py`, không đụng §11 "Điều khiển
giao diện" (vừa hoàn tất ở đợt 3A) — chỉ thêm mục mới sau §11.

## Bối cảnh

Tài liệu ban hành thật (`3. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Doanh_nghiệp.docx`)
có mục **"Kịch bản trường hợp sử dụng"** cho mỗi màn hình — 9 field cố định (Tên Use
Case/Mức quan trọng/Người dùng/Loại UC/Người sử dụng và yêu cầu/Mô tả tóm tắt/Thời điểm
sử dụng/Luồng sự kiện chuẩn/Luồng sự kiện nhỏ), hiện **không có nguồn dữ liệu nào** trong
`intel.md` — cùng loại khoảng trống mà đợt 3A đã lấp cho "Mô tả điều khiển" (§11). 3B-2
lặp lại đúng mẫu 3A đã dùng: thêm mục mới vào `intel-template.md`, mở rộng `code-intel.md`
để rút dữ liệu, thêm gate WARNING vào `intel_verify.py`; `srs-from-code` KHÔNG rót mục này
(để dành cho một đợt sau, cùng lý do đã áp cho §11).

## Quyết định

### 1. Thêm §12 "Kịch bản Use Case" vào `intel-template.md`

Đặt **sau §11**, không chèn giữa và không đánh số lại mục cũ (lý do kỹ thuật giữ nguyên
từ 3A: `intel_verify.py` hardcode số mục qua `_section_body(text, N)`).

Dùng **khối lồng `### [Tên Use Case]`** (như §3 thực thể, §5 luồng nghiệp vụ), **không**
phải bảng phẳng như §11 — nội dung nhiều dòng (luồng sự kiện chuẩn đánh số, luồng sự kiện
nhỏ khai triển riêng theo nhánh `S-n`) không vừa một ô bảng:

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
```

Giữ nguyên cả 9 field, đúng tên/thứ tự như docx — không lược bớt.

**Ba field không suy được từ code** (`Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng`) —
đây là phân loại nghiệp vụ thuần (mức độ ưu tiên, loại use case theo quy ước BA, khung
giờ sử dụng), không có căn cứ code nào trả lời được dù tìm kỹ tới đâu. Khác với kỷ luật
ba dạng đang áp cho các mục khác (không căn cứ → đưa xuống §8), ba field này **luôn ghi
cố định "Chưa có thông tin" ngay trong §12**, **không đưa xuống §8** — lý do: đây không
phải "chưa tìm ra", mà là "cấu trúc không thể tìm ra" (giống cách `srs-from-code` xử lý
khoảng trống hành chính hiện nay: ghi thẳng, không hỏi). Đưa xuống §8 sẽ làm trần câu hỏi
(`check_section8_cap`, giới hạn `max(3, m/3)`) tăng thêm 3 mục "vô nghĩa" cho MỖI use
case, dễ đẩy unit nhiều use case vượt trần chỉ vì ba field không bao giờ trả lời được.

**Các field còn lại** (`Người dùng`, `Người sử dụng và yêu cầu`, `Mô tả tóm tắt`,
`Luồng sự kiện chuẩn`, `Luồng sự kiện nhỏ`) áp đúng kỷ luật ba dạng hiện có: đọc thẳng →
ghi kèm cite; suy đoán → đánh dấu `(suy đoán)`; không căn cứ → không ghi field đó (hoặc
lược cả use case nếu không còn gì để viết), đưa câu hỏi xuống §8 như bình thường.

### 2. Nguồn dữ liệu — tái dùng bằng chứng đã thu ở §5/§2/§6, không quét code lần hai

`code-intel.md` thêm một bước (sau bước ghi §2–§7/§9/§11, cùng vị trí logic với §11) rút
§12 từ dữ liệu ĐÃ CÓ, không mở lại file quét mới:

- **`Màn hình`**: lấy nguyên văn từ cột "Màn hình / endpoint" của §2 — đây là khoá liên
  kết, xem mục 3.
- **`Người dùng`**: suy từ §6 (bảng Phân quyền, cột Vai trò) nếu có dòng khớp màn hình
  này; không có → suy từ đối tượng dùng màn hình đó ở §2, đánh dấu `(suy đoán)`.
- **`Người sử dụng và yêu cầu`**, **`Mô tả tóm tắt`**: viết từ chính bằng chứng của §5
  (mô tả luồng) + §2 (tên màn hình) — một câu/đoạn tóm gọn, cite trỏ về cùng `file:dòng`
  đã dùng ở §5 cho luồng tương ứng.
- **`Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`**: viết lại đúng bằng chứng của §5 (mục
  "Luồng nghiệp vụ" — `[Trình tự các bước, nêu rõ thành phần nào xử lý bước nào]`) theo
  khuôn đánh số/nhánh `S-n` của Use Case, KHÔNG suy luận bước mới ngoài những gì §5 đã
  có. §5 không có luồng nào ứng với màn hình này → không viết được `Luồng sự kiện chuẩn`
  có căn cứ, đưa xuống §8 với nhãn `[không suy được từ code]` (giữ nguyên nhãn hiện có,
  không đặt nhãn mới).

Bước này **phụ thuộc §2 và §5 đã ghi xong** (như §11 phụ thuộc §2) — đặt sau cả hai
trong quy trình.

### 3. Khoá liên kết — tái dùng đúng cột `Màn hình` của §2 (như §11)

`Màn hình` ở mỗi khối `### [Tên Use Case]` phải khớp **nguyên văn** giá trị cột
"Màn hình / endpoint" ở §2 — cùng khoá liên kết §11 đã dùng, không đặt khoá thứ ba. Một
use case có thể gộp nhiều FN (như ví dụ "Đăng nhập" của docx gồm Username/Facebook/
Google/Ghi nhớ/Khôi phục — cùng một use case, nhiều luồng nhỏ).

Màn hình/điểm vào ở §2 thật sự không có use case nào ứng với nó (endpoint kỹ thuật thuần
— webhook nội bộ, health-check, cron trigger) → áp đúng tinh thần dòng giải trình
`không-có-UI` của §11: không bắt buộc phải có khối `###` cho MỌI dòng §2, gate ở mục 4
chỉ WARNING chứ không BLOCKING, nên không cần một cơ chế giải trình riêng như §11 — nêu
lý do trong `warnings` là đủ, người soát tự quyết có bổ sung hay không.

### 4. Gate trong `intel_verify.py`: `check_section12_coverage`, WARNING có miễn trừ

Thêm hàm kiểm mới, mức **WARNING** (không BLOCKING) — cùng lý do §11's
`check_section11_coverage` (§2 lẫn cả endpoint không có UI/use case thật, chặn cứng sẽ
chặn oan nhóm đó, lặp lại đúng loại lỗi vòng-lặp-không-thoát mà `check_not_found_ratio`
từng mắc):

- Lấy tập tên màn hình từ cột đầu của bảng §2 (dùng lại `_table_data_rows`/`_section_body`
  đã có, `strip=False` để giữ nguyên nội dung bọc backtick — xem docstring `_section_body`
  của đợt 3A).
- Lấy tập tên màn hình xuất hiện ở field `- **Màn hình**: ...` của mỗi khối `###` §12 —
  cần hàm parse MỚI (`parse_section12`), khác `parse_section11` (table-row) vì §12 là
  khối lồng bullet-field, không phải bảng. Đọc từng dòng trong `_section_body(text, 12)`,
  khớp regex `^-\s+\*\*Màn hình\*\*:\s*(.+)$`, áp `_strip_backtick` giống §11.
- Màn hình có ở §2 mà không có khối `###` nào ở §12 nhắc tới nó → WARNING nêu đích danh
  tên màn hình đó.
- `Màn hình` ở §12 chứa giá trị không khớp bất kỳ màn hình nào ở §2 → WARNING (dấu hiệu
  gõ sai tên, hoặc dùng nhầm tên use case thay tên màn hình).

`check_cite_quality` (đang quét section `(2,3,4,5,6,7,9,11)`) **mở rộng thêm `12`** —
nhưng vì §12 không dùng bảng, `check_cite_quality` hiện tại chạy trên `_table_data_rows`
sẽ luôn trả rỗng cho §12 (không có bảng nào để quét ngoài phần "Luồng sự kiện chuẩn" nếu
được viết dạng bảng — mục này KHÔNG dùng bảng, dùng danh sách đánh số). Vì vậy
`check_cite_quality` **không** thêm `12` vào danh sách — viết một kiểm riêng nếu cần (xem
"Không làm trong phạm vi này"), tránh vá `check_cite_quality` để nhận nhầm quét không ra
gì mà tưởng là "sạch".

## Không làm trong phạm vi này

- Không viết `check_cite_quality` riêng cho nội dung "Luồng sự kiện chuẩn/nhỏ" của §12
  (kiểm cite theo dòng đánh số, không phải theo bảng) — để dành nếu thực tế cho thấy cần,
  tránh over-engineering một gate chưa chắc cần khi chưa có dữ liệu thật để đối chiếu.
- Không rót §12 sang `srs.md` — đó là việc của một đợt sau (cùng loại hoãn đã áp cho
  §11), không phải 3B-2 hay 3B-3 đã lên kế hoạch (3B-3 chỉ đổi khuôn tài liệu, chưa chắc
  đã rót cả use case; sẽ brainstorm riêng khi tới lượt).
- Không đổi bộ từ vựng `Loại UC`/`Mức quan trọng` — giữ đúng "Chưa có thông tin" cố định,
  không đặt enum hay gợi ý giá trị mặc định nào khác.
- Không chạy lại `code-intel` trên các `intel.md` đã sinh trước đợt này — file cũ không
  có §12; chạy lại lệnh trên unit đó sẽ bổ sung §12 theo cơ chế no-clobber sẵn có (chỉ
  thêm, không xoá mục cũ).

## Rủi ro

- **`parse_section12` là hàm phân tích khối bullet mới, không tái dùng được `_table_rows`
  sẵn có** — rủi ro lỗi regex khi field name chứa ký tự đặc biệt hoặc khi người viết lỡ
  đổi thứ tự bullet. Giảm nhẹ: field `Màn hình` LUÔN là bullet đầu tiên trong khối theo
  khuôn ở mục 1, nhưng parser không nên phụ thuộc vị trí — quét toàn bộ dòng trong khối
  tìm dòng khớp regex, không giả định vị trí cố định.
- **Use case gộp nhiều FN qua `Màn hình` giống hệt cách §11 làm** — kế thừa đúng rủi ro
  đã ghi nhận ở đợt 3A: cột `Màn hình` là liên kết dạng chuỗi, không phải ID; đổi tên màn
  hình ở §2 mà §12 không đổi theo là đứt liên kết âm thầm, gate WARNING bắt được nhưng
  không chặn.
- **Ba field "Chưa có thông tin" cố định có thể bị hiểu nhầm là placeholder chưa điền** —
  `intel_verify.py`'s `find_placeholders` chỉ bắt cặp `[...]` chưa thay, "Chưa có thông
  tin" là văn bản thường (không ngoặc vuông) nên không bị chặn nhầm; xác nhận lại khi
  viết test.
