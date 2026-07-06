Trước khi chạy quy trình plan core bên dưới:

## BƯỚC BẮT BUỘC — resolve template (chống bỏ sót addendum)
Preset ghi đè `plan-template` bằng `strategy: append` — addendum KHÔNG bake vào file core trên đĩa, chỉ hiện khi resolve. Trước khi tạo `plan.md`, PHẢI:
1. Chạy `specify preset resolve plan-template`.
2. Đọc **MỌI file** trong "Composition chain".
3. Ghép theo thứ tự priority: **core trước → addendum preset sau**. Template đầy đủ có mục "Constitution Check — Kỹ thuật (HOW)" (GATE trước Phase 0).
4. TUYỆT ĐỐI KHÔNG copy thẳng `.specify/templates/plan-template.md` — đó chỉ là layer core, THIẾU addendum. (`preset resolve` chỉ in path + chain, không in nội dung merged → phải tự đọc & ghép.)

Cổng Constitution Check kỹ thuật PHẢI pass trước Phase 0; vi phạm không biện minh ghi Complexity Tracking.

{CORE_TEMPLATE}
