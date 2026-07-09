---
name: speckit-addon-reviewer
description: >-
  Review chất lượng một Spec Kit preset hoặc extension (thư mục chứa preset.yml
  hoặc extension.yml, với commands/*.md, templates/*.md, scripts/, references/).
  Kiểm cả hai trục: lint cơ học tất định (manifest khai đủ, token {CORE_TEMPLATE},
  build-zip copy support dir, version bump) VÀ chất lượng prompt để model chạy
  chính xác không bỏ sót (đối chiếu core, hook conflict, săn đường-thoát/escape-hatch,
  vét cạn, ambiguity, generic-vs-specific, Anthropic skill best-practices) VÀ lens BA
  cho command tương tác (chi phí lượt hỏi/fatigue, phân tầng trọng yếu, recommended-bias,
  persist trạng thái, bàn giao vật lý giữa các lệnh, side-effect trước xác nhận).
  DÙNG SKILL NÀY bất cứ khi nào người dùng nói "review preset", "review extension",
  "kiểm speckit addon", "đánh giá command speckit", "spec-kit preset/extension có ổn
  không", hoặc trỏ vào một thư mục có preset.yml/extension.yml và muốn đánh giá —
  kể cả khi họ không gọi thẳng tên skill.
---

# Spec Kit Addon Reviewer

Review một **preset** (override core command của Spec Kit qua `strategy: wrap`/`replace`)
hoặc một **extension** (thêm command/template/script/hook mới). Mục tiêu: bắt lỗi mà
đọc lướt bỏ sót — nhất là lỗi ngữ nghĩa prompt khiến model (đặc biệt Sonnet) chạy sai
hoặc bỏ sót bước, và lỗi đóng gói khiến command gãy âm thầm sau khi cài.

## Vì sao có skill này

Review addon Spec Kit khó ở chỗ: file `.md` là **prompt cho model**, không phải code —
không compiler nào bắt lỗi. Lỗi đắt nhất không phải cú pháp mà là: hai chỉ thị chọi nhau
(preset bảo bỏ hook, core bảo MUST chạy), một "gate" có vẻ chặt nhưng model lách được,
một giả định cứng khiến addon chết trên dự án khác — và một lớp tinh vi hơn: prompt
**tối ưu cho model tuân thủ nhưng quên chi phí con người và độ bền vận hành** (phỏng vấn
40 lượt gây fatigue, trạng thái chỉ sống trong hội thoại chết theo compaction, bàn giao
giữa các lệnh không có nơi ghi vật lý). Song song, có lớp lỗi cơ học tất định
(manifest quên khai, build-zip quên copy `references/`) mà grep bắt được ngay, đừng phí
model cho nó. Skill này tách đúng hai lớp và dồn sức phán đoán vào lớp thực sự cần.

## Bước 0 — Nhận diện artifact

Đọc thư mục mục tiêu:
- Có `preset.yml` → **preset**. Dùng `references/preset-checklist.md`.
- Có `extension.yml` → **extension**. Dùng `references/extension-checklist.md`.
- Có cả hai (repo gộp nhiều addon) → review từng cái theo manifest của nó.

Đọc `references/speckit-mechanics.md` để nắm cơ chế core (tên section, template stack,
hook flow) trước khi phán đoán — nhiều finding chỉ lộ ra khi biết core hoạt động thế nào.

## Bước 1 — Lint trục tất định (INLINE, KHÔNG spawn agent)

Tự chạy grep/read ngay trong main thread. Đây là lỗi đúng-sai rõ, gọi agent là phí.
Theo đúng checklist tương ứng (preset/extension). Nhóm chính:

- **Manifest ↔ file**: mọi `commands/*.md` + `templates/*.md` thực có phải được khai trong
  `provides` của manifest; ngược lại, file khai trong manifest phải tồn tại. File mồ côi =
  finding (manifest không khai → command vô hiệu; file thiếu → cài gãy).
- **Preset**: mỗi command `strategy: wrap` PHẢI chứa token `{CORE_TEMPLATE}` đúng một lần.
  `replace` thì không.
- **Extension**: `build-zip.sh` phải copy mọi thư mục hỗ trợ mà command tham chiếu
  (`references/`, `scripts/`, ...) — bằng `cp -R` hoặc `find -exec cp` đều được, đừng chỉ grep
  `cp -R` kẻo báo nhầm. Manifest `provides` KHÔNG gate cái này — thiếu copy = command gãy sau
  cài dù manifest hợp lệ. Đây là gotcha số 1 của extension.
- **Version**: version trong manifest đã bump chưa (so với tag/README install URL).
- **Đánh số/tham chiếu chéo**: các bước đánh số trong command liền mạch; tham chiếu "bước N",
  "GĐ2", section core... trỏ đúng chỗ tồn tại.
- **Nhất quán thuật ngữ**: cùng một khái niệm dùng một tên xuyên suốt command + README +
  manifest (grep chéo). Lệch tên = nhiễu người đọc.

Ghi mọi finding tất định vào báo cáo (severity theo mức gãy: cài gãy = MAJOR, nhiễu = MINOR).

## Bước 2 — Review trục phán đoán (MULTI-ROUND, có agent)

Đây là phần cần hiểu ngữ nghĩa prompt. Chạy vòng lặp critic có kiểm soát.

**Mỗi vòng:**
1. Spawn **một** agent `critic` (model opus), inject: file addon, `{CORE_TEMPLATE}` nếu là
   preset (đọc từ core Spec Kit tương ứng), checklist tương ứng, và
   `references/escape-hatch-catalog.md` làm lens trung tâm. Yêu cầu critic trả findings có
   severity + verdict (ACCEPT/REVISE/REJECT).
2. Main thread **áp fix tối thiểu** cho các finding CRITICAL/MAJOR (tách vai: author ≠
   reviewer — critic không tự sửa).
3. Sang vòng sau: critic verify bản đã sửa.

**Guardrail dừng (BẮT BUỘC — nếu không sẽ loop đốt token):**
- Cap cứng **tối đa 3 vòng**.
- Dừng sớm khi: verdict = ACCEPT, HOẶC vòng mới không sinh finding MAJOR/CRITICAL mới
  (chỉ còn MINOR → dừng, liệt kê MINOR còn lại, không sửa tiếp nếu người dùng không yêu cầu).
- Không bao giờ để critic tự-áp-fix rồi tự-duyệt trong cùng một lượt.

**Trọng tâm phán đoán** (chi tiết trong escape-hatch-catalog + checklist):
- **Săn đường thoát** (lens trung tâm): với mỗi gate/quy tắc trong prompt, hỏi "model lười/
  nhanh lách kiểu gì?" — N/A khống, bảng tự-dựng-thiếu-dòng, ✅ giả, tự tuyên bố người dùng
  đã xác nhận, informed-guess thứ đáng lẽ phải hỏi.
- **Đối chiếu core** (preset): trùng lặp với `{CORE_TEMPLATE}`; override có tường minh không
  hay mâu thuẫn; **hook conflict** (preset bảo bỏ hook vs core "MUST invoke" — kinh điển);
  luật đè có neo đúng tên section core không.
- **Coupling nội tạng core**: preset/command tham chiếu cứng tên section/wording nào của
  core → rủi ro upstream đổi thì gãy âm thầm. Cờ để version-pin.
- **Sonnet-followability**: ambiguity 2-cách-hiểu, chỉ thị chọi nhau, chỗ suy luận nặng
  không có tiêu chí (vd "fact vs quyết định" mà thiếu ví dụ).
- **Generic vs specific**: giả định cứng (đường dẫn cố định, roadmap/domain-doc format riêng,
  constitution) → addon chạy được trên dự án fresh/khác loại không; có fallback khi thiếu
  hạ tầng không.
- **Anthropic skill best-practices**: concise, thuật ngữ nhất quán, không over-specify,
  prompt bloat (in lại nguyên bảng nhiều lần, nhắc cùng luật 3 lần), degrees-of-freedom hợp lý.
- **Chi phí người trả lời & độ bền vận hành (BA lens — bắt buộc với command tương tác)**:
  đếm worst-case số lượt hỏi (fatigue → trả lời ẩu → spec "đầy đủ" mà sai); quyết định có
  phân tầng trọng yếu hay mọi thứ đều tốn một lượt; option `(Recommended)` có buộc căn cứ
  không (anchoring bias — user mệt bấm gợi ý → ý model đội lốt xác nhận user); trạng thái
  quy trình có persist ra file hay chết theo compaction; bàn giao giữa các lệnh
  (specify→plan→tasks) có nơi ghi VẬT LÝ không; side-effect ghi file trước khi user xác
  nhận; nhánh hợp lệ cho ngoại lệ khuôn (feature không UI, repo không roadmap). Chi tiết:
  section cùng tên trong `preset-checklist.md`.
- **An toàn hook/script** (extension): hook command không nhận input chưa lọc; script không
  eval untrusted; không lộ secret.

## Bước 3 — Báo cáo hợp nhất

Gộp finding cả hai trục + mọi vòng thành MỘT báo cáo, không bắt người dùng đọc từng vòng:

```
# Review: <tên addon> (<preset|extension>)

VERDICT: ACCEPT | REVISE | REJECT   (sau tối đa 3 vòng)

## Đã sửa trong quá trình review
- <finding> → <fix đã áp>

## Còn lại
### CRITICAL / MAJOR
- <file:line> — <mô tả> — <đề xuất fix>
### MINOR
- ...

## Ghi chú
- Giả định cứng / rủi ro coupling / open questions
```

Severity: **CRITICAL** = cài/chạy gãy hoặc bỏ sót âm thầm không ai biết; **MAJOR** = model
dễ làm sai/bỏ bước; **MINOR** = nhiễu, bloat, không nhất quán. Verdict REVISE nếu còn
MAJOR+; ACCEPT nếu chỉ còn MINOR hoặc sạch.

## Reference files

- `references/preset-checklist.md` — checklist đầy đủ cho preset (wrap/replace, đối chiếu core, hook).
- `references/extension-checklist.md` — checklist cho extension (build-zip, hooks, scripts, install path).
- `references/escape-hatch-catalog.md` — **đọc kỹ**: mẫu đường-thoát model hay lách + cách bịt. Lens trung tâm của trục phán đoán.
- `references/speckit-mechanics.md` — cheatsheet cơ chế core Spec Kit: tên section, template resolution stack, hook flow, gotcha đóng gói.
