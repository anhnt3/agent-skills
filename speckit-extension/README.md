# dft-speckit — Spec Kit Extension dùng chung của DFT

Extension **nội bộ dùng chung** của DFT cho [Spec Kit](https://github.github.io/spec-kit/):
một nơi tập hợp các command hỗ trợ quy trình spec-driven development của công ty. Đây là
extension **đa command, mở rộng dần** — command đầu tiên là sinh testcase thủ công, và sẽ
bổ sung thêm command mới theo nhu cầu.

## Danh sách command

| Command | Mô tả |
|---------|-------|
| `speckit.dft-speckit.manual-xlsx` | Sinh testcase kiểm thử **thủ công** cho tester từ spec/acceptance criteria, xuất CSV rồi XLSX (cấu trúc cột và format cố định). Alias: `speckit.dft-speckit.manual-testcase`. |
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
│   └── manual-xlsx.md
├── scripts/                   # script hỗ trợ dùng chung cho các command
│   └── csv_to_xlsx.py         # CSV -> XLSX (tự dựng venv + openpyxl lần đầu)
├── .extensionignore
└── README.md
```

## Cài đặt (local dev)

Yêu cầu một project đã `specify init`.

```bash
specify extension add --dev /đường/dẫn/tới/speckit-extension
specify extension list
```

Sau khi cài, command khả dụng trong AI agent qua `/speckit.dft-speckit.manual-xlsx`.

## Chạy script trực tiếp (không qua specify)

```bash
python3 speckit-extension/scripts/csv_to_xlsx.py \
  specs/<feature>/testcases-manual.csv \
  specs/<feature>/testcases-manual.xlsx --sheet "<Tên feature>"
```

Chỉ cần `python3` — script tự dựng `.venv` + cài `openpyxl` ở lần chạy đầu.

## Định dạng cố định

CSV bắt buộc đúng **14 cột, đúng thứ tự**:

```
ID | Tiêu đề | Nhóm | Ưu tiên | Loại | Tiền điều kiện | Dữ liệu test | Các bước thực hiện | Kết quả mong đợi | Truy vết | Kết quả thực tế | Trạng thái | Bug ID | Ghi chú
```

10 cột đầu = thiết kế (versioned); 4 cột cuối = thực thi (tester điền, để trống trong
file nguồn). XLSX xuất ra có header nền xanh, tô màu ưu tiên P1/P2/P3, dropdown Trạng
thái, freeze panes và auto-filter.

## Nguồn gốc

Migrate từ skill `.claude/skills/manual-testcase-xlsx` (giữ nguyên bản gốc).
