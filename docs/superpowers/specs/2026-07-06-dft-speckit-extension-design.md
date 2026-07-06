# dft-speckit extension — Migrate manual-testcase-xlsx thành command

Ngày: 2026-07-06

## Mục tiêu
Tạo mới một spec-kit extension tại `speckit-extension/` và migrate skill
`.claude/skills/manual-testcase-xlsx` thành một command của extension. Giữ nguyên
skill gốc (không xoá).

## Quyết định
- Extension id: `dft-speckit`; command: `speckit.dft-speckit.manual-xlsx`.
- Không copy `.venv` vào extension; script `csv_to_xlsx.py` tự dựng venv lần đầu.
  Loại `.venv`/`__pycache__` qua `.extensionignore`.
- Metadata: author `Nguyen Tuan Anh`, license `MIT`, repository placeholder repo agent-skills.
- Giữ nguyên skill gốc để dùng song song.

## Cấu trúc
```
speckit-extension/
├── extension.yml              # manifest schema_version 1.0
├── commands/
│   └── manual-xlsx.md         # nội dung quy trình từ SKILL.md
├── scripts/
│   └── csv_to_xlsx.py         # copy nguyên từ skill gốc
├── .extensionignore
└── README.md
```

## Nội dung command
Chuyển toàn bộ quy trình SKILL.md: frontmatter `description`, `## User Input`
với `$ARGUMENTS` (đường dẫn spec/feature), quy trình 4 bước, 14 cột cố định,
quy tắc chất lượng, Verification. Lệnh chạy trỏ tới `scripts/csv_to_xlsx.py` trong
extension.

## Giả định
Tài liệu spec-kit chỉ mô tả bundle script chuẩn cho `.sh`/`.ps1`. Script này là
Python nên KHÔNG dùng cơ chế rewrite `{SCRIPT}`; command trỏ trực tiếp tới đường
dẫn `scripts/csv_to_xlsx.py` của extension.

## Verification
- `extension.yml` hợp lệ (id đúng pattern `^[a-z0-9-]+$`, command đúng pattern
  `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`).
- Script chạy được: sinh XLSX từ CSV mẫu 14 cột.
- Skill gốc còn nguyên.
