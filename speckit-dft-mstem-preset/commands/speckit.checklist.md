Trước khi chạy checklist core bên dưới, kiểm tra **fast-path bộ cố định**.

## Fast-path: bộ checklist cố định (deterministic)

Kích hoạt fast-path khi `$ARGUMENTS` chứa (token độc lập, không phân biệt hoa/thường) một trong: `ui-ux`, `ui/ux`, `uiux`, `ux`, `giao diện`, `trải nghiệm`, `convention`, `nguyên tắc IV`, hoặc cờ tường minh `--ui-ux`. **Không** khớp chữ `IV` đứng lẻ (dễ nhầm token nghiệp vụ). Nếu mơ hồ (vừa giống fast-path vừa giống domain khác) → hỏi người dùng muốn bộ IV cố định hay checklist động.

### Bước 1 — Stamp bộ cố định
- **Lấy FEATURE_DIR**: chạy script prerequisites của core (`check-prerequisites.sh --json`) để có FEATURE_DIR; hoặc đọc `.specify/feature.json`. Thiếu cả hai → báo lỗi rõ + hỏi feature nào, KHÔNG đoán.
- **KHÔNG sinh checklist động.** Copy nguyên văn bộ cố định:
  - Nguồn: chạy `specify preset resolve ui-ux-checklist` để lấy đường dẫn file (đừng hardcode preset id). Không resolve được → hỏi lại người dùng.
  - Đích: `FEATURE_DIR/checklists/ui-ux.md`.
  - Nếu `ui-ux.md` đã tồn tại: **giữ nguyên** trạng thái `[x]` + note người đã ghi; chỉ cập nhật nội dung item nếu bộ cố định đổi (không đánh lại số CHK).
  - Thay `[DATE]` bằng ngày hiện tại, `[Link to spec.md]` bằng đường dẫn spec.md của feature.

### Bước 2 — Chấm (chỉ khi có spec)
Nếu `$ARGUMENTS` chỉ tới spec.md (hoặc feature có spec.md): đọc spec, chấm **từng mục còn `[ ]` trống** (KHÔNG đụng mục người đã `[x]`):
- **Pass** → tick `[x]`, ghi cuối dòng ` — ✅ nguồn: <FR-xxx/§IV/…>`.
- **N/A** → giữ `[ ]`, ghi ` — ➖ N/A: <lý do>`.
- **Gap** (spec thiếu/mơ hồ, tester không viết được testcase) → giữ `[ ]`, ghi ` — ⚠️ Gap: <thiếu gì>`.
Mỗi verdict PHẢI trích nguồn spec; không có nguồn = Gap. Thêm cuối file mục `## Tổng` (đếm Pass/N/A/Gap).

### Bước 3 — Thảo luận & vá gap (có kiểm soát)
Command này vốn là gate read-only; chỉ sửa `spec.md` khi người dùng đồng ý từng mục. Với MỖI Gap:
1. Hỏi qua **AskUserQuestion** (một câu/lần, 2–4 option, `(Recommended)` đầu, kèm lý do) cách vá.
2. Cảnh báo rõ "sẽ chỉnh spec.md" trước khi ghi.
3. Ghi bổ sung vào một mục **`## Clarifications`** trong spec.md (append), giữ cấu trúc + dấu nguồn; **không sửa/ghi đè requirement đã có** — nếu cần đổi requirement gốc thì hand-off `/speckit.specify` hoặc `/speckit.clarify`, không tự sửa ở đây.
4. Chấm lại mục đó; đạt thì tick `[x]` + nguồn mới. Cập nhật `## Tổng`.
Hết gap (hoặc người dùng chấp nhận để lại): DỪNG, báo tổng kết.

Verdict đã gắn (`— ✅/⚠️/➖`) là trạng thái review, KHÔNG coi là "nội dung item cố định" khi re-run so sánh — re-run chỉ đồng bộ text mục CHK theo bộ cố định, giữ nguyên verdict + tick.

Không có spec → chỉ Bước 1, báo đã tạo list trống rồi DỪNG (không chạy core).

Ngược lại (args khác), chạy bình thường phần core bên dưới.

{CORE_TEMPLATE}
