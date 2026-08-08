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

**Domain doc** (nguồn làm giàu, **KHÔNG bắt buộc**): tìm bằng **quét nội dung `docs/domain/`, KHÔNG suy theo tên file** — tên file là tên cụm do người đặt, không suy được từ module/feature.

1. Không có thư mục `docs/domain/` hoặc thư mục rỗng → **đi tiếp bình thường**, không hỏi, không coi là lỗi.
2. Có → liệt kê mọi `*.md`, đọc **header + mục §1 (bảng thực thể)** của từng file. Chấm liên quan theo thứ tự tin cậy: (a) RM-ID của feature nằm trong dòng `Phủ RM` hoặc cột `Dùng ở (RM)` — **khớp chắc**; (b) module của item roadmap nằm trong dòng `Phủ module` — khớp khá; (c) entity/chủ đề trong doc trùng phạm vi feature — khớp yếu, chỉ dùng khi (a) và (b) đều rỗng. Nêu **bằng chứng** (dòng nào khớp), không kết luận bằng cảm giác.
3. **Xác nhận với người dùng trước khi dùng** (AskUserQuestion, gộp cùng lượt hỏi khác nếu có): trình file đã chọn + bằng chứng, cho phép **chỉ định lại file khác** hoặc **nói không dùng**. Nhiều file cùng khớp → liệt kê hết, cho chọn (có thể chọn nhiều). Không file nào khớp hoặc không chắc → **hỏi thẳng** "dự án có domain doc cho phần này không, ở đâu?" — người dùng nói không có → đi tiếp, không hỏi lại.
4. Đã xác nhận → dùng entity/FK/enum/rule ở đó làm **nguồn chuẩn** khi thiết kế data-model / điền Technical Context; KHÔNG mâu thuẫn doc, KHÔNG đẻ lại entity framework đã cung cấp (doc đánh dấu "dùng lại framework"). Thiết kế lòi ra thiếu/sai so với doc → cập nhật ngược **đúng file đó** (living doc).

**CẤM**: đoán theo tên file; tự chọn khi có ≥2 ứng viên; coi việc không có domain doc là lỗi hay điều kiện chặn.

Cổng Constitution Check của plan-template mặc định PHẢI pass trước Phase 0. Vi phạm chỉ được chấp nhận khi có biện minh ghi trong bảng Complexity Tracking (theo luật core); vi phạm không biện minh được → sửa thiết kế cho hết vi phạm, không đi tiếp.

{CORE_TEMPLATE}
