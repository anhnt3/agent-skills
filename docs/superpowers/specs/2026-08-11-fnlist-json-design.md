# Thiết kế lại `fnlist-import`: `functions.json` làm source of truth

**Ngày**: 2026-08-11
**Phạm vi đợt này**: `speckit-extension` — `commands/fnlist-import.md`,
`scripts/fnlist_import.py`, `references/functions-schema.md` (mới).

`commands/code-intel.md` và `commands/srs-from-code.md` **để đợt sau** — thiết kế phần
tác động lên chúng vẫn nằm ở §7 để đợt sau thực hiện, nhưng không sửa trong đợt này.
Xem "Hệ quả của việc chia làm hai đợt" ở cuối tài liệu.

## Bối cảnh

Đường ống reverse tài liệu gồm ba lệnh: `fnlist-import` (function list → danh mục chức
năng) → `code-intel` (codebase → `intel.md`) → `srs-from-code` (`intel.md` → `srs.md`).
Sau khi dùng thật, người dùng nêu 5 phản hồi về khâu đầu tiên:

1. Template đưa ra file riêng.
2. Phân chia rõ phần xử lý bằng Python và phần xử lý bằng LLM.
3. Đánh ID cho các cấp function (2, 3 hoặc 4 cấp tuỳ độ lớn dự án).
4. Cần code tất định lưu trữ JSON cho Python parse rồi đưa cho LLM.
5. Tối ưu output, đang bị duplicate thông tin với tài liệu khác.

Bản hiện tại sinh `.specify/docs/functions.md` — một bảng markdown 7 cột
(`FN-ID | Nhóm | Tên chức năng | Mô tả | Cụm | Nguồn code | Trạng thái`), format hardcode
trong hàm `render_markdown()`. Danh mục **phẳng một cấp**, cấp bậc duy nhất là cột `Nhóm`
dạng chuỗi tự do. `code-intel` và `srs-from-code` đọc file này bằng cách parse bảng
markdown, và **sửa tay** ba cột cuối — kèm một loạt "mỏ neo đếm dòng" trong prompt để
chống LLM sửa hỏng bảng.

## Quyết định

### 1. `functions.json` là output duy nhất; bỏ hẳn `functions.md`

Không sinh markdown nữa. Không ai đọc hay sửa tay danh mục chức năng — nó là dữ liệu
trung gian giữa ba lệnh, nên định dạng phải tối ưu cho máy đọc.

Hệ quả: mọi cơ chế tồn tại để bảo vệ bản sửa tay đều bị gỡ bỏ — no-clobber
`functions.new.md`, các mỏ neo đếm dòng bảng, và luật "không tự copy đè". Script độc
quyền ghi file thì không có bản sửa tay nào để mất.

### 2. Schema

Key tiếng Anh, nội dung tiếng Việt. Cây lồng `children`.

```json
{
  "schema_version": 1,
  "system": "Hệ thống DMS",
  "source": { "file": "FunctionList_DMS.xlsx", "sheet": "DanhMuc" },
  "updated": "2026-08-11",
  "functions": [
    {
      "id": "FN-01",
      "name": "Quản lý đơn hàng",
      "description": "",
      "children": [
        {
          "id": "FN-01-01",
          "name": "Danh sách đơn",
          "description": "Xem, tìm kiếm đơn hàng",
          "status": "intel",
          "children": []
        },
        { "id": "FN-01-02", "name": "Tạo đơn mới", "description": "", "children": [] }
      ]
    }
  ]
}
```

**Trường của một node** — đúng năm trường, không hơn:

| Trường | Ý nghĩa |
|---|---|
| `id` | Mã đa cấp, xem §3 |
| `name` | Tên chức năng, **nguyên văn** ô nguồn |
| `description` | Mô tả, **nguyên văn** ô nguồn; không có thì `""` |
| `status` | `pending` (mặc định) / `intel` / `srs`. Vắng mặt = `pending` |
| `children` | Mảng node con, rỗng nếu là lá |

**Những trường cố ý KHÔNG có** (phản hồi #5 — chống duplicate):

- `level` / `outline` / `parent` — suy ra được từ độ sâu lồng và vị trí trong mảng. Lưu
  thêm là tạo nguy cơ hai nguồn lệch nhau.
- `cum` (cụm chức năng) — suy ngược được: `intel.md` của mỗi cụm liệt kê FN-ID nó phủ.
  Đổi lại, tra "FN-01-05 thuộc cụm nào" phải quét `.specify/docs/*/intel.md`; chấp nhận
  được vì số cụm nhỏ.
- `nguon_code` (danh sách `file:dòng`) — đây là nội dung của `intel.md`. Lặp ở đây là
  bản dễ lạc hậu hơn bản gốc.
- Cột `Nhóm` cũ — cấp bậc giờ nằm trong cấu trúc cây, không còn là chuỗi tự do.

Thứ tự node trong mảng `children` = thứ tự dòng trong file nguồn.

### 3. Quy tắc ID đa cấp

Dạng `FN-01`, `FN-01-01`, `FN-01-01-01` — số cấp bằng độ sâu trong cây (2 đến 4 cấp tuỳ
dự án). Năm quy tắc, tất cả do script thi hành:

1. **Lần import đầu**: đánh số theo vị trí trong nhóm cha, bắt đầu từ `01`.
2. **Import lại, dòng đã tồn tại giữ nguyên ID**: khớp cũ↔mới theo **đường dẫn tên** —
   chuỗi `name` từ gốc xuống tới node đó (vd `Quản lý đơn hàng / Danh sách đơn`), không
   phải chỉ mình `name`. Nhờ vậy hai chức năng cùng tên "Thêm mới" ở hai nhóm khác nhau
   không còn tranh ID — bản hiện tại khớp theo tên đơn nên phải cảnh báo người dùng rằng
   ID của các dòng trùng tên không ổn định qua các lần import. Cảnh báo đó biến mất.
3. **Dòng mới chèn vào giữa**: nhận số kế tiếp chưa dùng **trong nhóm cha**, không dịch
   số của ai. Chèn giữa `FN-01-01` và `FN-01-02` thì được `FN-01-03` — nằm giữa bảng
   nhưng mang số cuối. Đây là cái giá để ID bất biến; số không phản ánh thứ tự hiển thị.
4. **Dòng bị xoá**: số đó bỏ trống vĩnh viễn, không cấp lại cho node khác (cấp lại là hai
   tài liệu ở hai thời điểm trỏ cùng một ID ra hai chức năng khác nhau).
5. **Chức năng chuyển sang nhóm cha khác**: tiền tố ID không thể còn đúng → xử lý như
   "bỏ + thêm", nhận ID mới dưới cha mới. `diff` phải gắn nhãn riêng
   `chuyển nhóm (FN-01-03 → FN-02-05)` để người dùng biết cập nhật các tài liệu đã trỏ ID
   cũ. Đây là điểm gãy truy vết duy nhất còn lại, và nó hiện diện tường minh.

### 4. Ranh giới Python / LLM (phản hồi #2)

**Nguyên tắc: mọi thao tác ghi file đều qua script; LLM chỉ quyết định và xác nhận.**

`scripts/fnlist_import.py` có ba subcommand:

| Lệnh | Việc |
|---|---|
| `inspect` | In cấu trúc thật của file (sheet, số dòng, `head`) **và dò kiểu phân cấp** — chấm điểm ba kiểu ở §5, in phỏng đoán kèm bằng chứng, không tự quyết |
| `write` | Đọc `mapping.json`, dựng cây, cấp ID theo §3, ghi `functions.json`; file đã tồn tại thì in `diff` |
| `update` | Nhận `FN-ID` + `status`, ghi vào JSON. `code-intel`/`srs-from-code` gọi lệnh này thay vì sửa tay |

LLM chịu trách nhiệm: quyết ánh xạ cột và kiểu phân cấp, hỏi người dùng khi mơ hồ, xác
nhận trước khi ghi, trình `diff`, báo cáo dòng bị bỏ.

### 5. Nhận diện phân cấp — hỗ trợ ba kiểu

File function list thực tế mỗi nơi một kiểu, nên script hỗ trợ cả ba, khai trong
`mapping.json` qua khối `hierarchy`:

```json
{
  "sheet": "DanhMuc",
  "first_data_row": 2,
  "columns": { "description": 5 },
  "hierarchy": { "mode": "columns", "level_columns": [1, 2, 3] },
  "skip_rows": []
}
```

- **`columns`** — mỗi cấp một cột (`Phân hệ | Nhóm | Chức năng`). `level_columns` liệt kê
  chỉ số cột theo thứ tự cấp. Ô trống nghĩa là dòng đó tiếp tục thuộc cha đã mở ở phía
  trên. `name` lấy từ cột sâu nhất có giá trị trên dòng đó.
- **`outline`** — một cột chứa số mục lục `1`, `1.1`, `1.1.1`; đếm dấu chấm ra cấp.
  Khai `{"mode": "outline", "column": 0}`.
- **`level`** — một cột ghi thẳng số cấp (1/2/3). Khai `{"mode": "level", "column": 0}`.

`inspect` chấm điểm cả ba và báo kiểu khả dĩ nhất kèm bằng chứng cụ thể; LLM **luôn phải
hỏi người dùng xác nhận** kiểu phân cấp trước khi ghi, kể cả khi điểm số rõ ràng.

Hệ đếm giữ nguyên quy ước hiện có, và đây là chỗ dễ nhầm: `first_data_row`, `columns`,
`level_columns`, `hierarchy.column` đều **0-based**; riêng `skip_rows` là **1-based**
(đúng số dòng người dùng thấy trong Excel).

Checkpoint xác nhận trước khi ghi (bước 3 của command hiện tại) giữ nguyên tinh thần bắt
buộc, nhưng render thử **cây 5 dòng đầu có thụt lề** thay vì bảng phẳng, để người dùng
thấy được cấp bậc đã dựng đúng chưa.

### 6. Nơi đặt schema (phản hồi #1)

`references/functions-schema.md` — mô tả schema (trường, ý nghĩa, giá trị hợp lệ, ví dụ
đầy đủ). Đặt ở `references/` chứ không phải `templates/` vì `templates/` khai trong
`extension.yml` là khung tài liệu spec-kit copy ra cho người dùng điền, còn đây là hợp
đồng dữ liệu giữa ba lệnh — cùng loại với `references/traceability.md` sẵn có. Cả ba
command trỏ tới file này thay vì mỗi command tự mô tả một bản.

`build-zip.sh` đã `cp -R references/`, nên không cần sửa gì để nó được đóng gói — nhưng
phải kiểm lại sau khi build (đây là lỗi từng gặp: support dir không được copy thì command
gãy trong bản cài).

### 7. Tác động sang `code-intel` và `srs-from-code` (đợt sau, không làm bây giờ)

- Đọc danh mục: từ parse bảng markdown → đọc `functions.json`. Việc phân giải đầu vào
  (`FN-001`, khoảng `FN-003..FN-012`, tên nhóm) chuyển sang duyệt cây; khoảng ID lấy theo
  **thứ tự duyệt cây (pre-order)**, tương đương "thứ tự dòng trong bảng" của bản cũ.
- Ghi ngược: từ "sửa tay bảng markdown + đếm dòng" → gọi `fnlist_import.py update`. Gỡ bỏ
  toàn bộ đoạn mỏ neo đếm dòng và luật no-clobber liên quan trong hai command này.
- Trường `cum` không còn: `srs-from-code` xác định FN thuộc cụm nào bằng chính `intel.md`
  của cụm đang xử lý, không tra ngược từ danh mục.

## Không làm trong phạm vi này

- Migration từ `functions.md` cũ sang `functions.json`. Đường ống chưa phát hành rộng;
  ai đã có `functions.md` thì import lại từ file Excel gốc.
- Validate bằng JSON Schema chuẩn (thư viện `jsonschema`) — script tự kiểm cấu trúc là đủ
  ở quy mô này.
- Đổi `intel.md`/`srs.md` sang JSON. Hai file đó có người đọc thật, markdown là đúng.

## Hệ quả của việc chia làm hai đợt

Đợt 1 chỉ làm `fnlist-import`. Từ lúc đợt 1 xong tới lúc đợt 2 xong, **đường ống đứt**:
`fnlist-import` sinh `functions.json`, còn `code-intel`/`srs-from-code` vẫn đi tìm
`functions.md` và sẽ dừng với thông báo "không tồn tại, hãy chạy `fnlist-import`" — chạy
lại cũng không sinh ra file đó nữa, nên người dùng rơi vào vòng lặp không lối thoát.

Hai việc bắt buộc làm trong đợt 1 để khoảng đứt này không âm thầm:

- `fnlist-import` **không xoá** `functions.md` cũ nếu project đã có. Ai đang dở việc thì
  `code-intel` vẫn chạy được trên bản cũ cho tới đợt 2.
- Bước kết thúc của `fnlist-import` nói thẳng: `functions.json` đã ghi, nhưng
  `code-intel`/`srs-from-code` **chưa đọc được định dạng này** — chưa chạy tiếp được cho
  tới khi hai lệnh đó được cập nhật. Không nhắc "bước kế tiếp là chạy `code-intel`" như
  hiện tại, vì lời nhắc đó sẽ dẫn người dùng vào đúng chỗ gãy.

## Rủi ro

- **Dựng cây từ bảng phẳng là chỗ dễ sai âm thầm** — nhất là mode `columns` với ô trống
  kế thừa cha. Checkpoint render cây ở §5 là hàng phòng thủ chính; test cần phủ cả ba
  mode, gồm ca nhảy cấp (cấp 1 xuống thẳng cấp 3) phải báo lỗi thay vì đoán.
- **Bỏ `cum` khiến tra ngược tốn hơn.** Nếu về sau số cụm lớn, có thể phải thêm lệnh
  index — nhưng chưa làm bây giờ.
