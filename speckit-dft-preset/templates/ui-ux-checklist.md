# Convention Checklist: UI/UX Consistency

**Purpose**: Spec-completeness gate cho UI/UX — spec PHẢI mô tả rõ các mục dưới, đủ để tester đọc spec là viết lại được testcase + SRS mà không cần hỏi lại.
**Created**: [DATE]
**Feature**: [Link to spec.md]

## Ngôn ngữ & Nội dung

- [ ] CHK001 **Tiếng Việt bản địa, không ngoại lệ.** Tiếng Việt là ngôn ngữ sản phẩm; mọi text UI có dấu; `vi-VN`, UTC+7; ngày `dd/MM/yyyy`, tiền `VNĐ`, thập phân dấu `,`. Không màn hình/thông báo nào tiếng Anh hay thiếu dấu. Chuỗi không nhúng vào logic (để i18n về sau khả thi).
- [ ] CHK002 **Message lấy từ catalog chung, không tự chế.** Mọi thông báo kết quả/lỗi trích từ Message Catalog cấp project; spec tham chiếu mã, không paraphrase. Câu thành công chung dùng đúng dạng chuẩn ("Cập nhật thành công"), **không** nhét tên đối tượng ("Cập nhật người dùng thành công" ✗) và **không** câu cụt thiếu vế ("Đã đặt lại mật khẩu cho " ✗). Chuỗi chưa có trong catalog phải thêm vào catalog trước, không đặt câu mới ngay trong màn hình.
  - *Ví dụ thật:* ✗ "Cập nhật phòng ban thành công" → ✓ "Cập nhật thành công" · ✗ "Đã khoá tài khoản" → ✓ "Khóa tài khoản thành công" · ✗ "Đã đặt lại mật khẩu cho " → ✓ "Đặt lại mật khẩu thành công".
- [ ] CHK002b **Một hành động — một động từ.** Cùng thao tác nghiệp vụ luôn dùng đúng một nhãn theo từ điển thuật ngữ (Create=Tạo mới, Update=Cập nhật, Delete=Xóa, Save=Lưu…); cấm đồng nghĩa lẫn lộn (Thêm mới/Tạo mới, Cập nhật/Update/Sửa). Áp dụng cho text nút, tiêu đề Dialog, breadcrumb, label và message.
  - *Ví dụ thật:* ✗ label "Thêm người dùng" + title popup lệch → ✓ menu "Tạo người dùng", title "Tạo người dùng", button "Tạo mới" (đồng bộ một động từ) · ✗ breadcrumb "Người dùng" → ✓ "Quản lý hệ thống > Quản lý người dùng".
- [ ] CHK002c **Thành công luôn có phản hồi.** Mọi thao tác thành công (tạo/sửa/xóa, upload file/thư mục, sao chép…) đều hiện toast xác nhận — không im lặng.
  - *Ví dụ thật:* ✗ upload tài liệu/thư mục thành công nhưng không có toast nào → ✓ hiện toast "Tải lên thành công".

## Nhập liệu & Validation

- [ ] CHK003 **Validation trước khi tin dữ liệu, luật có message chuẩn.** Trim đầu-cuối, chặn quá max, chặn all-whitespace ở required; kiểu tài chính không bao giờ float; mỗi kiểu field (email, SĐT `0xxxxxxxxx`/`+84…`, mã, tên, tiền, số ≥ 0, ngày) có một bộ luật + một câu lỗi cố định dùng chung (vd `VR_REQUIRED`, `VR_MAXLEN`, `VR_EMAIL`, `VR_PHONE`, `VR_MONEY_POSITIVE`). Spec khai mỗi field bằng danh sách mã luật áp dụng, không tự phát biểu lại luật hay tự chế câu lỗi; field không map được luật nào = thiếu luật, phải bổ sung (không "validation ẩn" trong code). Nhiều luật cùng field phải xác định thứ tự ưu tiên (vd file: check định dạng trước, rồi mới dung lượng — không gộp báo lẫn lộn).
  - *Ví dụ thật:* ✗ vượt maxlength Email báo toast "Email không hợp lệ" → ✓ inline dưới field "Vượt quá 255 ký tự" · ✗ file sai định dạng + quá 50MB báo gộp một câu → ✓ ưu tiên báo sai định dạng trước.
- [ ] CHK004 **Vị trí quyết định ý nghĩa.** Lỗi validation field hiển thị inline dưới field (không đổi màu viền). Kết quả thao tác / lỗi hệ thống hiển thị toast góc dưới phải. Không trộn hai kênh.
  - *Ví dụ thật:* ✗ nhập số âm báo bằng tooltip ở trường → ✓ chữ đỏ ngay dưới trường (đồng bộ các trường còn lại) · ✗ lỗi validation field bắn lên toast → ✓ để inline.

## Bố cục & Tương tác

- [ ] CHK005 **Bố cục nhất quán, dự đoán được.** Dùng khung layout + UI kit dùng chung, UI tự chế mới cần lý do; list cùng cấu trúc toolbar và sort mặc định; primary action solid accent ngoài cùng phải; form trong Dialog với tiêu đề/nút theo mẫu. User không học lại layout giữa các màn.
- [ ] CHK006 **Hành động phá hủy phải xác nhận và an toàn.** Xóa qua Alert Dialog xác nhận chuẩn, nút đỏ phải, disable sau click đầu; ràng buộc chặn xóa; debounce mọi action button chống double-submit. Popup xác nhận với đối tượng "có nội dung con" phải nêu rõ hệ quả lan truyền, không dùng câu xóa chung chung.
  - *Ví dụ thật:* ✗ xóa thư mục đang chứa dữ liệu vẫn hỏi "Bạn có chắc muốn xóa '$tên'? Hành động không thể hoàn tác" → ✓ "Thư mục '$tên' đang chứa $n thư mục con, $m tài liệu. Xóa sẽ xóa toàn bộ nội dung bên trong." · ✗ mở khóa hàng loạt chạy ngay → ✓ phải có popup xác nhận trước.
- [ ] CHK007 **Trạng thái luôn tường minh.** Mọi view dữ liệu xử lý rõ 4 trạng thái: loading, empty, error (kể cả mất mạng/timeout), có dữ liệu — không để màn trắng hay xoay vô hạn. Tác vụ dài có loading; trạng thái entity map cố định nhãn+màu; bảng rỗng có empty state và luôn hiện tổng số.
- [ ] CHK007b **Danh sách khai đủ cột và dữ liệu.** Spec liệt kê tường minh mọi cột của mỗi bảng/danh sách: tên cột (đúng từ điển thuật ngữ), nguồn dữ liệu, định dạng (ngày `dd/MM/yyyy`, tiền `VNĐ`, số), căn lề (số/tiền căn phải, text căn trái), và giá trị khi rỗng/null (vd `—`, không để trống). Không thiếu cột nghiệp vụ then chốt, không hiển thị sai/nhầm dữ liệu giữa các cột, không lộ mã kỹ thuật/ID thô thay cho nhãn. Cột hành động (nút/menu) khai riêng.
- [ ] CHK007c **Lọc / sắp xếp / tìm kiếm định nghĩa đầy đủ.** Với mỗi danh sách có filter/sort/search, spec khai: từng bộ lọc (field, kiểu control, giá trị mặc định), cột nào sort được + hướng mặc định, phạm vi ô tìm kiếm (tìm theo field nào), và hành vi cụ thể: lọc rỗng → hiện empty state (không phải màn cũ), reset xóa hết filter về mặc định, đổi filter/search reset về trang 1, giữ hay mất filter khi rời màn rồi quay lại. Nhiều điều kiện kết hợp (AND/OR) nêu rõ; không để "lọc theo trực giác".

## Truy cập & Thích ứng

- [ ] CHK008 **Truy cập được (a11y — mốc WCAG 2.1 AA).** Control có tên truy cập được, dialog quản lý focus, điều hướng bàn phím đầy đủ, tooltip khi nội dung bị cắt. Không bao giờ chỉ dùng màu để truyền trạng thái — luôn kèm nhãn/biểu tượng. UI mới không làm giảm a11y dưới AA.
- [ ] CHK009 **Thích ứng, không tràn vỡ, không mất tính năng.** Cùng chức năng chạy Desktop/Tablet/Mobile; layout co giãn nhưng không ẩn mất hành động hay dữ liệu cốt lõi ở màn nhỏ. Spec nêu breakpoint và hành vi khi hẹp: **thân trang không cuộn ngang**; nội dung rộng (bảng, biểu đồ, code) cuộn trong khung riêng `overflow-x:auto`; text dài cắt bằng `…` kèm tooltip, không tràn khỏi ô/đè lên phần tử khác; ảnh `max-width:100%`; nút/label không dính chồng nhau; vùng chạm ≥ 44px trên mobile. Nêu rõ bảng nhiều cột xử lý sao ở mobile (cuộn ngang hay đổi layout).

## Phân quyền

- [ ] CHK010 **UI phản ánh quyền.** Ẩn hoặc disable hành động theo quyền; không hiển thị nút mà thao tác sẽ bị từ chối. Quyền kế thừa nhất quán (tick Thêm/Sửa/Xóa auto-tick Xem).
  - *Ví dụ thật:* ✗ nút "Tải xuống" vẫn hiện với tài khoản không có quyền tải → ✓ ẩn nút khi thiếu quyền · ✗ tài khoản Đã khóa vẫn hiện nút "Khóa" → ✓ ẩn/đổi nút theo trạng thái.

## Kiểm thử được (Testability)

- [ ] CHK011 **Phần tử tương tác có định danh ổn định cho e2e.** Mọi control người dùng thao tác (button, input, dropdown, row hành động, toast, dialog, item danh sách) mang `data-testid` đặt tên theo quy ước `<màn>-<đối-tượng>-<hành-động>` (vd `user-form-submit`, `user-row-lock`, `toast-success`). Test e2e chọn phần tử qua `data-testid`, **không** bám vào text hiển thị (đổi theo message/i18n), thứ tự DOM, hay class CSS. Row trong bảng đính `data-testid`/`data-id` theo khóa bản ghi để chọn đúng dòng. Spec liệt kê testid cho các phần tử trọng yếu của luồng.
