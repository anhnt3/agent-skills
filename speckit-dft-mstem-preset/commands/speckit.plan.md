Trước khi chạy quy trình plan core bên dưới:

## Khảo sát codebase (đọc, không đoán)
Trước khi điền Technical Context / Structure Decision, khảo sát **codebase** hiện có **liên quan chức năng trong spec** (không quét cả repo — chỉ phần dính tới feature này).

**Domain doc của module** (nếu có, nguồn làm giàu): xác định module — ưu tiên lấy cột `Module` từ item roadmap tương ứng feature nếu dự án có roadmap; không có roadmap/cột đó thì suy luận từ spec/tên feature hoặc đường dẫn codebase, không chắc thì hỏi người dùng. Có module rồi, đọc `docs/domain/<module>.md` (`/`→`-`). Không thấy → thử doc gom theo **prefix** (segment cha, vd `system/admins` → `docs/domain/system.md`). Dùng entity/FK/enum/rule ở đó làm **nguồn chuẩn** khi thiết kế data-model / điền Technical Context — KHÔNG mâu thuẫn doc, KHÔNG đẻ lại entity framework đã cung cấp (doc đã đánh dấu "dùng lại framework"). Thiết kế lòi ra thiếu/sai so với doc → cập nhật ngược `docs/domain/<module>.md` (living doc).

Cổng Constitution Check của plan-template mặc định PHẢI pass trước Phase 0; vi phạm không biện minh ghi Complexity Tracking.

{CORE_TEMPLATE}
