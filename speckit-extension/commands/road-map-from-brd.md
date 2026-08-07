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

Kỳ vọng: **đường dẫn thư mục BRD**, mặc định `docs/brd` khi để trống.
Thư mục không tồn tại, hoặc không có `brd.manifest.yml` → **hỏi lại**, KHÔNG tự đi tìm
thư mục khác trong repo.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/brd_roadmap.py`.
Thư mục làm việc tạm: `.specify/tmp/roadmap-brd/`.

### 0. Chặn đầu vào

`docs/roadmap.md` **đã tồn tại** → **DỪNG NGAY**. In đường dẫn file cũ và nói rõ: lệnh này
KHÔNG merge vào roadmap có sẵn; muốn sinh lại thì người dùng tự đổi tên hoặc xoá file cũ.
Không hỏi "có muốn ghi đè không" — không ghi đè là quyết định đã chốt.

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
được im lặng bỏ qua** — chúng đổi cách hiểu cây. Đừng đọc lại toàn bộ `outline.json` nếu dòng
tóm tắt đã cho biết cả hai danh sách đều rỗng.

### 2. Quét codebase — CHỈ để suy phụ thuộc

Tìm trong codebase: auth/đăng nhập, phân quyền, entity/service dùng chung, module đã dựng.
Ghi nhận cái gì **đã có** để biết cái gì chặn cái gì.

- Không có codebase (repo mới, chỉ có `docs/`) → **bỏ qua bước này và nói thẳng**
  "chưa có codebase, phụ thuộc suy hoàn toàn từ BRD". KHÔNG hỏi vòng vo, KHÔNG dừng.
- **CẤM** dùng codebase để thêm item, bớt item, hay đặt cột `Trạng thái`. Màn có trong code
  mà không có trong BRD → chỉ **báo miệng** cho người dùng biết, KHÔNG ghi vào file.

### 3. Phân loại ứng viên

Mỗi node trong `outline.json` (bỏ qua node `kind: root`) rơi vào đúng một nhóm:

- **là màn** → một item roadmap
- **chứa k màn** → tách thành k item, mỗi item trỏ về cùng file kèm `#heading` khác nhau
- **không phải màn** → ghi vào `decisions.json` kèm **lý do cụ thể** (vd "từ điển thuật ngữ",
  "yêu cầu phi chức năng", "mục giới thiệu phạm vi")

Căn cứ: `signals` (bảng trường, nút thao tác, phân quyền, ảnh), `headings`, `head`, `chars`.
Outline chưa đủ để quyết một node → **`Read` thẳng file đó** theo `path`. CẤM đoán.

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

Trình cho người dùng **ĐẦY ĐỦ, không cắt bớt** hai bảng:

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

Rồi hỏi qua **AskUserQuestion**: **ranh giới wave** và **các cặp thứ tự có ràng buộc phụ thuộc**
là quyết định trọng yếu — phải hỏi. Vị trí tương đối trong cùng một wave đã nằm trong bảng đề
xuất — người dùng chỉnh trực tiếp, không tốn mỗi item một lượt hỏi.

Mỗi câu 2–4 option kèm lý do + trade-off; `(Recommended)` CHỈ khi có căn cứ và nêu căn cứ ngay
trong option. **Thứ tự là quyết định của người dùng** — chờ **phản hồi thật**; chưa có phản hồi
→ DỪNG, **KHÔNG ghi file**.

### 6. Ghi `docs/roadmap.md` theo khung CỐ ĐỊNH

**Dùng khung cố định, KHÔNG tự chế cấu trúc:**

- Lấy khung: chạy `specify preset resolve roadmap-template` để lấy đường dẫn file khung; không
  resolve được → đọc `.specify/extensions/dft-speckit/templates/roadmap-template.md`; vẫn không
  thấy → hỏi.
- Copy đúng cấu trúc khung (bảng tổng + khối chi tiết mỗi item), chỉ **điền** placeholder `[…]`,
  thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **ID ổn định** `RM-001`, `RM-002`, … cấp tăng dần theo thứ tự trong bảng tổng, khớp giữa bảng
  tổng và khối chi tiết.
- **Trường `Nguồn`** của mỗi item: đường dẫn tương đối từ gốc repo tới file BRD nguồn
  (`docs/brd/03-quan-ly/05-danh-sach.md`), thêm `#<tiêu đề mục>` khi nhiều item cùng trỏ về một
  file. Node không có file riêng (`inline`) thì trỏ vào thư mục của nó (`docs/brd/03-quan-ly/`).
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
- **Nuốt `warnings` cho gọn báo cáo** → người dùng mất thông tin cần để quyết.
- **Đọc toàn văn mọi file BRD** → vỡ context rồi bỏ sót mục cuối. Đọc `outline.json` trước,
  chỉ `Read` thêm file nào thật sự chưa quyết được.
