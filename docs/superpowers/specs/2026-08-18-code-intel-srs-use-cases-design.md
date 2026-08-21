# `code-intel`/`srs-from-code`: dùng `use_cases[]` làm khung S-n bắt buộc

**Ngày**: 2026-08-18
**Phạm vi đợt này**: `speckit-extension` — `commands/code-intel.md`, `commands/srs-from-code.md`,
`scripts/intel_tree.py` (+ test tương ứng). Đây chính là "đợt sau" đã hoãn tường minh ở
`docs/superpowers/specs/2026-08-18-fnlist-import-content-rows-design.md` §"Ngoài phạm vi".

## Bối cảnh

Đợt trước đã thêm `use_cases[]` vào `functions.json` (BA khai từ Excel, gộp trong node lá,
gồm `name`/`description` + tuỳ chọn `importance`/`type`/`usage_timing`). Nhưng **chưa lệnh
nào đọc trường này**:

- `code-intel §12` (Kịch bản Use Case) sinh **hoàn toàn từ code** (§2 màn hình + §5 luồng) —
  không đối chiếu `use_cases[]`.
- `Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng` bị hard-code "Chưa có thông tin" ở cả hai
  lệnh (`code-intel §12` và `srs-from-code` bước 5/6) — đúng lỗ hổng đợt trước sinh ra để vá,
  nhưng dữ liệu không chảy tới được vì không lệnh nào đọc `use_cases[]`.
- `intel_tree.py` (`is_leaf`, `compute_paths`, `propose`, `units`) chỉ đi theo `children`,
  hoàn toàn không biết `use_cases[]` tồn tại.

Người dùng cung cấp `srs.md` mẫu (tạo tay, gốc repo) xác nhận: một leaf gộp nhiều `use_cases[]`
(vd `FN-01-01` gộp 4 use-case thật từ Excel) chỉ sinh **một** khối `#####` — đúng khớp cơ chế
"chức năng nhỏ = nhánh `S-n`" đã có sẵn trong `srs-from-code` (đợt trước, commit `040879c` đã
làm xong phần co giãn cấp heading `##`→`#####` theo độ sâu cây, không cần sửa lại). Chỉ là cơ
chế `S-n` hiện tự suy hoàn toàn từ code, chưa biết `use_cases[]` tồn tại.

## Quyết định

### 1. Việc nặng nằm ở `code-intel`, không phải `srs-from-code`

Tìm bằng chứng theo từng nhánh `S-n` xảy ra ở `code-intel` (nơi quét code). `srs-from-code`
chỉ cần một thay đổi cơ học: thôi hard-code "Chưa có thông tin" cho 3 field, rót nguyên văn
giá trị `intel §12` đã ghi.

### 2. `intel_tree.py` — expose `use_cases[]` theo từng leaf

Thêm khả năng đọc `use_cases[]` của một node lá, dùng ở hai chỗ:
- `code-intel` bước 1: hiển thị trong cây xác nhận (mục 3 dưới đây).
- `code-intel` bước 5: lấy làm khung `S-n`, không tự parse `functions.json` bằng tay lần nữa
  (giữ đúng nguyên tắc hiện có: "đây là dữ liệu dùng để điền, không tự đọc lại bằng mắt rồi
  gõ tay").

Không thay đổi ngữ nghĩa `is_leaf`/`compute_paths`/`propose`/`units` hiện có (những hàm này
tiếp tục chỉ đi theo `children`, đúng vai trò "unit = một nhánh cây FN" không đổi) — chỉ thêm
khả năng đọc `use_cases[]` bên cạnh, không thay thế.

### 3. Checkpoint xác nhận cấu trúc TRƯỚC khi quét — bắt buộc, không tuỳ chọn

Mở rộng bước 1 hiện có của `code-intel` (đang xác nhận ranh giới unit qua cây thụt lề, dùng
AskUserQuestion) — với mỗi leaf trong unit đề xuất có `use_cases[]`, in thêm các dòng con
thụt sâu hơn, đánh dấu `·` (đúng quy ước vừa thêm ở checkpoint của `fnlist-import`). Người
dùng xác nhận/điều chỉnh **trước khi quét bắt đầu** — tận dụng đúng checkpoint đã có, không
thêm bước hỏi riêng.

Đây là cấu trúc **đã biết trước** (đọc thẳng từ `functions.json`, không phụ thuộc kết quả
quét) — khác với mục 4 dưới đây (cấu trúc chỉ lộ ra sau khi quét), lý do hai cơ chế xác nhận
khác nhau (chặn trước / gộp báo cáo cuối) không mâu thuẫn nhau.

### 4. `code-intel §12`: `use_cases[]` làm khung `S-n` bắt buộc

- **Leaf có `use_cases[]`** → danh sách nhánh `S-n` **cố định** theo đúng tên/thứ tự các item
  đó (không tự phát minh thêm cách chia nhỏ khác). Quét code để tìm bằng chứng khớp **từng
  nhánh** — không còn tự do khám phá "màn hình nào sinh ra bao nhiêu use case" như hiện tại.
- **Nhánh không tìm thấy bằng chứng code** → **vẫn giữ nhánh đó** trong `d.`/`e.`/`f.` (không
  âm thầm bỏ), ghi rõ "chưa tìm thấy hiện thực" ngay tại nhánh — nhất quán với quy ước đã có
  ở cấp FN/Chức năng ("Chưa tìm thấy hiện thực trong mã nguồn."), chỉ áp xuống tận cấp `S-n`.
- **`Mức quan trọng`/`Loại UC`/`Thời điểm sử dụng`** → lấy từ đúng item `use_cases[]` khớp
  nhánh đó nếu có giá trị (khi mapping Excel có khai cột và ô có giá trị); không có → vẫn
  "Chưa có thông tin" như cũ.
- **Leaf không có `use_cases[]`** → giữ nguyên hành vi hiện tại (tự khám phá `S-n` từ code,
  không đổi gì) — đây là đường tương thích ngược, đảm bảo `functions.json` cũ (chưa qua đợt
  `fnlist-import` mới, hoặc dùng mode không absorb) vẫn chạy được y hệt trước.
- **Code tìm thấy nhiều `S-n` hơn Excel khai** (chỉ biết được SAU khi quét, không thể biết
  trước lúc xác nhận cấu trúc ở mục 3): **không chặn quét lại** — vẫn thêm nhánh đó ngay
  (đặt sau các nhánh từ Excel, không âm thầm bỏ khớp với quy ước hiện có "không tìm thấy
  bằng chứng thì đưa xuống câu hỏi, không phải xoá"), nhưng dồn **toàn bộ** các nhánh phát
  sinh thêm của unit vào **đúng một lượt hỏi** ở báo cáo cuối bước 11 (đúng triết lý gộp báo
  cáo đã có cho `intel §10`) — liệt kê rõ leaf nào, nhánh `S-n` tên gì, hỏi người dùng có giữ
  hay cập nhật ngược vào function list Excel. **Không hỏi giữa lúc sinh** (mâu thuẫn với
  nguyên tắc "bước 5-8 không AskUserQuestion" đã có ở cả hai lệnh, đặc biệt vỡ khi chạy song
  song — subagent không có ai để hỏi trực tiếp).

### 5. `srs-from-code`: thôi hard-code 3 field

Bước 5 hiện ghi "Ba field của §12 luôn ghi cố định 'Chưa có thông tin' khi rót sang `d.`" →
đổi thành: **rót nguyên văn giá trị `intel §12` đã ghi** cho use case này — có thể là giá trị
thật (nếu `code-intel` mục 4 ở trên tìm được khớp có giá trị) hoặc vẫn "Chưa có thông tin"
(nếu không khớp được hoặc `intel §12` sinh theo đường tự khám phá cũ, không có `use_cases[]`
nguồn). `srs-from-code` không tự tra `functions.json` — chỉ rót đúng những gì `intel.md` đã
ghi, giữ nguyên ranh giới nội bộ/giao khách hiện có.

### 6. Ghi ngược `status` xuống tận `use_cases[]` item (mở rộng nhỏ, nhất quán với hạ tầng đã có)

Đợt trước đã mở rộng `walk()`/`assign_ids()`/`carry_status()`/`compute_retired()` trong
`fnlist_tree.py` để `use_cases[]` có ID ổn định và mang được `status` — `fnlist_import.py
update --set FN-01-01-UC-01=intel` đã chạy đúng ngay hôm nay dù chưa lệnh nào gọi nó với ID
dạng này. Đợt này tận dụng luôn: ở bước 10 (ghi ngược trạng thái) của cả hai lệnh, với mỗi
nhánh `S-n` **khớp được với một `use_cases[]` item cụ thể** (tìm thấy hoặc không tìm thấy code
đều tính là "đã xử lý" nhánh đó), gọi thêm `--set <id-use-case>=intel` (hoặc `=srs`) cho ID
`use_cases[]` item đó, bên cạnh `--set <FN-ID-leaf>=...` như hiện tại. Nhánh `S-n` tự khám
phá từ code (leaf không có `use_cases[]` nguồn) thì không có ID `use_cases[]` nào để set —
bỏ qua, chỉ set FN-ID leaf như cũ.

## Ngoài phạm vi

- Sửa `intel_verify.py`/`srs_verify.py` để thêm cổng kiểm riêng cho khớp `use_cases[]` ↔
  `S-n` (vd chặn nếu số nhánh `S-n` ít hơn số `use_cases[]` khai) — để đợt sau nếu thực tế
  dùng cho thấy cần; đợt này chỉ đổi luật sinh nội dung, chưa thêm cổng kiểm mới.
- Đổi cách `intel_tree.py propose`/`units` đề xuất ranh giới UNIT (cấp FN, không phải cấp
  use-case) — không đổi, `use_cases[]` không ảnh hưởng khái niệm "unit".
- Case một `use_cases[]` item ứng với NHIỀU màn hình thật (hiếm, chưa có bằng chứng) — xử lý
  theo đúng luật hiện có của `d.` (một bảng, các màn liên quan rải vào `e.`/`f.` theo từng
  `S-n`), không thiết kế thêm quy tắc riêng.

## Rủi ro

- **Đổi luật sinh `S-n` là điểm dễ vỡ nhất của `intel_verify.py`'s `check_section8_cap`** —
  nhánh "không tìm thấy" giờ không còn tự động rơi xuống §8 (mục 4 ở trên đã chốt: giữ ngay
  tại nhánh, không đưa xuống §8) nên không ăn vào trần `max(3, M/3)` — nhưng cần review lại
  `intel_verify.py` khi viết plan để xác nhận cổng cũ không vô tình chặn nhầm nội dung mới
  (vd `check_section12_coverage` có giả định gì về số khối `###`/nhánh không).
- **`srs_verify.py`'s `nhieu-use-case-mot-leaf`** (nhiều hơn một bảng use-case trong `d.`) đã
  có sẵn cổng chặn đúng cái đợt này KHÔNG được vi phạm — `use_cases[]` làm khung `S-n` vẫn
  phải gộp về đúng MỘT bảng `d.` cho mỗi leaf, không phải một bảng riêng cho mỗi
  `use_cases[]` item. Giữ nguyên gate này, không sửa.
