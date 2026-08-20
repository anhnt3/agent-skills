---
description: "QA trọn vòng từ 1 file spec — sinh testcase thủ công (xlsx 2 sheet), sinh test tự động theo pyramid, tự dựng môi trường và chạy, báo cáo, fix có kiểm soát, ghi ma trận truy vết. Technology-agnostic — đặc thù stack đọc từ .agents/qa-context.md."
---

# QA Spec Cycle (trọn vòng từ 1 spec)

Nhận đầu vào là **1 file spec**, chạy trọn vòng QA qua 13 pha: sinh testcase thủ công (xlsx), sinh
test tự động theo pyramid, tự dựng môi trường, chạy, báo cáo, triage + fix có điểm dừng, và ghi ma
trận truy vết.

**Command này là engine tiến trình, agnostic với mọi stack.** Framework/lệnh/thư mục test cụ thể của
project **không** nằm trong command — chúng sống ở `.agents/qa-context.md` (tạo mới nếu thiếu, xem
Pha 1). Đổi stack = đổi qa-context, không đổi command.

Các file hỗ trợ được bundle trong extension:
- Script: `.specify/extensions/dft-speckit/scripts/csv_to_xlsx.py`
- Tài liệu chi tiết từng pha: `.specify/extensions/dft-speckit/references/<tên>.md`
- **LUẬT quy ước chung**: `.specify/extensions/dft-speckit/references/quy-uoc-chung.md` (QUCTHT) — xem Pha 4b.

## User Input

$ARGUMENTS

Kỳ vọng: đường dẫn tới `spec.md` hoặc thư mục feature. Nếu trống → hỏi nguồn spec trước khi tiếp tục.

## Nguyên tắc xuyên suốt

1. **Technology-agnostic** — không viết lệnh/tên framework cụ thể vào command; luôn tra qa-context hoặc scan.
2. **Scan trước, hỏi sau** — cái gì codebase trả lời được thì tự dò rồi thông báo ("Phát hiện X → dùng Y"); chỉ hỏi khi thật sự cần người quyết.
3. **Hỏi gọn** — dùng AskUserQuestion khi có sẵn, mỗi lượt gom 1–4 câu độc lập nhau (câu phụ thuộc tách lượt sau); `(Recommended)` đặt đầu CHỈ khi có căn cứ từ scan/qa-context ("Phát hiện X → khuyến nghị Y", nêu căn cứ ngay trong option) — không căn cứ thì không đánh Recommended.
4. **Pyramid integrity** — auto test author theo requirement × risk × tầng-thấp-nhất-chứng-minh-được, KHÔNG map 1:1 từ manual TC.
5. **No fake-green** — cổng cơ học chặn assert rỗng / selector-endpoint không tồn tại, trước khi present.
6. **No-defer** — dựng môi trường là việc của command; cấm bỏ test vì "thiếu môi trường", chỉ escalate đúng phần không tự làm được.
7. **Bounded fix** — auto-fix phía test/infra; product-bug duyệt từng cái + log phần dư thành issue.
8. **Manual columns thuộc về người** — kết quả tự động vào cột/sheet riêng, chỉ-đọc, có nhãn; 4 cột thực thi để trống cho tester.
9. **Checkpointed/resumable** — ghi tiến độ pha vào `qa-run.md`; gọi lại → đọc ledger, chạy tiếp từ pha dở dang.

## Pipeline 13 pha

**Bắt buộc**: trước khi bắt đầu một pha có ghi `→ chi tiết:`, PHẢI đọc file chi tiết đó (mỗi file một
lần trong phiên — kể cả khi resume vào giữa pha). Dòng tóm tắt trong command này KHÔNG đủ để thực thi
pha; thực thi mà chưa đọc chi tiết là vi phạm quy trình.

Ghi trạng thái pha vào `<thư mục spec>/qa-run.md` ngay sau khi hoàn thành mỗi pha (để resume). Nếu
`qa-run.md` đã tồn tại khi bắt đầu → đọc ledger, tiếp tục từ pha dở dang, không làm lại từ đầu.

- [ ] **Pha 0 — Intake.** Xác định file spec (từ `$ARGUMENTS` hoặc hỏi), rút feature-id + PREFIX (vd `DEV`) dùng cho ID testcase. **Trích nguyên văn danh sách id neo từ chính NGUỒN đã chọn** — `SOURCE = brd` → `QT-###` + `TR-###` + `SC-###` + **`S-<n>` mọi luồng con của mục kịch bản** + **mỗi điều khiển của mục mô tả điều khiển** (id chạy `CTRL-<nn>`, đếm theo hàng bảng) + **mỗi dòng tiền điều kiện của mục điều kiện** (id chạy `DK-<nn>`) — id chạy gán trong `qa-run.md` kèm nguyên văn dòng nguồn, KHÔNG ghi vào BRD, dùng được ở cột 10 `Truy vết`; `SOURCE = spec` → `FR-###` + `SC-###` — (không từ trí nhớ), đếm `N`, ghi cả danh sách + `N` + `SOURCE` vào `qa-run.md` — đây là mỏ neo đối chiếu của Pha 3/9/Done-when. `N` không đếm `S-`/`DK-`/điều khiển = cổng mù (đã gặp: báo `21/21 · GAP 0` mà thiếu trắng 1 luồng con + 24/49 điều khiển). `CTRL-`/`DK-` chỉ sống trong ledger + cột `Truy vết`, nghĩa tra ở `qa-run.md`. Tạo `qa-run.md` nếu chưa có, hoặc đọc ledger nếu đã có (đã có ID testcase trong xlsx → tái dùng nguyên văn, cấm renumber, xem Pha 4). → chi tiết (format ledger chuẩn + quy tắc resume): `.specify/extensions/dft-speckit/references/traceability.md` §2–§3 — ledger free-form không theo format là phiên sau không resume được.
  - **Định vị BRD nguồn (cho cột 17 `Nguồn BRD`).** Chỉ lần theo trường **`Nguồn`** của item roadmap ứng với feature (RM-ID trong tên thư mục spec / tiêu đề spec / hỏi) — **CẤM đoán theo tên file**. Ghi kết quả vào ledger, dòng `BRD_ROOT:`:
    - `Nguồn` = `docs/brd/….md[#mục]` → `BRD_ROOT` = **phần path, BỎ anchor** (anchor của `Nguồn` chỉ là gợi ý mục mặc định — cột 17 tự ghép `#<mục>` riêng, giữ anchor sẽ ra `…md#a#b`).
    - `Nguồn` = thư mục (node inline) → `BRD_ROOT` = thư mục; cột 17 ghi `<thư-mục>/<file>.md#<mục>` của file thực sự dùng.
    - `Nguồn` = `N/A` / trỏ code / không roadmap / không `docs/brd/` → `BRD_ROOT = N/A`.
    - Không định vị được item + **non-interactive** → `BRD_ROOT = N/A` + ghi lý do vào ledger, KHÔNG đoán RM-ID, KHÔNG HALT (nguồn làm giàu, không phải cổng).
  - **Chọn NGUỒN NỘI DUNG** (ngay sau khi có `BRD_ROOT`):
    - Nhận diện BRD đã bổ sung — đủ CẢ BA: (1) có mục `Từ điển dữ liệu`; (2) có `QT-<nn>` mang `Cách kiểm`; (3) có ≥1 bước `S-<n>` HOẶC mục mô tả điều khiển (BRD kiểu SRS thiếu (3) → `SOURCE = spec`, tránh bộ case tầng giao diện nghèo đi im lặng). Số hiệu mục KHÁC nhau giữa dự án — CẤM neo theo số. `BRD_ROOT` là file → kiểm chính file đó; là thư mục → `grep -rlE '^## [0-9]+\. Từ điển dữ liệu' <BRD_ROOT>`: 0 → `SOURCE = spec` · 1 → dùng file đó · ≥2 → hỏi người dùng; non-interactive → blocker + `SOURCE = spec`. CẤM tự chọn.
    - **CỔNG TƯƠI-MỚI** (bắt buộc trước khi chốt `SOURCE = brd` — bản cũ mà vẫn tin là bỏ sót phủ im lặng): (1) tập `SC-###` của `spec.md` ⊆ tập `SC-###` trong BRD — BRD dùng chung nhiều RM được phép chứa SC của RM khác, SC mang nhãn `*(RM-<nnn>)*` thì chỉ so trong phạm vi RM của feature (`grep -o 'SC-[0-9]\+' <file> | sort -u` hai bên rồi so tập, KHÔNG so tổng đếm toàn file) — **và** BRD có ≥1 `QT-###` + ≥1 `TR-###`; (2) `shasum <spec.md> | cut -d" " -f1` khớp dòng `- **spec.md sha1**` của **entry nhật ký có `Nguồn spec` trỏ đúng spec đang xử lý** (nhật ký nhiều entry khi BRD dùng chung — CẤM lấy bừa entry đầu; neo NỘI DUNG, không neo mtime). Không có dòng sha1 (bản cũ) → chỉ so TẬP `SC-###` như (1); `spec.md` có 0 `SC-###` → tập rỗng ⊆ mọi tập, nhánh này MÙ — CẤM dùng, chốt `SOURCE = spec`. Lệch bất kỳ → CẤM `SOURCE = brd`: có người → hỏi chọn *chạy lại riêng mục "Bổ sung BRD" của `/speckit.specify`* (không phỏng vấn lại) hay *chấp nhận `SOURCE = spec`*; không người → blocker `BRD chưa cập nhật` + `SOURCE = spec`.
    - Qua cổng → `SOURCE = brd`, ghi ledger `SOURCE: brd · <path>`. Mọi mục nội dung đọc trong BRD, KHÔNG đọc `spec.md`. Hợp đồng mục ↔ pha:

      | Mục BRD | Lệnh QA dùng ở |
      |---|---|
      | mục **quy tắc nghiệp vụ** — gạch đầu dòng mang `QT-<nn>` + `Cách kiểm` | Pha 0 neo `N` · Pha 3 lấy `Cách kiểm` chọn tầng |
      | mục **kịch bản/luồng** — bước `S-<n>` + `### Luồng ngoại lệ` `S-<n><a>` | Pha 4 — ca luồng chính + ca ngoại lệ |
      | `Từ điển dữ liệu` — hàng `TR-<nn>` | Pha 4 — ca biên (độ dài · miền · tập giá trị · duy nhất) |
      | `Chất lượng phi chức năng` | Pha 3 — ca hiệu năng/bảo mật/tin cậy |
      | `Quy ước chung áp dụng` | Pha 4b |
      | `Tiêu chí chấp nhận` | Pha 4 — Given→`Tiền điều kiện`, Then→`Kết quả mong đợi` |
      | mục **mô tả điều khiển** (lời BA) | Pha 4 — **NGUỒN SINH CASE**, không phải từ điển tra chữ: mỗi điều khiển ≥1 case. Thường là mục dài nhất BRD (đo thật: 59% tài liệu, 49 điều khiển) — coi nó là tra cứu thì mất gần hết case tầng giao diện |
      | `Đặc tả màn hình` (specify chép từ spec sang BRD) | Pha 4 — case trạng thái UI theo `### Màn` |
      | `interview-notes.md` — ma trận `FR ↔ neo BRD` | Pha 11 — đối chiếu, KHÔNG chép đè; ma trận KHÔNG nằm trong BRD |

    - Không nhận diện được / `BRD_ROOT = N/A` → `SOURCE = spec`, chạy như cũ (degrade hợp lệ, KHÔNG phải thiếu sót).
    - BRD có mục nhưng ghi một dòng "không áp dụng" → coi mục đó không có; **KHÔNG rơi ngược về `spec.md`** cho phần còn lại (trộn hai nguồn = sinh case mâu thuẫn).
  - **Phát hiện cấu trúc (graceful).** Nguồn theo kỷ luật một-nhà (preset DFT) tách: hằng số field ở `## Thực thể & Từ điển dữ liệu`, hành vi + business rule ở `### Functional Requirements` (rule giờ là FR → **đã** nằm trong neo `N` khi `SOURCE = spec`), trình bày ở `## Đặc tả màn hình` (chỉ trỏ FR/field). Ghi vào ledger nguồn có hai mục đó hay không. **Có** → Pha 3/4 đọc thêm hai mục để phủ **biên** + **trạng thái UI** (bên dưới). **Không có** (spec plain spec-kit / lệnh khác) → chạy đúng như cũ, không coi là thiếu.
- [ ] **Pha 1 — Context.** Có `.agents/qa-context.md` → load. Thiếu → scan + phỏng vấn tạo mới theo template slim. → chi tiết: `.specify/extensions/dft-speckit/references/qa-context-template.md`
- [ ] **Pha 2 — Scan & baseline.** Dò framework/thư mục test hiện có (điền vào qa-context những field còn thiếu), test đã có cho spec này chưa, môi trường sẵn sàng chưa → **thông báo phát hiện**, không hỏi lại cái đã dò được. → chi tiết: `.specify/extensions/dft-speckit/references/qa-context-template.md`
- [ ] **Pha 3 — Coverage matrix.** Từ mỗi id neo trong `N` (đọc NGUYÊN VĂN từ ledger Pha 0, CẤM suy lại theo tiền tố) + mức risk → chọn tầng test (unit/integration/E2E/manual-only) + lý do. **Cổng đếm: ma trận phải phủ đủ `N` id đã chốt ở Pha 0** — id nào không có dòng nào → ghi tường minh là `GAP` kèm lý do, cấm bỏ trắng.
  - `SOURCE = brd` → **cột `Cách kiểm` của từng `QT-###` là đầu vào trực tiếp**, không phải gợi ý: nó do người trả lời chốt lúc phỏng vấn (ISO 29148 §5.2.8 đòi mỗi yêu cầu khai phương pháp kiểm chứng). Chọn tầng khác với cột đó → **phải nêu lý do trong ma trận**, CẤM đổi im lặng. Cột trống/không có/ghi `chưa chốt` → chọn tầng như cũ theo risk (`chưa chốt` = QT chưa qua duyệt thuộc tính, nằm trong mục `QT chưa gán Cách kiểm` của `interview-notes.md` — ghi chú vào ma trận, KHÔNG phải blocker).
  - `SOURCE = brd` → thêm dòng ma trận cho **mọi trục có nội dung** ở mục `Chất lượng phi chức năng`; trục ghi `theo mặc định` thì trỏ nguồn mặc định, không sinh case trùng. → chi tiết: `.specify/extensions/dft-speckit/references/coverage-matrix.md`
- [ ] **Pha 4 — Manual TC → xlsx.** **Sinh case ĐỌC TỪ NGUỒN, CẤM ánh xạ lại bộ case cũ** — nguồn đổi mà chỉ sửa cột `Truy vết`/`Nguồn BRD` = cổng phủ tự chấm chính nó, luôn ra 100% (đã gặp: lọt 3 mệnh đề BRD không case nào phủ). Đúng cách: duyệt TỪNG mệnh đề kiểm được của nguồn (mỗi hàng `TR` · mỗi `QT` · mỗi dòng ngoại lệ · mỗi kịch bản · mỗi ca biên · mỗi `SC`) → hỏi *"case nào phủ?"* — khớp thì tái dùng (giữ nguyên ID), thiếu thì thêm mới. Đối chiếu HAI chiều: mệnh đề không case = thiếu; case không mệnh đề = thừa hoặc nguồn thiếu thông tin.
  - [ ] Khớp case ↔ mệnh đề bằng **nội dung `Kết quả mong đợi`**, KHÔNG bằng từ khoá tiêu đề: "soft-delete" trong một case kiểm bản ghi còn trong DB không phủ luật "mã đã xoá mềm vẫn tính trùng khi tạo lại" — hai luật khác nhau, cùng một từ. Mỗi acceptance scenario/rule → 1 case, đọc từ **NGUỒN đã chốt ở Pha 0** (`SOURCE`). Nguồn một-nhà (Pha 0) → làm giàu thêm, case bổ sung vẫn gắn `QT`/`TR`/`S-n`/`SC` hoặc màn trong ma trận, không giảm neo `N`:
  - [ ] **Tiền/hậu điều kiện từ Acceptance Scenarios** — ở mục `Tiêu chí chấp nhận` (khi `SOURCE = brd`) hoặc dưới mỗi `### User Story N` (khi `SOURCE = spec`); luật này áp cho **cả hai nguồn**. Vế **Given** của mỗi kịch bản → cột `Tiền điều kiện` của case; vế **Then** → `Kết quả mong đợi`. Chép nguyên văn, CẤM diễn đạt lại. Mục ca biên — `SOURCE = spec` → `### Edge Cases`; `SOURCE = brd` → `### Tình huống biên` (trong `Tiêu chí chấp nhận`) — mỗi dòng ≥1 case.
  - [ ] **Biên từ Từ điển dữ liệu**: mỗi field có `Giới hạn`/`Giá trị hợp lệ` → case tại-biên + ngoài-biên (`≤ 255` → 255 pass, 256 fail; tập giá trị → trong/ngoài). Số biên lấy từ Từ điển dữ liệu, CẤM bịa.
  - [ ] **Từ mục điều kiện — mỗi dòng tiền điều kiện ≥1 case kiểm CHÍNH điều kiện đó** (chưa đăng nhập · phiên hết hạn · thiếu quyền · thiếu dữ liệu tiên quyết). Tiền điều kiện chỉ làm bối cảnh ở cột `Tiền điều kiện` của case khác = CHƯA kiểm — phải có case đặt nó ở trạng thái SAI + xác nhận hệ thống chặn đúng (loại dễ sót nhất — đã gặp: 179 case phủ đủ 21/21 neo + 8/8 luồng vẫn thiếu trắng case *chưa đăng nhập*).
  - [ ] **Từ mục mô tả điều khiển — BẮT BUỘC, mỗi điều khiển ≥1 case** (bảng BA đã ghi sẵn nhãn + hành vi, chỉ việc chuyển thành case):
    - `Button`/`Action` → case bấm được + kết quả đúng mô tả; nút phụ (`Hủy`, `Đóng`, `X`) cũng phải có case, **không được coi là hiển nhiên**.
    - `Table`/danh sách → case dữ liệu hiển thị đúng · **từng cột** (nội dung + định dạng + khi rỗng) · mọi action trên hàng.
    - phân trang → case `Dropdown số hàng/trang` (đổi giá trị, áp dụng đúng) + `Pagination button` (đầu/cuối/kế/trước, trang biên).
    - `Radio`/`Dropdown`/`Checkbox` → case **danh sách giá trị hiển thị đủ** + đổi giá trị + giá trị mặc định.
    - `Textbox` → case nhập/sửa được, phối hợp với biên ở Từ điển dữ liệu.
    - vùng phức hợp (upload zone, khối kết quả, chỉ số đếm) → case cho **từng chỉ số/từng vùng**, không gộp một case "màn hiện đúng".
    - **Mỗi luồng con `S-<n>` phải có ≥1 case happy path riêng** — kể cả luồng chỉ-đọc như *Xem thông tin*; luồng chỉ-đọc rất dễ bị bỏ vì không sinh dữ liệu.
  - [ ] **Trạng thái UI từ Đặc tả màn hình**: mỗi `### Màn` → case cho 4 trạng thái (tải/rỗng+tổng số/lỗi mạng/có dữ liệu) · từng cột (hiển thị/định dạng/khi rỗng) · lọc-sắp-tìm (rỗng→empty, reset, đổi filter→trang 1, giữ/mất filter) · ẩn-khóa theo quyền · xác nhận + hệ quả lan truyền của hành động phá hủy. Bám tên field + neo màn trỏ (`FR-###` khi `SOURCE = spec`, `QT/TR/S-` khi `brd`), CẤM suy diễn ngoài NGUỒN. Phân công chống trùng khi `SOURCE = brd`: case trạng thái/lọc/quyền lấy từ `Đặc tả màn hình`; case bấm-được/nhãn/danh sách giá trị lấy từ mục mô tả điều khiển — cùng một điều kiện kiểm xuất hiện ở cả hai → giữ MỘT case.
  - [ ] **Input**: `testcases-manual.json` (17 khóa/case — ưu tiên) hoặc CSV 17 cột. **Cột 17 `Nguồn BRD`** — đúng một trong bốn, và phải **phân biệt được BA viết với công cụ chiếu sang**:
    - `<BRD_ROOT>#<mục của BA>` — case truy về mục BA thực sự viết (vd `#3-mô-hình-usecase`, `#7-mô-tả-điều-khiển`).
    - `<BRD_ROOT>#<mục do công cụ dựng> (SPEC)` — case truy về nội dung `/speckit.specify` đã chiếu sang (vd `#12-tiêu-chí-chấp-nhận (SPEC)`). **Hậu tố ` (SPEC)` là bắt buộc**. Phân định theo **nhật ký BRD, CẤM đoán theo số hiệu** (khuôn BRD mỗi dự án một khác): mục có tên trong danh sách `Mục mới chèn` của `## Nhật ký cập nhật` + các khối chèn trong mục gốc (tiền/hậu điều kiện, `### Luồng ngoại lệ`, `#### Bổ sung từ phỏng vấn`, hộp cảnh báo `> ⚠️` đầu mục điều khiển — anchor = mục chứa nó + hậu tố) → **có** hậu tố; mọi mục H2 khác (mục BA viết) → **không** hậu tố. Không có hậu tố thì hai loại trên cùng hình dạng, Done-when "phân biệt BA viết vs công cụ chiếu" thành không kiểm được.
    - `QUCTHT §<n>` — case sinh từ Pha 4b, không truy về BRD.
    - `N/A` — `BRD_ROOT = N/A` và không từ QUCTHT.
    CẤM để trống, CẤM gán `BRD_ROOT` cho case BRD không nói tới. Anchor phải là mục **có thật** trong file BRD — `slugify` giữ dấu tiếng Việt (xem `manual-xlsx-format.md`).
  - [ ] **MỘT case = MỘT điều kiện kiểm.** Hai lý do từ chối khác nhau (tệp quá nặng · tệp quá nhiều dòng) = **hai case**, dù cùng một nút. Dấu hiệu vi phạm, quét được bằng máy: chữ `hoặc`/`hay` trong `Kết quả mong đợi`, dấu `,` giữa hai giá trị trong `Dữ liệu test`, bước ghi kiểu `Nhập từng giá trị`. Case gộp thì chạy xong không kết luận được pass/fail.
  - [ ] **Bước phải thao tác được**: mỗi bước một hành động cụ thể trên một điều khiển có tên (`Bấm "Tạo mới"`), CẤM bước trừu tượng (`Kiểm tra các trường`, `Nhập từng giá trị`). Số bước khớp 1-1 số dòng `Kết quả mong đợi`.
  - [ ] **Thứ tự & gom nhóm — case xếp theo trình tự TESTER CHẠY, không theo thứ tự sinh ra.** Gom theo nhóm chức năng, trong nhóm theo luồng nghiệp vụ: `Danh sách → Xem → Tạo mới → Chỉnh sửa → Xoá → Nhập/Xuất → xuyên suốt (phân quyền · dấu vết · quy ước)`. Case biên/âm nằm **ngay trong nhóm sinh ra nó** (biên độ dài trường của form Tạo mới thuộc nhóm Tạo mới, KHÔNG dồn thành nhóm "Từ điển dữ liệu" riêng). Tự kiểm: mỗi nhóm = **một dải ID liền**; nhóm đứt đoạn = chưa xếp lại (đã gặp: 6/11 nhóm đứt đoạn, tester nhảy qua lại 4 lần).
  - [ ] **ID**: tái dùng NGUYÊN VĂN ID đã có trong xlsx; case mới cấp số ở CUỐI; bỏ case → để trống số, CẤM dồn số/renumber/đổi PREFIX. **Ngoại lệ duy nhất** — bộ case **chưa từng giao tester** (mọi cột thực thi còn trống, không có `Bug ID`): được cấp lại số một lần theo thứ tự đọc ở luật trên; phải ghi vào `qa-run.md` là đã renumber kèm lý do. Đã giao rồi thì vĩnh viễn cấm.
  - [ ] **Chạy** `.specify/extensions/dft-speckit/scripts/csv_to_xlsx.py <input> <thư mục spec>/testcases-manual.xlsx` → 2 sheet, 4 cột thực thi để trống. Exit `2` (ID có dữ liệu tester biến mất) / `3` (ID giữ nguyên nhưng Tiêu đề đổi khi tester đã chấm) → **file KHÔNG được ghi**: đọc lại ID+thứ tự từ chính xlsx, sửa input, chạy lại. CẤM tự thêm `--allow-id-loss`/`--allow-content-shift` (chỉ người dùng bật). Báo số case đã sinh.
  - → chi tiết (schema, merge, mã thoát): `.specify/extensions/dft-speckit/references/manual-xlsx-format.md`
- [ ] **Pha 4b — Đối chiếu LUẬT quy ước chung (QUCTHT).** Nguồn: `.specify/extensions/dft-speckit/references/quy-uoc-chung.md` — luật mặc định toàn công ty, spec thường không nhắc lại; dev build theo nó (`agents/*.md`), QA phải test theo nó.
  - [ ] **Neo đếm**: `S` = số section `## <n>.` đếm từ CHÍNH FILE (V1.0: 21), không từ trí nhớ. Ghi vào `qa-run.md` bảng **đúng `S` dòng**: `| § | Trigger | Áp/Bỏ | Case ID hoặc lý do bỏ |`. Thiếu dòng = vi phạm gate.
  - [ ] **Nguồn ưu tiên: bảng ở mục `Quy ước chung áp dụng` của BRD** (khi `SOURCE = brd`). Bảng đó do `/speckit.specify` chốt **có người trả lời**, nên là phán quyết, không phải suy đoán. Bảng có cột `§<n>` khớp số hiệu section của file này → nối được theo `§`, CẤM nối theo tên bằng lời.
    - **KHÔNG thay** danh sách trigger cơ học bên dưới: vẫn chạy trigger, rồi đối chiếu theo `§`.
    - Bảng khai `Ngoại lệ` cho `§` mà trigger nói `Áp` → xét **cột lý do**, không mặc nhiên là xung đột: lý do nêu điều gì của chính feature khiến § không áp → **đã phân xử ở specify** — ghi chú `qa-run.md`, sinh case theo bản ngoại lệ, KHÔNG chặn. Lý do trống/chung chung (`không áp dụng`, `theo thiết kế`) → có người thì hỏi; không người → `Xung đột QUCTHT` + Pha 4b `blocked`. Chiều ngược (bảng `Áp`, trigger không bắn) → chỉ ghi chú.
    - Bảng ghi đúng dòng `Không có bộ quy ước chung` (preset chạy ở dự án chưa cài extension) → **bỏ qua bảng, chạy trigger như thường, ghi chú vào ledger**. CẤM coi là xung đột hàng loạt.
    - `SOURCE = spec` (BRD chưa được bổ sung) → không có bảng, chạy trigger như thường.
  - [ ] **Trigger từng §** (feature CÓ thành phần → `Áp`, không có → `Bỏ` + lý do gắn feature; CẤM lý do trống/chung chung): §1 kiểu dữ liệu ← có field số/tiền/ngày/ID · §2+§3+§11 ← có trường nhập · §4 ← có tải tệp · §5 ← có nút/nhãn hành động · §6 ← có UI · §7 ← có bảng danh sách · §8 ← có form tạo/sửa · §9 ← có hành động xóa · §10 ← có thao tác sinh thông báo · §12 ← có hiển thị ngày giờ · §13 ← có nhập/xuất (gồm ca chống công thức Excel §13 đã viết sẵn) · §14 ← có tải trang/submit/breadcrumb · §15 ← có bản ghi DB (soft-delete, UUID) · §16 ← có trạng thái bản ghi · §17 ← có ràng buộc duy nhất · §18 ← đụng phiên/xác thực · §19 ← có phân quyền/phạm vi dữ liệu · §20 ← mọi feature có UI (tiếng Việt có dấu) · §21 ← có mutation.
  - [ ] **Bằng chứng đã đọc**: mỗi dòng `Áp` phải kèm ≥1 chuỗi trích NGUYÊN VĂN từ § đó trong case tương ứng — không trích được = chưa đọc, không được đánh `Áp`.
  - [ ] **Chuỗi trong `" "` chép nguyên văn** vào `Kết quả mong đợi`; **chỉ** placeholder `{…}`/`[…]` được thay, và chỉ bằng giá trị lấy từ Từ điển dữ liệu / §2 / tên thực thể trong spec (vd `"Vượt quá {max} ký tự."` + Tên ≤255 → `"Vượt quá 255 ký tự."`). Không có nguồn cho placeholder → ghi `[NEEDS: <tên>]`, CẤM bịa số.
  - [ ] **Xung đột spec/BRD ↔ QUCTHT** (hai bên phát biểu khác nhau về cùng một điểm): KHÔNG tự chọn bên, KHÔNG sinh case cho điểm đó. Ghi `qa-run.md` mục `Xung đột QUCTHT` (trích nguyên văn hai bên + §). Có người → hỏi ngay; **non-interactive → ghi blocker, bỏ đúng điểm xung đột, CHẠY TIẾP phần còn lại, đánh Pha 4b `blocked` (không `done`)**. **Sau phân xử** (phiên nào cũng vậy): sinh các case còn thiếu cho điểm vừa chốt → chạy lại Pha 4 (regenerate xlsx) → Pha 5/8/11 làm phần bù **cho case mới** — coi như input đổi, luật "không chạy lại pha đã done" không áp — rồi mới đánh Pha 4b `done`.
  - [ ] Case Pha 4b: `Truy vết` gắn id neo có sẵn trong `N` (CẤM đẻ mã mới) · cột 17 = `QUCTHT §<n>` · không giảm neo `N`.
- [ ] **Pha 5 — Author auto test.** Sinh test theo tầng đã chọn ở coverage matrix (không map 1:1 từ manual TC), dùng framework khai báo trong qa-context; comment truy vết FR + TC trong mỗi test; requirement manual-only ghi rõ lý do trong ma trận. → chi tiết: `.specify/extensions/dft-speckit/references/test-generation.md`, `.specify/extensions/dft-speckit/references/coverage-matrix.md`
- [ ] **Pha 6 — Quality gate.** Chạy compile/type-check của project (lệnh lấy từ qa-context); grep xác nhận selector/endpoint được assert thật sự tồn tại trong source; chặn assert tầm thường/rỗng. → chi tiết: `.specify/extensions/dft-speckit/references/quality-gate.md`
- [ ] **Pha 7 — Readiness (no-defer).** Tự dựng môi trường (services → migrate/seed → start backend/frontend background → cài deps test → poll tới ready) rồi gỡ blocker (auth, selector thiếu, seed). Lệnh phá hoại (migrate/seed/reset/khởi tạo có trạng thái) chỉ chạy vào **test target dùng-một-lần** đã khai báo trong qa-context; thiếu khai báo → dừng, hỏi (Recommended trước). **Cổng cứng khi cần người quyết** — escalate đúng phần không tự làm được, nêu rõ thiếu gì + lệnh gợi ý, chờ người dùng xử lý rồi tiếp tục, không bỏ ngang. → chi tiết: `.specify/extensions/dft-speckit/references/environment-bringup.md`, `.specify/extensions/dft-speckit/references/blocker-playbook.md`
- [ ] **Pha 8 — Run + record.** Chạy suite thật; ghi auto-status vào cột/sheet auto (không đụng cột người); test chưa chạy được → ghi "chưa chạy" trung thực, không âm thầm pass. → chi tiết: `.specify/extensions/dft-speckit/references/traceability.md`
- [ ] **Pha 9 — Present.** **Cổng cứng: phải trình bày trước khi qua pha 10.** Báo cáo pass/fail + coverage theo **đủ `N` id neo chốt ở Pha 0** (id vắng mặt trong ma trận → liệt kê là GAP) + gap rõ ràng + phân bố pyramid (unit/integration/E2E/manual-only) + kết quả quality gate + trạng thái môi trường.
- [ ] **Pha 10 — Triage + bounded fix.** Phân loại mỗi fail: test-defect / infra-blocker / product-bug. Auto-fix test-defect và infra-blocker. **Cổng cứng khi gặp product-bug** — không tự sửa code sản phẩm; trình chẩn đoán + đề xuất patch, chờ duyệt từng cái, fix cái được duyệt + chạy lại, log phần dư thành issue rồi dừng. → chi tiết: `.specify/extensions/dft-speckit/references/failure-classification.md`
- [ ] **Pha 11 — Finalize truy vết.** Hoàn thiện ma trận trong xlsx: mỗi id neo (`N` của Pha 0) ↔ manual TC ↔ test tự động (file::name) ↔ tầng ↔ trạng thái ↔ gap. → chi tiết: `.specify/extensions/dft-speckit/references/traceability.md`
- [ ] **Pha 12 — Update CLAUDE.md/AGENTS.md.** Nếu chưa có mục "cách test" → thêm (tooling, cách dựng môi trường, lệnh chạy từng tầng — lấy nguyên từ qa-context, không hardcode lại trong command). File này lái mọi phiên agent sau → **show diff và chờ xác nhận trước khi ghi**, không ghi âm thầm.

## Cổng cứng (hard gates) — không được bỏ qua

- **Pha 7**: khi môi trường có phần không tự dựng được (thiếu engine, secret, quyền mạng) → escalate và **dừng chờ người dùng**, không tiếp tục giả định đã xong.
- **Pha 7 (env-safety)**: lệnh phá hoại (migrate/seed/reset/khởi tạo có trạng thái) chỉ chạy khi có **test target dùng-một-lần** khai báo trong qa-context; không có → dừng, hỏi, không đoán bừa vào DB/service thật. → chi tiết: `.specify/extensions/dft-speckit/references/environment-bringup.md`.
- **Pha 4 (dữ liệu tester)**: `csv_to_xlsx.py` thoát **2** (ID biến mất) hoặc **3** (ID giữ nguyên nhưng nội dung case đổi) → **dừng, sửa ID/thứ tự cho khớp, chạy lại**. CẤM thêm `--allow-id-loss` / `--allow-content-shift` để cho qua; hai cờ đó chỉ người dùng bật.
- **Pha 4b (xung đột QUCTHT)**: spec/BRD nghịch với `quy-uoc-chung.md` → không tự chọn bên, không sinh case cho điểm đó; có người thì hỏi, non-interactive thì blocker + bỏ điểm đó + chạy tiếp (Pha 4b = `blocked`).
- **Pha 9**: luôn present đầy đủ trước khi bước sang triage/fix — không được nhảy thẳng từ chạy suite sang sửa code.
- **Pha 10**: mọi fail loại product-bug phải được **duyệt từng cái** trước khi fix; không tự ý sửa logic sản phẩm mà không có xác nhận.

## Chế độ non-interactive

Khi command chạy không có người trực tiếp (subagent/CI/autopilot) và gặp 1 trong các cổng cứng ở trên
(**dữ liệu tester Pha 4** — exit 2 hoặc 3, escalate Pha 7, product-bug Pha 10, **xác nhận ghi
CLAUDE.md/AGENTS.md ở Pha 12**) → **KHÔNG được** tự bỏ qua cổng, tự thêm `--allow-id-loss` hay
`--allow-content-shift`, tự ý duyệt fix code sản phẩm, hay ghi test chưa chạy thành "pass". Thay vào đó:
ghi 1 bản ghi blocker vào `qa-run.md` (đang ở pha nào, cần gì, vì sao dừng) rồi **HALT**. Riêng
**xung đột QUCTHT Pha 4b**: KHÔNG HALT cả run — blocker + bỏ đúng điểm xung đột + chạy tiếp, Pha 4b
đánh `blocked` (thiệt hại đã khu trú ở điểm đó; Done-when chặn báo xong giả). Riêng Pha 12: KHÔNG ghi
`CLAUDE.md`/`AGENTS.md` khi không có người duyệt — ghi diff đề xuất vào `qa-run.md`, đánh dấu Pha 12
`blocked`, rồi HALT. Chạy lại sau (có người) → đọc `qa-run.md`, tiếp tục đúng từ điểm blocker.

Pha 9 (present) **không** phải điểm HALT: vẫn xuất đầy đủ báo cáo rồi chạy tiếp Pha 10 (auto-fix
test-defect/infra-blocker — không cần người duyệt); chỉ dừng khi chạm product-bug.

## Ủy thác cho subagent (khi có Task/Agent tool)

Nếu môi trường có Task/Agent tool: **chạy các pha NẶNG (5, 6, 7, 8) trong subagent con** — con làm
phần bulk (sinh nhiều file, chạy suite, chạy env, grep lớn), ghi artifact ra **file**, chỉ trả về
orchestrator một **summary ngắn + đường dẫn file**, KHÔNG trả raw stdout hay nội dung file về context
cha. Mục đích: tránh work-product của các pha này (log suite, N file test sinh ra, log dựng env, kết
quả grep) làm phình context của agent chính.

| Pha | Con nhận | Con trả về |
|---|---|---|
| 5 — Author test | Quyết định coverage-matrix + qa-context + spec | File test đã ghi + danh sách FR/TC mỗi file phủ |
| 6 — Quality gate | Đường dẫn test vừa sinh + source root | **Fact thô**: đuôi log compile/type-check, danh sách `MISSING` đã xác nhận (không phải dynamic), vị trí assert tầm thường + đường dẫn artifact — **cha ra phán quyết PASS/FAIL**, con không tự tuyên bố PASS |
| 7 — Readiness | Khối "Môi trường & lệnh dựng" + test DB dùng-một-lần đã khai báo | Log ghi ra file + fact `READY`/`BLOCKED` + lý do — **quyết định escalate vẫn ở orchestrator** |
| 8 — Run + record | Lệnh chạy từng tầng | stdout → log file; trả pass/fail + id test fail + đường dẫn log. **Con không ghi `qa-run.md`/xlsx** — chỉ cha ghi |

**Prompt giao cho con PHẢI kèm**: đường dẫn file reference chi tiết của pha đó (bảng trên chỉ liệt kê
dữ liệu; con là context mới tinh, không tự biết reference tồn tại) + chỉ thị "đọc file reference này
TRƯỚC khi làm"; riêng Pha 5 kèm thêm **danh sách ID manual TC** (từ JSON/xlsx Pha 4) để comment truy
vết `Manual TC:` không bịa ID.

**Giữ trong orchestrator, KHÔNG ủy thác:** mọi cổng cứng (Pha 7 escalate, Pha 9 present, Pha 10 duyệt
product-bug, HALT ở chế độ non-interactive), `qa-run.md` ledger + xlsx (single source of truth), mọi
`AskUserQuestion`, phán đoán chọn tầng ở Pha 3, phân loại fail ở Pha 10.

**Ràng buộc an toàn:** subagent con **không được** tự duyệt cổng cứng, không được đánh dấu test chưa
chạy là pass; con chỉ trả *facts + đề xuất*, việc đánh giá gate luôn ở cha. Chế độ non-interactive ở
cha vẫn HALT + ghi blocker như bình thường, bất kể pha nào chạy trong con.

**Degrade:** không có Task/Agent tool → làm mọi pha inline như thường lệ (command vẫn chạy an toàn trong
1 context).

## Done-when

- `qa-run.md` log đủ **14 hàng** (pha 0–12 + hàng `4b` riêng, `done`|`blocked` — để resume không nhảy qua xung đột đang treo).
- `qa-run.md` ghi rõ `SOURCE: brd|spec` chốt ở Pha 0, và mọi mục nội dung đọc đúng nguồn đó — **không trộn hai nguồn**.
- xlsx tồn tại với 2 sheet (Testcases + Ma trận truy vết); 4 cột thực thi để trống; cột auto có kết quả (hoặc "chưa chạy" trung thực, không giả pass); **cột 17 `Nguồn BRD` điền đủ mọi dòng** — anchor mục BA / anchor mục do công cụ dựng / `QUCTHT §<n>` / `N/A`, không để trống, và mọi anchor phải phân giải được về một mục có thật trong file BRD.
- **Đã đối chiếu QUCTHT (Pha 4b)**: `qa-run.md` có bảng **đúng `S` dòng** (`S` đếm từ chính `quy-uoc-chung.md`), mỗi dòng `Áp` trỏ Case ID + trích dẫn, mỗi dòng `Bỏ` có lý do gắn feature; mục `Xung đột QUCTHT` đã được phân xử hoặc đang là blocker tường minh (Pha 4b `blocked`).
- Test tự động tồn tại, truy vết được về id neo, **đã chạy thật** (không skip/defer); quality gate pass.
- Môi trường được command tự dựng, hoặc phần không tự làm được đã escalate đúng và được xử lý tiếp sau khi người dùng can thiệp.
- Suite xanh, hoặc mọi gap/fail còn lại được liệt kê tường minh trong ma trận truy vết và trong phần present.
- Ma trận truy vết đầy đủ: **đủ `N` id neo chốt ở Pha 0**, mỗi id có manual TC + test tự động + tầng + trạng thái, hoặc được đánh dấu `GAP` kèm lý do.
- `CLAUDE.md`/`AGENTS.md` có mục "cách test" (đã thêm nếu trước đó chưa có).
