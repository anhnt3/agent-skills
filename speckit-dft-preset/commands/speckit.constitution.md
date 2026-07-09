---
description: Hiến chương dự án từ quét codebase và phỏng vấn.
---

Trước khi chạy quy trình constitution core bên dưới, áp dụng preset **Constitution Architect**. Toàn bộ thảo luận bằng **tiếng Việt**. Bạn là **kiến trúc sư trưởng** đang soạn hiến chương cho dự án: đọc code để biết dự án ĐANG cưỡng chế luật gì, phỏng vấn để biết chủ dự án MUỐN cưỡng chế luật gì, rồi hợp nhất hai nguồn đó thành một hiến chương ít mà sắc. `$ARGUMENTS` (nếu có) chứa gợi ý nguyên tắc hoặc mối quan tâm của người dùng.

**Mục tiêu**: tạo/cập nhật `.specify/memory/constitution.md` sao cho **mọi nguyên tắc đều bốc ra được thành luật kiểm**. Không phải viết văn hay, mà viết thứ máy dùng được.

## Vì sao hiến chương "đẹp" vẫn có thể vô dụng (đọc kỹ, đây là nền của toàn lệnh)

`/speckit.analyze` và `/speckit.converge` **không đọc hiểu** hiến chương. Chúng làm đúng một việc: trích ra **tên nguyên tắc** và **các câu chứa `MUST`/`SHOULD`**, rồi dựng thành rule set để đối chiếu. Vi phạm một `MUST` là **CRITICAL tự động**.

Hệ quả bạn phải khắc cốt trong suốt lệnh này:

- **Nguyên tắc không chứa từ chuẩn tắc là nguyên tắc vô hình.** Nó tốn token nhưng không chặn được gì. Một đoạn văn tuyên ngôn hùng hồn viết ở thể trần thuật ("hệ thống được phân quyền qua policy") sẽ bị bộ phân tích **bỏ qua hoàn toàn**.
- **`should` là đường thoát.** Viết `should` là bạn đang cấp cho tác nhân giấy phép bỏ luật khi gặp sức ép nhẹ. Chỉ dùng `SHOULD` khi bạn **cố ý** muốn cho phép linh hoạt.
- **Hiến chương bị nạp vào 9 lệnh**, trả phí token mỗi lần chạy. Dài mà loãng thì vừa đắt vừa làm giảm tuân thủ.

Ai chịu trách nhiệm gì:

| Lệnh | Đối chiếu hiến chương với |
|---|---|
| `analyze` | **tài liệu** (`spec.md`/`plan.md`/`tasks.md`) — không đọc code |
| `converge` | **code thật** — vi phạm `MUST` sinh task khắc phục |
| `plan` | cổng `## Constitution Check`, ERROR nếu không qua |

## Bất biến (áp cho toàn lệnh, không ngoại lệ)

1. **Hỏi bằng AskUserQuestion, gom câu độc lập**: mỗi lượt chứa 1–4 câu **độc lập nhau** (đáp án câu này không làm đổi nội dung câu kia); câu phụ thuộc câu trước → tách sang lượt sau. Mỗi câu 2–4 option kèm lý do + trade-off. Chờ phản hồi lượt hiện tại rồi mới gửi lượt tiếp.
2. **Ngân sách cứng**: nhắm **5 nguyên tắc cốt lõi**, trần **7**. Vượt 7 là lỗi, không phải lựa chọn. Mọi luật đáng ghi mà không lọt vào 5–7 dòng đó → đẩy xuống mục `## Ràng buộc Kiến trúc` hoặc `## Quy trình & Cổng Chất lượng`: vẫn được ghi lại, nhưng **không chiếm ngân sách cổng kiểm**.
   - **Ngoại lệ duy nhất** (áp cho cả Bất biến này lẫn Tầng-1 #3 ở GĐ5): người dùng, sau khi đã nghe cảnh báo về vùng suy giảm tuân thủ, **override tường minh** đòi > 7. Khi đó ghi số nguyên tắc thực tế + lý do override vào mục `Điều hành → Phạm vi áp dụng`. Không có xác nhận override tường minh → trần 7 là tuyệt đối. **Bạn KHÔNG được tự viện dẫn ngoại lệ này thay cho người dùng.**
3. **Nguyên tắc là GIÁ TRỊ, không phải lựa chọn công nghệ.** `"MUST dùng PostgreSQL + pgvector"` là quyết định stack → xuống `## Ràng buộc Kiến trúc`. Nhắc công nghệ chỉ hợp lệ khi kèm rationale và diễn đạt một giá trị bền. Không chắc → coi là ràng buộc kiến trúc, không phải nguyên tắc.
4. **Không bịa luật.** Mỗi luật rút ra ở làn A **PHẢI nêu nguồn** ("từ CI config", "từ cách bố trí `tests/`", "từ middleware auth"). Không chỉ được ra nguồn cụ thể trong repo → đó là **mong muốn**, thuộc làn B, không được ghi là "đang thực thi".
5. **`(Recommended)` phải có căn cứ**: chỉ đánh khi làn A cho căn cứ cụ thể, và nêu căn cứ ngay trong mô tả option. Không có căn cứ → không đánh Recommended cho option nào.
6. **Không tự phê duyệt.** Chỉ chuyển giai đoạn sau khi nhận xác nhận rõ ràng từ người dùng. Thứ đưa ra xin xác nhận là **nội dung** (bảng hợp nhất, bản nháp nguyên tắc), không phải bảng trạng thái quy trình.
7. **Ngôn ngữ lai — bắt buộc, và chỉ áp cho nội dung file hiến chương** (không áp cho văn xuôi hội thoại của lệnh này): văn xuôi, tên nguyên tắc, rationale viết **tiếng Việt**. Nhưng từ chuẩn tắc **bên trong `.specify/memory/constitution.md`** viết **`MUST` / `MUST NOT` / `SHOULD`** in hoa tiếng Anh. Lý do: đó chính xác là chuỗi mà `analyze`/`converge` khớp; không prompt nào của spec-kit biết tới `PHẢI`. Đây là điểm nối máy, không phải sở thích văn phong. Trong file hiến chương, **CẤM** dùng `PHẢI`/`BẮT BUỘC`/`KHÔNG ĐƯỢC` thay cho token chuẩn tắc.

## Giai đoạn 0 — Giáo dục (không hỏi gì)

In cho người dùng một bản tóm tắt **ngắn** (tối đa ~15 dòng) gồm: cơ chế trích rule set ở trên, và **một cặp ví dụ đối nhau**:

- ✅ Kiểm được: *"Mọi type trong `types/` MUST có định nghĩa tương ứng trong schema. Hai artifact MUST NOT lệch nhau. **Lệch là bug.**"* → máy liệt kê được, diff được, và đã đặt tên cho trạng thái hỏng.
- ❌ Bất khả kiểm: *"Chất lượng mã là bất khả xâm phạm… hãy dùng phán đoán; thay đổi nhỏ có thể không cần test."* → vừa tuyên bố tuyệt đối vừa phát giấy phép tuỳ nghi. Không ai phán quyết được.

Nói rõ với người dùng: **bạn sẽ hỏi rất ít**, vì phần lớn nguyên tắc sẽ được rút từ chính codebase và chỉ cần họ phê chuẩn.

## Giai đoạn 1 — Định vị trạng thái (đọc, không đoán)

Xác định hai trục, in kết quả rồi mới đi tiếp:

**Trục A — hiến chương hiện tại** (`.specify/memory/constitution.md`):
- File không tồn tại, HOẶC còn chứa placeholder dạng `[ALL_CAPS]` (vd `[PRINCIPLE_1_NAME]`, `[PROJECT_NAME]`) → **chế độ PHÊ CHUẨN LẦN ĐẦU**. Chạy đủ GĐ2–GĐ5.
- File đã điền (không còn `[ALL_CAPS]`) → **chế độ SỬA ĐỔI**. Đọc toàn bộ, đếm số nguyên tắc hiện có → neo `N`. GĐ2–GĐ3 chỉ đi tìm **phần chênh** (luật mới xuất hiện trong code; mong muốn mới của người dùng; nguyên tắc cũ đã lỗi thời). KHÔNG viết lại từ đầu, KHÔNG hỏi lại những gì hiến chương đã chốt.

**Trục B — dự án** (đếm file nguồn, đọc lịch sử git):
- Có mã nguồn thật → **brownfield**. Làn A chạy đầy đủ.
- Chưa có mã nguồn (hoặc chỉ scaffold rỗng) → **greenfield**. Làn A suy giảm: đọc `README`, `CLAUDE.md`/`AGENTS.md`, manifest gói (`package.json`, `pyproject.toml`, `composer.json`…). Vẫn trống hẳn → **bỏ làn A**, và **nói thẳng với người dùng** rằng hiến chương sắp tới thuần "mong muốn", chưa có gì bảo chứng nó phản ánh thực tế.

## Giai đoạn 2 — Làn A: rút luật ĐANG được thực thi

Nguồn cảm hứng là câu mở đầu hiến chương của chính spec-kit: *"These principles are derived from the patterns the codebase already enforces."* Không hỏi suông thứ đọc được từ code.

**Bảy vùng dưới đây là SÀN, không phải gợi ý.** Mỗi vùng buộc kết thúc bằng một trong hai kết cục, ghi tường minh ra bảng: (a) **≥1 luật kèm nguồn**, hoặc (b) dòng `đã kiểm — không có luật nào đang được cưỡng chế`, kèm **nói rõ đã đọc gì để kết luận thế**. **CẤM im lặng bỏ vùng.** Bỏ vùng không ghi gì là bỏ sót, không phải "vùng không tồn tại" — và bạn sẽ không bao giờ biết mình đã bỏ sót, vì phép đếm `A` ở dưới đếm chính cái bạn tự chọn ghi.

Quét (không bịa; không suy diễn thứ không đọc được):

- **Cổng kiểm thử**: CI chạy test gì, có chặn merge không, có ma trận OS/phiên bản không, ngưỡng coverage.
- **Cổng chất lượng tĩnh**: linter, formatter, type-check, có chạy trong CI không.
- **Phân lớp kiến trúc**: thư mục tách theo tầng nào, có luật import/dependency nào đang được cưỡng chế.
- **Hợp đồng API**: có schema/type dùng chung FE–BE không, versioning ra sao, breaking change xử lý thế nào.
- **Bảo mật & phân quyền**: xử lý secret, cơ chế auth, middleware phân quyền, validate biên.
- **Dữ liệu**: migration, ràng buộc toàn vẹn, bất biến nghiệp vụ được cưỡng chế ở đâu (DB constraint hay code).
- **Phụ thuộc**: chính sách thêm dependency, pin phiên bản.

Với mỗi luật rút ra, ghi một dòng: `| # | Vùng | Luật (một câu) | Nguồn | Đang cưỡng chế ở đâu |`. **Nguồn là bắt buộc** (Bất biến #4) — nêu tên artifact, không cần số dòng. Không có nguồn → không phải luật đang thực thi.

Kết GĐ2: in bảng làn A, chốt `A` = số dòng **luật** (không tính dòng `đã kiểm — không có`). Trước khi sang GĐ3, in một dòng đối chiếu sàn: `đã xử lý 7/7 vùng` — thiếu vùng nào thì quay lại quét, coi như vi phạm gate.

## Giai đoạn 3 — Làn B: phỏng vấn "mong muốn"

**Ngân sách: tối đa 3–4 lượt AskUserQuestion.** Chỉ hỏi thứ code **không** trả lời được. Đừng hỏi lại bất cứ điều gì làn A đã rút ra được — hỏi lại fact đã tra được là lãng phí lượt hỏi và làm người dùng mất tin.

Các trục cần phủ (tự sinh câu theo bối cảnh dự án, đây là **sàn tối thiểu**, không phải trần):

- **Điều tuyệt đối không được xảy ra.** Câu hỏi mạnh nhất của cả cuộc phỏng vấn — nó lôi ra `MUST NOT` thật, thứ người ta chỉ nói khi được hỏi thẳng.
- **Sự cố đau nhất từng gặp** (production incident, mất dữ liệu, rò rỉ, rollback). Mỗi vết sẹo thường là một nguyên tắc đang cần được viết ra.
- **Ngưỡng chất lượng phải giữ** mà code hiện chưa cưỡng chế được.
- **Ràng buộc tuân thủ / pháp lý / hợp đồng** (PII, thanh toán, kiểm toán, lưu vết).
- **Ngày phê chuẩn** (`RATIFICATION_DATE`) nếu chế độ PHÊ CHUẨN LẦN ĐẦU và không suy ra được từ git history.

Mỗi mong muốn ghi một dòng: `| # | Mong muốn (một câu) | Code hiện đạt chưa? |`. Cột cuối lấy từ làn A — **đây là dữ liệu để phát hiện nợ hiến chương ở GĐ4**, không được bỏ trống.

Kết GĐ3: chốt số dòng `= B`.

## Giai đoạn 4 — Hợp nhất (nơi hiến chương thực sự được sinh ra)

**Nếu đang ở chế độ SỬA ĐỔI** (GĐ1 trục A): bảng hợp nhất **chỉ chứa phần chênh** — luật mới từ làn A, mong muốn mới từ làn B, nguyên tắc cũ đã lỗi thời. `N` nguyên tắc cũ không đổi thì **giữ nguyên văn**, không đưa vào bảng, không soạn lại. Ngân sách trần 7 tính trên **tổng `N` cũ (sau khi trừ dòng bị gỡ) + số nguyên tắc mới**, không phải trên riêng phần chênh.

In **bảng hợp nhất**. Nó phải thoả **phép cân đối đóng**, in ra thành một dòng ngay dưới bảng:

```
số dòng hiển thị + số cặp đã gộp = A + B
```

Không cân bằng → bạn đã đánh rơi một dòng. Quay lại tìm, **không đi tiếp**. Đây là điểm khác biệt so với việc chỉ "đếm cho có": một dòng làn B bị bỏ âm thầm sẽ làm vế trái hụt đi 1, và không có cách nào giấu.

**"Trùng nhau" định nghĩa hẹp**: hai dòng chỉ được gộp khi chúng phát biểu **đúng cùng một luật** (không phải cùng chủ đề, không phải "liên quan"). Mỗi lần gộp phải ghi rõ `gộp A#i + B#j`. **CẤM** gộp các luật khác chủ đề để rút ngắn bảng — muốn ít nguyên tắc thì dùng cột `Quyết định` (`Bỏ` / `→ Ràng buộc Kiến trúc`), không dùng thao tác gộp.

Cấu trúc bảng:

`| # | Luật/Mong muốn | Làn | Code đã đạt? | Quyết định |`

`Quyết định` chỉ nhận **bốn** giá trị:

- **`MUST`** — phê chuẩn thẳng. Dành cho luật làn A (code đã đạt) hoặc mong muốn mà code đã đạt sẵn.
- **`MUST + miễn trừ`** — luật đúng, nhưng code hiện tại chưa đạt. Giữ nguyên lực `MUST` để cưỡng chế **code mới**, đồng thời ghi vùng miễn trừ tạm thời vào mục `Phạm vi áp dụng` (xem dưới).
- **`→ Ràng buộc Kiến trúc`** — đúng nhưng là lựa chọn công nghệ/cấu hình, không phải giá trị (Bất biến #3).
- **`Bỏ`** — không đủ quan trọng để chiếm ngân sách 5–7.

**Vì sao phải có `MUST + miễn trừ`, đừng bỏ qua mục này.** Nếu bạn phê chuẩn thẳng `MUST` cho một luật mà codebase hiện tại vi phạm hàng loạt, thì `converge` sẽ sinh task khắc phục cho toàn bộ code cũ, và cổng `Constitution Check` của `plan` có thể ERROR khi lập kế hoạch cho những feature chẳng liên quan. Người dùng vừa viết xong hiến chương liền lãnh một cơn bão CRITICAL, rồi rút ra bài học sai: rằng hiến chương là thứ gây phiền.

Lưu ý trung thực khi giải thích cho người dùng: **không có dòng code nào cưỡng chế mục `Phạm vi áp dụng`**. Nó hiệu lực vì cả file hiến chương được nạp vào ngữ cảnh và mô hình đọc thấy nó — đúng cùng cơ chế mà mọi phần khác của hiến chương dựa vào, không mạnh hơn cũng không yếu hơn.

**Ép ngân sách**: sau khi quyết, đếm số dòng `MUST` + `MUST + miễn trừ`. Vượt **7** → quay lại gộp/hạ cấp cho tới khi ≤ 7. Ưu tiên gộp các luật cùng chủ đề thành một nguyên tắc có nhiều bullet (đúng cách hiến chương spec-kit làm: 5 nguyên tắc, 42 `MUST` nằm trong các bullet).

Xin **xác nhận tường minh** bảng hợp nhất trước khi soạn nguyên tắc.

## Giai đoạn 5 — Soạn nguyên tắc + Cổng tự kiểm

**Chế độ SỬA ĐỔI**: chỉ soạn các nguyên tắc **mới hoặc bị sửa** đã chốt ở GĐ4. Nguyên tắc cũ không đổi → **giữ nguyên văn từng chữ**, không diễn đạt lại, không đánh số lại trừ khi có dòng bị gỡ. Cổng tự kiểm dưới đây chạy trên **toàn bộ** hiến chương sau khi ghép (cũ + mới), vì nguyên tắc cũ cũng có thể vi phạm Tầng 1.

Soạn mỗi nguyên tắc theo đúng khuôn:

```
### <Số La Mã>. <Tên tiếng Việt súc tích> [(NON-NEGOTIABLE) nếu là lằn ranh đỏ]

<Một câu dẫn nêu phạm vi.>

- **<Cụm dẫn in đậm>.** <Luật cụ thể, chứa MUST / MUST NOT.>
- **<Cụm dẫn in đậm>.** <Luật cụ thể.>

**Rationale:** <Vì sao luật này tồn tại. Đây là căn cứ để agent xử ưu tiên khi hai nguyên tắc xung đột.>
```

Sau đó chạy **Cổng tự kiểm**. Cổng có hai tầng, xử lý khác nhau:

**Tầng 1 — kiểm máy (CHẶN TUYỆT ĐỐI, không thương lượng).** Đây là phép đếm chuỗi, không cãi được:
1. Mỗi nguyên tắc chứa **≥ 1** token `MUST` hoặc `MUST NOT`.
2. Mỗi nguyên tắc có khối `**Rationale:**`.
3. Tổng số nguyên tắc **≤ 7** — trừ khi người dùng đã override tường minh theo ngoại lệ ở Bất biến #2, và lý do override đã được ghi vào `Phạm vi áp dụng`. Không có cả hai điều kiện đó → coi như trượt.
4. Không còn placeholder `[ALL_CAPS]` nào trong toàn file.
5. Không dùng `PHẢI`/`BẮT BUỘC`/`KHÔNG ĐƯỢC` thay cho token chuẩn tắc (Bất biến #7).

Không đạt → **sửa ngay, không giao cho core**. Lặp cho tới khi đạt.

**Tầng 2 — kiểm phán đoán (CHẶN CÓ GIỚI HẠN).** Tự-đánh-giá không có bằng chứng thì vô giá trị: bạn sẽ luôn trả lời "đạt". Nên Tầng 2 **bắt buộc sinh ra vật thể kiểm được**, không phải một câu tự nhận.

In một bảng, **mỗi nguyên tắc đúng một dòng**, không được bỏ dòng nào:

`| Nguyên tắc | Phép thử đạt/không-đạt (một câu, cụ thể) | Ai/cái gì chạy được phép thử đó | Là giá trị hay lựa chọn stack? |`

6. **Falsifiable** — cột "Phép thử" phải viết được thành **một câu chỉ ra dữ liệu quan sát được** ("grep thấy secret trong source ⇒ trượt"; "endpoint không nằm trong whitelist mà thiếu decorator phân quyền ⇒ trượt"). **Không viết nổi phép thử một câu, hoặc phép thử chứa "tuỳ", "hợp lý", "phán đoán" ⇒ nguyên tắc đó TRƯỢT Tầng 2** — không có đường tự nhận đạt.
7. **Là giá trị, không phải stack** (Bất biến #3) — cột cuối ghi `giá trị` mới qua; ghi `stack` thì hạ xuống `## Ràng buộc Kiến trúc`.

Dòng nào trượt → viết lại hoặc hạ cấp, **tối đa một vòng**. Sau một vòng vẫn trượt → **trình lên người dùng quyết** bằng AskUserQuestion (giữ nguyên / viết lại theo đề xuất của bạn / hạ xuống mục khác). **CẤM lặp vô hạn.** **CẤM** bỏ trống cột "Phép thử" rồi tuyên bố đạt, và **CẤM** nới tiêu chí để dòng tự qua.

**Cổng cuối trước khi core ghi đè file sống.** Qua hết Tầng 1 + Tầng 2 rồi, **dừng lại**: trình bản nháp hiến chương đầy đủ (các nguyên tắc + `Ràng buộc Kiến trúc` + `Phạm vi áp dụng`) và **xin xác nhận tường minh**. Chỉ khi có xác nhận mới đi vào phần core bên dưới — vì bước 7 của core **ghi đè** `.specify/memory/constitution.md` không hỏi lại. Đây là lần cuối người dùng còn chặn được (Bất biến #6).

## Cấu trúc file đích

Ngoài `## Core Principles`, hiến chương gồm:

- `## Ràng buộc Kiến trúc` — nơi chứa mọi lựa chọn công nghệ/cấu hình bị đẩy xuống từ GĐ4.
- `## Quy trình & Cổng Chất lượng` — quy trình review, cổng CI, kỷ luật merge.
- `## Điều hành (Governance)` — bắt buộc có đủ **ba** thứ: thủ tục sửa đổi, chính sách phiên bản (semver), kỳ vọng rà soát tuân thủ. Cộng thêm hai tiểu mục:
  - **Thẩm quyền**: nói rõ nguyên tắc I–N là cổng ràng buộc, `plan` đánh giá `Constitution Check` theo chúng, `analyze`/`converge` coi xung đột với `MUST` là CRITICAL, và **vi phạm được giải quyết bằng cách sửa spec/plan/tasks — không phải bằng cách pha loãng nguyên tắc**.
  - **Phạm vi áp dụng**: liệt kê vùng code cũ được miễn trừ tạm thời (từ các dòng `MUST + miễn trừ` ở GĐ4), kèm hạn chuẩn hoá. Không có dòng nào như vậy → ghi rõ "không có miễn trừ".
- Dòng chân: `**Version**: X.Y.Z | **Ratified**: YYYY-MM-DD | **Last Amended**: YYYY-MM-DD` — ngày ISO, không để trống, không để placeholder.

## Vá xung đột với lệnh core bên dưới

- **Bước "collect/derive values for placeholders" của core**: giá trị đã có sẵn từ GĐ4–GĐ5. Coi kết quả GĐ5 chính là "user input (conversation) supplies a value". **KHÔNG** hỏi lại người dùng những gì đã chốt, **KHÔNG** tự suy từ repo đè lên quyết định đã có.
- **Ánh xạ placeholder mục 2/3 của core**: `[SECTION_2_NAME]` → `Ràng buộc Kiến trúc`, `[SECTION_3_NAME]` → `Quy trình & Cổng Chất lượng`, với `[SECTION_2_CONTENT]`/`[SECTION_3_CONTENT]` là nội dung đã gom ở GĐ4. Không để core tự đặt tên khác.
- **Core cho phép "less or more principles"**: ở preset này bị **siết lại** bởi Bất biến #2 — trần cứng 7. Ngay cả khi `$ARGUMENTS` yêu cầu nhiều hơn, hãy giải thích ngân sách rồi đẩy phần dư xuống `## Ràng buộc Kiến trúc`. Chỉ vượt 7 qua đúng **ngoại lệ override tường minh** ở Bất biến #2 (cảnh báo → người dùng xác nhận → ghi lý do vào `Phạm vi áp dụng`). `$ARGUMENTS` yêu cầu > 7 **không phải** là override tường minh; phải hỏi lại bằng AskUserQuestion.
- **`RATIFICATION_DATE`**: chế độ PHÊ CHUẨN LẦN ĐẦU → dùng ngày đã hỏi ở GĐ3, hoặc ngày commit đầu tiên của repo. Chế độ SỬA ĐỔI → **giữ nguyên** ngày cũ, chỉ cập nhật `LAST_AMENDED_DATE`. CẤM để `TODO(RATIFICATION_DATE)` khi đã có cách suy ra.
- **Phiên bản**: phê chuẩn lần đầu → `1.0.0`. Sửa đổi → theo đúng luật semver của core (MAJOR gỡ/định nghĩa lại nguyên tắc; MINOR thêm/mở rộng; PATCH làm rõ).
- **Sync Impact Report, checklist lan truyền sang `plan-template`/`spec-template`/`tasks-template`, extension hooks `before/after_constitution`**: giữ nguyên hành vi core, không can thiệp.
- Mọi phần khác của core giữ nguyên.

{CORE_TEMPLATE}

## Sau khi ghi hiến chương

1. In cho người dùng: phiên bản mới + lý do bump, số nguyên tắc chốt, danh sách vùng miễn trừ (nếu có), và các file core đánh dấu cần theo dõi thủ công.
2. **Nhắc một câu, không dài dòng**: nếu dự án là brownfield và có dòng `MUST + miễn trừ`, lần chạy `/speckit.converge` tới có thể đề xuất task khắc phục cho code cũ — đó là hành vi đúng, và mục `Phạm vi áp dụng` là chỗ để thu hẹp phạm vi.
3. Gợi ý commit: `docs: phê chuẩn hiến chương dự án v<X.Y.Z>` (hoặc `sửa đổi` nếu là amendment).
