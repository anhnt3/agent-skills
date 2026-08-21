# Thiết kế lại `code-intel`: quét theo cây `functions.json`, gọn hoá, hàng loạt

**Ngày**: 2026-08-12
**Phạm vi**: `speckit-extension` — `commands/code-intel.md`, `templates/intel-template.md`,
hai script mới `scripts/intel_tree.py` + `scripts/intel_verify.py`, `extension.yml`.

`srs-from-code.md` **không đổi trong đợt này** — vẫn đọc `.specify/docs/<cụm>/intel.md`
theo đường dẫn cũ; đường dẫn mới do đợt này tạo ra sẽ làm `srs-from-code` không tìm thấy
`intel.md` ở chỗ nó mong đợi. Đây là "khoảng đứt" thứ hai của cùng một dây chuyền (nối
tiếp khoảng đứt `fnlist-import` → `code-intel` đã ghi trong
`docs/superpowers/specs/2026-08-11-fnlist-json-design.md`), và cách xử lý giống hệt: nói
rõ trong bước kết thúc của `code-intel`, không nhắc chạy `srs-from-code`.

## Bối cảnh

Đợt trước đã đổi `fnlist-import` sang sinh `.specify/docs/functions.json` — cây chức năng
lồng `children`, ID đa cấp ổn định (`FN-01`, `FN-01-01`). `code-intel` hiện tại (386 dòng)
vẫn xây hoàn toàn quanh mô hình cũ: `functions.md` (bảng phẳng có cột `Cụm`/`Nguồn code`/
`Trạng thái`), tham số `<tên-cụm> <danh-sách-FN>` do người dùng gõ tay, và bước ghi ngược
sửa nhiều ô trên file dùng chung có xác nhận riêng.

Bốn thay đổi được yêu cầu, đều xuất phát từ việc chuyển sang cây:

1. Tối ưu template gọn hơn, bớt lặp.
2. Phân chia rõ việc nào Python làm, việc nào LLM làm.
3. Dùng subagent/loop quét hàng loạt toàn bộ function list, không chỉ một cụm mỗi lần gọi.
4. Thư mục sinh ra đánh số theo đúng cấu trúc `functions.json`, không còn tên cụm gõ tay.

## Quyết định

### 1. Hợp nhất mô hình tham số: một FN-ID đánh dấu điểm bắt đầu quét

Bỏ hẳn `<tên-cụm> <danh-sách-FN>`. Tham số mới là **một FN-ID duy nhất** (tuỳ chọn):

- Trống → điểm bắt đầu là **gốc cây** — quét toàn bộ dự án.
- `FN-01` → chỉ quét nhánh đó.
- Một FN-ID lá (không có con) → quét đúng một unit (chính nó).

Không còn khái niệm "cụm gõ tay" nữa. "Cụm" bây giờ *là* một node trong cây — tên và vị
trí của nó xác định từ `functions.json`, không phải chuỗi tự do người dùng đặt.

### 2. Đơn vị sinh `intel.md` (unit): node cha trực tiếp của lá

Một **unit** là node thoả một trong hai:

- Có con, và **toàn bộ con đều là lá** (không có cháu).
- Không có con (chính nó là lá đứng một mình, không có node cha-của-lá nào bao nó).

Thuật toán mặc định, đệ quy từ node bắt đầu:

```
default_units(node):
    nếu node không có con:            trả [node]
    nếu mọi con của node đều là lá:   trả [node]
    ngược lại:                        nối default_units(c) cho từng con c
```

Một lá đứng lẻ dưới một cha có con hỗn hợp (vài con là lá, vài con có cháu) tự thành một
unit riêng một mình — không bị gộp lên cha. Unit dạng này chỉ phủ đúng **một** FN-ID
(`M = 1`) — `intel_tree.py units` vẫn trả về danh sách FN-ID dạng mảng, chỉ có đúng một
phần tử.

**Đây chỉ là đề xuất, không phải quyết định cuối.** Trước khi quét, LLM trình cây thụt lề
có đánh dấu ranh giới unit đề xuất, hỏi qua AskUserQuestion người dùng xác nhận hoặc yêu
cầu gộp/tách lại. Điều chỉnh hợp lệ: chọn một tập node khác làm "root" của unit (sâu hơn
hoặc cao hơn đề xuất mặc định), miễn mỗi root vẫn tạo ra một nhánh cây hợp lệ. Gộp hai
nhánh **không phải anh em** (không cùng một tổ tiên trực tiếp) vào một `intel.md` **không
được hỗ trợ** — mỗi unit luôn ánh xạ đúng một nhánh cây, một thư mục.

### 3. Cấu trúc thư mục: lồng đúng độ sâu cây thật, đánh số theo vị trí

```
.specify/docs/
  01-quan-ly-don-hang/
    01-danh-sach-don/
      intel.md
    02-tao-don-moi/
      intel.md
  02-ai-service/
    01-tro-ly-ao/
      intel.md
  05-dang-xuat/
    intel.md              ← lá đứng một mình, không thêm cấp con
```

- Độ sâu thư mục = độ sâu thật của node trong cây tại nhánh đó — **không cố định 2 cấp**.
  Cây 4 cấp thì thư mục cũng lồng 4 cấp trước khi tới `intel.md`.
- Tên thư mục: `<hai-chữ-số-vị-trí>-<slug>`. Số vị trí lấy theo **chỉ số trong mảng
  `children`** của cha (0-based + 1, khớp thứ tự dòng file nguồn) — không phải số trong
  FN-ID (FN-ID có thể đổi khi cấp lại theo luật `fnlist-import`, vị trí hiển thị thì không
  cần khớp FN-ID).
- Slug: Python sinh tất định (không giao LLM đặt tên) — chuyển tên tiếng Việt có dấu
  (kể cả `đ`/`Đ`) sang không dấu, thường hoá, khoảng trắng/ký tự lạ → `-`, gộp `-` liền
  nhau, cắt `-` đầu/cuối. Hai node anh em trùng slug sau khi sinh (hiếm, tên khác nhau
  nhưng chuyển thành slug giống nhau) → hậu tố `-2`, `-3`… theo thứ tự xuất hiện.
- Lý do đặt slug ở Python, không phải LLM: chạy lại phải ra **đúng thư mục cũ** để
  no-clobber hoạt động. LLM tự đặt tên mỗi lần một kiểu là phá cơ chế chạy lại.

### 4. Phân chia Python / LLM

**`scripts/intel_tree.py`** (mới, tái dùng `walk`/`name_path`/`find_by_id` từ
`fnlist_tree.py` cùng thư mục `scripts/`) — thuần tính toán, không tìm code, không viết
nội dung:

- `propose` — từ node bắt đầu (hoặc gốc), chạy thuật toán mặc định §2, trả về danh sách
  root đề xuất kèm cây thụt lề có đánh dấu ranh giới, để LLM trình cho người dùng.
- `units` — nhận danh sách root đã người dùng xác nhận (có thể khác đề xuất mặc định),
  với mỗi root tính: đường dẫn thư mục đầy đủ (đánh số + slug), danh sách FN-ID lá thuộc
  nhánh đó kèm `name`/`status` hiện tại. Đây là dữ liệu LLM dùng để điền §1 của
  `intel.md` — không tự đọc lại `functions.json` bằng mắt mà gõ nhầm.

**`scripts/intel_verify.py`** (mới, cùng vai trò `srs_verify.py` cho `srs.md`) — chấm một
`intel.md` đã viết, hai mức:

- **BLOCKING** (exit khác 0): còn placeholder `[...]`; §1 thiếu/thừa dòng so với danh sách
  FN-ID lá thật của unit (đối chiếu `functions.json` qua `--root`); trần §8 (đếm dòng gắn
  nhãn `[không suy được từ code]` so với `max(3, 1/3 × M)` — giữ nguyên công thức của bản
  hiện tại, `M` = số FN-ID lá thuộc unit, ≥3 mục dùng cùng một chuỗi lý do); tỉ lệ "không
  tìm thấy" ở §1 vượt 1/3 `M`; no-clobber §8/§10 (mục cũ trong bản chụp trước khi ghi —
  truyền qua `--before <snapshot>` — phải còn khớp nguyên văn trong bản mới, số mục không
  giảm).
- **WARNING** (exit 0, in ra để LLM cân nhắc): cite trông không giống `file:dòng` hợp lệ;
  FN tìm thấy nhưng không xuất hiện ở §2 lẫn giải trình §7/§8.

LLM giữ nguyên toàn bộ phần cần phán đoán: thang tìm kiếm 4 nấc (tên Việt → file ngôn ngữ
→ route/permission → entity → dịch tiếng Anh Grep trực tiếp), quyết đọc-thẳng hay suy-đoán
theo có token đỡ khẳng định hay không, viết §2–§7 và §9, nhận diện phát hiện §10 (logic
mâu thuẫn/lỗ hổng bảo mật thấy được tình cờ). Trước khi báo xong, LLM chạy
`intel_verify.py` thay vì tự đếm bằng lời văn; BLOCKING thì sửa rồi chấm lại.

### 5. Ghi ngược trạng thái: gọi thẳng, không xác nhận riêng

Bản cũ bắt buộc một lượt AskUserQuestion trước khi ghi ngược `functions.md`, vì đó là sửa
ba ô (`Cụm`/`Nguồn code`/`Trạng thái`) trên file dùng chung — sai là hỏng dữ liệu nhiều
cụm khác. `functions.json` không còn hai cột đầu; chỉ còn một cờ `status`. Sau khi
`intel_verify.py` pass, gọi thẳng:

```bash
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json --set FN-01-01=intel
```

Không hỏi xác nhận riêng — `update` tự validate (ID tồn tại, status hợp lệ), và đổi status
là hành vi hoàn toàn có thể lùi lại (chạy `update` lần nữa). Vẫn giữ luật **không lùi
trạng thái**: nếu node đang `srs` (đã qua `srs-from-code`), không gọi `update` đặt lại
`intel` — script `intel_tree.py units` đã trả sẵn `status` hiện tại của từng FN để LLM
biết bỏ qua ca này.

### 6. Batch: hỏi song song hay tuần tự tại thời điểm chạy

Sau khi danh sách unit đã chốt (bước 2), nếu có ≥ 2 unit → hỏi qua AskUserQuestion: chạy
song song (mỗi unit một subagent độc lập, dùng Agent tool) hay tuần tự (xử từng unit một,
loop). Không cố định sẵn trong lệnh — người dùng quyết mỗi lần chạy theo quy mô dự án và
mong muốn theo dõi tiến độ. Đúng 1 unit thì không hỏi, chạy thẳng.

Mỗi unit chạy đúng quy trình rút đặc tả hiện có (không đổi): thang tìm kiếm, ba dạng cite,
§10, no-clobber, verify, ghi `intel.md` + gọi `update`.

### 7. Phần giữ nguyên, phần rút gọn

**Giữ nguyên** (logic lõi, không đổi trong đợt này):
- Kỷ luật ba dạng (đọc thẳng / suy đoán / không căn cứ) và tiêu chí "cite có token đỡ".
- Thang tìm kiếm 4 nấc.
- §10 phát hiện logic mâu thuẫn/lỗ hổng bảo mật, ranh giới với §8, cơ chế no-clobber nội
  dung tự do (mục cũ giữ nguyên khi chạy lại) — nay do `intel_verify.py` xác minh thay vì
  LLM tự so bằng mắt.
- §4 cột "Độ chắc chắn" (chắc/suy đoán), luật không rót suy đoán thẳng vào `srs.md`.
- Mỏ neo phân tán §2 (một dòng gánh quá 1/2 `M` khi `M ≥ 4` phải cite riêng từng FN).

**Rút gọn / bỏ hẳn** (nhờ chuyển sang cây + hai script mới):
- Toàn bộ "Validate cứng" về cú pháp tên cụm, cú pháp khoảng FN kiểu bảng phẳng
  (`FN-003..FN-012` theo thứ tự dòng), cảnh báo "FN đã có cụm khác", "đầu vào là tên
  nhóm không tự nở" — thay bằng: validate FN-ID khớp `^FN(?:-\d{2})+$` và tồn tại trong
  `functions.json`, còn lại là `intel_tree.py propose`/`units`.
- Bước 7 "Ghi ngược `functions.md` có xác nhận trước" (bảng 3 cột, mỏ neo đếm dòng) — thay
  bằng một lệnh `update --set`, không xác nhận riêng (§5).
- §1 không còn cần tham số `<danh-sách-FN>` gõ tay — `intel_tree.py units` liệt kê sẵn.
- Phần "Kiểm lại trước khi báo xong" hiện tự đếm bằng lời văn (trần §8, no-clobber, mỏ
  neo phủ) — thay bằng gọi `intel_verify.py`, mục "Sai lầm thường gặp" chỉ giữ những sai
  lầm còn khả năng xảy ra với luồng mới (bỏ các mục nói về `functions.md`/cụm gõ tay).

Mục tiêu: giảm số dòng đáng kể (ước lượng còn ~55-65% so với 386 dòng hiện tại) bằng cách
xoá phần đã chuyển sang script, không xoá phần đòi phán đoán.

## Không làm trong phạm vi này

- `srs-from-code.md` không đổi — đường dẫn `intel.md` mới (`.specify/docs/<đường-dẫn-
  cây>/intel.md` thay vì `.specify/docs/<cụm>/intel.md`) sẽ cần một đợt cập nhật riêng.
- Không có cơ chế đồng bộ giữa các subagent chạy song song — xem "Rủi ro".
- Không tự động di trú các `intel.md` đã sinh theo cấu trúc cụm cũ (`.specify/docs/<tên-
  cụm-gõ-tay>/intel.md`) sang cấu trúc cây mới. Dự án đã có `intel.md` kiểu cũ thì giữ
  nguyên, không đụng.

## Rủi ro

- **Ranh giới unit không ổn định qua các lần `fnlist-import` re-import.** Nếu cấu trúc cây
  đổi tại đúng một unit boundary (vd một node trước đây là "cha-của-lá" nay có thêm cháu vì
  người dùng thêm chức năng con trong Excel), lần `code-intel` kế tiếp trên nhánh đó sẽ đề
  xuất một unit khác — thư mục cũ và thư mục mới có thể không trùng nhau. Không tự động di
  trú nội dung `intel.md` cũ sang vị trí mới; người dùng phải tự đối chiếu. Bước xác nhận
  cây (§2) sẽ lộ ra khác biệt này (thư mục đề xuất khác thư mục đã có), nhưng không có gì
  ép người dùng phải nhận ra và xử lý.
- **Subagent chạy song song không thấy phát hiện của nhau.** Hai unit dùng chung một entity
  hoặc một luồng nghiệp vụ có thể cite khác nhau, hoặc lặp lại cùng một phát hiện §10 ở hai
  nơi. Chấp nhận là giới hạn đã biết, không thêm bước đồng bộ/tổng hợp trong đợt này.
- **Slug trùng lặp giữa các node không phải anh em** không phải vấn đề (thư mục lồng theo
  cây nên không đụng đường dẫn), nhưng slug quá dài (tên chức năng dài) cần cắt bớt —
  `intel_tree.py` phải giới hạn độ dài slug để tránh lỗi đường dẫn quá dài trên một số hệ
  điều hành.
