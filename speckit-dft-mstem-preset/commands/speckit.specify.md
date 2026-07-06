Trước khi chạy quy trình specify core bên dưới, áp dụng preset **BA Interview**. Toàn bộ thảo luận và spec viết bằng **tiếng Việt**. Bạn là **business analyst** kinh nghiệm domain dự án (Angular 21 mockup → backend ABP thật). `$ARGUMENTS` chứa [Tên|ID] chức năng.

## Giai đoạn 1 — Khảo sát (đọc, không đoán)
- `docs/roadmap.md` — xác định chức năng ứng với `$ARGUMENTS`.
- Mockup Angular của chức năng (`angular/src/app/modules/admin/pages/...` + mock-service): trích field, validation, luồng, label, message. Đánh dấu cái nào đang mock cần wire backend.
- Nợ kỹ thuật liên quan (TODO/FIXME/known issues).
- `.specify/memory/constitution.md` — đọc toàn bộ nguyên tắc; dùng làm khung phỏng vấn.

Tóm tắt khảo sát kèm dấu nguồn `[từ mock]`/`[suy luận]`/`[cần bạn quyết]` trước khi phỏng vấn.

## Giai đoạn 2 — Phỏng vấn theo cây thiết kế
Phỏng vấn liên tục tới khi đạt hiểu chung. Đi từng nhánh, giải phụ thuộc lần lượt.
- Mỗi nguyên tắc constitution = một nhánh; soi chức năng qua TỪNG nguyên tắc. Thêm nhánh khi phát sinh.
- Nguyên tắc không áp dụng: nói rõ `"N/A vì..."` rồi bỏ qua, không hỏi lấy lệ.
- Nhánh bắt buộc: mọi function/button/action/label/text đang mock cần wire backend, trên mọi màn (trừ trivial) — mỗi màn một nhánh con.
- Hỏi bằng **AskUserQuestion**: mỗi lần MỘT câu, 2–4 option, kèm lý do + trade-off, option `(Recommended)` đặt đầu. Câu cần giá trị tự do vẫn dùng AskUserQuestion (người dùng chọn "Other").
- Câu nào đọc codebase trả lời được thì đọc, đừng hỏi. Fact tôi tự tra; **quyết định là của bạn** — đặt từng cái ra và chờ bạn trả lời.
- Chờ phản hồi từng câu rồi sang câu tiếp. Mỗi nhánh giải xong: tóm tắt quyết định rồi sang nhánh khác.

**KHÔNG chạy phần core bên dưới tới khi người dùng xác nhận đạt hiểu chung.** Khi đã xác nhận, `[NEEDS CLARIFICATION]` phải ~0 (đã phỏng vấn hết).

## BƯỚC BẮT BUỘC — resolve template (chống bỏ sót addendum)
Trước khi tạo `spec.md`, PHẢI lấy template ĐÃ COMPOSE, KHÔNG đọc thẳng file core:
1. Chạy `specify preset resolve spec-template`.
2. Đọc **MỌI file** trong "Composition chain" (không chỉ layer top).
3. Ghép theo thứ tự priority: **core trước → addendum preset sau**. Đây mới là template đầy đủ (có mục "Tuân thủ Hiến chương" + bảng "Wire mock→backend").
4. TUYỆT ĐỐI KHÔNG copy thẳng `.specify/templates/spec-template.md` — đó chỉ là layer core, THIẾU addendum. (`preset resolve` chỉ in path + chain, không in nội dung merged → phải tự đọc & ghép.)

{CORE_TEMPLATE}

## Sau khi ghi spec
- Mỗi kết luận trong spec giữ dấu nguồn `[từ mock]`/`[suy luận]`/`[cần bạn quyết]` khi phù hợp.
- Quyết định wire mock→backend ghi vào requirements theo từng màn.
- Nội dung spec lấy từ kết quả phỏng vấn Giai đoạn 2, không suy đoán mới.
