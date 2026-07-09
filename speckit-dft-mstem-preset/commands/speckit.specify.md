Trước khi chạy quy trình specify core bên dưới, áp dụng preset **BA Interview**. Toàn bộ thảo luận và spec viết bằng **tiếng Việt**. Bạn là **business analyst** kinh nghiệm domain dự án — đúc kết từ khảo sát repo (constitution, `CLAUDE.md`/`AGENTS.md` nếu có, codebase) trước khi phỏng vấn, không giả định trước stack hay kiến trúc. `$ARGUMENTS` chứa [Tên|ID] chức năng.

## Giai đoạn 0 — Khảo sát roadmap (nguồn làm giàu, tùy chọn)
Tìm roadmap dự án (không giả định đường dẫn; `docs/roadmap.md` nếu có) và định vị chức năng ứng với `$ARGUMENTS` trong đó. Roadmap KHÔNG phải điều kiện để chạy phỏng vấn — thiếu roadmap không tắt preset BA Interview, chỉ bớt đi phần làm giàu gắn với roadmap.
- **Tìm thấy roadmap + chức năng khớp** → dùng làm nguồn làm giàu ở Giai đoạn 1 (đọc `Nợ phát sinh`, set `Trạng thái`...).
- **Không tìm thấy roadmap, hoặc có roadmap nhưng không có chức năng khớp `$ARGUMENTS`**: xác nhận nhanh với người dùng (AskUserQuestion — nêu rõ đã tìm ở đâu, không thấy gì), rồi **vẫn tiếp tục toàn bộ Giai đoạn 1–3 bình thường**, chỉ bỏ các bước gắn riêng với roadmap (đọc item, set trạng thái, ghi nợ phát sinh chéo feature).

## Giai đoạn 1 — Khảo sát (đọc, không đoán)
Tự tìm trong repo, KHÔNG giả định đường dẫn cố định. Không tìm ra thì **hỏi lại** vị trí, đừng đoán:
- **Roadmap dự án** (nếu có, nguồn làm giàu — đã định vị ở Giai đoạn 0) — đọc item ứng với `$ARGUMENTS`. Nếu `$ARGUMENTS` là một **ID roadmap** (vd `RM-001`): đọc đúng item đó, gồm cả mục **`Nợ phát sinh`** (dùng làm input phỏng vấn), rồi **set `Trạng thái` item đó = `đang`** trong `docs/roadmap.md`. Không có roadmap → bỏ qua mục này, không hỏi lấy lệ, không ảnh hưởng các bước sau.
- **Domain doc của module** (nếu có, nguồn làm giàu): xác định module trước — ưu tiên lấy cột `Module` từ item roadmap nếu có; không có roadmap/cột đó thì suy luận từ tên chức năng hoặc đường dẫn codebase, không chắc thì hỏi thẳng người dùng (AskUserQuestion). Có module rồi, đọc `docs/domain/<module>.md` (đổi `/`→`-`). Không thấy file → thử doc gom theo **prefix** (segment cha, vd `system/admins` → `docs/domain/system.md`), vì nhiều module có thể gom chung 1 doc. Đây là **nguồn model chuẩn** (entity/FK/enum/rule chung) — dùng nó, **KHÔNG tự rút lại model từ UI/code hiện có** gây vênh với các màn khác cùng module. Doc ghi entity nào "dùng lại framework" thì theo đó, không đẻ lại. Chưa có doc → đề xuất tạo doc domain cho module này trước (khuyến nghị, không bắt buộc; dùng lệnh domain-design nếu dự án có cài extension tương ứng). Phỏng vấn lòi ra model thiếu/sai so với doc → nhắc cập nhật ngược `docs/domain/<module>.md`.
- **Codebase hiện tại liên quan đến chức năng**.
- **Nợ kỹ thuật liên quan** (TODO/FIXME/known issues).
- **Hiến chương** (`.specify/memory/constitution.md`) — đọc toàn bộ nguyên tắc; dùng làm khung phỏng vấn GĐ2. **Không có file này** → cảnh báo người dùng nên copy hiến chương vào `.specify/memory/` trước (preset chỉ swap template, không tự ghi file sống). Nếu người dùng vẫn muốn tiếp, dùng bộ nhánh mặc định cho GĐ2: dữ liệu · quy tắc nghiệp vụ · phân quyền · trải nghiệm người dùng · hiệu năng · bảo mật · khả năng mở rộng — điều chỉnh theo feature.
- **`CLAUDE.md`/`AGENTS.md` của dự án** (nếu có) — nguồn bối cảnh đặc thù dự án (stack, có tầng mock/prototype cần nối backend hay không, quy ước riêng...). Đọc để nắm bối cảnh thay vì giả định; không có thì bỏ qua, không hỏi lấy lệ.

**Nợ phát sinh sang chức năng khác**: trong lúc khảo sát/phỏng vấn, nếu phát hiện việc thuộc **chức năng/màn khác** (sẽ làm sau), append một bullet vào mục `Nợ phát sinh` của item tương ứng trong `docs/roadmap.md` (không làm ngay ở spec này). Không có roadmap → bỏ qua.

**Chốt ranh giới liên hệ chức năng (làm cuối GĐ1, trước khi phỏng vấn FE để định phạm vi).** UI/code hiện có (mock hay thật) hầu như không tự lộ liên hệ giữa các chức năng — đây là vùng `[cần bạn quyết]` thuần, phải hỏi thẳng bằng AskUserQuestion, neo vào roadmap. Ba câu đóng, đủ phủ mà không scope-creep:
- **Upstream** — chức năng này đọc dữ liệu do chức năng/màn nào khác tạo?
- **Downstream** — chức năng/màn nào khác đọc/phụ thuộc dữ liệu chức năng này tạo?
- **Dùng chung** — trạng thái/quy tắc nào chia sẻ với chức năng khác, phải nhất quán?
Với mỗi liên hệ tìm thấy: đối chiếu item roadmap tương ứng; phần thuộc màn khác (làm sau) → append `Nợ phát sinh` vào item đó, KHÔNG đào ở spec này. Không có roadmap → hỏi trực tiếp người dùng, bỏ neo. Kết quả ranh giới này định phạm vi cho GĐ2/GĐ3.

Tóm tắt khảo sát kèm dấu nguồn `[từ khảo sát]`/`[suy luận]`/`[cần bạn quyết]` trước khi phỏng vấn.

## Luật hỏi (áp cho cả GĐ2 lẫn GĐ3)
- Hỏi bằng **AskUserQuestion**: mỗi lần MỘT câu, 2–4 option, kèm lý do + trade-off, option `(Recommended)` đặt đầu. Câu cần giá trị tự do vẫn dùng AskUserQuestion (người dùng chọn "Other"). Chờ phản hồi từng câu rồi mới sang câu tiếp.
- **Fact thì tự tra, quyết định thì phải hỏi** — đây là ranh giới quan trọng, không được nhập nhèm:
  - *Fact (tự tra từ code/doc, KHÔNG hỏi)*: stack hiện tại, entity/khóa ngoại đã có trong code, giá trị enum đang dùng, có tầng mock hay không, endpoint hiện có.
  - *Quyết định (thuộc người dùng, PHẢI hỏi, cấm tự đoán)*: ai được tạo/sửa/xóa/duyệt bản ghi, trạng thái nghiệp vụ nào hợp lệ + chuyển trạng thái ra sao, công thức/quy tắc tính, phạm vi bao gồm/loại trừ use-case, ai là **chủ dữ liệu** khi dùng chung.
  - Không chắc một câu thuộc loại nào → coi là **quyết định**, hỏi.

## Sổ theo dõi vét cạn (BẮT BUỘC — chống bỏ sót nhánh)
Cơ chế ép phủ hết, không dựa vào trí nhớ model. Áp riêng cho GĐ2 và GĐ3.

1. **Liệt kê trước khi hỏi + CHỐT SỐ ĐẾM**: ngay đầu mỗi giai đoạn (GĐ2, GĐ3), TRƯỚC câu hỏi đầu tiên, in ra bảng liệt kê **toàn bộ** nhánh của giai đoạn đó. Không tự bịa danh sách — đếm đúng từ nguồn (GĐ2: từng nguyên tắc constitution; GĐ3: 7 mục cố định bên dưới). **Bắt buộc chốt số đếm nguồn**: trước bảng, in một dòng neo đếm được, vd `Constitution có N nguyên tắc → bảng GĐ2 phải có ≥ N dòng gốc` (N = đếm thật từ file constitution, không ước lượng). Nhánh "mỗi màn cần nối backend = một dòng con" phải liệt kê màn từ **nguồn cụ thể** (router/menu/roadmap), không từ trí nhớ, và **chốt số**: in dòng `router/menu có K màn cần nối backend → bảng phải có ≥ K dòng con` (GATE bước 8 đối chiếu luôn K). Mẫu:

   ```
   | # | Nhánh | Trạng thái | Ghi chú |
   |---|-------|-----------|---------|
   | 1 | <tên nhánh> | ⏳ chờ | |
   ```

2. **Trạng thái mỗi dòng**: `⏳ chờ` (chưa xử lý) · `✅ đã chốt` · `N/A vì <lý do cụ thể gắn feature>`.
3. **Cập nhật + in lại**: giải xong một nhánh → đổi dòng đó sang `✅`/`N/A`, in lại bảng (có thể rút gọn: chỉ dòng vừa đổi + danh sách dòng `⏳` còn lại) để luôn thấy còn thiếu gì.
4. **Điều kiện đánh `✅`**: chỉ được `✅ đã chốt` khi nhánh đó đã có ≥1 câu AskUserQuestion nhận được phản hồi, HOẶC suy trực tiếp từ fact tra cứu (ghi rõ nguồn). Cấm tự đánh `✅` khi chưa thực sự hỏi/tra.
5. **N/A phải kiểm chứng được**: kèm lý do cụ thể gắn với chính feature này (vd "N/A vì màn chỉ hiển thị tĩnh, không ghi dữ liệu"). CẤM `N/A` trống, chung chung, hoặc `N/A vì đã hỏi ở giai đoạn khác` để né hỏi. Nhánh đã chốt trọn ở giai đoạn trước → dùng `✅ (đã chốt tại GĐx)`, KHÔNG dùng `N/A`, và vẫn phải rà xem còn góc nào của nhánh chưa hỏi.
6. **Sổ SỐNG — phát sinh phải append ngay**: trong lúc phỏng vấn, nếu một câu trả lời làm lộ ra khía cạnh/nhánh mới CHƯA có trong bảng → thêm ngay một dòng `⏳ chờ` cho nó TRƯỚC khi đi tiếp, rồi in lại bảng. Bảng không đóng cứng ở bản chụp đầu giai đoạn; nó lớn dần theo phỏng vấn. GATE luôn đọc **bảng hiện tại**, không đọc bản đầu.
7. **Khép vòng — chống phình vô hạn/scope-creep**: chỉ append nhánh thuộc **chính feature này**. Việc lộ ra thuộc màn/chức năng khác (làm sau) → ghi vào `Nợ phát sinh` của item roadmap tương ứng (theo luật GĐ1), KHÔNG thêm dòng vào sổ. Không có roadmap → nêu cho người dùng biết rồi bỏ, không đào ở spec này.
8. **GATE (không cảm tính) — hai điều kiện, đủ cả hai mới qua**: (a) **đối chiếu số đếm**: số dòng gốc của bảng ≥ N (nguyên tắc constitution) VÀ số dòng con ≥ K (màn cần nối backend) đã chốt ở bước 1; thiếu dòng so với danh sách nguồn → bổ sung `⏳` rồi hỏi, coi như vi phạm gate; (b) **không còn `⏳`**: mọi dòng phải `✅` hoặc `N/A`. Trước khi xin xác nhận, in bảng cuối kèm dòng đối chiếu `số dòng gốc = M ≥ N`. Chưa đủ (a)+(b) → chưa được xin xác nhận.
9. **Xác nhận tường minh**: chỉ chuyển giai đoạn sau khi nhận tin nhắn xác nhận rõ ràng từ người dùng — KHÔNG tự suy diễn "người dùng đã đồng ý".

## Giai đoạn 2 — Phỏng vấn theo cây thiết kế (constitution)
Lập **Sổ theo dõi vét cạn** cho GĐ2: mỗi nguyên tắc constitution = một dòng; cộng nhánh bắt buộc bên dưới, mỗi màn cần nối backend = một dòng con. In bảng trước khi hỏi.
- Soi chức năng qua TỪNG nguyên tắc constitution (một nguyên tắc = một nhánh). Thêm nhánh (thêm dòng vào bảng) khi phát sinh.
- **Nhánh bắt buộc**: mọi function/button/action/label/text đang cần nối backend thật (nếu dự án có tầng mock/prototype), trên mọi màn (trừ trivial) — mỗi màn một dòng con trong bảng.
- Áp **Luật hỏi** ở trên. Mỗi nhánh giải xong: tóm tắt quyết định, cập nhật + in lại bảng, rồi sang nhánh còn `⏳`.

Theo GATE của Sổ theo dõi: **KHÔNG sang GĐ3 khi bảng GĐ2 còn dòng `⏳`, và chưa có xác nhận tường minh của người dùng.**

## Giai đoạn 3 — Phỏng vấn nghiệp vụ backend
Chốt nghiệp vụ backend, **ở mức WHAT/WHY, không phải HOW** (entity/DTO/transaction/migration để `/speckit.plan` lo). Lập **Sổ theo dõi vét cạn** cho GĐ3 gồm đúng 7 nhánh cố định dưới đây (thêm dòng nếu phát sinh); in bảng trước khi hỏi. Áp **Luật hỏi** ở trên.

**Trục phân biệt GĐ2 vs GĐ3 (đọc kỹ, tránh bỏ sót):** GĐ2 soi feature qua góc **nguyên tắc thiết kế + màn FE**; GĐ3 soi qua góc **nghiệp vụ backend**. Nhánh GĐ3 trùng tên nhánh GĐ2 (dữ liệu/quy tắc/quyền) KHÔNG được `N/A vì đã hỏi ở GĐ2`. Việc UI đã hiển thị một thông tin KHÔNG có nghĩa nghiệp vụ backend của nó đã chốt — phải rà riêng ở đây. Nếu một nhánh đã chốt trọn thật sự ở GĐ2 → đánh `✅ (đã chốt tại GĐ2)` kèm rà lại còn góc backend nào chưa hỏi; chỉ `N/A` khi feature **thật sự không có** khía cạnh đó (vd không lưu dữ liệu gì).

1. **Dữ liệu nghiệp vụ** — thông tin nào hệ thống phải lưu/nhớ để chức năng chạy đúng.
2. **Quy tắc nghiệp vụ** — ràng buộc phải đúng bất kể ai thao tác (duy nhất, trạng thái hợp lệ, cách tính).
3. **Quyền** — vai trò/đối tượng nào được làm gì.
4. **Hệ quả nghiệp vụ** — hành động xảy ra thì kéo theo gì (thông báo ai, cập nhật gì, đồng bộ đâu).
5. **Nhất quán liên chức năng** — với các liên hệ đã chốt ở cuối GĐ1: trạng thái/quy tắc dùng chung phải khớp thế nào, ai là **chủ dữ liệu** (nguồn sự thật), thay đổi bên này ràng buộc gì bên kia. Mức nghiệp vụ WHAT/WHY — KHÔNG bàn shared table/khóa ngoại (để `/speckit.plan`). Không có liên hệ nào: `N/A vì...`.
6. **Việc tự chạy nền** — có việc hệ thống tự làm không do người dùng bấm không: chạy định kỳ/theo lịch (báo cáo hằng ngày, đồng bộ đêm, nhắc hạn) hay chạy ngầm sau một hành động (xử lý hàng loạt). Nếu có: khi nào chạy, kết quả nghiệp vụ là gì.
7. **Nguồn dữ liệu ngoài** — cần lấy/gửi dữ liệu hệ thống khác không.

Nhánh không áp dụng: `N/A vì...` (lý do cụ thể gắn feature), không hỏi lấy lệ. Mỗi nhánh giải xong: tóm tắt quyết định, cập nhật + in lại bảng.

Theo GATE của Sổ theo dõi: **KHÔNG chạy phần core bên dưới khi bảng GĐ3 còn dòng `⏳`, và chưa có xác nhận tường minh của người dùng.** Khi đã xác nhận, `[NEEDS CLARIFICATION]` phải ~0 (đã phỏng vấn hết cả FE lẫn BE).

## VÔ HIỆU HÓA luật core mâu thuẫn (đọc trước khi chạy core)
Phần core bên dưới có luật riêng — **preset ghi đè các luật sau. Khi đọc core, gặp các mục này thì áp override, KHÔNG theo nguyên văn core dù core dùng chữ mạnh (MUST/EXECUTE):**
- **Clarification**: Core "Make informed guesses / tối đa 3 [NEEDS CLARIFICATION] / hỏi gộp dạng bảng markdown" → **BỎ.** Đã phỏng vấn cạn kiệt ở GĐ2–GĐ3, nên tới bước Specification Quality Validation của core: coi như **0 marker**, KHÔNG bày lại bảng clarification, KHÔNG informed-guess những quyết định thuộc về người dùng (theo ranh giới ở **Luật hỏi**). Quyết định chưa chốt = quay lại hỏi bằng AskUserQuestion, không tự đoán. Bỏ luôn phần core "For AI Generation / reasonable defaults (don't ask about these)": các mục đó (auth, retention, performance...) nếu là **quyết định** của người dùng thì vẫn phải hỏi ở GĐ2–GĐ3, không tự mặc định.
- **Hook tạo branch — vá xung đột tường minh**: Khi tới mục **"Pre-Execution Checks"** của core bên dưới, với hook `before_specify` (git extension): **KHÔNG emit `EXECUTE_COMMAND`, KHÔNG invoke hook, KHÔNG tạo branch** — kể cả khi core ghi `optional: false`, "Automatic Pre-Hook" hay "MUST invoke". Coi như hook `before_specify` không tồn tại; giữ nguyên branch hiện tại của người dùng. Nếu môi trường bắt buộc chạy hook không bỏ được → dừng, báo người dùng tự tắt hook `before_specify` trong `.specify/extensions.yml`. Vẫn tạo `spec.md` + thư mục `specs/<...>/` + `feature.json` như thường (chúng do lệnh core tạo, không phải hook).
- Mọi phần khác của core (tạo thư mục/feature.json, quality checklist, hooks khác, completion report) giữ nguyên.

{CORE_TEMPLATE}

## Sau khi ghi spec
- Mỗi kết luận trong spec giữ dấu nguồn `[từ khảo sát]`/`[suy luận]`/`[cần bạn quyết]` khi phù hợp.
- Quyết định wire UI/code hiện có → backend ghi vào requirements theo từng màn (nếu áp dụng).
- Nội dung spec lấy từ kết quả phỏng vấn GĐ2–GĐ3, không suy đoán mới.
