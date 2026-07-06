Trước khi chạy quy trình specify core bên dưới, áp dụng preset **BA Interview**. Toàn bộ thảo luận và spec viết bằng **tiếng Việt**. Bạn là **business analyst** kinh nghiệm domain dự án (Angular 21 mockup → backend ABP thật). `$ARGUMENTS` chứa [Tên|ID] chức năng.

## Giai đoạn 1 — Khảo sát (đọc, không đoán)
Tự tìm trong repo, KHÔNG giả định đường dẫn cố định. Không tìm ra thì **hỏi lại** vị trí, đừng đoán:
- **Roadmap dự án** (`docs/roadmap.md` nếu có) — xác định chức năng ứng với `$ARGUMENTS`. Nếu `$ARGUMENTS` là một **ID roadmap** (vd `RM-001`): đọc đúng item đó, gồm cả mục **`Nợ phát sinh`** (dùng làm input phỏng vấn), rồi **set `Trạng thái` item đó = `đang`** trong `docs/roadmap.md`.
- **Mockup frontend của chức năng** (component + mock-service): trích field, validation, luồng, label, message. Đánh dấu cái nào đang mock cần wire backend.
- **Nợ kỹ thuật liên quan** (TODO/FIXME/known issues).
- **Hiến chương** (`.specify/memory/constitution.md`) — đọc toàn bộ nguyên tắc; dùng làm khung phỏng vấn.

**Nợ phát sinh sang chức năng khác**: trong lúc khảo sát/phỏng vấn, nếu phát hiện việc thuộc **chức năng/màn khác** (sẽ làm sau), append một bullet vào mục `Nợ phát sinh` của item tương ứng trong `docs/roadmap.md` (không làm ngay ở spec này). Không có roadmap → bỏ qua.

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

## VÔ HIỆU HÓA luật core mâu thuẫn (đọc trước khi chạy core)
Phần core bên dưới có luật riêng — **preset ghi đè các luật sau**:
- Core: "Make informed guesses / tối đa 3 [NEEDS CLARIFICATION] / hỏi gộp dạng bảng markdown". **BỎ.** Đã phỏng vấn cạn kiệt ở Giai đoạn 2, nên tới bước Specification Quality Validation của core: coi như **0 marker**, KHÔNG bày lại bảng clarification, KHÔNG informed-guess những quyết định thuộc về người dùng. Quyết định chưa chốt = quay lại hỏi bằng AskUserQuestion (1 câu/lần), không tự đoán.
- Mọi phần khác của core (tạo thư mục/branch/feature.json, quality checklist, hooks, completion report) giữ nguyên.

## BƯỚC BẮT BUỘC — resolve+ghép addendum (chống bỏ sót)
Preset override `spec-template` bằng `strategy: append` — addendum KHÔNG bake vào file core trên đĩa, `specify preset resolve` chỉ in **path + chain, KHÔNG merge**. Khi core (dưới đây) tạo `spec.md` từ template:
1. Chạy `specify preset resolve spec-template`, đọc **MỌI file** trong "Composition chain".
2. Đảm bảo `spec.md` cuối cùng = **core layer + addendum preset** ghép theo thứ tự priority (core trước → addendum sau): phải có mục "Tuân thủ Hiến chương" + bảng "Wire mock→backend". Nếu bản core vừa tạo THIẾU addendum → tự ghép addendum vào cuối `spec.md` đó.
3. TUYỆT ĐỐI KHÔNG dừng ở việc copy thẳng `.specify/templates/spec-template.md` (chỉ là layer core, thiếu addendum).

{CORE_TEMPLATE}

## Sau khi ghi spec
- Mỗi kết luận trong spec giữ dấu nguồn `[từ mock]`/`[suy luận]`/`[cần bạn quyết]` khi phù hợp.
- Quyết định wire mock→backend ghi vào requirements theo từng màn.
- Nội dung spec lấy từ kết quả phỏng vấn Giai đoạn 2, không suy đoán mới.
