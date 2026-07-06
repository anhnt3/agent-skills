Trước khi chạy checklist core bên dưới, kiểm tra **fast-path bộ cố định**.

## Fast-path: bộ checklist cố định (deterministic)

Nếu `$ARGUMENTS` nhắc tới `ui-ux` / `ui/ux` / `convention` / `nguyên tắc IV` / `IV`:
- **KHÔNG sinh checklist động.** Copy nguyên văn bộ cố định vào feature:
  - Nguồn: `.specify/presets/dft-mstem/templates/ui-ux-checklist.md`
  - Đích: `FEATURE_DIR/checklists/ui-ux.md` (FEATURE_DIR lấy từ `.specify/feature.json` hoặc script setup của core bên dưới).
  - Nếu `ui-ux.md` đã tồn tại: giữ trạng thái tick `[x]` hiện có, chỉ cập nhật nội dung item nếu bộ cố định đổi (không đánh lại số CHK).
  - Thay `[DATE]` bằng ngày hiện tại, `[Link to spec.md]` bằng đường dẫn spec.md của feature.
- Báo đã tạo `checklists/ui-ux.md` (10 mục CHK001–010, bộ IV cố định) rồi DỪNG — không chạy phần core.

Ngược lại (args khác), chạy bình thường phần core bên dưới.

{CORE_TEMPLATE}
