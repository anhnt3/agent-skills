# Preset checklist

Preset = override core command qua `preset.yml`. Review theo hai trục.

## Trục tất định (lint inline)

- [ ] Mọi command khai trong `provides` có file `commands/*.md` tồn tại; mọi file `.md` thực
      có được khai. Không mồ côi.
- [ ] Mỗi command `strategy: wrap` chứa đúng **một** token `{CORE_TEMPLATE}`. `replace` thì
      không có token (thay hẳn).
- [ ] Template `strategy: replace` trỏ file `templates/*.md` tồn tại, swap đúng core template.
- [ ] `id`, `version` hợp lệ; version đã bump nếu chuẩn bị release (README install URL +
      release.sh derive từ version).
- [ ] Bước đánh số trong command liền mạch; tham chiếu "bước N", "GĐx", tên section core trỏ
      đúng chỗ tồn tại.
- [ ] Thuật ngữ/nhãn nhất quán giữa command ↔ README ↔ `preset.yml` (grep chéo). Vd dấu nguồn,
      tên khái niệm phải một tên duy nhất.

## Trục phán đoán (critic)

### Đối chiếu core (dùng speckit-mechanics.md)
- [ ] Preset có **lặp lại** điều `{CORE_TEMPLATE}` đã nói không (validation, clarification,
      branch)? Lặp = thừa, dễ mâu thuẫn khi core đổi.
- [ ] Mỗi luật core bị đè có **vô hiệu hóa tường minh** không, hay chỉ nói chung "preset ghi
      đè"? Lời đè phải **neo vào tên section core** (vd "khi tới Pre-Execution Checks...").
- [ ] **Hook conflict**: nếu preset muốn bỏ/đổi hành vi hook (vd không tạo branch), có nêu rõ
      "kể cả khi core ghi optional:false / MUST invoke vẫn không theo" không? Đây là lỗi kinh
      điển — core "MUST" ở gần điểm hành động thắng lời đè mơ hồ ở xa. (escape-hatch #8)
- [ ] Phần core "For AI Generation / reasonable defaults (don't ask about these)" — nếu preset
      có triết lý hỏi kỹ, đã vô hiệu hóa phần này chưa (kẻo model tự mặc định auth/retention...)?

### Escape-hatch (dùng escape-hatch-catalog.md — lens trung tâm)
- [ ] Đi qua từng gate/quy tắc "bắt buộc", thử 10 mẫu đường thoát. Mẫu nào chưa bịt = finding.
- [ ] Gate có mỏ neo đếm từ nguồn ngoài, hay tự-xác-nhận trên danh sách model tự dựng?
- [ ] Mọi cửa bỏ qua (N/A, trivial, nếu-áp-dụng) buộc lý do kiểm chứng?

### Sonnet-followability
- [ ] Có chỗ nào **2 cách hiểu** dẫn tới hành vi ngược nhau không?
- [ ] Có chỉ thị nào **chọi nhau** không?
- [ ] Chỗ suy luận nặng (phân loại, ranh giới) có **ví dụ cụ thể** hay để model tự chế tiêu chí?

### Generic vs specific
- [ ] Giả định cứng nào (đường dẫn cố định, format roadmap/domain-doc riêng, constitution tồn
      tại)? Liệt kê.
- [ ] Chạy trên dự án **fresh/khác loại** không? Có **fallback** khi thiếu hạ tầng (vd
      constitution thiếu → bộ nhánh mặc định) không?
- [ ] README có tự mâu thuẫn về cái gì bắt buộc vs tùy chọn không?

### Best-practices / bloat
- [ ] Prompt bloat: in lại nguyên bảng nhiều lần, nhắc cùng một luật 3 chỗ, over-specify việc
      model đã biết? Gộp/tham chiếu lại được không?
- [ ] Coupling nội tạng core (neo tên section/wording cứng) → cờ rủi ro upstream đổi.
- [ ] Degrees of freedom: chỗ mơ hồ là **cố ý** (tùy ngữ cảnh) hay **vô tình** (quên định
      nghĩa)? Phân biệt.
