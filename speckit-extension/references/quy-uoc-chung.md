# THE DFT STANDARD — Quy Ước Chung Cho Phát Triển Hệ Thống (Frontend · Backend · QA)

> Bản thiết kế cốt lõi cho sự nhất quán, tối ưu UX/UI và giảm thiểu lỗi trên toàn bộ hệ sinh thái dự án DFT (mHome, sMartT, TIMS, QLCCU, Quản lý tài sản).
>
> Đây là **luật** áp cho **mọi** project DFT. Mọi chuỗi trong ngoặc kép phải dùng **nguyên văn**, không diễn đạt lại. Nguồn: `QUC.V1` (The DFT Standard).

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

> **Ghi chú nguồn**: mục 1–14 lấy nguyên từ `QUC.V1` (The DFT Standard). Mục 15–19 là phần **bổ sung** do rút ra từ thống kê bug thực tế (dms-chatbot-poc, 2026-07) — bịt các khoảng trống mà bản gốc chưa phủ. Khi bản gốc cập nhật có các mục này, hãy hợp nhất.

---

## 1. Kiến trúc của sự nhất quán

Bốn trụ cột của DFT Standard:

- **Dữ liệu lõi (Backend)** — quy chuẩn kiểu dữ liệu, giới hạn ký tự (MaxLength) và định dạng chuẩn hóa tại Database.
- **Tương tác & Validate (Interaction)** — luồng xử lý sự kiện (Debounce), tự động cắt chuỗi (Trim), và ma trận kiểm chuẩn đầu vào.
- **Giao diện (UI Components)** — cấu trúc Form, Grid, Nút bấm và quy tắc sử dụng hệ màu thương hiệu.
- **Phản hồi hệ thống (Feedback)** — logic hiển thị Toast, Popup và Text cảnh báo Inline theo thời gian thực.

## 2. Ký hiệu quy trình (Flowchart Standards)

| Ký hiệu | Ý nghĩa |
|---|---|
| Hình bầu dục (Oval) | Khởi đầu hoặc kết thúc quy trình |
| Hình bình hành | Thông tin hoặc dữ liệu đầu vào |
| Hình chữ nhật | Thao tác, xử lý thông tin tự động trong hệ thống |
| Hình thang | Thao tác xử lý thủ công (bằng tay) |
| Hình kim cương | Nút thắt ra quyết định (có điều kiện rẽ nhánh) |
| Hình tài liệu | Hồ sơ, biên bản, báo cáo đầu ra |

## 3. Ma trận kiểu dữ liệu lõi (Database Conventions)

| Trường thông tin | Kiểu dữ liệu | Quy tắc ràng buộc |
|---|---|---|
| Tên / Tên hiển thị | `Varchar(255)` | Viết hoa chữ cái đầu; tự động loại bỏ khoảng cách thừa |
| Mã (Code/ID) | `Varchar(50)` | Không ký tự đặc biệt, không khoảng trắng, trừ `_` hoặc `-` |
| Ghi chú / Mô tả | `Varchar(4000)` | Cho phép ký tự đặc biệt và xuống dòng |
| Tiền (VND) | `Decimal(18,0)` | Không chứa phần thập phân; dùng dấu `.` ngăn cách hàng nghìn |
| Số lượng (thập phân) / Tỉ lệ | `Decimal(18,2)` / `Decimal(5,2)` | Tối đa 2 chữ số sau dấu phẩy |
| Mật khẩu | `Varchar(128)` max | Bắt buộc mã hóa / hash; **tuyệt đối không lưu plaintext** |

## 4. Ma trận kiểm chuẩn dữ liệu phức tạp

### 4.1. Email — `Varchar(320)`

- Cấu trúc: Local-part (64) `@` Domain-part (255).
- Rule: mặc định convert về **chữ thường** (lower-case).
- Ký tự: không ký tự đặc biệt, trừ `.`, `_`, `-`.

### 4.2. Số điện thoại — `Varchar(44)`

- Nhập từ **10 – 44 số**.
- Rule: chỉ cho phép số và dấu `+` ở đầu.
- Hệ thống tự loại bỏ khoảng trắng — ví dụ `0123 456` → `0123456`.

### 4.3. Mật khẩu — **6 – 50 ký tự**

- Web Admin: **Min 8, Max 50**.
- Rule: bắt buộc gồm chữ hoa + chữ thường + số + ký tự đặc biệt.
- UI: hiển thị dạng ẩn `****`, có icon con mắt bật/tắt hiển thị.

## 5. Giải phẫu Form nhập liệu (Form Anatomy)

- **Bắt buộc nhập**: phải có dấu `*` màu đỏ (`#F22128`) cạnh Label.
- **Cảnh báo Inline**: chữ màu đỏ báo lỗi **ngay dưới ô nhập**. (Ví dụ: `"Đây là trường bắt buộc"`.)
- **Nút phụ (Discard/Hủy)**: luôn dùng màu xám `#555D6B`.
- **Trạng thái nút chính**: **Disable mặc định**; chỉ **Enable** khi nhập đủ các trường bắt buộc và đúng định dạng.
- Tiêu đề dialog thêm mới: dạng `"Thêm mới [tên thực thể]"` (ví dụ `"Thêm mới Người dùng"`).

## 6. Xử lý chuỗi & luồng sự kiện tương tác

### 6.1. Quy tắc khoảng trắng (White-space Rule)

- Trường **bắt buộc** mà nhập **toàn khoảng trắng** → **chặn và báo lỗi** `"Đây là trường bắt buộc"`.
- Trường hợp lệ → hệ thống **tự động Trim** (cắt khoảng trắng thừa đầu/cuối) rồi mới lưu.

### 6.2. Chống spam click (Debounce Event)

- Khi user click liên tục (double-click) vào nút Save/Submit, hệ thống **bắt buộc chặn sinh nhiều event**, chỉ ghi nhận và xử lý **1 event duy nhất** trong một khoảng thời gian.

## 7. Giải phẫu màn hình danh sách (The Data Grid)

| Yếu tố | Quy ước |
|---|---|
| Sticky Header | Hàng tiêu đề và bộ lọc luôn **cố định (sticky)** khi cuộn |
| Zebra Striping | Dòng hiển thị màu nền **xen kẽ** để dễ đọc |
| Cột Tác vụ & STT | Căn **giữa** (Center) |
| Cột Chữ | Căn **trái** (Left) |
| Cột Số / Tiền | Căn **phải** (Right) |
| Phân trang | Cho phép chọn `{10, 20, 50, 100}` bản ghi/trang |
| Nút Xóa | Chỉ hiện phía trên danh sách khi có **ít nhất 1 checkbox được tích**; nút màu đỏ |

## 8. Logic tìm kiếm & lọc (Search & Filter Behavior)

### 8.1. Text Search

- **Không phân biệt hoa thường** (case-insensitive): `"Nguyễn Văn A"` và `"nguyễn văn a"` trả về kết quả như nhau.
- **Bỏ qua khoảng trắng thừa**: tìm `"  Nguyễn  Văn  A  "` vẫn trả kết quả chuẩn.
- **Thực hiện tìm kiếm**: khi ấn phím **Enter** hoặc nút **Tìm kiếm** — **KHÔNG tìm realtime ở Textbox**. Realtime chỉ áp dụng cho **Dropdown search**.

### 8.2. Date Picker (Từ ngày – Đến ngày)

- Ràng buộc logic: **không cho phép chọn "Từ ngày" lớn hơn "Đến ngày"**.
- Nếu nhập sai bằng phím → báo lỗi đỏ `"Dữ liệu không hợp lệ"`.
- Bắt buộc chọn từ Calendar, hoặc nhập tay **đúng định dạng** `dd/MM/yyyy`.

## 9. Ma trận phản hồi hệ thống (When to use what?)

| Kênh | Vị trí | Dùng cho | Nội dung |
|---|---|---|---|
| **Toast** | Góc dưới phải | Thao tác thành công / thất bại chung (Thêm, Sửa, Xóa, Import) | `"Cập nhật thành công!"` · `"Xóa thành công x/y bản ghi"` |
| **Popup Alert** | Giữa màn hình | Xác nhận hành động nguy hiểm (Xóa) hoặc cảnh báo ràng buộc hệ thống | `"Bạn có chắc chắn muốn xóa?"` · `"Lỗi: Không được xóa do dữ liệu đang sử dụng"` |
| **Inline Text** | Chữ đỏ dưới ô nhập | Lỗi validate form hoặc trùng lặp dữ liệu (Existed) | `"$Trường_thông_tin$ đã tồn tại"` (check ngay khi rời khỏi ô nhập) |

- Popup xác nhận xóa: nút `"Cancel"` / `"Confirm"`; nền màn hình phía sau phải được **làm mờ (blur)**.

**Luật bắt buộc (rút từ ~55 bug sai/thiếu thông báo):**

- **Mỗi thao tác mutation (Tạo/Sửa/Xóa/Import/Chia sẻ…) phải bắn ĐÚNG 1 toast** — và phải xử lý **đủ cả hai nhánh** thành công lẫn thất bại. Thiếu toast ở nhánh nào cũng là bug.
- **Không tự chế nội dung thông báo.** Mọi chuỗi phải lấy **nguyên văn** từ bảng trên (hoặc từ spec). Chưa có chuỗi → **DỪNG và hỏi**, không tự sinh.
- **Đúng KÊNH**: lỗi validate trường → Inline; kết quả thao tác / lỗi hệ thống → Toast; xác nhận nguy hiểm → Popup. Dùng sai kênh (vd toast cho lỗi validate) là bug.
- **Backend ↔ Frontend phải khớp chuỗi**: message/nội dung backend trả về phải đúng chuỗi mà frontend hiển thị cho người dùng — không để backend trả một đằng, frontend map một nẻo.

## 10. Hệ màu & quy chuẩn nút bấm (Action UI Kit)

- Quy chuẩn kích thước: **W 120px × H 36px** (trừ nút icon / text dài). Font **14px Sans-serif**.

| Loại nút | Dùng cho | Màu |
|---|---|---|
| **Primary Action** | Thêm mới, Lưu, Tìm kiếm, Import | Nền xanh `#056887`, chữ trắng — **hover**: vàng `#FFB821`, chữ đen |
| **Danger Action** | Xóa | Nền đỏ `#F22128`, chữ trắng |
| **Neutral Action** | Hủy / Discard / Đóng | Nền xám `#555D6B`, chữ trắng |

## 11. Hành vi Combobox & Checkbox phân quyền

### 11.1. Combobox (Dropdown)

- Trường **không bắt buộc**: bắt buộc có icon `(x)` để xóa trắng giá trị đã chọn.
- Trường **bắt buộc**: **không** có icon `(x)` để xóa giá trị.
- **Dropdown có Search**: hỗ trợ tìm kiếm realtime ngay trong danh sách xổ xuống. Không có kết quả → báo `"Không có dữ liệu"`.

### 11.2. Phân quyền / Cấu trúc cây (Tree Checkbox)

- Tick **module cha** → tự động tick **toàn bộ** quyền con.
- Tick **Thêm / Sửa / Xóa** → tự động tick quyền **"Xem"**.
- Bỏ tick quyền **"Xem"** → tự động bỏ tick **tất cả** các quyền còn lại.

## 12. Quy chuẩn tải file đính kèm (Upload Rules)

- **Cơ chế validation**: hệ thống tự kiểm tra định dạng và dung lượng **trước** khi upload. Sai → **loại bỏ file ngay** và báo chữ đỏ dưới khung.
- **Thao tác**: luôn có nút `X` để xóa file trước khi ấn Lưu.

| Loại | Giới hạn | Định dạng | Ghi chú |
|---|---|---|---|
| Hình ảnh (Image) | Tối đa **5MB** | `.jpg, .jpeg, .png, .bmp` | Có thể hover vào tệp để xem trước (preview) |
| Tài liệu (Document) | Tối đa **30MB – 50MB** | `.pdf, .docx, .xlsx, .zip…` | — |

## 13. Lưu đồ xử lý nhập dữ liệu (The Import Flow)

- **Step 1 — Template**: cung cấp nút `"Tải file mẫu"` (Download Template) chuẩn định dạng.
- **Step 2 — Upload**: user kéo thả (drag & drop) hoặc chọn file — **chặn tối đa 1000 bản ghi/lần**.
- **Step 3 — Server Validation**: hệ thống tự quét lỗi định dạng, bỏ trống trường bắt buộc, hoặc trùng lặp dữ liệu DB.
- **Step 4 — Result Panel**:
  - Hiển thị Toast `"Nhập dữ liệu thành công"`.
  - Bảng tóm tắt: **Tổng số dòng** · **Thành công** (xanh) · **Thất bại** (đỏ).
  - **View Detail**: tải về file chi tiết báo lỗi (có cột lý do lỗi ở cuối để user sửa).

## 14. Developer Pre-Release Checklist

- [ ] Nút Submit/Lưu đã được **Disable mặc định** và chỉ **Enable khi form hợp lệ** chưa?
- [ ] Đã xử lý sự kiện **Debounce** (chặn double-click) cho **mọi** nút Action chưa?
- [ ] Textbox đã tự động **Trim khoảng trắng 2 đầu** chưa?
- [ ] Đã chặn người dùng nhập **khoảng trắng toàn bộ** vào trường bắt buộc chưa?
- [ ] Mật khẩu đã được **hash** và tuyệt đối không lưu plaintext chưa?
- [ ] Popup cảnh báo xóa đã làm **mờ màn hình background (blur)** chưa?
- [ ] Validation DB (check trùng lặp Name/Code) đã trả về **đúng thông báo lỗi dưới ô nhập** chưa?
- [ ] Mỗi mutation đã ghi **đúng 1 audit log** với hành động/tài nguyên chuẩn chưa? (§15)
- [ ] Tác vụ user **thiếu quyền** đã bị **ẩn** (không chỉ disable) và chặn ở **server** chưa? (§16)
- [ ] Sau Tạo/Sửa/Xóa/Di chuyển, list/cây đã **tự reload** và tên mới đồng bộ mọi màn chưa? (§17)
- [ ] File Export có **khớp bộ lọc/cột đang hiển thị** và **chống CSV injection** chưa? (§18)

---

## 15. Nhật ký hệ thống (Audit Log)

> Bổ sung — bản gốc chưa có. Rút từ ~35 bug: sai hành động, tài nguyên "unknown", không lưu, hoặc lưu 2 lần.

- **Mỗi thao tác thay đổi trạng thái = ĐÚNG 1 bản ghi audit.** Áp dụng cho: Tạo, Chỉnh sửa, Xóa, Chia sẻ / Bỏ chia sẻ, Kích hoạt / Vô hiệu hóa, Khôi phục phiên bản, Tải lên, Tải xuống, Xuất tài liệu, Đăng nhập / Đăng xuất, và Xem khi nghiệp vụ yêu cầu ghi lại.
- **Cấm double-log**: một thao tác không được sinh 2 log (thường do gọi API 2 lần hoặc log ở cả 2 tầng). Một hành động của người dùng = một entry.
- **Động từ hành động phải chuẩn hóa** — dùng đúng thuật ngữ, không lẫn:

| Đúng | Không dùng | Phân biệt |
|---|---|---|
| `Chỉnh sửa` | "Cập nhật", "Sửa", "Edit" | Thống nhất với §6 form |
| `Tải xuống` | "Xuất file" | Tải xuống ≠ Xuất tài liệu (2 hành động khác nhau) |
| `Xuất tài liệu` | "Xuất Excel", "Tải xuống" | Xuất = sinh file mới từ dữ liệu |
| `Xem trước` | "Xem", "Tải xuống" | Preview ≠ mở/tải |
| `Xem` | "Xem trước" | Chỉ khi thực sự mở nội dung |

- **`resourceType` phải xác định** — không được để trống hay `"unknown"`. Mỗi log ghi rõ loại tài nguyên (Tài liệu / Thư mục / Người dùng / Vai trò / Phòng ban / Thuật ngữ / Danh mục…) và định danh bản ghi.
- **Có bảng ánh xạ hành động ↔ chuỗi hiển thị** ở tầng backend, đối chiếu trước khi commit; không hardcode rải rác mỗi nơi một kiểu.

## 16. Phân quyền lúc chạy (Runtime Authorization)

> Bổ sung — §11 chỉ nói checkbox cây. Rút từ ~30 bug: lộ tác vụ, share không cascade, lộ scope.

- **Ẩn, không chỉ disable.** Tác vụ mà user không có quyền (Xóa / Sửa / Tải xuống / Chia sẻ…) phải **ẩn hẳn** khỏi UI, không hiển thị dạng mờ. Nút mờ vẫn là rò rỉ thông tin về khả năng.
- **Enforce ở server cho MỌI endpoint.** Không tin client: mỗi API mutation/truy vấn phải tự kiểm quyền server-side, kể cả khi UI đã ẩn nút. Ẩn UI là trải nghiệm, chặn server là bảo mật — phải có cả hai.
- **Chia sẻ phải cascade.** Chia sẻ / bỏ chia sẻ ở thư mục cha phải kế thừa xuống tài liệu/thư mục con. Đổi quyền ở cấp cha phải cập nhật cấp con; không để con "mồ côi" quyền cũ.
- **Data-scoping theo phòng ban.** Dữ liệu trả về phải giới hạn theo scope (phòng ban/đơn vị) của user hiện tại — không trả bản ghi ngoài phạm vi rồi mới ẩn ở client.
- Không được để RAG / tìm kiếm / API phụ **lách** qua lớp phân quyền (vd chatbot trích dẫn tài liệu mật mà user không có quyền đọc).

## 17. Đồng bộ sau thao tác & trùng dữ liệu

> Bổ sung. Rút từ ~25 bug: đổi tên xong màn khác vẫn tên cũ; check trùng sai với bản ghi đã xóa mềm.

- **Reload phạm vi ảnh hưởng sau mutation.** Sau Tạo / Đổi tên / Di chuyển / Xóa, tự động reload list hoặc cây, **và** mọi màn đang tham chiếu bản ghi đó (tên mới phải đồng bộ khắp nơi — breadcrumb, tiêu đề, màn liên quan). Không để tên cũ tồn tại ở một màn khác.
- **Check trùng theo đúng scope.** Uniqueness xét trong đúng phạm vi nghiệp vụ (tên trong cùng cấp thư mục / cùng danh mục / cùng phòng ban), không phải toàn hệ thống một cách máy móc.
- **Soft-delete ↔ uniqueness phải quyết định rõ ràng.** Khi tồn tại bản ghi đã xóa mềm cùng tên/mã: quy định **tường minh** là cho phép tái dùng tên hay báo trùng. Không để logic mơ hồ gây vừa false-positive (báo trùng với bản đã xóa) vừa false-negative.

## 18. Toàn vẹn Export & chống CSV injection

> Bổ sung — §12/§13 nói upload/import, chưa nói export. Rút từ ~15 bug.

- **File export phải KHỚP dữ liệu đang hiển thị**: đúng bộ lọc, đúng sort, đúng cột đang bật trên màn hình tại thời điểm bấm Xuất. Không xuất toàn bộ khi màn đang lọc.
- **Chống CSV injection**: ô bắt đầu bằng `=`, `+`, `-`, `@` (và tab/CR) phải được **escape** (prefix `'` hoặc bọc) trước khi ghi CSV/XLSX — tránh công thức chạy khi mở bằng Excel.
- **BOM UTF-8** cho file có tiếng Việt (đồng bộ §12).
- Tên file theo chuẩn `[Tên chức năng]_[ddMMyyyy]`.

## 19. Vòng đời phiên & xác thực

> Bổ sung. Rút từ nhóm bug session/auth.

- **Auto-logout khi mất hiệu lực**: tài khoản bị khóa, hoặc **sau khi đổi mật khẩu**, phải buộc đăng xuất phiên hiện tại/các phiên khác.
- **Xác nhận trước khi đăng xuất** nếu người dùng đang có thao tác dở.
- **Side-effect chỉ chạy SAU khi xác nhận**: không đăng xuất / xóa / gửi trước khi người dùng bấm nút xác nhận trong popup.
- **ESC / click nền không được tự đóng** form đang nhập dở mà chưa hỏi (tránh mất dữ liệu). Đồng bộ với §6 (xác nhận khi hủy lúc đã nhập).
- **Chặn double-submit**: chống gọi API 2 lần do double-click (đồng bộ Debounce §6.2) — đặc biệt các thao tác không idempotent (tạo bản ghi, gửi, thanh toán).
