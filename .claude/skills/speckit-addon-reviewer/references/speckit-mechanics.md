# Spec Kit — cheatsheet cơ chế (để review chính xác)

Biết cơ chế core mới bắt được lỗi ngữ nghĩa. Tóm tắt phần liên quan review.

## Mục lục
- Preset vs Extension
- Template resolution stack
- Vòng chạy lệnh core (specify làm ví dụ) + tên section
- Hook flow
- Gotcha đóng gói

## Preset vs Extension

| | Preset | Extension |
|---|---|---|
| Manifest | `preset.yml` (id kiểu `dft-mstem`) | `extension.yml` (id kiểu `dft-speckit`) |
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
