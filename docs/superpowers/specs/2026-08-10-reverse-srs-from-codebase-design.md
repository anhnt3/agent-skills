# Thiết kế — Reverse SRS từ codebase và function list

**Ngày**: 2026-08-10
**Trạng thái**: đã chốt qua brainstorming, chưa triển khai

## 1. Bối cảnh

Dev đã code và test đầy đủ theo function list dùng nghiệm thu đầu bài thầu, nhưng không có tài liệu chính thức theo template ban hành (BRD, SRS, ADD, User Manual). Cần dựng công cụ đi **chiều ngược**: từ function list + codebase đã hoàn thiện, sinh ra tài liệu bàn giao đúng khung quy định.

Repo `agent-skills` hiện đã có đường ống chiều xuôi (`brd-import` → `road-map-from-brd` → `domain-design` → `/speckit.specify`). Chiều reverse chưa có gì.

## 2. Phạm vi

**Trong phạm vi**: đường ống sinh **SRS**, gồm ba command mới thêm vào extension `dft-speckit` đang có, hai template và hai script.

**Ngoài phạm vi lần này**: BRD, ADD, User Manual. Chúng dùng lại được `intel.md` nên không phí công, nhưng mỗi loại là một khung tài liệu riêng với nguồn dữ liệu riêng (ADD cần kiến trúc/triển khai, User Manual cần ảnh màn hình). Gộp vào một spec sẽ làm spec không thực thi nổi. Làm xong đường ống SRS rồi thêm từng lệnh sau.

## 3. Kiến trúc

Ba command, mỗi bước để lại một file trên đĩa để người dùng review trước khi đi tiếp:

```
function list .xlsx ──▶ /speckit.dft-speckit.fnlist-import
                          └─▶ .specify/docs/functions.md

codebase + functions.md ─▶ /speckit.dft-speckit.code-intel <cụm> <FN-...>
                          └─▶ .specify/docs/<cụm>/intel.md

intel + functions.md ───▶ /speckit.dft-speckit.srs-from-code <cụm>
       + srs-template.md  └─▶ .specify/docs/<cụm>/srs.md
```

Bố cục file:

```
.specify/docs/
├── functions.md                    ← function list đã import, dùng chung mọi cụm
├── user_and_authent/
│   ├── intel.md                    ← đặc tả rút từ code, mọi dòng có file:line
│   └── srs.md                      ← SRS theo khung ban hành
└── <cụm khác>/
```

### 3.1. Vì sao tách ba bước, không gộp

**`functions.md` là điểm neo hợp đồng.** Nó có ID ổn định (`FN-001`) mà mọi tài liệu neo vào. Cổng kiểm cuối của lệnh SRS là: mọi FN thuộc cụm phải có một dòng trong ma trận truy vết, hoặc bị khai ngoài phạm vi kèm lý do. Cổng đó chỉ tồn tại nếu function list có một bản trên đĩa với ID ổn định.

**`intel.md` là nơi sửa sai rẻ nhất.** LLM đọc code sẽ suy sai vài chỗ. Sửa một dòng rule ở tầng intel rẻ hơn nhiều so với truy nó đã lan vào ba mục của SRS đã format.

**`intel.md` dùng lại được.** BRD/ADD/User Manual sau này chỉ cần lệnh mới đọc `.specify/docs/<cụm>/intel.md`, không quét lại code từ đầu.

### 3.2. Ranh giới nội bộ / giao khách

- `intel.md` **giữ** `file:line` — tài liệu nội bộ, để người dùng kiểm chứng từng khẳng định.
- `srs.md` **tránh** đường dẫn file, số dòng, tên class/hàm — tài liệu giao khách. Kiểm bằng cảnh báo, không chặn (xem §3.3).

### 3.3. Nguyên tắc mềm dẻo

Bộ command này phải chạy được trên nhiều dự án khác nhau, với khách hàng khác nhau và khung tài liệu khác nhau. Nguyên tắc chung:

**Chặn cứng chỉ dành cho thứ kiểm được tất định.** Cụ thể là hai thứ: mã chức năng thiếu dòng trong ma trận truy vết, và placeholder `[…]` còn sót. Cả hai đều đúng/sai rạch ròi, không cần phán đoán, và sửa rất rẻ.

**Mọi thứ cần phán đoán thì cảnh báo, để người quyết.** Nghi có đường dẫn code lọt vào `srs.md`, nghi thiếu ràng buộc field, nghi số dòng import lệch — báo rõ chỗ nghi và lý do, rồi đi tiếp. Kiểm bằng mẫu chuỗi luôn có báo nhầm; biến nó thành cổng chặn sẽ khiến người dùng phải đi vòng qua công cụ, và đó là kết cục tệ hơn.

**Khung tài liệu là mặc định, không phải luật.** `srs-template.md` giữ tên và thứ tự mục cấp I–VI để đầu ra ổn định, nhưng mục con lược bỏ được, mục riêng của dự án thêm được, và khách hàng có khung khác hẳn thì truyền template riêng cho lệnh.

**Chỗ chưa chắc thì đánh dấu, đừng bỏ trống.** Ràng buộc hay message chỉ suy đoán được vẫn ghi vào tài liệu, kèm `(cần xác nhận)`. Bỏ trống thì người soát không biết có thiếu; bịa mà không đánh dấu thì thành cam kết sai lúc nghiệm thu.

Siết thêm là việc của các bản sau, khi đã chạy thật vài dự án và biết chỗ nào thực sự hay sai.

### 3.4. Đặt trong `.specify/`

Người dùng chọn `.specify/docs/`. Lưu ý đã ghi nhận: `specify init` và nâng cấp CLI có ghi đè các thư mục con của spec-kit (`memory/`, `templates/`, `scripts/`, `extensions/`) nhưng không đụng `docs/`; rủi ro thật là project để `.specify/` trong `.gitignore` — khi đó tài liệu không vào git. **Cả ba command phải kiểm dòng đó và cảnh báo** trước khi ghi.

### 3.5. Chồng lấn với `domain-design`

`domain-design` cũng rút entity/FK/enum/rule từ codebase, ghi `docs/domain/`. Khác biệt: nó bắt buộc có `docs/roadmap.md` làm đầu vào và phục vụ chiều xuôi (nuôi `/speckit.specify`). Chiều reverse không có roadmap. Quyết định: `code-intel` là lệnh riêng, nhưng **mượn hình dạng mục entity của `domain-template`** để hai bên không mâu thuẫn về cách mô tả thực thể.

## 4. Đặc tả command

### 4.1. `/speckit.dft-speckit.fnlist-import <đường-dẫn.xlsx|.csv>`

Theo đúng kỷ luật của `brd-import`: **script chép nguyên văn, LLM chỉ quyết ánh xạ cột.** Đây là văn bản hợp đồng, LLM không được tự gõ lại nội dung.

Script `fnlist_import.py` hai chế độ:
- `inspect` — tự bootstrap `.venv` + `openpyxl` (như `csv_to_xlsx.py`), in tên sheet, header và vài dòng đầu. Không đoán gì.
- `write` — nhận ánh xạ cột dạng JSON, chép nguyên văn ô, ghi `.specify/docs/functions.md`.

LLM đọc output `inspect`, quyết cột nào là tên chức năng / mô tả / nhóm. Gặp nhiều sheet, header hai tầng, hoặc ô merge → hỏi qua AskUserQuestion, không tự chọn.

Cột của `functions.md`: `FN-ID | Nhóm | Tên chức năng | Mô tả | Cụm | Nguồn code | Trạng thái`.

- `FN-ID` cấp tăng dần theo thứ tự dòng gốc, không bao giờ đánh số lại.
- `Cụm` và `Nguồn code` để trống lúc import; `code-intel` điền ngược lại. Nhờ vậy `functions.md` luôn trả lời được "FN nào chưa ai làm tài liệu".

Đối chiếu số lượng: so số dòng chức năng ra với số dòng vào. Lệch thì **báo rõ dòng nào bị bỏ và vì sao** (dòng tiêu đề nhóm, dòng trống, dòng gộp ô) rồi hỏi người dùng xác nhận — file thầu thật hay có dòng phân nhóm xen giữa, chặn cứng ở đây sẽ khiến lệnh không dùng được với đúng loại file nó sinh ra để đọc.

No-clobber: file đã tồn tại → xuất `functions.new.md` kèm bảng khác biệt, không đè bản đã sửa tay.

### 4.2. `/speckit.dft-speckit.code-intel <tên-cụm> <FN-001..FN-012> [--deep]`

Kiểm đầu vào:
- Tên cụm là slug (`[a-z0-9_-]+`) — chặn, vì nó thành tên thư mục.
- FN không có trong `functions.md` → chặn, vì gần như chắc chắn là gõ nhầm mã.
- FN đã được cụm khác phủ → **cảnh báo, không chặn**. Một chức năng nền (đăng nhập, phân quyền) xuất hiện ở nhiều cụm là chuyện bình thường; cột `Cụm` trong `functions.md` cho phép nhiều giá trị.

Tạo `.specify/docs/<cụm>/` nếu chưa có (idempotent), ghi `intel.md` theo `intel-template`:

| § | Nội dung |
| --- | --- |
| 1 | Phủ FN — bảng `FN-ID ↔ tìm thấy ở đâu`; FN không tìm thấy code phải ghi rõ |
| 2 | Màn hình / endpoint |
| 3 | Thực thể & field (mượn hình dạng `domain-template`) |
| 4 | Validation & business rule |
| 5 | Luồng nghiệp vụ |
| 6 | Phân quyền |
| 7 | Tích hợp ngoài / job / event |
| 8 | Không suy được từ code — câu hỏi cho người |

**Luật xương sống — phân loại theo độ chắc chắn, không phải cấm viết.** Mỗi khẳng định ở §2–§7 rơi vào một trong ba dạng:

| Dạng | Cách ghi |
| --- | --- |
| Đọc thẳng từ code | Ghi bình thường, kèm `file:line` |
| Suy ra từ code, chưa chắc | Ghi kèm `file:line` gần nhất và đánh dấu `(suy đoán)` |
| Không có căn cứ nào trong code | Không viết ở §2–§7; đưa xuống §8 thành câu hỏi |

Bản đầu tiên của thiết kế này bắt buộc `file:line` cho mọi dòng. Nới ra vì có những thứ đúng nhưng không neo được vào một dòng code cụ thể — quy tắc rải trên bốn file, hành vi đến từ cấu hình framework, ràng buộc nằm trong migration đã chạy. Cấm viết chúng thì `intel.md` mất đúng phần khó nhất, còn §8 phình thành danh sách câu hỏi dài đến mức không ai trả lời.

`--deep` mở §3 tới từng field (kiểu, độ dài, nullable, mặc định, message lỗi) và §4 tới từng rule. Mặc định chạy mức gọn. Độ sâu đặt ở đây, không đặt ở lệnh `srs` — SRS luôn đổ hết những gì intel có.

Xong thì ghi ngược `Cụm` + `Nguồn code` vào `functions.md`.

No-clobber: chạy lại trên cụm đã có → giữ nguyên §8 đã được người trả lời và mọi ghi chú sửa tay.

### 4.3. `/speckit.dft-speckit.srs-from-code <tên-cụm> [--template <đường-dẫn>]`

Thiếu `<cụm>/intel.md` → **dừng**, nhắc chạy `code-intel` trước. SRS không có intel là viết từ trí tưởng tượng, đúng thứ đường ống này tồn tại để tránh.

Lấy khung: `--template` nếu có → `specify preset resolve srs-template` → fallback `.specify/extensions/dft-speckit/templates/srs-template.md`. Tham số `--template` để phục vụ khách hàng có template riêng mà không phải sửa file trong extension; mặc định vẫn là khung của công ty nên người dùng thông thường không phải biết đến nó.

Mục nào suy được từ `intel.md` thì rót thẳng. Mục mà code không bao giờ trả lời được — II.1 Mục đích, II.5 Phạm vi, IV Yêu cầu phi chức năng, N.1 Mục đích chức năng — thì phỏng vấn qua AskUserQuestion, gộp 1–4 câu độc lập mỗi lượt, cộng luôn các câu tồn ở §8 của intel.

Cổng cuối là `srs_verify.py`, phân hai mức:

**Chặn (`exit ≠ 0`, cấm báo xong)** — chỉ hai kiểm tra tất định:
- Mọi FN thuộc cụm có ≥1 dòng ở mục V (đặc tả hoặc khai ngoài phạm vi kèm lý do).
- Không còn placeholder `[…]`.

**Cảnh báo (`exit 0`, in ra để người soát)**:
- Mục cấp I–VI của khung bị thiếu hoặc lệch thứ tự — dự án có thể cố ý thêm/đổi mục, nên đây là nhắc chứ không phải lỗi.
- Chuỗi trông giống đường dẫn file hoặc `file:line`. Kiểm bằng mẫu chuỗi chắc chắn báo nhầm (tên file đính kèm trong mô tả nghiệp vụ, phiên bản dạng `x.y`), nên chỉ in vị trí nghi ngờ.
- Mục con còn nguyên tiêu đề nhưng không có nội dung.

Script nhận `--template <đường-dẫn>` để biết danh sách mục cần đối chiếu, mặc định dùng khung ship kèm.

## 5. Template

### 5.1. `srs-template.md` — đã tạo

Khung lấy từ tài liệu ban hành của công ty (BRD Quản lý tài khoản và xác thực), giữ nguyên tên và thứ tự mục lớn, đẩy độ chi tiết bên trong lên mức SRS:

```
I.   KIỂM SOÁT PHIÊN BẢN      I.1 Lịch sử thay đổi · I.2 Ma trận trách nhiệm
II.  GIỚI THIỆU               II.1 Mục đích · II.2 Tài liệu tham khảo
                              II.3 Quy ước từ viết tắt · II.4 Quy ước về ký hiệu · II.5 Phạm vi
III. ĐẶC TẢ YÊU CẦU CHỨC NĂNG   mỗi chức năng một khối N:
     N.1 Mục đích chức năng
     N.2 Đối tượng tham gia và phân quyền
     N.3 Mô tả chức năng (văn xuôi + giao diện + sơ đồ luồng + bảng Mô tả điều khiển)
     N.4 Đặc tả dữ liệu            ← thêm so với BRD
     N.5 Quy tắc nghiệp vụ
     N.6 Xử lý ngoại lệ và thông báo   ← thêm
     N.7 Giao tiếp hệ thống            ← thêm
IV.  YÊU CẦU PHI CHỨC NĂNG                ← thêm
V.   MA TRẬN TRUY VẾT                     ← thêm
VI.  PHỤ LỤC
```

Dùng lại nguyên văn từ tài liệu công ty: chú giải RACI ở I.2 và ba bảng ký hiệu ở II.4 (flowchart, ký hiệu trường, loại điều khiển). Chúng giống nhau ở mọi tài liệu nên để sẵn trong khung, command không phải nghĩ lại. Dự án dùng bộ ký hiệu khác thì thay cả bảng.

**Ba luật một-nhà** cài vào khung, cùng kỷ luật `spec-template` của preset — mục đích là sửa một chỗ thay vì ba chỗ, không phải để bắt lỗi:
- N.3 (Mô tả điều khiển) nói trình bày và hành vi; hằng số dữ liệu có nhà ở N.4, nội dung message có nhà ở N.6. Nhắc lại ngắn cho dễ đọc thì được, miễn hai chỗ không ghi hai giá trị khác nhau.
- N.6 chép nguyên văn message lấy được từ hệ thống thật (file ngôn ngữ, hằng số, mã lỗi); không tìm được thì mô tả ý nghĩa và đánh dấu `(cần xác nhận)`.
- N.4 **chỉ** ghi ràng buộc có căn cứ trong code (entity, DTO, validator, migration). Suy đoán thì để trống và hỏi người dùng; câu trả lời của họ mới là căn cứ để điền. Đây là ngoại lệ có chủ ý của luật "chỗ chưa chắc thì đánh dấu, đừng bỏ trống" ở §3.3 — bảng này là chuẩn để QA dựng testcase biên và khách đối chiếu lúc nghiệm thu, nên một con số suy đoán lọt vào đây thành cam kết sai, tệ hơn hẳn một ô trống.

Mục con không áp dụng thì lược bỏ (chức năng thuần đọc không cần N.4, chức năng không gọi ra ngoài không cần N.7). Vài chức năng nhỏ dùng chung một màn hình gộp được vào một khối, miễn bảng II.5 và ma trận V vẫn liệt kê đủ từng mã.

Ma trận truy vết ở V là `Mã chức năng | Tên chức năng | Mục SRS` — **không có** cột nguồn code (tài liệu giao khách).

### 5.2. `intel-template.md` — chưa tạo

Khung tám mục ở §4.2, mục entity mượn hình dạng `domain-template`.

## 6. Đóng gói

Thêm vào `speckit-extension`:
- `commands/fnlist-import.md`, `commands/code-intel.md`, `commands/srs-from-code.md`
- `templates/srs-template.md` (đã có), `templates/intel-template.md`
- `scripts/fnlist_import.py`, `scripts/srs_verify.py`
- Khai đủ trong `extension.yml` dưới `provides` — file không khai thì không có tác dụng.
- Bump version `extension.yml` trước khi chạy `release.sh`.

**Gotcha bắt buộc kiểm**: `build-zip.sh` phải `cp -R` mọi thư mục support mà command tham chiếu tới. Manifest `provides` chỉ khai command/template, **không** quyết định cái gì được đóng gói. Thiếu một dòng `cp` là ship command hỏng.

## 7. Kiểm thử

Theo đúng quy trình đã ghi trong `CLAUDE.md`:

1. `speckit-extension/build-zip.sh` → `unzip -l` xác nhận `templates/srs-template.md`, `templates/intel-template.md`, `scripts/fnlist_import.py`, `scripts/srs_verify.py` thực sự có trong gói.
2. Serve localhost, `specify extension add --from` vào một project `specify init --here --integration claude` vứt đi.
3. Chạy ba lệnh trên một codebase thật, kiểm `ls .specify/docs/<cụm>/`.
4. `srs_verify.py` chạy được standalone trên một `srs.md` cố tình thiếu một FN — phải exit ≠ 0.
5. `fnlist_import.py` smoke-test standalone với một Excel mẫu, không cần dựng cả project.

## 8. Rủi ro

| Rủi ro | Giảm thiểu |
| --- | --- |
| LLM bịa hành vi hệ thống không có thật | Phân loại ba dạng khẳng định ở `intel.md` §2–§7; không căn cứ thì xuống §8 |
| Suy đoán trôi vào tài liệu mà không ai biết | Đánh dấu `(suy đoán)` ở intel, `(cần xác nhận)` ở SRS — người soát tìm được bằng một lần tìm chuỗi |
| Tài liệu giao khách lộ đường dẫn code | Nhắc ở đầu template + cảnh báo của `srs_verify.py` |
| `.specify/` bị gitignore, tài liệu không vào git | Cả ba command kiểm và cảnh báo trước khi ghi |
| Nâng cấp `specify` CLI clobber command | Đã có quy trình trong `CLAUDE.md`: disable/enable lại addon sau mỗi lần nâng cấp |
| Sót chức năng khi nghiệm thu | Ma trận truy vết V + cổng chặn của `srs_verify.py` |
| Nới lỏng quá tay, tài liệu ra kém chất lượng | Chấp nhận có chủ ý ở bản đầu: chạy thật vài dự án rồi siết đúng chỗ hay sai, thay vì đoán trước |
