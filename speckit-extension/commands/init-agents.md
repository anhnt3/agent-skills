---
description: Dò stack của project, chọn đúng agent phù hợp trong catalog DFT rồi cài vào `.claude/agents/` để /speckit.agent-assign.assign có agent mà gán vào task. Chỉ hỗ trợ integration claude.
---

# Init agents theo stack của project

Dò **stack thật** của project đang mở, lọc ra những agent phù hợp trong catalog dùng chung của DFT (ship kèm extension), rồi cài vào `.claude/agents/` để extension `agent-assign` có agent mà quét và gán cho từng task trong `tasks.md`.

Catalog chứa agent cho **nhiều stack** (ABP/.NET, Angular, và sẽ mở rộng). Một project ABP + Angular chỉ nên nhận `backend-abp` + `frontend-angular` — **không đổ cả catalog vào project**, vì `agent-assign` khớp task với agent bằng `description`; agent của stack không tồn tại chỉ làm nhiễu và khiến nó gán sai.

**Vì sao chỉ `.claude/agents/`**: `agent-assign` hardcode đường quét là `.claude/agents/*.md` rồi `~/.claude/agents/*.md` — nó KHÔNG đọc `.specify/init-options.json` và KHÔNG biết tới `.cursor/` hay `.agents/`. Đổ agent ra chỗ khác thì nó không thấy. Đây là giới hạn của `agent-assign`, không phải lựa chọn của command này.

## User Input

`$ARGUMENTS`

- **Trống** → dò stack tự động (đường đi chính).
- **Danh sách tên agent** (vd `backend-abp, frontend-angular`) → bỏ qua bước dò, cài đúng các agent đó. Dùng khi bạn biết rõ mình muốn gì, hoặc khi dò sai.
- Tên không khớp agent nào trong catalog → liệt kê tên có thật, hỏi lại. **Đừng đoán, đừng tự sửa tên.**

## Quy trình (bắt buộc theo thứ tự)

### 1. Chặn sai integration

Đọc `.specify/init-options.json`, lấy field `integration`.

- `integration` **khác** `claude` → **DỪNG**. Báo đúng nguyên nhân: *"Project này dùng integration `<giá trị>`. `agent-assign` chỉ quét `.claude/agents/`, nên cài agent vào đây sẽ không được nó nhận. Command này hiện chỉ hỗ trợ `claude`."* KHÔNG cài gì, KHÔNG tự đổ vào thư mục khác.
- File không tồn tại / không đọc được → **DỪNG** và báo. Đừng mặc định là `claude`.

### 2. Nạp catalog

Nguồn: `.specify/extensions/dft-speckit/agents/`.

- Thư mục không tồn tại / rỗng / thiếu `registry.yml` → **DỪNG** và báo: extension cài thiếu file (nhiều khả năng `build-zip.sh` chưa copy thư mục `agents/`). **KHÔNG bịa nội dung agent.**
- Đọc `registry.yml`. Với mỗi mục trong `agents:`, đọc file `.md` tương ứng, rút `name` + `description` từ frontmatter.

**Đối soát registry với thư mục** — hai chiều, báo cả hai:
- File `.md` có trong thư mục nhưng **không có** mục trong registry → **báo lỗi**, nêu đích danh tên file. Agent đó không dò được stack nên không được chọn. Đây là lỗi đóng gói, không phải chuyện để im lặng bỏ qua.
- Mục trong registry trỏ tới file `.md` **không tồn tại** → **báo lỗi**, nêu đích danh.

Agent thiếu `description` trong frontmatter → **báo lỗi và loại** — `agent-assign` dùng `description` để tự khớp agent với task; agent không có description là agent vô dụng.

### 3. Dò stack

**Gốc quét = thư mục gốc project** (thư mục chứa `.specify/`). Mọi glob/grep chạy từ đây.

Với mỗi agent trong registry, chạy khối `detect.any` của nó. Agent **khớp** nếu **bất kỳ** signal nào khớp:

- `glob: <pattern>` → tồn tại ít nhất 1 file khớp pattern **ở bất kỳ đâu trong cây, KỂ CẢ ngay thư mục gốc**.
- `grep: { in: <pattern>, pattern: <regex> }` → tồn tại ít nhất 1 file khớp `in` mà nội dung khớp `regex`.

**Ngữ nghĩa `**/`**: hiểu `**/` là **không-hoặc-nhiều** thư mục — pattern `**/*.abpsln` phải khớp cả `./mSTEM.Admin.abpsln` ở gốc lẫn file lồng sâu. **Đừng dùng globber "nghiêm"** (coi `**/` là "ít nhất một thư mục") — nó bỏ sót file ở gốc và dò trượt stack. An toàn nhất: quét theo **tên file ở mọi cấp** (như `find -name`), không phụ thuộc độ sâu.

**Luôn loại trừ** khi quét: `node_modules/`, `bin/`, `obj/`, `dist/`, `.git/`, `.venv/`. Quét trúng mấy chỗ này sẽ dò ra stack ma (vd thấy `@angular/core` trong `node_modules` của một dự án không dùng Angular).

**Ghi lại BẰNG CHỨNG cho mỗi agent khớp** — signal nào khớp, và **đường dẫn file cụ thể** đã làm nó khớp. Bằng chứng này phải hiện ra ở bước 4. Nói "khớp" mà không chỉ được file nào = coi như không khớp.

### 4. Trình bày và xác nhận

Hiện bảng kết quả dò, **kèm bằng chứng**:

```text
Stack dò được:

| Agent            | Stack               | Bằng chứng                              | Đích                                | Trạng thái            |
|------------------|---------------------|-----------------------------------------|-------------------------------------|-----------------------|
| backend-abp      | ABP Framework (.NET)| mSTEM.Admin.abpsln                      | .claude/agents/backend-abp.md       | Tạo mới               |
| frontend-angular | Angular             | angular/package.json: "@angular/core"   | .claude/agents/frontend-angular.md  | Đã có — nội dung khác |

Không khớp (không cài):

| Agent          | Stack       | Lý do                        |
|----------------|-------------|------------------------------|
| backend-spring *(minh họa — catalog hiện chưa có agent này)* | Spring Boot | không thấy pom.xml/build.gradle |
```

Cột **Trạng thái** xác định bằng cách so nội dung file nguồn với file đích (nếu đích đã tồn tại):
- Đích chưa có → `Tạo mới`
- Đích có, nội dung **giống hệt** → `Đã đồng bộ` (bỏ qua, không ghi lại)
- Đích có, nội dung **khác** → `Đã có — nội dung khác`

Dùng **AskUserQuestion** để xác nhận. Bảng "Không khớp" phải hiện ra để người dùng còn cơ hội nói "dò sai, tôi vẫn muốn cài cái này" — cho phép họ **thêm** agent mà bước dò đã loại, và **bỏ** agent mà bước dò đã chọn.

**Không nhận được xác nhận tường minh** (chạy trong ngữ cảnh tự động không có người thật, câu hỏi không trả lời được) → **DỪNG, KHÔNG ghi file**. Cấm suy diễn "chắc người dùng đồng ý rồi".

Nếu có agent ở trạng thái `Đã có — nội dung khác`, hỏi rõ: **Ghi đè** bằng bản nguồn, hay **Giữ nguyên** file đích. **TUYỆT ĐỐI KHÔNG ghi đè im lặng** — file trong `.claude/agents/` có thể do người dùng sửa tay.

**Không agent nào khớp** → **DỪNG**, hiện bảng "Không khớp" đầy đủ kèm lý do, và nói thẳng là chưa có agent nào trong catalog hợp với stack này. KHÔNG cài bừa một agent "gần đúng".

### 5. Ghi file

Tạo `.claude/agents/` nếu chưa có. Ghi từng agent đã được xác nhận vào `.claude/agents/<name>.md`, **nguyên văn nội dung file nguồn** (kể cả frontmatter). Không chỉnh sửa, không "cải thiện" prompt của agent, **không chèn thêm field nào** — Claude Code chỉ hiểu `name`/`description`/`tools`/`model`.

Tên file đích lấy từ `name` trong frontmatter, **không phải** tên file nguồn — vì `agent-assign` khớp theo `name`.

### 6. Báo cáo

```text
Đã cài <n>/<số agent khớp> agent vào .claude/agents/

| Agent            | Kết quả    |
|------------------|------------|
| backend-abp      | Tạo mới    |
| frontend-angular | Giữ nguyên |
```

Rồi nhắc bước tiếp: chạy `/speckit.agent-assign.assign` để gán agent vào task trong `tasks.md`. Điều kiện: đã có `tasks.md` (tức đã chạy `/speckit.tasks`) **và** extension `agent-assign` đã cài (kiểm `.specify/extensions/agent-assign/` — chưa có thì nhắc cài trước, đừng tiến cử một lệnh không tồn tại).

## Sai lầm thường gặp

- **Đổ cả catalog vào project** — agent của stack không tồn tại làm nhiễu bước tự-khớp của `agent-assign`, khiến nó gán task cho agent sai. Chỉ cài agent dò ra được.
- **Dò stack bằng cách "đọc description rồi suy luận"** — tín hiệu dò nằm ở `registry.yml`, phải chạy đúng `detect.any`. Suy luận từ description sẽ trôi và chọn sai.
- **Quét cả `node_modules/`, `bin/`, `obj/`** — dò ra stack ma. Luôn loại trừ.
- **Báo "khớp" mà không chỉ được file bằng chứng** — không có bằng chứng thì không phải phát hiện, đó là phỏng đoán.
- **Đổ agent vào `.cursor/agents/` hay `.agents/` khi thấy integration khác** — `agent-assign` không quét những chỗ đó, làm vậy chỉ tạo ảo giác đã xong. Gặp integration khác thì DỪNG.
- **Ghi đè file đích mà không hỏi** — mất công sửa tay của người dùng.
- **Im lặng bỏ qua file `.md` thiếu mục registry** — nó sẽ vĩnh viễn không bao giờ được cài, mà không ai biết. Phải báo lỗi.
