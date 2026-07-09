---
description: Lập/cập nhật roadmap build từ codebase hiện có — xếp thứ tự làm từng màn/chức năng, ghi docs/roadmap.md.
---

# Roadmap build từ codebase

Codebase đã có đủ màn/chức năng (mockup, module chưa hoàn thiện, hoặc phần cần làm tiếp). Nhiệm vụ: sinh/cập nhật **`docs/roadmap.md`** xếp **thứ tự làm** từng màn/chức năng. Toàn bộ tiếng Việt. `$ARGUMENTS` (nếu có) là chỉ dẫn thêm (vd chỉ 1 module, hoặc yêu cầu tính lại thứ tự).

## 1. Quét codebase (đọc, không đoán)
Tự tìm & liệt kê **mọi màn/chức năng** liên quan trong codebase (frontend, backend, service, module…). Không tìm ra vị trí → **hỏi lại**, đừng đoán. Mỗi màn/chức năng ghi nhận: tên, module, mô tả ngắn, thực thể/CRUD chính, và **phụ thuộc rõ** (auth, permission, shared entity, chức năng khác).

**Chốt số N**: đếm màn từ nguồn liệt-kê-được (router/menu/thư mục pages/module list), ghi rõ nguồn + `N = <số>`. N là mỏ neo cho bước 5 — không đếm từ trí nhớ. `$ARGUMENTS` giới hạn phạm vi (vd 1 module) → `N` đếm trong phạm vi đó, gate bước 5 cũng tính theo phạm vi đó.

## 2. Đề xuất thứ tự (wave)
Xếp build theo phụ thuộc:
- **Wave 0 — nền tảng**: auth, permission, shared entity/service phải trước.
- **Wave sau**: chức năng phụ thuộc wave trước.
Trình bày đề xuất kèm **lý do thứ tự** (cái gì chặn cái gì).

## 3. Chốt ưu tiên (interview)
Hỏi qua **AskUserQuestion** — mỗi lần MỘT câu, 2–4 option, `(Recommended)` đầu, kèm lý do + trade-off. Xác nhận/điều chỉnh thứ tự, ưu tiên, gộp/tách. Fact tra từ codebase; **thứ tự là quyết định của người dùng** — đặt từng cái ra, chờ **phản hồi thật** của người dùng. Cấm tự tuyên bố người dùng đã đồng ý; chưa có phản hồi thật → dừng, KHÔNG ghi file.

## 4. Ghi `docs/roadmap.md` theo khung CỐ ĐỊNH
**Dùng khung cố định, KHÔNG tự chế cấu trúc** (để mỗi lần sinh ra format giống hệt):
- Lấy khung: chạy `specify preset resolve roadmap-template` để lấy đường dẫn file khung; không resolve được → đọc `.specify/extensions/dft-speckit/templates/roadmap-template.md`; vẫn không thấy → hỏi.
- **File CHƯA tồn tại** → copy đúng cấu trúc khung (bảng tổng + khối chi tiết mỗi item), chỉ **điền** placeholder `[…]`, thay `[DATE]` bằng ngày hiện tại. Giữ nguyên tên cột, thứ tự mục, format.
- **File ĐÃ tồn tại** → **ĐỌC file hiện tại trước**, chỉ chèn/sửa item tại chỗ, **KHÔNG copy khung đè**. Giữ nguyên cột `Trạng thái` và mục `Nợ phát sinh` của mọi item cũ; chỉ thêm item mới vào đúng wave / tính lại thứ tự khi người dùng yêu cầu.
- **ID ổn định** (`RM-001`, `RM-002`, …) khớp giữa bảng tổng và khối chi tiết — để `/speckit.specify <ID>` lấy được. Cấp **tăng dần theo lần thêm**, **KHÔNG bao giờ đánh số lại** khi đổi thứ tự (domain doc và spec cũ trỏ vào ID này). Thứ tự build thể hiện bằng cột `Wave` + vị trí dòng, KHÔNG bằng con số trong ID.

## 5. Kiểm lại (trước khi báo xong)
- Đếm lại từ nguồn ở bước 1: số item trong bảng tổng phải ≥ `N`. Thiếu → quét tiếp, KHÔNG báo xong.
- Mọi ID trong bảng tổng có khối chi tiết tương ứng và ngược lại.
- File cũ: mọi `Trạng thái` ≠ `chưa` và mọi `Nợ phát sinh` cũ còn nguyên.
- Không còn placeholder `[…]` sót lại.

Kết thúc: báo số item, thứ tự wave, và nhắc `/speckit.dft-speckit.domain-design <module>` rồi `/speckit.specify <ID>` để bắt đầu từng mục.
