# Preset checklist

Preset = override core command qua `preset.yml`. Review theo hai trục.

## Trục tất định (lint inline)

- [ ] Mọi command khai trong `provides` có file `commands/*.md` tồn tại; mọi file `.md` thực
      có được khai. Không mồ côi.
- [ ] Mỗi command `strategy: wrap` chứa đúng **một** token `{CORE_TEMPLATE}`. `replace` thì
      không có token (thay hẳn). (Cơ chế thật: upstream `str.replace` MỌI occurrence — nhiều token
      = core body bị nhân bản, vẫn là lỗi; thiếu token = hard error lúc cài.)
- [ ] Command wrap khai `strategy: wrap` ở **cả frontmatter file** (không chỉ manifest) + có
      `description` — upstream có code path legacy đọc từ frontmatter, và description là thứ
      hiển thị khi materialize thành skill.
- [ ] **`description` frontmatter phải NGẮN, vừa một dòng (~≤60 ký tự)** — description dài bị
      YAML emitter wrap nhiều dòng khi materialize, và `inject_argument_hint` của spec-kit chèn
      `argument-hint:` ngay sau dòng đầu → **frontmatter SKILL.md gãy YAML** (bug thực nghiệm
      trên 0.12.4). Kiểm bằng cách cài thật rồi parse YAML frontmatter của skill sinh ra.
- [ ] Build-zip của preset tự lọc rác (`.omc/`, `.DS_Store`...) — KHÔNG có `.presetignore`;
      preset bị copy nguyên thư mục lúc cài.
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

### Chi phí người trả lời & độ bền vận hành (BA lens — bắt buộc với command tương tác)

Prompt phỏng vấn/hỏi-đáp thường được viết tối ưu cho model tuân thủ, quên mất hai thứ:
người ngồi trả lời và vòng đời phiên chạy. Đây là lớp lỗi tác giả gần như không tự thấy.

- [ ] **Đếm worst-case số lượt hỏi** của flow (câu/lượt × sàn tối thiểu × số màn/nhánh...).
      Phỏng vấn tuần tự vượt ~15–20 lượt = cờ đỏ *interview fatigue*: từ đó người dùng trả
      lời ẩu, spec "đầy đủ" mà sai. Có gom câu độc lập chung lượt không (AskUserQuestion cho
      phép tới 4 câu/lần — command tự trói xuống 1 là tự gây hại)?
- [ ] **Phân tầng trọng yếu**: mọi quyết định có ngang nhau không (sort mặc định tốn một
      lượt như máy trạng thái nghiệp vụ)? Quyết định low-stakes nên là đề-xuất-kèm-căn-cứ
      rồi duyệt gộp; high-stakes mới đáng một lượt hỏi riêng.
- [ ] **Recommended/anchoring bias**: option gợi ý có buộc căn cứ (từ khảo sát/artifact)
      không? Prompt cấm model đoán nhưng bắt mọi câu phải có `(Recommended)` = mở cửa sau
      cho chính informed-guess — user mệt bấm gợi ý, ý model đội lốt xác nhận user.
- [ ] **Persist trạng thái**: bảng theo dõi/neo đếm/quyết định đã chốt có được ghi ra file
      không, hay chỉ sống trong hội thoại? Flow dài gần như chắc chắn bị compaction — trạng
      thái chỉ trong context là single point of failure. Có luật "đọc lại từ file, cấm dựng
      lại từ trí nhớ" không?
- [ ] **Bàn giao vật lý giữa các lệnh** (specify→plan→tasks): dữ liệu lệnh sau cần kế thừa
      có nơi ghi cụ thể (file/section được nêu tên) không? "Ghi lại để lệnh sau kế thừa" mà
      không nói ghi vào đâu = bay hơi cùng phiên chat.
- [ ] **Xác nhận cuối giai đoạn duyệt cái gì**: recap NỘI DUNG quyết định, hay chỉ bảng
      trạng thái quy trình? Người dùng ký nội dung, không ký tiến độ.
- [ ] **Side-effect trước xác nhận**: command có ghi/sửa file (roadmap, doc, status) trước
      khi người dùng xác nhận phạm vi không? Phiên hủy giữa chừng để lại vết bẩn gì?
- [ ] **Nhánh cho ngoại lệ khuôn**: feature không UI (K=0), repo không roadmap/domain doc,
      dự án fresh — mỗi trường hợp có đường đi hợp lệ không, hay prompt ép nặn ra artifact
      cho có?

### Best-practices / bloat
- [ ] Prompt bloat: in lại nguyên bảng nhiều lần, nhắc cùng một luật 3 chỗ, over-specify việc
      model đã biết? Gộp/tham chiếu lại được không?
- [ ] Coupling nội tạng core (neo tên section/wording cứng) → cờ rủi ro upstream đổi. Neo phải
      kiểm chứng được bằng máy (vd `scripts/check-core-anchors.sh`) và README/CLAUDE.md phải ghi
      "tested with spec-kit <version>".
- [ ] **Snapshot-clobber**: override preset là bản materialize, bị ghi đè khi nâng cấp CLI
      spec-kit / re-init. README preset có document bước re-reconcile sau upgrade
      (`preset disable` → `enable` + `preset resolve` verify) không? Thiếu = finding.
- [ ] Degrees of freedom: chỗ mơ hồ là **cố ý** (tùy ngữ cảnh) hay **vô tình** (quên định
      nghĩa)? Phân biệt.
