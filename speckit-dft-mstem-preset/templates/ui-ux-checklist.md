# Convention Checklist: UI/UX Consistency (Nguyên tắc IV)

**Purpose**: Spec-completeness gate cho UI/UX — spec PHẢI mô tả rõ các mục dưới, đủ để tester đọc spec là viết lại được testcase + SRS mà không cần hỏi lại.
**Created**: [DATE]
**Feature**: [Link to spec.md]

## Ngôn ngữ & Nội dung

- [ ] CHK001 **Tiếng Việt bản địa, không ngoại lệ.** Tiếng Việt là ngôn ngữ sản phẩm; mọi text UI có dấu; `vi-VN`, UTC+7; ngày `dd/MM/yyyy`, tiền `VNĐ`, thập phân dấu `,`. Không màn hình/thông báo nào tiếng Anh hay thiếu dấu. Chuỗi không nhúng vào logic (để i18n về sau khả thi).
- [ ] CHK002 **Message chuẩn hóa, không tự chế.** Phản hồi thành công/lỗi theo mẫu chung, không alert tùy tiện; mỗi kết quả thao tác và mỗi lỗi thống nhất về nội dung câu quy định — không paraphrase. 

## Nhập liệu & Validation

- [ ] CHK003 **Validation trước khi tin dữ liệu.** Trim, chặn quá max, chặn all-whitespace ở required; kiểu tài chính không bao giờ float; mỗi field có giới hạn và luật định dạng xác định.
- [ ] CHK004 **Vị trí quyết định ý nghĩa.** Lỗi validation field hiển thị inline dưới field (không đổi màu viền). Kết quả thao tác / lỗi hệ thống hiển thị toast góc dưới phải. Không trộn hai kênh.

## Bố cục & Tương tác

- [ ] CHK005 **Bố cục nhất quán, dự đoán được.** Dùng khung layout + UI kit dùng chung, UI tự chế mới cần lý do; list cùng cấu trúc toolbar và sort mặc định; primary action solid accent ngoài cùng phải; form trong Dialog với tiêu đề/nút theo mẫu. User không học lại layout giữa các màn.
- [ ] CHK006 **Hành động phá hủy phải xác nhận và an toàn.** Xóa qua Alert Dialog xác nhận chuẩn, nút đỏ phải, disable sau click đầu; ràng buộc chặn xóa; debounce mọi action button chống double-submit.
- [ ] CHK007 **Trạng thái luôn tường minh.** Mọi view dữ liệu xử lý rõ 4 trạng thái: loading, empty, error, có dữ liệu. Tác vụ dài có loading; trạng thái entity map cố định nhãn+màu; bảng rỗng có empty state và luôn hiện tổng số.

## Truy cập & Thích ứng

- [ ] CHK008 **Truy cập được (a11y — mốc WCAG 2.1 AA).** Control có tên truy cập được, dialog quản lý focus, điều hướng bàn phím đầy đủ, tooltip khi nội dung bị cắt. Không bao giờ chỉ dùng màu để truyền trạng thái — luôn kèm nhãn/biểu tượng. UI mới không làm giảm a11y dưới AA.
- [ ] CHK009 **Thích ứng, không mất tính năng.** Cùng chức năng chạy Desktop/Tablet/Mobile; layout co giãn nhưng không ẩn mất hành động hay dữ liệu cốt lõi ở màn nhỏ.

## Phân quyền

- [ ] CHK010 **UI phản ánh quyền.** Ẩn hoặc disable hành động theo quyền; không hiển thị nút mà thao tác sẽ bị từ chối. Quyền kế thừa nhất quán (tick Thêm/Sửa/Xóa auto-tick Xem).
