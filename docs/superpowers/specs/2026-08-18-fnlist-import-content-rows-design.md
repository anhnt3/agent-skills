# `fnlist-import`: dòng nội dung (content rows) + use-case con trong node lá

**Ngày**: 2026-08-18
**Phạm vi đợt này**: `speckit-extension` — `commands/fnlist-import.md`,
`scripts/fnlist_tree.py`, `scripts/fnlist_import.py`, `references/functions-schema.md`,
`scripts/tests/test_fnlist_import.py` (+ test mới cho `fnlist_tree.py` nếu tách file test).

`commands/code-intel.md` và `commands/srs-from-code.md` **không đụng tới trong đợt này** —
xem "Ngoài phạm vi" ở cuối tài liệu.

## Bối cảnh

Thử với dữ liệu thật (`Fnclist.xlsx`, sheet `UC`, 143 dòng) lộ ra hai lỗ hổng của
`fnlist-import` hiện tại:

1. **Không đọc được file có mã outline chỉ đánh ở dòng nhóm.** Cột `STT` trộn mã outline
   (`1`, `1.1`, `1.2.1`… — chỉ ở dòng tiêu đề nhóm, 30/142 dòng) và mã use-case (`uc001`…
   `uc112` — ở dòng nội dung thật, 112/142 dòng, không mang mã outline). `detect_hierarchy()`
   chấm điểm `outline` dưới ngưỡng 0.8 (thực tế ~0.21) nên không đề xuất nổi; kể cả ép chọn
   tay, `_level_and_name()` trả `level=None` cho dòng `uc001` và `build_tree()` ném lỗi cứng
   dừng toàn bộ. Ba kiểu phân cấp hiện có (`columns`/`outline`/`level`) đều giả định **mọi
   dòng tự khai cấp của chính nó** — file này thì chỉ dòng nhóm tự khai, dòng nội dung kế
   thừa cấp từ nhóm cha gần nhất.
2. **Thông tin nghiệp vụ thuần (BA) bị rơi mất từ vòng import, không có cơ hội thứ hai.**
   `srs-from-code.md` đã có quyết định tường minh (dòng 17-21): "mức quan trọng use case,
   loại UC theo quy ước BA, thời điểm sử dụng… code không thể tiết lộ" → ghi "Chưa có thông
   tin", không dừng hỏi — **đúng theo góc nhìn của nó** (chỉ đọc code). Nhưng dữ liệu này
   thực ra có sẵn trong file function list gốc lúc BA làm việc với khách, chỉ là
   `fnlist-import` hiện chỉ hỏi ánh xạ 2 cột `name`/`description`, không hỏi gì thêm — nên
   nó không bao giờ được thu thập.

`functions-diagram.md` (tạo tay, đối chiếu ý đồ) đã nêu đúng quy tắc mong muốn: "mọi đầu
mục đi thẳng xuống use-case (không có đầu mục con) đã gộp thành 1 chức năng lá" — tức nhiều
dòng `ucNNN` dưới một nhóm không có nhóm con phải gộp thành **một** node lá, không phải mỗi
`ucNNN` một node.

## Quyết định

### 1. "Dòng nội dung" — khái niệm mới, tách rời khỏi 3 kiểu phân cấp hiện có

Không thêm mode thứ tư. Thêm một trục độc lập, ghép được với `outline`/`level`/`columns`
(kiểu `staircase`) — mọi kiểu này đều đi qua `_level_and_name()`:

```json
{
  "hierarchy": {
    "mode": "outline",
    "column": 0,
    "unmatched_rows": "absorb"
  }
}
```

- Mặc định `unmatched_rows` = `"error"` — **giữ nguyên hành vi hiện tại** cho file cũ/đơn
  giản (mọi dòng đều đọc được cấp): dòng không đọc được cấp là lỗi cứng, dừng sạch.
- `"absorb"`: dòng không đọc được cấp theo kiểu đã chọn (`level=None` nhưng có `name`) →
  không phải lỗi — trở thành một mục trong mảng `use_cases` của node cha đang mở (đỉnh của
  `stack` khi duyệt). `stack` rỗng lúc gặp dòng này (chưa có nhóm cha nào mở) → lỗi rõ ràng,
  không đoán bừa.
- `columns` + `staircase` style: về mặt code cùng đi qua `_level_and_name()` như hai kiểu
  kia, nhưng **trên thực tế `unmatched_rows: "absorb"` không kích hoạt được ở kiểu này** —
  tên (`name`) của một dòng `columns` được suy ra TỪ CHÍNH ô của cột cấp vừa khớp (không có
  cột `name` riêng), nên dòng không khớp cột cấp nào cũng có `name` rỗng theo, rơi vào nhánh
  `if not name` ở `_build_leveled` và bị báo `skipped` ("ô tên chức năng trống") **trước khi
  chạm nhánh absorb**. Hậu quả vô hại (dòng vẫn được người dùng rà lại ở bước 5 của command),
  chỉ là absorb trong thực tế chỉ thật sự được khai thác ở `outline` và `level` — đừng dựa
  vào giả định nó cũng gộp use-case cho `columns`+`staircase`.
- `columns` + `repeated` style không áp dụng khái niệm này (đi qua `_build_repeated`, một
  hàm khác, đã có ngữ nghĩa "mọi dòng là lá" riêng — không đụng).

### 2. Schema `use_cases` trên node lá

```json
{
  "id": "FN-01-01",
  "name": "Nhóm chức năng Quản trị hệ thống và Người dùng",
  "description": "",
  "children": [],
  "use_cases": [
    {
      "id": "FN-01-01-UC-01",
      "name": "Quản lý danh sách người dùng",
      "description": "1. Quản trị hệ thống thao tác tạo mới...",
      "importance": "",
      "type": "",
      "usage_timing": ""
    }
  ]
}
```

- `use_cases` **vắng mặt** ở node không có dòng nội dung nào bên dưới — giữ nguyên "5
  trường, không hơn" cho phần lớn node như hiện tại; chỉ node nào thật sự gộp mới có thêm
  trường này.
- `importance` / `type` / `usage_timing` **chỉ ghi khi mapping có khai cột tương ứng và ô
  đó có giá trị**; không khai cột → bỏ hẳn trường trên mọi mục `use_cases` (không ghi
  `""` tràn lan), đúng tinh thần "vắng mặt = không có" của schema hiện tại.
- Một node **có thể vừa có `children` vừa có `use_cases`** (nhóm vừa chứa nhóm con vừa có
  vài dòng nội dung rời) — cho phép, không cấm, không cần hỏi thêm. Không có bằng chứng
  trường hợp này xảy ra trong `Fnclist.xlsx`, nhưng thuật toán nên xử lý được thay vì giả
  định "thuần khiết" rồi vỡ khi gặp file khác.

### 3. ID cho `use_cases` — dùng lại nguyên xi cơ chế `assign_ids` của FN

`UC-nn`, đánh số theo thứ tự trong node lá cha, ghép với ID node cha: `FN-01-01-UC-01`,
`FN-01-01-UC-02`… Bốn luật y hệt FN (chỉ đổi phạm vi từ "trong cây" thành "trong một node
lá"):

1. Import lại: use-case khớp theo **đường dẫn tên trong phạm vi node cha** (không phải toàn
   cây) giữ nguyên ID.
2. Use-case mới chèn giữa: số kế tiếp chưa dùng trong node cha đó, không dịch số của ai.
3. Use-case bị xoá: ID khai tử trong phạm vi node cha, không cấp lại.
4. Use-case đổi node cha (nhóm nội dung đổi vị trí lồng ghép): xử lý như "bỏ + thêm", ID
   mới — đúng tinh thần "chuyển nhóm" đã có ở FN.

Không dùng thẳng mã gốc trong Excel (`uc001`…) làm ID — mã này do BA gõ tay, không đảm bảo
ổn định giữa các lần sửa file nguồn, và không phải file function list nào cũng có cột mã
kiểu này.

**Hệ quả bắt buộc**: `walk()`, `assign_ids()`, `carry_status()`, `compute_retired()`,
`diff_trees()` trong `fnlist_tree.py` phải duyệt thêm `use_cases` bên cạnh `children`. Nếu
không, use-case đổi mô tả giữa hai lần import sẽ không hiện trong `diff`, và `status` của
use-case (nếu về sau có lệnh nào set) sẽ mất khi import lại — lặp đúng lớp lỗi mà thiết kế
FN hiện tại đã né.

`diff` mở rộng thêm loại `"use-case thêm"` / `"use-case bỏ"` / `"use-case đổi mô tả"`, tách
nhãn khỏi diff cấp FN để người đọc không lẫn "chức năng thêm/bớt" với "use-case con
thêm/bớt bên trong một chức năng không đổi".

### 4. Ánh xạ cột — hỏi hết, không chỉ name/description

`commands/fnlist-import.md` bước 2 thêm hai việc:

- **Tình huống bắt buộc hỏi thứ tư** (bên cạnh 3 tình huống đã có — nhiều sheet, header hai
  tầng, cột mô tả mơ hồ): gặp dòng không khớp kiểu phân cấp đã chọn → hỏi có phải "dòng nội
  dung, gộp vào nhóm cha làm use-case con" (`unmatched_rows: absorb`) hay là lỗi cấu trúc
  file cần người dùng sửa nguồn trước. Không tự suy luận.
- Sau khi chốt cột `name`/`description`/hierarchy, **quét các cột còn lại** (mọi cột trong
  `head` của `inspect`, không giới hạn ở cột đã dùng) và hỏi có cột nào khớp 1 trong 3 loại:
  Mức quan trọng, Loại UC, Thời điểm sử dụng UC. Không tự đoán tên cột khớp nghĩa —
  `inspect` đã in header + N dòng đầu cho mọi cột, đây là việc LLM đọc và hỏi xác nhận, không
  cần thêm thuật toán chấm điểm trong script (khác với chấm điểm hierarchy — 3 trường này là
  phân loại ngữ nghĩa tên cột, không phải pattern thống kê được).

`mapping.json.columns` mở rộng thêm 3 khoá tuỳ chọn cùng cấp với `name`/`description`:
`importance`, `type`, `usage_timing`. Trống/không khai → không ghi trường tương ứng.

### 5. Checkpoint cây (bước 3) hiển thị cả use_cases

Cây thụt lề mẫu 5 dòng hiện tại chỉ thụt theo `children`. Thêm: node lá có `use_cases` thì
in thêm các dòng con thụt sâu hơn, đánh dấu khác kiểu (vd tiền tố `·` thay vì gạch đầu dòng)
để phân biệt trực quan "nhóm/lá" với "use-case gộp bên trong lá" — đây là đúng chỗ dễ sai
nhất của đợt này (gộp nhầm nhiều use-case thành 1, hoặc tách nhầm 1 use-case thành nhiều
node lá).

### 6. Báo cáo `write` (bước 5)

Report JSON hiện tại: `out`, `written` (đếm qua `walk()`, chỉ tính node cây), `skipped`,
`retired`. `written` sẽ đếm rất ít so với tổng dòng thật nếu phần lớn dữ liệu rơi vào
`use_cases` (vd file mẫu: 30 node cây nhưng 112 dòng dữ liệu) — thêm trường
`written_use_cases` tách riêng, để không trông như thiếu dữ liệu.

## Sai lầm thường gặp (bổ sung vào danh sách đã có trong `fnlist-import.md`)

- **Coi dòng nội dung là lỗi cấu trúc khi thật ra file cố ý phân tầng kiểu "chỉ nhóm có
  mã"** → chọn `unmatched_rows: error` sai, dừng nhầm một file hợp lệ.
- **Ngược lại: chọn `absorb` cho một file mà dòng không khớp cấp thật sự là lỗi nhập liệu**
  → nuốt luôn dòng lỗi vào làm use-case, không ai phát hiện. Đây là lý do bước hỏi xác nhận
  không được bỏ qua dù `stack` đang mở sẵn một node hợp lý để gắn vào.
- **Bỏ qua quét cột bổ sung (Mức quan trọng/Loại UC/Thời điểm sử dụng)** → lặp lại đúng lỗ
  hổng đang sửa: thông tin có sẵn trong Excel nhưng không bao giờ được hỏi, xuống
  `srs-from-code` lại thành "Chưa có thông tin".
- **Trình checkpoint cây bước 3 mà không hiện `use_cases`** → giấu đúng chỗ dễ sai nhất của
  đợt này.
- **Sửa `assign_ids`/`carry_status`/`diff_trees` chỉ cho `children`, quên `use_cases`** →
  use-case mất `status`/đổi ID vô cớ qua các lần import lại, lặp lại lớp lỗi FN đã né.

## Test cần thêm

`test_fnlist_tree.py` (hoặc file test hiện có, tuỳ cấu trúc):

- `unmatched_rows: absorb` với pattern giống `Fnclist.xlsx` thu nhỏ: nhóm lồng 2-4 cấp, xen
  kẽ dòng nội dung không có mã outline → đúng node lá nào gộp đúng use-case nào, đúng cấp.
- `unmatched_rows` mặc định (`error`, không khai) trên cùng dữ liệu → vẫn dừng với lỗi như
  hành vi cũ (không phá file/test hiện có).
- `stack` rỗng gặp dòng nội dung ngay từ đầu (chưa mở nhóm nào) → lỗi rõ ràng, không crash
  kiểu khác (vd `IndexError`).
- Node vừa có `children` vừa có `use_cases`.
- ID `use_cases` ổn định qua hai lần `write` liên tiếp (đường dẫn tên không đổi → ID không
  đổi); use-case mới chèn giữa → số kế tiếp, không dịch use-case khác; use-case bị xoá → vào
  `retired_ids` theo đúng định dạng ID đầy đủ (`FN-01-01-UC-01`), không cấp lại.
- `diff_trees` báo đúng use-case thêm/bớt/đổi mô tả, tách nhãn khỏi diff cấp FN.
- 3 cột bổ sung (`importance`/`type`/`usage_timing`): có mapping → ghi đúng giá trị; không
  mapping → trường vắng mặt hoàn toàn trên mọi `use_cases` item (không ghi `""`).

`test_fnlist_import.py` (CLI-level, nếu có fixture xlsx/csv riêng): một ca `write` end-to-end
mô phỏng đúng shape `Fnclist.xlsx` (nhóm outline xen dòng nội dung, 2 trong 3 cột bổ sung có
mapping) → kiểm report JSON có `written_use_cases`, file `functions.json` ra đúng cấu trúc.

## Ngoài phạm vi

- **`code-intel`/`srs-from-code` đọc và dùng `use_cases`** (đặc biệt là đối chiếu với cơ chế
  `S-n` ("chức năng nhỏ") hiện `srs-from-code` đang suy hoàn toàn từ code qua `intel.md`,
  không đọc gì từ Excel) — để đợt sau, viết spec riêng. Đây là quyết định tinh tế (use-case
  BA khai và nhánh `S-n` suy từ code có phải cùng một khái niệm không, đối chiêu thế nào khi
  hai nguồn lệch nhau) không nên làm vội chung với đợt sửa `fnlist-import`. Người dùng chủ
  động chọn tách theo lệnh, "sửa từng command một cho đỡ lẫn".
- Migration `functions.json` đã ghi từ trước đợt này (chưa có `use_cases`) — import lại từ
  file Excel gốc là đủ, không cần script migrate riêng (đúng tiền lệ đã có ở thiết kế
  2026-08-11).
- Đặt tên khoá tiếng Anh khác cho `type`/`usage_timing` nếu người dùng muốn đổi lúc viết
  command — không phải quyết định kiến trúc, sửa tự do khi triển khai.

## Rủi ro

- **`unmatched_rows: absorb` là điểm dễ nuốt nhầm lỗi nhập liệu nhất** — một dòng đáng ra
  phải là nhóm cấp mới (nhưng người nhập quên đánh mã outline) sẽ lặng lẽ rơi vào
  `use_cases` của nhóm sai. Checkpoint cây bước 3 (mục 5) là hàng phòng thủ chính; không có
  cách nào script tự phát hiện được ca này vì về mặt dữ liệu nó hợp lệ.
- **Mở rộng `diff`/`carry_status`/`compute_retired` sang `use_cases` tăng bề mặt code cần
  đúng đồng thời với FN** — rủi ro chủ yếu là quên một trong bốn hàm khi sửa, che giấu bởi
  test hiện tại chỉ phủ `children`. Test mới ở trên nhắm thẳng vào từng hàm.
