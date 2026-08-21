# Đợt 3B-1: di trú `srs-from-code`/`srs_verify.py` sang mô hình cây `functions.json`

**Ngày**: 2026-08-12
**Phạm vi**: `speckit-extension` — `commands/srs-from-code.md`, `scripts/srs_verify.py`,
`scripts/tests/test_srs_verify.py`.

Đây là **đợt 3B-1**, tiền đề bắt buộc cho 3B-2 (thêm §12 "Kịch bản Use Case" vào
`code-intel`) và 3B-3 (viết lại khuôn tài liệu `srs-template.md`/`srs-from-code.md` theo
2 cấp Chức năng → Màn hình của tài liệu ban hành thật). Không đụng khuôn tài liệu
(I-VI/N.1-N.7), không đụng `srs-template.md`, không đụng `intel_tree.py`.

## Bối cảnh

Đợt 1 (`fnlist-import`) đã thay `functions.md` phẳng bằng `functions.json` dạng cây,
ID nhiều cấp (`FN-01-01`). Đợt 2 đã viết lại `code-intel` để dùng mô hình cây này (một
FN-ID gốc, `intel_tree.py propose`/`units`, batch qua subagent). Nhưng `srs-from-code.md`
và `srs_verify.py` **chưa được đụng tới** — cả hai vẫn giả định `functions.md` phẳng và
tham số `<tên-cụm>`:

- `srs-from-code.md` nhận `<tên-cụm> [--template ...]`, đọc `functions.md`, và ở bước 8
  tự tay sửa cột "Trạng thái" trong `functions.md`.
- `srs_verify.py` có `FN_ID_RE = r"\bFN-\d{3,}\b"` (khớp `FN-001`, không khớp
  `FN-01-01`), và `cluster_functions()` đọc bảng `functions.md` lọc theo cột "Cụm".

Vì `functions.md` không còn tồn tại và ID không còn đúng dạng, **`srs-from-code` hiện
đang hỏng hoàn toàn** — không phải một tính năng cần nâng cấp, mà một lệnh không chạy
được. Đây là lý do đợt này bắt buộc, tách riêng khỏi việc đổi khuôn tài liệu (3B-3, tuỳ
chọn/khi có docx).

Thiết kế dưới đây đã được người dùng xác nhận qua 5 câu hỏi làm rõ (xem lịch sử hội
thoại) — mỗi câu chọn phương án khuyến nghị.

## Quyết định

### 1. Tham số hợp nhất + batch — giống hệt `code-intel`

Đổi tham số nhận vào từ `<tên-cụm> [--template ...]` sang **một FN-ID** (rỗng = toàn bộ
cây), dùng lại nguyên `intel_tree.py propose --functions ... [--start FN-ID]` để đề xuất
unit và `intel_tree.py units --functions ... --roots FN-ID[,...]` để lấy danh sách unit
đã chọn — không viết logic tính unit mới, tái dùng 100% máy đã xây ở đợt 2.

Sau khi người dùng xác nhận cây/danh sách unit (giống hệt bước xác nhận của
`code-intel`):

- **≥ 2 unit** → hỏi người dùng chạy song song (subagent) hay tuần tự, giống `code-intel`
  bước 6.
- **Batch qua nhiều unit**: mỗi unit cần có `intel.md` sẵn (đường dẫn suy ra ở mục 2 dưới)
  mới sinh được `srs.md`. Unit nào **thiếu `intel.md`** thì **bỏ qua, không chặn cả batch**
  — chạy tiếp các unit còn lại, và báo rõ danh sách unit bị bỏ qua ở bước kết thúc (giống
  tinh thần báo cáo 3 phần đã có ở bước 9 hiện tại).
- **Chế độ một unit duy nhất** (người dùng chỉ chọn/còn lại đúng 1 unit sau khi xác nhận)
  mà unit đó thiếu `intel.md` → **dừng cứng** (hard-stop), giống hành vi báo lỗi hiện tại
  của bước 2 "Kiểm srs.md tồn tại" khi thiếu tiền đề — không âm thầm bỏ qua trong trường
  hợp chỉ có một việc để làm.

### 2. Đường dẫn `srs.md` — cùng thư mục với `intel.md`

`intel_tree.py units` trả về `path` là đường dẫn FILE đã kết thúc bằng `/intel.md`
(tương đối `.specify/docs/`). Suy ra đường dẫn `srs.md` bằng cách thay hậu tố:

```
path.replace("/intel.md", "/srs.md")   # cùng thư mục, không tạo cấu trúc cây mới
```

Không gọi lại `intel_tree.py` với tham số khác hay viết logic suy path mới — đây là phép
thay chuỗi đơn giản trên giá trị đã có, thực hiện ngay trong `srs-from-code.md` (bước
LLM, không cần script mới).

Trường "Hệ thống" và "Ngày cập nhật" ở đầu khung `srs.md` (hiện đang lấy từ đâu đó trong
`functions.md`/ngữ cảnh cũ) đổi sang đọc trực tiếp `functions.json` cấp gốc:
`{"system": ..., "updated": ...}` — hai field top-level đã có sẵn từ đợt 1, không cần
field mới.

### 3. `srs_verify.py`: đổi CLI, regex, và nguồn danh sách FN kỳ vọng

Ba thay đổi, cùng một nguyên lý: làm lại đúng những gì `intel_verify.py` đã làm ở đợt 2.

**a) CLI**: `--cluster <tên> --functions functions.md` →
`--root <FN-ID> --functions .specify/docs/functions.json` (mặc định `--functions` đổi
theo). `--root` rỗng nghĩa là toàn cây (giống cách `code-intel`/`intel_verify.py` coi FN-ID
rỗng là gốc ảo).

**b) Regex**: `FN_ID_RE = re.compile(r"\bFN-\d{3,}\b")` → chuyển thành
`re.compile(r"\bFN(?:-\d{2})+\b")`, giống hệt pattern `intel_tree.py`/`fnlist_tree.py`
đã dùng. Regex cũ không khớp ID nhiều cấp (`FN-01-01`) nên mọi chỗ dùng `FN_ID_RE` hiện
tại (`parse_matrix`, việc dò FN-ID trong bảng ma trận truy vết) đang câm lặng không khớp
gì — sửa regex là điều kiện để các gate còn lại có ý nghĩa trở lại.

**c) Nguồn danh sách FN kỳ vọng**: hàm `cluster_functions(functions_md, cluster)` (đọc
bảng `functions.md`, lọc cột 4 "Cụm") bị **xoá hoàn toàn**, thay bằng logic dựa trên
`fnlist_tree.subtree_leaves(node)` — cùng pattern `intel_verify.py main()` đã dùng:

```python
import fnlist_tree as ft
...
tree = json.loads(Path(a.functions).read_text(encoding="utf-8"))
node = ft.find_by_id(tree["functions"], a.root) if a.root else {"children": tree["functions"]}
wanted = [n["id"] for n in ft.subtree_leaves(node)]
```

(Tên hàm/tham số chính xác sẽ chốt ở bước viết plan; đây là hình dạng logic, không phải
chữ ký cuối cùng.) `verify()`'s tham số `cluster: str` đổi thành `root: str` (hoặc
tương đương) mang cùng vai trò; lời gọi `cluster_functions(functions_md, cluster)` bên
trong `verify()` đổi thành gọi hàm mới dựa trên `subtree_leaves`.

**Lợi ích phụ**: mô hình cụm cũ cho phép một FN thuộc nhiều cụm (`row[4]` là danh sách
phân tách dấu phẩy) — độ phức tạp "một FN nhiều cụm" biến mất hoàn toàn với mô hình cây
(một node chỉ có đúng một đường dẫn tới gốc).

Các phần còn lại của `srs_verify.py` (`strip_noise`, `find_placeholders`, `_table_rows`,
`_function_numbers`, `_matrix_cell_valid`, `parse_matrix`'s phần còn lại, `_top_headings`,
`_empty_sections`, cấu trúc BLOCKING/WARNING trong `verify()`) **giữ nguyên** — chỉ cắm
lại nguồn "wanted" và regex, không đổi logic đối chiếu ma trận/khung.

### 4. Ghi trạng thái ngược — qua `fnlist_import.py update`, chống race giống `code-intel`

Bước 8 hiện tại "Cập nhật `functions.md`" (tự sửa cột Trạng thái bằng tay) bị **xoá hoàn
toàn**, thay bằng gọi `fnlist_import.py update --file .specify/docs/functions.json --set
FN-ID=srs [--set FN-ID=srs ...]` — đúng cơ chế đã dùng ở `code-intel` cho trạng thái
`intel`.

Áp dụng lại nguyên xi cơ chế chống race đã xây ở đợt 2: khi chạy batch song song (nhiều
subagent), **subagent không tự gọi `update`** — mỗi subagent chỉ báo cặp `FN-ID=srs` về
agent điều phối (parent); parent đợi TẤT CẢ subagent hoàn tất, rồi gọi `update` đúng một
lần với toàn bộ `--set` gộp lại. Chạy tuần tự (không subagent) thì gọi `update` sau mỗi
unit như bình thường, không cần gộp.

### 5. Không làm trong phạm vi này

- **Khuôn tài liệu `srs.md` không đổi** — vẫn I. Kiểm soát phiên bản, II. Giới thiệu, III.
  Đặc tả yêu cầu chức năng (N.1–N.7), IV. Phi chức năng, V. Ma trận truy vết, VI. Phụ lục.
  Không thêm/xoá/đổi tên mục nào.
- **Kỷ luật rót 3 dạng** (đọc thẳng / suy đoán có đánh dấu / không có căn cứ →
  "Chưa có thông tin") và **kỷ luật no-clobber** (không ghi đè nội dung người dùng đã sửa
  tay) giữ nguyên hoàn toàn — bước 3-6 hiện tại của `srs-from-code.md` không đổi nội dung,
  chỉ đổi cách unit/đường dẫn được xác định (mục 1-2 ở trên).
- **Không rót nội dung §11 (điều khiển giao diện) hay §12 (use case, chưa tồn tại) sang
  `srs.md`** — đó là 3B-3, sau khi khuôn tài liệu được thiết kế lại theo 2 cấp.
- **`srs-template.md` không đổi** — file này chỉ bị đụng ở 3B-3.
- **`intel_tree.py` không đổi** — đợt này chỉ tiêu thụ `propose`/`units` đã có, không sửa
  logic tính unit.

### 6. Ghi chú bàn giao cho 3B-3: văn phong tài liệu ban hành

3B-1 không rót nội dung nào sang `srs.md` (mục 5), nhưng khi 3B-3 làm việc đó, **khuôn
văn phong (không chỉ cấu trúc mục) phải mô phỏng đúng cách viết của tài liệu ban hành
thật**, không phải văn phong kỹ thuật/liệt kê mặc định. Đọc trực tiếp
`3. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Doanh_nghiệp.docx` (toàn văn, 8445 đoạn,
qua `word/document.xml`, không chỉ heading) cho thấy các quy ước lặp lại nhất quán:

- **`Mục đích chức năng`**: đúng 1 câu (hoạ hoằn 2-3 câu ở khối cha gộp nhiều màn hình
  con), văn phong Hán-Việt trang trọng, nêu **giá trị/lý do nghiệp vụ** ("giúp...",
  "hỗ trợ...", "nhằm...", "đảm bảo..."), tuyệt đối không mô tả thao tác click/nhập.
  Ví dụ nguyên văn: *"Xác thực danh tính và phân quyền truy cập, đảm bảo chỉ những tài
  khoản doanh nghiệp đối tác hoặc cán bộ quản lý hợp lệ mới có quyền tiến hành khai thác
  các phân hệ quản trị của hệ thống."*
- **`Kịch bản trường hợp sử dụng`**: nhãn trường cố định, đúng thứ tự, đúng chính tả:
  `Tên Use Case` / `Mức quan trọng` / `Người dùng` / `Loại UC` / `Người sử dụng và yêu
  cầu` / `Mô tả tóm tắt` / `Thời điểm sử dụng` / `Luồng sự kiện chuẩn` / `Luồng sự kiện
  nhỏ`. `Mô tả tóm tắt` là MỘT đoạn văn liền mạch tóm toàn luồng bằng các mệnh đề nối
  dấu phẩy (không tách gạch đầu dòng). `Luồng sự kiện chuẩn` đánh số bước `1:`, `2:`…;
  nhánh rẽ trong bước đánh `S-1:`, `S-2:`… và gọi tên bằng cụm trong ngoặc kép ("hệ
  thống thực hiện luồng con "X""); `Luồng sự kiện nhỏ` khai triển lại đúng các nhãn
  `S-n` đó theo thứ tự.
- **`Mô tả điều khiển`**: cột `Tên điều khiển` luôn viết dạng `[Loại] "[nhãn hiển thị
  đúng nguyên văn trên UI]"` (vd `Textbox "Tên đăng nhập / Email quản trị"`). Cột `Mô tả
  điều khiển` luôn 2-3 câu tách dòng riêng theo đúng thứ tự vai trò: (1) **hình thức +
  vị trí** hiển thị (icon, placeholder, màu sắc, vị trí tương đối — "nằm bên trái phía
  dưới ô nhập mật khẩu"), (2) **ràng buộc** ngắn gọn nếu có, thường là câu độc lập
  "Trường bắt buộc." (không gộp vào câu khác), (3) **hành vi/mục đích** khi tương tác
  ("Click để…", "Định dạng dữ liệu nhập là… dùng để…").
- **`Yêu cầu nghiệp vụ`**: câu ghép mô tả logic điều kiện, dùng cấu trúc "Khi người dùng
  [hành động], hệ thống [phản ứng], đồng thời [phản ứng phụ]" hoặc "nếu… thì…, ngược
  lại…". Luôn nêu rõ **điều kiện kích hoạt** trước **kết quả**.
- **Chủ ngữ hành động nhất quán**: "Hệ thống" luôn là chủ ngữ khi mô tả xử lý phía sau
  ("Hệ thống xác thực…", "Hệ thống trả về…"), "Người dùng" khi mô tả thao tác. Không
  dùng thể bị động kiểu kỹ thuật ("dữ liệu được xử lý bởi…").
- **Không lẫn thuật ngữ code/kỹ thuật** (tên file, class, endpoint, biến) vào các mục
  này — thuần ngôn ngữ nghiệp vụ/giao diện, giống hệt kỷ luật "chuyển hoá bắt buộc khi
  rót" mà `srs-from-code.md` hiện đã áp cho N.3-N.7 (bước 4 hiện tại), chỉ khác là áp
  thêm yêu cầu về **giọng văn**, không chỉ về việc lược bỏ đường dẫn code.

Việc này **không thuộc phạm vi 3B-1** (3B-1 không rót nội dung, không đổi khuôn) — ghi
lại ở đây để không thất lạc trước khi 3B-3 được brainstorm, vì việc đọc lại toàn văn
8445 đoạn của docx để rút văn phong là chi phí không nên lặp lại hai lần.

## Rủi ro

- **`intel.md` sinh trước đợt 2 hoặc thiếu §11** không ảnh hưởng đợt này — 3B-1 chỉ quan
  tâm sự tồn tại của `intel.md` tại đường dẫn suy ra, không đọc nội dung theo mục số nào
  mới. Rủi ro thiếu §11 chỉ phát sinh ở 3B-3.
- **Chế độ một-unit hard-stop vs batch skip-and-report là hai hành vi khác nhau cho cùng
  một điều kiện (thiếu `intel.md`)** — có thể gây nhầm lẫn nếu tài liệu hoá không rõ. Bù
  lại bằng cách nói rõ ràng trong `srs-from-code.md`: "chỉ 1 unit sau xác nhận" luôn hard-
  stop, "≥ 2 unit" luôn skip-and-report; ranh giới là **số unit sau khi xác nhận**, không
  phải cách gọi lệnh.
- **Đổi `FN_ID_RE` có thể ảnh hưởng các gate khác dùng chung regex này** trong
  `srs_verify.py` (`parse_matrix` là chỗ dùng chính) — cần rà toàn bộ file khi viết plan
  để chắc không còn chỗ nào giả định định dạng `FN-\d{3,}` cũ (vd trong test hiện có của
  `test_srs_verify.py`, cần cập nhật fixture ID sang dạng nhiều cấp).
