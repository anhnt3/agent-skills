# Roadmap Build — [TÊN DỰ ÁN]

**Mục tiêu**: thứ tự build/hoàn thiện từng màn/chức năng.
**Cập nhật**: [DATE]
**Trạng thái item**: `chưa` (mặc định) / `đang` / `xong`.

## Bảng tổng (thứ tự build)

<!-- Ô ID là link tới nguồn của item. Link markdown resolve TƯƠNG ĐỐI VỚI FILE NÀY,
     còn trường **Nguồn** ở khối chi tiết viết tương đối GỐC REPO — hai hệ quy chiếu
     khác nhau. Roadmap ở docs/roadmap.md, nguồn ở docs/brd/x.md => link là brd/x.md
     (viết docs/brd/x.md sẽ ra docs/docs/brd/x.md, bấm vào 404). Nguồn là code ở
     src/app/y/ => link là ../src/app/y/. Nguồn = N/A => để ID text trần. -->

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
| [RM-001](brd/…md#heading) | [Tên màn] | [module] | 0 | [ID khác / auth / N/A] | chưa |
| [RM-002](brd/…md#heading) | [Tên màn] | [module] | 1 | [RM-001 / …] | chưa |

## Chi tiết

<!-- Mỗi item một khối. ID khớp bảng tổng. Giữ nguyên khối cũ khi cập nhật (không clobber Trạng thái + Nợ phát sinh). -->

### RM-001 — [Tên màn] ([module], Wave 0)

- **Mô tả**: [ngắn gọn chức năng làm gì]
- **Nguồn**: [docs/brd/…md#heading / đường dẫn code / N/A]
- **Thực thể/CRUD**: [entity chính + thao tác]
- **Phụ thuộc**: [ID khác / auth / permission / N/A]
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-002 — [Tên màn] ([module], Wave 1)

- **Mô tả**: [...]
- **Nguồn**: [docs/brd/…md#heading / đường dẫn code / N/A]
- **Thực thể/CRUD**: [...]
- **Phụ thuộc**: [RM-001 / …]
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống)
