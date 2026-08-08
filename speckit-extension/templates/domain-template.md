# Domain — [TÊN CỤM]

**Phủ RM**: [RM-xxx, RM-yyy, …] — danh sách chức năng doc này thiết kế model cho.
**Phủ module**: `[module-1]` (đầy đủ / một phần: [RM còn thiếu]), `[module-2]` (…) — dẫn xuất từ cột `Module` của các RM trên.
**Cập nhật**: [DATE]
**Vai trò**: nền model dùng chung — `/speckit.specify <RM-ID>` đọc file này trước để spec từng màn không vênh entity/FK. Doc MỎNG: chỉ model + ràng buộc, KHÔNG FR, KHÔNG edge-case màn (để dành specify).

<!-- Hai dòng trên là KHOÁ ĐỐI CHIẾU, không phải trang trí — /speckit.specify, /speckit.plan và
     domain-design đều tìm doc bằng cách QUÉT NỘI DUNG docs/domain/ (tên file không được dùng để
     suy ra gì cả).
       "Phủ RM"     — khoá khớp CHẮC, đơn vị nhỏ nhất không mơ hồ. Thiếu một RM ở đây = RM đó
                      tìm không ra doc, và lần chạy domain-design sau tưởng nó chưa design.
       "Phủ module" — khoá khớp phụ. Ghi "một phần" khi doc chỉ phủ MỘT SỐ RM của module đó,
                      kèm RM còn thiếu; ghi "đầy đủ" khi chưa đủ là đánh lừa người đọc.
     Sửa phạm vi doc thì phải sửa CẢ HAI dòng. -->

## 1. Thực thể (entity)

| Entity | Aggregate root? | Nguồn gốc | Nguồn (cite) | Mô tả 1 dòng | Dùng ở (RM) |
|--------|-----------------|-----------|--------------|--------------|-------------|
| [Tên] | có / không (thuộc [root]) | BRD / mới / framework (dùng lại) / framework + mở rộng / external ([doc sở hữu]) | [docs/brd/…md#mục / đường dẫn code / tên class-package framework] | [...] | [RM-xxx] |

<!-- Nguồn gốc = BRD -> entity rút từ tài liệu nghiệp vụ, chưa có code hiện thực.
     Cột Nguồn (cite) bắt buộc trỏ đích danh: file BRD + mục, đường dẫn code, hoặc tên
     class/package framework. "framework nói chung" không phải cite hợp lệ. -->

## 2. Field chính mỗi entity

<!-- Chỉ field định danh/khóa/enum/FK + field ảnh hưởng ràng buộc. KHÔNG liệt kê mọi field UI.
     Field lấy từ nguồn KHÁC với cite của entity ở §1 -> ghi `— nguồn: <cite>` cuối dòng. -->

### [Entity]
- `[Id/khóa]` — [kiểu khóa] (khóa chính)
- `[Field]` — [kiểu] — [ràng buộc: required / unique / max / default]
- audit: [có / không — theo convention codebase / chưa xác định (chưa có code)]

## 3. Quan hệ & FK

| Từ | → Tới | Kiểu | On delete | External? | Ghi chú |
|----|-------|------|-----------|-----------|---------|
| [Entity.FkId] | [Entity đích] | 1-N / N-N / 1-1 | Restrict / Cascade / SetNull | không / có ([doc sở hữu]) | [vì sao] |

<!-- Restrict = mặc định (chặn xóa khi còn tham chiếu). Nêu rõ khi khác.
     Chưa hỏi người dùng -> ghi `mặc định Restrict, chưa hỏi`; hết trần lượt hỏi -> `chưa chốt — sửa trực tiếp nếu sai`.
     External = có → entity đích thuộc doc khác; doc này chỉ tham chiếu, KHÔNG định nghĩa lại. Chưa có doc sở hữu → ghi entity vào §6. -->

## 4. Enum & error code

- **[EnumName]**: `A` / `B` / `C` — [nghĩa].
- **Error code**: `[Module]:[Code]` — [khi nào ném].

## 5. Rule chung

<!-- Ràng buộc áp cho nhiều màn — định nghĩa 1 lần ở đây, specify tham chiếu. -->
- [vd: không xóa Catalog khi còn thiết bị liên kết (FK restrict) — FR chi tiết ở RM tương ứng.]

## 6. Câu hỏi mở / nợ domain

<!-- Chỗ chưa chốt; specify lòi ra thì sửa ngược lên đây (living doc, no-clobber mục này).
     MỖI mục mở đầu bằng NHÃN LOẠI để đếm được:
       [không thấy nguồn]  — đã tìm mà không ra nguồn; PHẢI kèm đường dẫn/pattern đã quét. Chỉ loại này tính vào trần 1/3.
       [không sinh entity] — RM không đụng entity nào (dashboard, báo cáo tổng hợp).
       [nợ framework]      — chưa có code nên chưa rà được framework, rà lại khi dựng skeleton.
       [external]          — entity thuộc doc khác, doc sở hữu chưa tồn tại.
       [lệch BRD↔code]     — hai nguồn nói khác nhau, cần người quyết. -->
- (trống)
