# DFT Spec Kit Preset

Override `/speckit.constitution` thành phiên soạn hiến chương từ codebase + phỏng vấn, và `/speckit.specify` thành phiên business-analyst phỏng vấn tuần tự trước khi ghi spec.

## Preset này làm gì

Các override bổ trợ nhau (5 override, gom theo mục đích):

**0. Command `speckit.constitution`** (`strategy: wrap`) — *sinh hiến chương dùng được cho máy*:
- **Giáo dục trước, hỏi sau**: giải thích cơ chế thật — `analyze`/`converge` chỉ bốc *tên nguyên tắc* + *các câu chứa `MUST`/`SHOULD`* thành rule set. Nguyên tắc không có từ chuẩn tắc là **nguyên tắc vô hình**.
- **Làn A — quét codebase**: rút các luật dự án ĐANG cưỡng chế (cổng test, lint, phân lớp, hợp đồng API, secret/auth, migration, dependency). Mỗi luật **bắt buộc nêu nguồn**; không nêu được nguồn thì đó là mong muốn, không phải luật đang thực thi.
- **Làn B — phỏng vấn** (tối đa 3–4 lượt AskUserQuestion): chỉ hỏi thứ code không trả lời được — điều tuyệt đối không được xảy ra, sự cố đau nhất từng gặp, ràng buộc pháp lý.
- **Hợp nhất**: bảng đối chiếu hai làn, mỗi dòng chốt một trong bốn: `MUST` · `MUST + miễn trừ` · `→ Ràng buộc Kiến trúc` · `Bỏ`. **Ngân sách 5 nguyên tắc, trần cứng 7.**
- **`MUST + miễn trừ`** dành cho luật đúng mà code cũ chưa đạt: giữ lực `MUST` cho code mới, đồng thời ghi vùng miễn trừ vào mục `Phạm vi áp dụng` — nếu không, `/speckit.converge` sẽ sinh task khắc phục cho toàn bộ code cũ.
- **Cổng tự kiểm chặn cứng** trước khi giao core: mỗi nguyên tắc ≥1 `MUST`/`MUST NOT`, có `**Rationale:**`, ≤7 nguyên tắc, không còn placeholder `[ALL_CAPS]`.
- **Ngôn ngữ lai**: văn xuôi tiếng Việt, nhưng token chuẩn tắc viết `MUST`/`MUST NOT`/`SHOULD` in hoa — đó là chuỗi mà `analyze`/`converge` khớp; chúng không biết `PHẢI`.
- Core lo phần còn lại qua `{CORE_TEMPLATE}`: semver, Sync Impact Report, checklist lan truyền, extension hooks.
- Chạy được cả **greenfield** (không có code → làn A suy giảm, nói rõ với người dùng) lẫn **brownfield**, và phân biệt **phê chuẩn lần đầu** với **sửa đổi** (chỉ đi tìm phần chênh, không viết lại từ đầu).

**1. Command `speckit.specify`** (`strategy: wrap`) — điều khiển *cách hỏi*:
- Đóng vai **business analyst** theo domain dự án, thảo luận + spec bằng **tiếng Việt**.
- **Khảo sát trước khi hỏi**: tự tìm roadmap dự án (không rõ thì hỏi), domain doc, codebase, nợ kỹ thuật liên quan, và `.specify/memory/constitution.md`.
- **Phỏng vấn theo trục nghiệp vụ** (GĐ2 trên màn hình → GĐ3 nghiệp vụ nền) qua **AskUserQuestion**, gom 1–4 câu độc lập mỗi lượt. Quyết định **trọng yếu** (dữ liệu/quyền/luồng) hỏi từng câu; quyết định **thứ yếu** (sort mặc định, empty-state, wording) model đề xuất kèm căn cứ rồi duyệt gộp cuối giai đoạn. `(Recommended)` chỉ được đánh khi có căn cứ từ khảo sát. Hiến chương KHÔNG phải khung hỏi — là vòng kiểm GĐ4.
- **Sổ theo dõi vét cạn persist ra file** `.specify/interviews/<slug>.md` trong lúc phỏng vấn (chống mất trạng thái khi phiên dài), kết thúc chuyển thành `specs/<feature>/interview-notes.md`. Ràng buộc kỹ thuật từ GĐ4 ghi vào section `Ràng buộc kỹ thuật kế thừa` trong `spec.md` — kênh bàn giao cho `/speckit.plan`.
- Đánh dấu nguồn mỗi kết luận: `[từ khảo sát]` / `[suy luận]` / `[cần bạn quyết]`.
- **Chỉ ghi spec sau khi bạn xác nhận** đạt hiểu chung. `spec.md` dùng **spec-template do preset replace** (giữ nguyên các section core + thêm mục `## Đặc tả màn hình`); kết quả GĐ2 rót vào đó, mỗi màn một khối `### Màn`. Scaffolding core (tạo `specs/<n>-<name>/spec.md`, hooks) vẫn kéo vào qua `{CORE_TEMPLATE}`.

**2. Command `speckit.plan`** (`strategy: wrap`) — điều khiển *cách plan*:
- **Khảo sát codebase liên quan feature** (frontend + backend đang có) trước khi điền Technical Context / Structure Decision — plan dựa trên cái đang có, không chọn layout generic.
- `plan.md` dùng **plan-template mặc định**; cổng Constitution Check của core phải pass trước Phase 0.

**3. Template `spec-template` + `tasks-template`** (`strategy: replace`, tự chứa) — *đặc tả màn hình per-screen thay cho lệnh checklist*:
- `spec-template` tổ chức theo **kỷ luật một-nhà** (chống trùng lặp — Wiegers / Business Rules Manifesto / ISO 29148): **`## Thực thể & Từ điển dữ liệu`** sở hữu hằng số field (độ dài, miền giá trị, giá trị hợp lệ); **`### Functional Requirements`** sở hữu hành vi + business rule (duy nhất, liên trường, phân quyền, vòng đời); **`## Đặc tả màn hình`** mỗi màn một khối `### Màn` **chỉ mô tả trình bày & ranh giới** (control nào, cột, lọc/sắp/tìm, kênh báo, 4 trạng thái, xác nhận phá hủy) và **TRỎ** tới FR/field — không chép lại hằng số hay luật; **Acceptance Scenarios** là ví dụ trỏ FR. Chỉ nêu **yêu cầu bằng lời**; không mã hóa message/testid, không chọn thư viện/kiểu cột DB — để plan/tasks lo. Mỗi mục con chỉ điền khi màn thực sự có; `K = 0` → ghi "Không có màn".
- `tasks-template` giữ nguyên core + mục **"Phủ đặc tả màn hình"** nhắc lệnh tasks sinh đủ task cho từng `### Màn` (validation/trạng thái/cột/lọc/quyền/xác nhận phá hủy); cơ chế cụ thể (thư viện, resource string, data-testid) do task tự figure out theo stack.
- Quy ước UI/UX **chung toàn chương trình** (vi-VN, định dạng ngày/tiền, a11y, responsive, kênh báo lỗi, UI kit) **KHÔNG** nằm ở đây — do chỉ dẫn chung của dự án (frontend agent / design system) cưỡng chế, tránh lặp mỗi spec. Đây là lý do lệnh `speckit.checklist` cũ (đưa UI/UX gate vào một lệnh riêng) đã được bỏ.

> `speckit.specify` override *cách hỏi* + rót output vào `spec-template` (replace); `speckit.plan` override *cách plan*, vẫn dùng plan-template mặc định của core.

## Cài đặt

Nội bộ (dev, từ thư mục này):

```bash
specify preset add --dev ./speckit-dft-preset
```

**Tạo hiến chương (project mới):** chạy `/speckit.constitution`. Không cần copy file thủ công.

> Preset **không thể** ship hiến chương qua `type: template`: `specify init` gieo `.specify/memory/constitution.md` từ template core **trước** khi preset được cài, và đọc bằng đường dẫn trực tiếp nên bỏ qua `PresetResolver`. Override command `speckit.constitution` là cách duy nhất ghi được vào file sống. Chi tiết + bằng chứng: [`docs/research/constitution-quality.md`](https://github.com/anhnt3/agent-skills/blob/main/docs/research/constitution-quality.md) §6.

Kiểm tra:

```bash
specify preset info dft-preset            # xem 5 override (3 command + 2 template)
specify preset resolve spec-template      # spec-template = bản replace của preset (templates/spec-template.md)
specify preset list
```

Gỡ:

```bash
specify preset remove dft-preset
```

Từ GitHub release (sau khi publish):

```bash
specify preset add --from https://github.com/anhnt3/agent-skills/releases/download/dft-preset-v0.0.2/dft-preset-0.0.2.zip
```

## Publish (GitHub release zip — thủ công, chủ đích)

Release **chỉ** bằng script thủ công (không dùng GitHub Actions):

```bash
# 1. Bump version trong preset.yml (tăng đơn điệu từ baseline 0.0.1) rồi commit.
# 2. Chạy:
./release.sh          # build zip -> tạo/cập nhật GitHub Release + upload asset + cập nhật URL trong README
```

`release.sh` đọc version từ `preset.yml` (hoặc nhận version làm tham số), gọi `build-zip.sh` rồi dùng `gh` tạo release `dft-preset-v<version>`. Build zip riêng lẻ: `./build-zip.sh`.

Cài từ asset qua `specify preset add --from <url>`. Lưu ý: `--from` chỉ nhận HTTPS (hoặc localhost) — không nhận đường dẫn file local, và **không** verify sha256 (trade-off đã chấp nhận của kênh phân phối này).

## Khi nào dùng / không dùng

- **Dùng**: dự án cần một hiến chương thực sự cưỡng chế được; chức năng có mockup + mock-service cần chuyển sang backend thật.
- **Không dùng**: spec nhanh không cần phỏng vấn.

## Sau khi nâng cấp spec-kit CLI (bắt buộc đọc)

Override của preset là **snapshot đã materialize** vào thư mục command của agent — spec-kit không resolve lại stack mỗi lần chạy. Nâng cấp `specify` hoặc chạy lại `specify init` có thể ghi đè các file đã compose bằng bản core mới → override lặng lẽ biến mất. Sau mỗi lần nâng cấp:

```bash
specify preset disable dft-preset && specify preset enable dft-preset   # ép reconcile lại
specify preset resolve speckit.specify                                  # phải trỏ vào .specify/presets/dft-preset/
```

Đồng thời chạy `scripts/check-core-anchors.sh` (repo nguồn) để xác nhận các section core mà preset neo vào chưa bị upstream đổi tên.

## Yêu cầu

- `speckit_version >= 0.6.0` (cần AskUserQuestion trên Claude Code). Đã kiểm tương thích với spec-kit **0.12.11**.
- Dự án đã `specify init`. Chưa có `.specify/memory/constitution.md` cũng không sao — chạy `/speckit.constitution` để tạo. Với `/speckit.specify`, thiếu hiến chương thì preset cảnh báo + bỏ GĐ4, các giai đoạn phỏng vấn vẫn chạy đủ.
- Roadmap (tùy chọn, nguồn làm giàu): vị trí tùy dự án, command tự tìm, không rõ thì hỏi; không có cũng chạy đầy đủ các giai đoạn.
