# QUY ƯỚC CHUNG TOÀN HỆ THỐNG (QUCTHT V1.0)

LUẬT cho MỌI project DFT. Chuỗi trong `" "` dùng **nguyên văn**. Mục 1–20 = docx QUCTHT V1.0; mục 21 = bổ sung DFT.

## Mục lục

1. Kiểu dữ liệu chung
2. Ràng buộc độ dài trường
3. Từng loại trường nhập liệu
4. Tệp tải lên
5. Thuật ngữ chuẩn giao diện
6. Font & độ phân giải
7. Bảng dữ liệu (Data Grid)
8. Form Tạo mới / Chỉnh sửa
9. Dialog xác nhận xóa
10. Phân loại thông báo (Inline / Toast)
11. Thông báo lỗi Validation
12. Định dạng ngày giờ
13. Nhập / Xuất dữ liệu
14. Loading / Breadcrumb / Debounce
15. Quản lý dữ liệu & soft-delete
16. Trạng thái & màu bản ghi
17. Xử lý trùng dữ liệu
18. Phiên đăng nhập, xác thực & rate limit
19. Phân quyền ACL & phạm vi dữ liệu
20. Lưu ý triển khai
21. Bổ sung DFT (audit log, phân quyền runtime, đồng bộ sau thao tác)

---

## 1. Kiểu dữ liệu chung

| Loại | Kiểu | Ràng buộc |
|---|---|---|
| Tiền (VND) | `decimal(18,0)` | Không thập phân; dấu `.` phân cách nghìn |
| Số lượng nguyên | `int` | Không âm |
| Số lượng thập phân | `decimal(18,2)` | ≤2 chữ số thập phân |
| Tỷ lệ / % | `decimal(5,2)` | 0,00–100,00 |
| STT | `int` | Không null |
| **Khóa chính** | **UUID v4** | `8-4-4-4-12` hex; KHÔNG int auto-increment |
| Tài chính / độ chính xác cao | `decimal` | KHÔNG `float`/`double` |
| Thời điểm | `datetime` | UTC+7 |

## 2. Độ dài trường (nguồn DUY NHẤT)

| Trường | Tối đa | Ràng buộc |
|---|---|---|
| Mã (code/taxCode/productCode) | **50** | Không ký tự đặc biệt trừ `_` `-`; không khoảng trắng đầu/cuối |
| Tên / Contact Name | **255** | Unicode tiếng Việt; tự viết hoa chữ cái đầu khi hiển thị |
| Email | **255** | 1 dấu `@`, không khoảng trắng (§3) |
| Số điện thoại | **12** | §3 |
| Mật khẩu | **128** (hash) | Nhập ≥**8**; lưu hash, không plaintext |
| URL / File path | **500** | Ưu tiên HTTPS |
| Mô tả / Notes | **4000** | Cho phép ký tự đặc biệt + xuống dòng |
| Tên thư mục / tài liệu | **255** | Không chứa `/ \ : * ? " \|` |

## 3. Từng loại trường nhập liệu

- **Textbox**: trim khi lưu; toàn khoảng trắng ở trường bắt buộc → chặn; chặn nhập vượt §2 tại ô.
- **Email**: 1 `@`; trước `@` chữ/số/`. _ % + -`, không mở/kết bằng `.`, không `..`; sau `@` chữ/số/`.`/`-`, ≥1 `.`, tên miền ≥2 chữ; không khoảng trắng; check trùng không phân biệt hoa thường. Sai → `"Địa chỉ email không hợp lệ."`
- **Số điện thoại**: chỉ `0–9` + `+` ở đầu; bỏ khoảng trắng; trống hợp lệ nếu không bắt buộc; `0xxxxxxxxx` (10 số, đầu `0`) hoặc `+84xxxxxxxxx` (12 ký tự). Sai → `"Số điện thoại không hợp lệ."`
- **Date Picker**: `dd/MM/yyyy`; khoảng `dd/MM/yyyy - dd/MM/yyyy`; bắt đầu > kết thúc → `"Dữ liệu không hợp lệ."`; **chỉ chọn qua calendar, KHÔNG nhập tay**.
- **Số**: chỉ số dương (âm → khai BRD); nghìn dấu `.`; thập phân dấu `,` ≤2 (`2,21`).
- **Tiền VNĐ**: chỉ số; hiển thị `5.000.000 VNĐ`; không thập phân.
- **Tỷ lệ %**: chỉ số; `90%` / `99,22%`; 0,00–100,00; vượt → `"Dữ liệu không hợp lệ."`
- **Mật khẩu**: ≥8, bắt buộc hoa+thường+số+đặc biệt; ẩn `****` + nút bật/tắt. Sai → `"Mật khẩu tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."`; không khớp → `"Mật khẩu xác nhận không khớp."`
- **Mã tự sinh**: không cho sửa; placeholder `"Mã tự sinh"`.
- **Dropdown single**: chọn 1 giá trị.
- **Checkbox multi**: tick nhiều giá trị 1 nhóm.
- **Checkbox phân quyền (cây)**: tick cha → tick toàn bộ con; tick Thêm/Sửa/Xóa → tự tick **Xem**; bỏ tick **Xem** → bỏ toàn bộ quyền còn lại.

## 4. Tệp tải lên

| Loại | Kiểu | Định dạng | Số | DL/tệp | Tổng |
|---|---|---|---|---|---|
| Ảnh đại diện/logo/chữ ký | SINGLE | `JPG, PNG, WEBP` | 1 | **2 MB** | 2 MB |
| Nhập hàng loạt | SINGLE | `CSV, XLSX` | 1 | **10 MB, ≤5.000 dòng** | 10 MB |
| Đính kèm chung | MULTI | `PDF, DOCX, XLSX, JPG, PNG` | 10 | **25 MB** | 50 MB |

- SINGLE thay tệp cũ; MULTI thêm vào danh sách. Không `.xls` (chỉ `.xlsx`). Client kiểm khi chọn; **server kiểm lại toàn bộ, không tin client**.
- Trần cứng: 20 tệp/trường, 50 MB/tệp, 200 MB tổng.
- Kỹ thuật: ảnh cắt vuông + thu 512px + xóa EXIF, không giữ gốc; kiểm định dạng theo magic-byte; đọc/ghi theo luồng; endpoint upload riêng; 60 lần/phút/user; tệp tạm xóa sau 24h; tệp của bản ghi xóa-mềm xóa hẳn sau 90 ngày.
- Lỗi: `"Định dạng tệp không hợp lệ. Vui lòng chọn tệp [danh sách định dạng cho phép]."` · `"Dung lượng tệp vượt quá giới hạn cho phép ({limit}MB)."` · `"Tệp nhập vượt quá {maxRows} dòng. Vui lòng chia nhỏ tệp."` · `"Chỉ được tải lên tối đa {maxFiles} tệp."` · `"Tổng dung lượng các tệp vượt quá {maxTotalSize}MB."` · `"Tệp '{tên}' đã được chọn."` · gợi ý `"Hỗ trợ [định dạng]. Tối đa [giới hạn]MB."`

## 5. Thuật ngữ chuẩn (nhãn nút / tiêu đề / menu / thông báo / BRD)

| Hành động | CHUẨN | CẤM |
|---|---|---|
| Tạo | `"Tạo mới"` | Thêm mới, Thêm, Add, New |
| Sửa | `"Chỉnh sửa"` | Sửa, Cập nhật, Edit |
| Xóa | `"Xóa"` | Loại bỏ, Delete |
| Lưu | `"Lưu thay đổi"` | Lưu lại, Save |
| Hủy | `"Hủy"` | Đóng, Thoát, Cancel |
| Xuất | `"Xuất tài liệu"` | Xuất CSV/Excel/file, Export |
| Nhập | `"Nhập dữ liệu"` | Import, Tải lên dữ liệu |

## 6. Font & độ phân giải

- Sans-serif. Title **24px**, nội dung/nhãn/menu **14px**, inline error **12px**.
- Desktop `1920×1080`, Tablet `820×1180`, Mobile `430×932`.

## 7. Bảng dữ liệu (Data Grid)

| Yếu tố | Quy ước |
|---|---|
| Phân trang | **Server-side**; mặc định **10**; tùy chọn `{10, 20, 50, 100}` |
| Tổng số | Luôn hiển thị tổng bản ghi khớp lọc |
| Tìm kiếm | Contains, không phân biệt hoa thường, trim+gộp khoảng trắng; **debounce 300ms**; hỗ trợ Enter |
| Kết quả trống | `"Không có dữ liệu!"` |
| Sắp xếp | Cột sortable có mũi tên; mặc định `createdAt` giảm dần |
| Context menu | Menu `⋮` mỗi dòng: **Xem · Chỉnh sửa · Xóa** |
| Sticky | Hàng tiêu đề + bộ lọc cố định khi cuộn |
| Tooltip | Chỉ hiện khi nội dung bị cắt `...` |
| Căn lề | STT/Loại/Trạng thái/Thao tác → **giữa**; Số/Tiền → **phải**; header + còn lại → **trái** |
| Xóa cuối trang | Xóa bản ghi cuối trang >1 → về trang trước; xóa hết → `"Không có dữ liệu!"` |

**Toolbar** (trái→phải): `[Ô tìm kiếm] [Bộ lọc 1] [Bộ lọc 2] … [Xóa bộ lọc]   [+ Tạo mới]`. Ô tìm kiếm: icon kính lúp trái, placeholder `"Tìm kiếm..."`, debounce 300ms. Mỗi bộ lọc = 1 button Dropdown. `"Xóa bộ lọc"` ghost, chỉ hiện khi ≥1 filter active. Nút chính bên phải cùng.

**Nút hành động chính** (`"Tạo mới"` / `"Xuất tài liệu"`): nền `--accent` + chữ `--accent-foreground` + icon. Hover `--accent-hover`; Focus ring `--accent`; Disabled `bg-slate-200 text-slate-600` (không `--accent`+opacity).

## 8. Form Tạo mới / Chỉnh sửa (trong Dialog)

- Trường bắt buộc: dấu `*` **đỏ**, ngay sau label cách 1 khoảng trắng, không trong ngoặc, không màu khác.
- Tiêu đề: tạo `"Tạo [tên thực thể]"`, sửa `"Chỉnh sửa [tên thực thể]"`. Nút xác nhận: tạo `"Tạo mới"`, sửa `"Lưu thay đổi"`. Hủy `"Hủy"` — luôn enable.
- Nút xác nhận **disable** khi: form chưa đổi / chưa đủ trường bắt buộc / không hợp lệ / đang xử lý. Chỉ enable khi toàn bộ hợp lệ. Submit → spinner + disable toàn form.
- Validation realtime, lỗi đỏ dưới trường. Hủy khi đã nhập → hỏi xác nhận trước khi đóng.

## 9. Dialog xác nhận xóa

- Tiêu đề `"Xác nhận xóa [tên thực thể]"`.
- Nội dung `"Bạn có chắc chắn muốn xóa '[tên bản ghi]' này không? Hành động này không thể hoàn tác."`
- Nút `"Hủy"` (trái) · `"Xóa"` đỏ (phải). Nút Xóa disable ngay sau lần nhấn đầu.
- Ràng buộc FK → `"Không được xóa do dữ liệu này đang được sử dụng."`

## 10. Phân loại thông báo

Luật: validation trường → **Inline**; kết quả thao tác / lỗi hệ thống → **Toast**.

- **Inline** (dưới trường): **12px**, chữ đỏ, không nền, **KHÔNG đổi màu viền** ô. (Trừ màn đăng nhập.)
- **Toast** (góc dưới phải), 4 loại Success/Error/Warning/Info; tiếng Việt có dấu.

| Hành động | Thành công | Thất bại |
|---|---|---|
| Tạo mới | `"Tạo mới thành công."` | `"Không thể tạo mới. Vui lòng thử lại."` |
| Chỉnh sửa | `"Chỉnh sửa thành công."` | `"Không thể chỉnh sửa. Vui lòng thử lại."` |
| Xóa | `"Xóa thành công."` | `"Không được xóa do dữ liệu này đang được sử dụng."` |
| Tải lên tệp | `"Tải lên thành công."` | `"Tải lên thất bại. Vui lòng thử lại."` |
| Tải xuống | `"Đang tải xuống..."` | `"Không thể tải xuống. Vui lòng thử lại."` |
| Nhập dữ liệu | `"Nhập dữ liệu thành công."` | `"Nhập dữ liệu thất bại. Vui lòng kiểm tra lại file."` |
| Lỗi mạng | — | `"Không thể kết nối máy chủ."` |

Kênh: trường trống / sai định dạng-độ dài / mật khẩu không khớp → Inline; Tạo/Sửa/Xóa/sao chép/tải xuống/xuất thành công → Toast Success; API/mạng/5xx/403/ràng buộc → Toast Error; ảnh hưởng phụ → Warning; trạng thái hệ thống → Info.

## 11. Thông báo lỗi Validation (nguyên văn, kết thúc bằng `.`)

| Loại | Thông báo |
|---|---|
| Trường bắt buộc trống / toàn khoảng trắng | `"Đây là trường bắt buộc."` |
| Vượt độ dài tối đa | `"Vượt quá {max} ký tự."` |
| Ngoài khoảng độ dài | `"Phải từ {min} đến {max} ký tự."` |
| Email sai | `"Địa chỉ email không hợp lệ."` |
| SĐT sai | `"Số điện thoại không hợp lệ."` |
| Mật khẩu không đủ | `"Mật khẩu tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."` |
| Mật khẩu không khớp | `"Mật khẩu xác nhận không khớp."` |
| Khoảng ngày / sai định dạng tổng quát | `"Dữ liệu không hợp lệ."` |
| Định dạng tệp | `"Định dạng tệp không hợp lệ. Vui lòng chọn tệp [danh sách định dạng]."` |
| Tệp vượt dung lượng | `"Dung lượng tệp vượt quá giới hạn cho phép ({limit}MB)."` |
| Tệp vượt số dòng | `"Tệp nhập vượt quá {maxRows} dòng. Vui lòng chia nhỏ tệp."` |
| Tệp nén bất thường | `"Tệp nhập không hợp lệ hoặc bị nén bất thường."` |
| Vượt số lượng tệp | `"Chỉ được tải lên tối đa {maxFiles} tệp."` |
| Vượt tổng dung lượng | `"Tổng dung lượng các tệp vượt quá {maxTotalSize}MB."` |
| Tệp trùng (MULTI) | `"Tệp '{tên}' đã được chọn."` |
| Trùng dữ liệu | `"[Tên thực thể] đã tồn tại, vui lòng kiểm tra lại."` |

## 12. Định dạng ngày giờ (UTC+7)

| Ngữ cảnh | Định dạng | Ví dụ |
|---|---|---|
| Chỉ ngày | `dd/MM/yyyy` | `10/04/2026` |
| Ngày + giờ | `dd/MM/yyyy HH:mm:ss` | `10/04/2026 14:30:00` |
| Chỉ giờ | `HH:mm:ss` | `14:30:00` |
| Cột bảng (2 dòng) | D1 `HH:mm:ss` · D2 `dd/MM/yyyy` | — |
| Khoảng ngày | `dd/MM/yyyy - dd/MM/yyyy` | — |
| Tên file | `ddMMyyyy` | `15072026` |

## 13. Nhập / Xuất dữ liệu

**Nhập**: file mẫu → upload → validate → thông báo. Thành công `"Nhập dữ liệu thành công."`; thất bại `"Nhập dữ liệu thất bại. Vui lòng kiểm tra lại file."`. Giới hạn theo §4.

**Xuất**: nút `"Xuất tài liệu"`. Mặc định `.xlsx` (mọi chức năng). Tên file `[Tên chức năng]_[ddMMyyyy]`. Nội dung = toàn bộ dữ liệu theo bộ lọc + cột đang hiển thị.
- **≤100.000 dòng/lần** → vượt: `"Kết quả vượt quá 100.000 dòng. Vui lòng thu hẹp bộ lọc (khoảng thời gian, người dùng, hành động) rồi xuất lại."` Ghi file theo luồng.
- **≤2 lượt xuất đồng thời/máy chủ** → lượt 3: `"Hệ thống đang xử lý yêu cầu xuất khác. Vui lòng thử lại sau ít phút."`
- Giữ nguyên văn dữ liệu. Giá trị trông giống công thức (`+84912345678`, `-100`) → **KHÔNG thêm ký tự (như `'`)**; thay vào đó Excel ghi **văn bản thuần, chặn ô kiểu công thức**. CSV (chỉ khi ngoại lệ): UTF-8 có BOM. Test: xuất `=1+1`, `-100`, `+84912345678` → đúng nguyên văn.
- CSV chỉ khi: (1) máy khác đọc tự động **và** (2) >100.000 dòng; khai BRD. Im lặng → `.xlsx`.

## 14. Loading / Breadcrumb / Debounce

- **Loading**: bảng → skeleton rows; submit → spinner + disable toàn form; tải trang đầu → skeleton toàn trang; upload → progress từng item; tải xuống → toast `"Đang tải xuống..."`.
- **Breadcrumb**: đường dẫn đầy đủ; click node → về cấp đó; URL phản ánh trạng thái, deep-link bookmark được.
- **Debounce click**: chỉ xử lý **1 event**. Áp cho: Tạo mới, Lưu thay đổi, Xóa, Tìm kiếm, Xuất tài liệu.

## 15. Quản lý dữ liệu & soft-delete

- Bản ghi DB dùng **soft-delete** (`deletedAt`), không xóa vật lý; đã xóa mềm → không hiển thị trong danh sách.
- Khóa chính **UUID v4**; mọi bản ghi có `createdAt` + `updatedAt` tự động.
- Tên hiển thị dùng trường riêng, không dùng khóa kỹ thuật.

## 16. Trạng thái & màu bản ghi

Hoạt động/Kích hoạt → **Xanh lá** · Vô hiệu hóa/Bị khóa → **Xám** · Lỗi/Thất bại → **Đỏ** · Đang xử lý/Chờ → **Vàng**.

## 17. Xử lý trùng dữ liệu (check sau trim, không phân biệt hoa thường)

| Trường hợp | Thông báo |
|---|---|
| Email người dùng trùng | `"Email đã được sử dụng."` |
| Tên phòng ban trùng cùng cấp | `"Phòng ban đã tồn tại, vui lòng kiểm tra lại."` |
| Tên thư mục trùng cùng cấp cha | `"Thư mục đã tồn tại, vui lòng kiểm tra lại."` |
| Tên vai trò trùng | `"Vai trò đã tồn tại, vui lòng kiểm tra lại."` |
| Tổng quát | `"[Tên thực thể] đã tồn tại, vui lòng kiểm tra lại."` |

## 18. Phiên đăng nhập, xác thực & rate limit

- **OIDC + PKCE**; phiên silent refresh tự động.
- Phiên hết hạn / tài khoản bị khóa → về trang đăng nhập.
- **Đổi mật khẩu → chấm dứt NGAY toàn bộ phiên mọi thiết bị.**
- Chống brute-force do IdP.
- Khôi phục mật khẩu ≤5 lần/giờ/email → vượt: HTTP **429**. Endpoint nhạy cảm khác khai ngưỡng BRD.

## 19. Phân quyền ACL & phạm vi dữ liệu

- **ACL**: **OWNER** (xem/sửa/xóa/phân quyền/chia sẻ) · **EDITOR** (xem, sửa nội dung, tải lên/xuống) · **VIEWER** (chỉ xem + tải xuống).
- **Phạm vi dữ liệu**: **Cá nhân** (bản ghi mình tạo) · **Phòng ban** · **Phòng ban và cấp dưới** · **Toàn hệ thống**.
- Đơn vị tổ chức: dùng DUY NHẤT **"Phòng ban"** (không "Đơn vị"/"Bộ phận"/"Admin tổng").

## 20. Lưu ý triển khai

- UI **tiếng Việt có dấu, không ngoại lệ**; múi giờ **UTC+7**.
- Mọi service chạy **Docker container**. Trình duyệt Chrome/Edge/Firefox **120+**.
- Pagination params: `page, limit, search, sortBy, sortOrder`.
- Error format: `{ message, statusCode }`; lỗi xác thực `{ error: { code, message, timestamp } }`.
- Mọi giá trị giới hạn khai **hằng số tập trung**, không hardcode.

## 21. Bổ sung DFT (docx chưa phủ)

- **Audit log**: mỗi mutation (Tạo/Chỉnh sửa/Xóa/Chia sẻ/Kích hoạt/Vô hiệu hóa/Khôi phục/Tải lên/Tải xuống/Xuất tài liệu/Đăng nhập/Đăng xuất) = **ĐÚNG 1 entry**; **cấm double-log**; động từ chuẩn §5 (`Chỉnh sửa`≠"Cập nhật", `Tải xuống`≠`Xuất tài liệu`, `Xem trước`≠`Xem`); `resourceType` xác định (không `"unknown"`) + định danh bản ghi.
- **Phân quyền runtime**: tác vụ thiếu quyền (§19) → **ẩn hẳn, không disable mờ**; **enforce server MỌI endpoint**, không tin client; không để RAG/search lách.
- **Đồng bộ sau mutation**: Tạo/Sửa/Xóa/Di chuyển → reload list/cây + mọi màn tham chiếu (breadcrumb/tiêu đề); không để tên cũ sót.
- **Soft-delete ↔ uniqueness**: bản đã xóa mềm cùng tên/mã → quy định **tường minh** cho tái dùng hay báo trùng.
- **Chống mất dữ liệu**: ESC/click nền **không tự đóng** form đang nhập dở; **chặn double-submit** thao tác không idempotent.
