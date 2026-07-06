Trước khi chạy checklist core bên dưới, kiểm tra **fast-path bộ cố định**.

## Fast-path: bộ checklist cố định (deterministic)

Nếu `$ARGUMENTS` nhắc tới `ui-ux` / `ui/ux` / `convention` / `nguyên tắc IV` / `IV`:

### Bước 1 — Stamp bộ cố định
- **KHÔNG sinh checklist động.** Copy nguyên văn bộ cố định:
  - Nguồn: `.specify/presets/dft-mstem/templates/ui-ux-checklist.md`
  - Đích: `FEATURE_DIR/checklists/ui-ux.md` (FEATURE_DIR lấy từ `.specify/feature.json` hoặc script setup của core bên dưới).
  - Nếu `ui-ux.md` đã tồn tại: **giữ nguyên** trạng thái `[x]` + note người đã ghi; chỉ cập nhật nội dung item nếu bộ cố định đổi (không đánh lại số CHK).
  - Thay `[DATE]` bằng ngày hiện tại, `[Link to spec.md]` bằng đường dẫn spec.md của feature.

### Bước 2 — Chấm (chỉ khi có spec)
Nếu `$ARGUMENTS` chỉ tới spec.md (hoặc feature có spec.md): đọc spec, chấm **từng mục còn `[ ]` trống** (KHÔNG đụng mục người đã `[x]`):
- **Pass** → tick `[x]`, ghi cuối dòng ` — ✅ nguồn: <FR-xxx/§IV/…>`.
- **N/A** → giữ `[ ]`, ghi ` — ➖ N/A: <lý do>`.
- **Gap** (spec thiếu/mơ hồ, tester không viết được testcase) → giữ `[ ]`, ghi ` — ⚠️ Gap: <thiếu gì>`.
Mỗi verdict PHẢI trích nguồn spec; không có nguồn = Gap. Thêm cuối file mục `## Tổng` (đếm Pass/N/A/Gap).

### Bước 3 — Thảo luận & vá gap
Với MỖI Gap: hỏi người dùng qua **AskUserQuestion** (một câu/lần, 2–4 option, `(Recommended)` đầu, kèm lý do) cách vá. Sau khi chốt:
- Cập nhật `spec.md` (append/sửa requirement tương ứng, giữ cấu trúc + dấu nguồn).
- Chấm lại mục đó; đạt thì tick `[x]` + nguồn mới. Cập nhật `## Tổng`.
Hết gap (hoặc người dùng chấp nhận để lại): DỪNG, báo tổng kết.

Không có spec → chỉ Bước 1, báo đã tạo list trống rồi DỪNG (không chạy core).

Ngược lại (args khác), chạy bình thường phần core bên dưới.

{CORE_TEMPLATE}
