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
- **Prefix** (vd `system` hoặc `system/*`) → mọi module bắt đầu bằng prefix. Tương đương liệt kê tay các module con.

Gộp mọi item của mọi phần tử = phạm vi domain của **1 doc**.

- **Tên file**: nếu mọi phần tử chung 1 prefix → dùng prefix (vd cả 3 `system/*` → `docs/domain/system.md`). Không chung prefix → hỏi người dùng đặt tên cụm (AskUserQuestion), hoặc nối bằng `-`.
- Trống → đọc roadmap, **liệt kê các module** kèm số item, gợi ý cụm nên gom (prefix/phụ thuộc chung), hỏi người dùng chọn (AskUserQuestion) — cho chọn nhiều gom 1 doc.
- Phần tử nào không khớp → liệt kê module có thật, hỏi lại. **Đừng đoán.**

## Quy trình (bắt buộc theo thứ tự)

**Danh sách nhiều phần tử**: gộp mọi item của mọi phần tử thành **1 phạm vi**, chạy bước 1→7 **một lần** ra **1 doc chung**. Quan hệ giữa các module trong danh sách = nội bộ (cùng doc). External chỉ khi trỏ tới module NGOÀI danh sách.

### 1. Chốt phạm vi từ roadmap
`docs/roadmap.md` KHÔNG tồn tại → **dừng**, nhắc chạy `/speckit.dft-speckit.road-map-from-codebase` trước.
Có roadmap: lọc item theo **mọi phần tử** trong `<arg>` (khớp chính xác cột Module hoặc prefix — xem User Input), **gộp lại** thành 1 phạm vi. Ghi lại danh sách RM-ID + tên màn + thực thể/CRUD + phụ thuộc. Không phần tử nào khớp item → báo và dừng.
**Phụ thuộc chéo module**: nếu item trong phạm vi phụ thuộc RM thuộc **module khác** (vd Bán thiết bị phụ thuộc Doanh nghiệp), ghi nhận entity module khác đó là **tham chiếu ngoài** (external) — sẽ trỏ FK tới, KHÔNG định nghĩa lại ở doc này (xem bước 4).

### 2. Đọc nguồn, KHÔNG đoán
Rút model từ code thật trong codebase, không bịa. Tự tìm nguồn liên quan tới module (đừng giả định layout — quét thật):
- **Phía client/mockup**: model/type/interface + service của module — field, kiểu, quan hệ ngầm (id tham chiếu), enum, danh sách trạng thái.
- **Phía server (nếu module đã bắt đầu)**: entity/model, DTO, enum, error code, migration/schema — bất kể ngôn ngữ/framework.
- **Nguồn framework hợp lệ** (không chỉ code trong repo): base class / package / module nền tảng mà entity kế thừa hoặc framework cung cấp sẵn (vd lớp cha audit/aggregate, module Identity/permission có sẵn). Nhận diện qua: class kế thừa base của framework, package đã import, cấu hình module. Cite framework/base class làm nguồn = hợp lệ, KHÔNG tính là "bịa" — miễn không chế field không có thật.
- Không tìm được nguồn (kể cả framework) cho một entity → ghi vào mục "Câu hỏi mở", KHÔNG bịa field. Không xác định được vị trí code → hỏi lại, đừng đoán.

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
Hỏi **mỗi lần MỘT câu**, 2–4 option, `(Recommended)` đầu kèm lý do + trade-off. Chỉ hỏi cái **quyết định model, không suy được từ code**:
- Quan hệ N-N cần bảng nối hay không.
- Aggregate boundary (entity con thuộc root nào).
- On-delete: Restrict vs Cascade vs SetNull khi có tham chiếu.
- Field chung nên nằm ở entity nào (tránh trùng lặp).
Fact tra từ code; **quyết định thiết kế là của người dùng** — đặt từng cái, chờ trả lời.

### 6. Ghi `docs/domain/<module>.md` theo khung CỐ ĐỊNH
- Lấy khung: `specify preset resolve domain-template`; không resolve được → đọc `templates/domain-template.md` trong extension đã cài; vẫn không thấy → hỏi.
- Tên file: prefix chung của danh sách nếu có (vd cả 3 `system/*` → `system`), không thì tên cụm người dùng đặt / nối `-`. Chuẩn hóa: lowercase, thay mọi ký tự ngoài `[a-z0-9-]` bằng `-`, gộp `-` liền kề (vd `khdn/devices` → `docs/domain/khdn-devices.md`; `system` → `docs/domain/system.md`). Tạo thư mục `docs/domain/` nếu chưa có.
- Copy đúng cấu trúc khung, chỉ **điền** placeholder `[…]`, thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **KHÔNG clobber**: nếu file đã tồn tại, giữ nguyên mục **"Câu hỏi mở / nợ domain"** và mọi quyết định đã chốt; chỉ bổ sung/sửa entity khi người dùng yêu cầu hoặc specify phát hiện thiếu.

### 7. Verification (trước khi báo xong)
- Mọi RM-ID của module xuất hiện ở cột "Dùng ở (RM)" của ít nhất 1 entity (không entity nào → cảnh báo phạm vi sót).
- Mọi FK ở mục 3 trỏ tới: entity có thật ở mục 1 (nội bộ), HOẶC entity **external** đã nêu module sở hữu, HOẶC mục "Câu hỏi mở" (module sở hữu chưa có doc). FK trỏ vào hư vô → fail.
- Không còn placeholder `[…]` sót lại trong file.
- Không entity nào field bịa (mọi field truy được về nguồn ở bước 2, hoặc nằm trong "Câu hỏi mở").

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
