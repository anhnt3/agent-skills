# Nghiên cứu: đưa UI/UX checklist vào template spec/plan/tasks — cơ chế & chuẩn SDLC

> Nghiên cứu ngày 2026-07-12, phục vụ quyết định "**đưa `templates/ui-ux-checklist.md` vào template của
> spec/plan/tasks, không cần lệnh `checklist` nữa**".
> Ba mũi research song song: (1) source-code spec-kit (clone thật, HEAD `1be4299` — cùng commit đã kiểm
> ở `speckit-addon-review-2026-07-11.md`, version string `0.12.12.dev0`, **không có thay đổi cơ chế** so
> với 0.12.11); (2) tài liệu/web chính thức spec-kit; (3) chuẩn SDLC về mô tả spec một màn hình.
> Mọi kết luận chịu lực có dẫn `file:line` (source) hoặc URL (web). VERIFIED = đã đọc code; INFERRED = suy luận.

---

## TL;DR

1. **Ghi đè `spec-template`/`plan-template`/`tasks-template` bằng preset `strategy: replace` là CƠ CHẾ THẬT**
   và được resolver honor cả phía agent lẫn phía script. Đây là con đường "đưa nội dung vào template" đúng
   nghĩa đen và đúng tài liệu chính thức. **NHƯNG** `wrap`/`prepend`/`append` trên plan/tasks-template là
   **ngõ cụt**: script `setup-plan.sh`/`setup-tasks.sh` gọi `resolve_template` (chỉ trả path, không compose)
   → template `wrap` sẽ bị copy nguyên xi, **rò literal `{CORE_TEMPLATE}`** vào plan.md/tasks.md. Với template,
   **chỉ `replace` là an toàn** → phải ship template TỰ CHỨA (chép lại các section core còn muốn giữ).
2. **Con đường thứ hai — wrap COMMAND** (`speckit.specify`/`speckit.plan`/`speckit.tasks` với `strategy: wrap` +
   `{CORE_TEMPLATE}`) — resolver compose sạch và materialize thành snapshot; đây là cơ chế preset hiện tại đã
   dùng cho specify/plan. Robust, nhưng là snapshot (cần disable/enable sau khi nâng CLI).
3. **Template được resolve LIVE**, không materialize như command → override template KHÔNG cần nghi thức
   disable/enable sau nâng CLI (khác với command override). Đổi lại, `specify init --force` vẫn có thể ghi đè
   `.specify/templates/` core (không đụng `.specify/presets/<id>/templates/`).
4. **Về chuẩn SDLC**: nhúng một checklist CỐ ĐỊNH vào template spec/plan/tasks **không phải pattern được tài
   liệu spec-kit khuyến nghị** (hướng chính: checklist là artifact RIÊNG trong `FEATURE_DIR/checklists/*.md`;
   quy ước cố định thì để ở **constitution**). Nhưng không bị cấm. Chuẩn SDLC (29148, use-case, Volere, NN/G,
   GOV.UK) cho ta **bộ khung "giải phẫu spec một màn hình"** — và nguyên tắc vàng: **cái dùng chung định nghĩa
   một lần ở tài liệu hệ thống, mỗi màn tham chiếu theo ID, không lặp lại**. `ui-ux-checklist.md` hiện tại của
   repo chính là "convention dùng chung" đó.
5. **Hàm ý**: câu hỏi cốt lõi không phải "template hay command" thuần kỹ thuật, mà là **checklist nên là quy ước
   dùng chung được cưỡng chế (gate) hay là scaffold tĩnh trong artifact**. Xem §3.

---

## PHẦN 1 — Cơ chế spec-kit: nhúng checklist vào spec/plan/tasks

### 1.1 Core commands nạp template thế nào (VERIFIED)

Không hardcode path, không token `{...}` — **template resolve theo NAME qua stack preset/extension**, bởi agent
hoặc bởi script bash:

| Command | Ai resolve | Bằng chứng |
|---|---|---|
| `speckit.specify` | **Agent tự làm** (không có `scripts:` frontmatter) | `templates/commands/specify.md:96-97` — "Resolve the active `spec-template` … (equivalent to `specify preset resolve spec-template`)" rồi "Copy the resolved `spec-template` to spec.md"; reload ở `:113`. Path thay thế: `create-new-feature.sh:254` `resolve_template "spec-template"` |
| `speckit.plan` | **Script** `setup-plan.sh` | `plan.md:12` frontmatter `sh: scripts/bash/setup-plan.sh`; `setup-plan.sh:46` `TEMPLATE=$(resolve_template "plan-template" …)` → `cp` `:48`; `plan.md:63` "Load IMPL_PLAN template (already copied)" |
| `speckit.tasks` | **Script** `setup-tasks.sh` | `tasks.md:13` `sh: setup-tasks.sh`; `setup-tasks.sh:53` `resolve_template "tasks-template"`; `tasks.md:81` "Read the tasks template from TASKS_TEMPLATE … fallback `.specify/templates/tasks-template.md`" |
| `speckit.checklist` | Sinh động, KHÔNG stamp | `checklist.md:248` "Generate the checklist following the canonical template in `templates/checklist-template.md` for title, meta, category headings, ID formatting" — template chỉ cấp KHUNG, item sinh từ spec |

Resolver bash `resolve_template()` (`scripts/bash/common.sh:406-482`) đi tiers, **trả path đầu tiên khớp, copy, không compose**:
1. `.specify/templates/overrides/<name>.md`
2. presets `.specify/presets/<id>/templates/<name>.md` (theo priority registry)
3. extensions `.specify/extensions/<id>/templates/<name>.md`
4. core `.specify/templates/<name>.md`

Tên/file template core ship: `spec-template`, `plan-template`, `tasks-template`, `checklist-template`,
`constitution-template` (name = filename stem).

### 1.2 Preset/extension có ghi đè được template core không? (VERIFIED)

**CÓ — template resolve theo `name`, provide trùng tên sẽ shadow core.** Hai resolver song song:
- Python `PresetResolver.resolve()` (`presets/__init__.py:2632-2760`): tiers overrides→preset→extension→core→bundled, first match wins.
- Bash `resolve_template()` (`common.sh:406`): cùng thứ tự tiers → plan/tasks (qua script) cũng honor shadowing.

**Strategy — preset vs extension KHÁC nhau:**
- Preset: valid `{replace, prepend, append, wrap}` (`__init__.py:116`), script chỉ `{replace, wrap}` (`:117-118`),
  **mặc định `replace`** (`:231`). Preset template **có** honor strategy: `collect_all_layers` đọc `strategy`
  từ entry template khớp `name`+`type` (`:2951-2957`), `resolve_content` compose (`replace :2245`, `prepend/append`,
  `wrap` qua `{CORE_TEMPLATE}` `:3251-3263`). ⇒ **có** cơ chế `{CORE_TEMPLATE}` cho template, không chỉ command.
- Extension template: **luôn bị ép `replace`** (`__init__.py:3005/3040`, comment "always replace") — extension
  KHÔNG wrap/prepend/append template được.

**Nút thắt QUYẾT ĐỊNH — replace template có thực sự đổi thứ command nạp?**
- **`replace`: CÓ, trọn vẹn.** Cả agent (spec) lẫn `resolve_template` (plan/tasks) trả file preset trước → spec.md/plan.md/tasks.md sinh ra từ file của mình.
- **`wrap`/`prepend`/`append` trên plan/tasks-template: NGÕ CỤT.** `setup-plan.sh`/`setup-tasks.sh` gọi
  `resolve_template` (chỉ path, `common.sh:406`), KHÔNG gọi hàm compose `resolve_template_content`
  (`common.sh:485+` — **dead code, không script nào gọi**, VERIFIED bằng grep: chỉ 3 caller
  `create-new-feature.sh:254`, `setup-plan.sh:46`, `setup-tasks.sh:53`, đều bản không-compose). ⇒ template `wrap`
  bị copy nguyên xi, **rò literal `{CORE_TEMPLATE}`** vào output.
- **`spec-template`: cũng thực chất chỉ `replace`.** specify.md bảo agent làm ~`specify preset resolve spec-template`
  rồi *copy resolved file*. `specify preset resolve` (`_commands.py:308-360`) chỉ **in path layer ưu tiên cao
  nhất** + cảnh báo composition-chain, **không in nội dung đã compose** → agent copy file top preset (kèm literal
  `{CORE_TEMPLATE}` nếu lỡ dùng wrap).

⇒ **Với TEMPLATE, chỉ `replace` đáng tin. Muốn override template thì phải TỰ CHỨA** (chép lại các section core còn muốn).

### 1.3 Materialization template (VERIFIED)

- **Template KHÔNG materialize** vào `.specify/templates/` — nằm ở `.specify/presets/<id>/templates/<name>.md`,
  **resolve LIVE mỗi lần chạy**. `preset add` chỉ `shutil.copytree` sang `.specify/presets/<id>/` (`:1537-1540`).
- Chỉ **COMMAND** mới materialize vào command dir của agent (`_register_commands :1560`, reconcile `:701+`).
- **Hệ quả**: override template có hiệu lực ngay, re-resolve live → **KHÔNG cần disable/enable sau nâng CLI**
  (khác command override mà CLAUDE.md cảnh báo). Đổi lại `specify init --force` vẫn ghi đè `.specify/templates/`
  core (upgrade guide xác nhận, §1.6).

### 1.4 Lệnh checklist & ui-ux-checklist (VERIFIED)

- `speckit.checklist` **sinh động**, không stamp template cố định (`checklist.md:248`). Có `checklist-template`
  nhưng chỉ là khung cấu trúc.
- **`ui-ux-checklist` KHÔNG có auto-wiring.** Resolver chỉ đưa template ra khi có thứ hỏi **theo name**
  (`specify preset resolve ui-ux-checklist`). Không có đường quét-preset-rồi-tự-inject. ⇒ template standalone chỉ
  được tiêu thụ nếu **thân command chủ động resolve + đọc** nó (đúng như `speckit.checklist.md` preset đang làm).
- **Hook phase core nhận (VERIFIED grep `hooks.<phase>`):** `before_/after_` cho `specify, plan, tasks, checklist,
  clarify, analyze, implement, constitution, converge, taskstoissues`. Hook theo **command-phase, KHÔNG theo template**
  — không có hook gắn `spec-template`.

### 1.5 Tài liệu chính thức nói gì (web)

- **Template overridable qua resolution stack runtime**, thứ tự overrides > preset > extension > core; "Template
  resolution happens at runtime." — https://github.github.io/spec-kit/reference/presets.html
- **`strategy: replace` (default) shadow trọn template core**; 4 strategy `replace/prepend/append/wrap`; script chỉ
  `replace/wrap`. Tên template "lowercase-hyphen". — presets.html, `presets/README.md`
- **`.specify/templates/overrides/` = đường nhẹ nhất** cho chỉnh một-lần theo project (không cần cả preset). — presets.html
- **Checklist là "unit tests for requirements writing"** — kiểm chất lượng spec (đủ/rõ/nhất quán/đo được), viết ra
  **file RIÊNG** `FEATURE_DIR/checklists/<domain>.md`; anti-pattern: kiểm hành vi triển khai ("Verify button
  clicks"). — `templates/commands/checklist.md`
- **Quy ước cố định (UX/coding) thuộc CONSTITUTION** ("immutable system prompt"), không phải nhét vào template.
  Không nguồn cộng đồng nào khuyến nghị hard-code checklist trong template spec/plan/tasks. — den.dev, linuxera, runmaestro
- ⚠️ **Bất nhất field trong docs upstream**: `presets/README.md`+docs-site dùng `name:`+`strategy:`; `presets/PUBLISHING.md`
  lại dùng `replaces:`. Repo này (và docs-site) dùng `strategy: replace` — dạng được chứng thực tốt hơn. Cần verify
  schema CLI đang cài trước khi dựa vào `replaces:`.

### 1.6 Upgrade clobber (web, xác nhận lo ngại của repo)

- Upgrade guide: "If you customized files in `.specify/scripts/` or `.specify/templates/`, `--force` will overwrite
  them"; `specify init --here --force` từng ghi đè `.specify/memory/constitution.md`. Nên ưu tiên
  `.specify/templates/overrides/` vì "won't be clobbered during upgrades". — https://github.github.io/spec-kit/upgrade.html
- **GAP**: trang presets reference **im lặng** về rủi ro upgrade clobber materialization → nghi thức disable/enable/resolve
  của repo là phòng xa dựa trên hành vi source, docs không chỉ ra.
- ⚠️ **Pitfall vòng regenerate** (discussion #839): sau `/speckit.checklist` báo gap, chạy lại `/speckit.plan` "risks
  overwriting previous plan"; workaround của cộng đồng: dặn agent "DO NOT RECREATE FROM SCRATCH, READ CURRENT FILES
  AND UPDATE". Không có pattern chính thức. — https://github.com/github/spec-kit/discussions/839

### 1.7 Hai cơ chế khả thi (tóm tắt quyết định)

| Cơ chế | Thật? | Robust? | Ghi chú |
|---|---|---|---|
| **Replace `spec/plan/tasks-template`** (preset, `strategy: replace`) | ✅ | ✅ live-resolve, không cần disable/enable | Phải TỰ CHỨA; `wrap/prepend/append` = ngõ cụt (rò `{CORE_TEMPLATE}`); là "text tĩnh" — model có thể lướt |
| **Wrap COMMAND `specify/plan/tasks`** (preset, `strategy: wrap`) | ✅ | ✅ compose sạch, nhưng snapshot (disable/enable sau nâng CLI) | Cơ chế preset đang dùng; cho phép gate CHỦ ĐỘNG (chấm/ép), không chỉ text tĩnh |
| Nhét checklist vào constitution | ✅ | ✅ | Hướng "đúng chuẩn" của docs cho quy ước cố định; nhưng đổi bản chất (constitution = nguyên tắc, converge/analyze bốc theo MUST) |
| Extension override template | ✅ nhưng luôn `replace`, priority thấp hơn preset | — | Không phù hợp: repo tách extension = command mới, preset = override |

---

## PHẦN 2 — Mô tả spec MỘT MÀN HÌNH theo chuẩn SDLC

Một màn hình hầu như không do một loại artifact mô tả trọn; nó trải trên: SRS (interface requirements),
use-case spec (hành vi), UI/interaction spec (chi tiết màn), và acceptance criteria (agile/BDD).

### 2.1 Artifact chuẩn (FORMAL vs INDUSTRY)

- **ISO/IEC/IEEE 29148:2018** (kế thừa IEEE 830) — nội dung màn nằm ở **External Interface Requirements → User
  interfaces** (GUI standard/style-guide phải theo, bố cục, tập control, phím/chuột, quy ước error/help). SRS
  coi UI là interface thô; per-field/state/validation nằm ở functional requirements. 9 đặc tính requirement:
  Necessary, Appropriate, Unambiguous, Complete, Singular, Feasible, **Verifiable**, Correct, **Conforming**.
  — reqview.com/doc/iso-iec-ieee-29148-srs-example, drkasbokar.com 29148 PDF
- **Use-case spec (Cockburn/RUP)** — actor, precondition, postcondition, trigger, main success scenario (steps),
  **extensions (alternate + exception)**. Nhà của "action → outcome" và xử lý lỗi/ngoại lệ. — cockburn template, RUP ucspec
- **UI/screen spec (BA — Bridging the Gap)** — visual overview có nhãn theo section, display rules (sort, field nào
  hiện, thiếu field thì sao), messaging (message + điều kiện kích hoạt), links (mỗi nút/link đi đâu), field-level
  validation + business rule. Khuyến nghị: chỉ màn phức tạp mới cần UI spec đầy đủ; logic điều kiện nặng đẩy sang
  use-case tham chiếu. — bridging-the-gap.com
- **NN/G Prototype Specifications** — 3 nhóm annotation: **Element** (font/size/color/spacing), **Functionality**
  (cách control chạy, **ràng buộc như max ký tự & khi vi phạm thì sao**, **các state của component vd nút disabled
  theo điều kiện**), **Content** (message: tip ngữ cảnh & **error message**, nội dung copy). — nngroup.com/articles/prototype-specifications
- **User story + AC (Agile/BDD)** — story + acceptance criteria; 2 dạng: rule-checklist và Gherkin **Given/When/Then**
  (behavior-focused, map thẳng test). — altexsoft, testquality

### 2.2 Giải phẫu spec một màn hình (tổng hợp — dạng checklist)

Nhãn nguồn: [29148] formal · [UC] use-case · [Volere] · [NN/G] · [BA] · [GOV.UK] · [BDD].

**Định danh & mục đích**
- Screen ID + tên + mục đích một dòng [29148/UC]; vị trí trong luồng: upstream (vào) / downstream (ra) [BA/UC]

**Truy cập**
- Actor & vai trò; per-role thấy/sửa/thao tác → **tham chiếu ma trận quyền**, không inline [UC/BA]

**Điều kiện**
- Precondition để hiển thị; postcondition/side-effect khi thành công **và** khi hủy [UC]

**Kiểm kê UI (section có nhãn)**
- Field, button, table (+cột), filter/sort/search, link [BA/NN/G]

**Bảng field (mỗi field một dòng)**
- Kiểu · required? · format/constraint (vd max length) · giá trị hợp lệ · default [29148/NN/G]
- Luật validation → **câu lỗi chính xác** cho từng vi phạm [NN/G/BA]

**Trạng thái**
- Màn: default/populated, loading, empty, error, success [NN/G/BA]
- Component: default/hover/active/**disabled + điều kiện disable** [NN/G]

**Hành vi**
- Mỗi action/control: outcome, phản hồi hệ thống, dữ liệu đổi, điều hướng [UC main+extensions]
- Alternate + exception flow [UC]; business rule → tham chiếu **rule catalog** theo ID [BA/29148 "Conforming"]

**Message**
- Success/warning/error + điều kiện kích hoạt → tham chiếu **message catalog** theo key [NN/G/BA]

**Cross-cutting (tham chiếu, KHÔNG lặp)**
- Data model/dictionary [BA]; design-system component & state [NN/G/GOV.UK]; i18n string key & format theo locale;
  a11y: **WCAG 2.2 AA**, field có nhãn, thao tác bàn phím, nhận diện/sửa lỗi [GOV.UK]; responsive breakpoint

**Kiểm thử được**
- Định danh phần tử ổn định cho e2e [BDD]; AC mỗi hành vi (Given/When/Then và/hoặc rule), mỗi cái **đo được, không
  mơ hồ, verify được** (cấm "nhanh/thân thiện") [29148/BDD]; truy vết rule ↔ AC ↔ test case [BA/BDD]; Fit Criterion
  cho kỳ vọng phi chức năng [Volere]; đạt Definition of Ready; DoD áp toàn cục [Scrum]

### 2.3 Màn-lẻ vs hệ-thống: inline gì, tham chiếu gì (nguyên tắc vàng)

Nhất quán qua các chuẩn: **spec màn chỉ nói về màn đó; quy ước dùng chung factor ra tài liệu cross-cutting, tham
chiếu theo ID** — chính là đặc tính "**Conforming**" của 29148 và pattern design-system của công nghiệp.

- **Thuộc spec màn**: mục đích màn, kiểm kê phần tử, luật field, state, outcome mỗi action, điều hướng nội bộ, AC.
- **Thuộc tài liệu hệ thống (tham chiếu theo ID)**: data model/dictionary, **message/error catalog toàn cục**,
  design-system + state component, **ma trận quyền**, luật format validation dùng chung, i18n string, chuẩn a11y.
- Cơ chế chống lặp: **tham chiếu theo ID ổn định** (component ID, rule ID, message key, role) thay vì inline.

### 2.4 Đối chiếu với `ui-ux-checklist.md` hiện tại của repo

`ui-ux-checklist.md` (CHK001–011) **chính là bộ "quy ước dùng chung" + "gate hoàn chỉnh spec màn"** mà §2.3 mô tả,
đóng khung theo đặc thù DFT (tiếng Việt, message catalog, validation rule code `VR_*`, một-hành-động-một-động-từ,
4 state, khai đủ cột/filter/sort, quyền, `data-testid` e2e). Nó phủ gần trọn "giải phẫu" §2.2 ở tầng **convention
cross-cutting** — đúng thứ chuẩn khuyên "định nghĩa một lần, tham chiếu". Điều CHK làm hơn chuẩn: kèm **ví dụ ✗→✓
thật** và ràng buộc "trích nguồn spec" khi chấm → biến convention thành **gate kiểm được**.

---

## PHẦN 3 — Hàm ý cho quyết định thiết kế

Câu hỏi cốt lõi **không** thuần kỹ thuật (template vs command) mà là bản chất của checklist trong luồng:

1. **Checklist = gate CHỦ ĐỘNG (chấm spec + vá gap)** — sức mạnh hiện tại đến từ việc lệnh `checklist` *chấm* spec
   theo từng CHK, trích nguồn, và *sửa spec* chỗ gap. Nếu chỉ **paste CHK làm text tĩnh vào template** (replace
   spec-template), nó thành scaffold thụ động — model có thể điền cho có hoặc lướt qua, mất tác dụng gate.
   → Muốn giữ sức mạnh gate mà bỏ lệnh `checklist` thì phải **dệt bước KIỂM vào command wrap** (specify chấm CHK ở
   một giai đoạn như GĐ4 đối chiếu hiến chương; plan/tasks ép output tuân CHK), giữ `ui-ux-checklist.md` làm **một
   nguồn duy nhất** (DRY) mà command tham chiếu theo name.

2. **Chuẩn SDLC ủng hộ tách bạch**: convention dùng chung (CHK) định nghĩa một lần, mỗi màn *tham chiếu*. Nhúng
   nguyên văn CHK vào từng spec.md là **lặp lại convention** — ngược nguyên tắc "Conforming/reference-by-ID". Hợp
   chuẩn hơn: template spec/plan/tasks có **section trỏ tới bộ CHK** + command *cưỡng chế* đối chiếu, chứ không copy
   toàn văn 11 mục vào mọi spec.

3. **Phân bổ theo bản chất từng CHK** (gợi ý, cần chốt với người dùng):
   - Phần lớn CHK (message, validation, layout, state, cột/filter, quyền) là **nội dung SPEC** → thuộc `specify`
     (đã trùng nhiều với GĐ2/GĐ3 phỏng vấn hiện có) → gate ở specify.
   - CHK011 (`data-testid` e2e) nghiêng **triển khai** → thuộc `plan`/`tasks`.
   - `tasks`: hiện **preset CHƯA wrap** `speckit.tasks` → muốn đụng tasks phải thêm command wrap mới.

4. **Rủi ro vận hành cần cân**: replace 3 template core = phải tự chứa + tự bảo trì khi core đổi template (mất lợi
   ích "dùng template mặc định" mà preset đang cố ý giữ). Wrap command = snapshot, cần disable/enable sau nâng CLI
   (đã có runbook). Cả hai đều thêm bề mặt neo-nguyên-văn-core phải canh bằng `check-core-anchors.sh`.

**Các quyết định còn mở để thảo luận** (chưa chốt): (a) cơ chế — replace template / wrap command / hybrid section+gate;
(b) phân bổ CHK vào spec/plan/tasks theo bản chất hay dồn hết vào specify; (c) số phận lệnh `checklist` (xóa hẳn khỏi
manifest hay giữ cho chạy tay); (d) có thêm wrap `speckit.tasks` không; (e) giữ `ui-ux-checklist.md` làm nguồn DRY
được tham chiếu, hay inline nội dung vào template/command.

---

## Nguồn

**Source (clone HEAD `1be4299`, `0.12.12.dev0`):** `templates/commands/{specify,plan,tasks,checklist}.md`;
`scripts/bash/{common.sh,setup-plan.sh,setup-tasks.sh,create-new-feature.sh}`; `src/specify_cli/presets/__init__.py`,
`presets/_commands.py`; `templates/{spec,plan,tasks,checklist,constitution}-template.md`.

**Web:** presets reference https://github.github.io/spec-kit/reference/presets.html · extensions
https://github.github.io/spec-kit/reference/extensions.html · `presets/{README,PUBLISHING}.md` ·
checklist command `templates/commands/checklist.md` · upgrade guide https://github.github.io/spec-kit/upgrade.html ·
discussion #839 https://github.com/github/spec-kit/discussions/839 · CHANGELOG.

**Chuẩn SDLC:** ISO/IEC/IEEE 29148:2018 (reqview.com; drkasbokar.com PDF) · Cockburn/RUP use-case (cockburn template;
RUP ucspec) · Volere (volere.org) · NN/G prototype specs (nngroup.com/articles/prototype-specifications) · GOV.UK
Service Manual/Design System (design-system.service.gov.uk; gov.uk/service-manual) · BA UI spec (bridging-the-gap.com) ·
Gherkin/AC (altexsoft, testquality).
