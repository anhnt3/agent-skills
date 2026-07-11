# Spec Kit — cheatsheet cơ chế (để review chính xác)

Biết cơ chế core mới bắt được lỗi ngữ nghĩa. Tóm tắt phần liên quan review.

> **Cheatsheet là snapshot** — xác minh lần cuối với spec-kit **0.12.11** (2026-07-11, đối chiếu
> source; chi tiết: `docs/research/speckit-addon-review-2026-07-11.md`). Khi review, LUÔN xác minh
> các neo section với đúng version spec-kit mà addon nhắm tới (chạy `scripts/check-core-anchors.sh`
> trên project đích hoặc clone upstream), đừng tin cheatsheet mù quáng.

## Mục lục
- Preset vs Extension
- Template resolution stack
- Vòng chạy lệnh core (specify làm ví dụ) + tên section
- Hook flow
- Gotcha đóng gói
- Fact source-level dễ đoán sai (0.12.11)

## Preset vs Extension

| | Preset | Extension |
|---|---|---|
| Manifest | `preset.yml` (id kiểu `dft-preset`) | `extension.yml` (id kiểu `dft-speckit`) |
| Làm gì | **Override** core command hiện có | **Thêm** command/template mới |
| Cơ chế | `strategy: wrap` (chèn `{CORE_TEMPLATE}`) hoặc `replace` (thay hẳn) | command namespace `speckit.<ext-id>.<name>` |
| Template | `strategy: replace` swap core template (constitution, checklist...) | ship template mới |

`wrap`: nội dung preset bọc quanh, chèn `{CORE_TEMPLATE}` — core template được dán vào đúng
vị trí token đó lúc materialize. Nội dung preset **phía trên** token chạy trước phần core,
**phía dưới** token chạy sau. Điều này quan trọng cho hook conflict (xem dưới).

## Template resolution stack

`spec-template`, `plan-template`, `checklist-template`, `constitution-template` được resolve
qua stack preset/template (`specify preset resolve <name>`). Preset `replace` một template
sẽ thay bản core. Lệnh core tham chiếu "active template" chứ không hardcode → preset tự
chứa được (chạy trên dự án fresh không có constitution sẵn), NHƯNG `preset add` chỉ swap
template, **không ghi** `.specify/memory/constitution.md` sống → dự án fresh phải copy tay,
nếu không interview mất nguyên tắc. Đây là điểm review hay bắt: preset giả định constitution
tồn tại mà không có fallback.

## Vòng chạy lệnh core `specify` (tên section — dùng khi kiểm coupling)

Thứ tự trong `templates/commands/specify.md` của core:
1. **User Input** — `$ARGUMENTS`.
2. **Pre-Execution Checks** — đọc `.specify/extensions.yml`, chạy hook `before_specify`.
   Hook `optional: false` → core ghi "Automatic Pre-Hook / EXECUTE_COMMAND / **MUST** invoke".
3. **Outline** — sinh short-name, tạo branch (qua hook), tạo spec dir, copy spec-template.
4. **Specification Quality Validation** — sinh `checklists/requirements.md`, luật "tối đa 3
   [NEEDS CLARIFICATION]", "Make informed guesses", bảng clarification markdown.
5. **Mandatory Post-Execution Hooks** — `after_specify`.
6. **Completion Report**.
7. **Quick Guidelines / For AI Generation** — "reasonable defaults (don't ask about these)":
   auth, retention, performance...

**Vì sao cần tên section**: preset `wrap` đè luật core phải neo vào TÊN section ("khi tới
mục Pre-Execution Checks..."), không nói chung chung "preset ghi đè". Model đọc tuần tự, gặp
core "MUST invoke hook" ở gần điểm hành động dễ tuân core hơn lời đè mơ hồ ở xa. Neo tên =
bịt. Đồng thời: neo tên cứng = coupling, upstream đổi tên thì gãy → cờ version-pin.

## Hook flow

`.specify/extensions.yml` khai `hooks.before_<cmd>` / `hooks.after_<cmd>`. Extension (vd git)
đăng ký hook. Mỗi hook: `command`, `optional` (true = hỏi/tùy chọn, false = tự chạy MUST),
`prompt`, `description`, `condition` (core KHÔNG tự eval condition — để HookExecutor lo).

Git extension mặc định: `before_specify: speckit.git.feature (optional:false)` → tạo branch.
Branch do **hook** tạo, spec dir + `feature.json` do **lệnh core** tạo — tách biệt. Preset
muốn giữ branch hiện tại phải vô hiệu hóa hook này tường minh (kể cả `optional:false`/MUST).

## Gotcha đóng gói (extension)

- `build-zip.sh` phải `cp -R` MỌI support dir command tham chiếu. Manifest `provides` chỉ
  liệt command/template — KHÔNG gate cái gì được bundle. Command trỏ
  `.specify/extensions/<id>/references/foo.md` mà build-zip quên copy `references/` →
  ship command gãy, không lỗi lúc build.
- Install: `--from` chỉ nhận HTTPS/localhost, không nhận `file://`.
- Installed tree: `<project>/.specify/extensions/<id>/`. Sau cài, assert các referenced dir
  có mặt (vd `ls .../references/` đủ số file).
- Tag release phải KHỚP version manifest, không thì workflow fail.
- Dev install (`--dev`) copy cả thư mục (kéo theo `.omc/`, `dist/`...) — noise nhưng vô hại;
  zip release mới là cái sạch để verify cái thực ship.

## Fact source-level dễ đoán sai (xác minh trên 0.12.11)

1. **Preset override là snapshot materialize, không resolve lại lúc chạy.** Compose xong là ghi
   hẳn vào thư mục command của agent; chỉ reconcile khi preset install/remove/enable/disable.
   → Nâng cấp CLI spec-kit / re-init có thể clobber override âm thầm. Review addon nào không
   document bước re-reconcile sau upgrade = finding.
2. **`{CORE_TEMPLATE}` thay bằng `str.replace` — MỌI occurrence đều expand**, không phải đúng-một.
   Lint "đúng 1 token" vẫn đúng như best-practice (nhiều token = nhân đôi core body), nhưng đừng
   báo "cơ chế chỉ thay lần đầu". Thiếu token trong file wrap = hard error lúc cài.
3. **Không có `.presetignore`** — preset copy nguyên thư mục (`copytree` không ignore). Chỉ
   extension có `.extensionignore` (gitignore-compatible). Build-zip preset phải tự lọc rác.
4. **Hook event name sai chính tả chết âm thầm** — validator không whitelist tên event
   (`after_speciy` pass validation, không bao giờ chạy). Kiểm tên hook với đúng bộ
   `before_/after_ × {constitution,specify,clarify,plan,tasks,implement,checklist,analyze,taskstoissues}`.
5. **Claude integration là skills-based**: command materialize thành
   `.claude/skills/<command-name>/SKILL.md`, không phải `.claude/commands/*.md` (legacy fallback).
6. **Có code path legacy đọc `strategy: wrap` từ frontmatter FILE command** song song đường đọc
   manifest → file wrap nên khai `strategy: wrap` ở cả frontmatter + `description`. **`description`
   phải ngắn vừa 1 dòng (~≤60 ký tự)**: description dài bị wrap đa dòng lúc materialize và
   `argument-hint` bị chèn vào giữa → frontmatter skill gãy YAML (thực nghiệm 0.12.4).
7. **`replaces:` trong preset first-party chỉ là metadata** — resolution key theo `name`.
   Manifest không phải closed schema: field lạ bị nuốt im lặng; `schema_version` phải đúng `"1.0"`.
8. **Phân phối chính thức**: GitHub tag archive (`/archive/refs/tags/vX.Y.Z.zip` — installer chấp
   nhận nested 1 tầng) hoặc catalog + `sha256` (verify từ 0.11.7). KHÔNG có `specify extension
   bundle`; `specify bundle build` thuộc hệ **bundle** (`bundle.yml`, schema riêng) — đừng nhầm.
   `--from` không verify sha256.
9. **Core specify không còn gọi `create-new-feature.sh`** — branch do git-extension hook
   `before_specify` tạo; spec dir + `.specify/feature.json` do lệnh core tạo. Preset `replace`
   specify phải tự tái tạo logic feature-dir + feature.json, không thì downstream gãy.
