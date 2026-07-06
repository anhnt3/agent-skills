# DFT mSTEM — Spec Kit Preset

Override `/speckit.specify` thành một phiên business-analyst phỏng vấn tuần tự trước khi ghi spec, và ép spec output điền đủ 11 nguyên tắc hiến chương.

## Preset này làm gì

Hai override bổ trợ nhau:

**1. Command `speckit.specify`** (`strategy: wrap`) — điều khiển *cách hỏi*:
- Đóng vai **business analyst** theo domain dự án, thảo luận + spec bằng **tiếng Việt**.
- **Khảo sát trước khi hỏi**: đọc `docs/roadmap.md`, mockup frontend (field/validation/luồng/label/message), nợ kỹ thuật liên quan, và `.specify/memory/constitution.md`.
- **Phỏng vấn theo cây thiết kế**: mỗi nguyên tắc trong `constitution.md` là một nhánh; hỏi qua **AskUserQuestion**, mỗi lần một câu, 2–4 option, có `(Recommended)` + lý do + trade-off.
- Bắt buộc rà **wire mock→backend** trên mọi màn (trừ trivial).
- Đánh dấu nguồn mỗi kết luận: `[từ mock]` / `[suy luận]` / `[cần bạn quyết]`.
- **Chỉ ghi spec sau khi bạn xác nhận** đạt hiểu chung. Phần scaffolding core (tạo `specs/<n>-<name>/spec.md`, quality checklist, hooks) kéo vào qua `{CORE_TEMPLATE}` — luôn đồng bộ bản core.

**2. Template `spec-template`** (`strategy: append`) — ép *spec output có gì (mặt WHAT)*:
- Mục **Tuân thủ Hiến chương — Nghiệp vụ**: chỉ mặt business-rule/hành vi của các nguyên tắc I/IV/V/VI/VII/X/XI (điền hoặc `N/A vì...`).
- Bảng **wire mock→backend theo màn**.

**3. Template `plan-template`** (`strategy: append`) — ép *cổng kỹ thuật (mặt HOW)*:
- Mục **Constitution Check — Kỹ thuật** (GATE trước Phase 0): nhóm HOW II/III/VIII/IX + cơ chế của I/V/VI/X/XI (test, versioning, observability, Keycloak/JWT, rowversion/DB constraint, ABP multi-tenancy).

**4. Template `constitution-template`** (`strategy: replace`) — *ship hiến chương*:
- Chứa nguyên văn 11 nguyên tắc (Angular mockup → backend ABP). Addendum spec/plan tham chiếu đúng bộ này, nên preset **tự chứa luật** — dùng được cho project mới không có sẵn hiến chương.

**5. Command `speckit.checklist`** (`strategy: wrap`) + **template `ui-ux-checklist`** — *bộ checklist cố định*:
- `/speckit.checklist ui-ux` (hoặc args nhắc `convention`/`IV`) → **copy nguyên bộ IV cố định** (CHK001–010) vào `checklists/ui-ux.md`, giống hệt mỗi lần (không sinh động).
- Args khác → chạy checklist sinh động của core như thường.
- Là spec-completeness gate cho nguyên tắc IV: bổ trợ spec-addendum (addendum *điền* UX theo màn, checklist *gate* đã điền đủ chưa).

> Tách WHAT (spec) vs HOW (plan) theo đúng triết lý spec-kit: spec cho business đọc, plan gánh kỹ thuật. Constitution Check gate sống ở plan (đúng như constitution quy định).

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
specify preset info dft-mstem       # xem 6 override (2 command + 4 template)
specify preset resolve spec-template      # thấy composition chain: core → addendum
specify preset list
```

Gỡ:

```bash
specify preset remove dft-mstem
```

Từ GitHub release (sau khi publish):

```bash
specify preset add --from https://github.com/anhnt3/agent-skills/releases/download/dft-mstem-v1.3.0/dft-mstem-1.3.0.zip
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
- Dự án đã `specify init`, có `docs/roadmap.md` và `.specify/memory/constitution.md`.
