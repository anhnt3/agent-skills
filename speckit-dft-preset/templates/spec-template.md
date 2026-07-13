# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

**Input**: User description: "$ARGUMENTS"

<!--
  ┌─ NGUYÊN TẮC MỘT NHÀ (đọc trước khi điền — chống trùng lặp, theo Wiegers / Business Rules Manifesto 2.3 / ISO 29148) ─┐
  Mỗi sự thật chỉ được PHÁT BIỂU ở đúng MỘT mục; mọi mục khác chỉ TRỎ tới, không chép lại:
    • Hằng số của field (độ dài, miền giá trị, định dạng, giá trị hợp lệ, default) → sống ở "Thực thể & Từ điển dữ liệu".
    • Hành vi hệ thống & business rule (duy nhất, liên trường, phân quyền, vòng đời, công thức) → sống ở "Functional Requirements" (FR-###).
    • "Đặc tả màn hình" CHỈ mô tả TRÌNH BÀY & RANH GIỚI (màn nào, control nào, hiển thị gì, trạng thái nào) và TRỎ tới field/FR — TUYỆT ĐỐI không chép lại hằng số hay luật.
    • "Acceptance Scenarios" là VÍ DỤ kiểm chứng, trỏ FR — không phải bản định nghĩa thứ hai của luật.
  Thứ tự ưu tiên khi mâu thuẫn: Data Dictionary > Functional Requirements > Đặc tả màn hình > Acceptance Scenarios.
  Nếu đang viết một con số giới hạn hay một luật ở "Đặc tả màn hình" → nó thuộc DD hoặc FR: chuyển lên đó rồi trỏ.
  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
-->

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

<!--
  Acceptance Scenarios là VÍ DỤ kiểm chứng (specification by example), KHÔNG phải nơi định nghĩa luật.
  Khi một kịch bản đụng một luật hay một hằng số, hãy TRỎ tới FR/field thay vì chép giá trị:
  ✓ "Given email đã tồn tại (FR-012), When lưu, Then báo lỗi trùng"
  ✗ "Given email dài quá 255 ký tự…"  → 255 thuộc Từ điển dữ liệu, đừng chốt số ở đây.
-->

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  Đây là góc nhìn story-level của tình huống biên/lỗi. Cách MỖI màn TRÌNH BÀY các tình huống này
  (loading/rỗng/lỗi) nằm ở "Trạng thái màn" trong Đặc tả màn hình — đừng lặp chi tiết trình bày ở đây.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: Fill with functional requirements AND business rules.
  Đây là nhà DUY NHẤT của HÀNH VI hệ thống và BUSINESS RULE. Mỗi mục: một câu, kiểm được (singular + verifiable).
  Business rule = luật đúng bất kể màn nào nhập (import/API vẫn đúng): tính duy nhất, ràng buộc liên trường,
  phân quyền (ai được làm gì), vòng đời/chuyển trạng thái, công thức tính. Phát biểu ở đây, KHÔNG rải sang màn.
  "Đặc tả màn hình" và "Acceptance Scenarios" sẽ TRỎ số FR, không chép lại nội dung luật.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Business rule (phát biểu như FR, bằng lời, singular) — ví dụ:*

- **FR-006**: System MUST đảm bảo mỗi email là duy nhất trong toàn hệ thống *(quy tắc, đúng kể cả khi tạo qua import)*.
- **FR-007**: System MUST chỉ cho vai trò [Quản trị] thực hiện [duyệt]; các vai trò khác không được *(phân quyền)*.
- **FR-008**: System MUST bảo đảm [Ngày hết hạn] không sớm hơn [Ngày hiệu lực] *(ràng buộc liên trường)*.

*Example of marking unclear requirements:*

- **FR-00X**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]

## Thực thể & Từ điển dữ liệu *(bắt buộc nếu chức năng có dữ liệu)*

<!--
  Đây là nhà DUY NHẤT của thuộc tính field. Mọi HẰNG SỐ (độ dài, miền giá trị, định dạng, giá trị hợp lệ,
  default) chỉ được ghi ở đây. FR trỏ tới, bảng "Nhập liệu" và "Cột" của màn trỏ tới — KHÔNG nơi nào chép lại số.
  Chỉ nêu YÊU CẦU bằng lời/giá trị nghiệp vụ; KHÔNG chọn kiểu cột DB, không đặt tên bảng, không mã hoá — plan lo.
  Định dạng chuẩn toàn chương trình (ngày dd/MM/yyyy, tiền VNĐ, vi-VN) do quy ước chung của dự án lo; ở đây chỉ ghi
  KIỂU nghiệp vụ của field (ngày / tiền / số / email…), không lặp lại quy ước định dạng.
-->

### [Tên thực thể]

[Một câu: thực thể này đại diện cho gì; quan hệ chính với thực thể khác]

| Field | Kiểu | Bắt buộc | Giới hạn (min–max) | Giá trị hợp lệ / Ghi chú |
|---|---|---|---|---|
| [vd Email] | Email | Có | ≤ 255 ký tự | duy nhất — xem FR-006 |
| [vd Số tiền] | Tiền | Có | 0 ≤ x ≤ 1.000.000.000 | bội số 1.000 |
| [vd Trạng thái] | Lựa chọn | Có | — | {Nháp, Chờ duyệt, Đã duyệt, Từ chối} |

*"Giới hạn" ghi rõ toán tử/độ bao hàm (`≤ 255`, `0 ≤ x`). Không áp dụng → `—`. Cần biên chính xác cho boundary test.*

## Đặc tả màn hình *(bắt buộc nếu chức năng có giao diện)*

<!--
  Mục này CHỈ mô tả TRÌNH BÀY & RANH GIỚI của từng màn, bằng ngôn ngữ nghiệp vụ. Nguồn: kết quả phỏng vấn GĐ2.
  KỶ LUẬT MỘT NHÀ (bắt buộc):
    • Hằng số field (độ dài/miền/định dạng/giá trị hợp lệ) → KHÔNG ghi ở đây; đã có ở "Thực thể & Từ điển dữ liệu".
      Ở đây chỉ nhắc TÊN field.
    • Hành vi & business rule (điều gì xảy ra, ai được làm, luật liên trường/duy nhất) → KHÔNG mô tả lại ở đây;
      đã có ở Functional Requirements. Ở đây chỉ TRỎ số FR.
    • Ở đây chỉ thêm phần MÀN MỚI CÓ: control nào, hiển thị cột nào, lọc/sắp/tìm ra sao, kênh báo (inline/toast),
      4 trạng thái màn, xác nhận cho hành động phá hủy.
  KHÔNG ghi cơ chế triển khai (thư viện, resource string, data-testid) — plan/tasks tự quyết theo stack.
  KHÔNG lặp quy ước UI/UX chung toàn chương trình (vi-VN, a11y, responsive, format ngày/tiền) — do frontend agent lo.
  Mỗi mục con CHỈ điền khi màn thực sự có. Chức năng không giao diện → xóa mục này, ghi "Không có màn — nghiệp vụ mô tả ở Requirements".
-->

### Màn: [Tên màn]

- **Mục đích**: [một câu — màn này để làm gì]
- **Vai trò & quyền hiển thị**: [vai trò nào vào được màn; action nào ẩn/khóa với vai trò nào hoặc theo trạng thái bản ghi]. Luật phân quyền thực thi: xem [FR-###]. (Ở đây chỉ mô tả ẩn/khóa trên UI, không phát biểu lại luật.)

**Hành động** *(bỏ nếu màn chỉ hiển thị)*

| Hành động | Control (nút/menu) | Hành vi (trỏ FR) | Xác nhận nếu phá hủy | Phản hồi khi thành công (ý) |
|---|---|---|---|---|
| [vd Tạo mới] | [nút "Tạo mới"] | FR-001 | [—] | [báo tạo thành công] |
| [vd Xóa] | [icon Xóa ở dòng] | FR-0XX | [xác nhận; nếu đối tượng có nội dung con, nêu hệ quả lan truyền, vd "xóa N mục con, M tài liệu"] | [báo xóa thành công] |

**Dữ liệu hiển thị / Cột** *(bỏ nếu không phải danh sách)*

| Cột | Field (từ Từ điển dữ liệu) | Định dạng hiển thị | Khi rỗng/null hiển thị |
|---|---|---|---|
| [Tiêu đề cột] | [tên field] | [ngày / tiền / số / văn bản] | [vd —] |

- **Lọc / Sắp xếp / Tìm kiếm**: [lọc theo field nào (từ DD) + giá trị mặc định; cột nào sắp xếp được + hướng mặc định; ô tìm kiếm tìm theo field nào; hành vi: lọc không ra kết quả → empty state; reset xóa hết filter; đổi filter/tìm kiếm → về trang 1; rời màn rồi quay lại giữ hay mất filter]

**Nhập liệu trên màn** *(bỏ nếu màn không có form)*

<!-- Chỉ liệt kê field NÀO có mặt trên form này + phần thuộc về màn. Hằng số/định dạng ở Từ điển dữ liệu; luật liên trường/duy nhất ở FR — trỏ, không chép. -->

| Trường (từ Từ điển dữ liệu) | Bắt buộc trên màn này? | Ý thông báo khi sai | Kênh báo |
|---|---|---|---|
| [Email] | Có | [sai định dạng · vượt độ dài · trùng (FR-006)] | inline |
| [Số tiền] | Có | [không hợp lệ · vượt trần] | inline |

*Ràng buộc liên trường/duy nhất áp cho form này: xem [FR-006, FR-008]. Nhiều lỗi trên một trường: nêu thứ tự ưu tiên báo.*

- **Trạng thái màn**:
  - *Đang tải*: [hiển thị gì]
  - *Rỗng*: [empty state hiển thị gì; luôn hiện tổng số]
  - *Lỗi* (mất mạng/timeout): [hiển thị gì, có cho thử lại không]
  - *Có dữ liệu*: [hiển thị gì]

---

[Lặp khối "### Màn" cho mỗi màn trong phạm vi chức năng]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
