# Mở rộng `code-intel`: rút điều khiển giao diện (§11)

**Ngày**: 2026-08-12
**Phạm vi**: `speckit-extension` — `templates/intel-template.md`, `commands/code-intel.md`,
`scripts/intel_verify.py`, `extension.yml`.

Đây là **đợt 3A**, tiền đề bắt buộc cho đợt 3B (viết lại `srs-from-code` + `srs-template`
theo khuôn tài liệu ban hành 2 cấp). Không đụng `srs-*` và không đụng `intel_tree.py`
trong đợt này.

## Bối cảnh

Tài liệu ban hành thật của công ty (`3. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_
Doanh_nghiệp.docx`) có khuôn 2 cấp cực kỳ nhất quán — 39/39 khối màn hình dùng đúng một
trình tự 8 mục, không sai một lần nào:

**Cấp 1 — Chức năng**: `Sơ đồ chức năng` → `Mục đích chức năng` → `Mô tả chức năng`
**Cấp 2 — Màn hình** (nằm trong `Mô tả chức năng`): `Đối tượng tham gia` →
`Điều kiện thực hiện` → `Mô hình Usecase` → `Kịch bản trường hợp sử dụng` (bảng) →
`Thiết kế mô hình nghiệp vụ` → `Thiết kế UX/UI` → `Mô tả điều khiển` (bảng) →
`Yêu cầu nghiệp vụ`

Đối chiếu 8 mục đó với nguồn dữ liệu `intel.md` hiện có: 7 mục có nguồn, riêng
**`Mô tả điều khiển`** thì không. Đây lại là mục lớn nhất tài liệu — 197 bảng, mỗi bảng
liệt kê từng textbox/button/link của một màn hình. `intel.md` cố ý không quét bố cục UI
(chính `srs-from-code.md` hiện tại ghi rõ: "`intel.md` không quét bố cục UI, chỉ có tên
màn/route").

Ba cách lấp khoảng trống này đã được cân nhắc:

1. Cho `srs-from-code` đọc thẳng code UI lúc sinh SRS — gọn về phạm vi, nhưng **phá kỷ
   luật lõi** "SRS chỉ rót từ `intel.md`, không quét lại code". Kỷ luật đó tồn tại để
   `srs.md` không chứa khẳng định thiếu nguồn.
2. Bỏ trống, ghi note bổ sung thủ công — tài liệu giao khách thiếu mục lớn nhất.
3. **Rút control ở `code-intel` một lần, kèm cite** — `srs` vẫn thuần rót. Chọn phương án
   này: đắt hơn nhưng không nợ kỹ thuật.

## Quyết định

### 1. Thêm §11 "Điều khiển giao diện" vào `intel-template.md`

Đặt **sau §10**, không chèn giữa và không đánh số lại mục cũ. Lý do kỹ thuật cứng:
`intel_verify.py` hardcode số mục (`_section_body(text, 1)`, `(text, 8)`, `(text, 10)`,
và danh sách `(2,3,4,5,6,7,9)` trong `check_cite_quality`) — đánh số lại là phá gate vừa
xây xong ở đợt trước.

Bảng phẳng, không lồng theo màn hình:

```markdown
## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| [tên màn hình đúng như §2] | [nhãn hiển thị] | [Textbox/Button/…] | [hành vi, ràng buộc] | [file:dòng] |
```

- **Cột `Màn hình`** phải khớp **nguyên văn** giá trị cột `Màn hình / endpoint` của §2.
  Đây là khoá liên kết duy nhất giữa hai mục; đợt 3B lọc theo cột này để dựng bảng
  `Mô tả điều khiển` cho từng màn hình. Sai chính tả một ký tự là mất liên kết.
- **Cột `Loại`** dùng lại **nguyên bộ từ vựng đã có** trong `srs-template.md` §II.4
  ("Loại trường điều khiển"): `Textbox`, `Passwordbox`, `Checkbox`, `Dropdown`,
  `Datepicker`, `Button`, `Link`, `Label (chỉ xem)`. Không đặt bộ mới — đợt 3B rót thẳng
  giá trị này sang tài liệu giao khách, nơi bảng quy ước đó đã là chuẩn công ty. Bộ này
  không đóng: loại điều khiển thật không nằm trong danh sách (vd `Radio`, `Fileupload`,
  `Tab`) thì ghi tên loại đó, và đợt 3B sẽ bổ sung vào bảng quy ước §II.4.
- **Một giá trị `Loại` đặc biệt: `không-có-UI`** — xem §3.

Bảng phẳng (không lồng `### [Tên màn hình]` như §3 làm với entity) là chủ ý: `§11` chỉ
cần một bảng nên `_table_data_rows` xử lý được ngay, không phát sinh ca nhiều-bảng-một-mục
vốn đã phải vá một vòng ở đợt trước.

### 2. Quét control trong `code-intel.md`

Thêm một bước vào quy trình rút đặc tả, đặt sau bước ghi §2–§7/§9 (vì nó phụ thuộc §2 đã
có tên màn hình + cite điểm vào).

Cách quét: từ cột `Nguồn` của mỗi dòng §2 (đã có `file:dòng` điểm vào), mở file
component/template/view tương ứng và liệt kê control thật khai báo trong đó. Lần theo cả
component con được import nếu màn hình tách nhiều file.

Giữ nguyên **kỷ luật ba dạng** đang áp cho §2–§7, §9 — không nới cho §11:
- Control đọc thẳng được từ code (thẻ `<input>`, `<button>`, khai báo form field,
  binding…) → ghi bình thường, cite trỏ đúng dòng khai báo control đó.
- Suy ra nhưng chưa chắc (vd đoán nhãn hiển thị từ tên biến vì nhãn nằm ở file ngôn ngữ
  chưa tìm ra) → đánh dấu `(suy đoán)` kèm cite gần nhất.
- Không có căn cứ → **không ghi ở §11**, đưa câu hỏi xuống §8.

Ứng dụng không có view (endpoint REST thuần, job nền, CLI, message consumer) là chuyện
bình thường, không phải thiếu sót — xem §3.

### 3. Dòng giải trình `không-có-UI`

Màn hình/điểm vào ở §2 thật sự không có giao diện → ghi **đúng một dòng** ở §11:

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| `POST /api/orders` | — | `không-có-UI` | Endpoint REST, không có view; gọi từ client ngoài | `OrderController.cs:31` |

Bắt buộc kèm cite và nêu **lý do cụ thể** (loại điểm vào là gì), không được ghi chung
chung. Đây là giải trình có căn cứ, không phải ô trống — cùng tinh thần với nhãn
`[chính sách nghiệp vụ]` ở §8: một lối thoát chính đáng, nhưng phải nói rõ vì sao.

### 4. Gate trong `intel_verify.py`: WARNING có miễn trừ tường minh

Thêm một hàm kiểm mới, mức **WARNING** (không BLOCKING):

- Lấy tập tên màn hình từ cột đầu của bảng §2.
- Lấy tập tên màn hình xuất hiện ở cột `Màn hình` của §11.
- Màn hình có ở §2 mà không có dòng nào ở §11 → WARNING nêu đích danh tên màn hình đó.
- Dòng `Loại = không-có-UI` tính là **đã giải trình** → tắt cảnh báo cho màn hình đó.

Không BLOCKING vì hai lý do:
- §2 chứa lẫn màn hình thật và endpoint/job không có UI. Chặn cứng sẽ chặn oan nhóm sau,
  buộc phải xây cơ chế miễn trừ phức tạp hơn.
- Đợt trước vừa phải vá đúng loại lỗi này: `check_not_found_ratio` chặn cứng khiến unit
  `M ≤ 2` không bao giờ pass được, gây vòng lặp sửa-verify không thoát. Không lặp lại
  khuôn đó.

Cột `Màn hình` ở §11 chứa giá trị không khớp bất kỳ màn hình nào ở §2 → cũng WARNING
(dấu hiệu gõ sai tên, làm mất liên kết mà đợt 3B dựa vào).

## Không làm trong phạm vi này

- Không viết lại `srs-template.md` / `srs-from-code.md` theo khuôn 2 cấp — đó là đợt 3B.
- Không bổ sung `Radio`/`Fileupload`/… vào bảng quy ước §II.4 của `srs-template.md`
  (file đó thuộc đợt 3B).
- Không quét được ảnh chụp màn hình. Mục `Thiết kế UX/UI` của tài liệu ban hành (342 ảnh)
  sẽ là placeholder "cần chèn ảnh" ở đợt 3B; ba mục sơ đồ (`Sơ đồ chức năng`,
  `Mô hình Usecase`, `Thiết kế mô hình nghiệp vụ` — tổng 290 ảnh) sẽ sinh mermaid từ dữ
  liệu `intel.md` ở đợt 3B.
- Không chạy lại `code-intel` trên các `intel.md` đã sinh trước đợt này. File cũ không có
  §11; chạy lại lệnh trên unit đó sẽ bổ sung §11 theo cơ chế no-clobber sẵn có (chỉ thêm,
  không xoá mục cũ).

## Rủi ro

- **Cột `Màn hình` là liên kết dạng chuỗi, không phải ID.** Tên màn hình đổi ở §2 mà §11
  không đổi theo (hoặc ngược lại) là đứt liên kết âm thầm. Gate WARNING ở §4 bắt được cả
  hai chiều, nhưng WARNING không chặn — người dùng có thể bỏ qua. Đã cân nhắc dùng FN-ID
  làm khoá thay tên: không được, vì một FN lá có thể ứng với nhiều màn hình con và ngược
  lại, quan hệ không 1-1.
- **Chi phí quét tăng đáng kể.** Rút control nghĩa là mở thêm file view/component cho mỗi
  màn hình — với unit nhiều màn hình, đây là phần tốn nhất của lệnh. Chấp nhận: đây là dữ
  liệu cho mục lớn nhất của tài liệu giao khách.
- **`intel.md` đã sinh trước đợt này thiếu §11.** Đợt 3B rót sang SRS sẽ ra bảng
  `Mô tả điều khiển` rỗng cho các unit đó, cho tới khi chạy lại `code-intel`. Cần nói rõ
  trong tài liệu 3B thay vì để người dùng tự phát hiện.
