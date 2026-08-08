---
description: Lập roadmap build từ cây BRD markdown (docs/brd/) — xếp thứ tự làm từng màn, ghi docs/roadmap.md, gác cổng phủ 1-1 bằng script.
---

# Roadmap build từ BRD

BA đã giao BRD và `/speckit.dft-speckit.brd-import` đã bẻ thành cây markdown `docs/brd/`.
Nhiệm vụ: sinh **`docs/roadmap.md`** xếp **thứ tự làm** từng màn/chức năng. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: **BRD là nguồn chốt danh sách** — mọi node BRD phải hoặc có ít nhất một
item roadmap trỏ tới, hoặc được khai là "không phải màn" kèm lý do. Codebase (nếu có) **chỉ**
dùng để suy thứ tự; nó KHÔNG được thêm hay bớt item, KHÔNG đụng cột `Trạng thái`.

## User Input

`$ARGUMENTS`

Kỳ vọng: **đường dẫn thư mục BRD tương đối từ gốc repo** (vd `docs/brd`), mặc định `docs/brd`
khi để trống. Thư mục không tồn tại → **hỏi lại**, KHÔNG tự đi tìm thư mục khác trong repo.
Thư mục có `.md` nhưng **thiếu `brd.manifest.yml`** (BRD do BA viết tay, không qua `brd-import`)
→ KHÔNG dừng: chạy bước 0.5 dựng manifest.

Đường dẫn **tuyệt đối** (`C:/proj/docs/brd`, `/home/…`) hoặc có `../` → quy đổi về tương đối
gốc repo trước khi dùng; không quy đổi được (nằm ngoài repo) → **hỏi lại**, KHÔNG chạy tiếp.
Lý do: `--brd-rel` ở bước 7 là **tiền tố chuỗi** của trường `Nguồn`, mà `Nguồn` luôn viết
tương đối gốc repo — hai thứ lệch nhau thì mọi item báo "không có node BRD nào ở vị trí đó",
thông điệp lỗi không lộ nguyên nhân thật.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/brd_roadmap.py`.
Thư mục làm việc tạm: `.specify/tmp/roadmap-brd/`.

### 0. Chặn đầu vào

`docs/roadmap.md` **đã tồn tại** → **DỪNG NGAY**. In đường dẫn file cũ và nói rõ: lệnh này
KHÔNG merge vào roadmap có sẵn; muốn sinh lại thì người dùng tự đổi tên hoặc xoá file cũ.
Không hỏi "có muốn ghi đè không" — không ghi đè là quyết định đã chốt.

**Ngoại lệ duy nhất — nối lại phiên dở dang**: chỉ khi `.specify/tmp/roadmap-brd/decisions.json`
tồn tại và thoả **cả ba**:

1. `"brd_dir"` khớp thư mục BRD đang xử lý,
2. `"interview2_confirmed": true`,
3. **`"completed"` vắng mặt hoặc `false`** — đây là điều kiện phân biệt "bản nháp verify chưa
   qua" với "roadmap đã hoàn tất từ lần trước". Bước 7 ghi `"completed": true` ngay khi verify
   exit 0; thiếu điều kiện này thì mọi lần gọi lại sau một lần chạy thành công đều bị nhận nhầm
   là nối phiên và **ghi đè roadmap sản xuất**, xoá `Trạng thái` + `Nợ phát sinh` team đã tích luỹ.

Thiếu bất kỳ điều nào trong ba → áp luật dừng ở trên, KHÔNG tự suy diễn, KHÔNG "chắc là nháp".

Khi ngoại lệ áp dụng: nói rõ đang nối lại phiên, **bỏ qua bước 1–5**, đọc `decisions.json` lấy
phân loại + wave đã chốt, rồi **sửa tại chỗ `docs/roadmap.md` đang có** đúng các lỗi `verify`
báo — **KHÔNG sinh lại file từ khung**, KHÔNG đụng dòng/khối đang đúng (chúng có thể đã được
người dùng sửa tay giữa hai phiên). Chỉ dùng bước 6 làm **luật định dạng** cho phần đang sửa.
KHÔNG hỏi lại người dùng những gì `decisions.json` đã ghi.

### 0.5. Dựng `brd.manifest.yml` khi thiếu (BRD viết tay)

`brd.manifest.yml` là **danh sách node** — mỏ neo đếm mà toàn bộ gate phủ 1-1 dựa vào. Cây do
`brd-import` sinh đã có sẵn; cây BA viết tay thì chưa. **Bỏ qua bước này khi file đã tồn tại và
cây không lệch** (bước 1 sẽ báo `files_without_node`/`nodes_without_file` nếu lệch).

```bash
python .specify/extensions/dft-speckit/scripts/brd_roadmap.py manifest "<thư-mục-brd>"
```

Mặc định là **dry-run, không ghi gì**. Báo cáo JSON trả `total`, `kept`, `added`, `removed`,
`warnings`, `nodes`. Mô hình: **mỗi file `.md` là đúng một node**, thư mục chỉ là đường dẫn
(không sinh node), `media/` bị bỏ qua, `_index.md`/`README.md` ở gốc là node gốc (không tính
coverage). Title lấy theo thứ tự: `title` trong frontmatter → heading đầu tiên → tên file.

Trình cho người dùng: **tổng số node**, danh sách `added`/`removed` (đầy đủ khi ≤20 dòng, dài
hơn thì rút gọn nhưng phải nói rõ đã rút bao nhiêu), mọi `warnings`. Rồi hỏi qua
**AskUserQuestion**: "đây có đúng là danh sách mục BRD của anh/chị không?" — đây là **quyết định
của BA**, không phải fact để tự chốt. Có phản hồi đồng ý mới chạy lại kèm `--write`:

```bash
python .specify/extensions/dft-speckit/scripts/brd_roadmap.py manifest "<thư-mục-brd>" --write
```

- Manifest đã có sẵn thì lệnh **hoà giải, không sinh lại**: node còn khớp đường dẫn giữ nguyên
  `id`, file mới cấp `id` tiếp theo (không tái dùng id đã gỡ), node mất file bị gỡ và liệt kê
  trong `removed`. Giữ `id` ổn định là điều kiện để `decisions.json` và trường `Nguồn` của
  roadmap cũ không trỏ sai — CẤM xoá manifest đi sinh lại cho "sạch".
- Người dùng nói danh sách sai (thiếu mục, gom nhầm) → vấn đề nằm ở **cấu trúc file BRD**, không
  phải ở lệnh này: bảo họ tách/gộp file `.md` rồi chạy lại. KHÔNG sửa tay `brd.manifest.yml`.
- Mô hình một-file-một-node có hệ quả: **file chứa nhiều màn vẫn chỉ là một node**, một item
  roadmap là "phủ đủ". `verify` cảnh báo khi node >40.000 ký tự hoặc có ≥5 mục cấp 2 mà chỉ 1
  item trỏ tới — gặp cảnh báo đó thì tách item (bước 3, nhánh "chứa k màn"), đừng bỏ qua.

### 1. Trích outline

```bash
python .specify/extensions/dft-speckit/scripts/brd_roadmap.py outline "<thư-mục-brd>" \
  --out .specify/tmp/roadmap-brd/outline.json --quiet
```

**Luôn dùng `--quiet`.** Không có cờ này, lệnh in nguyên outline (toàn bộ `headings`, `head`,
`signals` từng node) ra stdout — trùng lặp với file `--out` và có thể vỡ context trên BRD lớn.
Với `--quiet`, `outline.json` vẫn được ghi đầy đủ như bình thường, còn stdout chỉ là **một dòng
tóm tắt tiếng Việt**: số node, đường dẫn file đã ghi, và số lượng `files_without_node` /
`nodes_without_file`.

Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp lỗi. Không tự chữa, không thử lệnh khác.

Đọc dòng tóm tắt trên stdout trước: nếu hai số `files_without_node` / `nodes_without_file`
khác 0, mở `outline.json` để lấy danh sách chi tiết. Báo cho người dùng: số node, và **liệt kê
đầy đủ** `files_without_node` (file BA thêm tay, manifest chưa biết) + `nodes_without_file`
(file đã bị xoá) khi hai danh sách đó không rỗng. Hai danh sách này không chặn nhưng **không
được im lặng bỏ qua** — chúng đổi cách hiểu cây. Cách xử đúng: quay lại **bước 0.5** chạy
`manifest` để hoà giải (giữ id cũ, thêm node cho file mới, gỡ node mất file), rồi chạy lại
`outline`. Đừng đi tiếp với manifest lệch: file ngoài manifest không được phép làm `Nguồn`. Đừng đọc lại toàn bộ `outline.json` nếu dòng
tóm tắt đã cho biết cả hai danh sách đều rỗng.

### 2. Quét codebase — CHỈ để suy phụ thuộc

Tìm trong codebase: auth/đăng nhập, phân quyền, entity/service dùng chung, module đã dựng.
Ghi nhận cái gì **đã có** để biết cái gì chặn cái gì.

Quét **có trần**: `Glob`/`Grep` theo tên (route, model/entity, `auth`, `permission`, `role`) và
đọc tối đa vài file thật sự cần. Mục tiêu chỉ là biết cái gì đã tồn tại — KHÔNG đọc cả repo,
đây là bước dễ vỡ context nhất của lệnh.

- Không có codebase (repo mới, chỉ có `docs/`) → **bỏ qua bước này và nói thẳng**
  "chưa có codebase, phụ thuộc suy hoàn toàn từ BRD". KHÔNG hỏi vòng vo, KHÔNG dừng.
- **CẤM** dùng codebase để thêm item, bớt item, hay đặt cột `Trạng thái`. Màn có trong code
  mà không có trong BRD → chỉ **báo miệng** cho người dùng biết, KHÔNG ghi vào file.

### 3. Phân loại ứng viên

Mỗi node trong `outline.json` (bỏ qua node `kind: root`) rơi vào đúng một nhóm:

- **là màn** → một item roadmap
- **chứa k màn** → tách thành k item, mỗi item trỏ về cùng file kèm `#heading` khác nhau
- **không phải màn** → ghi vào `decisions.json` kèm **lý do cụ thể**

**Lý do loại phải gắn vào nội dung node đó**, nêu bằng chứng đọc được từ outline (heading, `head`,
`signals`) — vd "chỉ là bảng thuật ngữ 2 cột, `signals.action_words`=0, không nút thao tác".
CẤM dán một nhãn chung ("không phải màn", "phi chức năng") cho nhiều node: `verify` cảnh báo khi
≥3 node dùng cùng một lý do, và khi loại quá nửa số node — hai cảnh báo đó phải đọc là "đã phân
loại ẩu", không phải nhiễu để bỏ qua.

Căn cứ: `signals` (bảng trường, nút thao tác, phân quyền, ảnh), `headings`, `head`, `chars`.
Outline chưa đủ để quyết một node → **`Read` thẳng file đó** theo `path`. CẤM đoán.

Đã có `.specify/tmp/roadmap-brd/decisions.json` với `"brd_dir"` khớp (phiên trước đứt giữa
Interview #1) → đọc lên làm **điểm xuất phát**, chỉ bổ sung/sửa phần khác, đừng phân loại lại
từ đầu rồi bắt người dùng duyệt lại những gì đã duyệt.

Ghi `.specify/tmp/roadmap-brd/decisions.json`:

```json
{
  "brd_dir": "docs/brd",
  "excluded": [
    {"node_id": "BRD-0003", "title": "Thuật ngữ và từ viết tắt", "reason": "từ điển thuật ngữ, không phải màn"}
  ]
}
```

### 4. Interview #1 — chốt phân loại

Mở đầu bằng **dòng đối soát bắt buộc**, số lấy thẳng từ `outline.json` / `decisions.json`:

```
Tổng node (bỏ root): N — là màn: A — tách: B (→ C item) — loại: D
```

**A + B + D phải bằng N.** Không khớp → phân loại đang sót hoặc trùng: quay lại bước 3 sửa,
**KHÔNG hỏi người dùng khi số chưa khớp**. Dòng này là mỏ neo để người dùng biết bảng dưới có
bị cắt hay không — thiếu nó thì cả hai bảng đều không kiểm chứng được.

Rồi trình **ĐẦY ĐỦ, không cắt bớt** hai bảng (số dòng bảng 1 phải đúng bằng D, bảng 2 đúng bằng B):

1. **Node bị loại** — mỗi dòng: id, tiêu đề, lý do loại.
2. **Node bị tách** — mỗi dòng: id, tiêu đề, tách thành mấy item, tên từng item.

Rồi hỏi qua **AskUserQuestion**, mỗi lượt gom **1–4 câu độc lập nhau**. Hỏi theo **nhóm quyết
định** (vd "nhóm 5 mục phi chức năng này loại hết hay giữ lại làm item hạ tầng?"), **KHÔNG hỏi
từng node một** — người dùng sửa trực tiếp trên bảng nếu muốn đổi lẻ tẻ.

**Chờ phản hồi thật.** Cấm tự tuyên bố người dùng đã đồng ý. Chưa có phản hồi → DỪNG, không đi
tiếp. Người dùng đổi quyết định → **cập nhật lại `decisions.json`** trước khi sang bước 5.

### 5. Đề xuất wave rồi Interview #2 — chốt thứ tự

Xếp build theo phụ thuộc:

- **Wave 0 — nền tảng**: auth, phân quyền, danh mục/thực thể mà màn khác tham chiếu.
- **Wave sau**: chức năng phụ thuộc wave trước.

Trình bảng đề xuất kèm **lý do thứ tự** (cái gì chặn cái gì), nêu rõ căn cứ đến từ BRD hay từ
codebase. Thứ tự tài liệu BRD chỉ dùng để phá hoà khi hai item không ràng buộc nhau.

Rồi hỏi qua **AskUserQuestion**: **ranh giới wave** và **các cặp thứ tự có ràng buộc phụ thuộc
mà bạn không chắc** là quyết định trọng yếu — phải hỏi. Cặp hiển nhiên (auth chặn mọi màn cần
đăng nhập, danh mục chặn màn tham chiếu nó) đưa vào bảng đề xuất, KHÔNG tốn một lượt hỏi. Vị trí
tương đối trong cùng một wave cũng vậy — người dùng chỉnh trực tiếp trên bảng.

**Trần: tối đa 3 lượt AskUserQuestion ở bước này** (mỗi lượt tới 4 câu). Còn điểm chưa chắc sau
3 lượt → ghi thẳng vào bảng đề xuất phương án của bạn kèm chữ "chưa chốt, sửa trực tiếp nếu sai",
KHÔNG hỏi tiếp. Hỏi tràn lan gây fatigue, người dùng trả lời ẩu còn hại hơn.

Mỗi câu 2–4 option kèm lý do + trade-off; `(Recommended)` CHỈ khi có căn cứ và nêu căn cứ ngay
trong option. **Thứ tự là quyết định của người dùng** — chờ **phản hồi thật**; chưa có phản hồi
→ DỪNG, **KHÔNG ghi file**.

Có phản hồi rồi → **ghi ngay `decisions.json` trước khi sang bước 6**, bổ sung hai khoá:

```json
{
  "brd_dir": "docs/brd",
  "excluded": [ … ],
  "waves": [
    {"rm_id": "RM-001", "man": "Đăng nhập", "wave": 0, "deps": [], "nguon": "docs/brd/01-chung/02-dang-nhap.md"}
  ],
  "interview2_confirmed": true
}
```

Đây là **nơi bàn giao vật lý** duy nhất của lệnh: nếu bước 7 chấm không qua và phiên đứt, bước 0
đọc đúng file này để nối lại mà không bắt người dùng trả lời lại hai vòng interview.

### 6. Ghi `docs/roadmap.md` theo khung CỐ ĐỊNH

Bước này có hai nhánh: **chạy mới** → sinh file từ khung theo luật dưới. **Nối lại phiên**
(ngoại lệ bước 0) → KHÔNG sinh lại, chỉ sửa tại chỗ file đang có; các luật dưới vẫn là chuẩn
định dạng cho phần bạn sửa.

**Dùng khung cố định, KHÔNG tự chế cấu trúc:**

- Lấy khung: chạy `specify preset resolve roadmap-template` để lấy đường dẫn file khung; không
  resolve được → đọc `.specify/extensions/dft-speckit/templates/roadmap-template.md`; vẫn không
  thấy → hỏi.
- Copy đúng cấu trúc khung (bảng tổng + khối chi tiết mỗi item), chỉ **điền** placeholder `[…]`,
  thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **ID ổn định** `RM-001`, `RM-002`, … cấp tăng dần theo thứ tự trong bảng tổng, khớp giữa bảng
  tổng và khối chi tiết. Định dạng **cứng**: `RM-` + **đúng 3 chữ số**. `RM-1` hay `RM-0012`
  không được `verify` nhận là item nào cả — dòng bị bỏ qua im lặng rồi gate đổ lỗi "node chưa có
  item nào trỏ tới" cho toàn bộ BRD, che mất nguyên nhân thật. Quá 999 item thì dừng, báo người dùng.
- **Cột `Trạng thái`** của MỌI item: `chưa`. Roadmap này mới sinh — không có item nào "đang"/"xong",
  kể cả khi codebase đã có màn đó (`verify` cảnh báo nếu khác).
- **Ô `ID` trong bảng tổng là LINK** tới chính nguồn của item — bấm vào mở thẳng mục BRD.
  **Hai trường này viết theo hai hệ quy chiếu khác nhau, đừng copy chuỗi từ cái nọ sang cái kia:**
  - `Nguồn` (khối chi tiết) — tương đối **gốc repo**: `docs/brd/03-quan-ly/05-danh-sach.md`
  - link ô ID — tương đối **thư mục chứa `docs/roadmap.md`**, tức bỏ tiền tố `docs/`:
    `| [RM-001](brd/03-quan-ly/05-danh-sach.md#danh-sách) | …`

  Viết `docs/brd/…` làm link thì trình đọc hiểu thành `docs/docs/brd/…` → bấm vào 404.
  `verify` resolve link theo vị trí roadmap rồi mới so với `Nguồn`, cảnh báo kèm link đúng nếu
  lệch, hoặc nếu ô ID còn là text trần trong khi `Nguồn` có đích thật. `Nguồn` = `N/A` → để ID
  text trần, không bịa link.
- **Trường `Nguồn`** của mỗi item: đường dẫn tương đối từ gốc repo tới file BRD nguồn
  (`docs/brd/03-quan-ly/05-danh-sach.md`), thêm `#<tiêu đề mục>` khi nhiều item cùng trỏ về một
  file. Node không có file riêng (`inline`) thì trỏ vào thư mục của nó (`docs/brd/03-quan-ly/`);
  khi một node `inline` tách thành nhiều item, mỗi item vẫn trỏ vào thư mục đó nhưng thêm
  `#<tiêu đề mục>` để phân biệt — `verify` chấp nhận anchor trên `Nguồn` thư mục và không đối
  chiếu heading (không có file để đối chiếu), nên anchor ở đây chỉ là nhãn cho người đọc.
  **Chỉ trỏ vào file/thư mục có trong `brd.manifest.yml`**: file BA thêm tay sau import
  (`files_without_node` ở bước 1) không có node nào ứng với nó → `verify` báo lỗi. Muốn đưa vào
  roadmap thì quay lại bước 0.5 chạy `manifest --write` cho manifest biết file đó, đừng cố trỏ
  `Nguồn` vào nó rồi gỡ item khi gate đỏ.
  **Cẩn thận**: `verify` chấm phủ theo *vị trí* (file/thư mục), không theo từng node. Với cây
  BRD do `brd-import` sinh ra, mỗi thư mục `inline` chỉ ứng với đúng một node nên việc này
  thường không gây lệch — nhưng đừng dựa vào đó: nếu một thư mục chứa nhiều màn thật (vd sau khi
  sửa tay `docs/brd/`), một `Nguồn` thư mục duy nhất sẽ tính TẤT CẢ các màn đó là đã phủ dù mỗi
  màn chưa có item riêng. Nguyên tắc đúng là mỗi màn thật luôn có item roadmap trỏ đích danh tới
  nó (dùng `#<tiêu đề mục>` để phân biệt khi cần) — không dựa vào việc gộp `Nguồn` thư mục để
  "phủ hộ" các màn khác.
- **KHÔNG để sót ngoặc vuông trần** ở bất cứ đâu — `verify` coi mọi `[...]` không phải link
  markdown là placeholder chưa điền và sẽ báo lỗi.
- **Cột `Wave`** trong bảng tổng chỉ chứa **số nguyên trần**: `0`, `1`, `2`, … — KHÔNG ghi
  `"Wave 0"` hay bất cứ chữ nào kèm số, dù mục 5 ở trên gọi bằng lời là "Wave 0". `verify` chấm
  cột này như số, chữ sẽ làm gãy gate ngay.
- **Cột `Phụ thuộc`**: mỗi ID liệt kê phải tồn tại trong bảng tổng; không có phụ thuộc thì ghi
  `N/A`. Một item **không được** phụ thuộc vào item ở Wave **sau** nó (Wave của item phụ thuộc
  phải ≤ Wave của chính nó) — `verify` báo lỗi "Wave nghịch" nếu sai.

### 7. Chấm bằng script — cổng cuối

```bash
python .specify/extensions/dft-speckit/scripts/brd_roadmap.py verify docs/roadmap.md \
  --brd "<thư-mục-brd>" --brd-rel "<thư-mục-brd>" \
  --decisions .specify/tmp/roadmap-brd/decisions.json
```

**CẤM báo xong khi mã thoát chưa là 0**, bất kể mã thoát cụ thể là gì.

- Exit 1 (`ok: false`) → **sửa `docs/roadmap.md` cho đúng rồi chạy lại**. Cấm "chữa" bằng cách
  nhét node vào `decisions.json` với lý do bịa — loại một node là quyết định phân loại, phải
  quay lại bước 4 hỏi người dùng. Cũng cấm chữa bằng cách bọc khối chưa điền trong fence code
  hay dòng `<!-- -->` để placeholder "biến mất" khỏi lượt quét — đó là qua mặt gate, không phải
  sửa lỗi.
- Sửa rồi chạy lại tối đa **vài lần** (khoảng 3); vẫn chưa exit 0 → **DỪNG**, báo cho người dùng
  danh sách lỗi còn lại nguyên văn, KHÔNG tự loop tiếp hay tự chế cách khác để né gate.
- Exit 2 → lỗi thao tác (sai đường dẫn, JSON hỏng). In nguyên thông điệp, DỪNG.
- **Liệt kê đầy đủ `warnings`** cho người dùng, kể cả khi `ok: true`.
- Sửa lỗi `verify` **không được đổi wave/phụ thuộc người dùng đã chốt** trong `waves` của
  `decisions.json`. Muốn sửa "Wave nghịch" mà buộc phải dời một cặp đã chốt → quay lại bước 5
  hỏi người dùng, KHÔNG tự dời rồi im lặng: gate xanh nhưng quyết định của người dùng bị nuốt.

Exit 0 rồi → **ghi `"completed": true` vào `decisions.json`** ngay. Đây là dấu đóng phiên; thiếu
nó thì lần gọi lệnh sau sẽ tưởng roadmap đã hoàn tất là bản nháp và ghi đè.

Kết thúc: báo số item, thứ tự wave, danh sách node đã loại kèm lý do, rồi nhắc
`/speckit.dft-speckit.domain-design <module>` và `/speckit.specify <ID>` để bắt đầu từng mục.

Nhắc dọn dẹp: `.specify/tmp/roadmap-brd/` giữ `outline.json` và `decisions.json` — cần cho lần
chấm lại, xoá được khi đã hài lòng với `docs/roadmap.md`.

## Sai lầm thường gặp

- **Tự chốt phân loại rồi chạy tiếp** → phân loại là quyết định của người dùng, phải hỏi thật.
- **Dùng codebase để thêm/bớt item hoặc đặt `Trạng thái`** → phá nguyên tắc lõi: BRD là nguồn
  chốt danh sách.
- **Loại node mà không ghi lý do vào `decisions.json`** → `verify` fail, và người dùng mất dấu
  vì sao một mục BRD biến mất.
- **Ghi đè `docs/roadmap.md` có sẵn** → xoá `Trạng thái` và `Nợ phát sinh` người khác đã ghi.
- **`verify` fail rồi vẫn báo xong**, hoặc nhét node vào `decisions.json` cho qua cổng, hoặc bọc
  placeholder chưa điền trong fence code / dòng `<!-- -->` cho biến mất khỏi lượt quét → che lỗi.
- **Gộp nhiều màn thật vào chung một `Nguồn` thư mục rồi coi là đã phủ hết** → `verify` chấm
  phủ theo vị trí nên gate có thể vẫn xanh, nhưng những màn đó chưa có item riêng của mình.
- **Loại hàng loạt node bằng một nhãn chung** ("không phải màn" dán cho 20 node) → gate vẫn xanh
  vì `reason` không rỗng, nhưng hàng chục màn thật biến mất. Lý do phải gắn nội dung từng node.
- **Nuốt `warnings` cho gọn báo cáo** → người dùng mất thông tin cần để quyết.
- **Đọc toàn văn mọi file BRD** → vỡ context rồi bỏ sót mục cuối. Đọc `outline.json` trước,
  chỉ `Read` thêm file nào thật sự chưa quyết được.
