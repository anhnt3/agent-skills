---
description: BA phỏng vấn nghiệp vụ tuần tự trước khi ghi spec.
strategy: wrap
---

Trước khi chạy quy trình specify core bên dưới, áp dụng preset **BA Interview**. Toàn bộ thảo luận và spec viết bằng **tiếng Việt**. Bạn là **business analyst** kinh nghiệm domain dự án — đúc kết từ khảo sát repo (constitution, `CLAUDE.md`/`AGENTS.md` nếu có, codebase) trước khi phỏng vấn, không giả định trước stack hay kiến trúc. `$ARGUMENTS` chứa [Tên|ID] chức năng.

**Mục tiêu**: chốt mọi quyết định nghiệp vụ của chức năng — quyết định **trọng yếu** qua phỏng vấn từng câu, quyết định **thứ yếu** qua đề-xuất-rồi-duyệt-gộp (Bất biến #3) — để `[NEEDS CLARIFICATION]` trong spec ≈ 0. Bạn **tự sinh** câu hỏi theo bối cảnh feature; các "sàn" nêu bên dưới là **mức tối thiểu không được thiếu**, KHÔNG phải giới hạn trên. Vét cạn nhưng tôn trọng thời gian người trả lời: người trả lời mệt thì trả lời ẩu, spec "đầy đủ" mà sai — chất lượng đến từ hỏi đúng trọng tâm, không từ số lượt hỏi.

**Phỏng vấn theo nghiệp vụ, không phỏng vấn theo hiến chương.** GĐ2–GĐ3 hỏi bằng ngôn ngữ nghiệp vụ. Hiến chương KHÔNG phải nguồn sinh câu hỏi — nó là **ràng buộc mà kết quả phỏng vấn phải vượt qua**, đối chiếu ở GĐ4. Đừng bao giờ hỏi người dùng nghiệp vụ về type safety, linter, kỷ luật kiểm thử hay API versioning.

## Bất biến (áp cho toàn lệnh, không ngoại lệ)

1. **Hỏi bằng AskUserQuestion, gom câu độc lập**: mỗi lượt AskUserQuestion chứa 1–4 câu **độc lập nhau** (đáp án câu này không làm đổi nội dung câu kia — thường là các câu cùng một màn hoặc cùng nhóm nhánh); câu phụ thuộc kết quả câu trước → tách sang lượt sau. Mỗi câu 2–4 option, kèm lý do + trade-off. Câu cần giá trị tự do vẫn dùng AskUserQuestion (người dùng chọn "Other"). Chờ phản hồi lượt hiện tại rồi mới gửi lượt tiếp.
2. **Fact thì tự tra, quyết định thì phải hỏi** — ranh giới này không được nhập nhèm:
   - *Fact (tự tra từ code/doc, KHÔNG hỏi)*: stack hiện tại, entity/khóa ngoại đã có trong code, giá trị enum đang dùng, có tầng mock hay không, endpoint hiện có, màn nào đã tồn tại trong router.
   - *Quyết định (thuộc người dùng, PHẢI hỏi hoặc đề xuất-rồi-duyệt theo Bất biến #3, cấm tự chốt)*: ai được tạo/sửa/xóa/duyệt bản ghi, trạng thái nghiệp vụ nào hợp lệ + chuyển trạng thái ra sao, công thức/quy tắc tính, phạm vi bao gồm/loại trừ use-case, ai là **chủ dữ liệu** khi dùng chung, **chức năng cần những màn nào nếu chưa màn nào tồn tại**.
   - Không chắc một câu thuộc loại nào → coi là **quyết định**.
3. **Quyết định chia hai tầng trọng yếu — hỏi cái đáng hỏi, đề xuất cái còn lại**:
   - *Trọng yếu* (PHẢI phỏng vấn từng câu, cấm đề xuất thay): mọi quyết định đụng **dữ liệu / quyền / luồng nghiệp vụ** — ai được tạo/sửa/xóa/duyệt, trạng thái + chuyển trạng thái, công thức/quy tắc tính, phạm vi use-case, chủ dữ liệu, danh sách màn khi chưa có màn nào.
   - *Thứ yếu* (đề xuất rồi duyệt gộp): chi tiết đổi được về sau mà không đụng dữ liệu/quyền/luồng — sắp xếp/lọc mặc định, nội dung empty-state, wording thông báo, bố cục hiển thị. Nhánh thứ yếu KHÔNG tốn lượt hỏi riêng: tự đề xuất giá trị kèm căn cứ, ghi vào sổ trạng thái `💡 đề xuất`; toàn bộ dòng `💡` được duyệt gộp trong recap cuối giai đoạn (Sổ theo dõi §8).
   - Không chắc thuộc tầng nào → coi là **trọng yếu**, hỏi.
4. **`(Recommended)` phải có căn cứ**: chỉ đánh `(Recommended)` khi khảo sát GĐ1 / BRD / domain doc / roadmap cho căn cứ cụ thể, và nêu căn cứ đó ngay trong mô tả option. Quyết định thuần nghiệp vụ mà bạn không có căn cứ → KHÔNG đánh Recommended cho bất kỳ option nào — gợi ý không căn cứ là dẫn người dùng chốt ý của bạn thay vì ý của họ.
5. **Nguồn làm giàu là tùy chọn, phỏng vấn thì không.** Roadmap, BRD, domain doc, hiến chương, `CLAUDE.md` — thiếu cái nào thì chỉ bỏ những bước gắn riêng với cái đó, mọi giai đoạn còn lại chạy đủ. CẤM lấy "thiếu tài liệu" làm lý do rút gọn phỏng vấn. (Luật này nêu một lần ở đây; các giai đoạn dưới không nhắc lại.)
6. **Không tự phê duyệt.** Chỉ chuyển giai đoạn sau khi nhận tin nhắn xác nhận rõ ràng từ người dùng — KHÔNG tự suy diễn "người dùng đã đồng ý". Thứ đưa ra xin xác nhận là **nội dung** (recap quyết định + bảng đề xuất, theo Sổ theo dõi §8), không phải chỉ bảng trạng thái quy trình.
7. **Không có người trả lời thật → HALT.** Lệnh này là phỏng vấn; chạy trong ngữ cảnh không có người trả lời trực tiếp (subagent/CI/autopilot, hoặc AskUserQuestion không khả dụng/không nhận được phản hồi thật) thì **CẤM** tự trả lời thay, tự đoán đáp án, hay tự vượt cổng xác nhận. Thay vào đó: ghi trạng thái hiện tại vào file sổ (Sổ theo dõi §7 — đang ở giai đoạn nào, các câu đang chờ hỏi; nếu còn ở GĐ1 chưa được phép tạo file sổ thì chỉ báo trạng thái, không ghi file) rồi **DỪNG**, báo rõ lệnh cần một phiên có người trả lời. Chạy lại sau (có người) → đọc file sổ, tiếp tục đúng từ điểm dừng.

## Giai đoạn 1 — Khảo sát (đọc, không đoán)

Tự tìm trong repo, KHÔNG giả định đường dẫn cố định. Với **nguồn làm giàu** (roadmap, BRD, domain doc, hiến chương): tìm hợp lý không thấy → hỏi **một lần gộp** ("dự án có roadmap/domain doc/hiến chương không, ở đâu?"); người dùng xác nhận không có → áp Bất biến #5, không hỏi lại. Với thứ **bắt buộc định vị** (codebase liên quan chức năng): không tìm ra thì **hỏi lại** vị trí, đừng đoán. **GĐ1 chưa ghi/sửa bất kỳ file nào** — mọi mutation (roadmap, file sổ) chỉ xảy ra sau xác nhận cuối GĐ1, để phiên hủy giữa chừng không để lại vết bẩn.

- **Roadmap dự án** (vd `docs/roadmap.md`): định vị item ứng với `$ARGUMENTS`. Nếu `$ARGUMENTS` là một **ID roadmap** (vd `RM-001`): đọc đúng item đó, gồm cả mục **`Nợ phát sinh`** (dùng làm input phỏng vấn). CHƯA set trạng thái — việc đó làm sau xác nhận cuối GĐ1.
- **BRD của chính item** (`docs/brd/…`) — nguồn nghiệp vụ gốc, đọc trước khi phỏng vấn, KHÔNG bắt buộc. Định vị DUY NHẤT qua trường **`Nguồn`** trong khối chi tiết của item roadmap (đường dẫn tương đối gốc repo). CẤM: đoán theo tên file; dùng link ô `ID` của bảng tổng (hệ quy chiếu khác — ghép `docs/` vào sẽ ra đường dẫn không tồn tại).
  - `Nguồn` = `docs/brd/….md[#mục]` → Read đúng file/mục đó.
  - `Nguồn` = thư mục → đọc các `.md` ngay trong đó, KHÔNG đệ quy thư mục con.
  - `Nguồn` = `N/A`/đường dẫn code, hoặc không có roadmap / không có `docs/brd/` → bỏ bước này (Bất biến #5).
  - `Nguồn` không tồn tại trên đĩa → hỏi lại đường dẫn (gộp lượt GĐ1); CẤM đoán file gần giống.
  - Rút: bảng trường · trạng thái/giá trị hợp lệ · quy tắc · phân quyền · luồng use-case · thông báo. Mỗi thứ kèm cite `docs/brd/<đường-dẫn>.md#<mục>`; không cite được → không được làm căn cứ `✅` (§3(b)) hay `(Recommended)` (Bất biến #4).
  - Có cả domain doc: model theo domain doc; use-case/thông báo/quyền chi tiết theo BRD; hai bên lệch → trình cả hai, người dùng chọn, CẤM tự chọn.

  **Nhận dạng KHUÔN của BRD** (trước khi rút nội dung — mỗi khuôn bỏ trống một tập mục cố định, biết khuôn = biết trước phải hỏi gì):

  - [ ] Đo dấu vân tay: `grep -rh '^## ' <thư-mục-BRD> | sort | uniq -c | sort -rn` (`<thư-mục-BRD>` = thư mục `docs/brd/…` chứa `Nguồn` của item; không có `Nguồn` → `docs/brd`) — toàn cây, chỉ đọc heading (ngoại lệ có chủ ý của luật không-đệ-quy). H2 lặp ≥3 file = khuôn.
  - [ ] In dấu vân tay cho người dùng → tra bảng. Khớp một hàng = ≥3 H2 của hàng đó có mặt; <3 hoặc khớp nhiều hàng → mô tả + hỏi người dùng, CẤM tự xếp.

  | Dấu vân tay H2 lặp | Khuôn | Khuôn này CẤU TRÚC bỏ trống → phải hỏi |
  |---|---|---|
  | `Mô hình Usecase` · `Kịch bản trường hợp sử dụng` · `Thiết kế mô hình nghiệp vụ` · `Thiết kế giao diện` · `Mô tả điều khiển` | **Hồ sơ thiết kế / đặc tả use-case kiểu RUP-UML** | tiền điều kiện · hậu điều kiện · luồng ngoại lệ · quy tắc nghiệp vụ tách bạch · yêu cầu phi chức năng · hằng số field · tập giá trị lựa chọn · ma trận quyền · vòng đời trạng thái |
  | `Yêu cầu chức năng` · `Yêu cầu phi chức năng` · `Quy tắc nghiệp vụ` | **SRS kiểu IEEE 830 / ISO 29148** | đặc tả màn hình · trạng thái UI · nguyên văn thông báo |
  | Không mục nào lặp | **Không theo khuôn** | coi như im lặng toàn bộ — chạy đủ sàn GĐ2/GĐ3; `M = 0` |

  - [ ] Ghi sổ mục `Khuôn BRD`; đếm `M` = số mục khuôn bỏ trống. Mỗi mục → một dòng `⏳` vào GĐ2 (thuộc màn) / GĐ3 (nghiệp vụ nền), `Nguồn = khuôn BRD`. **Neo: GĐ2+GĐ3 có ≥ `M` dòng `Nguồn = khuôn BRD`** — nạp thiếu là vi phạm gate.
  - [ ] Mục khuôn trùng mục sàn → VẪN TẠO DÒNG RIÊNG mang `Nguồn = khuôn BRD` (đếm vào `M`), trạng thái `✅ (đã phủ tại sàn GĐ<x> mục <n>)` chỉ khi dòng sàn đã `✅`; phần khuôn nêu mà sàn chưa trả lời → thêm `⏳`. CẤM `N/A vì đã có ở dòng sàn`, CẤM chỉ ghi chú vào dòng sàn thay vì tạo dòng (M sẽ không bao giờ đạt).

  **Quét xung đột BRD ↔ quy ước chung** (không tìm thấy file quy ước → hỏi một lần trong lượt gộp GĐ1; không có → bỏ, không nhắc lại). Quét cơ học, không đọc hiểu:

  - [ ] Neo `T` = số section đánh số của file quy ước, đếm bằng `grep -cE '^## [0-9]+\. ' <file quy ước>` (= `S`; ký hiệu riêng, không dùng lại `P`/`Q`). Section không có gì để quét vẫn in dòng `0` — CẤM tự phán "§ này không có gì để quét" để giảm `T`.
  - [ ] **Vòng 2 — đối chiếu theo VAI TRÒ, không chỉ theo chuỗi `CẤM`** (chuỗi chết lọt biến thể đồng nghĩa — đo thật: `"Lưu thông tin"`, `"Đóng"` lọt vì cột `CẤM` chỉ ghi `Lưu lại/Save`, `Cancel`):
    - [ ] Liệt kê MỌI nhãn giao diện trong BRD: nút · hành động · **nhãn trường · tiêu đề form/dialog** (quy ước phủ cả tiêu đề/menu/thông báo, không chỉ nút).
    - [ ] **Gộp dòng trước khi quét — BẮT BUỘC** (pandoc ngắt dòng giữa `<td>`, grep bám dòng sót quá nửa — đo thật: 12/21 nhãn):

    ```bash
    tr '\n' ' ' < <file BRD> \
      | grep -oE '(Button|Action|Label|Title|Textbox|Dropdown|Radio Button|Checkbox|Nút|Nhãn|Tiêu đề|Ô nhập|Danh sách chọn)[[:space:]]*["“][^"”]*["”]' \
      | sed 's/  */ /g' | sort -u
    # Cổng chống-rỗng: BRD có chuỗi trong nháy (grep -c '["“]' > 0) mà lệnh trên trích 0 nhãn
    # ⇒ LỆNH HỎNG (pandoc từ .docx dùng nháy cong “ ”) — sửa lệnh rồi quét lại, CẤM kết luận "0 xung đột".
    ```

    - [ ] Gán vai trò từng nhãn (submit form tạo · submit form sửa · huỷ · đóng · xoá · nhập · xuất · tiêu đề dialog · nhãn trường) → so nhãn CHUẨN của vai trò đó ở bảng thuật ngữ. Lệch = điểm khớp, KỂ CẢ khi chữ không nằm trong cột `CẤM`.
    - [ ] Hai nhãn khác nhau cho cùng một trường/hành động ở hai chỗ trong BRD = điểm khớp (giao diện sẽ hiện hai tên cho một thứ), kể cả khi cả hai đều hợp lệ — đo thật: `"Trạng thái vận hành"` (form) vs `"Trạng thái"` (lưới/bộ lọc).
  - [ ] In bảng **đủ `T` dòng** `| § | Số mục đã quét | Số lần khớp | Điểm khớp (BRD đang ghi → quy ước bắt buộc) |` — ghi cả dòng `0`. Thiếu dòng = vi phạm gate; CẤM kết luận "không xung đột" khi chưa in đủ `T` dòng.
  - [ ] Ghi bảng ra `.specify/interviews/<slug>.scan.md` ngay (ngoại lệ có chủ ý của "GĐ1 chưa ghi file" — chống mất khi phiên đứt). **Mọi trích dẫn file scan trong BRD / `interview-notes.md` phải là đường dẫn SAU bàn giao** (`specs/<thư-mục-feature>/scan-xung-dot-quy-uoc.md`), KHÔNG phải đường dẫn tạm `.specify/interviews/` (đã gặp: trỏ file tạm → chuỗi tham chiếu gãy sau bàn giao).
  - [ ] Mọi dòng `0` → đi tiếp. Có khớp → **quyết định trọng yếu** (Bất biến #3): gom theo NHÓM (nhãn nút · nguyên văn thông báo · thiết kế dữ liệu), mỗi nhóm một câu — theo quy ước hay giữ BRD làm ngoại lệ có lý do. CẤM tự chọn bên. Chốt → append `Xung đột BRD chờ BA` + ghi vào mục `Quy ước chung áp dụng` của BRD ở bước Bổ sung BRD (số hiệu H2 gán lúc chèn, không cố định).
  - [ ] Dương tính giả có thật (nút `✕` ≠ hành động "Hủy") → trình danh sách cho người dùng loại, CẤM báo số tổng như mọi dòng đều sai. Ghi cuối bảng scan dòng tổng **`Điểm lệch còn lại sau phân xử = <n>`** trong MỌI trường hợp (không khớp gì → `= 0`; người dùng loại dương tính giả xong → cập nhật lại) — mọi cổng đếm hộp cảnh báo (Bước 1 Bổ sung BRD + lớp 3) neo vào `n` này, KHÔNG neo vào `Số lần khớp` thô.

  **Phân loại mọi điều BRD nói** — BRD rút ngắn *số lượt hỏi*, không rút ngắn *phạm vi hỏi*:

  | Trạng thái BRD | Xử lý | Sau khi chốt |
  |---|---|---|
  | Rõ + không mâu thuẫn code/domain doc | fact (Bất biến #2) — vào bảng **`BRD đã chốt sẵn`** (nhánh · nội dung · cite), duyệt gộp một lượt ở recap GĐ1 → nhánh GĐ2/GĐ3 tương ứng `✅`, ghi chú `BRD <cite>` | — |
  | Mơ hồ / thiếu / lệch | quyết định — hỏi ở GĐ2–GĐ3, nội dung BRD làm option `(Recommended)` kèm cite | vào bước Bổ sung BRD như thường; **chỉ khi** nội dung đã chốt *nghịch* câu BA đang có → append `Xung đột BRD chờ BA` |
  | Im lặng | hỏi như thường — im lặng ≠ `N/A` | vào bước Bổ sung BRD như thường — im lặng thì không mâu thuẫn được, không phát sinh dòng sửa |

  CẤM lấy "BRD đã mô tả rồi" làm cớ bỏ mục sàn GĐ2/GĐ3, bỏ neo `K`, hay cắt dòng sổ — BRD là văn bản BA viết trước, không phải quyết định người dùng đã chốt, và thường bỏ trống đúng các mục sàn GĐ3 (hệ quả, vi phạm, vòng đời, job nền).
- **Domain doc** — **nguồn model chuẩn khi có, nhưng KHÔNG bắt buộc**. Tìm bằng **quét nội dung `docs/domain/`, KHÔNG suy theo tên file** (tên file là tên cụm do người đặt, không suy được từ module/chức năng):
  1. Không có thư mục `docs/domain/` hoặc rỗng → đi tiếp bình thường, không coi là thiếu sót. Có thể **gợi ý một lần** dựng domain doc trước cho đỡ vênh (`domain-design <RM-ID này + các RM liên quan chia sẻ entity>` nếu dự án cài extension — lệnh đó nhận danh sách RM, không nhận tên module), người dùng không muốn thì thôi, không nhắc lại.
  2. Có → liệt kê mọi `*.md`, đọc **header + §1 (bảng thực thể)** từng file. Chấm liên quan theo thứ tự tin cậy: (a) RM-ID đang specify nằm trong dòng `Phủ RM` hoặc cột `Dùng ở (RM)` — **khớp chắc**; (b) module của item roadmap nằm trong dòng `Phủ module` — khớp khá; (c) entity/chủ đề trùng phạm vi chức năng — khớp yếu, chỉ dùng khi (a) và (b) đều rỗng. Luôn nêu **bằng chứng** (dòng nào khớp).
  3. **Phải xác nhận với người dùng** trước khi dùng: trình file đã chọn + bằng chứng, cho phép **chỉ định lại file khác** hoặc **nói không dùng**. Nhiều file cùng khớp → liệt kê hết, cho chọn (có thể chọn nhiều). Không khớp hoặc không chắc → hỏi thẳng "có domain doc cho phần này không, ở đâu?"; người dùng nói không có → đi tiếp, **không hỏi lại** (Bất biến #5). Gộp câu này vào lượt hỏi chung của GĐ1 nếu còn câu khác.
  4. Đã xác nhận → dùng entity/FK/enum/rule trong doc, **KHÔNG tự rút lại model từ UI/code hiện có** gây vênh với các màn khác cùng cụm. Entity doc ghi "dùng lại framework" thì theo đó, không đẻ lại. Phỏng vấn lòi ra model thiếu/sai → nhắc cập nhật ngược **đúng file đó**.
  - **Không có người trả lời thật** (Bất biến #7): chỉ chấp nhận **đúng một** file **khớp chắc**, ghi rõ trong sổ là "chưa được người dùng xác nhận"; mơ hồ hoặc ≥2 ứng viên → bỏ qua domain doc và ghi vào sổ để hỏi ở phiên có người. KHÔNG dừng cả lệnh vì đây là nguồn không bắt buộc.
  - **CẤM**: đoán theo tên file; tự chọn khi có ≥2 ứng viên; coi việc không có domain doc là lỗi hay điều kiện chặn.
- **Codebase hiện tại liên quan đến chức năng**, và **nợ kỹ thuật liên quan** (TODO/FIXME/known issues).
- **Màn hình hiện có**: liệt kê từ router/menu các màn thuộc phạm vi `$ARGUMENTS`. Đây là **fact**, đếm được — dùng làm neo `K` cho GĐ2. Router rỗng / chức năng làm mới hoàn toàn → `K` chưa biết, sẽ **hỏi** ở đầu GĐ2, không tự bịa danh sách màn. Chức năng cũng có thể **không có màn nào** (API nội bộ, job nền, tích hợp) — đây là kết cục hợp lệ, sẽ chốt `K = 0` ở GĐ2, không nặn ra màn hình cho có.
- **Hiến chương** (`.specify/memory/constitution.md`) — đọc toàn bộ, **để dùng ở GĐ4 (đối chiếu)**, KHÔNG dùng làm khung câu hỏi cho GĐ2–GĐ3. Đếm số nguyên tắc → neo `N`. Không có file này → cảnh báo người dùng nên copy hiến chương vào `.specify/memory/` (preset chỉ swap template, không tự ghi file sống); người dùng vẫn muốn tiếp → **bỏ GĐ4**, GĐ2–GĐ3 chạy đủ như thường.
- **`CLAUDE.md`/`AGENTS.md` của dự án** (nếu có) — bối cảnh đặc thù: stack, có tầng mock/prototype cần nối backend hay không, quy ước riêng.

**Chốt ranh giới liên hệ chức năng (làm cuối GĐ1, trước khi phỏng vấn để định phạm vi).** UI/code hiện có (mock hay thật) hầu như không tự lộ liên hệ giữa các chức năng — đây là vùng `[cần bạn quyết]` thuần, phải hỏi thẳng bằng AskUserQuestion, neo vào roadmap. Ba câu đóng, đủ phủ mà không scope-creep (độc lập nhau → được gom một lượt theo Bất biến #1):

- **Upstream** — chức năng này đọc dữ liệu do chức năng/màn nào khác tạo?
- **Downstream** — chức năng/màn nào khác đọc/phụ thuộc dữ liệu chức năng này tạo?
- **Dùng chung** — trạng thái/quy tắc nào chia sẻ với chức năng khác, phải nhất quán?

Với mỗi liên hệ tìm thấy: đối chiếu item roadmap tương ứng; phần thuộc màn khác (làm sau) → ghi một bullet vào mục **`Nợ chờ ghi`** của sổ, KHÔNG đào ở spec này và KHÔNG sửa roadmap giữa chừng. Không có roadmap → hỏi trực tiếp người dùng, bỏ neo. **Kết quả ba câu này là nguồn neo bắt buộc cho nhánh "nhất quán liên chức năng" ở GĐ3.**

**Nợ phát sinh sang chức năng khác**: trong suốt khảo sát/phỏng vấn, phát hiện việc thuộc **chức năng/màn khác** (sẽ làm sau) → ghi bullet vào mục `Nợ chờ ghi` của sổ. Toàn bộ `Nợ chờ ghi` được append vào `Nợ phát sinh` của item tương ứng trong `docs/roadmap.md` **một lượt** ở "Sau khi ghi spec" — không sửa roadmap rải rác giữa phỏng vấn.

**Kết GĐ1 — xác nhận rồi mới mutation**: tóm tắt khảo sát kèm dấu nguồn `[từ khảo sát]`/`[suy luận]`/`[cần bạn quyết]` + kết quả ba câu ranh giới + **bảng `BRD đã chốt sẵn`** (nếu item có BRD) → **xin xác nhận tường minh**. Khi có xác nhận: (a) set `Trạng thái = đang` cho item roadmap (nếu định vị được), (b) tạo file sổ (Sổ theo dõi §7, gom cả `Nợ chờ ghi` phát hiện ở GĐ1), rồi vào GĐ2.

## Sổ theo dõi vét cạn (BẮT BUỘC — áp cho GĐ2, GĐ3, GĐ4)

Cơ chế ép phủ hết bằng phép đếm + hồ sơ bền ngoài hội thoại, không dựa vào trí nhớ model.

1. **Chốt số đếm từ nguồn NGOÀI, trước câu hỏi đầu tiên.** Đầu mỗi giai đoạn, in một dòng neo đếm được rồi mới in bảng. Số đếm phải lấy từ file/artifact thật hoặc từ câu trả lời của người dùng — **cấm ước lượng, cấm đếm từ danh sách do chính bạn nghĩ ra** (tự sinh rồi tự đối chiếu với chính nó thì gate vô nghĩa).
   - GĐ2: `phạm vi có K màn → bảng GĐ2 phải có K dòng gốc, MỖI dòng gốc kèm 5 dòng con ⏳ (một dòng cho mỗi mục sàn 1–5 của GĐ2) → tối thiểu 6K dòng` (K đếm từ router/menu, hoặc do người dùng chốt nếu chưa có màn; `K = 0` hợp lệ → bỏ GĐ2). Điều kiện `✅` (§3) xét trên TỪNG dòng con — một câu trả lời không thể ✅ cả màn.
   - GĐ3: `Bước A có P dòng; bổ sung Q dòng từ sàn → bảng cuối có P+Q dòng`. P là danh sách tự sinh (không artifact nào liệt kê nghiệp vụ nền) nên KHÔNG mạnh như neo K/N — bù bằng cột `Nguồn` bắt buộc từng dòng (xem GĐ3).
   - GĐ4: `Hiến chương có N nguyên tắc → bảng GĐ4 phải có đúng N dòng` (N đếm thật trong file).
   - **Neo phụ (cũng phải in số đối chiếu ở GATE, không được bỏ)**:
     - `M` = số mục mà **khuôn BRD** bỏ trống (GĐ1). Đối chiếu: bảng GĐ2 + GĐ3 cộng lại có ≥ `M` dòng mang `Nguồn = khuôn BRD`. Không nhận dạng được khuôn / không có BRD → `M = 0`, ghi rõ.
     - `T` = `S` — số section đánh số của file quy ước, đếm bằng `grep -cE '^## [0-9]+\. '` (xem GĐ1); bảng quét xung đột phải đủ `T` dòng. Không có file quy ước → `T = 0`, ghi rõ.
     - `S` = số section của **file quy ước chung** (sàn GĐ3 mục 10). Đối chiếu: bảng ở mục `Quy ước chung áp dụng` có đúng `S` dòng. Không có file → `S = 0`, ghi rõ.
     - `J` = số job nền đếm từ file cấu hình scheduler (sàn GĐ3 mục 8), nếu dự án có.
   - **In một BẢNG NEO duy nhất ở đầu mỗi giai đoạn** thay vì rải neo: `| Ký hiệu | Nguồn đếm | Giá trị | Đã có trong bảng |`. Bảy ký hiệu tối đa: `K · N · M · T · S · J · P/Q`. `T` và `S` CÙNG GIÁ TRỊ (cùng lệnh đếm trên file quy ước) nhưng kiểm HAI bảng khác nhau — `T`: bảng quét xung đột GĐ1, `S`: bảng mục 10 GĐ3; đừng nhầm `S` (neo đếm) với tiền tố bước `S-<n>`. Ký hiệu không áp dụng → ghi `0` kèm lý do, CẤM bỏ dòng.
2. **Bảng**: `| # | Nhánh | Tầng | Nguồn | Trạng thái | Ghi chú |` — **cột `Nguồn` bắt buộc cho CẢ GĐ2 và GĐ3** (neo `M` đếm theo cột này; GĐ2 thiếu cột thì không đếm được). Tầng ∈ `trọng yếu` · `thứ yếu` (theo Bất biến #3). Nguồn ∈ `khuôn BRD` · `BRD <cite>` · `domain doc` · `liên hệ GĐ1` · `nợ kỹ thuật` · `GĐ2` · `sàn` · `phán đoán BA`. Trạng thái ∈ `⏳ chờ` · `💡 đề xuất` (chỉ cho nhánh thứ yếu; Ghi chú chứa giá trị đề xuất + căn cứ) · `✅ đã chốt` · `N/A vì <lý do cụ thể gắn feature>`. (GĐ4 dùng bộ trạng thái riêng, xem GĐ4.)
3. **Điều kiện đánh `✅`**: (a) nhánh đã có ≥1 câu AskUserQuestion nhận được phản hồi; HOẶC (b) suy trực tiếp từ fact tra cứu (ghi rõ nguồn) — gồm dòng lấy từ BRD **đã** qua bảng `BRD đã chốt sẵn` ở GĐ1, Ghi chú phải mang cite `docs/brd/…md#<mục>`; HOẶC (c) dòng `💡` đã qua duyệt gộp ở recap cuối giai đoạn (§8); HOẶC (d) dòng khuôn BRD trùng một mục sàn — ghi `✅ (đã phủ tại sàn GĐ<x> mục <n>)`, **chỉ hợp lệ khi dòng sàn được trỏ tới đã `✅`**, và phải rà phần khuôn nêu mà dòng sàn chưa trả lời. Cấm tự đánh `✅` ngoài bốn đường này — đọc thấy trong BRD nhưng chưa qua bảng duyệt GĐ1 thì **chưa** được `✅`.
4. **`N/A` phải kiểm chứng được**: lý do cụ thể gắn với chính feature này (vd "N/A vì màn chỉ hiển thị tĩnh, không ghi dữ liệu"). CẤM `N/A` trống, chung chung, hoặc `N/A vì đã hỏi ở giai đoạn khác` để né hỏi.
5. **Sổ SỐNG — phát sinh phải append ngay**: một câu trả lời làm lộ ra nhánh mới thuộc **chính feature này** → thêm ngay một dòng `⏳` TRƯỚC khi đi tiếp. GATE luôn đọc **bảng hiện tại**, không đọc bản chụp đầu giai đoạn. Việc lộ ra thuộc màn/chức năng khác → ghi `Nợ chờ ghi` (theo luật GĐ1), KHÔNG thêm dòng vào sổ.
6. **In bảng tiết chế**: bảng ĐẦY ĐỦ chỉ in hai chỗ — đầu giai đoạn (ngay sau dòng neo) và tại GATE. Giữa chừng, giải xong hoặc phát sinh nhánh → chỉ in dòng vừa đổi + một dòng đếm `còn X ⏳ · Y 💡 chưa duyệt`. In lại cả bảng sau mỗi câu là nhiễu chôn nội dung hỏi-đáp, không phải kỷ luật.
7. **File sổ — hồ sơ bền ngoài hội thoại**: tạo `.specify/interviews/<slug>.md` (slug kebab-case không dấu sinh từ `$ARGUMENTS`) ngay sau xác nhận GĐ1. Cập nhật (ghi đè toàn bộ) **sau mỗi lượt AskUserQuestion có quyết định được chốt**, vào cuối mỗi giai đoạn, và ngay trước mỗi lần xin xác nhận — phiên dài chắc chắn bị tóm tắt context, file chỉ cập nhật cuối giai đoạn là hổng đúng đoạn dễ trôi nhất. Nội dung: neo đếm, bảng sổ đầy đủ, recap các quyết định đã chốt, ràng buộc `→ plan` (GĐ4), mục `Nợ chờ ghi`, mục `Xung đột BRD chờ BA`. Đây là **nguồn sự thật**: phiên dài bị tóm tắt context / bảng trôi mất → đọc lại file này, CẤM dựng lại bảng từ trí nhớ.
8. **Recap cuối giai đoạn — thứ người dùng duyệt là NỘI DUNG**: đạt GATE (§9) rồi mới in, theo thứ tự: (a) recap nội dung các quyết định đã chốt, gom theo màn/nhóm nhánh; (b) **bảng duyệt gộp** các dòng `💡` (nhánh + giá trị đề xuất + căn cứ) — người dùng chỉnh dòng nào thì chốt theo bản chỉnh, xác nhận đồng nghĩa duyệt các dòng còn lại; (c) bảng sổ cuối + dòng đối chiếu số đếm. Sau phản hồi của người dùng: chuyển các `💡` thành `✅` (theo giá trị đã chỉnh nếu có), cập nhật file sổ, rồi mới chuyển giai đoạn.
9. **GATE (không cảm tính) — đủ cả hai mới được in recap xin xác nhận**:
   (a) **đối chiếu số đếm — in TỪNG dòng, cấm viết "mọi neo đều đạt"**:
   ```
   Dòng bảng: <số dòng thực>/<neo dòng giai đoạn — GĐ2: ≥6K · GĐ3: ≥P+Q · GĐ4: =N> (vế trái đếm SỐ DÒNG của bảng, KHÔNG đếm số màn/số mục)
   K: <đếm>/<K>   ·   M (Nguồn=khuôn BRD): <đếm>/<M>   ·   T: <đếm>/<T>
   S (bảng mục `Quy ước chung áp dụng`): <đếm>/<S>   ·   J: <đếm>/<J>   ·   P+Q: <đếm>
   ```
   Neo nào `0` thì vẫn in `0/0` kèm lý do — bỏ dòng = vi phạm gate. GĐ4 in thêm dòng `N: <đếm>/<N>` (số nguyên tắc hiến chương — chỉ có giá trị ở GĐ4, giai đoạn khác ghi `—`). Thiếu dòng so với danh sách nguồn → bổ sung `⏳` rồi hỏi, cũng là vi phạm gate.
   (b) **không còn `⏳`**: mọi dòng phải `✅`, `💡` hoặc `N/A`.

## Giai đoạn 2 — Nghiệp vụ trên màn hình (thứ người dùng nhìn thấy)

Phỏng vấn hành vi nghiệp vụ của từng màn trong phạm vi. Ngôn ngữ nghiệp vụ, không ngôn ngữ kỹ thuật. Các câu độc lập của cùng một màn gom chung lượt AskUserQuestion (Bất biến #1).

**Chốt `K` trước.** Màn đã tồn tại → đếm từ router/menu (fact). Chưa màn nào tồn tại → hỏi người dùng "chức năng này gồm những màn nào" (quyết định trọng yếu), chốt danh sách rồi mới đếm; item có BRD thì lấy danh sách màn BRD mô tả làm **đề xuất kèm cite** cho câu hỏi đó, **KHÔNG** tự chốt `K` theo BRD — BRD mô tả nghiệp vụ, không phản ánh màn thật trong code. **Chức năng không có giao diện** (API nội bộ, job nền, tích hợp, migration nghiệp vụ): xác nhận với người dùng rồi chốt `K = 0` → ghi vào sổ + file sổ, **bỏ GĐ2**, toàn bộ nghiệp vụ dồn về GĐ3 — CẤM nặn ra màn hình cho có. `K ≥ 1` → in dòng neo `K`, in bảng: **mỗi màn một dòng gốc + 5 dòng con `⏳`, mỗi mục sàn (1)–(5) dưới đây một dòng con RIÊNG** — dòng gốc chỉ là tiêu đề nhóm của màn, KHÔNG gộp các mục sàn vào nó; GATE §9 đối chiếu theo neo `≥ 6K` đã chốt ở §1.

**Có BRD thì điền trước, đừng hỏi lại.** BRD use-case thường đã mô tả nút / trường / cột / luồng của màn: điền sẵn các dòng con theo BRD kèm cite, phân loại theo luật ở GĐ1, rồi chỉ hỏi phần BRD im lặng hoặc nói mơ hồ. Số dòng sổ giữ nguyên `≥ 6K` — điền trước là để **trả lời** dòng đó, không phải để xoá dòng đó.

Với mỗi màn, sàn tối thiểu phải chốt (thêm nhánh khi phát sinh, theo Sổ SỐNG):

1. **Mục đích & hành động** — màn này để làm gì; người dùng làm được những hành động nào; mỗi hành động dẫn tới kết quả nghiệp vụ gì.
2. **Dữ liệu hiển thị** — hiển thị thông tin gì, lấy từ đâu, sắp xếp/lọc mặc định thế nào.
3. **Ai thấy gì** — vai trò nào vào được màn này; hành động nào ẩn/khóa với vai trò nào.
4. **Trạng thái bất thường** — chưa có dữ liệu thì hiện gì; thao tác lỗi thì người dùng thấy gì; hành động phá hủy có cần xác nhận không.
5. **Điều kiện vào màn & kết quả để lại** — phải có sẵn gì thì mới vào/dùng được màn này (đã đăng nhập, đã chọn bản ghi cha, đã có dữ liệu nền, thiết bị đã kết nối); và sau một hành động thành công thì hệ thống ở trạng thái nào, người dùng được đưa đi đâu. Đây là **hai đầu của mọi ca kiểm** — dựng dữ liệu trước, kiểm gì sau — và là thứ khuôn BRD kiểu use-case hầu như luôn bỏ trống (bảng nhận dạng khuôn, GĐ1).

**Phân tầng trong sàn** (Bất biến #3): thường thì (1), (3) và (5) là trọng yếu — hỏi từng câu; chi tiết của (2)/(4) — sort/lọc mặc định, nội dung empty-state, wording lỗi — thường thứ yếu → `💡 đề xuất`, duyệt gộp cuối GĐ2. Nhưng xét theo từng feature, không máy móc: empty-state của một màn phê duyệt tài chính có thể là trọng yếu.

**Nếu dự án có tầng mock/prototype** (theo `CLAUDE.md`/khảo sát): thêm cho mỗi màn một dòng con — function/button/action/label/text nào đang chạy trên dữ liệu giả và cần nối backend thật. Đây là câu hỏi *wiring*, hỏi **sau** năm mục nghiệp vụ trên, không thay thế chúng.

Mỗi nhánh giải xong: cập nhật sổ theo §6. Theo GATE + recap (§8–§9): **KHÔNG sang GĐ3 khi bảng GĐ2 còn `⏳`, còn `💡` chưa duyệt, hoặc chưa có xác nhận tường minh của người dùng.**

**Định tuyến kết quả phỏng vấn vào spec.md — KỶ LUẬT MỘT NHÀ (chống trùng lặp).** Spec-template preset ship sẵn có ba nhà tách bạch; mỗi sự thật ghi đúng một nhà, nơi khác chỉ trỏ:
- **Hằng số của field** (độ dài, miền giá trị, giá trị hợp lệ, default) — từ khảo sát/domain doc/GĐ3 — ghi ở mục **`## Thực thể & Từ điển dữ liệu`** (đây chính là "Key Entities" mà core nhắc, đã nâng thành từ điển dữ liệu). Không rải hằng số sang màn.
- **Hành vi hệ thống & business rule** (điều gì xảy ra khi thao tác, tính duy nhất, ràng buộc liên trường, phân quyền, vòng đời/chuyển trạng thái, công thức) — chủ yếu từ **GĐ3** — ghi ở **`### Functional Requirements`** dưới dạng FR-### bằng lời, singular. Không mô tả lại luật trong màn.
- **Trình bày & ranh giới từng màn** — từ **GĐ2** — ghi ở **`## Đặc tả màn hình`**, mỗi màn một khối `### Màn: <tên>` theo khung cố định. Bảng *Hành động* trỏ số **FR** cho hành vi; bảng *Nhập liệu*/*Cột* nhắc **tên field** từ Từ điển dữ liệu; mục *Vai trò & quyền* trỏ FR phân quyền. **TUYỆT ĐỐI không chép lại hằng số hay luật ở màn — chỉ trỏ.** Nếu đang viết một con số giới hạn hay một luật ở màn → chuyển lên DD/FR rồi trỏ.

Chỉ điền mục con màn thực sự có (màn chỉ đọc → bỏ *Hành động* & *Nhập liệu*; không phải danh sách → bỏ *Cột* & *Lọc/Sắp/Tìm*), không nặn field cho có. **Acceptance Scenarios** là ví dụ trỏ FR, không chép hằng số/luật. Chỉ nêu **yêu cầu bằng lời**; **KHÔNG** ghi thư viện validation, mã message/resource string, quy ước data-testid, hay kiểu cột DB — để `/speckit.plan` và `/speckit.tasks` tự quyết theo stack. KHÔNG lặp quy ước UI/UX chung toàn chương trình (vi-VN, định dạng ngày/tiền, a11y, responsive, kênh báo lỗi, UI kit). `K = 0` (chức năng không giao diện) → xóa mục `## Đặc tả màn hình`, ghi đúng một dòng "Không có màn — nghiệp vụ mô tả ở Requirements".

## Giai đoạn 3 — Nghiệp vụ nền (thứ màn hình không kể ra)

Giao diện chỉ kể ra thứ **có pixel**. GĐ3 vét phần còn lại: những sự thật nghiệp vụ mà không màn hình nào nhắc bạn hỏi. Giữ ở mức WHAT/WHY — entity/DTO/transaction/migration để `/speckit.plan` lo. (Feature `K = 0`: GĐ3 là giai đoạn phỏng vấn chính, gánh toàn bộ nghiệp vụ.)

**Bước A — tự liệt kê, từng dòng có nguồn gốc.** Từ kết quả GĐ1 (BRD của item, khuôn BRD, domain doc, ranh giới liên hệ, nợ kỹ thuật, roadmap), GĐ2, cộng với phán đoán BA của bạn, liệt kê **mọi** nhánh nghiệp vụ nền mà chức năng này cần chốt — không giới hạn số nhánh. Mỗi dòng ghi cột `Nguồn`: `BRD <cite>` / `khuôn BRD` / `domain doc` / `liên hệ GĐ1` / `nợ kỹ thuật` / `GĐ2` / `phán đoán BA`. Vì `P` không có neo ngoài, nguồn gốc từng dòng là thứ thay thế neo — dòng `phán đoán BA` hợp lệ nhưng phải ghi rõ là phán đoán. **In bảng Bước A (P dòng) trước, rồi mới đối chiếu Bước B.**

**Bước B — lưới an toàn, đối chiếu sàn.** In **bảng đối chiếu đúng 13 dòng** (mỗi mục sàn 1–13 dưới đây một dòng): mỗi dòng hoặc trỏ `#` của dòng Bước A đã phủ mục đó, hoặc thêm dòng `⏳` mới vào sổ (Nguồn: `sàn`). Mục sàn không trỏ được dòng nào VÀ không thêm dòng mới = vi phạm gate; CẤM kết luận "Bước A đã phủ đủ" bằng một câu mà không có bảng 13 dòng này. Sàn là **mức tối thiểu để bắt thiếu, không phải trần**: mọi nhánh tự sinh ở Bước A giữ nguyên, không được cắt cho khớp sàn.

*Sàn — không artifact nào trong repo liệt kê ra chúng, nên buộc phải hỏi:*

1. **Dữ liệu nghiệp vụ** — thông tin nào hệ thống phải lưu/nhớ để chức năng chạy đúng.
2. **Quy tắc nghiệp vụ** — ràng buộc phải đúng bất kể ai thao tác (duy nhất, trạng thái hợp lệ, công thức tính).
3. **Quyền** — vai trò/đối tượng nào được làm gì (ở mức nghiệp vụ, không chỉ ẩn/hiện nút như GĐ2).
4. **Hệ quả nghiệp vụ** — một hành động xảy ra thì kéo theo gì: thông báo ai, cập nhật gì, đồng bộ đâu. (Nút thì nhìn thấy; hệ quả của nó thì không.)
5. **Xử lý khi vi phạm quy tắc** — nghiệp vụ xử lý thế nào khi ràng buộc bị phá, không chỉ happy path. (Đây là *vi phạm luật nghiệp vụ*; hỏng hạ tầng/thiết bị nằm ở mục 11 — hai thứ khác nhau, không gộp.)
6. **Vòng đời dữ liệu** — bản ghi sống bao lâu, khi nào hết hiệu lực / lưu trữ / xóa, ai được khôi phục.
7. **Nhất quán liên chức năng** — với các liên hệ đã chốt cuối GĐ1: trạng thái/quy tắc dùng chung phải khớp thế nào, ai là **chủ dữ liệu** (nguồn sự thật), thay đổi bên này ràng buộc gì bên kia. Chỉ `N/A` khi GĐ1 không tìm ra liên hệ nào.

*Sàn có neo ngoài — đếm từ artifact nếu dự án có; không có artifact thì vẫn phải hỏi:*

8. **Việc tự chạy nền** — hệ thống tự làm gì mà không do người dùng bấm: chạy theo lịch (báo cáo hằng ngày, đồng bộ đêm, nhắc hạn) hoặc chạy ngầm sau một hành động (xử lý hàng loạt). Dự án có file cấu hình scheduler/cron/job → **đếm từ đó**: `có J job liên quan → bảng phải có ≥ J dòng con`. Không tìm thấy file → vẫn hỏi thẳng "có việc chạy nền nào không"; CẤM `N/A vì không tìm thấy cấu hình`.
9. **Nguồn dữ liệu ngoài** — cần lấy/gửi dữ liệu hệ thống khác không. Có config tích hợp → đếm từ đó; không có → vẫn hỏi.

*Sàn bổ sung — hai mục dưới đây tồn tại vì chúng là thứ testcase cần mà KHÔNG artifact nào nói ra, kể cả BRD:*

10. **Quy ước chung áp dụng** *(→ mục `Quy ước chung áp dụng` của BRD — số hiệu H2 gán lúc chèn)* — feature áp § nào, ngoại lệ § nào + lý do:
    - Định vị file quy ước — hai gói PHẢI cùng một file: (1) `.specify/extensions/dft-speckit/references/quy-uoc-chung.md` nếu extension đã cài; (2) không có mới hỏi người dùng. **Ghi path đã dùng vào dòng đầu mục `Quy ước chung áp dụng` của BRD**.
    - Neo `S` = số section `## <n>.` của file đó. Bảng **đúng `S` dòng**, mỗi dòng `§<n>` + tên section nguyên văn. Thiếu dòng = vi phạm gate. File tồn tại mà `S = 0` → HALT, hỏi cách đánh số.
    - **Cột `Lý do nếu ngoại lệ` là CỔNG**: lý do nêu điều gì của chính feature khiến § không áp → lệnh QA sinh case theo ngoại lệ, đi tiếp; lý do trống/chung chung (`không áp dụng`, `theo thiết kế`) → QA đánh `blocked`.
    - Phân tầng: mặc định cả `S` dòng = `Áp`, ghi `💡`, duyệt gộp recap GĐ3. Chỉ hỏi trọng yếu cho § (a) có trong bảng xung đột GĐ1, (b) feature có lý do ngoại lệ cụ thể.
    - Mỗi nhóm xung đột GĐ1 đã chốt → một dòng: theo quy ước / ngoại lệ + lý do.
    - Không có file quy ước → `N/A vì dự án không có bộ quy ước chung`. CẤM `N/A` kiểu "theo chuẩn chung" không nói chuẩn nào.
11. **Hỏng hạ tầng & thiết bị** — khác mục 5 (mục 5 = luật nghiệp vụ bị phá; mục này = hệ thống bên dưới hỏng giữa chừng): mất mạng/timeout khi đang lưu · phiên hết hạn giữa thao tác · quyền bị thu hồi · bản ghi bị người khác sửa/xóa trước · thao tác dở dang khi tải lại trang. Feature có thiết bị/tích hợp ngoài → hỏi thêm đúng rủi ro đó (đứt kết nối giữa lúc truyền, dữ liệu trả về sai, hết thời gian chờ).
    - Câu thông báo lỗi mạng dùng chung → trỏ mục 10, KHÔNG hỏi lại; thứ phải hỏi là **nghiệp vụ xử lý ra sao** (giữ/bỏ dữ liệu đang nhập, cho thử lại không, trạng thái để lại).
12. **Chất lượng phi chức năng** *(→ mục `Chất lượng phi chức năng` của BRD — số hiệu H2 gán lúc chèn)* — ISO/IEC 25010 làm **lăng kính rà soát, KHÔNG phải 9 ô bắt buộc điền**:
    - Ba tầng chống lặp: NFR toàn hệ thống → hiến chương/tài liệu NFR dự án · mặc định theo loại thành phần → file quy ước chung · **ở đây CHỈ ghi chỗ feature khác mặc định**.
    - In bảng **đúng 9 dòng**, cột `Trigger bắn?` xét theo thành phần feature:

    | Trục 25010 | Trigger — feature CÓ thành phần này thì mới hỏi |
    |---|---|
    | Functional Suitability | *(phủ bởi FR — đánh `đã phủ`, không hỏi riêng)* |
    | Performance Efficiency | có danh sách/báo cáo · xuất dữ liệu · xử lý hàng loạt |
    | Compatibility | có tích hợp hệ thống khác · thiết bị · định dạng trao đổi |
    | Interaction Capability | có giao diện người dùng |
    | Reliability | có thao tác ghi nhiều bước · phụ thuộc kết nối có thể đứt |
    | Security | có xác thực · phân quyền · dữ liệu cá nhân |
    | Safety | có **tác động ra thế giới thực** (điều khiển thiết bị vật lý, giao dịch tiền, gửi dữ liệu ra ngoài) |
    | Maintainability | mặc định `Bỏ` — mối quan tâm của `/speckit.plan`; chỉ hỏi khi lòi ra ràng buộc kiến trúc |
    | Flexibility | có dự kiến mở rộng cấu hình/loại đối tượng |

    - Bắn → TRA giá trị mặc định cụ thể (hiến chương / file quy ước / tài liệu NFR dự án) rồi hỏi KÈM MỐC: *"Mặc định hệ thống: <giá trị + nguồn>. Feature này có cần khác không?"* — option `(Recommended)` = theo mặc định. KHÔNG tra được mặc định cụ thể → `Bỏ` + lý do NÊU CÁC FILE ĐÃ TRA (vd `đã tra hiến chương + quy-uoc-chung.md — không có mặc định về hiệu năng danh sách`), KHÔNG tốn lượt hỏi. CẤM hỏi chay trục 25010 không kèm mốc — người trả lời nghiệp vụ không thể trả lời, đáp án sẽ là dấu cao su.
    - Không bắn → `Bỏ` + lý do gắn feature. CẤM `Bỏ` trống/chung chung. Thiếu dòng nào trong 9 = vi phạm gate. Cuối bảng in `Bỏ vì không có mặc định: <n>/9` — `n` cao bất thường = chưa tra thật.
13. **Thang thuộc tính yêu cầu** *(chuẩn bị `Ưu tiên` + `Cách kiểm` cho bước "Gán thuộc tính cho từng FR" ở "Sau khi ghi spec"; giá trị `Cách kiểm` sau đó gắn vào dòng `QT-<nn>` của BRD — 29148 §5.2.8)* — GĐ3 chưa có mã `FR-###` (core sinh sau GĐ4) → **chỉ chốt THANG, không gán từng FR**:
    - Thang `Ưu tiên` (vd `Cao · Trung bình · Thấp`) + tiêu chí phân mức; tập `Cách kiểm`: `kiểm thử` · `thanh tra` · `phân tích` · `trình diễn`. Cả hai `💡`, duyệt gộp recap GĐ3.
    - Gán cho từng FR làm ở "Sau khi ghi spec". CẤM gán ở đây.

Theo GATE + recap (§8–§9): **KHÔNG sang GĐ4 khi bảng GĐ3 còn `⏳`, còn `💡` chưa duyệt, hoặc chưa có xác nhận tường minh của người dùng.**

## Giai đoạn 4 — Đối chiếu hiến chương (vòng KIỂM, không phải vòng HỎI)

Không có hiến chương → bỏ giai đoạn này, sang thẳng core.

Đây **không** phải phỏng vấn. Duyệt qua **từng** nguyên tắc trong `N`, mỗi nguyên tắc một dòng, và với mỗi nguyên tắc trả lời đúng một câu: *kết quả phỏng vấn GĐ2–GĐ3 có vi phạm hoặc bỏ trống thứ nguyên tắc này đòi hỏi không?* Không tốn lượt của người dùng, trừ khi phát hiện lỗ.

In dòng neo `N` rồi in bảng đúng `N` dòng. Mỗi dòng nhận đúng một disposition — **không dùng `N/A`**:

- `✅ đạt` — nêu rõ quyết định nào trong GĐ2–GĐ3 đã thỏa nguyên tắc. Cấm đánh `✅` mà không trỏ được vào một quyết định cụ thể.
- `⚠ lỗ → đã hỏi` — nguyên tắc đòi một **quyết định nghiệp vụ** mà phỏng vấn chưa chốt → quay lại hỏi bằng AskUserQuestion, chốt xong mới đổi trạng thái. Ví dụ: nguyên tắc đòi "mỗi domain object nêu bất biến của nó trong spec" mà GĐ3 chưa chốt bất biến của bản ghi → hỏi.
- `→ plan` — nguyên tắc là **ràng buộc kỹ thuật thuần**, không sinh câu hỏi nghiệp vụ (vd type safety, linter, kỷ luật kiểm thử, API versioning, structured logging). Ghi nguyên văn ràng buộc vào mục `Ràng buộc → plan` của file sổ; khi ghi spec, chúng được chép vào section riêng trong `spec.md` (xem "Sau khi ghi spec") — `/speckit.plan` đọc `spec.md`, đó là kênh bàn giao. **Đây là disposition hợp lệ, không phải né việc** — nhưng cấm dùng nó cho nguyên tắc có chứa quyết định nghiệp vụ.

Ranh giới giữa `→ plan` và `⚠ lỗ`: nguyên tắc nêu *cách cưỡng chế* (bất biến phải cưỡng chế ở domain + DB; endpoint phải phân quyền qua policy) mà spec chưa nêu *nội dung nghiệp vụ* tương ứng (bất biến đó là gì; ai được duyệt) → đó là **`⚠ lỗ`**, phải hỏi, KHÔNG được đẩy sang plan.

GATE GĐ4: bảng đủ `N` dòng, không dòng nào còn `⏳`, mọi dòng `⚠` đã chuyển thành đã-chốt; cập nhật file sổ (bảng GĐ4 + mục `Ràng buộc → plan`). Nếu GĐ4 không sinh ra câu hỏi nào → in bảng và đi tiếp, không cần xin xác nhận lại. Nếu có sinh câu hỏi → **xin xác nhận tường minh** trước khi chạy core.

Khi qua GĐ4, `[NEEDS CLARIFICATION]` phải ~0 (đã phỏng vấn hết cả phần trên màn lẫn phần nền, và đã đối chiếu hiến chương).

## VÔ HIỆU HÓA luật core mâu thuẫn (đọc trước khi chạy core)

Phần core bên dưới có luật riêng — **preset ghi đè các luật sau. Khi đọc core, gặp các mục này thì áp override, KHÔNG theo nguyên văn core dù core dùng chữ mạnh (MUST/EXECUTE):**

- **Clarification**: Core "Make informed guesses / tối đa 3 [NEEDS CLARIFICATION] / hỏi gộp dạng bảng markdown" → **BỎ.** Đã phỏng vấn cạn kiệt ở GĐ2–GĐ4, nên tới bước Specification Quality Validation của core: vẫn **QUÉT spec thật** tìm marker `[NEEDS CLARIFICATION]` — mỗi marker còn sót → hỏi bằng AskUserQuestion (KHÔNG áp trần 3 marker của core, KHÔNG informed-guess những quyết định thuộc về người dùng theo ranh giới ở Bất biến #2), đưa về **0 marker thật** rồi mới tick mục "No [NEEDS CLARIFICATION] markers remain" — CẤM tick khi chưa quét. KHÔNG bày lại bảng clarification của core; quyết định chưa chốt = quay lại hỏi, không tự đoán. Bỏ luôn phần core "For AI Generation / reasonable defaults (don't ask about these)": các mục đó (auth, retention, performance...) nếu là **quyết định** của người dùng thì vẫn phải hỏi hoặc đề-xuất-rồi-duyệt theo Bất biến #3, không tự mặc định ngầm.
- **Hook tạo branch — vá xung đột tường minh**: Khi tới mục **"Pre-Execution Checks"** của core bên dưới, với hook `before_specify` (git extension): **KHÔNG emit `EXECUTE_COMMAND`, KHÔNG invoke hook, KHÔNG tạo branch** — kể cả khi core ghi `optional: false`, "Automatic Pre-Hook" hay "MUST invoke". Coi như hook `before_specify` không tồn tại; giữ nguyên branch hiện tại của người dùng. Nếu môi trường bắt buộc chạy hook không bỏ được → dừng, báo người dùng tự tắt hook `before_specify` trong `.specify/extensions.yml`. Vẫn tạo `spec.md` + thư mục `specs/<...>/` + `feature.json` như thường (chúng do lệnh core tạo, không phải hook).
- **Completion Report / "Done When" của core**: KHÔNG được báo hoàn tất khi chưa làm xong mục **"Sau khi ghi spec"** của preset (nằm DƯỚI phần core bên dưới) — coi các việc trong đó là các dòng bổ sung bắt buộc của "Done When": mục `## Đặc tả màn hình` đã điền đủ (mỗi màn trong phạm vi có một khối `### Màn` khai đủ theo khung, hoặc ghi "Không có màn" nếu `K = 0`), section `Ràng buộc kỹ thuật kế thừa` đã có trong `spec.md`, `interview-notes.md` đã chuyển, **file scan đã chuyển thành `specs/<thư-mục-feature>/scan-xung-dot-quy-uoc.md` và mọi link trích dẫn qua `test -f`**, **bảng `Thuộc tính FR` đã duyệt và nằm trong `interview-notes.md`**, nợ roadmap đã ghi, và — nếu item có `Nguồn` trỏ `docs/brd/…` — **BRD đã qua mục "Bổ sung BRD": bản gốc đã sao lưu, cổng 3 lớp đã in NGUYÊN OUTPUT và khớp (lớp 1 `MẤT` = 0 · lớp 2 `LẶP` = 0 · lớp 3 đủ)**; mục `Xung đột BRD chờ BA` trong `interview-notes.md` (nếu có) đã báo người dùng.
- Mọi phần khác của core (tạo thư mục/feature.json, quality checklist, hooks khác) giữ nguyên.

{CORE_TEMPLATE}

## Sau khi ghi spec

- **Bàn giao cho plan (bắt buộc)**: thêm vào cuối `spec.md` section `## Ràng buộc kỹ thuật kế thừa (cho /speckit.plan)` liệt kê nguyên văn các ràng buộc `→ plan` thu được ở GĐ4 (không có ràng buộc nào thì ghi `Không có`). `/speckit.plan` đọc `spec.md` — ràng buộc chỉ nằm trong hội thoại thì phiên chạy plan sau sẽ không bao giờ thấy.
- **Hồ sơ phỏng vấn**: chuyển file sổ `.specify/interviews/<slug>.md` thành `specs/<thư-mục-feature>/interview-notes.md`, **và file quét xung đột `.specify/interviews/<slug>.scan.md` thành `specs/<thư-mục-feature>/scan-xung-dot-quy-uoc.md`** (audit trail nằm cạnh spec; xóa file gốc sau khi chuyển). Chuyển xong → **sửa mọi tham chiếu tới hai file này trong BRD và trong `interview-notes.md` sang đường dẫn mới**, rồi kiểm bằng lệnh — mỗi đường dẫn trích trong hai file phải `test -f` thành công; còn một link gãy = chưa xong.
- **Ghi nợ roadmap một lượt**: các bullet trong `Nợ chờ ghi` → append vào mục `Nợ phát sinh` của item roadmap tương ứng trong `docs/roadmap.md` (nếu dự án có roadmap); báo lại cho người dùng danh sách nợ đã ghi.
  - **CẤM dùng ngoặc vuông `[...]` trong dòng nợ** (vd `[2026-08-17, từ specify RM-002]`): `check_placeholders` của `brd_roadmap.py` coi mọi span `[...]` không phải link markdown là **placeholder chưa điền** → `verify` exit ≠ 0. Dùng ngoặc tròn: `(2026-08-17 · từ specify RM-XXX)`.
  - Sửa cả trường `**Phụ thuộc**` nếu phỏng vấn lòi ra phụ thuộc mà roadmap ghi `N/A` — nợ không chỉ là bullet.
  - Chạy lại `brd_roadmap.py verify` **sau khi** ghi nợ; exit ≠ 0 → sửa ngay, đừng để lại roadmap gãy.
- **Gán thuộc tính cho từng FR (làm TRƯỚC khi Bổ sung BRD)**: `spec.md` đã có mã `FR-###`, giờ mới gán được. Với **mỗi** FR, đề xuất `Ưu tiên` + `Cách kiểm` theo thang đã chốt ở sàn GĐ3 mục 13, kèm căn cứ ngắn (gợi ý đề xuất: hành vi quan sát được trên giao diện = `kiểm thử`; `thanh tra` khi phải soi dữ liệu/log; `phân tích` khi không chạy được trong phân hệ này — đây là ĐỀ XUẤT chờ duyệt, không phải giá trị tự điền); **trình một bảng duy nhất để duyệt gộp một lượt** — CẤM hỏi từng FR (20 FR là 40 lượt). Người dùng chỉnh dòng nào thì chốt theo bản chỉnh; **bảng đã duyệt ghi vào `interview-notes.md` mục `Thuộc tính FR`** — Bước 1 của Bổ sung BRD đọc từ đó, không đọc từ trí nhớ. Đây là **thẩm quyền thật** mà lệnh QA dựa vào để chọn tầng test; model tự điền là biến phỏng đoán thành thẩm quyền giả.
- **Bổ sung BRD**: chạy mục "Bổ sung BRD" bên dưới (nếu item có `Nguồn` trỏ `docs/brd/…`). Làm **sau** khi `spec.md` đã ghi xong — bước này chèn nội dung rút từ spec, spec chưa xong thì chèn bản dở.
- Mỗi kết luận trong spec giữ dấu nguồn `[từ khảo sát]`/`[suy luận]`/`[cần bạn quyết]` khi phù hợp.
- Quyết định wire UI/code hiện có → backend ghi vào requirements theo từng màn (nếu áp dụng).
- Nội dung spec lấy từ kết quả phỏng vấn GĐ2–GĐ4 (gồm cả các đề xuất thứ yếu đã được duyệt gộp), không suy đoán mới.

## Bổ sung BRD (chạy sau khi đã ghi xong `spec.md`)

**Mục tiêu**: BRD tự đủ sinh testcase, KHÔNG cần mở `spec.md` — mà vẫn là tài liệu của BA, đọc được cho BA/Tester/Dev.
**Chuẩn ghép**: Cockburn *fully dressed* / RUP Use-Case Spec · ISO/IEC/IEEE 29148:2018 §5.2.8 · ISO/IEC 25010 · Gherkin.
**Quyền hạn — CHỈ CHÈN**: CẤM dời mục, CẤM viết lại/tóm tắt câu BA, CẤM gom nội dung BA xuống phụ lục.
Chép một nội dung BA sang chỗ thứ hai = **lặp**. Cổng lớp 2 chỉ bắt bản sao NGUYÊN VĂN — **diễn đạt lại nội dung BA ở mục mới cũng là lặp và bị CẤM dù cổng không đo được**: mục mới chỉ được TRỎ neo (`xem QT-05`), không phát biểu lại. Ngoại lệ duy nhất: khối `Đặc tả màn hình` chép nguyên văn từ `spec.md` vì nó mang trạng thái/lọc/quyền mà mục thiết kế của BA bỏ trống — nhưng nút/cột đã có trong mục điều khiển của BA thì CHỈ TRỎ, không mô tả lại.
Sửa một dòng BA có sẵn = phải khai `Danh sách sửa` (Bước 0 việc 9).
**BỎ QUA** (ghi lý do vào `interview-notes.md`) khi thiếu một trong: (a) item có `Nguồn` trỏ `docs/brd/…`; (b) có người trả lời thật (Bất biến #7).
**Chạy lại RIÊNG mục này được** (không phỏng vấn lại) khi `spec.md` đổi sau lần bổ sung trước — vào thẳng Bước 0; việc 5 xử lý file đã bổ sung.
`Nguồn` trỏ **thư mục** có nhiều file → hỏi người dùng file nào là BRD của item trước khi vào Bước 0, CẤM tự chọn.

> Vì sao CHỈ CHÈN: mọi thiết kế vừa-sắp-xếp-lại vừa-giữ-nguyên-văn đều sinh HAI bản của cùng nội dung
> (đo thật trên bản tái-cấu-trúc đời cũ: phụ lục 69% file, 21% câu phía trên là bản sao). Chèn-thêm đưa lặp-nguyên-văn về 0 theo cấu trúc; lặp-diễn-đạt-lại tự giữ bằng luật một-nhà (#4).

### Bước 0 — Lưới an toàn (đúng thứ tự — đảo là mất dữ liệu)

1. [ ] `Nguồn` mang `#<anchor>` trỏ vào FILE → **HALT**, báo người dùng bỏ anchor (giữ path) rồi chạy lại — đánh số heading làm anchor chết, `verify` exit ≠ 0. Anchor trỏ thư mục = vô hại, đi tiếp.
2. [ ] `git status --porcelain <file BRD>` phải SẠCH — file đang có thay đổi chưa commit (của người khác/lượt trước) → HALT, báo người dùng commit/stash trước; không sạch thì `git diff` ở "Sau khi ghi" trộn hai nguồn, hết giá trị kiểm.
3. [ ] Sao lưu bản GỐC: `mkdir -p` rồi copy → `.specify/brd-backup/<đường-dẫn>.$(date +%F-%H%M%S).goc.md` — bắt buộc giờ-phút-giây (chạy lại cùng ngày mà thiếu thì lần 2 đè bản gốc BA). Không sao lưu được → **HALT, chưa chạm file**.
4. [ ] Di trú: file có `<!-- SPEC:BEGIN` hoặc mục `## 11. Thiết kế tham chiếu` (dấu vết bản tái-cấu-trúc đời cũ) → **HALT**, báo người dùng `git checkout <commit trước khi tái cấu trúc> -- <file>` rồi chạy lại. CẤM tự gỡ — bản đời cũ đã trộn lời BA với lời máy, không tách được bằng lệnh.
5. [ ] File đã có mục `## Nhật ký cập nhật` (đã bổ sung ở item/lượt trước — KHÔNG phải dấu vết đời cũ ở việc 4) → **CHẾ ĐỘ CẬP NHẬT**:
   - Hai nhánh dưới áp **ĐỒNG THỜI** khi nhật ký có nhiều entry: dựng lại phần của entry trùng spec, giữ nguyên phần của entry khác. Khối không mang nhãn RM thuộc về entry **CŨ NHẤT** (lượt đầu chưa gắn nhãn).
   - Entry nhật ký có `Nguồn spec` TRÙNG spec hiện tại (chạy lại cùng RM) → mục/khối do công cụ chèn lượt trước thuộc entry đó được **DỰNG LẠI** từ `spec.md` hiện tại — thay nguyên khối, CẤM chèn bản thứ hai.
   - Entry khác RM (BRD dùng chung) → không tạo lại mục đã có, chỉ chèn nội dung mới vào mục sẵn có; MỌI đơn vị mới đều mang nhãn RM: hàng bảng (`TR-`, quy ước, NFR) gắn cột `RM` (thêm cột nếu chưa có); khối/dòng phi-bảng gắn hậu tố `*(RM-<nnn>)*` — `### Màn: <tên> *(RM-002)*`, `**SC-007** *(RM-002)*`, mỗi kịch bản Given/When/Then, mỗi dòng `Tình huống biên`; SC trùng số giữa hai RM → giữ nguyên số, phân biệt bằng nhãn. CẤM xoá/sửa hàng/khối mang RM khác.
6. [ ] Sao lưu bản BA → `….ba.md` (**`.ba.md` là đơn vị so của toàn bộ Bước 2**, `.goc.md` chỉ để khôi phục; lượt đầu hai file cùng nội dung). **Ở chế độ cập nhật, `.ba.md` = phần BA + phần của entry KHÁC**: trước khi chụp số đo, loại khỏi nó CHỈ các mục/khối thuộc **entry có `Nguồn spec` trùng spec hiện tại** (những thứ sắp được dựng lại — tên đọc từ `Mục mới chèn` của entry đó + khối chèn trong mục gốc); mục/khối của entry KHÁC **giữ nguyên trong `.ba.md`** để lớp 1 vẫn canh chúng — xoá phần của RM khác sẽ bắn `MẤT` như xoá lời BA.
7. [ ] Đơn vị so = **thân câu sau khi bóc bullet + tiền tố đánh số** (`^\s*(S-)?\d+[a-z]?[.:)]\s*`). Gắn thêm tiền tố ID (`**QT-05** · `) hay đánh số heading ≠ sửa, KHÔNG khai; đổi bất kỳ chữ nào trong thân câu = sửa, PHẢI khai.
8. [ ] Chụp số đo trên `.ba.md` bằng ĐÚNG các lệnh sau — đã kiểm chứng 0 dương tính giả trên BRD pandoc thật, CẤM chế biến thể:

   ```bash
   BA=<đường-dẫn .ba.md>;  OUT=.specify/interviews/<slug>
   # Sent — thân câu; grep -v '^#' loại heading (heading = cấu trúc, được phép đánh số)
   sed 's/<[^>]*>//g' "$BA" | grep -v '^[[:space:]]*#' | tr '.;' '\n\n' \
     | sed -E 's/^[[:space:]]*[-*+][[:space:]]+//; s/^[[:space:]]*(S-)?[0-9]+[a-z]?[.:)][[:space:]]*//; s/^[[:space:]]+//; s/[[:space:]]+$//; s/[[:space:]]+/ /g' \
     | grep -vE '^$|^[-|:[:space:]]*$' | sort -u > "$OUT.sent.txt"
   # Long — câu ≥60 byte (awk đếm byte, ~40 ký tự tiếng Việt — lệch về phía chặt hơn), ĐƠN VỊ CỦA CỔNG LẶP (ngắn hơn là mảnh từ vựng chung, đếm sẽ dương tính giả)
   awk 'length($0)>=60' "$OUT.sent.txt" > "$OUT.long.txt"
   # Str — chuỗi trong nháy (cả nháy cong); bỏ frontmatter/thẻ/CSS/đường dẫn ảnh
   awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$BA" | sed 's/<[^>]*>//g' | grep -o '["“][^"”]*["”]' \
     | grep -vE '\.(png|jpe?g|webp)"|width:|height:|^"\.\.' | sort -u > "$OUT.str.txt"
   # Img
   grep -o 'src="[^"]*"' "$BA" | sort -u > "$OUT.img.txt"
   # Ctrl — MỖI đoạn của MỖI ô bảng = một chuỗi tìm độc lập. Chạy CẢ HAI khuôn bảng:
   #   HTML <table> (pandoc) và markdown pipe. Chỉ làm một khuôn = cột này trích 0 ô ở
   #   khuôn kia mà vẫn in "0/0" như đã kiểm — cổng rỗng, đúng thứ lưới an toàn phải chặn.
   # Cắt tiếp theo </p>: một ô thường gói nhiều đoạn. CẤM chuẩn hoá dấu `|` khi trích.
   { tr '\n' ' ' < "$BA" | sed 's|</t[dh]>|\n|g' | grep '<t[dh][^>]*>' | sed 's/.*<t[dh][^>]*>//' \
       | sed 's|</p>|\n|g' | sed 's/<[^>]*>//g'
     sed -n '/^| \*\*/p' "$BA" | sed 's/^|[[:space:]]*//; s/[[:space:]]*|[[:space:]]*$//' \
       | awk -F'[[:space:]]*\\|[[:space:]]*' '{gsub(/\*\*/,"",$1); print $1; if($2!="") print $2}'
   } | sed 's/[[:space:]]\+/ /g; s/^ //; s/ $//' \
     | grep -vE '^$|^Tên điều khiển$|^Mô tả điều khiển$' | sort -u > "$OUT.ctrl.txt"
   # Cổng chống-cột-rỗng: có bảng mà trích 0 ô ⇒ lệnh trích hỏng, KHÔNG phải "không có bảng".
   grep -qE '<table|^\| ' "$BA" && [ ! -s "$OUT.ctrl.txt" ] && echo "HALT: BA có bảng nhưng ctrl trích 0 ô"
   # Bản phẳng của BA — mẫu số của cổng lặp
   sed 's/<[^>]*>//g' "$BA" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' > "$OUT.ba-flat.txt"
   ```
9. [ ] `Danh sách sửa`: mỗi dòng đủ `đang có` → `sẽ thành` + lý do **trỏ về một phân xử đã chốt** (đúng `§` bảng xung đột GĐ1 / đúng câu hỏi GĐ2–GĐ3); không trỏ được → không được vào danh sách. **Trình bằng AskUserQuestion, có xác nhận tường minh rồi mới đi tiếp** (Bất biến #6). **Chốt tại đây và ĐÓNG BĂNG**: sau khi lớp 1 đã chạy, CẤM thêm dòng để hợp lệ hoá `MẤT` vừa lộ — `MẤT` không có sẵn trong danh sách = khôi phục, muốn sửa thật thì khôi phục xong quay lại việc này với xác nhận mới. Khung chèn-thêm thường có `Danh sách sửa` **rỗng** — rỗng là bình thường, không phải dấu hiệu bỏ sót.
10. [ ] Thiếu bất kỳ việc nào trên → CẤM vào Bước 1.

### Bước 1 — Chèn mục mới + gắn ID

**Giữ nguyên mọi mục H2 của BA, đúng thứ tự, đúng câu chữ.** Chỉ đánh số heading (`## Mô tả điều khiển` → `## 7. Mô tả điều khiển`) và chèn thêm.
Khuôn BRD mỗi dự án một khác (đo ở GĐ1) — CẤM áp cứng danh sách tên mục. Neo theo **vai trò nội dung**:

| Bổ sung | Chèn ở đâu | Không tìm thấy mục neo thì |
|---|---|---|
| Tiền điều kiện · Hậu điều kiện thành công · Bảo đảm tối thiểu | cuối mục **điều kiện** của BA | tạo mục `Điều kiện` ngay sau mục đầu tiên |
| `### Luồng ngoại lệ` (`S-3a`, `S-6b`… neo vào bước có sẵn) | mục con cuối của mục **kịch bản/luồng** | tạo mục `Luồng sự kiện` sau mục usecase |
| `Từ điển dữ liệu` | H2 mới ngay **sau** mục **mô tả điều khiển** | cuối cụm mục thiết kế |
| `QT-<nn>` + ` · *Cách kiểm: <tầng>*` | gắn vào **từng gạch đầu dòng sẵn có** của mục **quy tắc/yêu cầu nghiệp vụ**; luật còn thiếu ghi dưới `#### Bổ sung từ phỏng vấn`. Giá trị `Cách kiểm` lấy từ **bảng `Thuộc tính FR` đã duyệt trong `interview-notes.md`**, CẤM tự điền; `QT` không ánh xạ được về FR nào trong bảng → ghi `Cách kiểm: chưa chốt` + một dòng vào mục `QT chưa gán Cách kiểm` của `interview-notes.md` (mục riêng — KHÔNG dồn vào `Xung đột BRD chờ BA`, đó là chỗ chờ BA duyệt nội dung), CẤM đoán tầng | tạo mục `Quy tắc nghiệp vụ` sau `Từ điển dữ liệu` |
| `Đặc tả màn hình` · `Quy ước chung áp dụng` · `Chất lượng phi chức năng` · `Tiêu chí chấp nhận` · `Giả định · Phụ thuộc · Ngoài phạm vi` · `Nhật ký cập nhật` | H2 mới, nối **sau** mục quy tắc, đúng thứ tự này | — |

**Nội dung từng mục mới** (lấy từ sàn phỏng vấn, CẤM bịa):

| Mục mới | Nguồn | Bắt buộc có |
|---|---|---|
| Từ điển dữ liệu | sàn GĐ3 + `## Thực thể & Từ điển dữ liệu` của `spec.md` | bảng `TR-<nn> · Trường · Kiểu · Bắt buộc · Độ dài/Miền · Tập giá trị · Duy nhất theo phạm vi · Mặc định · Thông báo lỗi` |
| Quy ước chung áp dụng | sàn GĐ3 mục 10 | dòng đầu = path file quy ước; bảng đúng `S` dòng `§ · Tên mục · Áp/Ngoại lệ · Lý do` |
| Chất lượng phi chức năng | sàn GĐ3 mục 12 | bảng 9 trục 25010; trục theo mặc định ghi `Theo mặc định — <nguồn>`, CẤM bỏ dòng |
| Đặc tả màn hình | `## Đặc tả màn hình` của `spec.md` | chép nguyên khối, mỗi màn một `### Màn` — nguồn của họ case trạng thái UI khi QA đọc BRD; mỗi khối PHẢI giữ đủ dòng trạng thái + quyền của spec (khối rỗng/chỉ-một-dòng-trỏ = vi phạm lớp 3); phần nút/cột đã có ở mục điều khiển của BA → chỉ trỏ, không mô tả lại; `FR-###` trong khối đổi theo luật (1) hàng dưới; `K = 0` → một dòng `Không có màn` |
| Tiêu chí chấp nhận | `spec.md` | `Given/When/Then` + mục con `### Tình huống biên` (chép NGUYÊN VĂN từng dòng `### Edge Cases` của spec) + tiêu chí đo được `SC-` — **mã `SC-` chép NGUYÊN VĂN từ `spec.md` (template dùng `SC-001` ba chữ số), CẤM đánh số lại** (cổng tươi-mới của lệnh QA so TẬP chuỗi nguyên văn hai bên). **Hai luật khi chép**: (1) thay mọi `FR-###` trong văn spec bằng neo `QT/TR/S-` tương ứng — BRD không có bảng FR, giữ FR là con trỏ gãy; (2) xem luật hộp cảnh báo ở hàng dưới |
| **Hộp cảnh báo nhãn lệch** | bảng xung đột GĐ1 | Chèn hộp `> ⚠️` **ngay đầu mục mô tả điều khiển** (tại chỗ nhãn sai nằm — đặt ở mục khác là tester đọc bảng điều khiển không thấy, đã gặp báo lỗi ngược). Số hàng = dòng tổng **`Điểm lệch còn lại sau phân xử`** của bảng scan GĐ1 (đã loại dương tính giả). MỖI điểm lệch một hàng `nhãn BA → nhãn quy ước` + bên thắng + nơi phân xử — **CẤM nén phần dư thành văn xuôi** (câu gộp không nói nhãn đúng là gì = vô dụng cho kiểm thử; đã gặp: 9 hàng / 31 điểm lệch). Điểm lệch không phải nhãn (thiếu control · thiếu tiêu đề dialog · sai định dạng tệp xuất) vẫn một hàng riêng, cột đích ghi thứ phải có |
| Giả định · Phụ thuộc · Ngoài phạm vi | `## Assumptions` của `spec.md` + sổ phỏng vấn | Giả định = chép nguyên văn `## Assumptions`; Phụ thuộc = ranh giới liên hệ GĐ1 + trường `Phụ thuộc` của item roadmap; Ngoài phạm vi = phạm vi item roadmap + `Nợ chờ ghi`. Khối không chốt được ở phỏng vấn → ghi `Chưa chốt ở phỏng vấn <ngày>`, CẤM bịa. `Ngoài phạm vi` là rào chắn chống lượt QA sau tự bịa case ngoài đợt — CẤM bỏ mục |
| Nhật ký cập nhật | Bước 3 | **luôn là mục cuối cùng** |

**Bốn luật gắn ID** (vi phạm là cổng lớp 2 bắt):
1. Gắn ID = **thêm tiền tố/hậu tố vào dòng có sẵn**, thân câu không đổi một chữ. CẤM viết lại câu BA cho "gọn hơn".
2. **KHÔNG tạo mục `Yêu cầu chức năng (FR)`.** Neo truy vết là `S-<n><a>` (bước/ngoại lệ) · `QT-<nn>` (quy tắc) · `TR-<nn>` (trường). Một mục FR chỉ diễn đạt lại ba thứ đó bằng chữ khác = nguồn lặp lớn nhất.
3. **Ma trận truy vết `FR ↔ neo BRD` ghi vào `interview-notes.md`, KHÔNG vào BRD.** BRD là tài liệu đọc, không phải bảng đối soát. Neo phải **mang đúng nội dung** của FR, không chỉ tồn tại: FR về thuật ngữ → QT thuật ngữ (không phải QT phân quyền); FR về vòng đời trạng thái → QT vòng đời. FR không có QT/TR/S nào chứa nội dung nó → **thêm QT vào `Bổ sung từ phỏng vấn`**, CẤM gán bừa vào neo gần nghĩa.
4. **Một luật một nhà — áp cho cả phần chèn.** Cổng LẶP chỉ canh câu BA, không canh phần công cụ viết, nên tự giữ: ca của `Luồng ngoại lệ` đã có trong `Tình huống biên` → dòng ngoại lệ chỉ giữ ID + một dòng tham chiếu (`**S-6b** — xem Tình huống biên, mục Tiêu chí chấp nhận`), nội dung đầy đủ ở MỘT nơi; luật chuẩn hoá/bất biến của trường chỉ ở bảng Từ điển — dòng `S-` trỏ `TR-<nn>`, không phát biểu lại. `Luồng ngoại lệ` viết đầy đủ CHỈ cho ca không có nhà khác (hỏng hạ tầng, phiên, giới hạn tệp).

- Mục mới không có nội dung → một dòng lý do gắn feature (vd `Không có giao diện ngoài — không gọi hệ thống nào khác`). CẤM bỏ trắng, CẤM xoá mục.
- **Ghi `$OUT.allow-dup.txt` NGAY TẠI ĐÂY** (không phải lúc chạy cổng): mỗi câu chép-nguyên-văn-từ-spec mà trùng câu BA → một dòng. File này ĐÓNG BĂNG khi vào Bước 2 — cổng sẽ kiểm từng dòng có thật trong `spec.md`.
- Frontmatter (`brd_id` · `title` · `breadcrumb`) + H1: **giữ nguyên vẹn** — `verify` khớp anchor theo heading, manifest khoá theo `title`.
- Tự kiểm cuối Bước 1: `grep -c '^## [0-9]\+\. ' <file BRD>` = (số H2 gốc của BA) + (số mục mới đã chèn). In cả hai số.

### Bước 2 — Cổng 3 lớp (không qua → KHÔI PHỤC từ `.goc.md`)

```bash
NEW=<file BRD mới>;  OUT=.specify/interviews/<slug>
sed 's/<[^>]*>//g' "$NEW" > "$OUT.new-stripped.md"
tr '\n' ' ' < "$OUT.new-stripped.md" | sed 's/[[:space:]]\+/ /g' > "$OUT.new-flat.txt"

# LỚP 1 — không rơi nội dung BA
for f in sent str img ctrl; do
  while IFS= read -r c; do
    grep -qF -- "$c" "$OUT.new-stripped.md" || grep -qF -- "$c" "$OUT.new-flat.txt" \
      || grep -qF -- "$c" "$NEW" || echo "MẤT[$f]: $c"
  done < "$OUT.$f.txt"
done

# LỚP 2 — không chép nội dung BA sang chỗ thứ hai (câu ≥60 byte + ô bảng/điều khiển ≥40 byte)
dup() { while IFS= read -r c; do
  n1=$(grep -oF -- "$c" "$OUT.ba-flat.txt" | wc -l | tr -d ' ')
  n2=$(grep -oF -- "$c" "$OUT.new-flat.txt" | wc -l | tr -d ' ')
  [ "$n2" -gt "$n1" ] && echo "$1 ($n1→$n2): $c"
done; }
dup "LẶP"      < "$OUT.long.txt"
awk 'length($0)>=40' "$OUT.ctrl.txt" | dup "LẶP-CTRL"
```

- `grep -qF --` bắt buộc có `--` — câu bắt đầu bằng `-` sẽ bị đọc thành option, báo mất giả hàng loạt.
- **In nguyên output cả hai lớp, CẤM tóm tắt.** Điều kiện qua: **0 dòng `MẤT[...]`** ngoài `Danh sách sửa` **VÀ 0 dòng `LẶP`/`LẶP-CTRL`** (trừ ngoại lệ allow-dup dưới đây).
- **Ngoại lệ allow-dup**: câu thuộc khối chép-nguyên-văn-từ-spec (Given/When/Then · `### Tình huống biên` · `Đặc tả màn hình` · `## Assumptions`) trùng câu BA → được phép `n2 = n1 + 1`. `$OUT.allow-dup.txt` đã ghi và ĐÓNG BĂNG từ Bước 1 — CẤM thêm dòng sau khi thấy output `LẶP`; dòng `LẶP` có câu nằm trong file này và `n2 ≤ n1+1` → bỏ qua; vượt → vẫn là LẶP. Kiểm file không bịa (phải 0 dòng):

  ```bash
  while IFS= read -r c; do grep -qF -- "$c" <spec.md> || echo "ALLOW-DUP GIẢ: $c"; done < "$OUT.allow-dup.txt"
  ```
- `MẤT` không khớp `Danh sách sửa` → khôi phục từ `.goc.md` **đúng timestamp của lượt này** (ghi ở việc 3 — file mới nhất có thể là bản đã hỏng của lượt sau). `LẶP` → xoá bản sao ở mục MỚI (không bao giờ xoá ở mục gốc của BA), chạy lại cổng. CẤM "ghi tạm sửa sau".
- Lớp 2 đã kiểm chứng: bản gốc so chính nó = 0 · bản gốc + mục mới hợp lệ = 0 · bản tái-cấu-trúc-đời-cũ = 41 LẶP.

**LỚP 3 — đủ nội dung sinh testcase. Đếm bằng lệnh, in output, CẤM tự nhẩm:**

| Thứ | Trong `spec.md` | Trong BRD | Phép so |
|---|---|---|---|
| số field Từ điển dữ liệu | | | **=** |
| số kịch bản Given/When/Then | | | **=** |
| số dòng Edge Case → `Tình huống biên` (nguyên văn) | | | **=** |
| số `SC-###` | | | **=** |
| số khối `### Màn` ở `Đặc tả màn hình` (khối thiếu dòng trạng thái hoặc dòng quyền → KHÔNG tính) | | | **=** |
| số dòng bảng Quy ước | *(`S` — sàn GĐ3 mục 10)* | | **= `S`** |
| số trục NFR đã xét | *(9 — sàn GĐ3 mục 12)* | | **= 9** |
| `QT-###` có `Cách kiểm` | — | | **100%** (`chưa chốt` hợp lệ nếu có dòng tương ứng trong `QT chưa gán Cách kiểm`) |
| `QT chưa chốt` | *(trần = số QT không được FR nào trỏ tới trong ma trận `FR ↔ neo BRD`)* | | **≤ trần** — vượt = né bảng `Thuộc tính FR`, in `<n>/<tổng QT>` |
| `FR-###` của spec có neo BRD trong `interview-notes.md` | | | **100%** |
| số hàng trong hộp cảnh báo nhãn lệch | *(dòng `Điểm lệch còn lại sau phân xử` của bảng scan GĐ1)* | | **=** |

- Edge Case của spec nằm nguyên văn ở `Tình huống biên`; `Luồng ngoại lệ` KHÔNG chép lại (luật gắn ID #4) — chỉ kiểm mọi Edge Case tìm được trong BRD, bằng lệnh — **bóc markdown ở CẢ HAI vế**:

  ```bash
  sed 's/\*//g' <file BRD> > /tmp/brd-plain.md
  awk '/^### Edge Cases/,/^## Requirements/' <spec.md> | grep '^- ' | sed 's/^- //; s/\*//g' \
    | while IFS= read -r e; do
        grep -qF -- "$(echo "$e" | cut -c1-45)" /tmp/brd-plain.md || echo "THIẾU: $e"
      done
  ```
- Dòng `QT-### có Cách kiểm` và neo `S` (số mục file quy ước) phải đếm bằng ĐÚNG lệnh sau — đếm theo dòng là sai, cả hai đối tượng đều **trải nhiều dòng**:

  ```bash
  # QT có `Cách kiểm` — gộp file thành một dòng rồi cắt theo mốc `- **QT-`
  tr '\n' ' ' < <file BRD> | sed 's/- \*\*QT-/\n- **QT-/g' | grep '^- \*\*QT-' \
    | awk '{match($0,/QT-[0-9]+/); id=substr($0,RSTART,RLENGTH); if(index($0,"Cách kiểm")==0) print "THIẾU Cách kiểm: " id}'
  # S = số mục ĐÁNH SỐ của bộ quy ước; `## Mục lục` KHÔNG phải một mục quy ước
  grep -cE '^## [0-9]+\. ' <file quy ước chung>
  ```
- Mọi dòng khác = bằng tuyệt đối. CẤM suy rộng `≥`.
- CHẾ ĐỘ CẬP NHẬT (Bước 0 việc 5): hàng/khối/dòng mang nhãn RM KHÁC → LOẠI khỏi mọi phép đếm lớp 3, CẤM xoá — lệch do đếm lẫn RM khác là lỗi đếm, không phải lỗi tài liệu; khối của lượt trước CÙNG RM đã được DỰNG LẠI ở Bước 1, đếm như bình thường.
- Lệch → **kiểm lệnh đếm trước khi sửa tài liệu**: hai lỗi đếm đã gặp thật là (a) đếm QT theo dòng trong khi luật của BA dài nhiều dòng, (b) lấy `S` bằng số `^## ` thay vì số mục đánh số. Xác nhận lệnh đúng rồi mới kết luận tài liệu lệch. Đối chiếu cả **danh sách ID**, không chỉ số lượng.

### Bước 3 — Nhật ký

Append vào mục `Nhật ký cập nhật`, mới nhất trên cùng. Ngày = output `date +%F`, CẤM bịa:

```
### <YYYY-MM-DD> — <RM-ID> (/speckit.specify)
- **Loại**: bổ sung theo chuẩn (Cockburn/RUP + 29148 + 25010 + Gherkin) — chèn-thêm, không tái cấu trúc
- **Bản sao lưu**: .specify/brd-backup/<đường-dẫn>.<YYYY-MM-DD-HHMMSS>.goc.md + ….ba.md
- **Mục BA giữ nguyên**: <n>
- **Mục mới chèn**: <n> — <liệt kê tên, phân tách bằng ` · `>
- **Nguồn spec**: specs/<thư-mục-feature>/spec.md
- **spec.md sha1**: <output `shasum <spec.md> | cut -d" " -f1`> — cổng tươi-mới của lệnh QA, CẤM bỏ; neo NỘI DUNG, không neo mtime (git clone đặt lại mtime)
- **Hồ sơ phỏng vấn**: specs/<thư-mục-feature>/interview-notes.md
- **Cổng lớp 1**: MẤT ngoài Danh sách sửa = <n> (phải 0) — câu <n> · chuỗi <n> · control <n> · ảnh <n>
- **Cổng lớp 2**: LẶP = <n> · LẶP-CTRL = <n> (phải 0, ngoài allow-dup) — đơn vị so <n> câu ≥60 byte + <n> ô ≥40 byte
- **Cổng lớp 3**: field <n>/<n> · kịch bản <n>/<n> · ngoại lệ <n>/<n> · SC <n>/<n> · quy ước <n>/<n> · trục NFR <n>/9 · QT có Cách kiểm <n>/<n> · FR có neo <n>/<n>
- **Câu BA đã sửa có chủ ý**: <n> — từng dòng "<đang có>" → "<sẽ thành>" (lý do); không có → `không có`
```

### Sau khi ghi

- [ ] `git diff -- <file BRD>` → trình người dùng. Khung chèn-thêm cho diff **gần như chỉ có dòng `+`**; xuất hiện nhiều dòng `-` = đã dời/viết lại, sai quyền hạn → soát lại Bước 1.
- [ ] Có extension `dft-speckit` → chạy `python .specify/extensions/dft-speckit/scripts/brd_roadmap.py verify docs/roadmap.md --brd docs/brd --brd-rel docs/brd`; exit ≠ 0 → **khôi phục từ backup**, báo lỗi nguyên văn.
- [ ] KHÔNG đụng `brd.manifest.yml`.
- [ ] Dọn file làm việc: xoá `.specify/interviews/<slug>.{sent,long,str,img,ctrl,ba-flat,new-flat,allow-dup}.txt` + `<slug>.new-stripped.md` (GIỮ backup trong `.specify/brd-backup/`).
- [ ] **Cảnh báo nguồn sự thật (bắt buộc nêu)**: từ đây markdown là bản gốc, `.docx` chỉ là hạt giống — `brd-import` chạy lại sẽ không merge được. Liệt kê file đã bổ sung: `grep -rl "Từ điển dữ liệu" docs/brd/`.
- [ ] Báo cáo cuối: file đã ghi · ba bảng cổng · danh sách câu BA đã sửa · đường dẫn backup.
