---
description: Plan khảo sát codebase + đọc ràng buộc kế thừa từ spec.md.
strategy: wrap
---

Chạy bước **Setup** của core bên dưới TRƯỚC (script setup-plan cho FEATURE_SPEC/IMPL_PLAN/SPECS_DIR — không tự đoán feature dir); các việc sau đây chèn **giữa Setup và bước điền Technical Context**:

## Khảo sát codebase (đọc, không đoán)
Trước khi điền Technical Context / Structure Decision, khảo sát **codebase** hiện có **liên quan chức năng trong spec** (không quét cả repo — chỉ phần dính tới feature này).

**Ràng buộc kế thừa từ specify**: đọc section `## Ràng buộc kỹ thuật kế thừa (cho /speckit.plan)` ở cuối `spec.md` (do preset specify ghi). Có section → **đếm số ràng buộc = R**, và tại Constitution Check in **bảng đúng R dòng**: mỗi ràng buộc → nơi nó được phản ánh trong plan (mục/file cụ thể) HOẶC lý do không áp dụng cho feature này. Thiếu dòng = chưa xong; CẤM kết luận "đã đối chiếu ✓" bằng một câu không có bảng. Không có section (spec tạo trước preset v3 hoặc bằng lệnh khác) → bỏ qua, không coi là lỗi.

**Đọc spec theo kỷ luật một-nhà + QUYẾT cơ chế (nếu spec do preset ghi)**: spec tách ba nhà — dùng đúng nguồn khi điền Technical Context / data-model, và plan là nơi CHỐT phần cơ chế mà spec cố ý bỏ ngỏ:
- `## Thực thể & Từ điển dữ liệu` = nguồn **data-model** (field, kiểu, giới hạn, giá trị hợp lệ). Đây là nơi chứa hằng số — không tự bịa field ngoài đây, không mâu thuẫn.
- `### Functional Requirements` = **hành vi + business rule** (duy nhất, liên trường, phân quyền, vòng đời, công thức). `## Đặc tả màn hình` chỉ là trình bày và trỏ FR/field — đừng rút model/luật từ mục màn.
- Spec **cố ý bỏ ngỏ cơ chế** ("bằng lời", không thư viện/mã hoá). Plan là nơi CHỐT cơ chế và ghi vào ĐÚNG artifact core đã sinh — **KHÔNG tạo section "Cơ chế" mới trong `plan.md`** (tránh trùng vai với `research.md`):
  - **`research.md`** (Phase 0 — quyết định + lý do, dạng ADR): thư viện validation áp các luật ở DD/FR, cách lấy chuỗi thông báo từ resource string/message catalog của framework, quy ước định danh e2e (`data-testid`), thư viện a11y/responsive. Mỗi quyết định kèm lý do ngắn.
  - **`data-model.md`** (Phase 1): ánh xạ mỗi field trong `## Thực thể & Từ điển dữ liệu` → kiểu cột + ràng buộc DB; entity/quan hệ rút từ đó (không mâu thuẫn giới hạn đã khai ở DD).
  Không có các mục DD/FR/màn trong spec (spec tạo bằng lệnh khác) → bỏ qua, không coi là lỗi.

**Domain doc của module** (nếu có, nguồn làm giàu): xác định module — ưu tiên lấy cột `Module` từ item roadmap tương ứng feature nếu dự án có roadmap; không có roadmap/cột đó thì suy luận từ spec/tên feature hoặc đường dẫn codebase, không chắc thì hỏi người dùng. Có module rồi, đọc `docs/domain/<module>.md` (`/`→`-`). Không thấy → thử doc gom theo **prefix** (segment cha, vd `system/admins` → `docs/domain/system.md`). Dùng entity/FK/enum/rule ở đó làm **nguồn chuẩn** khi thiết kế data-model / điền Technical Context — KHÔNG mâu thuẫn doc, KHÔNG đẻ lại entity framework đã cung cấp (doc đã đánh dấu "dùng lại framework"). Thiết kế lòi ra thiếu/sai so với doc → cập nhật ngược `docs/domain/<module>.md` (living doc).

Cổng Constitution Check của plan-template mặc định PHẢI pass trước Phase 0. Vi phạm chỉ được chấp nhận khi có biện minh ghi trong bảng Complexity Tracking (theo luật core); vi phạm không biện minh được → sửa thiết kế cho hết vi phạm, không đi tiếp.

{CORE_TEMPLATE}
