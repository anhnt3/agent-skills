# DFT mSTEM — Spec Kit Preset

Override `/speckit.specify` thành một phiên business-analyst phỏng vấn tuần tự trước khi ghi spec, và ép spec output điền đủ 11 nguyên tắc hiến chương.

## Preset này làm gì

Các override bổ trợ nhau (5 override, gom theo mục đích):

**1. Command `speckit.specify`** (`strategy: wrap`) — điều khiển *cách hỏi*:
- Đóng vai **business analyst** theo domain dự án, thảo luận + spec bằng **tiếng Việt**.
- **Khảo sát trước khi hỏi**: tự tìm roadmap dự án (không rõ thì hỏi), codebase, nợ kỹ thuật liên quan, và `.specify/memory/constitution.md`.
- **Phỏng vấn theo cây thiết kế**: mỗi nguyên tắc trong `constitution.md` là một nhánh; hỏi qua **AskUserQuestion**, mỗi lần một câu, 2–4 option, có `(Recommended)` + lý do + trade-off.
- Đánh dấu nguồn mỗi kết luận: `[từ mock]` / `[suy luận]` / `[cần bạn quyết]`.
- **Chỉ ghi spec sau khi bạn xác nhận** đạt hiểu chung. `spec.md` dùng **spec-template mặc định** của spec-kit — toàn bộ scaffolding core (tạo `specs/<n>-<name>/spec.md`, quality checklist, hooks) kéo vào qua `{CORE_TEMPLATE}`.

**2. Command `speckit.plan`** (`strategy: wrap`) — điều khiển *cách plan*:
- **Khảo sát codebase liên quan feature** (frontend + backend đang có) trước khi điền Technical Context / Structure Decision — plan dựa trên cái đang có, không chọn layout generic.
- `plan.md` dùng **plan-template mặc định**; cổng Constitution Check của core phải pass trước Phase 0.

**3. Template `constitution-template`** (`strategy: replace`) — *ship hiến chương*:
- Chứa nguyên văn 11 nguyên tắc (Angular mockup → backend ABP). Khung phỏng vấn tham chiếu đúng bộ này, nên preset **tự chứa luật** — dùng được cho project mới không có sẵn hiến chương.

**4. Command `speckit.checklist`** (`strategy: wrap`) + **template `ui-ux-checklist`** — *bộ checklist cố định + chấm*:
- `/speckit.checklist ui-ux @spec.md` → 3 bước: **stamp** bộ IV cố định (CHK001–010) → **chấm** theo spec (tick `[x]` pass + nguồn, `⚠️ Gap`, `➖ N/A`, bảng Tổng) → **thảo luận vá** từng gap qua AskUserQuestion, cập nhật spec.md rồi tick pass.
- Chỉ điền mục còn `[ ]` trống; **giữ nguyên tick + note người đã ghi** (không clobber).
- Không kèm spec → chỉ stamp list trống. Args khác → chạy checklist sinh động của core.
- Là spec-completeness gate cho nguyên tắc IV (UI/UX).

> `speckit.specify` và `speckit.plan` dùng template mặc định của spec-kit, chỉ override *cách hỏi/cách plan*, không override cấu trúc output.

## Cài đặt

Nội bộ (dev, từ thư mục này):

```bash
specify preset add --dev ./speckit-dft-mstem-preset
```

**Kích hoạt hiến chương (project mới chưa có hiến chương):** `preset add` không tự ghi vào file sống `.specify/memory/constitution.md` — nó chỉ đổi template. Copy hiến chương shipped vào memory để khung phỏng vấn có nội dung:

```bash
cp .specify/presets/dft-mstem/templates/constitution.md .specify/memory/constitution.md
```

Bỏ qua bước này nếu project đã có sẵn hiến chương phù hợp (vd admin_mbf).

Kiểm tra:

```bash
specify preset info dft-mstem       # xem 5 override (3 command + 2 template)
specify preset resolve spec-template      # spec-template = core mặc định (preset không override)
specify preset list
```

Gỡ:

```bash
specify preset remove dft-mstem
```

Từ GitHub release (sau khi publish):

```bash
specify preset add --from https://github.com/anhnt3/agent-skills/releases/download/dft-mstem-v2.7.0/dft-mstem-2.7.0.zip
```

## Publish (GitHub release zip)

Đóng gói + release giống `speckit-extension`:

```bash
./build-zip.sh                 # -> dist/dft-mstem-<version>.zip (đọc version từ preset.yml)
```

Release tự động: push tag `dft-mstem-v<version>` (khớp `preset.version` trong preset.yml) → workflow `.github/workflows/release-speckit-preset.yml` build zip + tạo GitHub Release kèm asset.

```bash
git tag dft-mstem-v1.0.0
git push origin dft-mstem-v1.0.0
```

Cài từ asset qua `specify preset add --from <url>`. Lưu ý: `--from` chỉ nhận HTTPS (hoặc localhost) — không nhận đường dẫn file local.

## Khi nào dùng / không dùng

- **Dùng**: chức năng có mockup + mock-service cần chuyển sang backend thật, dự án có `constitution.md` làm khung review.
- **Không dùng**: spec nhanh không cần phỏng vấn, hoặc dự án không có mockup/constitution.

## Yêu cầu

- `speckit_version >= 0.6.0` (cần AskUserQuestion trên Claude Code).
- Dự án đã `specify init`, có `.specify/memory/constitution.md` và một file roadmap (vị trí tùy dự án; command tự tìm, không rõ thì hỏi).
