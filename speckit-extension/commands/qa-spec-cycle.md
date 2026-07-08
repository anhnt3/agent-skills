---
description: "QA trọn vòng từ 1 file spec — sinh testcase thủ công (xlsx 2 sheet), sinh test tự động theo pyramid, tự dựng môi trường và chạy, báo cáo, fix có kiểm soát, ghi ma trận truy vết. Technology-agnostic — đặc thù stack đọc từ .agents/qa-context.md."
---

# QA Spec Cycle (trọn vòng từ 1 spec)

Nhận đầu vào là **1 file spec**, chạy trọn vòng QA qua 13 pha: sinh testcase thủ công (xlsx), sinh
test tự động theo pyramid, tự dựng môi trường, chạy, báo cáo, triage + fix có điểm dừng, và ghi ma
trận truy vết.

**Command này là engine tiến trình, agnostic với mọi stack.** Framework/lệnh/thư mục test cụ thể của
project **không** nằm trong command — chúng sống ở `.agents/qa-context.md` (tạo mới nếu thiếu, xem
Pha 1). Đổi stack = đổi qa-context, không đổi command.

Các file hỗ trợ được bundle trong extension:
- Script: `.specify/extensions/dft-speckit/scripts/csv_to_xlsx.py`
- Tài liệu chi tiết từng pha: `.specify/extensions/dft-speckit/references/<tên>.md`

## User Input

$ARGUMENTS

Kỳ vọng: đường dẫn tới `spec.md` hoặc thư mục feature. Nếu trống → hỏi nguồn spec trước khi tiếp tục.

## Nguyên tắc xuyên suốt

1. **Technology-agnostic** — không viết lệnh/tên framework cụ thể vào command; luôn tra qa-context hoặc scan.
2. **Scan trước, hỏi sau** — cái gì codebase trả lời được thì tự dò rồi thông báo ("Phát hiện X → dùng Y"); chỉ hỏi khi thật sự cần người quyết.
3. **Câu hỏi luôn có phương án Recommended đầu tiên + lý do** (dùng AskUserQuestion khi có sẵn).
4. **Pyramid integrity** — auto test author theo requirement × risk × tầng-thấp-nhất-chứng-minh-được, KHÔNG map 1:1 từ manual TC.
5. **No fake-green** — cổng cơ học chặn assert rỗng / selector-endpoint không tồn tại, trước khi present.
6. **No-defer** — dựng môi trường là việc của command; cấm bỏ test vì "thiếu môi trường", chỉ escalate đúng phần không tự làm được.
7. **Bounded fix** — auto-fix phía test/infra; product-bug duyệt từng cái + log phần dư thành issue.
8. **Manual columns thuộc về người** — kết quả tự động vào cột/sheet riêng, chỉ-đọc, có nhãn; 4 cột thực thi để trống cho tester.
9. **Checkpointed/resumable** — ghi tiến độ pha vào `qa-run.md`; gọi lại → đọc ledger, chạy tiếp từ pha dở dang.

## Pipeline 13 pha

Ghi trạng thái pha vào `<thư mục spec>/qa-run.md` ngay sau khi hoàn thành mỗi pha (để resume). Nếu
`qa-run.md` đã tồn tại khi bắt đầu → đọc ledger, tiếp tục từ pha dở dang, không làm lại từ đầu.

- [ ] **Pha 0 — Intake.** Xác định file spec (từ `$ARGUMENTS` hoặc hỏi), rút feature-id + PREFIX (vd `DEV`) dùng cho ID testcase. Tạo `qa-run.md` nếu chưa có, hoặc đọc ledger nếu đã có.
- [ ] **Pha 1 — Context.** Có `.agents/qa-context.md` → load. Thiếu → scan + phỏng vấn tạo mới theo template slim. → chi tiết: `.specify/extensions/dft-speckit/references/qa-context-template.md`
- [ ] **Pha 2 — Scan & baseline.** Dò framework/thư mục test hiện có (điền vào qa-context những field còn thiếu), test đã có cho spec này chưa, môi trường sẵn sàng chưa → **thông báo phát hiện**, không hỏi lại cái đã dò được. → chi tiết: `.specify/extensions/dft-speckit/references/qa-context-template.md`
- [ ] **Pha 3 — Coverage matrix.** Từ mỗi FR/AC + mức risk → chọn tầng test (unit/integration/E2E/manual-only) + lý do. → chi tiết: `.specify/extensions/dft-speckit/references/coverage-matrix.md`
- [ ] **Pha 4 — Manual TC → xlsx.** Mỗi acceptance scenario/rule → 1 testcase. Output cố định tại `<thư mục spec>/testcases-manual.xlsx` (Pha 8/11 đọc/ghi lại đúng file này qua chạy lại script, script tự merge nên giữ nguyên cột tester đã điền). Cách ưu tiên (ít lỗi hơn): viết `testcases-manual.json` (16 khóa/case) rồi convert; CSV 16-cột cũng được chấp nhận. Chạy `.specify/extensions/dft-speckit/scripts/csv_to_xlsx.py` để dựng file `.xlsx` 2 sheet (Testcases + Ma trận truy vết); 4 cột thực thi để trống cho tester. Báo số case đã sinh. Script chỉ cần `python3`; lần chạy đầu tự tạo venv + cài `openpyxl` (cần mạng lần đầu đó). → chi tiết: `.specify/extensions/dft-speckit/references/manual-xlsx-format.md`
- [ ] **Pha 5 — Author auto test.** Sinh test theo tầng đã chọn ở coverage matrix (không map 1:1 từ manual TC), dùng framework khai báo trong qa-context; comment truy vết FR + TC trong mỗi test; requirement manual-only ghi rõ lý do trong ma trận. → chi tiết: `.specify/extensions/dft-speckit/references/test-generation.md`, `.specify/extensions/dft-speckit/references/coverage-matrix.md`
- [ ] **Pha 6 — Quality gate.** Chạy compile/type-check của project (lệnh lấy từ qa-context); grep xác nhận selector/endpoint được assert thật sự tồn tại trong source; chặn assert tầm thường/rỗng. → chi tiết: `.specify/extensions/dft-speckit/references/quality-gate.md`
- [ ] **Pha 7 — Readiness (no-defer).** Tự dựng môi trường (services → migrate/seed → start backend/frontend background → cài deps test → poll tới ready) rồi gỡ blocker (auth, selector thiếu, seed). Lệnh phá hoại (migrate/seed/reset/khởi tạo có trạng thái) chỉ chạy vào **test target dùng-một-lần** đã khai báo trong qa-context; thiếu khai báo → dừng, hỏi (Recommended trước). **Cổng cứng khi cần người quyết** — escalate đúng phần không tự làm được, nêu rõ thiếu gì + lệnh gợi ý, chờ người dùng xử lý rồi tiếp tục, không bỏ ngang. → chi tiết: `.specify/extensions/dft-speckit/references/environment-bringup.md`, `.specify/extensions/dft-speckit/references/blocker-playbook.md`
- [ ] **Pha 8 — Run + record.** Chạy suite thật; ghi auto-status vào cột/sheet auto (không đụng cột người); test chưa chạy được → ghi "chưa chạy" trung thực, không âm thầm pass. → chi tiết: `.specify/extensions/dft-speckit/references/traceability.md`
- [ ] **Pha 9 — Present.** **Cổng cứng: phải trình bày trước khi qua pha 10.** Báo cáo pass/fail + coverage theo từng FR + gap rõ ràng + phân bố pyramid (unit/integration/E2E/manual-only) + kết quả quality gate + trạng thái môi trường.
- [ ] **Pha 10 — Triage + bounded fix.** Phân loại mỗi fail: test-defect / infra-blocker / product-bug. Auto-fix test-defect và infra-blocker. **Cổng cứng khi gặp product-bug** — không tự sửa code sản phẩm; trình chẩn đoán + đề xuất patch, chờ duyệt từng cái, fix cái được duyệt + chạy lại, log phần dư thành issue rồi dừng. → chi tiết: `.specify/extensions/dft-speckit/references/failure-classification.md`
- [ ] **Pha 11 — Finalize truy vết.** Hoàn thiện ma trận trong xlsx: mỗi FR/AC ↔ manual TC ↔ test tự động (file::name) ↔ tầng ↔ trạng thái ↔ gap. → chi tiết: `.specify/extensions/dft-speckit/references/traceability.md`
- [ ] **Pha 12 — Update CLAUDE.md/AGENTS.md.** Nếu chưa có mục "cách test" → thêm (tooling, cách dựng môi trường, lệnh chạy từng tầng — lấy nguyên từ qa-context, không hardcode lại trong command). File này lái mọi phiên agent sau → **show diff và chờ xác nhận trước khi ghi**, không ghi âm thầm.

## Cổng cứng (hard gates) — không được bỏ qua

- **Pha 7**: khi môi trường có phần không tự dựng được (thiếu engine, secret, quyền mạng) → escalate và **dừng chờ người dùng**, không tiếp tục giả định đã xong.
- **Pha 7 (env-safety)**: lệnh phá hoại (migrate/seed/reset/khởi tạo có trạng thái) chỉ chạy khi có **test target dùng-một-lần** khai báo trong qa-context; không có → dừng, hỏi, không đoán bừa vào DB/service thật. → chi tiết: `.specify/extensions/dft-speckit/references/environment-bringup.md`.
- **Pha 9**: luôn present đầy đủ trước khi bước sang triage/fix — không được nhảy thẳng từ chạy suite sang sửa code.
- **Pha 10**: mọi fail loại product-bug phải được **duyệt từng cái** trước khi fix; không tự ý sửa logic sản phẩm mà không có xác nhận.

## Chế độ non-interactive

Khi command chạy không có người trực tiếp (subagent/CI/autopilot) và gặp 1 trong các cổng cứng ở trên
(escalate Pha 7, present Pha 9, product-bug Pha 10) → **KHÔNG được** tự bỏ qua cổng, tự ý duyệt fix
code sản phẩm, hay ghi test chưa chạy thành "pass". Thay vào đó: ghi 1 bản ghi blocker vào
`qa-run.md` (đang ở pha nào, cần gì, vì sao dừng) rồi **HALT**. Chạy lại sau (có người) → đọc
`qa-run.md`, tiếp tục đúng từ điểm blocker.

## Ủy thác cho subagent (khi có Task/Agent tool)

Nếu môi trường có Task/Agent tool: **chạy các pha NẶNG (5, 6, 7, 8) trong subagent con** — con làm
phần bulk (sinh nhiều file, chạy suite, chạy env, grep lớn), ghi artifact ra **file**, chỉ trả về
orchestrator một **summary ngắn + đường dẫn file**, KHÔNG trả raw stdout hay nội dung file về context
cha. Mục đích: tránh work-product của các pha này (log suite, N file test sinh ra, log dựng env, kết
quả grep) làm phình context của agent chính.

| Pha | Con nhận | Con trả về |
|---|---|---|
| 5 — Author test | Quyết định coverage-matrix + qa-context + spec | File test đã ghi + danh sách FR/TC mỗi file phủ |
| 6 — Quality gate | Đường dẫn test vừa sinh + source root | `PASS`, hoặc danh sách `MISSING` đã xác nhận (không phải dynamic) |
| 7 — Readiness | Khối "Môi trường & lệnh dựng" + test DB dùng-một-lần đã khai báo | Log ghi ra file + `READY`/`BLOCKED` + lý do — **quyết định escalate vẫn ở orchestrator** |
| 8 — Run + record | Lệnh chạy từng tầng | stdout → log file; kết quả ghi vào `qa-run.md`/xlsx; trả pass/fail + id test fail |

**Giữ trong orchestrator, KHÔNG ủy thác:** mọi cổng cứng (Pha 7 escalate, Pha 9 present, Pha 10 duyệt
product-bug, HALT ở chế độ non-interactive), `qa-run.md` ledger + xlsx (single source of truth), mọi
`AskUserQuestion`, phán đoán chọn tầng ở Pha 3, phân loại fail ở Pha 10.

**Ràng buộc an toàn:** subagent con **không được** tự duyệt cổng cứng, không được đánh dấu test chưa
chạy là pass; con chỉ trả *facts + đề xuất*, việc đánh giá gate luôn ở cha. Chế độ non-interactive ở
cha vẫn HALT + ghi blocker như bình thường, bất kể pha nào chạy trong con.

**Degrade:** không có Task/Agent tool → làm mọi pha inline như thường lệ (command vẫn chạy an toàn trong
1 context).

## Done-when

- `qa-run.md` log đủ 13 pha.
- xlsx tồn tại với 2 sheet (Testcases + Ma trận truy vết); 4 cột thực thi để trống; cột auto có kết quả (hoặc "chưa chạy" trung thực, không giả pass).
- Test tự động tồn tại, truy vết được về FR/AC, **đã chạy thật** (không skip/defer); quality gate pass.
- Môi trường được command tự dựng, hoặc phần không tự làm được đã escalate đúng và được xử lý tiếp sau khi người dùng can thiệp.
- Suite xanh, hoặc mọi gap/fail còn lại được liệt kê tường minh trong ma trận truy vết và trong phần present.
- Ma trận truy vết đầy đủ: mỗi FR/AC → manual TC + test tự động + tầng + trạng thái.
- `CLAUDE.md`/`AGENTS.md` có mục "cách test" (đã thêm nếu trước đó chưa có).
