---
description: Dò stack của project, chọn đúng agent phù hợp trong catalog DFT rồi cài vào `.claude/agents/` của project. Chỉ hỗ trợ integration claude. Hỏi trước khi ghi đè.
---

# Init agents theo stack của project

Dò **stack thật** của project đang mở, lọc agent phù hợp trong catalog DFT (ship kèm extension), cài vào `.claude/agents/` để công cụ AI của project dùng.

Catalog có agent cho **nhiều stack** (ABP/.NET, Angular, sẽ mở rộng). Project ABP + Angular chỉ nhận `backend-abp` + `frontend-angular` — **không đổ cả catalog**; agent thừa của stack khác làm loãng và dễ chọn nhầm.

## User Input

`$ARGUMENTS`

- **Trống** → dò stack tự động (đường chính).
- **Danh sách tên agent** (vd `backend-abp, frontend-angular`) → bỏ qua bước dò, cài đúng các agent đó.
- Tên không khớp agent nào trong catalog → liệt kê tên có thật, hỏi lại. Đừng đoán, đừng tự sửa tên.

## Quy trình (theo thứ tự)

### 1. Chặn sai integration

Đọc `.specify/init-options.json`, lấy field `integration`.

- `integration` khác `claude` → **DỪNG**, báo: *"Command chỉ hỗ trợ integration `claude` (ghi agent vào `.claude/agents/`). Project dùng `<giá trị>`."* KHÔNG cài, KHÔNG đổ vào thư mục khác.
- File thiếu / không đọc được → **DỪNG**, báo. Đừng mặc định `claude`.

### 2. Nạp catalog

Nguồn: `.specify/extensions/dft-speckit/agents/`.

- Thư mục thiếu / rỗng / thiếu `registry.yml` → **DỪNG**, báo (nhiều khả năng `build-zip.sh` chưa copy `agents/`). Không bịa nội dung agent.
- Đọc `registry.yml`; với mỗi mục, đọc file `.md`, rút `name` + `description`.

Đối soát registry ↔ thư mục, báo cả hai chiều:
- File `.md` có nhưng thiếu mục registry → **báo lỗi**, nêu tên file (không dò được stack nên không được chọn).
- Mục registry trỏ file `.md` không tồn tại → **báo lỗi**, nêu tên.
- Agent thiếu `description` → **báo lỗi và loại**.

### 3. Dò stack

**Gốc quét = thư mục chứa `.specify/`.** Mọi glob/grep chạy từ đây.

Với mỗi agent, chạy `detect.any`. Khớp nếu **bất kỳ** signal nào khớp:
- `glob: <pattern>` → có ≥1 file khớp **ở bất kỳ đâu, KỂ CẢ thư mục gốc**.
- `grep: { in, pattern }` → có ≥1 file khớp `in` mà nội dung khớp `pattern`.

**`**/` = không-hoặc-nhiều thư mục**: `**/*.abpsln` phải khớp cả `./mSTEM.Admin.abpsln` ở gốc. Đừng dùng globber "nghiêm" (coi `**/` là "≥1 thư mục") — nó bỏ sót file gốc. An toàn nhất: quét theo tên file mọi cấp (như `find -name`).

**Luôn loại trừ**: `node_modules/`, `bin/`, `obj/`, `dist/`, `.git/`, `.venv/` (tránh dò stack ma).

**Ghi BẰNG CHỨNG cho mỗi agent khớp**: signal nào + đường dẫn file cụ thể. "Khớp" mà không chỉ được file = coi như không khớp.

### 4. Trình bày và xác nhận

Hiện bảng dò kèm bằng chứng:

```text
Stack dò được:
| Agent            | Stack               | Bằng chứng                            | Đích                               | Trạng thái            |
|------------------|---------------------|---------------------------------------|------------------------------------|-----------------------|
| backend-abp      | ABP Framework (.NET)| mSTEM.Admin.abpsln                    | .claude/agents/backend-abp.md      | Tạo mới               |
| frontend-angular | Angular             | angular/package.json: "@angular/core" | .claude/agents/frontend-angular.md | Đã có — nội dung khác |

Không khớp (không cài):
| Agent                                          | Stack       | Lý do                           |
|------------------------------------------------|-------------|---------------------------------|
| backend-spring *(minh họa — catalog chưa có)*  | Spring Boot | không thấy pom.xml/build.gradle |
```

Cột **Trạng thái** = so nội dung nguồn với đích: chưa có → `Tạo mới`; giống hệt → `Đã đồng bộ` (bỏ qua); khác → `Đã có — nội dung khác`.

Dùng **AskUserQuestion** để xác nhận. Bảng "Không khớp" phải hiện để người dùng còn **thêm** agent bị loại hoặc **bỏ** agent đã chọn.

- Có agent `Đã có — nội dung khác` → hỏi rõ **Ghi đè** hay **Giữ nguyên**. TUYỆT ĐỐI không ghi đè im lặng (file có thể do người dùng sửa tay).
- Không nhận được xác nhận tường minh (chạy tự động, không trả lời được) → **DỪNG, KHÔNG ghi file**. Cấm suy diễn "chắc đồng ý".
- Không agent nào khớp → **DỪNG**, hiện bảng "Không khớp" đầy đủ. Không cài bừa agent "gần đúng".

### 5. Ghi file

Tạo `.claude/agents/` nếu chưa có. Ghi mỗi agent đã xác nhận vào `.claude/agents/<name>.md`, **nguyên văn nội dung nguồn** (kể cả frontmatter). Không sửa, không chèn field.

Tên file đích = `name` trong frontmatter (không phải tên file nguồn).

### 6. Báo cáo

```text
Đã cài <n>/<số agent khớp> agent vào .claude/agents/
| Agent            | Kết quả    |
|------------------|------------|
| backend-abp      | Tạo mới    |
| frontend-angular | Giữ nguyên |
```

## Sai lầm thường gặp

- **Đổ cả catalog** — agent thừa của stack khác gây chọn nhầm. Chỉ cài agent dò ra được.
- **Dò bằng "đọc description rồi suy luận"** — tín hiệu ở `registry.yml`, phải chạy đúng `detect.any`.
- **Quét cả `node_modules/`, `bin/`, `obj/`** — dò ra stack ma.
- **Báo "khớp" không có file bằng chứng** — đó là phỏng đoán, không phải phát hiện.
- **Ghi agent vào `.cursor/` hay `.agents/` khi integration khác** — command chỉ ghi `.claude/agents/`; integration khác → DỪNG.
- **Ghi đè đích mà không hỏi** — mất công sửa tay người dùng.
- **Im lặng bỏ qua file `.md` thiếu mục registry** — nó vĩnh viễn không được cài. Phải báo lỗi.
