# QUY ƯỚC CHUNG TOÀN HỆ THỐNG (QUCTHT V1.0)

LUẬT cho MỌI project DFT. Mục 1–20 = docx QUCTHT V1.0 (các luật con `N.M` có thể là bổ sung DFT chèn vào mục gốc); mục 21 = bổ sung DFT.

## Cách dùng (bắt buộc)

- Chuỗi trong `" "` = **nguyên văn** — cấm diễn đạt lại, cấm thêm/bớt dấu câu, cấm dịch.
- Placeholder `{…}` / `[…]` trong chuỗi **phải** thay bằng giá trị thật lấy từ §2 / Từ điển dữ liệu / tên thực thể trong spec; phần ngoài placeholder giữ nguyên ký tự. Không có nguồn cho placeholder → agent DỪNG, báo; `qa-spec-cycle` ghi `[NEEDS: <tên>]` rồi chạy tiếp. CẤM bịa số.
- Đơn vị trích dẫn trong báo cáo dev = mã luật `§N.M` (vd `§7.14`). Bảng tra không có `.M` → trích `§N` + khóa hàng (vd `§2 Email`). Bảng đối chiếu cấp section (Pha 4b của `qa-spec-cycle`) vẫn khóa theo `§N` cấp mục — CẤM tách `.M`.
- Mọi khẳng định ĐẠT phải kèm `file:line` thật trong code.
- QUC chọi **repo** → theo QUC, ghi XUNG ĐỘT vào báo cáo, KHÔNG dừng.
- QUC chọi **task / spec / BRD** → CẤM tự chọn bên: agent DỪNG + báo mâu thuẫn; `qa-spec-cycle` ghi blocker và bỏ đúng điểm đó.
- QUC tự mâu thuẫn → DỪNG, trích cả hai mã luật.
- Cần một giá trị **thuộc phạm vi QUC** (độ dài, chuỗi, định dạng, ngưỡng, nhãn) mà QUC không có → DỪNG, báo; CẤM bịa, CẤM lấy từ repo. Giá trị nghiệp vụ ngoài phạm vi QUC (tên field, entity, rule) → lấy từ spec/plan/data-model theo luật của agent.

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
| **Khóa chính** | **UUID v4** | `8-4-4-4-12` hex; CẤM int auto-increment |
| Tài chính / độ chính xác cao | `decimal` | CẤM `float`/`double` |
| Thời điểm | `datetime` | UTC+7 |

## 2. Độ dài trường (nguồn DUY NHẤT)

| Trường | Tối đa | Ràng buộc |
|---|---|---|
| Mã (code/taxCode/productCode) | **50** | Không ký tự đặc biệt trừ `_` `-`; không khoảng trắng đầu/cuối |
| Tên / Contact Name | **255** | Unicode tiếng Việt; tự viết hoa chữ cái đầu khi hiển thị |
| Email | **255** | 1 dấu `@`, không khoảng trắng (§3.2) |
| Số điện thoại | **12** | §3.3 |
| Mật khẩu | **128** (hash) | Nhập ≥**8**; lưu hash, CẤM plaintext |
| URL / File path | **500** | Ưu tiên HTTPS |
| Mô tả / Notes | **4000** | Cho phép ký tự đặc biệt + xuống dòng |
| Tên thư mục / tài liệu | **255** | CẤM chứa `/ \ : * ? " \|` |

## 3. Từng loại trường nhập liệu

- **3.1 Textbox** — trim khi lưu; toàn khoảng trắng ở trường bắt buộc → chặn; chặn nhập vượt §2 ngay tại ô.
- **3.2 Email** — 1 `@`; trước `@`: chữ/số/`. _ % + -`, không mở/kết bằng `.`, không `..`; sau `@`: chữ/số/`.`/`-`, ≥1 `.`, tên miền ≥2 chữ; không khoảng trắng; check trùng không phân biệt hoa thường. Sai → `"Địa chỉ email không hợp lệ."`
- **3.3 Số điện thoại** — chỉ `0–9` + `+` ở đầu; bỏ khoảng trắng; trống hợp lệ nếu không bắt buộc; `0xxxxxxxxx` (10 số, đầu `0`) hoặc `+84xxxxxxxxx` (12 ký tự). Sai → `"Số điện thoại không hợp lệ."`
- **3.4 Date Picker** — `dd/MM/yyyy`; khoảng `dd/MM/yyyy - dd/MM/yyyy`; bắt đầu > kết thúc → `"Dữ liệu không hợp lệ."`; **chỉ chọn qua calendar, CẤM nhập tay**.
- **3.5 Số** — chỉ số dương (cần âm → khai BRD); nghìn dấu `.`; thập phân dấu `,` ≤2 (`2,21`).
- **3.6 Tiền VNĐ** — chỉ số; hiển thị `5.000.000 VNĐ`; không thập phân.
- **3.7 Tỷ lệ %** — chỉ số; `90%` / `99,22%`; 0,00–100,00; vượt → `"Dữ liệu không hợp lệ."`
- **3.8 Mật khẩu** — ≥8, bắt buộc hoa + thường + số + đặc biệt; ẩn `****` + nút bật/tắt. Sai → `"Mật khẩu tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."`; không khớp → `"Mật khẩu xác nhận không khớp."`
- **3.9 Mã tự sinh** — CẤM sửa; placeholder `"Mã tự sinh"`.
- **3.10 Dropdown single** — chọn 1 giá trị. **Checkbox multi** — tick nhiều giá trị trong 1 nhóm.
- **3.11 Checkbox phân quyền (cây)** — tick cha → tick toàn bộ con; tick Thêm/Sửa/Xóa → tự tick **Xem**; bỏ tick **Xem** → bỏ toàn bộ quyền còn lại.

## 4. Tệp tải lên

| Loại | Kiểu | Định dạng | Số | DL/tệp | Tổng |
|---|---|---|---|---|---|
| Ảnh đại diện/logo/chữ ký | SINGLE | `JPG, PNG, WEBP` | 1 | **2 MB** | 2 MB |
| Nhập hàng loạt | SINGLE | `CSV, XLSX` | 1 | **10 MB, ≤5.000 dòng** | 10 MB |
| Đính kèm chung | MULTI | `PDF, DOCX, XLSX, JPG, PNG` | 10 | **25 MB** | 50 MB |

- **4.1** SINGLE thay tệp cũ; MULTI thêm vào danh sách. CẤM `.xls` (chỉ `.xlsx`).
- **4.2** Client kiểm khi chọn; **server kiểm lại toàn bộ, không tin client**.
- **4.3** Trần cứng: 20 tệp/trường, 50 MB/tệp, 200 MB tổng.
- **4.4** Ảnh: cắt vuông + thu 512px + xóa EXIF, không giữ gốc.
- **4.5** Kiểm định dạng theo magic-byte; đọc/ghi theo luồng; endpoint upload riêng; 60 lần/phút/user.
- **4.6** Tệp tạm xóa sau 24h; tệp của bản ghi xóa-mềm xóa hẳn sau 90 ngày.
- **4.7** Chuỗi lỗi: `"Định dạng tệp không hợp lệ. Vui lòng chọn tệp [danh sách định dạng cho phép]."` · `"Dung lượng tệp vượt quá giới hạn cho phép ({limit}MB)."` · `"Tệp nhập vượt quá {maxRows} dòng. Vui lòng chia nhỏ tệp."` · `"Chỉ được tải lên tối đa {maxFiles} tệp."` · `"Tổng dung lượng các tệp vượt quá {maxTotalSize}MB."` · `"Tệp '{tên}' đã được chọn."` · gợi ý `"Hỗ trợ [định dạng]. Tối đa [giới hạn]MB."`

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

- **6.1** Sans-serif. Title **24px**; nội dung/nhãn/menu **14px**; inline error **12px**.
- **6.2** Desktop `1920×1080`; Tablet `820×1180`; Mobile `430×932`.

## 7. Bảng dữ liệu (Data Grid)

| ID | Yếu tố | Luật |
|---|---|---|
| 7.1 | Phân trang | **Server-side**; mặc định **10**; tùy chọn `{10, 20, 50, 100}` |
| 7.2 | Tổng số | Luôn hiển thị tổng bản ghi khớp lọc |
| 7.3 | Tìm kiếm | Contains, không phân biệt hoa thường, trim + gộp khoảng trắng; **debounce 300ms**; hỗ trợ Enter |
| 7.4 | Kết quả trống | `"Không có dữ liệu!"` |
| 7.5 | Sắp xếp | Cột sortable có mũi tên; mặc định `createdAt` giảm dần |
| 7.6 | Context menu | Menu `⋮` mỗi dòng: **Xem · Chỉnh sửa · Xóa** |
| 7.7 | Sticky | Hàng tiêu đề + bộ lọc cố định khi cuộn |
| 7.8 | Tooltip | Chỉ hiện khi nội dung bị cắt `...` |
| 7.9 | Căn lề | STT/Loại/Trạng thái/Thao tác → **giữa**; Số/Tiền → **phải**; header + còn lại → **trái** |
| 7.10 | STT | Cộng offset trang (`pageIndex * pageSize + i + 1`); CẤM `i + 1` cục bộ |
| 7.11 | Xóa cuối trang | Xóa bản ghi cuối của trang >1 → về trang trước; xóa hết → `"Không có dữ liệu!"` |

**Toolbar**

- **7.12** Thứ tự trái→phải: `[Ô tìm kiếm] [Bộ lọc 1] [Bộ lọc 2] … [Xóa bộ lọc]   [+ Tạo mới]`. Nút hành động chính ở bên phải cùng.
- **7.13** Ô tìm kiếm: icon kính lúp bên trái, placeholder `"Tìm kiếm..."`, debounce 300ms.
- **7.14** Mỗi bộ lọc = 1 button Dropdown.
- **7.15** `"Xóa bộ lọc"`: ghost + icon `remove-filter` (phễu gạch chéo); **luôn hiển thị**, CẤM ẩn.
- **7.16** `"Xóa bộ lọc"` **enable** khi ≥1 tiêu chí lọc đang active — tính cả ô tìm kiếm khác rỗng; **disable** khi mọi tiêu chí ở mặc định.
- **7.17** Click `"Xóa bộ lọc"` → mọi tiêu chí về mặc định (gồm ô tìm kiếm — xóa rỗng) + về trang 1; giữ nguyên sắp xếp và page size.

**Nút hành động chính** (`"Tạo mới"` / `"Xuất tài liệu"`)

- **7.18** Nền `--accent` + chữ `--accent-foreground` + icon. Hover `--accent-hover`. Focus ring `--accent`.
- **7.19** Disabled `bg-slate-200 text-slate-600` — CẤM `--accent` + opacity.

## 8. Form Tạo mới / Chỉnh sửa (trong Dialog)

- **8.1** Trường bắt buộc: dấu `*` **đỏ**, ngay sau label cách 1 khoảng trắng; CẤM đặt trong ngoặc, CẤM màu khác.
- **8.2** Tiêu đề: tạo `"Tạo [tên thực thể]"`, sửa `"Chỉnh sửa [tên thực thể]"`.
- **8.3** Nút xác nhận: tạo `"Tạo mới"`, sửa `"Lưu thay đổi"`. Nút `"Hủy"` luôn enable.
- **8.4** Nút xác nhận **disable** khi: form chưa đổi / chưa đủ trường bắt buộc / không hợp lệ / đang xử lý. Chỉ enable khi toàn bộ hợp lệ. Áp cho **cả Tạo lẫn Chỉnh sửa**.
- **8.5** Submit → spinner + disable toàn form.
- **8.6** Validation realtime, lỗi đỏ dưới trường.
- **8.7** Hủy khi đã nhập dở → hỏi xác nhận trước khi đóng.

## 9. Dialog xác nhận xóa

- **9.1** Tiêu đề `"Xác nhận xóa [tên thực thể]"`.
- **9.2** Nội dung `"Bạn có chắc chắn muốn xóa '[tên bản ghi]' này không? Hành động này không thể hoàn tác."`
- **9.3** Nút `"Hủy"` (trái) · `"Xóa"` đỏ (phải). Nút Xóa disable ngay sau lần nhấn đầu.
- **9.4** Vướng ràng buộc FK → `"Không được xóa do dữ liệu này đang được sử dụng."`

## 10. Phân loại thông báo

- **10.1** Kênh: validation trường → **Inline**; kết quả thao tác / lỗi hệ thống → **Toast**.
- **10.2** Inline (dưới trường): **12px**, chữ đỏ, không nền, **CẤM đổi màu viền** ô. Ngoại lệ duy nhất: màn đăng nhập.
- **10.3** Toast: góc dưới phải; 4 loại Success/Error/Warning/Info; tiếng Việt có dấu.
- **10.4** Mỗi mutation bắn **đúng 1 toast**, đủ cả nhánh thành công lẫn thất bại.
- **10.5** Lỗi nghiệp vụ server trả mã lỗi → map qua bảng message của feature; CẤM hiện 1 câu chung cho mọi lỗi. Chỉ fallback câu chung khi mã không có trong bảng map (§20.5).

| Hành động | Thành công | Thất bại |
|---|---|---|
| Tạo mới | `"Tạo mới thành công."` | `"Không thể tạo mới. Vui lòng thử lại."` |
| Chỉnh sửa | `"Chỉnh sửa thành công."` | `"Không thể chỉnh sửa. Vui lòng thử lại."` |
| Xóa | `"Xóa thành công."` | `"Không được xóa do dữ liệu này đang được sử dụng."` |
| Tải lên tệp | `"Tải lên thành công."` | `"Tải lên thất bại. Vui lòng thử lại."` |
| Tải xuống | `"Đang tải xuống..."` | `"Không thể tải xuống. Vui lòng thử lại."` |
| Nhập dữ liệu | `"Nhập dữ liệu thành công."` | `"Nhập dữ liệu thất bại. Vui lòng kiểm tra lại file."` |
| Lỗi mạng | — | `"Không thể kết nối máy chủ."` |

- **10.6** Định tuyến kênh: trường trống / sai định dạng-độ dài / mật khẩu không khớp → Inline · Tạo/Sửa/Xóa/sao chép/tải xuống/xuất thành công → Toast Success · API/mạng/5xx/403/ràng buộc → Toast Error · ảnh hưởng phụ → Warning · trạng thái hệ thống → Info.

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

- **12.1** Chuỗi thời điểm server trả về phải mang UTC tường minh (hậu tố `Z` hoặc offset); thiếu → sửa ở tầng serialize, CẤM để client tự đoán.
- **12.2** Convert "giờ VN → UTC" áp **đúng 1 lần**, tại điểm ghi.
- **12.3** Kiểm: mở Chỉnh sửa rồi Lưu mà không đổi gì → mọi giá trị ngày giờ giữ nguyên.

## 13. Nhập / Xuất dữ liệu

- **13.1 Nhập** — luồng: tải file mẫu → upload → validate → thông báo. Thành công `"Nhập dữ liệu thành công."`; thất bại `"Nhập dữ liệu thất bại. Vui lòng kiểm tra lại file."` Giới hạn theo §4.
- **13.2 Xuất** — nút `"Xuất tài liệu"`; mặc định `.xlsx` cho mọi chức năng; tên file `[Tên chức năng]_[ddMMyyyy]`; nội dung = toàn bộ dữ liệu theo bộ lọc hiện tại + cột đang hiển thị.
- **13.3** ≤**100.000 dòng**/lần; vượt → `"Kết quả vượt quá 100.000 dòng. Vui lòng thu hẹp bộ lọc (khoảng thời gian, người dùng, hành động) rồi xuất lại."` Ghi file theo luồng.
- **13.4** ≤**2 lượt xuất đồng thời**/máy chủ; lượt 3 → `"Hệ thống đang xử lý yêu cầu xuất khác. Vui lòng thử lại sau ít phút."`
- **13.5** Giữ nguyên văn dữ liệu. Giá trị trông giống công thức (`=1+1`, `-100`, `+84912345678`) → **CẤM thêm ký tự** (như `'`); ghi **văn bản thuần, chặn ô kiểu công thức**. Test bắt buộc: xuất `=1+1`, `-100`, `+84912345678` → đọc lại đúng nguyên văn.
- **13.6** CSV chỉ khi đủ **cả hai**: (1) máy khác đọc tự động **và** (2) >100.000 dòng; phải khai trong BRD. Không khai → `.xlsx`. CSV dùng UTF-8 có BOM.

## 14. Loading / Breadcrumb / Debounce

- **14.1** Loading: bảng → skeleton rows; submit → spinner + disable toàn form; tải trang đầu → skeleton toàn trang; upload → progress từng item; tải xuống → toast `"Đang tải xuống..."`.
- **14.2** Breadcrumb: đường dẫn đầy đủ; click node → về cấp đó; URL phản ánh trạng thái; deep-link bookmark được.
- **14.3** Debounce click: chỉ xử lý **1 event**. Áp cho: Tạo mới, Lưu thay đổi, Xóa, Tìm kiếm, Xuất tài liệu.

## 15. Quản lý dữ liệu & soft-delete

- **15.1** Bản ghi DB dùng **soft-delete** (`deletedAt`), CẤM xóa vật lý; đã xóa mềm → không hiển thị trong danh sách.
- **15.2** Khóa chính **UUID v4**; mọi bản ghi có `createdAt` + `updatedAt` tự động.
- **15.3** Tên hiển thị dùng trường riêng, CẤM dùng khóa kỹ thuật.

## 16. Trạng thái & màu bản ghi

- **16.1** Hoạt động/Kích hoạt → **Xanh lá** · Vô hiệu hóa/Bị khóa → **Xám** · Lỗi/Thất bại → **Đỏ** · Đang xử lý/Chờ → **Vàng**.

## 17. Xử lý trùng dữ liệu

- **17.1** Check trùng sau trim, không phân biệt hoa thường, đúng scope nghiệp vụ.
- **17.2** Scope query kiểm trùng phải khớp scope unique index/constraint thật ở DB (cùng lọc hoặc cùng không lọc bản xóa mềm).
- **17.3** Kiểm trùng phía client chỉ là gợi ý UX; server là nguồn đúng cuối cùng.

| Trường hợp | Thông báo |
|---|---|
| Email người dùng trùng | `"Email đã được sử dụng."` |
| Tên phòng ban trùng cùng cấp | `"Phòng ban đã tồn tại, vui lòng kiểm tra lại."` |
| Tên thư mục trùng cùng cấp cha | `"Thư mục đã tồn tại, vui lòng kiểm tra lại."` |
| Tên vai trò trùng | `"Vai trò đã tồn tại, vui lòng kiểm tra lại."` |
| Tổng quát | `"[Tên thực thể] đã tồn tại, vui lòng kiểm tra lại."` |

## 18. Phiên đăng nhập, xác thực & rate limit

- **18.1** **OIDC + PKCE**; phiên silent refresh tự động.
- **18.2** Phiên hết hạn / tài khoản bị khóa → về trang đăng nhập.
- **18.3** Đổi mật khẩu → chấm dứt NGAY toàn bộ phiên trên mọi thiết bị.
- **18.4** Chống brute-force do IdP đảm nhiệm.
- **18.5** Khôi phục mật khẩu ≤5 lần/giờ/email; vượt → HTTP **429**. Endpoint nhạy cảm khác khai ngưỡng trong BRD.

## 19. Phân quyền ACL & phạm vi dữ liệu

- **19.1** ACL: **OWNER** (xem/sửa/xóa/phân quyền/chia sẻ) · **EDITOR** (xem, sửa nội dung, tải lên/xuống) · **VIEWER** (chỉ xem + tải xuống).
- **19.2** Phạm vi dữ liệu: **Cá nhân** (bản ghi mình tạo) · **Phòng ban** · **Phòng ban và cấp dưới** · **Toàn hệ thống**.
- **19.3** Đơn vị tổ chức gọi DUY NHẤT là **"Phòng ban"** — CẤM "Đơn vị" / "Bộ phận" / "Admin tổng".
- **19.4** Guard/điều hướng theo quyền phải fail-safe đúng chiều: CẤM dùng giá trị mặc định (khi quyền thật chưa load xong) để **chặn** truy cập — deep-link/F5 phải vào được (§14.2).

## 20. Lưu ý triển khai

- **20.1** UI **tiếng Việt có dấu, không ngoại lệ**; múi giờ **UTC+7**.
- **20.2** Mọi service chạy **Docker container**. Trình duyệt Chrome/Edge/Firefox **120+**.
- **20.3** Pagination params: `page, limit, search, sortBy, sortOrder`.
- **20.4** Error format: `{ message, statusCode }`; lỗi xác thực `{ error: { code, message, timestamp } }`.
- **20.5** Mã lỗi nghiệp vụ đồng bộ đủ 3 nơi: nơi khai ở backend · file localization (mọi ngôn ngữ) · bảng map message ở FE. 1 mã = 1 ý nghĩa; CẤM tái dùng mã đã có chủ.
- **20.6** Mọi giá trị giới hạn khai bằng **hằng số tập trung**; CẤM hardcode.
- **20.7** Server validate lại **mọi** input, không tin client; validate trên giá trị gốc **trước** khi coerce/gán mặc định.

## 21. Bổ sung DFT (docx chưa phủ)

- **21.1 Audit log** — mỗi mutation (Tạo/Chỉnh sửa/Xóa/Chia sẻ/Kích hoạt/Vô hiệu hóa/Khôi phục/Tải lên/Tải xuống/Xuất tài liệu/Đăng nhập/Đăng xuất) = **ĐÚNG 1 entry**; CẤM double-log; động từ chuẩn §5 (`Chỉnh sửa`≠"Cập nhật", `Tải xuống`≠`Xuất tài liệu`, `Xem trước`≠`Xem`); `resourceType` xác định (CẤM `"unknown"`) + định danh bản ghi.
- **21.2 Phân quyền runtime** — tác vụ thiếu quyền (§19) → **ẩn hẳn, CẤM disable mờ**; enforce server ở **MỌI** endpoint, không tin client; không để RAG/search lách.
- **21.3 Đường đọc sạch** — endpoint `Get*`/`GetList*` CẤM ghi DB, kể cả khi tính trạng thái dẫn xuất; cần persist → background job / domain event riêng.
- **21.4 Đồng bộ sau mutation** — Tạo/Sửa/Xóa/Di chuyển → reload list/cây + mọi màn tham chiếu (breadcrumb, tiêu đề); CẤM để tên cũ sót lại.
- **21.5 Soft-delete ↔ uniqueness** — bản đã xóa mềm trùng tên/mã: quy định **tường minh** tái dùng hay báo trùng (§17.2).
- **21.6 Chống mất dữ liệu** — ESC / click nền CẤM tự đóng form đang nhập dở; chặn double-submit ở thao tác không idempotent.
- **21.7 Migration trên bảng đã có dữ liệu** — làm hẹp kiểu cột, đổi `default`, đổi ý nghĩa enum đang dùng, hoặc thêm unique index → bắt buộc kèm bước backfill/dedupe tường minh trước khi áp; thiếu = migration CHƯA XONG dù build xanh.
