Trước khi chạy quy trình plan core bên dưới:

## Khảo sát codebase (đọc, không đoán)
Trước khi điền Technical Context / Structure Decision, khảo sát **frontend và backend** hiện có **liên quan chức năng trong spec** (không quét cả repo — chỉ phần dính tới feature này): mock component/service, DTO, aggregate, permission, convention, migration liên quan. Plan phải dựa trên cái đang có (tái dùng gì, wire vào đâu), không chọn layout mẫu generic.

## BƯỚC BẮT BUỘC — resolve+ghép addendum (chống bỏ sót)
Preset override `plan-template` bằng `strategy: append` — addendum KHÔNG bake vào file core trên đĩa; `specify preset resolve` chỉ in **path + chain, KHÔNG merge**. Khi core (dưới đây) tạo `plan.md` từ template:
1. Chạy `specify preset resolve plan-template`, đọc **MỌI file** trong "Composition chain".
2. Đảm bảo `plan.md` cuối cùng = **core layer + addendum preset** (core trước → addendum sau): phải có mục "Constitution Check — Kỹ thuật (HOW)" (GATE trước Phase 0). Nếu bản core vừa tạo THIẾU addendum → tự ghép addendum vào cuối `plan.md` đó.
3. TUYỆT ĐỐI KHÔNG dừng ở việc copy thẳng `.specify/templates/plan-template.md` (chỉ là layer core, thiếu addendum).

Cổng Constitution Check kỹ thuật PHẢI pass trước Phase 0; vi phạm không biện minh ghi Complexity Tracking.

{CORE_TEMPLATE}
