# Đợt 3B-3: viết lại `srs-template.md`/`srs-from-code.md` theo đúng khuôn docx thật

**Ngày**: 2026-08-13
**Phạm vi**: `speckit-extension` — `templates/srs-template.md`, `commands/srs-from-code.md`,
`scripts/srs_verify.py` (+ `scripts/tests/test_srs_verify.py`).

Tiếp theo 3B-1 (di trú `srs-from-code`/`srs_verify.py` sang mô hình cây) và 3B-2 (thêm §12
Kịch bản Use Case vào `code-intel`). Không đụng `code-intel.md`/`intel-template.md`/
`intel_verify.py`/`intel_tree.py`/`fnlist_tree.py` — dữ liệu nguồn (§1-§12 của `intel.md`)
đã đủ, đợt này chỉ đổi cách rót sang `srs.md`.

## Bối cảnh

`srs-template.md` hiện tại (I. Kiểm soát phiên bản, II. Giới thiệu, III. Đặc tả yêu cầu
chức năng theo `## N.` phẳng, IV. Phi chức năng, V. Ma trận truy vết, VI. Phụ lục) là khuôn
tự đặt ra ban đầu, không khớp cấu trúc thật tài liệu ban hành công ty
(`3. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Doanh_nghiệp.docx`). Đọc toàn văn + đối
chiếu Navigation pane của Word xác nhận cấu trúc thật có **4 cấp lồng nhau**, không phải 2
cấp như giả định ban đầu của 3B batch:

```
Nhóm (1. Giao tiếp trong hệ thống / 2. Đăng ký đăng nhập / 3. Quản lý thông tin cá nhân...)
  └─ Chức năng (2.1 Đăng nhập / 3.1 Quản lý thông tin cá nhân...)
       ├─ Sơ đồ chức năng
       ├─ Mục đích chức năng
       └─ Mô tả chức năng
            └─ Màn hình (CHỈ có heading riêng khi Chức năng có ≥2 màn hình)
                 └─ a-h: Đối tượng tham gia, Điều kiện thực hiện, Mô hình Usecase,
                         Kịch bản trường hợp sử dụng, Thiết kế mô hình nghiệp vụ,
                         Thiết kế UX/UI, Mô tả điều khiển, Yêu cầu nghiệp vụ
```

Bằng chứng: Navigation pane của Word (ảnh người dùng cung cấp) cho "2.1.3. Mô tả chức năng"
của "Đăng nhập" liệt kê thẳng `a.` đến `h.` (1 màn hình, không có heading màn hình riêng);
đọc thêm phần "Quản lý thông tin cá nhân" cho thấy một Chức năng có 3 Màn hình
("Trang thông tin cá nhân", "Quản lý lịch sử sử dụng cá nhân", "Thông báo của hệ thống"),
mỗi màn hình có trọn bộ `a.`-`h.` riêng — xác nhận cấp Màn hình chỉ xuất hiện khi cần phân
biệt nhiều màn hình trong một Chức năng.

Toàn bộ khuôn I-VI cũ (kiểm soát phiên bản, ma trận truy vết, phụ lục...) **không tồn tại**
trong docx thật — đây là khung nghiệm thu nội bộ công ty tự thêm vào, khác mục đích với văn
bản giao khách. Quyết định của đợt này: **bỏ hẳn I-VI**, `srs.md` chỉ còn đúng cấu trúc docx.

## Quyết định

### 1. Khuôn `srs-template.md` — 4 cấp heading, số thứ tự thật

```markdown
## [Tên Nhóm]

### [Tên Chức năng]

<!-- FN: FN-01-01, FN-01-02 -->

#### Sơ đồ chức năng

```mermaid
flowchart TD
    ...
```

#### Mục đích chức năng

[1 câu, văn phong đã chốt ở 3B-1 spec §6]

#### Mô tả chức năng

##### [Tên Màn hình]

###### a. Đối tượng tham gia
###### b. Điều kiện thực hiện
###### c. Mô hình Usecase
###### d. Kịch bản trường hợp sử dụng
###### e. Thiết kế mô hình nghiệp vụ
###### f. Thiết kế UX/UI
###### g. Mô tả điều khiển
###### h. Yêu cầu nghiệp vụ
```

- **`##`–`######` đúng 6 cấp, khớp trần Markdown (h1-h6)** — không còn chỗ lồng sâu hơn,
  đây là lý do không thể giữ thêm bất kỳ cấp trung gian nào khác.
- **Cấp `##### [Tên Màn hình]` chỉ xuất hiện khi Chức năng có ≥ 2 màn hình.** Đúng 1 màn
  hình (trùng tên Chức năng, như "Đăng nhập") → bỏ heading này, `a.`-`h.` nối thẳng vào
  `#### Mô tả chức năng`.
- **Số thứ tự (`1.`/`2.1.`/`a.`-`h.`) tính theo VỊ TRÍ XUẤT HIỆN khi ghi**, không lưu cố
  định — cùng cách `intel_tree.py`'s `compute_paths()` đã đánh số thư mục `01-`/`02-` theo
  vị trí trong `children` (không phải theo FN-ID). Thêm/bớt Nhóm hay Chức năng ở lần chạy
  sau tự tính lại số, không để lại số nhảy cóc, không cần cơ chế "giữ số cũ".
- **`<!-- FN: FN-ID, FN-ID... -->`** — HTML comment ẩn, đặt ngay dưới heading Chức năng,
  liệt kê mọi FN-ID lá mà Chức năng đó phủ. Không hiện khi xem markdown/xuất Word — chỉ
  `srs_verify.py` đọc để đối chiếu `functions.json`. Đây là cơ chế THAY THẾ mục V Ma trận
  truy vết đã bỏ — vẫn giữ được cổng BLOCKING "mọi FN phải có mặt" mà không lộ FN-ID (một
  khái niệm nội bộ của pipeline, không có trong docx thật) ra tài liệu khách thấy.
- **Bỏ hẳn `I.`/`II.`/`IV.`/`V.`/`VI.`** — không giữ lại bất kỳ mục nào (lịch sử phiên bản,
  giới thiệu, phi chức năng, ma trận truy vết, phụ lục). Không-clobber vẫn áp dụng ở mức
  nội dung (so khối Chức năng/Màn hình cũ trước khi ghi đè), chỉ không còn mục `I.1` riêng
  để ghi lịch sử thay đổi dạng bảng.

### 2. Hai mục cấp Nhóm KHÔNG tự sinh — đánh dấu bằng comment ẩn, không lược bỏ âm thầm

Docx có hai loại nội dung cấp Nhóm không gắn với FN nào cụ thể: **"1. Giao tiếp trong hệ
thống"** (bảng giao thức toàn hệ thống, xuất hiện đúng một lần đầu tài liệu) và, cuối mỗi
Nhóm, **"Sơ đồ các giao thức kết nối giữa các khối"** + **"Cơ sở dữ liệu"** (2 mục phụ lục
lặp lại mỗi Nhóm). Cả ba đều không có đơn vị FN để đối chiếu, và nội dung của chúng (kiến
trúc hệ thống, giao thức, schema DB) nằm ngoài phạm vi rút từ `intel.md` hiện có (không mục
`§1`-`§12` nào của `intel.md` là nguồn trực tiếp cho các mục này).

**3B-3 không tự sinh ba mục này** — nhưng không lược bỏ âm thầm: mỗi Nhóm sinh ra một comment
ẩn ngay dưới heading Nhóm:

```markdown
## [Tên Nhóm]

<!-- TODO 3B-4: Sơ đồ các giao thức kết nối giữa các khối, Cơ sở dữ liệu — chưa tự sinh, cần đợt sau -->
```

(Riêng "Giao tiếp trong hệ thống" chỉ xuất hiện một lần cho cả tài liệu, không lặp theo
Nhóm — comment tương ứng đặt ở đầu file, trước Nhóm đầu tiên, nếu `srs-from-code` sinh toàn
bộ cây từ gốc.) Giữ đúng kỷ luật "không silently drop" đã áp xuyên suốt pipeline (giống
cách `intel §8`/`§10` không bao giờ bị xoá âm thầm) — người soát thấy rõ phần nào chưa có,
không phải tự đoán tại sao thiếu.

### 3. Mermaid — 3 loại sơ đồ, 3 quy ước dữ liệu riêng

- **Sơ đồ chức năng** (cấp Chức năng) + **Thiết kế mô hình nghiệp vụ** (cấp Màn hình, mục
  `e.`): cả hai dùng `flowchart`, dựng từ `intel §5` (Luồng nghiệp vụ). Sơ đồ chức năng là
  luồng tổng quan (toàn bộ luồng của Chức năng, gộp mọi màn hình con); Thiết kế mô hình
  nghiệp vụ là luồng chi tiết của riêng màn hình đó, nêu rõ thành phần nào xử lý bước nào
  (đúng như `§5` đã ghi). `§5` không có luồng nào ứng với Chức năng/Màn hình đang viết →
  lược bỏ sơ đồ, không tự suy các bước — giữ nguyên luật "không sơ đồ bịa" đã có ở
  `srs-from-code.md` hiện tại.
- **Mô hình Usecase** (mục `c.`): mermaid không có UML use-case native — mô phỏng bằng
  `flowchart` (actor = node chữ nhật, use case = node oval `([Tên Use Case])`, cạnh nối
  actor→use case). Dữ liệu từ `intel §12` (Tên Use Case + Người dùng) kết hợp `§6` (Phân
  quyền, nếu cần chi tiết hoá vai trò). `§12` không có khối `###` nào ứng với màn hình này
  → lược bỏ sơ đồ.
- **Thiết kế UX/UI** (mục `f.`): không tự sinh mockup — luôn ghi cố định
  `_(cần chèn ảnh — không tự sinh)_`, giữ nguyên placeholder cố định đã thống nhất từ đầu
  batch 3B.

### 4. Mapping `intel.md` → khuôn mới

| Nguồn (`intel.md`) | Đích (`srs.md`) |
| --- | --- |
| §1 Phủ chức năng | `<!-- FN: ... -->` dưới mỗi Chức năng |
| §2 Màn hình / điểm vào | Tên Màn hình (mục `##### [Tên Màn hình]`), câu mở đầu "Mô tả chức năng" |
| §3 Thực thể, §4 Kiểm tra hợp lệ | rải vào mục `h.` Yêu cầu nghiệp vụ (văn xuôi, văn phong 3B-1 §6 — không còn bảng N.4/N.5 riêng, khuôn docx không tách) |
| §5 Luồng nghiệp vụ | 2 sơ đồ mermaid (Sơ đồ chức năng, Thiết kế mô hình nghiệp vụ) |
| §6 Phân quyền | mục `a.` Đối tượng tham gia, `b.` Điều kiện thực hiện |
| §7 Tích hợp ngoài, §9 Thông báo hiển thị | rải vào mục `h.` Yêu cầu nghiệp vụ |
| §11 Điều khiển giao diện | mục `g.` Mô tả điều khiển (bảng Tên điều khiển/Mô tả điều khiển, đúng khuôn docx đã xác nhận ở 3B-1 spec §6) |
| §12 Kịch bản Use Case | mục `d.` Kịch bản trường hợp sử dụng (9 field nguyên văn, đã có sẵn cấu trúc khớp) + mục `c.` Mô hình Usecase (mermaid) |
| §10 Phát hiện logic/bảo mật | **Không rót** — chỉ dùng ở bước cuối để hỏi người dùng, giữ nguyên luật hiện có |

Ba thành phần `Mô tả điều khiển`/`Kịch bản trường hợp sử dụng`/`Mô hình Usecase` giờ có
NGUỒN THẬT (§11/§12, xây ở 3A/3B-2) — khác thời điểm `srs-from-code.md` hiện tại còn phải
lược bỏ các mục này vì `intel.md` chưa có gì.

Văn phong rót giữ nguyên toàn bộ quy ước đã chốt ở spec 3B-1 §6 (Mục đích chức năng 1 câu
Hán-Việt trang trọng; Kịch bản sử dụng đúng 9 field/nhãn trường; Mô tả điều khiển 2-3 câu
theo thứ tự hình thức→ràng buộc→hành vi; Yêu cầu nghiệp vụ câu ghép điều kiện→kết quả).

### 5. `srs_verify.py` — viết lại phần lớn

Bỏ hẳn: `parse_matrix`, `_matrix_cell_valid`, `FUNC_HEADING_RE` (`^##\s+(\d+)\.`), mọi logic
dựa trên "V. Ma trận truy vết" — không còn ý nghĩa với khuôn mới.

BLOCKING mới:
- Mọi FN trong `wanted_functions()` (đã có từ 3B-1, không đổi) phải xuất hiện trong ít nhất
  một `<!-- FN: ... -->`. Thay thế hoàn toàn vai trò của `thieu-fn` cũ.
- `find_placeholders` giữ nguyên (regex `[...]`, đã có sẵn cơ chế loại trừ comment/code
  fence/mermaid `[Nhập thông tin]`).

WARNING mới: mỗi Chức năng (`###`) phải đủ 3 mục con `Sơ đồ chức năng`/`Mục đích chức
năng`/`Mô tả chức năng`; mỗi Màn hình (heading `#####` hoặc trực tiếp dưới `#### Mô tả chức
năng` nếu chỉ 1 màn hình) phải đủ 8 mục `a.`-`h.`. Không BLOCKING vì một số mục hợp lệ để
rỗng/lược khi không có căn cứ (Sơ đồ mermaid, Mô hình Usecase) — chặn cứng sẽ tái tạo đúng
lỗi `check_not_found_ratio` đã từng mắc ở batch 2.

## Không làm trong phạm vi này

- Không tự sinh "Giao tiếp trong hệ thống"/"Sơ đồ giao thức kết nối"/"Cơ sở dữ liệu" — đánh
  dấu comment ẩn `TODO 3B-4`, để đợt sau (xem mục 2).
- Không tự động chèn ảnh chụp UX/UI thật — luôn `_(cần chèn ảnh — không tự sinh)_`.
- Không đụng `code-intel.md`/`intel-template.md`/`intel_verify.py`/`intel_tree.py`/
  `fnlist_tree.py` — dữ liệu nguồn `§1`-`§12` giữ nguyên như đã có.
- Không xây cơ chế export Markdown → Word (`.docx`) thật — `srs.md` vẫn là file Markdown
  giao khách, không phải quy trình đóng gói tài liệu.

## Rủi ro

- **Số thứ tự tính theo vị trí, không phải khoá ổn định** — hai lần chạy `srs-from-code`
  liên tiếp mà Nhóm/Chức năng bị thêm/bớt/đổi thứ tự giữa chừng sẽ làm SỐ đổi dù NỘI DUNG
  không đổi. Không phải lỗi (đây là hành vi có chủ đích, khớp cách docx thật đánh số lại
  toàn bộ mỗi khi có thay đổi cấu trúc), nhưng cần nói rõ trong lệnh để người dùng không
  hiểu nhầm là bug khi thấy số nhảy giữa hai lần chạy.
- **`<!-- FN: ... -->` là cơ chế MỚI, chưa có tiền lệ trong pipeline** — khác `§10`'s cột
  `Kết luận` (đã có tiền lệ ghi ngược một dòng), đây là lần đầu HTML comment mang dữ liệu
  cấu trúc (danh sách ID) thay vì chỉ là ghi chú tự do. Cần viết rõ định dạng
  (`FN: FN-01-01, FN-01-02`, phân tách dấu phẩy) và test kỹ edge case (Chức năng phủ 0 FN —
  không nên xảy ra nhưng phải xử lý, comment rỗng `<!-- FN: -->` có hợp lệ không).
- **Cấp Màn hình có/không tuỳ số lượng** — logic "1 màn hình thì bỏ heading, ≥2 thì thêm"
  làm `srs_verify.py`'s parser phải xử lý HAI hình dạng khác nhau cho cùng một vị trí dữ
  liệu (8 mục nằm trực tiếp dưới `#### Mô tả chức năng` HOẶC dưới `##### [Tên Màn hình]`) —
  phức tạp hơn một hình dạng cố định, cần test cả hai ca kỹ.
- **`intel §11`/`§12` sinh trước batch 3A/3B-2 sẽ thiếu dữ liệu cho `g.`/`c.`/`d.`** — các
  unit đã chạy `code-intel` trước hai đợt đó cần chạy lại mới có đủ nguồn cho `srs-from-code`
  rót đầy đủ; không tự động chạy lại thay người dùng (giữ nguyên nguyên tắc đã áp dụng nhất
  quán từ đầu chuỗi 3A/3B-1/3B-2).
