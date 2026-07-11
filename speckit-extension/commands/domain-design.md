---
description: Thiết kế/cập nhật domain tổng thể cho MỘT hoặc NHIỀU module trong docs/roadmap.md — rút entity/FK/enum/rule chung, ghi docs/domain/<module>.md làm nền cho /speckit.specify từng màn.
---

# Domain design cho module (nhận danh sách)

Trước khi specify từng màn, dựng **domain tổng thể** cho một hoặc nhiều module: entity, FK, quan hệ, enum, rule chung. Mục tiêu = specify **tách từng màn** nhưng **không vênh model**, vì mọi màn cùng đọc 1 domain doc. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: doc MỎNG — chỉ model + ràng buộc chung. KHÔNG đào FR, KHÔNG edge-case từng màn (để dành `/speckit.specify`). Living doc: specify lòi ra thiếu → sửa ngược. Just-in-time: chỉ design module sắp tới lượt, KHÔNG design cả dự án trước (tránh over-design). **Thứ tự**: module bị phụ thuộc (Wave thấp, shared entity như doanh nghiệp/gói dịch vụ) nên design trước để module sau tham chiếu external tới doc đã có.

## User Input

`$ARGUMENTS`

Kỳ vọng: **một hoặc danh sách giá trị cột `Module`** trong `docs/roadmap.md`, phân tách bằng dấu phẩy hoặc khoảng trắng (vd `system/admins, system/groups, system/roles`). Roadmap KHÔNG đánh số module — nhận tên module, không nhận số.

**Cả danh sách gom vào 1 domain doc chung** — vì các module đi cùng nhau thường chia sẻ model (vd `system/admins` + `system/groups` + `system/roles` cùng User/Role/Permission). Gom chung để entity dùng chung định nghĩa 1 lần, quan hệ giữa chúng là **nội bộ** (không phải external). Đây chính là mục tiêu chống vênh.

Mỗi phần tử nhận dạng:
- **Khớp chính xác** một module (vd `khdn/devices`) → mọi item module đó.
- **Prefix** (vd `system` hoặc `system/*`) → mọi module bắt đầu bằng prefix. Tương đương liệt kê tay các module con. Roadmap không dùng quy ước `<khu-vực>/<module>` (không có `/`) → prefix chỉ khớp đầu chuỗi; nói rõ điều này khi báo phạm vi.

Gộp mọi item của mọi phần tử = phạm vi domain của **1 doc**.

- **Tên file**: theo quy tắc ở bước 6.
- Trống → đọc roadmap, **liệt kê các module** kèm số item, gợi ý cụm nên gom (prefix/phụ thuộc chung), hỏi người dùng chọn (AskUserQuestion) — cho chọn nhiều gom 1 doc.
- Phần tử nào không khớp → liệt kê module có thật, hỏi lại. **Đừng đoán.**

## Quy trình (bắt buộc theo thứ tự)

**Danh sách nhiều phần tử**: gộp mọi item của mọi phần tử thành **1 phạm vi**, chạy bước 1→7 **một lần** ra **1 doc chung**. Quan hệ giữa các module trong danh sách = nội bộ (cùng doc). External chỉ khi trỏ tới module NGOÀI danh sách.

### 1. Chốt phạm vi từ roadmap
`docs/roadmap.md` KHÔNG tồn tại → **dừng**, nhắc chạy `/speckit.dft-speckit.road-map-from-codebase` trước.
Có roadmap: lọc item theo **mọi phần tử** trong `<arg>` (khớp chính xác cột Module hoặc prefix — xem User Input), **gộp lại** thành 1 phạm vi. Ghi lại danh sách RM-ID + tên màn + thực thể/CRUD + phụ thuộc. Không phần tử nào khớp item → báo và dừng. Item có cột Module trống/không đọc được → báo tường minh, KHÔNG im lặng bỏ.
**Chốt số N**: đếm thẳng từ `docs/roadmap.md` số item khớp phạm vi, ghi `N = <số>`. N là mỏ neo cho bước 7 — bước 7 đếm lại từ roadmap, không tin danh sách bước này.
**Phụ thuộc chéo module**: với mỗi RM-ID ở cột Phụ thuộc, tra ngược cột Module của RM-ID đó trong roadmap để biết nó trong hay ngoài phạm vi. Nếu item trong phạm vi phụ thuộc RM thuộc **module khác** (vd Bán thiết bị phụ thuộc Doanh nghiệp), ghi nhận entity module khác đó là **tham chiếu ngoài** (external) — sẽ trỏ FK tới, KHÔNG định nghĩa lại ở doc này (xem bước 4).

### 2. Đọc nguồn, KHÔNG đoán
Rút model từ code thật trong codebase, không bịa. Tự tìm nguồn liên quan tới module (đừng giả định layout — quét thật):
- **Phía client/mockup**: model/type/interface + service của module — field, kiểu, quan hệ ngầm (id tham chiếu), enum, danh sách trạng thái.
- **Phía server (nếu module đã bắt đầu)**: entity/model, DTO, enum, error code, migration/schema — bất kể ngôn ngữ/framework.
- **Nguồn framework hợp lệ** (không chỉ code trong repo): base class / package / module nền tảng mà entity kế thừa hoặc framework cung cấp sẵn (vd lớp cha audit/aggregate, module Identity/permission có sẵn). Nhận diện qua: class kế thừa base của framework, package đã import, cấu hình module. Cite framework/base class làm nguồn = hợp lệ, KHÔNG tính là "bịa" — **với điều kiện nêu đích danh tên class/package + nơi thấy nó** (vd `kế thừa BaseAuditEntity, khai ở src/Domain/Common`). Cite chung chung ("framework Identity có sẵn") KHÔNG hợp lệ, coi như bịa.
- Không tìm được nguồn (kể cả framework) cho một entity → ghi vào mục "Câu hỏi mở", KHÔNG bịa field. Không xác định được vị trí code → hỏi lại, đừng đoán.
- **"Câu hỏi mở" không phải chỗ né việc**: mỗi mục ghi vào đó phải kèm lý do kiểm chứng được ("đã quét `<đường dẫn/pattern>`, không thấy nguồn"). Cấm ghi mục trống lý do.

### 3. Ưu tiên dùng lại đồ framework đã cho
Trước khi định nghĩa entity/field/enum MỚI, kiểm tra framework/nền tảng của codebase **đã cung cấp sẵn** cái đó chưa (vd: user/role/permission/tenant, trường audit, khóa, soft-delete, cây phân cấp…). Có sẵn →
- **Dùng thẳng** nếu đủ.
- **Mở rộng/kế thừa** (thêm field, quan hệ) nếu thiếu — KHÔNG dựng bản song song.
- Ghi rõ trong doc entity nào là "của framework (dùng lại)" vs "của framework + mở rộng" vs "mới hoàn toàn", kèm nguồn.
Chỉ tạo entity mới khi framework KHÔNG có. Bịa lại cái framework đã lo = nợ kỹ thuật, cấm.

### 4. Rút domain (mỏng)
Tổng hợp:
- **Entity** + đánh dấu aggregate root vs entity con.
- **Field chính**: chỉ khóa/định danh/enum/FK + field ảnh hưởng ràng buộc. Bỏ field thuần UI.
- **Quan hệ & FK**: hướng, cardinality (1-N/N-N/1-1), **on-delete** (mặc định Restrict). FK trỏ tới entity **module khác** → đánh dấu **tham chiếu ngoài (external)**, ghi rõ entity đó thuộc `docs/domain/<module-khác>.md`; định nghĩa entity là việc của module sở hữu, doc này CHỈ tham chiếu (không copy field). Module đó chưa có doc → ghi entity external vào "Câu hỏi mở".
- **Enum & error code**.
- **Rule chung** áp nhiều màn (định nghĩa 1 lần).

### 5. Interview chỗ mơ hồ (AskUserQuestion)
Hỏi qua AskUserQuestion, mỗi lượt gom **1–4 câu độc lập nhau** (vd on-delete của các FK khác nhau, aggregate boundary của các cụm entity khác nhau — đáp án câu này không đổi nội dung câu kia); câu phụ thuộc kết quả câu trước → tách lượt sau. Mỗi câu 2–4 option kèm lý do + trade-off; `(Recommended)` CHỈ khi có căn cứ từ code/nguồn bước 2 (nêu căn cứ ngay trong option) — quyết định thiết kế mà code không cho căn cứ thì không đánh Recommended, gợi ý bừa là dẫn người dùng chốt ý của bạn. Chỉ hỏi cái **quyết định model, không suy được từ code**:
- Quan hệ N-N cần bảng nối hay không.
- Aggregate boundary (entity con thuộc root nào).
- On-delete: Restrict vs Cascade vs SetNull khi có tham chiếu.
- Field chung nên nằm ở entity nào (tránh trùng lặp).
Fact tra từ code; **quyết định thiết kế là của người dùng** — đặt từng cái, **chờ phản hồi thật của người dùng**, cấm tự suy "chắc đồng ý". Không chắc một thứ là fact hay quyết định → coi là **quyết định**, phải hỏi. **On-delete — tiêu chí hỏi đếm được**: FK nối **hai aggregate root khác nhau**, HOẶC entity cha xuất hiện trong item roadmap có thao tác Xóa → BẮT BUỘC hỏi, không lặng lẽ lấy mặc định. Chỉ được lấy mặc định Restrict không hỏi cho FK trỏ dữ liệu danh mục thuần (lookup/enum-table), và mọi FK lấy mặc định phải ghi tường minh vào bảng §3 (cột Ghi chú: `mặc định Restrict, chưa hỏi`).

### 6. Ghi `docs/domain/<module>.md` theo khung CỐ ĐỊNH
- Lấy khung: `specify preset resolve domain-template`; không resolve được → đọc `.specify/extensions/dft-speckit/templates/domain-template.md`; vẫn không thấy → hỏi.
- Tên file: prefix chung của danh sách nếu có (vd cả 3 `system/*` → `system`); KHÔNG có prefix chung → hỏi người dùng tên cụm qua AskUserQuestion (đề xuất tên nối `-` làm option Recommended, căn cứ: suy từ tên các module). Chuẩn hóa: lowercase, thay mọi ký tự ngoài `[a-z0-9-]` bằng `-`, gộp `-` liền kề (vd `khdn/devices` → `docs/domain/khdn-devices.md`; `system` → `docs/domain/system.md`). Tạo thư mục `docs/domain/` nếu chưa có.
- **Giữ hợp đồng tra cứu cho `/speckit.specify` và `/speckit.plan`** (chúng tra `docs/domain/<module>.md` rồi mới thử prefix): nếu tên doc gộp KHÔNG suy được từ tên module thành viên theo phép chuẩn hóa trên (trường hợp không có prefix chung), sau khi ghi doc gộp phải ghi thêm cho MỖI module thành viên một file stub `docs/domain/<module>.md` chứa đúng một dòng trỏ sang doc gộp (vd `Domain của module này nằm ở docs/domain/<tên-cụm>.md`) — thiếu stub là specify/plan im lặng chạy không có domain doc.
- **File CHƯA tồn tại** → copy đúng cấu trúc khung, chỉ **điền** placeholder `[…]`, thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **File ĐÃ tồn tại** → **ĐỌC file hiện tại trước**, chỉ chèn/sửa entity tại chỗ; **KHÔNG copy khung đè**. Giữ nguyên mục **"Câu hỏi mở / nợ domain"** và mọi quyết định đã chốt; chỉ bổ sung/sửa entity khi người dùng yêu cầu hoặc specify phát hiện thiếu. Câu hỏi mở cũ nay bước 2 đã tìm được nguồn → gạch khỏi mục đó và điền vào entity (giải nợ, không để tồn đọng).

### 7. Verification (trước khi báo xong)
- **Đếm lại từ `docs/roadmap.md`** (không dùng lại danh sách bước 1): số item khớp phạm vi phải bằng `N`; mọi RM-ID trong N đó xuất hiện ở cột "Dùng ở (RM)" của ít nhất 1 entity. Lệch → phạm vi sót, fail.
- Mọi FK ở mục 3 trỏ tới: entity có thật ở mục 1 (nội bộ), HOẶC entity **external** đã nêu module sở hữu, HOẶC mục "Câu hỏi mở" (module sở hữu chưa có doc). FK có entity đích **nằm trong phạm vi doc này** mà bị đẩy sang "Câu hỏi mở" → fail (phải định nghĩa). FK trỏ vào hư vô → fail.
- Mọi mục trong "Câu hỏi mở" có lý do kiểm chứng được (đã quét đâu, không thấy gì). Mục trống lý do → fail.
- Mục 4 (enum/error code) và mục 5 (rule chung): mỗi dòng truy được về nguồn bước 2 hoặc quyết định người dùng ở bước 5.
- Không còn placeholder `[…]` sót lại trong file.
- Không entity nào field bịa: mọi field truy được về nguồn ở bước 2 — nguồn framework phải nêu **đích danh class/package**, "framework nói chung" → fail — hoặc nằm trong "Câu hỏi mở".

Kết thúc: báo doc đã tạo/cập nhật (danh sách module đã gom, đường dẫn file, số entity, số FK, số câu hỏi mở còn lại), và nhắc:
`/speckit.specify <RM-ID>` — mỗi màn đọc `docs/domain/<module>.md` làm nền model.

## Sai lầm thường gặp
- **Design cả dự án 1 lần** → BDUF, đoán sai. Chỉ làm module sắp tới lượt.
- **Nhồi FR/edge-case màn vào domain doc** → loãng, trùng specify. Domain chỉ model + ràng buộc.
- **Bịa field không có trong mockup/backend** → ghi "Câu hỏi mở", đừng chế.
- **Clobber "Câu hỏi mở"/quyết định cũ khi chạy lại** → mất context. No-clobber mục đó.
- **Quên on-delete** → specify màn xóa vênh nhau. Luôn nêu, mặc định Restrict.
- **Copy entity module khác vào doc này** → 2 nguồn sự thật, vênh. Entity module khác = tham chiếu external, module sở hữu định nghĩa.
- **Đẩy entity framework (Identity/audit) vào "Câu hỏi mở" vì không thấy trong repo** → sai. Base class/package framework là nguồn hợp lệ, đánh dấu "framework (dùng lại)".
