# THE DFT STANDARD — Quy Ước Chung (Frontend · Backend · QA)

LUẬT áp cho MỌI project DFT. Chuỗi trong `" "` phải dùng **nguyên văn**, không diễn đạt lại. Nguồn: QUC.V1.

## Mục lục

1. Kiến trúc của sự nhất quán
2. Ký hiệu quy trình (Flowchart)
3. Ma trận kiểu dữ liệu lõi (Database)
4. Ma trận kiểm chuẩn dữ liệu phức tạp (Email / SĐT / Mật khẩu)
5. Giải phẫu Form nhập liệu
6. Xử lý chuỗi & luồng sự kiện tương tác
7. Giải phẫu màn hình danh sách (Data Grid)
8. Logic tìm kiếm & lọc
9. Ma trận phản hồi hệ thống (Toast / Popup / Inline)
10. Hệ màu & quy chuẩn nút bấm
11. Hành vi Combobox & Checkbox phân quyền
12. Quy chuẩn tải file đính kèm
13. Lưu đồ xử lý nhập dữ liệu (Import Flow)
14. Developer Pre-Release Checklist
15. Nhật ký hệ thống (Audit Log)
16. Phân quyền lúc chạy (Runtime Authorization)
17. Đồng bộ sau thao tác & trùng dữ liệu
18. Toàn vẹn Export & chống CSV injection
19. Vòng đời phiên & xác thực

---

## 1. Kiến trúc của sự nhất quán

4 trụ cột: Dữ liệu lõi (Backend — kiểu/MaxLength/định dạng DB) · Tương tác & Validate (Debounce, Trim, kiểm chuẩn input) · Giao diện (Form/Grid/Nút + hệ màu) · Phản hồi (Toast/Popup/Inline). *(Nguyên tắc — không phải mục kiểm code.)*

## 2. Ký hiệu quy trình (Flowchart)

| Ký hiệu | Ý nghĩa |
|---|---|
| Hình bầu dục (Oval) | Khởi đầu / kết thúc quy trình |
| Hình bình hành | Thông tin / dữ liệu đầu vào |
| Hình chữ nhật | Thao tác / xử lý tự động |
| Hình thang | Thao tác thủ công (tay) |
| Hình kim cương | Quyết định (rẽ nhánh có điều kiện) |
| Hình tài liệu | Hồ sơ / biên bản / báo cáo đầu ra |

## 3. Ma trận kiểu dữ liệu lõi (Database)

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| Tên / Tên hiển thị | `Varchar(255)` | Viết hoa chữ cái đầu; loại bỏ khoảng cách thừa |
| Mã (Code/ID) | `Varchar(50)` | Không ký tự đặc biệt, không khoảng trắng, trừ `_` `-` |
| Ghi chú / Mô tả | `Varchar(4000)` | Cho phép ký tự đặc biệt và xuống dòng |
| Tiền (VND) | `Decimal(18,0)` | Không phần thập phân; dấu `.` ngăn cách hàng nghìn |
| Số lượng (thập phân) / Tỉ lệ | `Decimal(18,2)` / `Decimal(5,2)` | Tối đa 2 chữ số sau dấu phẩy |
| Mật khẩu | `Varchar(128)` max | Bắt buộc hash; **không lưu plaintext** |

## 4. Ma trận kiểm chuẩn dữ liệu phức tạp

### 4.1. Email — `Varchar(320)`
- Cấu trúc: Local-part (64) `@` Domain-part (255).
- Convert **chữ thường** (lower-case).
- Không ký tự đặc biệt, trừ `.` `_` `-`.

### 4.2. Số điện thoại — `Varchar(44)`
- **10 – 44 số**; chỉ số và dấu `+` ở đầu.
- Tự loại khoảng trắng: `0123 456` → `0123456`.

### 4.3. Mật khẩu — **6 – 50 ký tự**
- Web Admin: **Min 8, Max 50**.
- Bắt buộc gồm: chữ hoa + chữ thường + số + ký tự đặc biệt.
- UI: ẩn `****`, có icon con mắt bật/tắt.

## 5. Giải phẫu Form nhập liệu

- Trường bắt buộc: dấu `*` màu đỏ `#F22128` cạnh Label.
- Inline error: chữ đỏ **ngay dưới ô nhập** (vd `"Đây là trường bắt buộc"`).
- Nút phụ (Discard/Hủy): xám `#555D6B`.
- Nút chính: **Disable mặc định**; chỉ Enable khi đủ trường bắt buộc + đúng định dạng.
- Tiêu đề dialog thêm mới: `"Thêm mới [tên thực thể]"` (vd `"Thêm mới Người dùng"`).

## 6. Xử lý chuỗi & luồng sự kiện

### 6.1. Khoảng trắng
- Trường bắt buộc nhập **toàn khoảng trắng** → chặn, báo `"Đây là trường bắt buộc"`.
- Hợp lệ → **Trim** đầu/cuối rồi mới lưu.

### 6.2. Debounce
- Click liên tục (double-click) Save/Submit → chặn sinh nhiều event, chỉ xử lý **1 event** trong một khoảng thời gian.

## 7. Giải phẫu màn hình danh sách (Data Grid)

| Yếu tố | Quy ước |
|---|---|
| Sticky Header | Hàng tiêu đề + bộ lọc **cố định (sticky)** khi cuộn |
| Zebra Striping | Màu nền dòng **xen kẽ** |
| Cột Tác vụ & STT | Căn **giữa** |
| Cột Chữ | Căn **trái** |
| Cột Số / Tiền | Căn **phải** |
| Phân trang | `{10, 20, 50, 100}` bản ghi/trang |
| Nút Xóa | Chỉ hiện khi có **≥1 checkbox tích**; màu đỏ |

## 8. Logic tìm kiếm & lọc

### 8.1. Text Search
- **Không phân biệt hoa thường**: `"Nguyễn Văn A"` = `"nguyễn văn a"`.
- **Bỏ qua khoảng trắng thừa**.
- Tìm khi ấn **Enter** hoặc nút **Tìm kiếm** — **KHÔNG realtime ở Textbox**. Realtime chỉ cho **Dropdown search**.

### 8.2. Date Picker (Từ ngày – Đến ngày)
- Không cho "Từ ngày" > "Đến ngày".
- Nhập sai bằng phím → báo đỏ `"Dữ liệu không hợp lệ"`.
- Chọn từ Calendar, hoặc nhập tay đúng `dd/MM/yyyy`.

## 9. Ma trận phản hồi hệ thống

| Kênh | Vị trí | Dùng cho | Nội dung |
|---|---|---|---|
| **Toast** | Góc dưới phải | Kết quả thao tác (Thêm/Sửa/Xóa/Import) | `"Cập nhật thành công!"` · `"Xóa thành công x/y bản ghi"` |
| **Popup Alert** | Giữa màn hình | Xác nhận nguy hiểm (Xóa) / cảnh báo ràng buộc | `"Bạn có chắc chắn muốn xóa?"` · `"Lỗi: Không được xóa do dữ liệu đang sử dụng"` |
| **Inline Text** | Chữ đỏ dưới ô nhập | Lỗi validate / trùng dữ liệu | `"$Trường_thông_tin$ đã tồn tại"` (check khi rời ô nhập) |

- Popup xóa: nút `"Cancel"` / `"Confirm"`; nền sau **làm mờ (blur)**.
- Mỗi mutation (Tạo/Sửa/Xóa/Import/Chia sẻ) bắn **ĐÚNG 1 toast**, đủ **cả 2 nhánh** thành công + thất bại.
- Chuỗi lấy **nguyên văn** (bảng trên hoặc spec). Chưa có → DỪNG, báo. Không tự chế.
- Đúng KÊNH: validate trường → Inline; kết quả/lỗi hệ thống → Toast; xác nhận nguy hiểm → Popup.
- Backend trả message **khớp nguyên văn** chuỗi frontend hiển thị.

## 10. Hệ màu & quy chuẩn nút bấm

- Kích thước: **W 120px × H 36px** (trừ nút icon/text dài). Font **14px Sans-serif**.

| Loại | Dùng cho | Màu |
|---|---|---|
| **Primary** | Thêm mới, Lưu, Tìm kiếm, Import | Nền xanh `#056887`, chữ trắng; **hover** vàng `#FFB821`, chữ đen |
| **Danger** | Xóa | Nền đỏ `#F22128`, chữ trắng |
| **Neutral** | Hủy / Discard / Đóng | Nền xám `#555D6B`, chữ trắng |

## 11. Combobox & Checkbox phân quyền

### 11.1. Combobox (Dropdown)
- Trường **không bắt buộc**: có icon `(x)` để xóa giá trị đã chọn.
- Trường **bắt buộc**: **không** có icon `(x)`.
- Dropdown có Search: realtime trong danh sách xổ; không kết quả → `"Không có dữ liệu"`.

### 11.2. Tree Checkbox (phân quyền)
- Tick **module cha** → tự tick **toàn bộ** quyền con.
- Tick **Thêm/Sửa/Xóa** → tự tick **"Xem"**.
- Bỏ tick **"Xem"** → tự bỏ **tất cả** quyền còn lại.

## 12. Quy chuẩn tải file đính kèm

- Validate định dạng + dung lượng **trước** upload. Sai → loại file ngay, báo chữ đỏ dưới khung.
- Luôn có nút `X` xóa file trước khi Lưu.

| Loại | Giới hạn | Định dạng | Ghi chú |
|---|---|---|---|
| Hình ảnh | **5MB** | `.jpg, .jpeg, .png, .bmp` | Hover xem trước (preview) |
| Tài liệu | **30MB – 50MB** | `.pdf, .docx, .xlsx, .zip…` | — |

## 13. Lưu đồ xử lý nhập dữ liệu (Import Flow)

- Step 1 — Template: nút `"Tải file mẫu"` chuẩn định dạng.
- Step 2 — Upload: kéo thả / chọn file, **chặn tối đa 1000 bản ghi/lần**.
- Step 3 — Server Validation: quét lỗi định dạng, bỏ trống trường bắt buộc, trùng DB.
- Step 4 — Result Panel: Toast `"Nhập dữ liệu thành công"`; bảng tóm tắt Tổng số dòng · Thành công (xanh) · Thất bại (đỏ); View Detail tải file chi tiết lỗi (cột lý do ở cuối).

## 14. Developer Pre-Release Checklist

- [ ] Nút Submit/Lưu **Disable mặc định**, chỉ **Enable khi form hợp lệ**.
- [ ] **Debounce** (chặn double-click) cho **mọi** nút Action.
- [ ] Textbox **Trim khoảng trắng 2 đầu**.
- [ ] Chặn nhập **toàn khoảng trắng** vào trường bắt buộc.
- [ ] Mật khẩu **hash**, không lưu plaintext.
- [ ] Popup xóa làm **mờ background (blur)**.
- [ ] Validation DB (trùng Name/Code) trả **đúng thông báo lỗi dưới ô nhập**.
- [ ] Mỗi mutation ghi **đúng 1 audit log** hành động/tài nguyên chuẩn (§15).
- [ ] Tác vụ **thiếu quyền** bị **ẩn** (không chỉ disable) + chặn ở **server** (§16).
- [ ] Sau Tạo/Sửa/Xóa/Di chuyển, list/cây **tự reload**, tên mới đồng bộ mọi màn (§17).
- [ ] File Export **khớp bộ lọc/cột hiển thị** + **chống CSV injection** (§18).

## 15. Nhật ký hệ thống (Audit Log)

- Mỗi thao tác thay đổi trạng thái = **ĐÚNG 1 bản ghi audit**. Áp dụng: Tạo, Chỉnh sửa, Xóa, Chia sẻ/Bỏ chia sẻ, Kích hoạt/Vô hiệu hóa, Khôi phục phiên bản, Tải lên, Tải xuống, Xuất tài liệu, Đăng nhập/Đăng xuất, và Xem khi nghiệp vụ yêu cầu.
- **Cấm double-log**: 1 hành động = 1 entry (đừng gọi API 2 lần / log 2 tầng).
- Động từ chuẩn hóa:

| Đúng | Không dùng | Phân biệt |
|---|---|---|
| `Chỉnh sửa` | "Cập nhật", "Sửa", "Edit" | Thống nhất §6 |
| `Tải xuống` | "Xuất file" | ≠ Xuất tài liệu |
| `Xuất tài liệu` | "Xuất Excel", "Tải xuống" | = sinh file mới từ dữ liệu |
| `Xem trước` | "Xem", "Tải xuống" | Preview ≠ mở/tải |
| `Xem` | "Xem trước" | Chỉ khi thực mở nội dung |

- `resourceType` **xác định**, không trống / không `"unknown"` (Tài liệu / Thư mục / Người dùng / Vai trò / Phòng ban / Thuật ngữ / Danh mục…) + định danh bản ghi.
- Có bảng ánh xạ hành động ↔ chuỗi hiển thị ở backend; không hardcode rải rác.

## 16. Phân quyền lúc chạy (Runtime Authorization)

- **Ẩn, không disable**: tác vụ user không có quyền (Xóa/Sửa/Tải xuống/Chia sẻ) → ẩn hẳn, không hiển thị mờ.
- **Enforce server MỌI endpoint**: mỗi API tự kiểm quyền server-side, kể cả khi UI đã ẩn. (Ẩn UI = trải nghiệm; chặn server = bảo mật — cần cả hai.)
- **Chia sẻ cascade**: share/bỏ share thư mục cha kế thừa xuống con; đổi quyền cha cập nhật con.
- **Data-scope theo phòng ban**: trả dữ liệu giới hạn scope user, không trả rồi mới ẩn ở client.
- Không để RAG/search/API phụ **lách** lớp phân quyền.

## 17. Đồng bộ sau thao tác & trùng dữ liệu

- **Reload sau mutation**: sau Tạo/Đổi tên/Di chuyển/Xóa, tự reload list/cây **và** mọi màn tham chiếu bản ghi (breadcrumb, tiêu đề). Không để tên cũ sót.
- **Check trùng đúng scope**: uniqueness trong đúng phạm vi nghiệp vụ (cùng cấp thư mục / cùng danh mục / cùng phòng ban), không phải toàn hệ thống.
- **Soft-delete ↔ uniqueness**: khi có bản đã xóa mềm cùng tên/mã, quy định **tường minh** cho tái dùng hay báo trùng. Không để mơ hồ.

## 18. Toàn vẹn Export & chống CSV injection

- Export **khớp dữ liệu đang hiển thị**: đúng bộ lọc/sort/cột đang bật tại thời điểm bấm Xuất.
- **Chống CSV injection**: ô bắt đầu bằng `=` `+` `-` `@` (và tab/CR) phải **escape** (prefix `'` hoặc bọc) trước khi ghi CSV/XLSX.
- **BOM UTF-8** cho file tiếng Việt.
- Tên file: `[Tên chức năng]_[ddMMyyyy]`.

## 19. Vòng đời phiên & xác thực

- **Auto-logout** khi tài khoản bị khóa hoặc **sau đổi mật khẩu** (buộc đăng xuất phiên hiện tại/khác).
- **Xác nhận trước khi đăng xuất** nếu đang có thao tác dở.
- **Side-effect chỉ chạy SAU xác nhận**: không đăng xuất/xóa/gửi trước khi bấm nút xác nhận.
- **ESC / click nền không tự đóng** form đang nhập dở mà chưa hỏi.
- **Chặn double-submit** (chống gọi API 2 lần), nhất là thao tác không idempotent.
