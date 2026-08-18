---
description: Sinh .specify/docs/<đường-dẫn-cây>/srs.md theo đúng cấu trúc 4 cấp của tài liệu ban hành thật (Nhóm→Chức năng→Sơ đồ/Mục đích/Mô tả chức năng→Màn hình→a.-g.) từ intel.md và functions.json — nhận một FN-ID gốc (trống = toàn dự án), tái dùng intel_tree.py để đề xuất/xác nhận unit rồi sinh SRS theo batch (song song/tuần tự), chỉ ghi nội dung phản ánh đúng những gì code thật sự làm, thông tin hành chính thiếu thì ghi "Chưa có thông tin", và tổng hợp một lượt cuối cùng những phát hiện logic/bảo mật đáng chú ý để hỏi người dùng.
---

# SRS từ code intel theo cây functions.json

Rót `.specify/docs/<đường-dẫn-cây>/intel.md` (tài liệu nội bộ, kèm nguồn `file:dòng`)
thành **`.specify/docs/<đường-dẫn-cây>/srs.md`** — tài liệu **giao khách**, đúng cấu trúc
4 cấp của tài liệu ban hành thật (`Nhóm → Chức năng → Sơ đồ/Mục đích/Mô tả chức năng →
Màn hình → a.-g.`), không lộ đường dẫn mã nguồn. Toàn bộ tiếng Việt. Dùng `python3` nếu
`python` không có.

**Tài liệu này tập trung vào source code** — mô tả đúng những gì hệ thống *thật sự làm*
theo `intel.md`, không phải một bản diễn giải nghiệp vụ suy đoán. Hai loại thông tin xử
lý khác nhau:

- **Thông tin hành chính/nghiệp vụ thuần mà code không thể tiết lộ** (mức quan trọng use
  case, loại UC theo quy ước BA, thời điểm sử dụng, chính sách kinh doanh chỉ người mới
  biết…) → ghi thẳng "Chưa có thông tin" trong tài liệu, không đánh dấu gì đặc biệt,
  không dừng lại hỏi. Cuối báo cáo chỉ nhắc gọn một dòng — bổ sung nếu cần, không phải
  một cuộc trao đổi.
- **Phát hiện đáng chú ý khi đọc code** — logic mâu thuẫn, xung đột giữa các phần code,
  dấu hiệu lỗ hổng bảo mật (đã được `code-intel` ghi vào `intel §10`) → đây mới là thứ
  đáng dừng lại. Tổng hợp **một lượt** ở cuối, hỏi người dùng: cố ý thiết kế vậy hay là
  bug. **Không ghi vào `srs.md`** — tài liệu giao khách không nêu loại phát hiện này.

## User Input

`$ARGUMENTS`

Kỳ vọng: **trống, hoặc một FN-ID** — giống hệt `code-intel`:

- Trống → điểm bắt đầu là **gốc cây** — chọn unit trong toàn bộ dự án.
- `FN-01` → chỉ xét unit trong nhánh đó.
- Một FN-ID lá → đúng một unit (chính nó).

Không còn khái niệm "tên cụm gõ tay" hay "`--template` khách hàng" — thư mục sinh ra tự
động từ cấu trúc `functions.json`, và khuôn `srs.md` mô phỏng đúng MỘT cấu trúc tài liệu
ban hành cố định (không còn khung tuỳ biến theo khách).

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

(Việc xác định "unit mang marker Giao tiếp trong hệ thống" KHÔNG làm ở đây — xem cuối
bước 2, vì danh sách root đã chốt ở bước này còn có thể bị lọc bớt tại bước 2 nếu thiếu
`intel.md`.)

### 2. Tính đường dẫn `srs.md` + kiểm `intel.md` đã có chưa

```bash
python .specify/extensions/dft-speckit/scripts/intel_tree.py units \
  --functions .specify/docs/functions.json --roots <FN-ID,FN-ID,...>
```

Với mỗi unit trả về, `path` là đường dẫn FILE `intel.md` (đã có sẵn hậu tố `/intel.md`),
TƯƠNG ĐỐI so với `.specify/docs/`. Suy đường dẫn `srs.md` của unit bằng cách **thay hậu
tố**: `path.replace("/intel.md", "/srs.md")` — cùng thư mục với `intel.md`, không gọi lại
`intel_tree.py` với tham số khác, không viết logic suy path mới.

Với mỗi unit đã chốt, kiểm sự tồn tại của `.specify/docs/<path unit>` (đường dẫn `intel.md`
thật, `.specify/docs/` + `path`):

- **`intel.md` tồn tại** → đưa vào danh sách **runnable**, tiếp tục.
- **`intel.md` không tồn tại**:
  - **Trước khi kết luận "chưa chạy `code-intel`"**: grep nhanh mọi `§1 Phủ chức năng`
    trong các `intel.md` đã có dưới `.specify/docs/` xem FN-ID nào của unit này đã xuất
    hiện ở MỘT `intel.md` khác (dấu hiệu cây đã xác nhận ở bước 1 lệch với cây đã dùng khi
    chạy `code-intel` trước đó — vd người dùng chốt lại ranh giới unit khác lần trước, rồi
    ở bước 1 của lần chạy này lỡ chấp nhận đề xuất mặc định thay vì ranh giới đã chốt cũ).
    **Có khớp mà tổng số unit đã chốt ở bước 1 là đúng 1** → DỪNG NGAY (giống nhánh 1-unit
    thiếu `intel.md` bên dưới, không tạo `srs.md`), báo rõ FN-ID đó đã có `intel.md` ở
    đường dẫn nào, hỏi người dùng xác nhận lại ranh giới unit ở bước 1 thay vì tự ý coi là
    "thiếu, phải chạy `code-intel`". **Có khớp mà tổng số unit đã chốt ≥ 2** → **KHÔNG**
    dừng cả batch (giữ đúng nguyên tắc skip-and-report của nhánh ≥2-unit bên dưới) — vẫn
    bỏ qua unit đó như bình thường, nhưng ghi rõ trong danh sách "đã bỏ qua" thêm lý do
    "nghi ngờ trùng phạm vi với `<đường-dẫn-intel.md-khác>`" thay vì chỉ "thiếu intel.md",
    để người dùng tự quyết có cần xác nhận lại cây hay không SAU KHI các unit runnable
    khác đã chạy xong. Không khớp gì → đi tiếp hai nhánh dưới như bình thường.
  - Tổng số unit đã chốt ở bước 1 là **đúng 1** → **DỪNG NGAY**, nhắc chạy
    `/speckit.dft-speckit.code-intel <FN-ID gốc của unit>` trước. Không tạo `srs.md`.
  - Tổng số unit đã chốt **≥ 2** → **bỏ qua** unit đó, ghi lại vào danh sách **đã bỏ qua**
    (FN-ID + tên), tiếp tục xét các unit còn lại — không dừng cả batch.

Danh sách **runnable** rỗng sau khi lọc (mọi unit ≥2 đều thiếu `intel.md`) → **DỪNG**,
in toàn bộ danh sách "đã bỏ qua", nhắc chạy `code-intel` trước cho các unit đó.

Ngay sau khi danh sách **runnable** đã chốt ở bước này (không đợi tới bước 5), xác định
**unit mang marker "Giao tiếp trong hệ thống"** — quyết định này chỉ làm MỘT LẦN ở đây,
dùng chung cho mọi bước sau kể cả khi dispatch song song ở bước 3: nếu đây là chạy từ gốc
cây (FN-ID rỗng ở bước User Input) thì unit mang marker là **unit đầu tiên trong danh
sách runnable** (đúng thứ tự, SAU KHI đã lọc bớt unit thiếu `intel.md` ở bước này — không
phải danh sách root đã chốt thô ở bước 1, để marker không bao giờ rơi vào một unit vừa bị
bỏ qua; kể cả khi danh sách runnable chỉ có 1 unit — unit đó mang marker); nếu đây KHÔNG
phải chạy từ gốc cây (một FN-ID/nhánh con cụ thể) thì không unit nào mang marker. Ghi nhớ
FN-ID gốc của unit này (nếu có) để mang xuống bước 3 và bước 5.

### 3. Chạy song song hay tuần tự?

Danh sách **runnable** có **≥ 2 unit** → hỏi qua AskUserQuestion: chạy song song (mỗi
unit một subagent độc lập qua Agent tool) hay tuần tự (xử từng unit một). **Đúng 1 unit
runnable** → chạy thẳng bước 4-11 dưới đây, không hỏi.

Chạy song song: dispatch một Agent riêng cho mỗi unit runnable, giao FN-ID gốc của unit,
đường dẫn `srs.md` đã suy ở bước 2, đường dẫn `intel.md` tương ứng, danh sách FN-ID kèm
status (từ bước 2), cờ **có phải là unit mang marker "Giao tiếp trong hệ thống" hay không**
(đã resolve một lần ở bước 2 — chỉ đúng một subagent trong cả đợt dispatch nhận cờ `có`,
mọi subagent còn lại nhận cờ `không`), và yêu cầu subagent đọc lại chính file lệnh này
(`.specify/extensions/dft-speckit/commands/srs-from-code.md`) rồi thực hiện đúng Bước
4–11 dưới đây cho một unit đó. Không đồng bộ giữa các subagent — hai unit dùng chung một
entity có thể diễn giải khác nhau, chấp nhận là giới hạn đã biết (giống hệt `code-intel`).

Subagent **không tự gọi** `fnlist_import.py update` ở Bước 10 của chính nó. Thay vào đó,
sau khi Bước 9 (verify) pass sạch, subagent **báo cáo lại** cho agent cha danh sách cặp
`FN-ID=srs` VÀ ID `use_cases[]`=srs cần cập nhật (không tự ghi) — đúng cả hai loại ID mà
Bước 10 quy định phải `--set`, không chỉ FN-ID leaf — tránh race: nhiều subagent cùng ghi
đè `functions.json` sẽ làm mất cập nhật của nhau. Agent cha đợi **tất cả** subagent hoàn
tất, gom toàn bộ cặp `FN-ID=srs` và `use_cases[]`=srs từ mọi subagent, rồi gọi
`fnlist_import.py update` **đúng một lần** với đầy đủ các `--set`.

Cùng lúc báo cáo cặp `FN-ID=srs`, subagent **cũng báo cáo lại** — không tự trình bày,
không tự hỏi người dùng — hai thứ nữa:

- Danh sách các dòng `intel §10` đang `đang chờ` của unit mình (mô tả + nguồn `file:dòng`
  + đường dẫn `intel.md`): subagent không có lượt tương tác tiếp theo của riêng nó để
  nhận câu trả lời, nên không thể tự hỏi rồi tự ghi ngược `intel.md` §10 như luồng tuần tự
  làm (xem bước 11 phần 2).
- **Nguyên văn `warnings` (nếu có) từ lần chạy `srs_verify.py` cuối cùng của unit mình**,
  kèm dòng tổng kết `N lỗi chặn, M cảnh báo.` — subagent đã tự soát và xử lý theo bước 9
  (không được im lặng bỏ qua), nhưng **việc trình bày cho người dùng vẫn phải xảy ra**,
  và subagent không có ai để trình bày trực tiếp. Không báo cáo mục này = warnings của
  unit đó biến mất hoàn toàn khỏi mọi báo cáo mà người dùng thấy được.

Agent cha gom các danh sách này từ mọi subagent, gộp vào ĐÚNG MỘT lượt hỏi người dùng ở
cuối (cho §10) và ĐÚNG MỘT phần trình bày warnings gộp theo unit (bước 11 phần 1), rồi tự
ghi ngược
`intel.md` §10 theo từng unit sau khi có câu trả lời.

Chạy tuần tự: lặp qua từng unit runnable, thực hiện Bước 4–11 cho unit đó xong mới sang
unit kế.

### 4. Kiểm `srs.md` đã tồn tại chưa (làm TRƯỚC khi rót/viết/ghi bất cứ gì)

**Chỗ duy nhất trong lệnh này ghi vào `.specify/docs/<đường-dẫn-cây>/srs.md` là bước 8
"Điền khung".** Mục này chỉ đọc và ghi nhớ, không ghi gì cả — nhưng phải làm trước các
bước 5–7, vì luật no-clobber dưới đây phải có trong đầu **trước khi** bước 8 chạm vào
file, không phải đọc ra sau khi đã ghi đè mất bản cũ.

`srs.md` **chưa tồn tại** → không có gì phải giữ, đi tiếp bước 5.

`srs.md` **đã tồn tại** → đọc toàn bộ nội dung hiện tại, ghi nhớ luật sẽ áp ở bước 8:
mọi nội dung người dùng/BA đã sửa tay ở bất kỳ mục nào (kể cả những mục trước đây ghi
"Chưa có thông tin" mà nay đã có nội dung thật) sẽ **giữ nguyên**, chỉ cập nhật mục nào
có nội dung khác đi khi so trực tiếp bản `srs.md` hiện có với `intel.md`/`functions.json`
hiện tại — so theo NỘI DUNG từng khối Chức năng/Màn hình, không có mốc thời gian/hash để
so "đã đổi từ lần chạy trước" một cách trừu tượng. Khuôn mới không còn mục `I.1` lịch sử
thay đổi dạng bảng (bỏ cùng toàn bộ khuôn I-VI) — no-clobber chỉ còn ở mức nội dung, không
còn dòng lịch sử riêng để ghi thêm.

**Mỏ neo tất định trước khi ghi** (như `code-intel` bước 8 đang làm với `intel.md`):
copy nguyên file `srs.md` hiện tại sang một đường dẫn tạm, đặt tên theo **FN-ID gốc của
unit**: `.specify/tmp/srs-before/<FN-ID-gốc>.md` (tạo thư mục nếu chưa có). Dùng đường
dẫn tạm đó làm `--before` ở bước 9 (`srs_verify.py` nhận đường dẫn file trên đĩa, không
nhận nội dung inline) — script đối chiếu để chặn cứng nếu một khối Chức năng có trong
bản trước mà biến mất hoàn toàn khỏi bản mới (dấu hiệu rõ nhất của việc ghi đè nhầm nội
dung BA đã sửa tay, thay vì chỉ cập nhật mục thay đổi theo luật ở trên). Sau khi
`srs_verify.py` pass sạch, có thể xoá file tạm (dọn dẹp, không bắt buộc).

### 5. Rót phần suy được từ intel

Đọc `intel.md` của unit và `functions.json`. Ánh xạ mục — không tự ý đổi hướng, mục nào
trong `intel.md` không có thì mục `srs.md` tương ứng cũng không có gì để rót:

| Nguồn (`intel.md`) | Đích (`srs.md`) |
| --- | --- |
| §1 Phủ chức năng | `<!-- FN: ... -->` dưới mỗi Chức năng |
| §2 Màn hình / điểm vào | xác định MÀN HÌNH THẬT hiện thực từng leaf FN-ID (dùng để lấy nội dung a.-g. rót vào mỗi khối `#####`, xem quy ước leaf-based ở bước 8); câu mở đầu "Mô tả chức năng" |
| §3 Thực thể và trường dữ liệu | rải vào mục `g. Yêu cầu nghiệp vụ` |
| §4 Kiểm tra hợp lệ và quy tắc nghiệp vụ | rải vào mục `g. Yêu cầu nghiệp vụ` |
| §5 Luồng nghiệp vụ | mermaid `sequenceDiagram` ở `###### e. Thiết kế mô hình nghiệp vụ` (chi tiết từng màn hình, có swimlane) — KHÔNG dùng cho `#### Sơ đồ chức năng` (mục đó dựng từ `functions.json`, xem bước 8) |
| §6 Phân quyền | mục `a. Đối tượng tham gia`, `b. Điều kiện thực hiện` |
| §7 Tích hợp ngoài, tác vụ nền, sự kiện | rải vào mục `g. Yêu cầu nghiệp vụ` |
| §9 Thông báo hiển thị | rải vào mục `g. Yêu cầu nghiệp vụ` |
| §11 Điều khiển giao diện | phần BẢNG của mục `f. Thiết kế UX/UI và Mô tả điều khiển` (bảng Tên điều khiển/Mô tả điều khiển, khớp cột `Màn hình` của §11 với màn hình hiện thực leaf đang viết) |
| §12 Kịch bản Use Case | mục `d. Kịch bản trường hợp sử dụng` — **ĐÚNG MỘT bảng cho cả mục** (một khối `#####` = một use case): `Tên Use Case` = tên leaf (tiêu đề khối `#####`), 8 field còn lại là hàng bảng, xem quy ước bảng HTML ở bước 8. Nhiều khối `###` của §12 cùng ứng với leaf này → chúng là các CHỨC NĂNG NHỎ, gộp thành các nhánh `S-1`, `S-2`… trong `Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ` của bảng duy nhất đó, KHÔNG viết thành nhiều bảng. **Chọn đúng khối §12 thuộc leaf đang viết**: khối CÓ comment `<!-- use-case-id: <id> -->` ngay dưới heading (đường A, `code-intel` bước 5 phần A) → chọn theo khoá này, khối thuộc leaf có FN-ID là TIỀN TỐ của `<id>` (vd marker `FN-01-01-UC-01` thuộc leaf `FN-01-01`) — dùng khoá này bất kể `Màn hình` của khối là tên màn hình thật hay câu sentinel "Chưa tìm thấy hiện thực trong mã nguồn." (ca không tìm thấy). Khối KHÔNG có marker (đường B, tự khám phá) → chọn như cũ, khớp `Màn hình` với §2. Field `Màn hình` (khi dùng làm khoá) KHÔNG copy vào `d.` + mục `c. Mô hình Usecase` (mermaid, dựng từ Tên Use Case + Người dùng của §12) |
| §10 Phát hiện logic/bảo mật | **Không rót vào `srs.md`** — chỉ dùng ở bước 11 để hỏi người dùng |

**Ba field `Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng` khi rót sang `d. Kịch bản
trường hợp sử dụng`: rót NGUYÊN VĂN giá trị `intel §12` đã ghi cho use case này** — có
thể là giá trị thật (khi `code-intel` tìm được khớp `use_cases[]` có giá trị Excel cho
field đó) hoặc vẫn "Chưa có thông tin" (khi không khớp được, hoặc `intel §12` sinh theo
đường tự khám phá không có `use_cases[]` nguồn). `srs-from-code` không tự tra
`functions.json` để lấy ba field này — chỉ rót đúng những gì `intel.md` đã ghi, giữ
nguyên ranh giới nội bộ/giao khách hiện có (không tự suy đoán giá trị khác với những gì
`intel §12` đã kết luận).

**Hai mục cấp Nhóm không có nguồn trong `intel.md` — KHÔNG tự sinh, đánh dấu comment ẩn
thay vì lược bỏ âm thầm**: "Sơ đồ các giao thức kết nối giữa các khối" và "Cơ sở dữ liệu"
(mỗi Nhóm), và "Giao tiếp trong hệ thống" (một lần đầu tài liệu, nếu sinh từ gốc cây).
Với mỗi Nhóm, thêm ngay dưới heading Nhóm:

```markdown
<!-- TODO 3B-4: Sơ đồ các giao thức kết nối giữa các khối, Cơ sở dữ liệu — chưa tự sinh, cần đợt sau -->
```

Với "Giao tiếp trong hệ thống" — **chỉ unit đã được xác định ở bước 2 là "unit mang
marker"** (một cờ đã resolve một lần cho cả đợt chạy, cùng cờ được truyền xuống khi
dispatch song song ở bước 3) mới thêm marker; các unit khác trong cùng đợt chạy — kể cả
khi cũng là chạy từ gốc cây, chỉ là không phải unit đầu tiên trong danh sách runnable đã
chốt ở bước 2 — KHÔNG thêm. Khi thêm, thêm ngay ở đầu file `srs.md` vừa sinh, TRƯỚC heading
`## [Tên Nhóm]` đầu tiên:

```markdown
<!-- TODO 3B-4: Giao tiếp trong hệ thống — chưa tự sinh, cần đợt sau -->
```

Sinh từ một unit con (gốc unit không phải gốc thật của cây) → cờ ở bước 2 luôn là "không
mang marker" nên KHÔNG thêm — "Giao tiếp trong hệ thống" chỉ có ý nghĩa một lần cho toàn
tài liệu, không lặp lại theo từng unit từng phần, và trong một đợt chạy root-level nhiều
unit thì cũng chỉ đúng một unit (unit đầu tiên đã chốt) mang marker, không phải mọi unit.

Không tự suy nội dung cho ba mục này từ bất kỳ nguồn nào — không có `§N` nào của
`intel.md` là nguồn hợp lệ cho kiến trúc hệ thống/schema DB.

**Sơ đồ mermaid — ba loại, ba quy ước riêng, đều tuân kỷ luật "không sơ đồ bịa"**:

- **`#### Sơ đồ chức năng`**: KHÔNG phải sơ đồ luồng nghiệp vụ — là CÂY TÊN chức năng con.
  `flowchart TD`, node gốc = tên Chức năng (khối `###` đang viết). Chỉ nối TÊN với TÊN bằng
  mũi tên xuống — không thêm bước xử lý, điều kiện, hay node hình thoi quyết định nào (đó
  là việc của `e.`). **Node con phải PHỦ ĐÚNG những gì `#### Mô tả chức năng` bên dưới thật
  sự có** — một sơ đồ chỉ có mỗi node gốc trơ trọi trong khi phần dưới đặc tả 6 chức năng nhỏ là
  SAI (lỗi đã gặp thật). Lấy node con theo thứ tự ưu tiên:
  1. `functions.json` CÓ node con trong subtree Chức năng này → dùng đúng tên các node đó
     (trường `name`, bỏ dấu gạch đầu dòng `- `/`+ ` và dấu chấm cuối câu), đệ quy đủ số cấp.
  2. `functions.json` KHÔNG có node con (Chức năng chính là một leaf, chỉ sinh đúng một
     khối `#####`) → node con = **tên các CHỨC NĂNG NHỎ, tức các nhánh `S-n` viết ở mục
     `d.`** của khối đó.

  Có cả hai thì vẽ hai cấp: leaf `functions.json` ở cấp 1, chức năng nhỏ (`S-n`) của leaf
  đó ở cấp 2.
  Luôn dựng được (nguồn cục bộ, không phụ thuộc `intel §5`) — không còn case "không có dữ
  liệu, xoá khối mermaid" cho mục này.
- **`###### e. Thiết kế mô hình nghiệp vụ`**: `sequenceDiagram` (KHÔNG phải `flowchart`),
  **ĐÚNG MỘT khối mermaid cho cả mục** — nhiều chức năng nhỏ KHÔNG được tách thành nhiều
  khối mermaid liên tiếp (mỗi khối lặp lại nguyên si danh sách participant, nhìn thành
  nhiều sơ đồ rời rạc; lỗi đã gặp thật). Khai `actor`/`participant` MỘT LẦN ở đầu, rồi
  **mỗi CHỨC NĂNG NHỎ (nhánh `S-n` ở mục `d.`) bọc trong một khối `rect` có
  `Note over <actor>,<participant cuối>: <Tên chức năng nhỏ>`** làm nhãn (nhãn phải TRÙNG
  tên nhánh `S-n` tương ứng) — chính là các khung chữ nhật phân tách của tài liệu ban hành thật. Mô phỏng UML
  sequence diagram có swimlane: `actor` cho vai trò người dùng thực hiện, `participant` cho
  từng thành phần xử lý bước. Participant lấy đúng tên thành phần `§5` đã nêu cho luồng này
  (vd Web UI/Backend/Database/dịch vụ ngoài…); `§5` không nêu tên thành phần nào cho bước đó
  thì được tự suy hợp lý theo đúng bước xử lý `§5` đã mô tả (không bịa thêm thành phần `§5`
  không hề nhắc tới ở bất kỳ đâu trong luồng). Nhánh điều kiện (§5 ghi "nếu…"/"trường
  hợp…") thể hiện bằng `alt`/`else` **bên trong `rect` của chức năng nhỏ tương ứng**. `§5` không
  có luồng nào cho leaf này → xoá cả khối mermaid. Nhánh `S-n` mà §12 ghi `Luồng sự kiện
  chuẩn`/`Luồng sự kiện nhỏ` là "Chưa tìm thấy hiện thực trong mã nguồn." (đường A không
  tìm thấy, hoặc not-found cục bộ hai field flow — xem `code-intel.md` bước 5 phần A) →
  **bỏ qua nhánh đó, không vẽ `rect`** cho nó — không có luồng thật nào để mô phỏng.
- **`###### c. Mô hình Usecase`**: mermaid không có UML use-case native — mô phỏng bằng
  `flowchart` (actor = node chữ nhật `A([Tên actor])`, use case = node oval
  `UC([Tên Use Case])`, cạnh nối actor→use case). Dữ liệu từ `intel §12` (trường
  `Người dùng` → actor, `Tên Use Case` → use case). `§12` không có khối `###` nào ứng với
  màn hình hiện thực leaf này → xoá cả khối mermaid. Khối §12 mà `Màn hình` (hoặc `Người
  dùng`) ghi nguyên văn "Chưa tìm thấy hiện thực trong mã nguồn." (đường A không tìm thấy)
  → **bỏ qua khối đó, không vẽ actor/use case cho nó** — không vẽ một actor tên là câu
  sentinel đó.

**`###### f. Thiết kế UX/UI và Mô tả điều khiển`**: MỘT mục gộp, **CHIA THEO TỪNG USE
NĂNG NHỎ**. Mỗi nhánh `S-n` ở mục `d.` là một đầu mục lớn `**[Tên chức năng nhỏ]**` ở đây
(cùng tên, cùng thứ tự, đúng bằng số nhánh `S-n` ở `d.`), bên dưới nó theo đúng thứ tự:
(1) placeholder ảnh của các màn liên quan RIÊNG chức năng nhỏ đó — luôn ghi cố định
`_(cần chèn ảnh — không tự sinh)_`, không bao giờ tự vẽ mockup hay mô tả bố cục
(`intel.md` không quét bố cục UI); (2) ngay dưới là bảng điều khiển RIÊNG của chức năng
nhỏ đó (rót từ `intel §11`, quy ước cột xem bước 6).

**TUYỆT ĐỐI KHÔNG gộp điều khiển của mọi chức năng nhỏ vào MỘT bảng duy nhất** — lỗi đã gặp
thật: một bảng 30 dòng trộn lẫn điều khiển của tạo mới, sửa, khoá, chuyển đơn vị, không
tra được điều khiển nào thuộc thao tác nào. Điều khiển dùng chung cho nhiều chức năng nhỏ
(vd nút "Hủy" của mọi hộp thoại) thì LẶP LẠI ở từng chỗ dùng nó, không tách thành một
bảng "dùng chung" riêng. Leaf không có nhánh `S-n` nào (use case một luồng thẳng) → KHÔNG
chia đầu mục, chỉ một ảnh + một bảng.

**Cố ý lệch docx ban hành** (docx tách thành hai mục `f.`/`g.` riêng): tách rời thì người
đọc phải xem hết ảnh màn của mọi chức năng nhỏ rồi mới tới bảng điều khiển — gộp lại để ảnh
và bảng của cùng một chức năng nhỏ nằm cạnh nhau. Vì vậy `Yêu cầu nghiệp vụ` mang chữ `g.` (chứ
không phải `h.`), tổng cộng BẢY mục `a.`-`g.`, không phải tám.

### 6. Chuyển hoá bắt buộc khi rót

> `intel.md` là tài liệu nội bộ, `srs.md` giao khách. Khi rót sang: **bỏ hết
> `file:dòng`, tên class, tên hàm, đường dẫn mã nguồn**. Nội dung mang dấu `(suy đoán)` ở
> intel vẫn phản ánh đúng thứ code làm (đó là suy luận có căn cứ, chỉ chưa chắc 100%) —
> rót bình thường vào `srs.md`, không cần đánh dấu gì thêm (tài liệu này không phải chỗ
> để lộ mức độ tự tin nội bộ).

`intel §9` không có nguyên văn thông báo (câu hỏi đã bị đưa xuống `intel §8` vì không tìm
được nguồn) → mục `g. Yêu cầu nghiệp vụ` viết mô tả **ý nghĩa** của thông báo dựa trên
`intel §5`/`§4` (hành vi hệ thống khi tình huống đó xảy ra), không bịa nguyên văn giả.

Văn phong rót giữ nguyên toàn bộ quy ước đã chốt ở spec đợt 3B-1 §6:

- **`Mục đích chức năng`**: đúng 1 câu, văn phong Hán-Việt trang trọng, nêu giá trị/lý do
  nghiệp vụ ("giúp...", "nhằm...", "đảm bảo..."), không mô tả thao tác.
- **`a. Đối tượng tham gia` / `b. Điều kiện thực hiện`**: dòng gạch đầu dòng (`- `), đúng
  như tài liệu ban hành thật — kể cả khi chỉ có một dòng duy nhất liệt kê nhiều vai trò
  cách nhau bằng dấu phẩy (không tách thành nhiều bullet khi các vai trò đó cùng áp dụng
  một điều kiện/quyền như nhau).
- **`d. Kịch bản trường hợp sử dụng`**: cả 9 field nằm trong MỘT bảng HTML thô (`<table>`,
  không phải cú pháp `|...|` — xem khung mẫu ở `srs-template.md`), 4 field đầu là bảng 2
  cột thật (`<td>` không `colspan`), 5 field còn lại mỗi field một hàng `colspan="2"`.
  Nhãn field bọc `<b>...</b>`. TUYỆT ĐỐI không để dòng trống bên trong khối
  `<table>...</table>`, một dòng trống ở giữa làm nhiều bộ render coi khối HTML đã kết
  thúc và phần còn lại biến thành văn bản thô ngoài bảng.
  `Mô tả tóm tắt` là một đoạn văn liền mạch tóm toàn luồng bằng các mệnh đề nối dấu phẩy.
  `Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ` dùng LIST HTML LỒNG NHAU thật (`<ol>`/`<li>`,
  `<div style="margin-left:1.5em">`) — KHÔNG nối phẳng bằng `<br>`, mất hết thụt lề khi
  xuất Word, đọc rối như một khối văn bản dẹt. `Luồng sự kiện chuẩn` đánh số bước bằng
  `<li>` (`1.`, `2.`…, tự động theo `<ol>`, không gõ tay số thứ tự); nhánh rẽ trong bước
  đánh `S-1:`, `S-2:`… gọi tên bằng cụm trong ngoặc kép, thụt lề lồng NGAY TRONG `<li>` của
  bước phát sinh nhánh đó (`<div style="margin-left:1.5em">S-1: "..."</div>` bên trong
  `<li>`). `Luồng sự kiện nhỏ` khai triển lại đúng các nhãn `S-n` đó theo thứ tự, mỗi `S-n`
  một khối `<div style="margin-left:1.5em">` riêng chứa dòng nhãn + một `<ol>` các bước con
  của nhánh đó — xem đúng cấu trúc mẫu ở `srs-template.md`.
  > **Rủi ro chưa kiểm chứng thực nghiệm**: lý do chọn HTML thô (thay vì `|...|`/`<br>`) là
  > để giữ colspan/thụt lề khi xuất sang Word — nhưng máy dựng khuôn này KHÔNG cài `pandoc`
  > để chạy thử thật `pandoc srs.md -o srs.docx`. Nếu người/công cụ nào đó sau này xuất
  > `srs.md` sang `.docx` bằng pandoc, HTML thô có rủi ro bị đưa vào dưới dạng `RawBlock`
  > mà docx writer không xử lý (bỏ im lặng, không báo lỗi) — khi đó cả mục `d.` biến mất
  > khỏi bản Word mà cổng kiểm ở đây (chỉ soát `srs.md`, không soát output Word) không biết.
  > Trước khi giao bản Word đầu tiên dựng từ khuôn này: chạy thử một lần thật, xác nhận `d.`
  > còn nguyên trong `.docx`; nếu không, quay lại dùng bảng markdown thuần (mất `colspan`
  > nhưng chắc chắn không bị bỏ) cho tới khi có đường xuất khác xử lý được HTML thô.
- **Bảng điều khiển trong `f. Thiết kế UX/UI và Mô tả điều khiển`**: MỖI chức năng nhỏ một
  bảng riêng, đặt NGAY DƯỚI placeholder ảnh của chính chức năng nhỏ đó (không tách heading
  `######` riêng — đầu mục chỉ là dòng in đậm `**[Tên chức năng nhỏ]**`). Cột `Tên điều khiển` viết dạng
  `**[Loại] "[nhãn hiển thị đúng nguyên văn trên UI]"**` — IN ĐẬM cả ô (`**...**`), đúng
  như tài liệu ban hành thật. Cột `Mô tả điều khiển` giữ văn xuôi thường (không in đậm),
  2-3 câu tách dòng riêng theo thứ tự: (1) hình thức + vị trí hiển thị, (2) ràng buộc ngắn
  gọn nếu có (câu độc lập "Trường bắt buộc."), (3) hành vi/mục đích khi tương tác.
- **`g. Yêu cầu nghiệp vụ`**: CÓ quy tắc thật → danh sách gạch đầu dòng (`- `), MỖI quy
  tắc/ràng buộc một dòng riêng — không gộp nhiều quy tắc thành đoạn văn nhiều câu. Mỗi
  dòng vẫn là câu ghép "Khi người dùng [hành động], hệ thống [phản ứng], đồng thời [phản
  ứng phụ]" hoặc "nếu… thì…, ngược lại…" — nêu rõ điều kiện kích hoạt trước kết quả. Quy
  tắc nào có nhiều nhánh con liên quan chặt (cùng một điều kiện gốc) mới gộp chung một
  dòng; các quy tắc độc lập nhau tách dòng riêng.

  **CHỈ GHI QUY TẮC QUAN TRỌNG — đây là nơi chốt nghiệp vụ, KHÔNG phải bản kê mọi thứ code
  làm.** Tiêu chí giữ: quy tắc mà người đọc KHÔNG suy ra được từ quy ước phần mềm thông
  thường, sai thì có hậu quả nghiệp vụ thật. Nhắm **5-12 dòng mỗi khối leaf**; vượt xa
  ngưỡng đó gần như chắc chắn đang liệt kê thứ đáng bỏ (bản đã gặp thật: 38 dòng, quá nửa
  là ràng buộc validate từng trường và nguyên văn thông báo).
  - **BỎ** (đã có chỗ khác, hoặc hiển nhiên với mọi phần mềm): ràng buộc định dạng/độ dài
    từng trường (tối đa N ký tự, đúng định dạng email/số điện thoại, mật khẩu có chữ hoa/
    số/ký tự đặc biệt) và "trường bắt buộc" — **đã nằm ở cột `Mô tả điều khiển` mục `f.`**,
    ghi lại ở đây là trùng lặp; nguyên văn câu thông báo lỗi/thành công; hành vi CRUD/UI
    thông thường (đóng hộp thoại sau khi lưu, tải lại danh sách, khoá nút khi đang gửi,
    phân trang/sắp xếp mặc định, độ trễ gõ phím, loại bản ghi đã xoá khỏi truy vấn, ghi
    nhật ký thao tác).
  - **GIỮ**: quy tắc duy nhất/trùng lặp và phạm vi áp dụng; phân quyền và phạm vi dữ liệu
    (ai được thấy/thao tác cái gì); vòng đời trạng thái và điều kiện chuyển trạng thái;
    ràng buộc liên trường/liên thực thể, quy tắc tính toán; giao dịch/hoàn tác và tính
    nhất quán giữa các hệ thống; hành vi TRÁI quy ước thông thường.
  - **Phân vân thuộc loại nào → GIỮ.** KHÔNG được dùng cớ "hiển nhiên" để bỏ quy tắc có
    ngưỡng/con số nghiệp vụ, quy tắc phân quyền, hay quy tắc trạng thái — ba loại này luôn
    ở lại dù trông đơn giản. Rút gọn ở đây là bỏ thứ TRÙNG hoặc thứ mọi phần mềm đều làm,
    KHÔNG phải bỏ bớt cho ngắn.

  **KHÔNG có gì để ghi → giữ PLAIN SENTENCE,
  KHÔNG thêm `- `** — viết đúng nguyên văn "Chưa có thông tin." hoặc (ca chưa tìm thấy
  code) "Chưa tìm thấy hiện thực trong mã nguồn." như quy định ở bước 8, giống mọi mục
  a.-g. khác. `srs_verify.py` nhận diện mục rỗng bằng khớp NGUYÊN VĂN hai câu này (không
  có `- ` ở đầu) — thêm dấu gạch đầu dòng vào câu rỗng làm cổng kiểm `chuc-nang-rong-ruot`
  không nhận ra được nữa, một Chức năng thật sự rỗng ruột sẽ lọt qua cổng BLOCKING.
- Chủ ngữ nhất quán: "Hệ thống" khi mô tả xử lý phía sau, "Người dùng" khi mô tả thao
  tác. Không lẫn thuật ngữ code/kỹ thuật vào các mục này.

### 7. Điền phần còn lại — chỉ ghi thứ chắc chắn

Không dùng AskUserQuestion ở bước này.

- **Mọi câu chưa có trả lời ở `intel §8`** (chính sách nghiệp vụ thuần, không phải phát
  hiện logic/bảo mật của §10): không chèn vào `srs.md`. Gom lại, đưa vào mục "Thông tin
  còn thiếu" ở báo cáo cuối bước 11 — một dòng mỗi câu, ngắn gọn.
- Nội dung mô tả hệ thống viết từ dữ kiện `intel.md`/`functions.json` sẵn có, phản ánh
  đúng những gì code làm — không tự thêm diễn giải "giá trị nghiệp vụ" khi không có căn
  cứ, nêu đúng những gì hệ thống làm, không suy luận vì sao nó làm vậy.

### 8. Điền khung — đánh số theo vị trí, ghi FN comment

**Trước khi viết bất kỳ nội dung nào**: `specify preset resolve srs-template` → không
resolve được → đọc `.specify/extensions/dft-speckit/templates/srs-template.md` → vẫn
không thấy → hỏi. Đây là khung mẫu MỘT Nhóm/MỘT Chức năng duy nhất — dùng để lấy đúng
chuỗi heading cố định (`#### Sơ đồ chức năng`/`Mục đích chức năng`/`Mô tả chức năng`,
`###### a.`-`g.`, format `<!-- FN: ... -->`) rồi lặp lại cấu trúc đó cho mọi Nhóm/Chức
năng thật của unit — **không tự nhớ lại từ mô tả bằng lời ở các bước trên**, dù mô tả đã
khá đầy đủ: `srs_verify.py` so khớp tên heading CHÍNH XÁC theo chuỗi cố định (kể cả dấu
câu, khoảng trắng), sai một ký tự sẽ làm cổng kiểm cấu trúc (bước 9) im lặng không chạy
được cho Chức năng đó, không báo lỗi gì — đọc thẳng từ khung mẫu tránh rủi ro gõ lại sai.

Đây là bước duy nhất ghi vào `srs.md`. Áp đúng luật no-clobber đã ghi nhớ ở bước 4 nếu
file đã tồn tại từ trước.

- **Đánh số theo VỊ TRÍ XUẤT HIỆN khi ghi** — Nhóm đầu tiên là `1.`, Chức năng đầu tiên
  trong Nhóm là `<số Nhóm>.1`, khối leaf đầu tiên là `<số Chức năng>.3.1` (vì `Mô tả chức
  năng` luôn là mục `####` thứ ba), tiếp tục tăng dần. Chữ cái `a.`-`g.` LUÔN cố định thứ
  tự (không phụ thuộc vị trí, đây là 7 mục có tên riêng, không phải danh sách đếm). Không
  lưu số cố định giữa các lần chạy — chạy lại tự tính lại theo cấu trúc hiện tại, giống
  cách `intel_tree.py`'s `compute_paths()` đánh số thư mục theo vị trí trong `children`.
- **BỐN cấp `##` → `#####` đều nhận tiền tố số phân cấp**, đúng như tài liệu ban hành thật
  (docx: `3.1.3. Mô tả chức năng` → `3.1.3.1. Trang thông tin cá nhân`):

  | Cấp | Ví dụ | Nguồn số |
  | --- | --- | --- |
  | `##` Nhóm | `## 1. [Tên Nhóm]` | vị trí Nhóm trong tài liệu |
  | `###` Chức năng | `### 1.1. [Tên Chức năng]` | vị trí trong Nhóm |
  | `####` ba mục cố định | `#### 1.1.1. Sơ đồ chức năng`, `1.1.2. Mục đích chức năng`, `1.1.3. Mô tả chức năng` | luôn theo thứ tự cố định 1/2/3 |
  | `#####` khối leaf | `##### 1.1.3.1. [Tên leaf]` | vị trí trong `Mô tả chức năng` |

  **Riêng bảy mục `###### a.`-`g.` KHÔNG BAO GIỜ nhận tiền tố số** — chữ `a.`-`g.` đã là
  "số" cố định riêng của chúng, thêm số vị trí vào nữa là sai.

  Tên mục sau tiền tố số phải giữ NGUYÊN VĂN (`Sơ đồ chức năng`, `Mục đích chức năng`,
  `Mô tả chức năng`, `a. Đối tượng tham gia`…) — `srs_verify.py` bóc tiền tố số rồi so khớp
  CHÍNH XÁC phần tên còn lại để chạy các cổng kiểm cấu trúc; đổi tên mục là tắt cổng.
- **`##### Tên leaf function list` LUÔN có mặt — một khối cho MỖI leaf FN-ID trong TOÀN BỘ
  subtree `functions.json` của Chức năng đang viết, bất kể sâu mấy cấp** (KHÔNG chỉ con
  trực tiếp — một Chức năng có cháu/chắt vẫn phải sinh khối cho từng leaf ở đáy cây, không
  dừng ở cấp nhóm-con trung gian), đối chiếu trực tiếp `functions.json` (không còn nhóm
  theo màn hình, không còn điều kiện ≥2 màn hình). Với mỗi leaf:
  - **Tiêu đề** = trường `name` của leaf trong `functions.json`, bỏ dấu gạch đầu dòng
    `- `/`+ ` và dấu chấm cuối câu — KHÔNG đưa mã FN-ID vào tiêu đề (tài liệu giao khách
    không lộ mã nội bộ).
  - **Ngay dưới heading, thêm comment ẩn `<!-- FN-leaf: <FN-ID của leaf này> -->`** — chỉ
    phục vụ đối chiếu/công cụ, không hiện khi xem markdown/xuất Word. Đây là marker RIÊNG
    (khác `<!-- FN: ... -->` ở heading Chức năng — hai marker không thay thế nhau, viết cả
    hai). **Đây là cổng BLOCKING** (`srs_verify.py`'s `check_leaf_blocks`, bước 9): tập
    FN-leaf của mọi khối `#####` trong một Chức năng phải khớp CHÍNH XÁC (không thiếu,
    không thừa, không trùng) với tập FN-ID trong `<!-- FN: ... -->` của chính Chức năng đó
    — thiếu một khối, thiếu một comment, hay trùng comment giữa hai khối đều bị chặn.
  - **Nội dung `a.`-`g.` bên dưới lấy từ MÀN HÌNH THẬT hiện thực leaf này** (xác định qua
    `intel §2`/`§11`/`§12`). Hai leaf khác nhau cùng chung một màn hình → LẶP NGUYÊN VẸN
    toàn bộ `a.`-`g.` (kể cả bảng điều khiển trong `f.`, mọi bảng UC ở `d.`) ở cả hai khối `#####` — không
    cắt gọn nội dung theo riêng từng leaf, chấp nhận trùng lặp để đối chiếu 1-1 với function
    list cho dễ.
  - **Leaf không ánh xạ được sang màn hình riêng nào** (hành động đó chỉ là một nút/thao
    tác nằm trên màn hình của leaf khác, không có `intel §2` riêng) → lấy nội dung a.-g.
    của màn hình chứa hành động đó, nêu rõ ở mục `b. Điều kiện thực hiện` rằng đây là một
    thao tác trong màn hình đó (không bịa một màn hình riêng không tồn tại).
  - **Leaf ứng với dòng §2 có `Loại = không-có-UI` ở `§11`** (endpoint REST thuần, job nền,
    CLI, message consumer — không có giao diện thật) vẫn tạo khối `#####` riêng như bình
    thường (mọi leaf đều có khối, không có ngoại lệ) — chỉ khác là mục
    `f. Thiết kế UX/UI và Mô tả điều khiển` của khối đó ghi "Chưa có thông tin" (không có
    UI để mô tả — bỏ luôn cả placeholder ảnh lẫn bảng điều khiển),
    các mục còn lại vẫn rót đúng nội dung nghiệp vụ tìm được.
- **`<!-- FN: FN-ID, FN-ID... -->` ngay dưới heading Chức năng** — liệt kê MỌI FN-ID lá mà
  Chức năng đó phủ (lấy từ `intel §1`, đối chiếu `intel §2` xem FN nào gắn với màn hình
  nào thuộc Chức năng này). Đây là cổng BLOCKING duy nhất còn lại (thay ma trận truy vết
  cũ) — thiếu một FN trong comment này là tài liệu chưa xong, `srs_verify.py` ở bước 9 sẽ
  chặn.
- **Mọi Nhóm/Chức năng phải có mặt trong `srs.md`** — không được lược bỏ Chức năng nào chỉ
  vì nội dung ít; Chức năng chưa tìm thấy code (`intel §1` ghi "không tìm thấy") vẫn viết
  một khối Chức năng, KHÔNG có khái niệm "Ngoài phạm vi" nào để bỏ qua hẳn Chức năng đó
  (khuôn docx không có mục dạng ma trận truy vết để khai "Ngoài phạm vi" nữa — mọi FN
  trong phạm vi đều phải xuất hiện trong `<!-- FN: ... -->` của MỘT Chức năng nào đó, dù
  nội dung còn sơ sài).
  - **Ca "chưa tìm thấy code" viết KHÁC ca "có code nhưng thiếu thông tin hành chính".**
    Mục `g. Yêu cầu nghiệp vụ` của Chức năng chưa tìm thấy code ghi đúng nguyên văn
    `Chưa tìm thấy hiện thực trong mã nguồn.` — KHÔNG dùng "Chưa có thông tin" cho ca
    này (hai câu mang nghĩa khác nhau: một câu là "có code, chỉ thiếu thông tin hành
    chính không suy được", câu kia là "không có bằng chứng nào cho thấy FN này đã hiện
    thực"). Các mục a.-g. còn lại vẫn ghi "Chưa có thông tin" như bình thường. Đây không
    chỉ là quy ước hành văn: `srs_verify.py` bước 9 chặn (BLOCKING) một Chức năng mà TẤT
    CẢ mục a.-g. đều rỗng/"Chưa có thông tin" (comment FN đủ không có nghĩa tài liệu có
    nội dung) — câu "Chưa tìm thấy hiện thực trong mã nguồn." ở mục `g.` là bằng chứng có
    thật (khớp `intel §1`) khiến Chức năng đó KHÔNG bị tính là rỗng ruột, trong khi vẫn
    trung thực rằng không có gì để đặc tả.

### 9. Cổng cuối — chạy trước khi báo xong

```bash
python .specify/extensions/dft-speckit/scripts/srs_verify.py \
  .specify/docs/<đường-dẫn-cây>/srs.md \
  --functions .specify/docs/functions.json \
  --root <FN-ID gốc của unit> \
  [--before .specify/tmp/srs-before/<FN-ID-gốc>.md]
```

`--before` chỉ truyền khi `srs.md` đã tồn tại từ trước (bước 4 đã snapshot) — unit lần đầu
sinh `srs.md` thì không có gì để so, bỏ cờ này. Đọc JSON trả về, có hai khoá `blocking` và
`warnings`.

- **`blocking` khác rỗng (mã thoát ≠ 0) → cấm báo xong.** Với mục có `goi_y` (`thieu-fn`,
  `placeholder`, `chuc-nang-rong-ruot`, `khoi-leaf-rong-ruot`, `mat-chuc-nang`,
  `thieu-fn-leaf`, `trung-fn-leaf`, `thieu-khoi-leaf`, `fn-leaf-la`, `html-bang-hong`,
  `nhieu-use-case-mot-leaf`), sửa theo đúng gợi ý đó.
  `nhieu-use-case-mot-leaf` nghĩa là mục `d.` của một khối `#####` có nhiều hơn một bảng
  use case — gộp lại thành MỘT bảng (tên use case = tên leaf), các use case thừa chuyển
  thành nhánh `S-n` trong `Luồng sự kiện chuẩn`/`Luồng sự kiện nhỏ`, rồi chỉnh `e.`/`f.`
  chia theo đúng các nhánh `S-n` đó. KHÔNG được xoá bớt nội dung use case để qua cổng.
  Bốn `loai` `thieu-fn-leaf`/`trung-fn-leaf`/`thieu-khoi-leaf`/
  `fn-leaf-la` đều thuộc gate `check_leaf_blocks` (ràng buộc mỗi khối `#####` ↔ đúng một
  leaf FN-ID, xem bước 8) — sửa bằng cách thêm/sửa comment `<!-- FN-leaf: ... -->` hoặc
  thêm khối `#####` còn thiếu, KHÔNG được xoá bớt leaf khỏi `<!-- FN: ... -->` để né gate.
  `khoi-leaf-rong-ruot` giống `chuc-nang-rong-ruot` nhưng soát RIÊNG từng khối `#####` (một
  khối cụ thể rỗng dù Chức năng cha đã "sạch" nhờ khối khác) — ba cách sửa dưới đây cho
  `chuc-nang-rong-ruot` áp y hệt cho khối bị `khoi-leaf-rong-ruot`, chỉ khác phạm vi (một
  khối, không phải cả Chức năng). `html-bang-hong` nghĩa là khối `<table>` ở mục `d.` có
  dòng trống bên trong, thẻ mở/đóng lệch cặp, hoặc `<table>`/`</table>` không khớp số lượng
  trong toàn văn bản — sửa lại đúng cú pháp HTML, không xoá bảng để né cảnh báo.
  `thieu-fn` nghĩa là một FN-ID chưa xuất hiện trong bất kỳ `<!-- FN: ... -->` nào — kiểm
  lại khối Chức năng tương ứng đã có comment đúng chưa, không phải "thêm một dòng ma trận
  cho có" như khuôn cũ (khuôn này không còn ma trận). `chuc-nang-rong-ruot` nghĩa là một
  Chức năng có `<!-- FN: ... -->` đủ nhưng cả 7 mục a.-g. đều rỗng/"Chưa có thông tin" —
  **ba ca khác nhau, ba cách sửa khác nhau**: (1) FN chưa tìm thấy code (`intel §1` ghi
  "không tìm thấy") → sửa mục `g.` thành đúng câu `Chưa tìm thấy hiện thực trong mã
  nguồn.` (bước 8 đã quy định — câu này KHÔNG bị tính là rỗng); (2) FN đã tìm thấy code
  nhưng mọi thứ `intel.md` ghi được về Chức năng này chỉ nằm ở `§8` (câu hỏi chính sách
  nghiệp vụ, KHÔNG được rót vào `srs.md` theo luật bước 7) → mục `g.` viết một câu THẬT
  mô tả những gì code làm được xác nhận (vd tên hành động, đối tượng tác động — lấy từ
  `intel §2`/tên Chức năng, không cần đợi §8 trả lời để có câu này), không để cả 8 mục
  trống chỉ vì phần SÂU HƠN của nghiệp vụ chưa rõ; (3) không thuộc ca 1 hay 2 → quay lại
  bước 5-6 rót thật, không phải một FN nào cũng "hợp lệ" chỉ vì có comment. Không được
  dùng câu `Chưa tìm thấy hiện thực trong mã nguồn.` cho ca 2 — FN đó rõ ràng có code, câu
  này sẽ sai sự thật. `mat-chuc-nang` (chỉ xuất hiện khi có `--before`) nghĩa
  là không FN-ID nào của một Chức năng ở bản trước còn được phủ ở bản mới (đổi tên/đổi số
  thứ tự vị trí là bình thường, không bị tính là mất) — kiểm lại có ghi đè nhầm nội dung
  đã sửa tay không, không được tự ý xoá hẳn một FN khỏi mọi Chức năng. Sửa xong, **chạy
  lại script** — không tự cho là đã sửa đúng mà không xác nhận lại bằng cách chạy thật.
- **`warnings` khác rỗng (mã thoát vẫn 0) → không phải lỗi, nhưng phải trình bày NGAY
  TẠI ĐÂY cho người dùng**, trước khi làm bước 10. `chuc-nang-thieu-muc`/`man-hinh-thieu-
  muc` nghĩa là một Chức năng/Màn hình thiếu heading con bắt buộc — xem lại có phải bỏ sót
  thật hay chỉ là nội dung để trống hợp lệ (vd không có luồng §12 cho mermaid `c.`).
  `yeu-cau-nghiep-vu-dai` nghĩa là mục `g.` của một khối leaf vượt ngưỡng mềm 15 gạch đầu
  dòng — soát lại theo đúng danh sách BỎ/GIỮ ở bước 6 (bỏ ràng buộc định dạng từng trường,
  nguyên văn thông báo, hành vi CRUD/UI thông thường; giữ nguyên quy tắc phân quyền/trạng
  thái/ngưỡng nghiệp vụ). Chức năng phức tạp thật sự vượt ngưỡng là hợp lệ — nhưng phải nêu
  rõ đã soát và vì sao giữ, không được im lặng bỏ qua.
  `nghi-duong-dan-code` có thể là báo nhầm (tên file nghiệp vụ hợp lệ trong mô tả); chọn
  "đây là báo nhầm" thì phải nêu đích danh từng chuỗi + lý do cụ thể. Không được im lặng
  bỏ qua bất kỳ warning nào.
  - **`muc-rong` là loại DỄ SỐT RUỘT gộp chung nhất** — bước 5/6 chủ ý cho phép để trống
    `###### c. Mô hình Usecase`, `###### e. Thiết kế mô hình nghiệp vụ` khi không có nguồn
    (§12/§5 không có dữ liệu). **`#### Sơ đồ chức năng` KHÔNG còn nằm trong danh sách được
    phép trống** — mục này dựng từ `functions.json` (luôn có dữ liệu), nên `muc-rong` ở
    mục này LÀ lỗi thật, phải sửa chứ không được xếp vào nhóm "đã lường trước". Một unit
    sạch vẫn có thể ra vài `muc-rong` "đã lường trước" — **tối đa 2 mục CHO MỖI khối
    `#####`** (đúng `c.` và `e.` của khối đó, do thiếu nguồn), KHÔNG PHẢI hằng số "2 mục"
    cho cả tài liệu: một Chức năng có N khối `#####` thiếu nguồn có thể ra tới 2×N
    `muc-rong` hợp lệ — đếm theo số khối, không phải một con số cố định. **Không được vì
    vậy mà lướt qua CẢ danh sách warnings** — tách riêng: liệt kê các `muc-rong` đã lường
    trước (đúng `c.`/`e.` của từng khối, do thiếu nguồn) thành MỘT dòng gộp, rồi soát TỪNG
    warning còn lại (mọi `muc-rong` khác — bao gồm bất kỳ `muc-rong` nào ở `#### Sơ đồ chức
    năng` — mọi `chuc-nang-thieu-muc`/`man-hinh-thieu-muc`/`nghi-duong-dan-code`) như bình
    thường — không được gộp cả nhóm "còn lại" vào lý do của các mục đã lường trước.

### 10. Ghi ngược trạng thái

**Chạy tuần tự** (hoặc chạy đơn 1 unit runnable): gọi `update` ngay sau mỗi unit, sau khi
đã trình bày xong `warnings` ở bước 9 — không cập nhật trạng thái trước khi người dùng có
cơ hội thấy những gì còn cần soát. **Chạy song song**: **không** gọi ở đây — xem hướng
dẫn gom về agent cha ở bước 3.

Mọi FN thuộc unit đã xuất hiện trong ít nhất một `<!-- FN: ... -->` → đặt trạng thái
`srs`. **Cùng lúc**, với mỗi khối `###` ở `intel §12` (đường A, dựng từ `use_cases[]`) đã
rót thành một nhánh `S-n` trong `srs.md` — dù tìm thấy code hay "Chưa tìm thấy hiện thực
trong mã nguồn." — đặt luôn `srs` cho đúng ID `use_cases[]` item đó:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=srs --set FN-01-01-UC-01=srs \
  [--set FN-01-02=srs ...]
```

Gọi thẳng, không cần xác nhận riêng — `update` tự validate toàn bộ ID trước khi ghi.
Nhánh `S-n` tự khám phá từ code (không có `use_cases[]` nguồn) không có ID nào để set —
chỉ set FN-ID leaf như cũ.

### 11. Kết thúc — tổng hợp một lượt, không chèn rải rác trong lúc sinh

Với mỗi unit, báo theo đúng ba phần dưới, tách bạch rõ mức độ quan trọng — đừng trộn
chung thành một danh sách phẳng:

1. **Số liệu**: đường dẫn `srs.md`, số Nhóm/Chức năng đã đặc tả, và **dán nguyên văn dòng
   tổng kết `N lỗi chặn, M cảnh báo.`** của lần chạy `srs_verify.py` **cuối cùng** (bằng
   chứng đã thực sự chạy, không phải tự thuật lại bằng lời). `M > 0` → **liệt kê nguyên
   văn từng warning** ngay tại phần này (không chỉ con số `M`) — tuần tự đã trình bày ở
   bước 9 rồi, phần này với chạy tuần tự chỉ là nhắc lại gọn; **chạy song song thì đây là
   LẦN DUY NHẤT warnings của unit đó tới được người dùng** — dùng đúng nội dung subagent
   đã báo cáo lại (bước 3), không được chỉ dán số `M` mà bỏ qua nội dung.

2. **Phát hiện cần bạn xác nhận** — chỉ liệt kê các mục `intel §10` có cột `Kết luận` =
   `đang chờ` (mục đã có kết luận `cố ý`/`bug` từ lần trước thì bỏ qua, không hỏi lại).
   Không có mục nào đang chờ → bỏ hẳn phần này. Với mỗi mục: nêu mô tả và nguồn `file:dòng`
   từ `intel.md`, hỏi rõ: *"đây là cố ý thiết kế vậy hay là bug? (trả lời ngay ở lượt sau,
   hoặc tự điền cột `Kết luận` trong `intel.md` nếu tiện hơn)"* Đây là phần **quan trọng
   nhất** của báo cáo — đặt lên đầu nếu có.

   **Sau khi người dùng trả lời** (ở lượt tiếp theo): ghi kết luận **ngược lại đúng dòng
   đó** trong `intel.md` §10 — cột `Kết luận` đổi thành `cố ý — <ghi chú ngắn>` hoặc
   `bug — <ghi chú ngắn>`. Chỉ sửa cột này, không đổi mô tả/nguồn.

   **Chạy song song**: phần 2 này chỉ do **agent cha** trình bày, đúng MỘT lần cho cả
   batch — mỗi subagent chỉ **báo cáo lại** danh sách dòng `đang chờ` của unit mình (đã mô
   tả ở bước 3), agent cha **gộp** danh sách từ mọi subagent thành một phần 2 duy nhất.

3. **Thông tin còn thiếu** (thấp — chỉ để biết, không cần xử lý ngay): liệt kê ngắn gọn
   ba loại, mỗi mục một dòng — (a) mục ghi "Chưa có thông tin" ở `srs.md`; (b) câu hỏi
   chính sách nghiệp vụ chưa trả lời ở `intel §8`; (c) hai mục cấp Nhóm chưa tự sinh
   ("Sơ đồ các giao thức kết nối giữa các khối"/"Cơ sở dữ liệu", đánh dấu comment
   `TODO 3B-4` ở bước 5). Kết một câu: *"bổ sung nếu cần, không bắt buộc phải xử lý ngay —
   chạy lại lệnh sau khi bổ sung sẽ giữ nguyên phần đã có."*

Chạy hàng loạt (**≥ 2 unit runnable**) thì tổng kết thêm ở cuối, sau báo cáo của mọi
unit: tổng số unit đã xử lý, danh sách unit **đã bỏ qua** vì thiếu `intel.md` (từ bước 2,
kèm gợi ý chạy `code-intel` cho từng unit đó), danh sách unit lỗi nếu có subagent nào
BLOCKING mà không tự sửa được.

## Sai lầm thường gặp

- **Chèn `(cần xác nhận)` hoặc bất kỳ đánh dấu tương tự nào vào `srs.md`** → tài liệu này
  chỉ chứa nội dung chắc chắn; thông tin thiếu ghi thẳng "Chưa có thông tin" không đánh
  dấu, phát hiện logic/bảo mật không đưa vào file này dưới bất kỳ hình thức nào.
- **Dừng lại hỏi AskUserQuestion ở bước 5–8** → lệnh này chủ ý không hỏi trong lúc SINH.
  Chỉ bước 1 (xác nhận cây) và bước 3 (song song/tuần tự) dùng AskUserQuestion trong lúc
  sinh. Bước 11 phần 2 vẫn hỏi — bằng văn xuôi, SAU khi đã sinh xong — đây không phải một
  ngoại lệ của luật trên, mà là bước báo cáo cuối cùng; **không được bỏ qua bước 11 phần 2
  chỉ vì đọc nhầm câu này thành "không bước nào khác được hỏi".**
- **Rải phát hiện `intel §10` vào từng mục lúc viết** → dồn hết vào bước 11, một lượt duy
  nhất, đặt lên đầu báo cáo.
- **Ghi vào `srs.md` trước khi đọc bản cũ (bỏ qua bước 4)** → đè sạch nội dung người dùng
  đã sửa tay.
- **Quên snapshot `.specify/tmp/srs-before/` + truyền `--before` khi `srs.md` đã tồn tại
  từ trước** → không có gì báo lỗi lúc chạy (`srs_verify.py` im lặng bỏ qua no-clobber
  check khi thiếu `--before`, không tự phát hiện file đích đã tồn tại để cảnh báo) — nội
  dung BA đã sửa tay bị ghi đè mất mà cổng vẫn báo "0 lỗi chặn" như thể mọi thứ ổn. Luôn
  coi bước snapshot ở bước 4 là bắt buộc khi `srs.md` đã tồn tại, không phải "làm nếu nhớ".
- **Ghi thẳng `file:dòng` hoặc tên class/hàm từ intel sang srs** → phá ranh giới nội bộ/
  giao khách.
- **Bịa `Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng` ở mục `d.`** thay vì ghi "Chưa có
  thông tin" → đây là phân loại nghiệp vụ thuần, không có căn cứ code nào trả lời được —
  nhưng nếu `intel §12` đã ghi giá trị thật cho field này thì rót nguyên văn giá trị đó
  (xem bước 5), "Chưa có thông tin" chỉ đúng khi `intel §12` cũng ghi vậy.
- **Tự vẽ mockup hoặc mô tả bố cục cho phần ảnh của mục `f. Thiết kế UX/UI và Mô tả điều
  khiển`** → luôn ghi cố định `_(cần chèn ảnh — không tự sinh)_`, `intel.md` không quét bố
  cục UI. (Phần BẢNG điều khiển của cùng mục này thì có nguồn thật là `intel §11` — rót
  bình thường, đừng nhầm hai phần với nhau.)
- **Tách `f.` trở lại thành hai mục riêng `f. Thiết kế UX/UI` + `g. Mô tả điều khiển` theo
  docx** → khuôn này CỐ Ý gộp làm một (`srs_verify.py` so khớp đúng bảy tên mục `a.`-`g.`,
  tách ra sẽ bị chặn `man-hinh-thieu-muc` và `Yêu cầu nghiệp vụ` sai chữ).
- **Tự bẻ một use case lớn thành N use case nhỏ rồi viết N bảng ở `d.`** → MỘT khối `#####`
  là MỘT use case, mục `d.` có ĐÚNG MỘT bảng. Các chức năng nhỏ bên trong là nhánh `S-n`
  của chính use case đó, không phải use case riêng (lỗi đã gặp thật: một leaf sinh 6 bảng).
- **Gộp mọi điều khiển của mọi chức năng nhỏ vào MỘT bảng duy nhất ở `f.`** → phải chia
  theo từng chức năng nhỏ, mỗi cái một đầu mục in đậm + ảnh riêng + bảng riêng.
- **Tách `e.` thành nhiều khối mermaid liên tiếp** → đúng MỘT khối `sequenceDiagram`, các
  chức năng nhỏ phân tách bằng `rect` + `Note over`.
- **Vẽ `#### Sơ đồ chức năng` chỉ có mỗi node gốc** trong khi `#### Mô tả chức năng` bên
  dưới đặc tả nhiều chức năng nhỏ → node con phải phủ đúng những gì phần dưới thật sự có.
- **Tự suy luận bước cho sơ đồ mermaid khi `intel §5`/`§12` không có dữ liệu** → xoá cả
  khối mermaid, một sơ đồ bịa trông như đã xác minh còn nguy hiểm hơn văn xuôi bịa.
- **Tự sinh nội dung cho "Sơ đồ các giao thức kết nối giữa các khối"/"Cơ sở dữ liệu"/
  "Giao tiếp trong hệ thống"** → không có nguồn nào trong `intel.md` cho ba mục này, luôn
  đánh dấu comment `TODO 3B-4`, không tự suy.
- **Bỏ khối `#####` của một leaf FN-ID vì "trùng màn hình với leaf khác đã viết rồi"** →
  sai, mỗi leaf LUÔN có khối `#####` riêng dù nội dung `a.`-`g.` lặp y hệt leaf khác cùng
  màn hình — đây là thiết kế cố ý để đối chiếu 1-1 với `functions.json`, không phải lỗi
  trùng lặp cần dọn.
- **Đưa mã FN-ID vào tiêu đề `#####`** thay vì để trong comment ẩn `<!-- FN-leaf: ... -->`
  → lộ mã nội bộ ra tài liệu giao khách.
- **Thiếu comment `<!-- FN-leaf: ... -->` dưới một khối `#####`**, hoặc gộp nhiều FN-ID vào
  một comment `FN-leaf` duy nhất → mỗi khối `#####` ứng với ĐÚNG MỘT leaf, một comment
  `FN-leaf` chỉ chứa một FN-ID.
- **Thiếu hoặc sai `<!-- FN: ... -->` dưới một Chức năng** → cổng BLOCKING duy nhất của
  khuôn mới, `srs_verify.py` sẽ chặn báo xong nếu một FN trong phạm vi không xuất hiện
  trong bất kỳ comment nào.
- **Dùng "Ngoài phạm vi" hoặc bất kỳ cơ chế nào để bỏ qua hẳn một FN/Chức năng** → khuôn
  mới không còn mục ma trận truy vết để khai nhánh này; mọi FN trong phạm vi bắt buộc
  xuất hiện trong một `<!-- FN: ... -->`, dù nội dung Chức năng đó còn sơ sài (nhiều mục
  `a.`-`g.` phải ghi "Chưa có thông tin").
- **`blocking` khác rỗng mà vẫn báo xong**, hoặc sửa `srs.md` chỉ để qua cổng mà không sửa
  nội dung thật → cổng nghiệm thu trở thành hình thức.
- **Trình bày `warnings` sau khi đã ghi ngược trạng thái ở bước 10** → đảo đúng thứ tự bắt
  buộc: trình bày trước, ghi ngược sau. **Chỉ áp cho chạy tuần tự/đơn** — chạy song song,
  subagent không có ai để "trình bày" trước khi cha gọi `update`; cha buộc phải đợi TẤT
  CẢ subagent xong (kể cả để gom `--set`) trước khi có warnings để trình bày ở bước 11, nên
  thứ tự ghi-trước-trình-bày-sau ở chạy song song là **cấu trúc bắt buộc**, không phải vi
  phạm luật này.
- **Chạy `srs-from-code` khi `intel.md` chưa có** → viết SRS từ trí tưởng tượng.
- **Chạy song song mà để subagent tự gọi `fnlist_import.py update`** → race, luôn báo cáo
  về agent cha, cha gọi `update` một lần duy nhất sau khi mọi subagent xong.
- **Áp nhầm "hard-stop" và "skip-and-report" cho ca thiếu `intel.md`** → chỉ đúng 1 unit
  đã chốt mới hard-stop; ≥ 2 unit thì bỏ qua unit thiếu, chạy tiếp phần còn lại.
- **Chạy song song mà subagent không báo cáo lại `warnings` của unit mình** → warnings
  của unit đó biến mất khỏi mọi báo cáo (subagent không có ai để "trình bày" trực tiếp
  theo nghĩa bước 9, agent cha không tự sinh lại được nội dung nó không hề nhận). Bước 3
  yêu cầu subagent báo cáo cả `FN-ID=srs`, dòng `intel §10` đang chờ, LẪN nguyên văn
  `warnings` — thiếu bất kỳ phần nào trong ba phần đó là bỏ sót âm thầm.
- **Tự bịa lại "Chưa có thông tin" cho `Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng` dù
  `intel §12` đã ghi giá trị thật** → rót nguyên văn những gì `intel.md` có, không tự ý
  ghi đè bằng "Chưa có thông tin" theo thói quen cũ.
- **Quên set status cho ID `use_cases[]` item ở bước 10, chỉ set FN-ID leaf** → tiến độ
  của riêng use-case đó không được ghi nhận dù đã rót xong vào `srs.md`.
