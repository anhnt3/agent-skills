---
description: Lập/cập nhật roadmap build từ codebase hiện có — xếp thứ tự làm từng màn/chức năng, ghi docs/roadmap.md.
---

# Roadmap build từ codebase

Codebase đã có đủ màn/chức năng (mockup, module chưa hoàn thiện, hoặc phần cần làm tiếp). Nhiệm vụ: sinh/cập nhật **`docs/roadmap.md`** xếp **thứ tự làm** từng màn/chức năng. Toàn bộ tiếng Việt. `$ARGUMENTS` (nếu có) là chỉ dẫn thêm (vd chỉ 1 module, hoặc yêu cầu tính lại thứ tự).

## 1. Quét codebase (đọc, không đoán)
Tự tìm & liệt kê **mọi màn/chức năng** liên quan trong codebase (frontend, backend, service, module…). Không tìm ra vị trí → **hỏi lại**, đừng đoán. Mỗi màn/chức năng ghi nhận: tên, module, mô tả ngắn, thực thể/CRUD chính, và **phụ thuộc rõ** (auth, permission, shared entity, chức năng khác).

## 2. Đề xuất thứ tự (wave)
Xếp build theo phụ thuộc:
- **Wave 0 — nền tảng**: auth, permission, shared entity/service phải trước.
- **Wave sau**: chức năng phụ thuộc wave trước.
Trình bày đề xuất kèm **lý do thứ tự** (cái gì chặn cái gì).

## 3. Chốt ưu tiên (interview)
Hỏi qua **AskUserQuestion** — mỗi lần MỘT câu, 2–4 option, `(Recommended)` đầu, kèm lý do + trade-off. Xác nhận/điều chỉnh thứ tự, ưu tiên, gộp/tách. Fact tra từ codebase; **thứ tự là quyết định của người dùng** — đặt từng cái ra, chờ trả lời.

## 4. Ghi `docs/roadmap.md` theo khung CỐ ĐỊNH
**Dùng khung cố định, KHÔNG tự chế cấu trúc** (để mỗi lần sinh ra format giống hệt):
- Lấy khung: chạy `specify preset resolve roadmap-template` để lấy đường dẫn file khung; không resolve được → đọc `templates/roadmap-template.md` trong thư mục extension đã cài; vẫn không thấy → hỏi.
- Copy đúng cấu trúc khung (bảng tổng + khối chi tiết mỗi item), chỉ **điền** placeholder `[…]`, thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **ID ổn định** (`RM-001`, `RM-002`, …) khớp giữa bảng tổng và khối chi tiết — để `/speckit.specify <ID>` lấy được.

**KHÔNG clobber**: nếu `docs/roadmap.md` đã tồn tại, **giữ nguyên** cột `Trạng thái` và mục `Nợ phát sinh` của item cũ; chỉ thêm item mới vào đúng wave / tính lại thứ tự khi người dùng yêu cầu.

Kết thúc: báo số item, thứ tự wave, và nhắc `/speckit.specify <ID>` để bắt đầu từng mục.
