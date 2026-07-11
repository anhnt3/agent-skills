---
description: Plan khảo sát codebase + đọc ràng buộc kế thừa từ spec.md.
strategy: wrap
---

Trước khi chạy quy trình plan core bên dưới:

## Khảo sát codebase (đọc, không đoán)
Trước khi điền Technical Context / Structure Decision, khảo sát **codebase** hiện có **liên quan chức năng trong spec** (không quét cả repo — chỉ phần dính tới feature này).

**Ràng buộc kế thừa từ specify**: đọc section `## Ràng buộc kỹ thuật kế thừa (cho /speckit.plan)` ở cuối `spec.md` (do preset specify ghi). Có section → mỗi ràng buộc trong đó là **đầu vào bắt buộc** khi điền Technical Context / thiết kế — không được bỏ sót; đối chiếu lại ở Constitution Check. Không có section (spec tạo trước preset v3 hoặc bằng lệnh khác) → bỏ qua, không coi là lỗi.

**Domain doc của module** (nếu có, nguồn làm giàu): xác định module — ưu tiên lấy cột `Module` từ item roadmap tương ứng feature nếu dự án có roadmap; không có roadmap/cột đó thì suy luận từ spec/tên feature hoặc đường dẫn codebase, không chắc thì hỏi người dùng. Có module rồi, đọc `docs/domain/<module>.md` (`/`→`-`). Không thấy → thử doc gom theo **prefix** (segment cha, vd `system/admins` → `docs/domain/system.md`). Dùng entity/FK/enum/rule ở đó làm **nguồn chuẩn** khi thiết kế data-model / điền Technical Context — KHÔNG mâu thuẫn doc, KHÔNG đẻ lại entity framework đã cung cấp (doc đã đánh dấu "dùng lại framework"). Thiết kế lòi ra thiếu/sai so với doc → cập nhật ngược `docs/domain/<module>.md` (living doc).

Cổng Constitution Check của plan-template mặc định PHẢI pass trước Phase 0. Vi phạm chỉ được chấp nhận khi có biện minh ghi trong bảng Complexity Tracking (theo luật core); vi phạm không biện minh được → sửa thiết kế cho hết vi phạm, không đi tiếp.

{CORE_TEMPLATE}
