# Hiến chương Spec Kit: thế nào là tốt, và vì sao

> Nghiên cứu ngày 2026-07-09. Đối chiếu ba nguồn: source code `github/spec-kit` (clone, chạy thử thật),
> corpus hiến chương thật trên GitHub, và tài liệu học thuật/cộng đồng.
> Mọi con số chịu lực trong tài liệu này đều đã được kiểm chứng độc lập; chỗ nào không kiểm được đều ghi rõ.

## TL;DR

Một hiến chương tốt **không phải văn bản hay**, mà là **văn bản mà `/speckit.analyze` bốc ra được thành rule set**.
Sáu thuộc tính, xếp theo mức chịu lực:

1. Mỗi nguyên tắc **kiểm được** (phát biểu ra được phép thử đạt/không-đạt).
2. Dùng **`MUST` / `MUST NOT`** dứt khoát, bỏ `should` trần.
3. **Ngắn**: ~5 nguyên tắc, ~600–1500 từ.
4. Mỗi nguyên tắc có **Rationale**.
5. Nguyên tắc là **giá trị**, không phải lựa chọn công nghệ.
6. Mục **Điều hành tự đấu dây** vào cổng kiểm mà nó cưỡng chế.

---

## 1. Cơ chế: vì sao hiến chương có hiệu lực hay không

Đây là nền của mọi tiêu chí bên dưới. `analyze` và `converge` **không đọc hiểu** hiến chương.
Chúng làm đúng một việc — `templates/commands/analyze.md:113`:

> "**Constitution rule set**: Extract principle names and MUST/SHOULD normative statements"

Rồi `analyze.md:157` và `:249`: vi phạm một MUST là **CRITICAL tự động**, và `analyze.md:60`:

> "Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks —
> not dilution, reinterpretation, or silent ignoring of the principle."

**Hệ quả trực tiếp: một nguyên tắc không chứa từ chuẩn tắc là một nguyên tắc vô hình.**
Nó tốn token nhưng không chặn được gì.

### Ai tiêu thụ hiến chương, và tiêu thụ thế nào

Có hai tầng, khác nhau về bản chất — đây là chỗ rất dễ nhầm:

| Lệnh | Đọc gì | Làm gì với hiến chương |
|---|---|---|
| `analyze` | **chỉ** `spec.md`, `plan.md`, `tasks.md` | Bốc rule set, đối chiếu **artifact**. **Không đọc code.** |
| `converge` | codebase + spec/plan/tasks | *"**Code** that violates a MUST principle is the highest-severity finding and produces a corresponding remediation task"* (`converge.md:86`) |
| `plan` | spec + hiến chương | Điền cổng `## Constitution Check`; `plan.md:164` *"ERROR on gate failures"* |
| `specify`, `tasks`, `clarify`, `checklist`, `implement`, `taskstoissues` | — | Chỉ nạp làm ngữ cảnh nền (`IF EXISTS`), không phân tích cấu trúc |

Tổng cộng **9 lệnh tiêu thụ** hiến chương (`constitution` là bên ghi, không tính).

Chỉ **`converge`** đối chiếu hiến chương với **code thật**. `analyze` đối chiếu với **tài liệu**.

### Không có gì cưỡng chế bằng code

Không một test nào trong `tests/` kiểm định dạng hiến chương — không kiểm số nguyên tắc, không kiểm
`MUST`, không kiểm dòng version, không kiểm placeholder. Toàn bộ "hợp đồng chất lượng" chỉ được
cưỡng chế **bằng prompt**. Điều này áp cho mọi thứ trong hiến chương, kể cả các điều khoản miễn trừ:
chúng hiệu lực **chỉ vì** cả file được nạp vào ngữ cảnh và mô hình đọc thấy.

---

## 2. Sáu thuộc tính của hiến chương tốt

### 2.1. Kiểm được (falsifiable) — trục chất lượng thật

Phép thử: *một người review hoặc một công cụ có ra được phán quyết đạt/không-đạt mà không cần
phán đoán chủ quan không?*

Lệnh core yêu cầu thẳng (`templates/commands/constitution.md:99`):

> "Principles are declarative, testable, and free of vague language ('should' → replace with MUST/SHOULD rationale where appropriate)."

**Tốt nhất trong corpus** — `DirectedEdges/specs`, nguyên tắc I:

> "Every type in `types/` has a corresponding definition in `schema/component.schema.json`...
> Changes to one MUST be reflected in the other before publishing. Neither artifact may drift
> ahead of the other. **Misalignment is a bug.**"

Máy kiểm được: liệt kê type, liệt kê schema, diff. Nó còn **đặt tên cho trạng thái hỏng**.

**Tệ nhất** — `RobAWilkinson/jazzgym`, nguyên tắc III:

> "Code quality, readability, and maintainability are non-negotiable… **Use judgment**: trivial
> changes, one-liners, and simple fixes may not require tests"

Vừa tuyên bố bất khả xâm phạm, vừa phát giấy phép tuỳ nghi. Không agent nào phán quyết được.

### 2.2. `MUST` / `MUST NOT` dứt khoát

Lý do sâu hơn hình thức RFC 2119: **`should` cấp cho tác nhân một đường thoát hợp lệ** — giấy phép
bỏ luật khi gặp sức ép nhẹ. `MUST` gỡ quyền tuỳ nghi đó. Tầng `MUST`/`SHOULD`/`MAY` cho phép bạn
**chủ động chọn chỗ nào agent được phép linh hoạt**.

Thực tế corpus: 11/12 file dùng `MUST`. `SHALL` gần như tuyệt chủng. File 0-MUST
(`microsoft/azure-agents-control-plane`) đọc như gợi ý, không như luật.

**Lưu ý cho dự án tiếng Việt:** không prompt nào của spec-kit nhắc tới ngôn ngữ khác; `analyze` khớp
chuỗi `MUST`/`SHOULD`. Viết `PHẢI` là đang phụ thuộc vào việc mô hình tự ánh xạ ngữ nghĩa.
Cách an toàn: **văn xuôi tiếng Việt + token `MUST`/`MUST NOT` viết hoa tiếng Anh**.

### 2.3. Ngắn — ~5 nguyên tắc, ~600–1500 từ

Hiến chương bị nạp vào **9 lệnh**, trả phí mỗi lần chạy. Ba nguồn độc lập hội tụ:

| Nguồn | Bằng chứng |
|---|---|
| spec-kit tự dogfood (`.specify/memory/constitution.md`) | **5** nguyên tắc, 1.743 từ, 42 `MUST`, 2 `SHOULD` |
| Corpus 12 repo thật (đếm lại độc lập) | median **5** nguyên tắc, **931** từ |
| Marri (đo trên case study) | 15 nguyên tắc → 78% tuân thủ; 3–5 → 96%; 5–8 → 91% |

Hai file corpus vượt 5.000 từ (`theplant` 6.200, `flowspec` 5.217) đều thoái hoá thành sổ tay quy
trình, không còn là hiến chương.

### 2.4. Có Rationale

Lệnh core: *"explicit rationale if not obvious"* (`constitution.md:77`). Hiến chương của chính spec-kit
có `**Rationale:**` ở **5/5** nguyên tắc. Trong corpus chỉ 7/12 có — và đó là nhóm mạnh nhất.

Rationale không phải trang trí: **khi hai nguyên tắc xung đột, đó là căn cứ duy nhất để agent xử ưu tiên.**
`lancarme` có 71 `MUST` và **0 rationale** — mệnh lệnh dày đặc, không cơ sở phân xử.

Mẫu tốt (`debrief/debrief`):

> "**Rationale**: The goal is enabling emergency hotfixes and knowledge extraction, not exhaustive
> coverage. An LLM that can quickly locate relevant code is more valuable than one with access to
> complete but unnavigable documentation."

### 2.5. Nguyên tắc là giá trị, không phải lựa chọn công nghệ

Lỗi phạm trù kinh điển — `duongdam/bun-server-js`, nguyên tắc IV:

> "The system MUST leverage PostgreSQL with the pgvector extension for robust HNSW indexing…"

Đó là **quyết định stack**, thuộc mục *Ràng buộc Kiến trúc*. Nó sẽ churn ngay khi đổi vector store,
và trao cho agent một mệnh lệnh triển khai giòn thay vì một giá trị để giữ.

Ranh giới: nhắc công nghệ **được**, nếu kèm rationale và diễn đạt một giá trị bền.
`rustnation/nvim` "Lua-First Configuration" hợp lệ — đó là repo cấu hình Neovim, và có rationale.

### 2.6. Điều hành tự đấu dây vào cổng kiểm

Hiến chương spec-kit nói thẳng nó bị cưỡng chế ở đâu:

> "Principles I–V are binding gates. The `## Constitution Check` section of the plan template MUST be
> evaluated against these principles, and `/speckit.analyze` treats conflicts with a MUST as CRITICAL.
> Violations are resolved by changing the spec, plan, or tasks — not by diluting a principle."

---

## 3. Các chế độ hỏng

1. **Placeholder chưa điền** — chế độ hỏng phổ biến nhất ngoài đời (xem §4.2).
2. **Nguyên tắc mơ hồ** ("chất lượng là quan trọng") — không có gì để đối chiếu.
3. **`should` thay vì `MUST`** — trao đường thoát cho agent.
4. **Quá nhiều nguyên tắc** — pha loãng + truncation.
5. **Chi tiết triển khai đội lốt nguyên tắc** — thuộc spec/plan, làm hiến chương churn.
6. **Số nguyên tắc công bố ≠ số định nghĩa** (`Azure-Samples` nói "11 mandatory patterns", chỉ có 9).
7. **Agent áp dụng quá đà** — xem §5.
8. **Sửa hiến chương không tự động cập nhật spec/plan/tasks đã sinh** — đây chính là lý do lệnh core
   có bước *Sync Impact Report*.

### Cái bẫy của hiến chương "mong muốn" trên dự án brownfield

Nếu phê chuẩn một nguyên tắc mà code hiện tại **chưa đạt** thành `MUST`:

- **`converge`** sẽ đẻ ra task khắc phục cho toàn bộ code cũ (`converge.md:86`);
- **cổng `Constitution Check` của `plan`** có thể ERROR, chặn việc lập kế hoạch cho feature không liên quan.

Người dùng vừa viết xong hiến chương liền lãnh một cơn bão, rồi học được bài học sai: rằng hiến
chương là thứ gây phiền. Cách xử: giữ `MUST` (đủ lực cho code **mới**) + thêm mục **Phạm vi áp dụng**
trong Điều hành, liệt kê vùng miễn trừ tạm thời và hạn chuẩn hoá.

---

## 4. Bằng chứng thực nghiệm

### 4.1. Hiến chương spec-kit tự dùng (nguồn chuẩn nhất)

`.specify/memory/constitution.md` — 214 dòng, 1.743 từ, **5 nguyên tắc**, 42 `MUST`, 2 `MUST NOT`,
2 `SHOULD`, `**Rationale:**` ở cả 5/5. Mở đầu bằng một câu định hướng cho brownfield:

> "These principles are **derived from the patterns the codebase already enforces**."

Tức: đọc code, rút ra luật đang có, rồi trình cho người phê chuẩn — không hỏi suông.

### 4.2. Corpus hiến chương thật trên GitHub

12 file đã điền, đếm lại độc lập:

| Chỉ số | Giá trị |
|---|---|
| Số nguyên tắc | `[3, 5, 5, 5, 5, 5, 6, 7, 7, 7, 10]` — median **5**, mode **5** |
| Số từ | median **931**, cụm chính 600–1500 |
| Dùng `MUST` | 11/12 |
| Có Rationale | 7/12 |

**Placeholder chưa điền:** trong 21 file tải về, **9 file là template trắng nguyên** (~39 từ, còn
`[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`…). Có `748` file `constitution.md` công khai còn chứa
`[PRINCIPLE_1_DESCRIPTION]`.

> ⚠️ **Không dùng tỷ lệ phần trăm.** GitHub code search trả `total_count` **không tất định**: cùng một
> truy vấn chạy 3 lần cho `2556, 1224, 2556` và `9744, 9744, 2188`. Tuỳ lần bốc, "tỷ lệ chưa điền"
> ra 7,7% hoặc 34%. Chỉ con số tuyệt đối và mẫu tải-thật là dùng được.

### 4.3. Bằng chứng học thuật

**Marri, *Constitutional Spec-Driven Development*** (arXiv:2602.02584, 31/01/2026) — đã tải PDF, đọc
Bảng 5 nguyên văn:

| Strategy | Principles | Compliance | Quality |
|---|---|---|---|
| Full Constitution | 15 | 78% | Inconsistent |
| Relevant Selection | 3-5 | **96%** | High |
| Hierarchical | 5-8 | 91% | Good |

Abstract: *"constitutional constraints reduce security defects by 73% compared to unconstrained AI generation"*.

> ⚠️ **Đọc như chiều hướng, không phải hằng số.** Bài tự ghi trong Threats to Validity:
> *"Small sample size (n=1 project) limits statistical power for quantitative claims."*
> Một đội duy nhất, đã qua đào tạo bảo mật, có hiệu ứng Hawthorne, domain ngân hàng.

**Farrag, *The Productivity-Reliability Paradox*** (arXiv:2605.01160, 01/05/2026) — nghiên cứu can
thiệp **ba đội công nghiệp** (before/after, mỗi pha 2 tháng). Luận điểm:
*"Specification discipline, not model capability, is the binding constraint on AI-assisted software dependability."*

Đóng góp thực dụng nhất — **ngưỡng áp dụng hiến chương**:

> "The constitutional governance threshold should apply to tasks that directly handle authentication,
> authorization, payment processing, personally identifiable information… Routine input validation for
> non-sensitive fields can be addressed through executable contracts (tests that verify sanitization)
> **without requiring full constitutional governance, preserving velocity for the majority of tasks.**"

---

## 5. Mặt trái, ít người nói

Birgitta Böckeler (martinfowler.com) quan sát hiến chương hỏng theo **cả hai chiều**:

- bị phớt lờ — *"the guidelines don't guarantee compliance despite their prominent role"*;
- **áp dụng quá đà** — *"the agent go way overboard because it was too eagerly following instructions
  (e.g. one of the constitution articles)"*.

Nhiều hơn và mạnh hơn **không** luôn tốt hơn.

Cách hoà giải với các bài đo được (suy luận, không phải quan sát trực tiếp): các bài đo dùng hiến
chương **bảo mật neo vào CWE** — kiểm được bằng máy. Böckeler quan sát các nguyên tắc **kiến trúc**
— mờ hơn. Càng kiểm được thì agent càng tuân thủ đáng tin. Vòng lại đúng thuộc tính §2.1.

---

## 6. Ghi chú về cơ chế preset (đã kiểm thực nghiệm)

Liên quan trực tiếp nếu muốn ship hiến chương qua preset:

- **Preset không thể ghi vào `.specify/memory/constitution.md` bằng `type: template`.**
  `init.py:450` gieo hiến chương **trước** khi cài preset (`init.py:509`), và đọc
  `.specify/templates/constitution-template.md` bằng **đường dẫn trực tiếp** (`init.py:39`),
  bỏ qua `PresetResolver`. Hàm gieo còn có guard `if memory_constitution.exists(): return`.
- **`PresetResolver` khớp theo tên file trên đĩa**, không theo `name:` trong manifest. Nhưng
  `constitution-template` **không có consumer nào** ngoài `init.py:39` → template preset là vô dụng.
- **Cách duy nhất chạm được file sống: override command `speckit.constitution`.**
  Kiểm chứng: preset `strategy: replace` → nội dung hạ cánh đúng
  `.claude/skills/speckit-constitution/SKILL.md` kèm `source: preset:<id>`. GitHub cũng làm vậy trong preset `lean`.
- **`strategy: wrap` bắt buộc có token `{CORE_TEMPLATE}`.** Thiếu → preset **fail toàn bộ, không đăng
  ký gì**, core giữ nguyên. Hỏng ồn ào, không âm thầm.
- **`strategy` là key thật** (`tmpl.get("strategy", "replace")`); `replaces:` trong preset `lean`/
  `self-test` của chính GitHub **không được code đọc** — chỉ là trang trí.
- **Hiến chương sống sót qua `specify init --force`** (đã thử). CHANGELOG dòng 1292:
  `fix: preserve constitution.md during reinitialization (#1541)`. Cảnh báo trong `docs/upgrade.md` đã lỗi thời.

## 7. Mâu thuẫn trong tài liệu spec-kit

`spec-driven.md` mô tả mô hình **9 điều khoản** ("The Nine Articles of Development"), trong khi
`constitution-template.md` và hiến chương thật của họ chỉ có **5**. Tài liệu khái niệm đi trước code
và chưa được cập nhật — **đừng lấy con số 9 làm chuẩn**.

---

## Nguồn

**Source code** (clone `github/spec-kit`, `main`, 2026-07-09): `templates/commands/{constitution,analyze,converge,plan,specify,tasks,clarify,checklist,implement}.md`,
`templates/constitution-template.md`, `.specify/memory/constitution.md`, `src/specify_cli/commands/init.py`,
`src/specify_cli/presets/__init__.py`, `presets/lean/`, `presets/self-test/`, `spec-driven.md`, `CHANGELOG.md`.

**Học thuật**
- Marri, S. R. — *Constitutional Spec-Driven Development: Enforcing Security by Construction in AI-Assisted Code Generation*. https://arxiv.org/abs/2602.02584
- Farrag, S. E. — *The Productivity-Reliability Paradox: Specification-Driven Governance for AI-Augmented Software Development*. https://arxiv.org/abs/2605.01160

**Cộng đồng**
- Böckeler, B. — *Exploring Gen AI: SDD tools*. https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- spec-kit issue #1149 (ranh giới hiến chương ↔ spec; **đã đóng, "not planned"** — là đề xuất của người báo, không phải hướng dẫn chính thức)
- spec-kit discussion #980

**Corpus** (hiến chương thật): `DirectedEdges/specs`, `debrief/debrief`, `lem-project/lem`,
`lchorbadjiev/obsidian-toolbox`, `rustnation/nvim`, `vtex-apps/admin-pages`,
`microsoft/azure-agents-control-plane`, `duongdam/bun-server-js`, `RobAWilkinson/jazzgym`,
`gilstrickland-ship-it/polymorph`, `JuniorSantosDev86/lancarme`, `theplant/speckit-starter-go`,
`jpoley/flowspec`, `Azure-Samples/azure-speckit-constitution`.
