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
| `speckit.dft-speckit.domain-design` | Thiết kế/cập nhật domain tổng thể cho 1 module trong roadmap, ghi `docs/domain/<module>.md`. |
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
│   └── domain-design.md
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
│   └── csv_to_xlsx.py         # CSV/JSON -> XLSX 2 sheet (tự dựng venv + openpyxl lần đầu)
├── templates/
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

### Tự động qua GitHub Actions (khuyến nghị)

Workflow [`.github/workflows/release-speckit-extension.yml`](../.github/workflows/release-speckit-extension.yml)
chạy khi push tag `dft-speckit-v<version>`, tự build zip và tạo GitHub Release kèm asset.

```bash
# 1. Cập nhật version trong extension.yml (vd 1.0.0) rồi commit.
# 2. Tag + push (version phải khớp extension.yml, nếu không workflow báo lỗi):
git tag dft-speckit-v1.0.0
git push origin dft-speckit-v1.0.0
```

Sau khi workflow xong, cài bằng:

```bash
specify extension add dft-speckit --force --from \
  https://github.com/anhnt3/agent-skills/releases/download/dft-speckit-v1.6.0/dft-speckit-1.6.0.zip
```

> Cũng có thể chạy tay qua tab **Actions → Release dft-speckit extension → Run workflow** và nhập version.

### Build zip thủ công (local)

```bash
speckit-extension/build-zip.sh          # đọc version từ extension.yml
speckit-extension/build-zip.sh 1.0.0    # hoặc chỉ định version
# -> speckit-extension/dist/dft-speckit-<version>.zip
```

Upload zip đó lên Release (hoặc host nội bộ) rồi dùng URL với `--from`.

## Định dạng cố định (Pha 4 của `qa-spec-cycle`)

CSV/JSON của testcase thủ công bắt buộc đúng **16 cột, đúng thứ tự** — script validate header cứng
(`EXPECTED_HEADER`) và raise lỗi nếu sai tên/thứ tự/số field:

```
ID | Tiêu đề | Nhóm | Ưu tiên | Loại | Tiền điều kiện | Dữ liệu test | Các bước thực hiện | Kết quả mong đợi | Truy vết | Test tự động | Kết quả tự động | Kết quả thực tế | Trạng thái | Bug ID | Ghi chú
```

Cột 1–11 = thiết kế (versioned); cột 12 (`Kết quả tự động`) = skill/CI ghi (chỉ-đọc với tester);
4 cột cuối (13–16) = thực thi (tester điền, để trống trong file nguồn). XLSX xuất ra **2 sheet**
(Testcases + Ma trận truy vết): header nền xanh, tô màu ưu tiên P1/P2/P3, dropdown Trạng thái,
freeze panes và auto-filter. Chi tiết đầy đủ: [`references/manual-xlsx-format.md`](references/manual-xlsx-format.md).

## Nguồn gốc

Migrate từ skill `.claude/skills/qa-spec-cycle` (giữ nguyên bản gốc). Command này thay thế command
`manual-xlsx` cũ — vòng QA đầy đủ bao trùm luôn phần sinh testcase thủ công ở Pha 4.
