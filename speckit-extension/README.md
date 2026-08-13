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
| `speckit.dft-speckit.fnlist-import` | **Reverse tài liệu — bước 1/3.** Nhập function list (`.xlsx`/`.csv`) đã dùng nghiệm thu thành `.specify/docs/functions.json` — cây chức năng, `FN-ID` đa cấp ổn định. Script chép nguyên văn, LLM chỉ quyết ánh xạ cột. Ghi đè tại chỗ (không ai sửa tay file này); chạy lại giữ ID cũ theo đường dẫn tên và trình `diff`. |
| `speckit.dft-speckit.code-intel` | **Reverse tài liệu — bước 2/3.** Rút đặc tả đủ sâu từ codebase theo cây `functions.json`. Tham số là **một FN-ID** đánh dấu điểm bắt đầu quét (trống = toàn dự án); tự đề xuất unit theo luật cha-trực-tiếp-của-lá, xác nhận qua cây thụt lề, rồi quét (hỏi song song/tuần tự khi có nhiều unit). Ghi `.specify/docs/<đường-dẫn-cây>/intel.md` — tài liệu nội bộ, mọi khẳng định kèm nguồn `file:dòng`. |
| `speckit.dft-speckit.srs-from-code` | **Reverse tài liệu — bước 3/3.** Sinh `.specify/docs/<đường-dẫn-cây>/srs.md` theo đúng cấu trúc 4 cấp cố định của tài liệu ban hành thật (`Nhóm → Chức năng → Sơ đồ/Mục đích/Mô tả chức năng → Màn hình → a.-g.`) từ `intel.md` — tài liệu giao khách, không lộ đường dẫn mã nguồn, chỉ chứa nội dung phản ánh đúng những gì code làm. Thông tin hành chính thiếu ghi thẳng "Chưa có thông tin", không hỏi. Phát hiện logic mâu thuẫn/lỗ hổng bảo mật thì tổng hợp một lượt cuối khi báo cáo, không rót vào tài liệu. Chốt bằng cổng `srs_verify.py`: FN thiếu mặt trong comment ẩn `<!-- FN: ... -->` hoặc còn placeholder là cấm báo xong. Không còn cờ `--template` — khung cố định, không tuỳ biến theo khách. |
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
│   ├── brd-import.md          # bẻ BRD .docx lớn thành cây markdown docs/brd/
│   ├── fnlist-import.md       # reverse 1/3: function list -> .specify/docs/functions.json
│   ├── code-intel.md          # reverse 2/3: codebase -> .specify/docs/<đường-dẫn-cây>/intel.md
│   └── srs-from-code.md       # reverse 3/3: intel.md -> .specify/docs/<đường-dẫn-cây>/srs.md
├── agents/                    # catalog agent DFT (nguồn cho init-agents)
│   ├── registry.yml           # tín hiệu dò stack (glob/grep) — nhà duy nhất
│   ├── backend-abp.md         # agent ABP/.NET (kèm cổng Quy ước chung)
│   └── frontend-angular.md    # agent Angular (kèm cổng Quy ước chung)
├── references/                # tài liệu chi tiết từng pha của qa-spec-cycle + schema functions.json
│   ├── qa-context-template.md
│   ├── coverage-matrix.md
│   ├── manual-xlsx-format.md
│   ├── test-generation.md
│   ├── quality-gate.md
│   ├── environment-bringup.md
│   ├── blocker-playbook.md
│   ├── failure-classification.md
│   ├── traceability.md
│   └── functions-schema.md    # schema functions.json (hợp đồng dữ liệu, đọc trước khi chạy fnlist-import)
├── scripts/                   # script hỗ trợ dùng chung cho các command
│   ├── csv_to_xlsx.py         # CSV/JSON -> XLSX 2 sheet (tự dựng venv + openpyxl lần đầu)
│   ├── brd_import.py          # CLI probe|split cho brd-import
│   ├── brd_roadmap.py         # CLI manifest|outline|verify cho road-map-from-brd
│   ├── promote_headings.lua   # Lua filter cho pandoc (bậc dò 2-4)
│   ├── brd/                   # engine brd-import (naming/outline/convert/docx_probe/splitter/verify)
│   ├── fnlist_import.py       # CLI inspect|write|update cho fnlist-import
│   ├── fnlist_tree.py         # logic dựng cây/cấp ID/diff cho fnlist-import (thuần, không I/O)
│   └── srs_verify.py          # cổng nghiệm thu cho srs-from-code (blocking + warnings)
├── templates/                 # khung output cố định (resolve qua `specify preset resolve <tên>`)
│   ├── roadmap-template.md    # khung docs/roadmap.md cho road-map-from-codebase và road-map-from-brd
│   ├── domain-template.md     # khung docs/domain/<cụm>.md cho domain-design
│   ├── intel-template.md      # khung .specify/docs/<cụm>/intel.md (nội bộ, giữ file:dòng)
│   └── srs-template.md        # khung .specify/docs/<cụm>/srs.md (giao khách, khung ban hành mặc định)
├── LICENSE
└── README.md
```

## Reverse tài liệu từ codebase

Dành cho dự án đã code/test xong theo function list dùng nghiệm thu, nhưng chưa có SRS
chính thức. Ba command chạy theo thứ tự, mỗi bước để lại một file trên đĩa để review
trước khi đi tiếp:

```
function list .xlsx/.csv ──▶ /speckit.dft-speckit.fnlist-import
                               └─▶ .specify/docs/functions.json

codebase + functions.json ──▶ /speckit.dft-speckit.code-intel [FN-ID]
                               └─▶ .specify/docs/<đường-dẫn-cây>/intel.md

intel.md + functions.json ──▶ /speckit.dft-speckit.srs-from-code <đường-dẫn-cây>
                               └─▶ .specify/docs/<đường-dẫn-cây>/srs.md
```

`[FN-ID]` là điểm bắt đầu quét — trống thì quét toàn cây; `code-intel` tự đề xuất ranh giới
unit theo cấu trúc `functions.json` (node có tất cả con đều là lá, hoặc node không con đứng
một mình), người dùng xác nhận qua cây thụt lề trước khi quét. Không còn khái niệm "cụm gõ
tay" — thư mục output sinh tự động từ cây (đánh số + slug tất định), không phải chuỗi tự do
người dùng gõ.

```
.specify/docs/
├── functions.json             # cây chức năng đã import, FN-ID đa cấp ổn định, dùng chung toàn cây
├── 01-xac-thuc/
│   ├── 01-dang-nhap/
│   │   ├── intel.md           # nội bộ — mọi khẳng định kèm nguồn file:dòng
│   │   └── srs.md             # giao khách — đúng khung ban hành, không lộ đường dẫn code
│   └── <unit khác trong nhánh>/
└── <nhánh khác>/
```

`functions.json` là cây (không phải bảng), ghi đè tại chỗ ở mỗi lần chạy lại — không có
cơ chế `.new`/no-clobber, vì không ai sửa tay file này: ID cũ giữ theo đường dẫn tên,
`status` do `code-intel`/`srs-from-code` ghi cũng được chép sang bản mới. Schema đầy đủ:
[`references/functions-schema.md`](references/functions-schema.md).

**`intel.md` (nội bộ) khác `srs.md` (giao khách)** — đây là ranh giới quan trọng nhất
của cả đường ống. `code-intel` phân loại mỗi khẳng định thành ba dạng: đọc thẳng từ code
(kèm `file:dòng`), suy đoán (kèm `file:dòng` gần nhất + đánh dấu), hoặc không có căn cứ
(xuống mục câu hỏi, gắn nhãn loại). Riêng phát hiện logic mâu thuẫn hoặc dấu hiệu lỗ hổng
bảo mật thấy được trong lúc rút thì ghi vào một mục riêng (§10) — khác "không biết" ở
§8, đây là "đã thấy và thấy có vấn đề". `srs-from-code` rót từ `intel.md` sang, bỏ hết
đường dẫn mã nguồn.

**Không hỏi trong lúc sinh, tài liệu chỉ chứa nội dung chắc chắn** — `srs-from-code` mô
tả đúng những gì code làm; thông tin hành chính/nghiệp vụ thuần mà code không thể tiết lộ
(người ký duyệt, chính sách chỉ người mới biết…) ghi thẳng "Chưa có thông tin", không
đánh dấu, không dừng lại hỏi. Phát hiện ở `intel §10` **không rót vào `srs.md`** — tổng
hợp một lượt duy nhất ở cuối báo cáo, hỏi người dùng: cố ý thiết kế vậy hay là bug. Ngoại
lệ riêng ở mục Đặc tả dữ liệu (bảng QA dùng làm chuẩn test biên): ràng buộc chỉ suy đoán
được thì để trống, không viết gì — sai một ràng buộc ở đây nguy hiểm hơn một ô trống.

**Cổng nghiệm thu** — `srs_verify.py` chấm `srs.md` trước khi cho phép báo xong, chỉ chặn
cứng hai thứ kiểm được tất định: FN-ID trong phạm vi thiếu mặt trong mọi comment ẩn
`<!-- FN: ... -->`, và placeholder `[…]` còn sót. Mọi thứ cần phán đoán (đường dẫn code
nghi lọt vào tài liệu giao khách, Chức năng/Màn hình thiếu mục con, mục để trống) chỉ
cảnh báo, không chặn.

Ví dụ chạy đầy đủ:

```bash
/speckit.dft-speckit.fnlist-import refs/function-list.xlsx
/speckit.dft-speckit.code-intel FN-01        # hoặc để trống để quét toàn dự án
/speckit.dft-speckit.srs-from-code FN-01     # hoặc để trống để sinh cho toàn cây
```

Chạy thử `srs_verify.py` độc lập (không qua command) — tham số là FN-ID gốc của phạm vi
đang kiểm (`--root`, rỗng = toàn cây):

```bash
python speckit-extension/scripts/srs_verify.py \
  .specify/docs/01-xac-thuc/01-dang-nhap/srs.md \
  --functions .specify/docs/functions.json \
  --root FN-01-01
```

Ngoài phạm vi hiện tại: BRD, ADD (Architecture Design Document), User Manual. Chúng dùng
lại được `intel.md` (không quét code lại từ đầu) nhưng mỗi loại cần một khung riêng —
sẽ thêm dần theo nhu cầu.

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
  https://github.com/anhnt3/agent-skills/releases/download/dft-speckit-v0.0.5/dft-speckit-0.0.5.zip
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

CSV/JSON của testcase thủ công bắt buộc đúng **16 cột, đúng thứ tự** — script validate header cứng
(`EXPECTED_HEADER`) và raise lỗi nếu sai tên/thứ tự/số field:

```
ID | Tiêu đề | Nhóm | Ưu tiên | Loại | Tiền điều kiện | Dữ liệu test | Các bước thực hiện | Kết quả mong đợi | Truy vết | Test tự động | Kết quả tự động | Kết quả thực tế | Trạng thái | Bug ID | Ghi chú
```

Cột 1–11 = thiết kế (versioned); cột 12 (`Kết quả tự động`) = command/CI ghi (chỉ-đọc với tester);
4 cột cuối (13–16) = thực thi (tester điền, để trống trong file nguồn). XLSX xuất ra **2 sheet**
(Testcases + Ma trận truy vết): header nền xanh, tô màu ưu tiên P1/P2/P3, dropdown Trạng thái,
freeze panes và auto-filter. Chi tiết đầy đủ: [`references/manual-xlsx-format.md`](references/manual-xlsx-format.md).

## Nguồn gốc

Migrate từ skill `.claude/skills/qa-spec-cycle` (giữ nguyên bản gốc). Command này thay thế command
`manual-xlsx` cũ — vòng QA đầy đủ bao trùm luôn phần sinh testcase thủ công ở Pha 4.
