---
description: Rút đặc tả đủ sâu từ codebase theo cây functions.json, ghi .specify/docs/<đường-dẫn-cây>/intel.md kèm nguồn file:dòng — tài liệu nội bộ làm đầu vào cho srs-from-code. Tham số là một FN-ID đánh dấu điểm bắt đầu quét (trống = toàn dự án); tự đề xuất unit theo luật cha-trực-tiếp-của-lá, xác nhận qua cây thụt lề, rồi quét (hỏi song song/tuần tự khi có nhiều unit). Ghi thêm §10: phát hiện logic mâu thuẫn/lỗ hổng bảo mật thấy được trong lúc rút, để srs-from-code hỏi người dùng riêng.
---

# Code intel theo cây functions.json

Trước khi sinh SRS, rút **đặc tả thật** của codebase: màn hình, thực thể, quy tắc, luồng,
phân quyền, tích hợp — mỗi khẳng định kèm nguồn `file:dòng`. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: đây là tài liệu **nội bộ**, không giao khách — chỗ giao khách là
`srs.md` do lệnh `srs-from-code` sinh sau. Mỗi khẳng định ở §2–§7, §9, §11, §12 thuộc đúng
một trong ba dạng, không được lẫn lộn:

| Dạng | Cách ghi |
| --- | --- |
| Đọc thẳng từ code | Ghi bình thường, kèm `file:dòng` |
| Suy ra từ code, chưa chắc | Ghi kèm `file:dòng` gần nhất và đánh dấu `(suy đoán)` |
| Không có căn cứ nào trong code | **KHÔNG viết ở §2–§7, §9**; đưa xuống §8 thành câu hỏi |

**Cite không phải là dán một đường dẫn cho có — nó phải trỏ đúng chỗ đỡ được khẳng
định.** Kiểm bằng cách tự hỏi: dòng `file:dòng` đó có chứa **token cụ thể** làm căn cứ
trực tiếp cho câu vừa viết không (tên trường, regex, hằng số, annotation validation,
điều kiện `if`)? Có → **đọc thẳng**. Không có token nào, chỉ là suy luận hợp lý từ một
chỗ gần đó (vd thấy unique index rồi suy "trùng mã bị chặn" nhưng chưa thấy nhánh báo
lỗi thật) → **suy đoán**, dán đúng regex/hằng số làm nguồn đọc thẳng cho một khẳng định
suy đoán là tự đánh lừa chính lượt kiểm lại ở cuối. Ví dụ:

- Đọc thẳng: trường `MaxLength(200)` tại `Domain/User.cs:41` → "Tên tối đa 200 ký tự".
- Suy đoán: thấy `[Index(IsUnique = true)]` trên `Email` tại `Domain/User.cs:38`, chưa
  thấy nhánh xử lý lỗi trùng → "Email phải duy nhất *(suy đoán, chưa thấy message lỗi)*
  — `Domain/User.cs:38`".

Không có nguồn thì không được viết ở §2–§7, §9 — đây là luật ngăn tài liệu bàn giao sau
này chứa hành vi hệ thống không hề có.

## User Input

`$ARGUMENTS`

Kỳ vọng: **trống, hoặc một FN-ID**. FN-ID đánh dấu điểm bắt đầu quét:

- Trống → điểm bắt đầu là **gốc cây** — quét toàn bộ dự án.
- `FN-01` → chỉ quét nhánh đó.
- Một FN-ID lá → quét đúng một unit (chính nó).

Không còn khái niệm "cụm gõ tay" — thư mục sinh ra tự động từ cấu trúc `functions.json`,
không phải chuỗi tự do người dùng đặt.

## Validate cứng trước khi làm bất cứ gì khác

- **`.specify/docs/functions.json` không tồn tại** → DỪNG, nhắc chạy
  `/speckit.dft-speckit.fnlist-import` trước.
- **`$ARGUMENTS` không trống và không khớp `^FN(?:-\d{2})+$`** → DỪNG, in cú pháp hợp lệ
  (`FN-01`, `FN-01-01`, …), hỏi lại. Không tự đoán/tự sửa.
- **FN-ID đúng cú pháp nhưng không có trong cây** → chạy
  `python .../scripts/intel_tree.py units --functions .specify/docs/functions.json --roots <FN-ID>`
  sẽ tự báo lỗi kèm đúng FN-ID không tìm thấy — DỪNG, in nguyên thông điệp, không tự đoán
  ID gần đúng.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/`. Dùng `python3` nếu
`python` không có (macOS/Linux).

### 1. Đề xuất unit + xác nhận cây

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py propose \
  --functions .specify/docs/functions.json [--start <FN-ID nếu có>]
```

In ra danh sách unit đề xuất (mặc định: node có tất cả con đều là lá, hoặc node không
có con đứng một mình) kèm cây thụt lề có đánh dấu `[UNIT]`. Trình nguyên văn cây này cho
người dùng qua AskUserQuestion: xác nhận đúng ranh giới, hay muốn gộp/tách lại?

- Điều chỉnh hợp lệ: chọn một tập node KHÁC làm root của unit (sâu hơn hoặc cao hơn đề
  xuất), miễn mỗi root vẫn là một nhánh cây hợp lệ (không lẫn hai node không phải anh em
  vào cùng một unit — điều đó không được hỗ trợ).
- Chưa có phản hồi → DỪNG, không sang bước 2.
- Có điều chỉnh → dùng danh sách root người dùng chốt (không phải danh sách đề xuất mặc
  định) cho bước 2.
- Sau khi người dùng chốt danh sách root, kiểm: không root nào là tổ tiên hoặc hậu duệ
  của root khác trong **cùng danh sách** (nếu có, một FN sẽ lọt vào hai unit chồng lấn).
  Phát hiện vi phạm → DỪNG, chỉ rõ cặp root lồng nhau, hỏi lại người dùng chọn lại.

### 2. Tính đường dẫn + danh sách FN cho từng unit đã chốt

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py units \
  --functions .specify/docs/functions.json --roots <FN-ID,FN-ID,...>
```

Trả về, cho mỗi unit: `path` — đường dẫn FILE `intel.md` đầy đủ (đã có sẵn hậu tố
`/intel.md`), TƯƠNG ĐỐI so với `.specify/docs/` (ghép `.specify/docs/` + `path` mới ra
đường dẫn thật trong repo) — và danh sách FN-ID lá thuộc nhánh (kèm `name`/`status` hiện
tại) — đây là dữ liệu dùng để điền §1 của `intel.md`, không tự đọc lại `functions.json`
bằng mắt rồi gõ tay.

### 3. Chạy song song hay tuần tự?

Có **≥ 2 unit** → hỏi qua AskUserQuestion: chạy song song (mỗi unit một subagent độc lập
qua Agent tool) hay tuần tự (xử từng unit một). Đúng 1 unit → chạy thẳng bước 4-10 dưới
đây, không hỏi.

Chạy song song: dispatch một Agent riêng cho mỗi unit, giao FN-ID gốc của unit, đường dẫn
file `intel.md` (`path`, tương đối `.specify/docs/`), danh sách FN-ID kèm status (từ bước
2), và yêu cầu subagent đọc lại chính file lệnh này
(`.specify/extensions/dft-speckit/commands/code-intel.md`) rồi thực hiện đúng Bước 4–10
dưới đây cho một unit đó. Không đồng bộ giữa các subagent — hai unit dùng chung một
entity có thể cite khác nhau, chấp nhận là giới hạn đã biết.

Subagent **không tự gọi** `fnlist_import.py update` ở Bước 10 của chính nó. Thay vào đó,
sau khi Bước 9 (verify) pass sạch, subagent **báo cáo lại** cho agent cha danh sách cặp
`FN-ID=status` cần cập nhật (không tự ghi) — tránh race: nhiều subagent cùng ghi đè
`functions.json` sẽ làm mất cập nhật của nhau. Agent cha đợi **tất cả** subagent hoàn
tất, gom toàn bộ cặp `FN-ID=status` từ mọi subagent, rồi gọi `fnlist_import.py update`
**đúng một lần** với đầy đủ các `--set`.

Cùng lúc, subagent **cũng báo cáo lại nguyên văn `warnings`** (nếu có) từ lần chạy
`intel_verify.py` cuối cùng của unit mình, kèm dòng tổng kết `N lỗi chặn, M cảnh báo.` —
subagent không có ai để "trình bày" trực tiếp như một agent chạy đơn/tuần tự vẫn làm;
không báo cáo mục này thì warnings của unit đó (vd `cite-khong-ro`, `fn-khong-co-mat-o-
muc-2`, `man-hinh-thieu-dieu-khien`, `ghi-chu-khong-du-bang-chung`) biến mất hoàn toàn
khỏi mọi thứ người dùng thấy được. Agent cha đưa nguyên văn warnings đã gom vào phần
"Kết thúc" của báo cáo cho từng unit.

Chạy tuần tự: lặp qua từng unit, thực hiện Bước 4–10 cho unit đó xong mới sang unit kế.

### 4. Quét codebase — theo danh sách FN của unit, không theo trí nhớ

`functions.json` chứa **tên chức năng tiếng Việt** (`name`); code gần như chắc chắn dùng
định danh tiếng Anh. Grep thẳng tên tiếng Việt vào code gần như luôn ra rỗng — đó **không
phải** bằng chứng "không tìm thấy", đó là bằng chứng "tìm sai chỗ".

**Thang tìm kiếm tối thiểu — thử ít nhất 2 nấc trước khi được kết luận "không tìm
thấy"** cho một FN:

1. Tra chuỗi tiếng Việt (tên chức năng, từ khoá trong `description`) trong file ngôn
   ngữ/hằng số UI (`*.i18n.*`, `vi.json`, resource string…) → lấy key → Grep nơi dùng key.
2. Bảng route/menu/navigation/permission-code — bất kể khai bằng file config hay code.
3. Tên bảng/entity suy từ danh từ nghiệp vụ trong tên chức năng.
4. Từ khoá tiếng Anh dịch từ tên chức năng + từ khoá `description`, Grep trực tiếp.

Không có route/controller kiểu web (ứng dụng desktop, job nền, CLI) → điểm vào là
form/command handler/scheduler entry — vẫn áp thang tìm kiếm trên, chỉ đổi nơi tìm.

Từ điểm vào tìm được, lần theo tới service/repository/entity/validator liên quan.

**Mỏ neo phủ FN**: gọi `M` = số phần tử `fn_ids` của unit (từ bước 2). Cuối bước này,
mỗi FN phải rơi vào đúng một trong hai nhóm:
- **Tìm thấy** — có ít nhất một điểm vào cụ thể (`file:dòng`).
- **Không tìm thấy** — đã thử **thang tìm kiếm ở trên (≥2 nấc)**, ghi rõ ở cột `Ghi chú`
  §1 **ít nhất 2 pattern/từ khoá/thư mục thực sự đã chạy trong phiên này**. Ô `Ghi chú`
  trống, hoặc chỉ ghi chung chung kiểu "đã tìm không thấy", coi như **chưa tìm**.

**Tỉ lệ không tìm thấy vượt 1/3 `M`** → nhiều khả năng đang tìm sai module/sai phạm vi,
không phải codebase thiếu — **DỪNG**, trình danh sách FN không tìm thấy kèm pattern đã
thử, hỏi người dùng có đúng phạm vi không. `intel_verify.py` ở bước 9 cũng chặn ca này,
nhưng dừng sớm ở đây đỡ tốn công viết trước khi biết sai phạm vi.

**Mỗi mục §8 phải gắn một nhãn loại** ở đầu dòng — nhãn nào không nêu coi như
`[không suy được từ code]`:

- `[không suy được từ code]` — đã tìm mà không ra căn cứ; **loại duy nhất tính vào trần**.
- `[chính sách nghiệp vụ]` — quyết định chỉ người mới biết, không phải thứ code có thể
  tiết lộ dù tìm kỹ tới đâu.
- `[FN không tìm thấy]` — FN đã kết luận không tìm thấy code ở §1.
- `[chờ trả lời từ lần trước]` — câu hỏi mang sang từ lần chạy trước, chưa có phản hồi.

### 5. Ghi theo kỷ luật ba dạng

Rút vào §2 (Màn hình/điểm vào), §3 (Thực thể & trường dữ liệu), §4 (Kiểm tra hợp lệ &
quy tắc nghiệp vụ), §5 (Luồng nghiệp vụ), §6 (Phân quyền), §7 (Tích hợp ngoài, tác vụ
nền, sự kiện), §9 (Thông báo hiển thị), §11 (Điều khiển giao diện — xem hướng dẫn riêng
cuối bước này), §12 (Kịch bản Use Case — xem hướng dẫn riêng cuối bước này) của
`intel-template`.

Mỗi FN **tìm thấy** phải xuất hiện ở cột `FN liên quan` của **ít nhất một** dòng §2. FN
tìm thấy code nhưng không sinh màn hình nào (job nền, quyền thuần backend) → ghi rõ ở §7,
hoặc ở §8 với nhãn `[chính sách nghiệp vụ]` nếu không có gì để ghi ở §7 — **không dùng
nhãn `[không suy được từ code]`** cho ca này, đây là giải trình chính đáng chứ không phải
bế tắc. **Không được** để FN đó vắng mặt hoàn toàn khỏi §2 mà không giải trình ở một
trong hai nơi trên — `intel_verify.py` cảnh báo (WARNING) ca này ở bước 9.

**Mỏ neo phân tán — chỉ áp khi `M ≥ 4`** (dưới ngưỡng đó một dòng gánh hết là chuyện bình
thường, vd unit 2–3 FN Thêm/Sửa/Xoá cùng một màn): một dòng §2 gánh quá **1/2** số `M` →
không tự động fail, nhưng **mỗi FN trên dòng đó phải cite riêng** (handler/action
`file:dòng` khác nhau cho từng FN, không dùng chung một cite cho cả nhóm).

Mỗi dòng bạn định viết, tự hỏi: cite có chứa token đỡ trực tiếp cho khẳng định không
(xem "Nguyên tắc lõi")? Có → đọc thẳng. Không → `(suy đoán)`. Không có gì để cite →
xuống §8.

**§4 tách riêng cột "Độ chắc chắn"** (`chắc` / `suy đoán`) — mức tự tin nội bộ để người
soát tay đọc trực tiếp `intel.md`. Khuôn `srs.md` hiện tại (đợt 3B-3) không còn mục
"Đặc tả dữ liệu" riêng; mọi quy tắc (kể cả đánh dấu `suy đoán`) rót chung vào mục
`g. Yêu cầu nghiệp vụ`, không đánh dấu lại mức tự tin trong tài liệu giao khách.

**Điều khiển giao diện (§11)** — sau khi §2 đã có đủ tên màn hình + cite điểm vào, với
mỗi màn hình đó: mở file component/template/view mà cột `Nguồn` của §2 trỏ tới (lần theo
cả component con nếu màn hình tách nhiều file), liệt kê control thật khai báo trong đó
(input, button, checkbox, dropdown, link…) vào bảng §11. Giữ nguyên kỷ luật ba dạng —
không nới riêng cho §11: đọc thẳng từ khai báo control → ghi bình thường kèm cite đúng
dòng khai báo; suy đoán (vd đoán nhãn hiển thị vì nhãn nằm ở file ngôn ngữ chưa tìm ra) →
đánh dấu `(suy đoán)`; không có căn cứ → không ghi, đưa xuống §8.

Cột `Màn hình` của §11 phải khớp **nguyên văn** giá trị cột `Màn hình / endpoint` tương
ứng ở §2 — đây là khoá liên kết duy nhất giữa hai mục mà `srs-from-code` đợt sau dùng để
dựng bảng điều khiển cho từng màn hình. Sai một ký tự là mất liên kết.

Cột `Loại` dùng lại đúng bộ từ vựng "Loại trường điều khiển" cố định: `Textbox`,
`Passwordbox`, `Checkbox`, `Dropdown`, `Datepicker`, `Button`, `Link`,
`Label (chỉ xem)`; loại thật không nằm trong danh sách thì ghi tên loại đó nguyên văn.

Màn hình/điểm vào ở §2 **thật sự không có giao diện** (endpoint REST thuần, job nền, CLI,
message consumer) → ghi **đúng một dòng** §11 với `Loại = không-có-UI`, cột `Mô tả` nêu
rõ **lý do cụ thể** (loại điểm vào là gì), kèm cite — đây là giải trình có căn cứ, không
phải ô trống. `intel_verify.py` ở bước 9 cảnh báo (WARNING) nếu một màn hình ở §2 không
có dòng §11 nào (kể cả dòng `không-có-UI`), hoặc nếu §11 có tên màn hình không khớp §2.

**Kịch bản Use Case (§12)** — sau khi §2 và §5 đã ghi xong (mục này phụ thuộc cả hai),
với mỗi màn hình đã có ở §2: dựng một khối `### [Tên Use Case]` trong §12, KHÔNG quét
code lần hai — tái dùng đúng bằng chứng đã thu:

- **Màn hình**: lấy nguyên văn từ cột "Màn hình / endpoint" của §2 — đây là khoá liên
  kết, phải khớp chính xác.
- **`Người dùng`**: suy từ §6 (bảng Phân quyền, cột Vai trò) nếu có dòng khớp màn hình
  này; không có → suy từ đối tượng dùng màn hình đó ở §2, đánh dấu `(suy đoán)`.
- **`Người sử dụng và yêu cầu`**, **`Mô tả tóm tắt`**: viết từ chính bằng chứng của §5
  (mô tả luồng) + §2 (tên màn hình) — một câu/đoạn tóm gọn, cite trỏ về cùng `file:dòng`
  đã dùng ở §5 cho luồng tương ứng.
- **`Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`**: viết lại đúng bằng chứng của §5 theo
  khuôn đánh số/nhánh `S-n` của Use Case, KHÔNG suy luận bước mới ngoài những gì §5 đã
  có. §5 không có luồng nào ứng với màn hình này → xem ranh giới và cách gộp câu hỏi §8
  ngay dưới đây.
- **`Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng`**: LUÔN ghi cố định "Chưa có thông
  tin" — đây là phân loại nghiệp vụ thuần, không có căn cứ code nào trả lời được.
  **Không đưa ba field này xuống §8** — khác kỷ luật ba dạng đang áp cho các field còn
  lại, vì đây không phải "chưa tìm ra" mà là "cấu trúc không thể tìm ra"; đưa xuống §8
  sẽ cộng thêm 3 câu hỏi vô nghĩa cho MỖI use case vào trần `§8`.

**Ranh giới rõ trước khi quyết định viết gì** — hai tình huống "không có gì để viết cho
màn này" dễ bị lẫn, phải tách đúng ngay từ đầu:

- **Màn hình/điểm vào không có use case thật nào** (endpoint kỹ thuật thuần — webhook
  nội bộ, health-check, cron trigger, không gắn với luồng người dùng nào) → **không viết
  khối `###`** cho nó, và **không đưa gì xuống §8** (khác §11 — §12 không có dòng giải
  trình `không-có-UI` riêng). Đây là lối thoát WARNING-only của `check_section12_coverage`:
  `intel_verify.py` ở bước 9 chỉ cảnh báo chứ không chặn nếu bỏ sót, người soát tự quyết
  có bổ sung hay không — cùng tinh thần với cách các mục khác của pipeline này xử lý thứ
  không có bằng chứng để rút.
- **Màn hình này CÓ use case thật, chỉ là §5 hiện chưa ghi luồng nào ứng với nó** → vẫn
  viết khối `###` bình thường (các field khác vẫn rút được từ §2/§6); riêng
  `Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ` không viết được có căn cứ → đưa xuống §8 với
  nhãn `[không suy được từ code]`, KHÔNG bỏ khối `###`.

**Gộp câu hỏi §8 theo unit, không theo từng màn hình**: khi nhiều màn hình trong cùng
một unit đều rơi vào ca thứ hai ở trên (có use case thật nhưng thiếu luồng §5), không
tạo một mục §8 riêng cho mỗi màn — gộp thành **một** mục duy nhất liệt kê tên các màn
hình đó, vd: "`[không suy được từ code]` Các màn hình sau chưa có luồng nghiệp vụ ở §5 để
dựng Luồng sự kiện chuẩn: <Màn A>, <Màn B>, …". Lý do: nhãn `[không suy được từ code]` là
nhãn duy nhất tính vào trần `check_section8_cap` (`max(3, M/3)`); một unit có nhiều màn
cùng thiếu luồng §5 mà tạo mỗi màn một mục riêng dễ đẩy tổng số mục §8 vượt trần và
BLOCKING, trong khi ca này (thiếu luồng §5 cho một use case có thật) là ca duy nhất ở §12
vẫn phải xuống §8 — ba field phân loại nghiệp vụ ở trên đã được chặn khỏi §8 hoàn toàn,
nên càng cần gộp ca còn lại để không tự đẩy unit vào chặn cứng.

### 6. Ghi phát hiện đáng chú ý — logic mâu thuẫn / lỗ hổng bảo mật

Trong lúc rút §2–§7, nếu **thấy rõ** một trong hai điều sau, ghi vào §10 — mục **khác
hẳn** §8: không phải "không biết", mà là "đã thấy và thấy có vấn đề":

- **Logic mâu thuẫn**: hai chỗ code xử lý cùng một nghiệp vụ nhưng theo hai quy tắc khác
  nhau, hoặc một ràng buộc tự triệt tiêu chính nó.
- **Dấu hiệu lỗ hổng bảo mật**: thiếu kiểm tra quyền sở hữu trước khi cho sửa/xoá record
  của người khác, mật khẩu/token so sánh hoặc lưu dạng plaintext, endpoint nhạy cảm không
  qua middleware xác thực đáng lẽ phải có, v.v.

**Không chủ động mở rộng phạm vi quét để tìm lỗ hổng một cách hệ thống** — đó là việc của
security review riêng. Chỉ ghi những gì **tình cờ thấy rõ** trong lúc rút đặc tả bình
thường. Mỗi mục phải kèm `file:dòng` và mô tả **cụ thể** vì sao đáng ngờ.

**Trục 1 — đây có phải một vấn đề thật không?** Không rõ ràng (chỉ là cảm giác) → **bỏ
qua, không ghi gì cả**. Không có phát hiện thật nào → ghi "Không có" ở §10.

**Trục 2 — đã chắc là vấn đề thật, nhưng thuộc §8 hay §10?** Mâu thuẫn/thiếu sót **thấy
được trong chính code** → **§10**, không viết lại thành câu hỏi kiểu `[chính sách nghiệp
vụ]` ở §8 để né việc. Thứ **code hoàn toàn không mâu thuẫn, chỉ đơn giản là không biết**
→ §8. **Đã chắc là vấn đề thật nhưng không chắc thuộc §8 hay §10 → coi là §10.**

Mỗi FN **tìm thấy** có tên chứa động từ ghi dữ liệu (Thêm/Sửa/Xoá/Cập nhật/Duyệt/Khoá…)
phải hoặc có một dòng §6 với cite chứng minh có kiểm quyền sở hữu/quyền truy cập, hoặc có
một mục §10 giải trình **nơi đã tra** (middleware/filter/policy nào đã đọc) vì sao không
kiểm được điều đó — thiếu cả hai mà vẫn ghi "Không có" ở §10 là chưa chạy bước này.

### 7. Độ sâu — luôn đầy đủ

Không có mức nông/sâu để chọn — mọi lần chạy đều rút tới:
- §3: đủ bảng field (kiểu, độ dài/miền giá trị, bắt buộc, mặc định), không chỉ tên thực thể.
- §4: đủ từng quy tắc, không chỉ liệt kê tên.
- §9: thông báo hiển thị, lấy **nguyên văn** từ file ngôn ngữ/hằng số/mã lỗi, **hoặc**
  chuỗi literal ngay trong code nếu dự án không tách riêng file ngôn ngữ. Không tìm được
  nguyên văn ở bất kỳ hai nguồn đó → không ghi ở §9, đưa câu hỏi xuống §8.

### 8. Lấy khung, ghi `intel.md`

`specify preset resolve intel-template` → không resolve được → đọc
`.specify/extensions/dft-speckit/templates/intel-template.md` → vẫn không thấy → hỏi.

Thư mục cha của `.specify/docs/<path>` (tức bỏ phần `/intel.md` ở cuối `path`) chưa có →
tạo, gồm mọi cấp cha nếu chưa có (vd `mkdir -p` trên phần thư mục, không phải trên `path`
nguyên vẹn — `path` đã có sẵn `/intel.md` ở cuối, không phải tên thư mục).

**`intel.md` chưa tồn tại** → copy khung, điền theo nội dung đã rút.

**`intel.md` đã tồn tại (chạy lại)** → bước snapshot dưới đây và cờ `--before` ở bước 9
**BẮT BUỘC**, không phải tuỳ chọn — `intel_verify.py` tự nó không biết file đã tồn tại từ
trước hay không (không tự phát hiện thiếu `--before` mà cảnh báo), nên bỏ sót bước này
KHÔNG gây lỗi gì hiển thị — chỉ đơn giản là §8/§10 cũ bị ghi đè mất mà không một cổng nào
bắt được. Không có tín hiệu lỗi để tự phát hiện đã quên: đây là lý do PHẢI làm bước snapshot
này TRƯỚC khi ghi, theo đúng thứ tự dưới, mỗi lần `intel.md` đã tồn tại, không có ngoại lệ.
**Đọc file hiện tại trước, chụp lại nguyên văn
toàn bộ nội dung file**. Trước khi ghi đè, copy nguyên file hiện tại sang một đường dẫn
tạm, đặt tên theo **FN-ID gốc của unit** (đã có sẵn ở bước 1/2, duy nhất tuyệt đối trong
toàn cây — không tự suy slug): `.specify/tmp/intel-before/<FN-ID-gốc>.md` (vd
`.specify/tmp/intel-before/FN-01-02.md`; tạo thư mục `.specify/tmp/intel-before/` nếu
chưa có). Không dùng slug thư mục ở đây: hai unit khác nhánh cây có thể trùng slug cấp lá
(vd `01-a/01-danh-sach` và `02-b/01-danh-sach` cùng ra `danh-sach`), khi chạy song song
hai subagent sẽ ghi đè chồng snapshot của nhau. Dùng đường dẫn tạm đó làm `--before` ở
bước 9 (`intel_verify.py` nhận đường dẫn file trên đĩa, không nhận nội dung inline). Sau
khi `intel_verify.py` pass sạch, có thể xoá file tạm (dọn dẹp, không bắt buộc). Rồi:

- **Header `**Phủ chức năng**`** = **chính xác** danh sách FN-ID lá của unit này (từ bước
  2) — không phải hợp cũ+mới. Trong mô hình cây, danh sách này tất định theo đúng nhánh,
  chỉ đổi nếu cấu trúc cây thay đổi giữa hai lần `fnlist-import` re-import (hiếm).
- **§1**: đúng một dòng cho mỗi FN-ID trong danh sách hiện tại (bước 2), không hơn không
  kém. FN-ID nào có dòng cũ trong file nhưng **không còn** nằm trong danh sách hiện tại
  (dấu hiệu cấu trúc cây đã đổi tại đúng node này) → **xoá dòng đó khỏi §1** (giữ lại sẽ
  bị `intel_verify.py` chặn với lỗi `thua-fn-o-muc-1`), và **báo rõ cho người dùng ở phần
  Kết thúc**: FN-ID nào bị rụng khỏi unit này, nhắc họ tự kiểm nội dung cũ của FN đó có
  cần chuyển sang unit khác không (không tự động di trú).
- **§8, §10**: **chỉ được nối thêm, không được sửa/xoá mục cũ.** Câu hỏi cũ nay đã có
  câu trả lời từ code → **giữ nguyên câu hỏi**, thêm một dòng ngay dưới:
  `— Đã rõ từ code: <file:dòng>`. Cột `Kết luận` ở §10 giữ nguyên giá trị hiện có (dù
  `đang chờ`, `cố ý — …`, hay `bug — …`) — `code-intel` không bao giờ tự sửa cột này.
- Chỉ bổ sung/cập nhật phần rút được mới ở các mục khác **trừ §8 và §10**; không copy
  khung đè lên toàn file.

### 9. Verify

```bash
python .specify/extensions/dft-speckit/scripts/intel_verify.py .specify/docs/<path> \
  --functions .specify/docs/functions.json --root <FN-ID gốc của unit> \
  [--before .specify/tmp/intel-before/<FN-ID-gốc>.md]
```

`<path>` là giá trị `path` từ bước 2 (đã có sẵn hậu tố `/intel.md`) — **không** ghép thêm
`/intel.md` lần nữa.

Mã thoát khác 0 → còn BLOCKING, đọc báo cáo JSON, sửa `intel.md` theo đúng lỗi nêu, chạy
lại `intel_verify.py` cho tới khi sạch. WARNING không chặn nhưng phải đọc và cân nhắc sửa
trước khi báo xong.

### 10. Ghi ngược trạng thái

**Chạy tuần tự** (hoặc chạy đơn 1 unit): gọi `update` ngay sau mỗi unit như mô tả dưới
đây. **Chạy song song**: **không** gọi ở đây — xem hướng dẫn gom về agent cha ở bước 3.

Với mỗi FN-ID **tìm thấy** trong unit mà `status` hiện tại (từ bước 2) **không phải
`srs`** (không lùi trạng thái — đã qua `srs-from-code` thì không đặt lại `intel`):

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=intel [--set FN-01-02=intel ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate, và đổi status là hành vi có
thể lùi lại. FN-ID vốn đã `srs` thì bỏ qua, không đưa vào `--set`.

## Kết thúc

Với mỗi unit, báo: FN đã xử lý (tìm thấy/không tìm thấy), FN-ID bị rụng khỏi §1 nếu có
(bước 8), số mục §8 đang chờ trả lời, số phát hiện §10 (nêu ngắn gọn từng phát hiện),
đường dẫn `intel.md`, và **dán nguyên văn dòng tổng kết `N lỗi chặn, M cảnh báo.`** của
lần chạy `intel_verify.py` **cuối cùng** ở bước 9 — bằng chứng đã thực sự chạy script,
không phải tự thuật lại bằng lời "verify pass sạch". Thiếu dòng này (nhất là ở subagent
chạy song song, không có ai giám sát nó gõ lệnh) là dấu hiệu bước 9 có thể chưa thực sự
chạy. **`M > 0` → liệt kê nguyên văn từng warning ngay tại đây** (không chỉ con số `M`) —
chạy tuần tự thì đây là nhắc lại gọn nội dung đã trình bày ở bước 9; **chạy song song thì
đây là LẦN DUY NHẤT warnings của unit đó tới được người dùng** (dùng đúng nội dung subagent
đã báo cáo lại ở bước 3 — không được chỉ dán số `M` mà bỏ nội dung). Chạy hàng loạt (≥2
unit) thì tổng kết thêm: tổng số unit đã xử lý, danh sách unit lỗi (nếu có subagent nào
BLOCKING mà không tự sửa được).

## Sai lầm thường gặp

- **Grep thẳng tên tiếng Việt vào code rồi kết luận "không tìm thấy" khi rỗng** → tên
  chức năng trong `functions.json` là tiếng Việt, code gần như chắc chắn tiếng Anh. Phải
  qua thang tìm kiếm (tra file ngôn ngữ lấy key trước) trước khi kết luận.
- **Cite một file "gần đúng" cho có, để khỏi phải đánh dấu `(suy đoán)`** → cite phải
  chứa token đỡ trực tiếp khẳng định, không phải một đường dẫn hợp lý nghe qua.
- **Tự gộp hai nhánh không phải anh em vào một unit** khi điều chỉnh cây ở bước 1 → mỗi
  unit luôn ánh xạ đúng một nhánh cây, một thư mục — không được hỗ trợ.
- **Đẩy phần lớn nội dung xuống §8 mà không gắn nhãn, hoặc gắn bừa nhãn không tính vào
  trần để lách** → nhãn `[không suy được từ code]` mới bị tính trần, ba nhãn còn lại là
  lối thoát chính đáng — dùng sai nhãn để né trần là tự lừa chính `intel_verify.py`.
- **Một dòng §2 gánh gần hết `M` FN mà không cite riêng từng FN** → chỉ áp khi `M ≥ 4`.
- **Quên snapshot + truyền `--before` khi `intel.md` đã tồn tại từ trước** → không có gì
  báo lỗi lúc chạy (`intel_verify.py` im lặng bỏ qua no-clobber check khi thiếu `--before`,
  không tự phát hiện file đích đã tồn tại để cảnh báo) — §8/§10 cũ bị ghi đè mất mà cổng
  kiểm vẫn báo "0 lỗi chặn" như thể mọi thứ ổn. Đây là lỗi ÂM THẦM NHẤT trong cả lệnh này:
  luôn coi bước snapshot ở bước 8 là bắt buộc, không phải "làm nếu nhớ".
- **Chạy lại làm rụng câu hỏi §8 hoặc phát hiện §10 của lần trước** → §8/§10 chỉ được
  nối thêm, không sửa/xoá mục cũ — `intel_verify.py --before` bắt được ca này (so nguyên
  văn §8/§10 với bản chụp trước khi ghi), NHƯNG chỉ khi `--before` thật sự được truyền
  (xem mục ngay trên). Ngược lại, §1/header thì KHÔNG áp luật giữ
  nguyên: phải khớp **chính xác** danh sách FN hiện tại của unit (bước 2) — dòng FN đã
  rụng khỏi unit này (cấu trúc cây đổi) phải bị xoá khỏi §1, không phải giữ lại; giữ lại
  sẽ bị `intel_verify.py` chặn với lỗi `thua-fn-o-muc-1`. Rụng dòng nào phải báo rõ ở
  phần Kết thúc.
- **Sửa/xoá câu hỏi §8 vì thấy nó "lỗi thời"** → giữ nguyên câu hỏi, thêm dòng "Đã rõ từ
  code: file:dòng" bên dưới, không viết đè.
- **Dùng ngoặc vuông cho "chưa trả lời" ở §8** (`[để trống...]`) → `intel_verify.py` coi
  đó là placeholder chưa điền, chặn báo xong dù tài liệu hợp lệ. Dùng `_(chưa có)_`.
- **Ghi status `intel` cho FN đã là `srs`** → lùi trạng thái, mất dấu FN đã qua
  `srs-from-code`. Kiểm `status` hiện tại (từ `intel_tree.py units`) trước khi `--set`.
- **Chủ động đi quét toàn bộ codebase tìm lỗ hổng bảo mật** → §10 chỉ ghi thứ tình cờ
  thấy rõ trong lúc rút §2–§7, không phải một security audit.
- **Ghi vào §10 một nghi ngờ mơ hồ không kèm lý do cụ thể** → không đủ căn cứ để người
  dùng phán đoán cố ý hay bug; không rõ ràng thì bỏ qua, không đoán.
- **Bỏ trống §11 cho một màn hình có giao diện thật** → mục lớn nhất của tài liệu giao
  khách (đợt `srs-from-code` sau) sẽ thiếu bảng điều khiển cho màn đó. Không có giao diện
  thật thì phải ghi dòng `không-có-UI` kèm lý do, không phải bỏ trống.
- **Cột `Màn hình` ở §11 không khớp nguyên văn cột `Màn hình / endpoint` ở §2** (gõ khác
  một chữ, viết tắt khác) → đứt liên kết mà đợt sau dựa vào để dựng bảng điều khiển từng
  màn; `intel_verify.py` cảnh báo (WARNING) ca này nhưng không chặn, dễ bị bỏ qua.
- **Không viết khối `###` cho một use case có thật ở §12** → phần đợt `srs-from-code` sau
  dựng kịch bản use case cho màn đó sẽ thiếu hẳn. Chỉ được bỏ khối `###` khi màn
  hình/điểm vào thật sự không có use case nào (endpoint kỹ thuật thuần), không phải vì
  ngại viết hay vì §5 tạm thời chưa có luồng.
- **Field `Màn hình` ở một khối §12 không khớp nguyên văn cột `Màn hình / endpoint` ở
  §2** (gõ khác một chữ, viết tắt khác) → đứt liên kết mà đợt sau dựa vào để nối use case
  với màn hình; `intel_verify.py` cảnh báo (WARNING) ca này nhưng không chặn, dễ bị bỏ qua.
