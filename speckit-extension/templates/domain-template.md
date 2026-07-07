# Domain — [TÊN MODULE]

**Module**: `[module]` (giá trị cột Module trong docs/roadmap.md)
**Cập nhật**: [DATE]
**Phạm vi**: các item roadmap [RM-xxx, RM-yyy, …] thuộc module này.
**Vai trò**: nền model dùng chung — `/speckit.specify <RM-ID>` đọc file này trước để spec từng màn không vênh entity/FK. Doc MỎNG: chỉ model + ràng buộc, KHÔNG FR, KHÔNG edge-case màn (để dành specify).

## 1. Thực thể (entity)

| Entity | Aggregate root? | Nguồn gốc | Mô tả 1 dòng | Dùng ở (RM) |
|--------|-----------------|-----------|--------------|-------------|
| [Tên] | có / không (thuộc [root]) | mới / framework (dùng lại) / framework + mở rộng / external ([module khác]) | [...] | [RM-xxx] |

## 2. Field chính mỗi entity

<!-- Chỉ field định danh/khóa/enum/FK + field ảnh hưởng ràng buộc. KHÔNG liệt kê mọi field UI. -->

### [Entity]
- `[Id/khóa]` — [kiểu khóa] (khóa chính)
- `[Field]` — [kiểu] — [ràng buộc: required / unique / max / default]
- audit: [có / không — theo convention codebase]

## 3. Quan hệ & FK

| Từ | → Tới | Kiểu | On delete | External? | Ghi chú |
|----|-------|------|-----------|-----------|---------|
| [Entity.FkId] | [Entity đích] | 1-N / N-N / 1-1 | Restrict / Cascade / SetNull | không / có ([module sở hữu]) | [vì sao] |

<!-- Restrict = mặc định (chặn xóa khi còn tham chiếu). Nêu rõ khi khác.
     External = có → entity đích thuộc docs/domain/<module-khác>.md; doc này chỉ tham chiếu, KHÔNG định nghĩa lại. Module đó chưa có doc → ghi entity vào §6 Câu hỏi mở. -->

## 4. Enum & error code

- **[EnumName]**: `A` / `B` / `C` — [nghĩa].
- **Error code**: `[Module]:[Code]` — [khi nào ném].

## 5. Rule chung module

<!-- Ràng buộc áp cho nhiều màn — định nghĩa 1 lần ở đây, specify tham chiếu. -->
- [vd: không xóa Catalog khi còn thiết bị liên kết (FK restrict) — FR chi tiết ở RM tương ứng.]

## 6. Câu hỏi mở / nợ domain

<!-- Chỗ chưa chốt; specify lòi ra thì sửa ngược lên đây (living doc, no-clobber mục này). -->
- (trống)
