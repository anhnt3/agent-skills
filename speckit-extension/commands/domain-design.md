---
description: Thiết kế/cập nhật domain tổng thể cho MỘT CỤM CHỨC NĂNG (danh sách RM-xxx trong docs/roadmap.md) — rút entity/FK/enum/rule chung từ BRD (docs/brd/, qua trường Nguồn của roadmap) VÀ codebase, ghi docs/domain/<cụm>.md làm nền model cho /speckit.specify từng RM. Nhận lại RM đã design lần trước (mở rộng doc cũ, không tạo doc trùng). Chạy được cả khi dự án chưa có dòng code nào.
---

# Domain design cho cụm chức năng (nhận danh sách RM)

Trước khi specify từng màn, dựng **domain tổng thể** cho một cụm chức năng liên quan nhau: entity, FK, quan hệ, enum, rule chung. Mục tiêu = specify **tách từng RM** nhưng **không vênh model**, vì mọi RM trong cụm cùng đọc 1 domain doc. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: doc MỎNG — chỉ model + ràng buộc chung. KHÔNG đào FR, KHÔNG edge-case từng màn (để dành `/speckit.specify`). Living doc: specify lòi ra thiếu → sửa ngược. Just-in-time: chỉ design cụm sắp tới lượt, KHÔNG design cả dự án trước (tránh over-design). **Thứ tự**: RM bị phụ thuộc (Wave thấp, shared entity như doanh nghiệp/gói dịch vụ) nên design trước để cụm sau tham chiếu external tới doc đã có.

**Vì sao gộp cả danh sách vào 1 doc**: entity KHÔNG map 1-1 với màn — `User`/`Role`/`Permission` trải khắp nhiều RM. Tách mỗi RM một file thì hoặc copy lại entity (hai nguồn sự thật = đúng cái vênh cần chống), hoặc bắc tham chiếu external chằng chịt mà `/speckit.specify` phải lần nhiều file mới ráp đủ một aggregate. Nên: **1 doc = 1 bounded context** = cụm RM **thật sự chia sẻ entity**. Gộp hai nhóm RM không dính entity nào chỉ vì tiện gõ một lệnh → doc phình mà không chống vênh được gì; thấy vậy phải nói thẳng và đề xuất chạy hai lệnh riêng.

## User Input

`$ARGUMENTS`

Kỳ vọng: **danh sách chức năng theo ID `RM-xxx`** trong `docs/roadmap.md` (một hoặc nhiều), phân tách bằng dấu phẩy hoặc khoảng trắng.

**Cú pháp hợp lệ — chỉ hai dạng:**
- `RM-001` — ID đơn, `RM-` + **đúng 3 chữ số**.
- `RM-003..RM-012` — khoảng, lấy mọi RM từ đầu đến cuối **theo thứ tự dòng trong bảng tổng** của roadmap (không phải theo số học), bao gồm hai đầu.

**Validate cứng trước khi làm bất cứ gì khác — KHÔNG tự dịch, KHÔNG đoán:**
- Phần tử nào không khớp hai dạng trên → **DỪNG**, in phần tử sai và cú pháp hợp lệ.
- **Đầu vào là tên module** (`system/admins`, `khdn`, có `/` hoặc là giá trị cột `Module`) → **KHÔNG chấp nhận, KHÔNG tự nở thành danh sách RM**. Lệnh này nhận chức năng, không nhận module: một module có thể có RM chưa tới lượt design, tự nở là kéo vào phạm vi thứ người dùng không chọn. Xử lý: in bảng RM của module đó (ID, tên màn, Wave) và bảo người dùng chọn RM cần design, rồi dừng chờ.
- `RM-xxx` đúng cú pháp nhưng **không có trong roadmap** → DỪNG, liệt kê ID có thật quanh đó.
- Trùng lặp → gộp, báo số đã gộp.
- **Trống** → đọc roadmap, liệt kê item theo Wave kèm cột Module, gợi ý cụm nên gom (cùng Wave / cùng module / phụ thuộc lẫn nhau), hỏi người dùng chọn qua AskUserQuestion. Không tự chọn hộ.

**Cả danh sách gom vào 1 domain doc chung**: quan hệ giữa các entity của các RM trong danh sách là **nội bộ**; external chỉ khi trỏ tới entity của RM NGOÀI danh sách.

## Quy trình (bắt buộc theo thứ tự)

### 1. Chốt phạm vi từ danh sách RM

`docs/roadmap.md` KHÔNG tồn tại → **dừng**. Roadmap là **đầu vào bắt buộc**: mọi RM-ID, cột `Module`, trường `Nguồn` đều từ đó. Nhắc chạy trước một trong hai, tuỳ dự án khởi từ đâu:
- `/speckit.dft-speckit.road-map-from-brd` — dự án khởi từ tài liệu BRD (`docs/brd/`, đầu ra của `brd-import`), kể cả khi chưa có dòng code nào.
- `/speckit.dft-speckit.road-map-from-codebase` — dự án đã có code.

Với mỗi RM trong danh sách đã validate, đọc khối chi tiết trong roadmap: tên màn, `Mô tả`, `Thực thể/CRUD`, `Phụ thuộc`, `Nguồn`, và cột `Module` ở bảng tổng.

**Hai mỏ neo đếm — chốt ngay, ghi ra cho người dùng thấy** (bước 8 đếm lại, KHÔNG tin danh sách bước này):
- `N` = số RM-ID phân biệt trong phạm vi (sau khi gộp trùng và nở khoảng).
- `E` = số **thực thể phân biệt** ở trường `**Thực thể/CRUD**` của các RM đó (gộp trùng tên). Trường này nằm trong **khối Chi tiết** mỗi item, KHÔNG phải cột của bảng tổng.
  - Trường đó trống / `N/A` / chỉ ghi tên màn (không phải danh từ thực thể) ở ≥1 RM → **`E` không đáng tin**: nói thẳng với người dùng và bỏ dùng `E` ở bước 8.
  - **Mỏ neo phân tán, áp trong MỌI trường hợp**: không entity nào được gánh **quá 1/2** số RM trong phạm vi ở cột `Dùng ở (RM)`. Đây mới là thứ thật sự chặn entity catch-all — `E` chỉ chặn được khi roadmap ghi thực thể tử tế (12 màn CRUD cùng ghi `Thiết bị` thì `E = 1`, một entity là đủ qua).

**Module dẫn xuất**: tập giá trị cột `Module` của các RM đã chọn. Dùng để đặt tên file và điền dòng `Phủ module` ở bước 7 — KHÔNG dùng để mở rộng phạm vi. Với mỗi module dẫn xuất, đếm luôn số RM của module đó **nằm ngoài** phạm vi: >0 nghĩa là doc này phủ module đó **một phần**, phải ghi rõ ở header (xem bước 7).

**Bounded context**: nhìn `Thực thể/CRUD` và `Phụ thuộc` — nếu hai nhóm RM trong danh sách **không chia sẻ entity nào**, nói thẳng và đề xuất chạy hai lệnh riêng thay vì gộp. Đừng lặng lẽ gộp cho xong.

**Phụ thuộc chéo**: với mỗi RM-ID ở cột `Phụ thuộc`, xem nó trong hay ngoài phạm vi (giá trị phi-RM như `auth`, `permission`, `N/A` thì bỏ qua). Phụ thuộc RM **ngoài phạm vi** → entity của RM đó là **tham chiếu ngoài** (external): trỏ FK tới, KHÔNG định nghĩa lại (xem bước 5).

### 2. Đối chiếu doc domain đã có — chốt CHẾ ĐỘ CHẠY

Chạy **trước khi phỏng vấn**, vì kết quả quyết định toàn bộ phần sau. Quét `docs/domain/*.md`, mỗi file đọc `**Phủ RM**`, `**Phủ module**` và bảng §1. Đối chiếu với phạm vi:

- **Mọi RM trong phạm vi đều đã được một doc phủ** → **KHÔNG có gì để thiết kế mới**. Báo doc đó, hỏi qua AskUserQuestion: (a) rà lại doc (giải nợ §6, bổ sung field thiếu) — chạy tiếp ở chế độ **mở rộng**; (b) dừng, không làm gì. Không được lặng lẽ sinh doc thứ hai.
- **Một phần RM đã có doc, phần còn lại chưa** → **chế độ mở rộng**: mặc định **cập nhật chính doc đang phủ** (thêm RM mới vào `Phủ RM`, thêm entity/FK phát sinh), KHÔNG tạo doc mới song song. Chỉ tách doc mới khi người dùng chọn, và khi đó doc cũ giữ nguyên RM của nó.
- **RM trong phạm vi rải ở NHIỀU doc khác nhau** → DỪNG, hỏi: gộp các doc đó làm một (doc bị thay thì **xoá `Phủ RM` khỏi nó và ghi một dòng trỏ sang doc mới**, để lần quét sau không khớp nhầm vào doc rỗng), hay thu hẹp phạm vi lần chạy này. Đừng tự gộp.
- **Trùng entity dù RM không trùng** → entity sắp định nghĩa trùng tên với entity ở §1 của doc khác. Hỏi: (a) tham chiếu **external** tới doc đang sở hữu — mặc định nên chọn; (b) gộp hai doc. Đây là ca hay gặp nhất trong luồng just-in-time: cụm sau toàn RM mới nhưng dùng lại entity cụm trước đã định nghĩa; registry `Phủ RM` không bắt được ca này, chỉ §1 bắt được.
- **Doc cũ không có dòng `Phủ RM`** (sinh bằng khung trước) → suy phạm vi theo thứ tự: cột `Dùng ở (RM)` ở §1 → dòng `Phủ module` → cuối cùng mới tới tên file (tên file chỉ là gợi ý yếu, không phải khoá). Nghi ngờ → coi là **CÓ** xung đột và hỏi người dùng; đoán "chắc không trùng" là bỏ rơi doc cũ. Chốt xong thì bổ sung `Phủ RM` cho doc đó khi cập nhật.

Chốt xong chế độ chạy (**tạo mới** / **mở rộng doc X** / **dừng**) mới đi tiếp. Nói rõ chế độ đã chốt cho người dùng.

### 3. Đọc nguồn, KHÔNG đoán

Rút model từ **nguồn thật**, không bịa. Nguồn thật gồm **tài liệu BRD** và **code** — hai thứ ngang hàng, KHÔNG phải chọn một: dự án nào có cả hai thì **đọc cả hai** (BRD cho ý định nghiệp vụ, code cho model đã hiện thực), lệch nhau thì nêu ở §6 chứ đừng tự chọn bên. Tự tìm nguồn (đừng giả định layout — quét thật):

- **Tài liệu BRD** (`docs/brd/`): với **mỗi RM trong phạm vi**, đọc trường `**Nguồn**` ở khối chi tiết item đó. Trỏ `docs/brd/…md` (có thể kèm `#<tiêu đề mục>`) → `Read` đúng file/mục đó. Rút entity, field + kiểu + ràng buộc từ **bảng trường**, enum từ danh sách trạng thái/giá trị cho phép, quan hệ từ mô tả nghiệp vụ, phân quyền từ mục quyền. Cite bằng `docs/brd/<đường-dẫn>.md#<mục>`. `Nguồn` = `N/A` hoặc trỏ đường dẫn code → RM đó không có BRD, dùng nhánh code.
- **Domain doc đã có** (`docs/domain/*.md`): §1 của mọi doc trong thư mục. Entity đã được doc khác định nghĩa → **KHÔNG định nghĩa lại**, dùng làm **tham chiếu external** (bước 5).
- **Phía client/mockup**: model/type/interface + service — field, kiểu, quan hệ ngầm (id tham chiếu), enum, danh sách trạng thái.
- **Phía server (nếu đã bắt đầu)**: entity/model, DTO, enum, error code, migration/schema — bất kể ngôn ngữ/framework.
- **Nguồn framework hợp lệ**: base class / package / module nền tảng mà entity kế thừa hoặc framework cung cấp sẵn. Nhận diện qua class kế thừa base của framework, package đã import, cấu hình module. Cite **phải nêu đích danh tên class/package + nơi thấy nó** (vd `kế thừa BaseAuditEntity, khai ở src/Domain/Common`). Cite chung chung ("framework Identity có sẵn") KHÔNG hợp lệ, coi như bịa.
- Không tìm được nguồn (BRD, code, doc cũ, lẫn framework) cho một entity → ghi vào §6, KHÔNG bịa field. Không xác định được vị trí code → hỏi lại, đừng đoán.
- **Chưa có code (dự án khởi từ BRD, repo mới chỉ có `docs/`)** → nói thẳng "chưa có codebase, model rút hoàn toàn từ BRD", chạy tiếp bằng nguồn BRD. KHÔNG hỏi vòng vo, KHÔNG dừng, và **KHÔNG được lấy đó làm lý do đẩy cả bộ entity vào §6** — BRD đã có bảng trường thì đó là nguồn đủ để rút model.
- **§6 không phải chỗ né việc**: mỗi mục phải kèm nhãn loại + lý do kiểm chứng được ("đã đọc `docs/brd/…md#…` và quét `<đường dẫn/pattern>`, không thấy nguồn"). Cấm mục trống lý do, và cấm ghi lý do cho một nguồn khi nguồn kia còn chưa đọc.

### 4. Ưu tiên dùng lại đồ framework đã cho

Trước khi định nghĩa entity/field/enum MỚI, kiểm tra framework/nền tảng **đã cung cấp sẵn** chưa (user/role/permission/tenant, trường audit, khóa, soft-delete, cây phân cấp…). Có sẵn →
- **Dùng thẳng** nếu đủ; **mở rộng/kế thừa** nếu thiếu — KHÔNG dựng bản song song.
- Ghi rõ entity nào "framework (dùng lại)" vs "framework + mở rộng" vs "mới hoàn toàn", kèm cite.

Chỉ tạo entity mới khi framework KHÔNG có. Bịa lại cái framework đã lo = nợ kỹ thuật, cấm.

**"Chưa có codebase" = TOÀN REPO** không có mã nguồn ngoài `docs/`, `.specify/` — phải nêu bằng chứng (đã `Glob` pattern gì, kết quả rỗng), không tự tuyên bố. **RM này chưa có code nhưng repo đã có code → KHÔNG áp nhánh dưới**: framework vẫn tồn tại và vẫn phải kiểm đủ, nếu không sẽ định nghĩa lại User/Role/audit mà framework đã lo.

Đúng là chưa có codebase → **bỏ qua bước này và nói thẳng** "chưa có code nên chưa biết framework, entity đánh dấu nguồn gốc `BRD`". Ghi vào §6 một dòng `[nợ framework]`. KHÔNG dừng, và **CẤM suy đoán framework** ("chắc dùng ASP.NET Identity") — chưa có code thì không có căn cứ.

### 5. Rút domain (mỏng)

- **Entity** + đánh dấu aggregate root vs entity con.
- **Field chính**: chỉ khóa/định danh/enum/FK + field ảnh hưởng ràng buộc. Bỏ field thuần UI.
- **Quan hệ & FK**: hướng, cardinality (1-N/N-N/1-1), **on-delete** (mặc định Restrict). FK trỏ entity **ngoài phạm vi doc** → đánh dấu **external**, ghi rõ doc sở hữu; định nghĩa là việc của doc đó, doc này CHỈ tham chiếu (không copy field). Chưa có doc sở hữu → ghi vào §6 nhãn `[external]`.
- **Enum & error code**.
- **Rule chung** áp nhiều RM (định nghĩa 1 lần).

### 6. Interview chỗ mơ hồ (AskUserQuestion)

**Mở đầu: đọc file decisions nếu có.** Đường dẫn tất định từ phạm vi (xem cuối bước này). File tồn tại và `rm_ids` khớp **đúng** danh sách hiện tại → đọc lên làm điểm xuất phát, **KHÔNG hỏi lại** cái đã có trong `answers`. Lệch dù một phần tử → bỏ qua file, hỏi từ đầu (quyết định cũ gắn với phạm vi cũ). Ở **chế độ mở rộng**, quyết định đã ghi trong doc cũ cũng tính là đã chốt — KHÔNG hỏi lại.

Hỏi qua AskUserQuestion, mỗi lượt gom **1–4 câu độc lập nhau**; câu phụ thuộc kết quả câu trước → tách lượt sau. Mỗi câu 2–4 option kèm lý do + trade-off; `(Recommended)` CHỈ khi có căn cứ từ nguồn bước 3 (nêu căn cứ ngay trong option) — quyết định thiết kế mà nguồn không cho căn cứ thì không đánh Recommended, gợi ý bừa là dẫn người dùng chốt ý của bạn.

Chỉ hỏi cái **quyết định model, không suy được từ nguồn**: quan hệ N-N có cần bảng nối; aggregate boundary; on-delete; field chung nên nằm ở entity nào.

Fact tra từ nguồn; **quyết định thiết kế là của người dùng** — **chờ phản hồi thật**, cấm tự suy "chắc đồng ý". Không chắc một thứ là fact hay quyết định → coi là **quyết định**, phải hỏi.

**On-delete — tiêu chí hỏi đếm được**: FK nối **hai aggregate root khác nhau**, HOẶC entity cha xuất hiện trong RM có thao tác Xóa → thuộc diện phải hỏi. Chỉ được lấy mặc định Restrict không hỏi cho FK trỏ dữ liệu danh mục thuần (lookup/enum-table), và mọi FK lấy mặc định phải ghi vào cột Ghi chú §3: `mặc định Restrict, chưa hỏi`.

**Trần: tối đa 4 lượt AskUserQuestion ở bước này.** Hỏi cái không chắc trước. Hết trần mà còn điểm chưa chốt → ghi phương án của bạn kèm `chưa chốt — sửa trực tiếp nếu sai` ở cột Ghi chú, KHÔNG hỏi tiếp. **Trần không phải sàn**: chỉ được dùng nhãn `chưa chốt` sau khi đã thực sự dùng hết 4 lượt, hoặc khi không còn điểm nào thuộc diện phải hỏi.

**Persist quyết định** — có phản hồi rồi thì ghi ngay trước khi sang bước 7. Tên file suy **tất định từ phạm vi**, KHÔNG dùng tên cụm (tên cụm mãi bước 7 mới chốt): danh sách RM-ID **sắp xếp tăng dần**, nối bằng `_`:
`.specify/tmp/domain-design/RM-001_RM-004_RM-007.decisions.json`

```json
{
  "rm_ids": ["RM-001", "RM-004", "RM-007"],
  "N": 3, "E": 5,
  "answers": [
    {"hoi": "on-delete User -> AdminGroup", "chot": "Restrict", "can_cu": "người dùng chọn"}
  ]
}
```

Danh sách dài (>8 RM) làm tên file quá dài → dùng `RM-<đầu>__<cuối>__<số lượng>.decisions.json` (vd `RM-001__RM-020__12.decisions.json`) và so khớp bằng `rm_ids` **bên trong** file, không bằng tên. File này là **trợ giúp nối lại phiên, KHÔNG phải giấy phép ghi đè**: luật no-clobber ở bước 7 vẫn áp nguyên.

### 7. Ghi `docs/domain/<cụm>.md` theo khung CỐ ĐỊNH

**Kiểm lại xung đột ngay trước khi ghi** (bước 2 đã chốt chế độ, nhưng phạm vi có thể đã đổi sau khi hỏi): quét lại `docs/domain/*.md`, đối chiếu `Phủ RM` + §1. Phát sinh xung đột mới → DỪNG, chưa ghi gì, hỏi lại.

- Lấy khung: `specify preset resolve domain-template`; không resolve được → đọc `.specify/extensions/dft-speckit/templates/domain-template.md`; vẫn không thấy → hỏi.
- **Tên file** (chỉ khi tạo mới; chế độ mở rộng giữ nguyên tên doc cũ): đặt tên **gợi nhớ theo nội dung cụm** — prefix chung của module dẫn xuất nếu có (cả 3 RM đều `system/*` → `system`), không có thì hỏi người dùng tên cụm qua AskUserQuestion (đề xuất tên nối `-` làm option Recommended, căn cứ: suy từ tên các module/màn). Chuẩn hóa: lowercase, ký tự ngoài `[a-z0-9-]` → `-`, gộp `-` liền kề. Tạo `docs/domain/` nếu chưa có.
  - Tên file **không phải khoá tra cứu**: `/speckit.specify` và `/speckit.plan` tìm domain doc bằng **quét nội dung** `docs/domain/` (đối chiếu `Phủ RM` / `Phủ module` / §1) rồi **hỏi người dùng xác nhận**, KHÔNG suy theo tên file. Vì vậy **không cần file stub** cho module lẻ — đặt tên sao cho người đọc nhận ra cụm là đủ.
- **Header phải khai đủ hai dòng — đây mới là thứ specify/plan đối chiếu**: `**Phủ RM**` = đúng danh sách RM doc này phủ (chế độ mở rộng: cũ + mới); đây là khoá khớp **chắc** của specify/plan, thiếu một RM là RM đó tìm không ra doc. `**Phủ module**` = module dẫn xuất, mỗi module ghi rõ **đầy đủ** hay **một phần** kèm RM còn thiếu — ghi `đầy đủ` khi mới phủ một phần là nói dối người đọc: specify của RM chưa phủ sẽ khớp vào doc này và tưởng model đã có.
- **File CHƯA tồn tại** → copy đúng cấu trúc khung, chỉ **điền** placeholder `[…]`, thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **File ĐÃ tồn tại (chế độ mở rộng)** → **ĐỌC file hiện tại trước**, chỉ chèn/sửa entity tại chỗ; **KHÔNG copy khung đè**. Giữ nguyên §6 và mọi quyết định đã chốt; cập nhật `Phủ RM`/`Phủ module`/`Cập nhật`. Mục §6 nay bước 3 đã tìm được nguồn → gạch khỏi đó và điền vào entity (giải nợ).
  - **Ngoại lệ migration khung — DUY NHẤT**: doc sinh bằng bản khung cũ thiếu **phần cấu trúc** của khung hiện tại (dòng `Phủ RM`, dòng `Phủ module`, cột `Nguồn (cite)` ở §1, nhãn loại ở §6) → được phép thêm **đúng phần thiếu đó**; entity chưa biết nguồn điền `[chưa cite — bổ sung khi rà]`, mục §6 chưa có nhãn thì gán nhãn theo nội dung. Không đụng nội dung đã có.

### 8. Verification (trước khi báo xong)

Fail bất kỳ mục nào → sửa rồi chấm lại, KHÔNG báo xong.

- **Đếm lại từ `docs/roadmap.md`** (không dùng lại danh sách bước 1): số RM trong phạm vi phải bằng `N`; mọi RM đó xuất hiện ở cột `Dùng ở (RM)` của ít nhất 1 entity. RM **không sinh/đụng entity nào** (dashboard, báo cáo tổng hợp) → ghi vào §6 nhãn `[không sinh entity]` kèm lý do, tính là đã phủ; KHÔNG gán bừa vào một entity cho qua gate.
- **`Phủ RM` ở header liệt kê đúng và đủ** `N` RM (chế độ mở rộng: đủ cả RM cũ lẫn mới). Thiếu một RM = lần chạy sau tưởng RM đó chưa design, sinh doc trùng.
- **§1 phải có ≥ `E` entity** (bỏ mục này nếu bước 1 đã kết luận `E` không đáng tin). Ít hơn → giải trình từng thực thể roadmap-nêu mà không thành entity domain. Không giải trình được → fail: doc đang rỗng ruột.
- **Mỏ neo phân tán**: không entity nào chiếm quá **1/2** số RM trong phạm vi ở cột `Dùng ở (RM)` → vượt là dấu hiệu entity catch-all, fail. Áp cả khi `E` không dùng được.
- **Không định nghĩa lại entity của doc khác**: entity ở §1 không trùng tên với entity ở §1 của doc khác trong `docs/domain/`, trừ khi đã đánh dấu `external ([doc sở hữu])`. Trùng mà không đánh dấu → fail.
- Mọi entity ở §1 phải có khối tương ứng ở §2. Entity có ở bảng mà không field nào → fail.
- Mọi FK ở §3 trỏ tới: entity có thật ở §1 (nội bộ), HOẶC entity **external** đã nêu doc sở hữu, HOẶC §6 nhãn `[external]`. FK có entity đích **nằm trong phạm vi doc này** mà bị đẩy sang §6 → fail. FK trỏ vào hư vô → fail.
- **Trần §6** — chỉ tính mục gắn nhãn `[không thấy nguồn]`: quá **1/3** số entity, HOẶC ≥3 mục dùng **cùng một chuỗi lý do** → KHÔNG được báo xong: dừng, trình danh sách và hỏi nguồn. Mỗi mục phải nêu đường dẫn/pattern **thực sự đã chạy trong phiên này**. Mục nhãn `[không sinh entity]` / `[nợ framework]` / `[external]` / `[lệch BRD↔code]` không tính vào trần.
- §4 và §5: mỗi dòng truy được về nguồn bước 3 hoặc quyết định người dùng ở bước 6.
- Không còn placeholder `[…]` sót lại.
- Không field bịa: mọi field truy được về nguồn ở bước 3 — cite **đích danh**; "framework nói chung" hay "theo BRD" trống trơn → fail — hoặc nằm ở §6.
- **Đã đọc BRD chưa**: mọi RM có `Nguồn` trỏ `docs/brd/` thì file BRD đó phải thực sự được `Read` trong phiên này và xuất hiện ở cột `Nguồn (cite)` của ít nhất một entity, hoặc được giải trình ở §6 bằng mục nhãn `[không thấy nguồn]`. Sinh doc mà chưa mở file BRD nào → fail, kể cả khi codebase đã cho đủ model. Nhãn `[chưa cite — bổ sung khi rà]` chỉ chấp nhận cho entity có từ trước phiên này (migration khung), KHÔNG cho entity mới thêm.

Kết thúc: báo chế độ chạy (tạo mới / mở rộng doc nào), danh sách RM đã phủ, module dẫn xuất kèm đầy-đủ/một-phần, đường dẫn file, `N`/`E`, số entity, số FK, số mục §6 còn lại theo nhãn, số điểm `chưa chốt`. Rồi nhắc:
`/speckit.specify <RM-ID>` — specify tự tìm doc này bằng cách quét `docs/domain/` và đối chiếu `Phủ RM`, rồi hỏi bạn xác nhận.

## Sai lầm thường gặp

- **Nhận tên module rồi tự nở thành danh sách RM** → kéo vào phạm vi RM người dùng không chọn. Lệnh này nhận RM, module chỉ là thứ dẫn xuất.
- **Design cả dự án 1 lần** → BDUF, đoán sai. Chỉ làm cụm sắp tới lượt.
- **Gộp hai nhóm RM không chia sẻ entity nào vào 1 doc** → doc phình mà không chống vênh được gì. 1 doc = 1 bounded context.
- **RM đã design lần trước, lần này sinh doc mới song song** → hai nguồn sự thật, specify tra khớp-chính-xác-trước-prefix nên có thể vẫn đọc bản cũ stale. Bước 2 chốt chế độ **mở rộng** chính doc đang phủ.
- **Định nghĩa lại entity doc khác đã có, chỉ vì RM lần này là RM mới** → `Phủ RM` không bắt được ca này; phải đọc §1 của mọi doc ở bước 3. Entity đã có chủ = tham chiếu external.
- **Ghi `Phủ module: đầy đủ` khi mới phủ một phần** → specify của RM chưa phủ tìm thấy doc và tưởng model đã có, spec ra thiếu entity.
- **Nhồi FR/edge-case màn vào domain doc** → loãng, trùng specify. Domain chỉ model + ràng buộc.
- **Chỉ quét code, bỏ qua BRD** → dự án khởi từ BRD ra doc rỗng ruột mà vẫn báo xong; dự án có code thì mất ý định nghiệp vụ chỉ BRD mới có. Đọc cả hai.
- **Bịa field không có trong nguồn** → ghi §6 nhãn `[không thấy nguồn]` kèm lý do kiểm chứng được.
- **Dồn cả bộ entity vào §6 cho nhanh** → trần 1/3 bắt được, và doc đó vô dụng với specify.
- **Một entity catch-all gánh cả `N` RM** → mỏ neo phân tán bắt được.
- **Clobber §6 / quyết định cũ khi chạy lại** → mất context. No-clobber mục đó.
- **Ghi đè lên doc domain thật của lần chạy trước** → xoá trắng quyết định đã chốt. Kiểm registry `Phủ RM` + §1 trước khi ghi bất cứ gì.
- **Thiếu RM trong dòng `Phủ RM`** → specify/plan quét nội dung để tìm doc, RM không có trong đó thì coi như chưa có domain doc; và lần chạy domain-design sau tưởng RM đó chưa design.
- **Quên on-delete** → specify màn xóa vênh nhau. Luôn nêu, mặc định Restrict, ghi rõ chưa hỏi.
- **Đẩy entity framework (Identity/audit) vào §6 vì không thấy trong repo** → sai. Base class/package framework là nguồn hợp lệ, đánh dấu "framework (dùng lại)".
