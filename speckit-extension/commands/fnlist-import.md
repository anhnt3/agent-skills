---
description: Nhập function list (.xlsx/.csv) đã dùng nghiệm thu thành .specify/docs/functions.json — cây chức năng có ID đa cấp ổn định làm điểm neo truy vết cho mọi tài liệu bàn giao.
---

# Nhập function list thành functions.json

Có một file function list (`.xlsx` hoặc `.csv`) đã dùng để nghiệm thu đầu bài thầu với
khách. Nhiệm vụ: chuyển thành **`.specify/docs/functions.json`** — cây chức năng có mã
`FN-01-01` ổn định, làm điểm neo truy vết cho toàn bộ đường ống reverse tài liệu.
Toàn bộ tiếng Việt.

Schema của file đầu ra: `.specify/extensions/dft-speckit/references/functions-schema.md`.
**Đọc file đó trước khi bắt đầu** — nó là hợp đồng dữ liệu, không phải tài liệu tham khảo
tuỳ chọn.

**Nguyên tắc lõi**: **script chép, bạn chỉ quyết ánh xạ.** Bạn KHÔNG được tóm tắt, chuẩn
hoá, sửa chính tả hay "làm đẹp" nội dung ô. Đây là văn bản hợp đồng nghiệm thu — script là
thứ duy nhất ghi `functions.json`; việc của bạn là dò file, quyết cột nào là gì và cấp bậc
thể hiện ra sao, xác nhận với người dùng, chạy script, đối chiếu kết quả, báo cáo trung thực.

**Mã thoát khác 0 ở bất kỳ lệnh nào dưới đây → DỪNG, in nguyên thông điệp lỗi cho người
dùng. Không tự chữa, không tự đoán tham số khác rồi thử lại.** Ngoại lệ duy nhất:
thông điệp `Không có sheet 'X'. Sheet hiện có: […]` — quay lại bước 2 hỏi người dùng
chọn đúng tên sheet từ danh sách đó.

## User Input

`$ARGUMENTS`

Kỳ vọng: **đường dẫn tới một file `.xlsx` hoặc `.csv`**. Trống, không tồn tại, hoặc sai
đuôi → **hỏi lại**, KHÔNG tự đi tìm file trong repo.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/fnlist_import.py`.
Dùng `python3` nếu `python` không có (macOS/Linux). Lần đầu đọc `.xlsx`, script tự dựng
`.venv` + cài `openpyxl` — **cần mạng**, chỉ một lần.

### 0. Kiểm `.gitignore`

```bash
git check-ignore -q .specify/docs/functions.json && echo "BỊ IGNORE" || echo "OK"
```

In ra `BỊ IGNORE` → **cảnh báo người dùng trước khi ghi**: tài liệu bàn giao sẽ không
vào git. Không chặn — có thể là chủ ý của project. Đề nghị luôn phương án đổi `--out` ở
bước 4 sang một đường dẫn không bị ignore nếu người dùng muốn.

### 1. Dò cấu trúc

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py inspect "<đường-dẫn>"
```

Mặc định chỉ in **8 dòng đầu × 12 cột đầu** (`--max-rows`/`--max-cols`). File có nhiều
hơn 12 cột, hoặc 8 dòng đầu chưa đủ để phân biệt đâu là header/đâu là dữ liệu thật (vd
vài dòng logo/tiêu đề merge ở đầu) → **chạy lại với giới hạn lớn hơn**, không được đoán
ngoài khung nhìn đang có:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py inspect "<đường-dẫn>" \
  --max-rows 20 --max-cols 20 --first-data-row 1
```

`--first-data-row` (0-based) ảnh hưởng tới việc dò phân cấp: dò trên vùng dữ liệu, nên
đoán sai dòng bắt đầu là ứng viên phân cấp cũng lệch theo. Xác định `first_data_row`
trước, rồi chạy lại `inspect` với đúng giá trị đó nếu nó khác 1.

Nhiều sheet → mỗi sheet đều xuất hiện trong `sheets`; đọc `head` của **từng** sheet
trước khi quyết sheet nào là function list thật.

### 2. Quyết ánh xạ cột và kiểu phân cấp

Trường `hierarchy_candidates` của mỗi sheet là **phỏng đoán kèm bằng chứng, không phải
quyết định**. Ba kiểu:

- `columns` — mỗi cấp một cột (`Phân hệ | Nhóm | Chức năng`). Kèm `style`:
  `staircase` (mỗi dòng chỉ điền một cột cấp) hoặc `repeated` (tên cha lặp lại mọi dòng).
- `outline` — một cột chứa số mục lục `1`, `1.1`, `1.1.1`.
- `level` — một cột ghi thẳng số cấp 1/2/3.

**Luôn luôn hỏi người dùng xác nhận kiểu phân cấp qua AskUserQuestion**, kể cả khi chỉ có
một ứng viên và `score` bằng 1.0. Danh sách rỗng cũng phải hỏi — rỗng nghĩa là script
không thấy dấu hiệu phân cấp nào, và "danh sách phẳng một cấp" là một câu trả lời hợp lệ
cần người dùng xác nhận, không phải mặc định im lặng.

Lý do không tự chọn: cột mô tả cũng là cột chữ nên có thể lọt vào ứng viên `columns`, và
một cột "STT" dạng `1.1` của tài liệu đánh số tay có thể không phải cấu trúc chức năng
thật. Script không phân biệt được, người dùng thì có.

Bốn tình huống sau cũng **bắt buộc hỏi**, không tự chọn — **không chắc một tình huống có
thuộc nhóm này hay không thì coi như thuộc**, mặc định là hỏi:

- **Nhiều sheet** — sheet nào là function list thật (không phải sheet ghi chú/phụ lục).
- **Header hai tầng** — vd dòng 0 có ô trống xen kẽ (chỉ vài cột lớn có chữ) và dòng 1
  mới điền đủ nhãn con cho từng cột. Phân biệt với **header một tầng nhưng tên cột dài**
  (dòng 0 mọi ô đều có chữ, chỉ là "Mô tả chi tiết chức năng" thay vì "Mô tả") — trường
  hợp sau KHÔNG cần hỏi, tự chọn `first_data_row` = 1 là đủ.
- **Cột mô tả mơ hồ** — không chắc cột nào là mô tả chức năng hay chỉ là ghi chú/trạng thái.
- **Có dòng không khớp kiểu phân cấp đã chọn** — hỏi đây có phải "dòng nội dung", gộp vào
  nhóm cha làm use-case con (`unmatched_rows: "absorb"`), hay đó thật ra là lỗi cấu trúc
  file (thiếu mã phân cấp ở một dòng đáng ra phải là nhóm) cần người dùng sửa nguồn trước
  khi import tiếp. Không tự suy luận theo hướng nào — hai khả năng đều hợp lý và hậu quả
  chọn sai khác nhau hoàn toàn (một bên mất use-case thật, một bên nuốt nhầm lỗi nhập liệu).

Mỗi lượt AskUserQuestion gom 1–4 câu độc lập nhau.

**Chỉ áp dụng bước quét dưới đây khi đã xác nhận `unmatched_rows: "absorb"`** (file có dòng
nội dung cần gộp thành use-case con — xem giải thích `unmatched_rows` bên dưới). Ba trường
Mức quan trọng/Loại UC/Thời điểm sử dụng chỉ tồn tại trên mục `use_cases[]`, script KHÔNG
bao giờ ghi chúng vào node cây FN (node FN chỉ đúng 5 trường theo schema) — nếu mapping
không dùng `"absorb"` thì bỏ qua hẳn bước quét này, hỏi mà không dùng vào đâu chỉ tốn lượt
người dùng vô ích.

Đã xác nhận `"absorb"` → sau khi chốt cột `name`/`description`/hierarchy, **quét nốt các
cột còn lại** trong `head` đã in ở bước 1 (không giới hạn ở cột đã dùng) và hỏi có cột nào
khớp 1 trong 3 loại: Mức quan trọng use case, Loại UC, Thời điểm sử dụng UC. Đây là thông
tin nghiệp vụ thuần mà không giai đoạn nào sau này của đường ống (đọc code) suy ra lại
được — bỏ qua ở đây là mất vĩnh viễn, không có cơ hội thứ hai. Không tự đoán tên cột khớp
nghĩa gì — `inspect` đã in header + N dòng đầu cho mọi cột, việc còn lại là đọc và hỏi xác
nhận qua AskUserQuestion, không cần thuật toán chấm điểm nào (khác với hierarchy — đây là
phân loại ngữ nghĩa tên cột, không phải pattern đếm được).

Ghi ánh xạ đã chốt ra `.specify/tmp/fnlist/mapping.json`:

```json
{
  "first_data_row": 1,
  "columns": { "name": 1, "description": 2 },
  "hierarchy": { "mode": "outline", "column": 0 },
  "skip_rows": []
}
```

Với `mode: "columns"` thì khai `level_columns` + `style` thay cho `column`, và **bỏ hẳn
`columns.name`** (tên lấy từ cột cấp sâu nhất có giá trị trên dòng đó):

```json
{ "hierarchy": { "mode": "columns", "level_columns": [0, 1, 2], "style": "staircase" } }
```

Gặp file mà mã phân cấp chỉ đánh ở dòng tiêu đề nhóm, còn dòng nội dung (từng use-case,
từng giao dịch cụ thể) không mang mã nào — dòng nội dung đó không phải lỗi, nó gộp thành
một mục trong `use_cases` của nhóm cha gần nhất đang mở. Khai `unmatched_rows: "absorb"`
trong khối `hierarchy`:

```json
{
  "first_data_row": 1,
  "columns": { "name": 1, "description": 2, "importance": 3 },
  "hierarchy": { "mode": "outline", "column": 0, "unmatched_rows": "absorb" },
  "skip_rows": []
}
```

Mặc định (`unmatched_rows` vắng mặt) là `"error"` — dòng không đọc được cấp vẫn dừng cứng
như trước, dùng cho file mà MỌI dòng đều tự khai cấp. Ba khoá tuỳ chọn khác trong `columns`
— `importance` (Mức quan trọng), `type` (Loại UC), `usage_timing` (Thời điểm sử dụng) —
chỉ khai khi sheet thật sự có cột tương ứng; xem mục trên về cách hỏi.

`skip_rows` (tuỳ chọn) là danh sách số dòng **1-based** — đúng số dòng người dùng nhìn
thấy trong Excel, **khác hệ đếm** với `first_data_row`/`columns`/`level_columns`/
`hierarchy.column` ở trên (0-based). Lẫn hệ đếm ở đây là bỏ nhầm một dòng khác với dòng
định bỏ, và hậu quả không lộ ra ở đâu cả.

### 3. Xác nhận trước khi ghi (checkpoint bắt buộc)

**Không được bỏ qua bước này dù cảm thấy ánh xạ đã "rõ ràng".** Tự render **cây 5 dòng
dữ liệu đầu** theo ánh xạ đã chọn, thụt lề theo cấp. Node lá có use-case con (khi
`unmatched_rows: "absorb"`) thì in thêm các dòng con thụt sâu hơn, đánh dấu bằng `·` để
phân biệt trực quan với nhóm/lá:

```
Quản lý đơn hàng
  Danh sách đơn — Xem, tìm kiếm đơn hàng
    · Xem đơn — Xem chi tiết đơn (Mức quan trọng: Cao)
    · Tìm đơn — Tìm theo mã
  Tạo đơn mới
Quản lý khách hàng
```

Cây thụt lề chứ không phải bảng phẳng, vì thứ dễ sai nhất ở lệnh này là **cấp bậc**, và
bảng phẳng giấu đúng cái đó đi. Đặc biệt khi dùng `unmatched_rows: "absorb"`, đây là đúng
chỗ dễ sai nhất của trường hợp gộp use-case: gộp nhầm nhiều use-case khác nhau thành một,
hoặc ngược lại tách nhầm một use-case thành nhiều node lá. Cây có `·` phải cho người dùng
thấy rõ NHÓM nào gộp bao nhiêu use-case.

Hỏi qua AskUserQuestion: "Cấp bậc và ánh xạ này đúng chưa?" — **chờ phản hồi thật, cấm tự
tuyên bố người dùng đã đồng ý.** Chưa có phản hồi → DỪNG, không chạy bước 4. Sai → quay
lại bước 2 sửa ánh xạ, xác nhận lại từ đầu.

Lý do bắt buộc: mọi `FN-ID` sau này của `code-intel`/`srs-from-code` neo vào đúng lần ghi
này. Sai ở đây khó gỡ hơn nhiều so với một lượt hỏi.

`--system`/`--date` dùng ở bước 4: lấy tên hệ thống từ `$ARGUMENTS`, README, hoặc
constitution project nếu có; không chắc thì hỏi cùng lượt AskUserQuestion này. `--date`
= ngày chạy lệnh (YYYY-MM-DD). Không tự bịa tên hệ thống.

### 4. Ghi

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py write "<đường-dẫn>" \
  --mapping .specify/tmp/fnlist/mapping.json \
  --out .specify/docs/functions.json \
  --system "<tên hệ thống>" \
  --date <YYYY-MM-DD> \
  --sheet "<tên sheet đã chọn ở bước 1>"
```

**Luôn truyền `--sheet` tường minh, kể cả file chỉ có một sheet — và giá trị PHẢI lấy
đúng nguyên văn từ trường `name` của sheet đã chọn trong JSON `inspect` ở bước 1, không
tự gõ tên khác.** Với `.xlsx` đó là tên sheet thật; với `.csv` đó **không phải** "Sheet1"
hay tên bịa nào — nó là tên file bỏ đuôi (script dùng làm khoá nội bộ cho CSV). Truyền
sai tên (kể cả với CSV) làm script không tìm thấy khoá và dừng với lỗi — đây là hành vi
đúng (không âm thầm sai). Thiếu hẳn cờ `--sheet` mới là ca nguy hiểm: script âm thầm dùng
sheet đầu tiên trong file, không báo lỗi — nếu đó không phải sheet vừa xác nhận ở bước 3,
lệnh ghi ra dữ liệu của sheet sai mà không có gì tố cáo.

Script in báo cáo JSON ra stdout: `out`, `written` (số node cây FN), `written_use_cases`
(số use-case đã gộp — có thể lớn hơn nhiều `written` nếu phần lớn dữ liệu là dòng nội
dung), `skipped`, `retired`, và (chạy lại trên file đã có) `diff`. Đọc cả hai con số —
`written` nhỏ không có nghĩa là thiếu dữ liệu nếu `written_use_cases` bù lại đủ.

Chạy lại trên `functions.json` đã có thì script **ghi đè tại chỗ** — đúng như thiết kế,
vì không ai sửa tay file này: ID cũ được giữ theo đường dẫn tên, `status` do
`code-intel`/`srs-from-code` ghi cũng được chép sang bản mới. Không có bản `.new` nào và
không cần hợp nhất tay.

### 5. Đối chiếu tính đầy đủ

Đọc báo cáo.

**Kênh mất dòng thật nằm ở phần script không hề đếm**: mọi dòng có chỉ số **trước
`first_data_row`** không xuất hiện ở `written` lẫn `skipped` — với script, chúng không
tồn tại. Luôn luôn — không có điều kiện nào để bỏ qua bước này — trình lại các dòng
`head` từ chỉ số `0` tới `first_data_row − 1` của bước 1, và với **từng dòng** nêu lý do
cụ thể vì sao nó không phải một chức năng (dòng tiêu đề nhóm, dòng logo, dòng merge).
Thường chỉ có một dòng header nên chi phí gần như bằng không; nhưng bỏ qua bước này là
đúng chỗ một chức năng thật ở đầu bảng có thể biến mất mà không một tín hiệu nào tố cáo.

Có `skipped` → **liệt kê đích danh từng dòng** (số dòng + lý do: `ô tên chức năng trống`
hoặc `người dùng khai bỏ`), hỏi qua AskUserQuestion: có dòng nào trong số này thực ra là
một chức năng thật không? **Chờ phản hồi thật, cấm tự kết luận thay người dùng** dù lý do
trông hợp lý đến đâu.

- Xác nhận có dòng bỏ nhầm → sửa `mapping.json` rồi **quay lại bước 3** (xác nhận lại,
  không nhảy thẳng bước 4). Chạy lại `write` là an toàn: script giữ ID cũ theo đường dẫn
  tên, không cần xoá gì trước.
- Xác nhận đúng là bỏ → đi tiếp bước 6.

### 6. Trình `diff` (chỉ khi chạy lại trên file đã có)

Trình bảng `diff` cho người dùng. Bảy loại (bốn loại gốc + ba nhãn use-case) và cách nói về
chúng:

- `thêm` / `bỏ` — chức năng mới xuất hiện / biến mất so với lần import trước.
- `đổi mô tả` — cùng vị trí trong cây, nội dung mô tả đổi.
- `chuyển nhóm` — **loại quan trọng nhất, phải nói rõ**: chức năng đổi nhóm cha nên
  **ID đã đổi** (`id_cu` → `id_moi`). Mọi tài liệu đang trỏ `id_cu` (`intel.md`, `srs.md`
  đã sinh) sẽ trỏ trượt và **phải sửa tay** — nêu đích danh ID cũ, ID mới, và nhắc người
  dùng rà lại. Đây là điểm gãy truy vết duy nhất của thiết kế; đừng trình lẫn vào các
  thay đổi thường. Nếu chức năng vừa chuyển nhóm vừa đổi mô tả cùng lúc, entry này còn
  kèm mô tả cũ/mới — trình đầy đủ cho người dùng, đừng chỉ báo việc chuyển nhóm mà bỏ
  sót phần đổi mô tả.
- `use-case thêm` / `use-case bỏ` / `use-case đổi mô tả` — cùng ý nghĩa như trên nhưng cho
  một use-case con BÊN TRONG một node lá không đổi, tách nhãn riêng để không lẫn với thay
  đổi ở cấp chức năng. Không có `use-case chuyển nhóm` — use-case đổi node cha hiện ra như
  một cặp `use-case bỏ` + `use-case thêm` rời rạc, không gộp.

Đổi tên chức năng hiện ra dưới dạng một cặp `bỏ` + `thêm` (khớp cũ↔mới dựa trên tên, nên
tên đổi là mất dấu vết). Thấy một cặp `bỏ`/`thêm` trông giống nhau về nghiệp vụ → nói
thẳng khả năng đây là đổi tên chứ không phải thêm/bớt chức năng.

**`diff` chỉ so sánh chức năng lá (không có con)** — thay đổi mô tả, thêm, hoặc xoá một
chức năng cấp cao (có con) sẽ KHÔNG hiện trong `diff`. Đừng trình `diff` như thể nó đã đủ;
nếu người dùng sửa cả tên/mô tả của một nhóm cha, phải tự nhắc là thay đổi đó không nằm
trong bảng `diff`.

`retired` liệt kê TOÀN BỘ ID đã bị khai tử tính tới thời điểm này (tích luỹ qua mọi lần
import, không chỉ lần vừa rồi) — nói cho người dùng biết các ID này sẽ không bao giờ được
cấp lại cho chức năng khác. Từ lần import thứ ba trở đi, danh sách này sẽ chứa cả ID chết
từ các lần trước, không chỉ ID vừa chết ở lần này — đừng trình như thể toàn bộ danh sách
là mới.

### 7. Kết thúc

Báo: số chức năng đã ghi (`written`), số use-case đã gộp (`written_use_cases`), sheet đã
dùng, đường dẫn file. Báo cả hai con số — chỉ nói `written` dễ khiến người dùng tưởng nhầm
là mất dữ liệu khi phần lớn nội dung nằm ở `use_cases[]` chứ không phải node cây FN.

**Nói rõ trạng thái đường ống**: `functions.json` đã ghi, nhưng
`/speckit.dft-speckit.code-intel` và `/speckit.dft-speckit.srs-from-code` **hiện chưa đọc
được định dạng này** (chúng vẫn tìm `functions.md`) — chưa chạy tiếp được cho tới khi hai
lệnh đó được cập nhật. **KHÔNG nhắc người dùng chạy `code-intel` như bước kế tiếp** — lời
nhắc đó dẫn thẳng vào chỗ gãy.

Project đã có `.specify/docs/functions.md` từ trước → **không xoá nó**. Nói cho người dùng
biết file cũ vẫn còn để `code-intel` chạy tạm được cho tới khi hai lệnh kia được cập nhật.

## Sai lầm thường gặp

- **Tự chọn kiểu phân cấp theo `score` cao nhất mà không hỏi** → cột mô tả bị hiểu thành
  cột cấp, hoặc cột STT đánh tay bị hiểu thành cấu trúc chức năng. `hierarchy_candidates`
  là phỏng đoán, không phải quyết định.
- **Tự đoán ánh xạ cột khi header mơ hồ, hoặc bỏ qua checkpoint bước 3** → sai cột là sai
  toàn bộ `functions.json`, và mọi FN-ID sau đó neo vào dữ liệu sai.
- **Trình checkpoint dạng bảng phẳng thay vì cây thụt lề** → giấu đúng cái dễ sai nhất là
  cấp bậc.
- **Quên truyền `--sheet` ở bước 4** → script âm thầm dùng sheet đầu tiên, không báo lỗi.
- **Nhầm hệ đếm của `skip_rows` (1-based) với các trường còn lại (0-based)** → bỏ nhầm
  dòng khác với dòng định bỏ.
- **Bỏ qua việc trình các dòng trước `first_data_row`** → chức năng thật ở đầu bảng biến
  mất mà không tín hiệu nào tố cáo. Công thức đếm của script không bắt được ca này.
- **Tự viết lại / tóm tắt nội dung ô** → phá hợp đồng lõi. Script chép, bạn không chép.
- **Tự kết luận `skipped` là ổn mà không hỏi** → dòng chức năng thật bị âm thầm rơi khỏi
  tài liệu bàn giao.
- **Trình `chuyển nhóm` như một thay đổi bình thường** → người dùng không biết ID đã đổi,
  các `intel.md`/`srs.md` cũ trỏ trượt mà không ai rà.
- **Nhắc chạy `code-intel` ở bước 7** → hai lệnh đó chưa đọc được `functions.json`.
- **Sửa tay `functions.json`** → script là chương trình duy nhất được phép ghi; muốn đổi
  `status` thì gọi `fnlist_import.py update`.
- **Coi dòng nội dung là lỗi cấu trúc khi thật ra file cố ý phân tầng kiểu "chỉ nhóm có
  mã"** → chọn `unmatched_rows: "error"` sai, dừng nhầm một file hợp lệ.
- **Ngược lại: chọn `"absorb"` cho một file mà dòng không khớp cấp thật sự là lỗi nhập
  liệu** → nuốt luôn dòng lỗi vào làm use-case, không ai phát hiện.
- **Bỏ qua quét cột bổ sung (Mức quan trọng/Loại UC/Thời điểm sử dụng)** → thông tin có sẵn
  trong Excel nhưng không bao giờ được hỏi, xuống `srs-from-code` lại thành "Chưa có thông
  tin" — đúng lỗ hổng đang sửa.
- **Trình checkpoint cây bước 3 mà không hiện use-case con** → giấu đúng chỗ dễ sai nhất
  của trường hợp gộp.
- **Cột mã outline có ô chứa giá trị không đúng dạng mã (không rỗng, không phải `1`/`1.1`...)**
  → giờ dừng với lỗi 'không đọc được cấp của dòng' thay vì âm thầm coi là nhóm cấp 1 như hành
  vi cũ (đã sửa hành vi ngầm sai này) — đây là thay đổi có thể lộ ra trên cả file KHÔNG dùng
  `unmatched_rows: "absorb"`, không chỉ file dùng tính năng gộp use-case.
