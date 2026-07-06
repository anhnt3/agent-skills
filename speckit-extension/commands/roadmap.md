---
description: Lập/cập nhật roadmap build từ frontend mockup — xếp thứ tự wire backend từng màn/chức năng, ghi docs/roadmap.md.
---

# Roadmap build từ mock

Frontend mockup đã có đủ màn/chức năng. Nhiệm vụ: sinh/cập nhật **`docs/roadmap.md`** xếp **thứ tự wire backend** từng màn. Toàn bộ tiếng Việt. `$ARGUMENTS` (nếu có) là chỉ dẫn thêm (vd chỉ 1 module, hoặc yêu cầu tính lại thứ tự).

## 1. Quét mock (đọc, không đoán)
Tự tìm & liệt kê **mọi màn/chức năng** trong frontend mockup (component + mock-service). Không tìm ra vị trí mock → **hỏi lại**, đừng đoán. Mỗi màn ghi nhận: tên, module, mô tả ngắn, thực thể/CRUD chính, và **phụ thuộc rõ** (auth, permission, shared entity, màn khác).

## 2. Đề xuất thứ tự (wave)
Xếp build theo phụ thuộc:
- **Wave 0 — nền tảng**: auth, permission, shared entity/service phải trước.
- **Wave sau**: chức năng phụ thuộc wave trước.
Trình bày đề xuất kèm **lý do thứ tự** (cái gì chặn cái gì).

## 3. Chốt ưu tiên (interview)
Hỏi qua **AskUserQuestion** — mỗi lần MỘT câu, 2–4 option, `(Recommended)` đầu, kèm lý do + trade-off. Xác nhận/điều chỉnh thứ tự, ưu tiên, gộp/tách. Fact tra từ mock; **thứ tự là quyết định của người dùng** — đặt từng cái ra, chờ trả lời.

## 4. Ghi `docs/roadmap.md`
**KHÔNG clobber**: nếu file đã tồn tại, **giữ nguyên** cột `Trạng thái` và mục `Nợ phát sinh` của các item cũ; chỉ cập nhật thứ tự/nội dung khi người dùng yêu cầu. Item mới thêm vào đúng wave.

Mỗi item có **ID ổn định** (vd `RM-001` hoặc `<module>-<slug>`) để `/speckit.specify <ID>` lấy được.

Cấu trúc file:
- **Bảng tổng** (thứ tự build): `ID | Màn | Module | Wave | Phụ thuộc | Trạng thái`.
  - Trạng thái: `chưa` (mặc định) / `đang` / `xong`.
- **Chi tiết mỗi item** (khối riêng theo ID):
  ```
  ### RM-001 — <Tên màn> (<module>, Wave <n>)
  - Mô tả: <ngắn>
  - Thực thể/CRUD: <...>
  - Phụ thuộc: <ID khác / auth / permission / N/A>
  - Trạng thái: chưa
  - Nợ phát sinh:
    - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)
  ```

Kết thúc: báo số item, thứ tự wave, và nhắc `/speckit.specify <ID>` để bắt đầu từng mục.
