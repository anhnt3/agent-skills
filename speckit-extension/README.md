# dft-speckit — Spec Kit Extension dùng chung của DFT

Extension **nội bộ dùng chung** của DFT cho [Spec Kit](https://github.github.io/spec-kit/):
một nơi tập hợp các command hỗ trợ quy trình spec-driven development của công ty. Đây là
extension **đa command, mở rộng dần** — command đầu tiên là sinh testcase thủ công, và sẽ
bổ sung thêm command mới theo nhu cầu.

## Danh sách command

| Command | Mô tả |
|---------|-------|
| `speckit.dft-speckit.qa-spec-cycle` | **QA trọn vòng từ 1 file spec** — 13 pha: sinh testcase thủ công (xlsx 2 sheet), sinh test tự động theo pyramid, tự dựng môi trường và chạy, báo cáo, triage + fix có kiểm soát, ghi ma trận truy vết. Technology-agnostic (đặc thù stack đọc từ `.agents/qa-context.md`). Bao trùm luôn command `manual-xlsx` cũ ở Pha 4. |
| `speckit.dft-speckit.road-map-from-codebase` | Lập/cập nhật roadmap build từ codebase — xếp thứ tự từng màn, ghi `docs/roadmap.md`. |
| `speckit.dft-speckit.road-map-from-brd` | Lập roadmap build từ cây BRD markdown `docs/brd/` — phủ 1-1 node BRD ↔ item, gác cổng bằng script. |
| `speckit.dft-speckit.domain-design` | Thiết kế/cập nhật domain tổng thể cho một cụm chức năng — nhận **danh sách `RM-xxx`** trong roadmap (gom 1 doc), ghi `docs/domain/<cụm>.md`. RM đã design thì mở rộng doc cũ. |
| `speckit.dft-speckit.init-agents` | Dò stack thật của project (tín hiệu glob/grep khai trong `agents/registry.yml`, có bằng chứng file), lọc đúng agent trong catalog DFT rồi cài vào `.claude/agents/` để `/speckit.agent-assign.assign` có agent mà gán vào task. Chỉ hỗ trợ integration `claude`. Hỏi trước khi ghi đè. |
| `speckit.dft-speckit.brd-import` | Bẻ một file BRD `.docx` lớn thành cây markdown nhỏ phản chiếu navigation pane của Word — mỗi mục ở cấp đã chọn là một file, kèm `brd.manifest.yml`, `media/` và `reference.docx`. Dò cấu trúc 6 bậc (Heading style → style tự chế có `outlineLvl` → mục lục → đánh số gõ tay → cỡ chữ → LLM phán đoán); LLM chỉ quyết ranh giới, script chép nguyên văn. Kiểm chứng bằng ghép ngược byte-for-byte. Chạy lại khi đã có `docs/brd/` thì xuất ra `docs/brd.new/` kèm bảng khác biệt, không đè lên bản BA đã sửa tay. Ví dụ: `/speckit.dft-speckit.brd-import refs/BRD-khach-hang.docx` |
| _(sắp có)_ | Các command DFT khác sẽ được thêm vào đây. |

## Thêm command mới

1. Tạo file `commands/<tên>.md` (frontmatter `description` + nội dung quy trình).
2. Khai báo command trong `extension.yml` dưới `provides.commands` theo pattern
   `speckit.dft-speckit.<tên>`.
3. Nếu cần script hỗ trợ, đặt trong `scripts/`.

## Cấu trúc

```
speckit-extension/
├── extension.yml              # manifest (khai báo mọi command)
├── commands/                  # mỗi file .md = 1 command
│   ├── qa-spec-cycle.md       # QA trọn vòng 13 pha từ 1 spec
│   ├── road-map-from-codebase.md
│   ├── road-map-from-brd.md   # roadmap từ cây BRD docs/brd/
│   ├── domain-design.md
│   ├── init-agents.md         # dò stack, cài agent DFT vào .claude/agents/
│   └── brd-import.md          # bẻ BRD .docx lớn thành cây markdown docs/brd/
├── agents/                    # catalog agent DFT (nguồn cho init-agents)
│   ├── registry.yml           # tín hiệu dò stack (glob/grep) — nhà duy nhất
│   ├── backend-abp.md         # agent ABP/.NET (kèm cổng Quy ước chung)
│   └── frontend-angular.md    # agent Angular (kèm cổng Quy ước chung)
├── references/                # tài liệu chi tiết từng pha của qa-spec-cycle
│   ├── qa-context-template.md
│   ├── coverage-matrix.md
│   ├── manual-xlsx-format.md
│   ├── test-generation.md
│   ├── quality-gate.md
│   ├── environment-bringup.md
│   ├── blocker-playbook.md
│   ├── failure-classification.md
│   └── traceability.md
├── scripts/                   # script hỗ trợ dùng chung cho các command
│   ├── csv_to_xlsx.py         # CSV/JSON -> XLSX 2 sheet (tự dựng venv + openpyxl lần đầu)
│   ├── brd_import.py          # CLI probe|split cho brd-import
│   ├── brd_roadmap.py         # CLI manifest|outline|verify cho road-map-from-brd
│   ├── promote_headings.lua   # Lua filter cho pandoc (bậc dò 2-4)
│   └── brd/                   # engine brd-import (naming/outline/convert/docx_probe/splitter/verify)
├── templates/                 # khung output cố định (resolve qua `specify preset resolve <tên>`)
│   ├── roadmap-template.md    # khung docs/roadmap.md cho road-map-from-codebase và road-map-from-brd
│   └── domain-template.md     # khung docs/domain/<cụm>.md cho domain-design
├── LICENSE
└── README.md
```

## Cài đặt (local dev)

Yêu cầu một project đã `specify init`.

```bash
specify extension add dft-speckit --force --dev /đường/dẫn/tới/speckit-extension
specify extension list
```

Sau khi cài, command khả dụng trong AI agent qua `/speckit.dft-speckit.qa-spec-cycle`.

## Chạy script trực tiếp (không qua specify)

```bash
python3 speckit-extension/scripts/csv_to_xlsx.py \
  specs/<feature>/testcases-manual.csv \
  specs/<feature>/testcases-manual.xlsx --sheet "<Tên feature>"
```

Chỉ cần `python3` — script tự dựng `.venv` + cài `openpyxl` ở lần chạy đầu.

## Phát hành (release lên GitHub)

Cài qua `specify extension add dft-speckit --force --from <url>` yêu cầu URL trỏ tới **file zip** chứa
extension (thư mục gốc `dft-speckit/` có `extension.yml` bên trong).

### Release thủ công qua `release.sh` (đường duy nhất, chủ đích)

```bash
# 1. Bump version trong extension.yml (tăng đơn điệu từ baseline 0.0.1) rồi commit.
# 2. Chạy (yêu cầu `gh auth login`):
speckit-extension/release.sh            # build zip -> tạo/cập nhật Release + upload asset + cập nhật URL README
```

Sau khi release xong, cài bằng:

```bash
specify extension add dft-speckit --force --from \
  https://github.com/anhnt3/agent-skills/releases/download/dft-speckit-v0.2.0/dft-speckit-0.2.0.zip
```

### Build zip riêng lẻ (không release)

```bash
speckit-extension/build-zip.sh          # đọc version từ extension.yml
speckit-extension/build-zip.sh 1.0.0    # hoặc chỉ định version
# -> speckit-extension/dist/dft-speckit-<version>.zip
```

Upload zip đó lên Release (hoặc host nội bộ) rồi dùng URL với `--from`. Lưu ý: `--from` không verify
sha256 — trade-off đã chấp nhận của kênh phân phối này.

## Định dạng cố định (Pha 4 của `qa-spec-cycle`)

CSV/JSON của testcase thủ công bắt buộc đúng **17 cột, đúng thứ tự** — script validate header cứng
(`EXPECTED_HEADER`) và raise lỗi nếu sai tên/thứ tự/số field:

```
ID | Tiêu đề | Nhóm | Ưu tiên | Loại | Tiền điều kiện | Dữ liệu test | Các bước thực hiện | Kết quả mong đợi | Truy vết | Test tự động | Kết quả tự động | Kết quả thực tế | Trạng thái | Bug ID | Ghi chú | Nguồn BRD
```

Cột 1–11 = thiết kế (versioned); cột 12 (`Kết quả tự động`) = command/CI ghi (chỉ-đọc với tester);
cột 13–16 = thực thi (tester điền, để trống trong file nguồn); **cột 17 `Nguồn BRD`** = một trong bốn (giá trị thứ hai mang hậu tố ` (SPEC)` để phân biệt nội dung BA viết với nội dung `/speckit.specify` chiếu sang):
`docs/brd/…md#<mục>` (truy về mục **BA viết** — command lần theo trường `Nguồn` của item roadmap, không
đoán tên file) · `docs/brd/…md#<mục> (SPEC)` (truy về mục do `/speckit.specify` **chèn thêm** — `Từ điển dữ liệu`,
`Tiêu chí chấp nhận`, `Chất lượng phi chức năng`…; mục vốn có của BA không mang hậu tố) · `QUCTHT §<n>` (case sinh từ đối chiếu quy ước chung) ·
`N/A`. Script từ chối cột 17 trống. Cột 17 nằm **sau** vùng tester là cố ý: cột 13–16 giữ nguyên
vị trí nên merge dữ liệu tester không đổi và file xlsx cũ 16 cột vẫn đọc đúng.

XLSX xuất ra **2 sheet** (Testcases + Ma trận truy vết): header nền xanh, tô màu ưu tiên P1/P2/P3,
dropdown Trạng thái, freeze panes và auto-filter.

**Chống hỏng dữ liệu tester** — `ID` là khóa merge, hai cổng đều **không ghi file** và thoát ≠ 0:

| Exit | Ca | Cờ mở (chỉ người dùng bật) |
|---|---|---|
| `2` | ID cũ có dữ liệu tester **biến mất** khỏi input mới | `--allow-id-loss` |
| `3` | ID **giữ nguyên** nhưng Tiêu đề đổi trong khi tester đã chấm → kết quả bị gắn sang case khác, im lặng | `--allow-content-shift` |

Quy tắc tránh cả hai: case mới **cấp số ở cuối**, không chèn vào giữa rồi đánh số lại; bỏ case thì để
trống số đó. Chi tiết đầy đủ: [`references/manual-xlsx-format.md`](references/manual-xlsx-format.md).

## Nguồn gốc

Migrate từ skill `.claude/skills/qa-spec-cycle` (giữ nguyên bản gốc). Command này thay thế command
`manual-xlsx` cũ — vòng QA đầy đủ bao trùm luôn phần sinh testcase thủ công ở Pha 4.
