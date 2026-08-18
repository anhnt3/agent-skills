# Code intel — [TÊN UNIT]

**Cập nhật**: [DATE]
**Phủ chức năng**: [FN-001, FN-002, …]

<!-- TÀI LIỆU NỘI BỘ. Không giao khách — chỗ giao khách là srs.md cùng thư mục.
     Mỗi khẳng định ở §2–§7 VÀ §9 thuộc một trong ba dạng:
       - Đọc thẳng từ code   → ghi bình thường, kèm `đường/dẫn.ext:dòng`
       - Suy ra, chưa chắc   → ghi kèm nguồn gần nhất và đánh dấu (suy đoán)
       - Không căn cứ nào    → KHÔNG viết ở §2–§7, §9; đưa xuống §8 thành câu hỏi
     Mục không áp dụng cho unit này (đã kiểm tra, thật sự không có) → ghi "Không có",
     giữ tiêu đề. Luôn rút đủ sâu (không có mức nông/sâu để chọn). -->

## 1. Phủ chức năng

| FN-ID | Tên chức năng | Tìm thấy ở đâu | Ghi chú |
| --- | --- | --- | --- |
| [FN-001] | [tên] | [đường/dẫn hoặc "không tìm thấy"] | [—] |

<!-- Danh sách FN-ID lấy nguyên từ `intel_tree.py units` — không tự gõ tay,
     không tự bớt/thêm. FN không tìm thấy code phải ghi rõ "không tìm thấy" —
     im lặng bỏ qua là cách tài liệu bàn giao thiếu chức năng mà không ai biết. -->

## 2. Màn hình / điểm vào

| Màn hình / endpoint | Đường dẫn ứng dụng | Nguồn | FN liên quan |
| --- | --- | --- | --- |
| [tên] | [/route] | [file:dòng] | [FN-001] |

## 3. Thực thể và trường dữ liệu

<!-- Hình dạng mục này mượn từ templates/domain-template.md §1–§2 để code-intel
     và domain-design không mô tả entity theo hai kiểu khác nhau. Khác domain-
     template ở chỗ: đây là NƠI SUY, không phải nơi thiết kế — mọi dòng phải
     trỏ nguồn đọc được, không có cột "Nguồn gốc: BRD / mới". -->

### [TênThựcThể]

- **Nguồn**: [file:dòng]
- **Khoá chính**: [trường]
- **Quan hệ**: [FK → thực thể khác, kiểu 1-N/N-N/1-1]

| Trường | Kiểu | Bắt buộc | Ràng buộc | Mặc định | Nguồn |
| --- | --- | --- | --- | --- | --- |
| [tên] | [kiểu] | [Có/Không] | [độ dài, miền giá trị, duy nhất] | [—] | [file:dòng] |

## 4. Kiểm tra hợp lệ và quy tắc nghiệp vụ

| # | Quy tắc | Nguồn | Độ chắc chắn |
| --- | --- | --- | --- |
| 1 | [điều kiện → hệ quả] | [file:dòng] | [chắc / suy đoán] |

<!-- Cột "Độ chắc chắn" ghi lại mức tự tin nội bộ khi rút quy tắc. Khuôn srs.md hiện tại
     (đợt 3B-3, cấu trúc 4 cấp mô phỏng docx thật) không còn N.4/N.5 riêng — mọi quy tắc
     (kể cả đánh dấu "suy đoán") rót chung vào mục `g. Yêu cầu nghiệp vụ`, không đánh dấu
     lại mức tự tin trong tài liệu giao khách (xem srs-from-code.md bước 6). Cột này vẫn
     hữu ích cho người soát tay đọc trực tiếp intel.md. -->

## 5. Luồng nghiệp vụ

### [Tên luồng]

[Trình tự các bước, nêu rõ thành phần nào xử lý bước nào.]

- **Nguồn**: [file:dòng, file:dòng]

## 6. Phân quyền

| Vai trò | Chức năng / hành động | Điều kiện | Nguồn |
| --- | --- | --- | --- |
| [vai trò] | [hành động] | [điều kiện dữ liệu] | [file:dòng] |

## 7. Tích hợp ngoài, tác vụ nền, sự kiện

| Loại | Mô tả | Kích hoạt khi | Nguồn |
| --- | --- | --- | --- |
| [dịch vụ ngoài / job / event] | [làm gì] | [điều kiện] | [file:dòng] |

## 8. Không suy được từ code — câu hỏi cho người

<!-- Câu đã được trả lời thì ghi câu trả lời ngay dưới, GIỮ NGUYÊN, đừng xoá —
     lần chạy lại sau sẽ không hỏi lại (living doc, no-clobber mục này, giống
     §6 của domain-template).
     MỖI mục mở đầu bằng NHÃN LOẠI để đếm được (dùng đúng một trong bốn):
       [không suy được từ code]   — đã tìm mà không ra căn cứ. Loại DUY NHẤT tính vào trần.
       [chính sách nghiệp vụ]     — quyết định chỉ người mới biết, không phải thứ
                                    code có thể tiết lộ dù tìm kỹ tới đâu (kể cả
                                    ca FN không sinh màn hình nào, không có gì để
                                    ghi ở §7).
       [FN không tìm thấy]        — FN đã kết luận không tìm thấy code ở §1.
       [chờ trả lời từ lần trước] — câu hỏi mang sang từ lần chạy trước.
     Thiếu nhãn = mặc định tính là [không suy được từ code] (an toàn: bị đếm
     trần chứ không lọt lưới). Nhãn giữ nguyên dấu ngoặc vuông vĩnh viễn — đây
     là ký hiệu phân loại cố định, KHÔNG phải chỗ điền nội dung rồi xoá đi.

     Câu chưa có trả lời ghi "— **Trả lời**: _(chưa có)_" — dùng gạch dưới in
     nghiêng, KHÔNG dùng ngoặc vuông kiểu "[để trống...]": intel_verify.py coi
     mọi cặp ngoặc vuông còn sót là placeholder chưa điền và chặn báo xong;
     dùng ngoặc vuông ở đây sẽ khiến một tài liệu hợp lệ (đang có câu hỏi mở)
     không bao giờ qua được cổng. -->

1. [nhãn] [Câu hỏi] — **Trả lời**: _(chưa có)_

## 9. Thông báo hiển thị

| Ngữ cảnh | Nguyên văn thông báo | Nguồn |
| --- | --- | --- |
| [tình huống] | "[nguyên văn]" | [file:dòng] |

<!-- Lấy từ file ngôn ngữ / hằng số / mã lỗi. Nguồn cho mục `g. Yêu cầu nghiệp vụ` của
     srs.md khi mô tả hành vi/thông báo hệ thống — chép nguyên văn, không diễn đạt lại. -->

## 10. Phát hiện cần người quyết định — logic mâu thuẫn / lỗ hổng bảo mật

| # | Loại | Mô tả | Nguồn | Kết luận |
| --- | --- | --- | --- | --- |
| 1 | [logic mâu thuẫn / lỗ hổng bảo mật] | [mô tả cụ thể: mâu thuẫn với chỗ nào, hoặc rủi ro gì] | [file:dòng, file:dòng] | đang chờ |

<!-- KHÁC HẲN §8: đây không phải "không biết", mà là "đã thấy và thấy có vấn đề".
     Chỉ ghi phát hiện THẤY ĐƯỢC trong lúc rút §2–§7 — KHÔNG chủ động mở rộng phạm vi
     quét để tìm lỗ hổng bảo mật một cách hệ thống, đó là việc của security review
     riêng, không phải mục tiêu của command này.
     Mỗi mục PHẢI kèm file:dòng và mô tả CỤ THỂ vì sao đáng ngờ — "trông không an
     toàn" hay "có vẻ sai" không đủ; phải nói rõ mâu thuẫn với dòng/quy tắc nào, hoặc
     lỗ hổng cụ thể là gì (vd "không kiểm quyền sở hữu record trước khi cho sửa",
     "mật khẩu so sánh dạng plaintext"). Không có phát hiện nào → ghi "Không có" (thay
     hẳn bảng, không để lại dòng mẫu).

     RANH GIỚI VỚI §8: mâu thuẫn/thiếu sót THẤY ĐƯỢC trong code → §10, không hạ cấp
     thành câu hỏi §8 kiểu "chính sách có cho phép..." để né việc. Thứ code hoàn toàn
     không mâu thuẫn, chỉ đơn giản không biết (vd "ngưỡng duyệt bao nhiêu tiền thì cần
     cấp trên ký") → §8. Không chắc thuộc loại nào → coi là §10.

     Cột `Kết luận`: giá trị "đang chờ" (không ngoặc vuông) mặc định khi mới ghi.
     srs-from-code đọc mục này để hỏi người dùng "cố ý hay là bug", rồi ghi kết luận
     NGƯỢC lại đúng dòng này — "cố ý — <ghi chú>" hoặc "bug — <ghi chú>". Đây là CỘT
     DUY NHẤT được phép cập nhật trên một dòng đã có (chỉ srs-from-code được ghi;
     code-intel không bao giờ tự sửa cột này); mô tả/nguồn của dòng thì không đổi.

     No-clobber khi chạy lại: chỉ được THÊM phát hiện mới; phát hiện cũ (#/Loại/Mô
     tả/Nguồn) giữ nguyên dù thấy nó nhỏ hay đã hết quan trọng — cột Kết luận là
     ngoại lệ duy nhất (và chỉ srs-from-code được sửa nó). Đây là nơi srs-from-code
     lấy để tổng kết hỏi người dùng, không rót vào srs.md (tài liệu giao khách không
     nêu phát hiện kiểu này). -->

## 11. Điều khiển giao diện

| Màn hình | Tên điều khiển | Loại | Mô tả | Nguồn |
| --- | --- | --- | --- | --- |
| [tên màn hình đúng như §2] | [nhãn hiển thị] | [Textbox/Button/…] | [hành vi, ràng buộc] | [file:dòng] |

<!-- Cột `Màn hình` PHẢI khớp nguyên văn cột "Màn hình / endpoint" của §2 — đây là khoá
     liên kết duy nhất giữa hai mục, dùng bởi srs-from-code (đợt sau) để lọc ra bảng điều
     khiển cho từng màn hình. Sai một ký tự là mất liên kết.

     Cột `Loại` dùng lại đúng bộ từ vựng "Loại trường điều khiển" cố định: Textbox,
     Passwordbox, Checkbox, Dropdown, Datepicker, Button, Link, Label (chỉ xem) — không
     đặt bộ mới. Loại thật không nằm trong danh sách đó thì ghi tên loại đó nguyên văn.

     Màn hình/điểm vào ở §2 thật sự không có giao diện (endpoint REST thuần, job nền,
     CLI, message consumer) → ghi ĐÚNG MỘT dòng với Loại = không-có-UI, cột Mô tả nêu rõ
     lý do cụ thể (loại điểm vào là gì), kèm cite. Đây là giải trình có căn cứ, không
     phải ô trống — cùng tinh thần với nhãn [chính sách nghiệp vụ] ở §8.

     Giữ nguyên kỷ luật ba dạng đang áp cho §2–§7, §9 — không nới riêng cho §11: đọc
     thẳng từ khai báo control → ghi bình thường kèm cite; suy đoán → đánh dấu (suy
     đoán); không có căn cứ → không ghi, đưa xuống §8. -->

## 12. Kịch bản Use Case

<!-- Khuôn dưới đây mô tả ĐƯỜNG B (leaf không có `use_cases[]` trong `functions.json`) —
     mọi quy tắc "luôn ghi cố định", "PHẢI khớp nguyên văn cột Màn hình", "không căn cứ →
     không ghi/lược cả use case, đưa xuống §8" trong khuôn này CHỈ áp cho đường B. Leaf CÓ
     `use_cases[]` đi theo ĐƯỜNG A — xem `commands/code-intel.md` bước 5 phần "A. Leaf có
     use_cases[]": khung `S-n` cố định theo `use_cases[]`, ba field phân loại có thể mang
     giá trị thật từ Excel, "không tìm thấy" ghi thẳng "Chưa tìm thấy hiện thực trong mã
     nguồn." tại field thay vì lược/xuống §8, và mỗi khối đường A luôn kèm comment
     `<!-- use-case-id: ... -->` (xem dòng mẫu dưới `### [Tên Use Case]`) làm khoá liên
     kết cho `srs-from-code` — Field `Màn hình` không dùng được làm khoá cho khối "không
     tìm thấy" vì nó mang câu "Chưa tìm thấy hiện thực..." thay vì tên màn hình thật. -->

### [Tên Use Case]

<!-- use-case-id: [FN-ID-UC-nn nếu khối này dựng từ use_cases[] (đường A); bỏ hẳn dòng
     comment này nếu khối tự khám phá từ code (đường B) — xem code-intel.md bước 5 -->

- **Màn hình**: [tên màn hình đúng như §2]
- **Mức quan trọng**: Chưa có thông tin
- **Người dùng**: [vai trò, từ §6 hoặc suy từ §2]
- **Loại UC**: Chưa có thông tin
- **Người sử dụng và yêu cầu**: [câu tóm tắt mục đích sử dụng]
- **Mô tả tóm tắt**: [đoạn văn tóm lược toàn luồng]
- **Thời điểm sử dụng**: Chưa có thông tin

**Luồng sự kiện chuẩn**:
1. [bước] — [file:dòng]
2. [bước] — [file:dòng]

**Luồng sự kiện nhỏ**:
- S-1: [tên nhánh] — [file:dòng]
  1. [bước]
  2. [bước]

<!-- Field `Màn hình` PHẢI khớp nguyên văn cột "Màn hình / endpoint" của §2 — cùng khoá
     liên kết §11 đã dùng, dùng bởi một đợt sau để nối use case với màn hình. Sai một ký
     tự là mất liên kết.

     Giữ nguyên cả 9 field theo đúng tên/thứ tự của tài liệu ban hành, không lược bớt.
     Ba field `Mức quan trọng`, `Loại UC`, `Thời điểm sử dụng` là phân loại nghiệp vụ
     thuần — không có căn cứ code nào trả lời được dù tìm kỹ tới đâu. Đây KHÔNG phải
     "chưa tìm ra" (không đưa xuống §8), mà là "cấu trúc không thể tìm ra" — luôn ghi cố
     định "Chưa có thông tin" ngay tại đây. Đưa ba field này xuống §8 sẽ cộng thêm 3 mục
     "vô nghĩa" cho MỖI use case vào trần câu hỏi (`check_section8_cap`), dễ đẩy unit
     nhiều use case vượt trần chỉ vì ba field không bao giờ trả lời được.

     Các field còn lại (`Người dùng`, `Người sử dụng và yêu cầu`, `Mô tả tóm tắt`,
     `Luồng sự kiện chuẩn`, `Luồng sự kiện nhỏ`) áp đúng kỷ luật ba dạng đang dùng cho
     §2–§7, §9, §11: đọc thẳng → ghi kèm cite; suy đoán → đánh dấu (suy đoán); không căn
     cứ → không ghi field đó (hoặc lược cả use case nếu không còn gì để viết), đưa câu
     hỏi xuống §8 với nhãn [không suy được từ code].

     KHÔNG quét code lần hai để rút mục này — tái dùng đúng bằng chứng đã thu ở §2 (tên
     màn hình), §5 (luồng nghiệp vụ, viết lại theo khuôn đánh số/nhánh S-n của Use Case),
     và §6 (vai trò phân quyền) nếu có dòng khớp màn hình này. §5 không có luồng nào ứng
     với màn hình này → không viết được `Luồng sự kiện chuẩn` có căn cứ, đưa xuống §8. -->
