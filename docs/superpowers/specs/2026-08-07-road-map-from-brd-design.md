# Thiết kế: lệnh `road-map-from-brd`

**Ngày**: 2026-08-07
**Gói**: `speckit-extension` (`dft-speckit`)
**Trạng thái**: đã chốt thiết kế, chưa hiện thực

## 1. Vấn đề

`/speckit.dft-speckit.brd-import` bẻ một BRD `.docx` thành cây markdown `docs/brd/`
kèm `brd.manifest.yml`. Sau bước đó chưa có gì nối tiếp: muốn có `docs/roadmap.md`
thì phải chạy `/speckit.dft-speckit.road-map-from-codebase`, mà lệnh đó lấy danh sách
màn từ router/menu/thư mục pages — vô dụng khi dự án mới chỉ có tài liệu.

Cần một lệnh anh em: cùng đích đến (`docs/roadmap.md`, cùng `roadmap-template`),
khác nguồn đầu vào (thư mục BRD markdown).

## 2. Phạm vi

**Trong phạm vi**: sinh `docs/roadmap.md` từ `docs/brd/`; suy Wave/Phụ thuộc có
tham chiếu codebase hiện có; gác cổng phủ 1-1 giữa node BRD và item roadmap bằng
script.

**Ngoài phạm vi**: merge vào `docs/roadmap.md` đã tồn tại; thêm item từ codebase;
đặt cột `Trạng thái` theo mức độ đã code; sinh spec hay domain doc.

## 3. Quyết định đã chốt

| # | Quyết định | Lý do |
|---|---|---|
| Đ1 | Danh sách màn = **lai**: `brd.manifest.yml` làm khung ứng viên, đọc thêm để lọc mục phi-màn và tách mục chứa nhiều màn | Thuần manifest thì "Thuật ngữ" cũng thành item; đọc toàn văn 50+ file thì vỡ context |
| Đ2 | Thêm trường `**Nguồn**` vào `roadmap-template.md` | Cho `/speckit.specify <ID>` mở đúng file BRD; và là khoá để `verify` chấm phủ |
| Đ3 | `docs/roadmap.md` đã tồn tại → **dừng**, không merge | Đơn giản, không có nguy cơ clobber `Trạng thái`/`Nợ phát sinh`. Muốn sinh lại thì người dùng tự xoá/đổi tên |
| Đ4 | Script trích outline; LLM đọc thêm file cụ thể khi outline chưa đủ quyết | Đúng triết lý `brd-import` (script cơ học, LLM quyết ranh giới), chịu được BRD lớn |
| Đ5 | Quét codebase **chỉ để suy Wave/Phụ thuộc** — không thêm/bớt item, không đụng `Trạng thái` | BRD là nguồn chốt danh sách; mọi màn BRD phải có ≥1 item |
| Đ6 | Script `verify` gác cổng phủ; LLM vẫn là người ghi file theo template | Template là scaffold văn xuôi — đem vào Python sẽ lệch âm thầm. Nhưng "phủ đủ" thì phải kiểm bằng code, không kiểm bằng lời hứa |

Hướng đã cân nhắc và **loại**: script tự render `roadmap.md` từ decisions.json
(cấu trúc template bị hardcode trong Python → drift); thuần prompt không script
(bước phủ 1-1 thành LLM tự chấm bài của chính nó).

## 4. Kiến trúc

### 4.1. File đụng tới

| File | Việc |
|---|---|
| `speckit-extension/commands/road-map-from-brd.md` | mới — lệnh |
| `speckit-extension/scripts/brd_roadmap.py` | mới — CLI hai lệnh con `outline` \| `verify` |
| `speckit-extension/templates/roadmap-template.md` | sửa — thêm trường `**Nguồn**` |
| `speckit-extension/commands/road-map-from-codebase.md` | sửa — dạy nó điền `**Nguồn**` |
| `speckit-extension/extension.yml` | khai command mới + bump `0.0.6` → `0.0.7` |
| `speckit-extension/README.md` | mô tả lệnh mới |
| `speckit-extension/scripts/tests/test_brd_roadmap.py` | mới — test `outline` + `verify` |

`build-zip.sh` **không cần sửa**: nó copy `scripts/` bằng `find` đệ quy (loại
`.venv`, `__pycache__`, `scripts/tests/`), nên script mới tự vào zip.

Script mới đứng riêng ở `scripts/brd_roadmap.py`, **không** nhét vào package
`scripts/brd/` — package đó là luồng docx→markdown và đã có `outline.py` với ý
nghĩa khác (outline của tài liệu Word), trùng tên sẽ gây nhầm.

### 4.2. Luồng

```
docs/brd/ + brd.manifest.yml ──outline──► .specify/tmp/roadmap-brd/outline.json
                                                    │
                    quét codebase (LLM, chỉ suy phụ thuộc) ─┤
                                                    ▼
                                  interview qua AskUserQuestion (2 lượt)
                                                    ▼
                    .specify/tmp/roadmap-brd/decisions.json
                    (chỉ chứa node bị loại + lý do)
                                                    ▼
                       LLM ghi docs/roadmap.md theo roadmap-template
                                                    ▼
                    brd_roadmap.py verify → exit ≠ 0 thì CẤM báo xong
```

### 4.3. Chặn đầu vào

`$ARGUMENTS` là thư mục BRD, mặc định `docs/brd`.

- Thư mục không tồn tại, hoặc không có `brd.manifest.yml` → **hỏi lại**, không tự
  đi tìm thư mục khác trong repo.
- `docs/roadmap.md` đã tồn tại → **dừng ngay**, in đường dẫn file cũ và nói rõ:
  lệnh này không merge, muốn sinh lại thì tự đổi tên hoặc xoá file cũ.

## 5. `scripts/brd_roadmap.py`

Stdlib thuần, không thêm dependency. `brd.manifest.yml` do chính `splitter.py`
ghi theo định dạng flow cố định một dòng mỗi node
(`  - { id: …, order: …, title: "…", path: "…", parent: …, chars: … }`, chuỗi
escape bằng `_q`: `\` → `\\`, `"` → `\"`). Parser nhắm đúng định dạng đó là tất
định — không cần PyYAML.

### 5.1. `outline <brd-dir> [--out <json>] [--head N]`

Mặc định `--out .specify/tmp/roadmap-brd/outline.json`, `--head 15`.

Mỗi node in ra:

- `id`, `order`, `depth`, `title`, `parent`, `chars`
- `path` (hoặc `dir` + `inline: true` với node không có file riêng)
- `breadcrumb` — chuỗi tiêu đề cha→con, dùng để suy cột `Module`
- `headings` — heading con bên trong file, kèm cấp
- `head` — `N` dòng đầu phi-rỗng của file
- `signals` — đếm cơ học: số bảng, số dòng bảng, số ảnh (`<img`), số lần khớp từ
  khoá thao tác (Thêm/Sửa/Xoá/Tìm kiếm/Duyệt/Xuất…), từ khoá phân quyền
  (quyền/vai trò/nhóm người dùng), và bảng-có-cột-Trường (dấu hiệu đặc tả dữ liệu)

Không in toàn văn. LLM có `path` để tự `Read` thêm khi outline chưa đủ quyết.

Ở cấp gốc còn in hai danh sách lệch — BA sửa tay `docs/brd/` sau khi import là
chuyện thường:

- `files_without_node` — file `.md` có trên đĩa nhưng không có trong manifest
- `nodes_without_file` — manifest khai nhưng file đã mất

Hai danh sách này là **warning**, không chặn, nhưng lệnh phải báo ra.

### 5.2. `verify <roadmap.md> --brd <dir> --decisions <json>`

Gom hết lỗi rồi in một lần (không dừng ở lỗi đầu), in báo cáo JSON
`{ok, errors[], warnings[]}` ra stdout, exit 1 nếu `errors` không rỗng.

**Lỗi (fail):**

1. **Phủ**: mọi node BRD phải hoặc xuất hiện trong trường `**Nguồn**` của ≥1
   item, hoặc nằm trong `decisions.json → excluded[]` kèm `reason` không rỗng.
   Thiếu cả hai → liệt kê đích danh node.
2. `**Nguồn**` trỏ tới file không tồn tại, hoặc `#anchor` không khớp heading nào
   trong file đó. Giá trị `**Nguồn**` là **đường dẫn tương đối từ gốc repo**
   (`docs/brd/03-quan-ly/05-danh-sach.md`), phần sau `#` được coi là khớp nếu
   trùng **text heading nguyên văn** hoặc **slug GFM** của một heading trong file
   (so khớp không phân biệt hoa/thường).
3. ID `RM-\d{3}` trùng nhau; hoặc bảng tổng ↔ khối chi tiết không khớp hai chiều.
4. Còn sót placeholder `[…]` hoặc `[DATE]`.
5. Cột `Phụ thuộc` trỏ ID không tồn tại; có chu trình phụ thuộc; hoặc item có
   Wave nhỏ hơn Wave của thứ nó phụ thuộc.

**Warning (không fail):**

- Item không có trường `**Nguồn**` (file roadmap cũ sinh trước khi đổi template)
- Một node > 40.000 ký tự chỉ map vào đúng 1 item — nhiều khả năng phải tách

Node `inline` (không có file riêng) được tính là node cần phủ như mọi node khác;
`**Nguồn**` của item trỏ vào nó dùng đường dẫn thư mục (`dir`).

### 5.3. `decisions.json`

Cố ý tối giản:

```json
{
  "brd_dir": "docs/brd",
  "excluded": [
    {"node_id": 3, "title": "Thuật ngữ và từ viết tắt", "reason": "từ điển thuật ngữ, không phải màn"}
  ]
}
```

Bản đồ item↔node đã nằm trong chính `roadmap.md` qua trường `**Nguồn**` — không
chép ra hai nơi để khỏi lệch.

## 6. Quy trình trong `road-map-from-brd.md`

1. **Chặn đầu vào** (§4.3) → chạy `outline`, đọc JSON, báo số node và hai danh
   sách lệch nếu có.
2. **Quét codebase — chỉ để suy phụ thuộc**: tìm auth/phân quyền/entity dùng
   chung/module đã dựng. Không có codebase (dự án mới, chỉ có `docs/`) → **bỏ
   qua và nói thẳng** "chưa có codebase, phụ thuộc suy hoàn toàn từ BRD", không
   hỏi vòng vo. Ràng buộc cứng viết ngay trong lệnh: codebase **không được thêm
   hay bớt item**, **không đụng cột `Trạng thái`**.
3. **Phân loại ứng viên**: mỗi node → `là màn` / `chứa k màn → tách` / `không
   phải màn + lý do`. Nhóm thứ ba ghi vào `decisions.json`. Không đủ căn cứ từ
   outline → `Read` thẳng file đó, **không đoán**.
4. **Interview #1 — chốt phân loại**: trình **đầy đủ** hai bảng (bị loại kèm lý
   do; bị tách kèm `k`) rồi hỏi qua **AskUserQuestion**. Hỏi theo *nhóm quyết
   định*, không hỏi từng node — người dùng sửa trực tiếp trên bảng.
5. **Đề xuất Wave + Phụ thuộc** kèm lý do "cái gì chặn cái gì" → **Interview #2 —
   chốt ranh giới wave**. Chờ **phản hồi thật**; cấm tự tuyên bố người dùng đã
   đồng ý; chưa có phản hồi → dừng, **không ghi file**.
6. **Ghi `docs/roadmap.md`** theo khung cố định: resolve `roadmap-template` y hệt
   cách `road-map-from-codebase` §4 làm (`specify preset resolve roadmap-template`
   → fallback `.specify/extensions/dft-speckit/templates/roadmap-template.md` →
   hỏi). Điền `**Nguồn**`. ID cấp tăng dần từ `RM-001`.
7. **Chạy `verify`** → exit ≠ 0 thì sửa file rồi chạy lại; **cấm báo xong khi
   chưa exit 0**. In đủ warnings. Kết thúc: báo số item, thứ tự wave, danh sách
   node đã loại, rồi nhắc `/speckit.dft-speckit.domain-design <module>` →
   `/speckit.specify <ID>`.

Đóng bằng mục **Sai lầm thường gặp** (theo kiểu `brd-import.md`):

- Tự chọn phân loại rồi chạy tiếp mà không hỏi thật
- Dùng codebase để thêm/bớt item hoặc đặt `Trạng thái`
- Loại node mà không ghi lý do vào `decisions.json`
- `verify` fail rồi vẫn báo xong
- Nuốt warnings cho gọn báo cáo

Tổng chi phí hỏi: **2 lượt AskUserQuestion**, đặt đúng chỗ trọng yếu (phân loại,
ranh giới wave).

## 7. Sửa template & tương thích ngược

`roadmap-template.md`, khối chi tiết thêm đúng một dòng ngay sau `**Mô tả**`:

```
- **Nguồn**: [docs/brd/…md#heading / đường dẫn code / N/A]
```

Bảng tổng **không** thêm cột. `road-map-from-codebase.md` §4 thêm một câu: điền
`**Nguồn**` bằng đường dẫn file/thư mục code, không xác định được thì `N/A`.
File `roadmap.md` cũ thiếu trường này không làm gãy lệnh nào — `verify` chỉ cảnh
báo.

## 8. Test

`speckit-extension/scripts/tests/test_brd_roadmap.py`, dựng fixture `docs/brd/`
nhỏ bằng tay (2–3 file + `brd.manifest.yml` viết đúng định dạng `splitter.py` ghi):

**`outline`**

- parse manifest có `title` chứa dấu `,` và `"` đã escape
- node `inline` (không có `path`, có `dir`)
- phát hiện `files_without_node` và `nodes_without_file`
- `signals` đếm đúng trên fixture đã biết trước số bảng/ảnh/từ khoá

**`verify`**

- happy path → exit 0
- thiếu phủ → exit 1, nêu đúng node còn thiếu
- node bị loại có `reason` → pass; `reason` rỗng → fail
- `**Nguồn**` trỏ file không tồn tại → fail
- ID trùng → fail
- bảng tổng ↔ khối chi tiết lệch → fail
- chu trình phụ thuộc → fail
- Wave nghịch (item Wave 0 phụ thuộc item Wave 1) → fail
- còn `[…]` → fail

## 9. Xử lý lỗi

`outline` và `verify` in thông điệp tiếng Việt một dòng rồi exit ≠ 0. Lệnh dừng
và in nguyên văn thông điệp cho người dùng — **không tự chữa, không thử lệnh
khác**. Đây là cùng hợp đồng lỗi mà `brd-import.md` đang dùng.
