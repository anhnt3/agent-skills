# Ma trận truy vết + state ledger (`qa-run.md`) — Pha 8/11, agnostic

## Nội dung

1. [Ma trận truy vết (trục = requirement, sống trong xlsx)](#1-ma-trận-truy-vết-trục--requirement-sống-trong-xlsx)
2. [State ledger `qa-run.md` — chỉ để resume](#2-state-ledger-qa-runmd--chỉ-để-resume)
3. [Quy tắc resume — bắt buộc khi skill được gọi lại](#3-quy-tắc-resume--bắt-buộc-khi-skill-được-gọi-lại)

Có **hai artefact khác mục đích, không được lẫn vào nhau**:

1. **Ma trận truy vết** — sống trong sheet "Ma trận truy vết" của `testcases-manual.xlsx` (sinh bởi
   `scripts/csv_to_xlsx.py`, xem `manual-xlsx-format.md`). Đây là nguồn sự thật cho câu hỏi "requirement
   nào đã được test, ở tầng nào, còn gap không".
2. **`qa-run.md`** — state ledger nằm cạnh spec (`<thư mục spec>/qa-run.md`). Đây **chỉ** để resume phiên
   làm việc (chạy tiếp từ pha nào), **không** phải nơi lưu truy vết requirement.

Không dùng `qa-run.md` để trả lời "FR-004 có test chưa" — luôn tra ở xlsx. Không dùng xlsx để trả lời
"lần chạy trước dừng ở pha nào" — luôn đọc `qa-run.md`.

## 1. Ma trận truy vết (trục = requirement, sống trong xlsx)

Mô hình dữ liệu, trục chính là **FR/AC**, không phải test case. Sheet "Ma trận truy vết" trong
`testcases-manual.xlsx` (sinh bởi `scripts/csv_to_xlsx.py`) có 5 cột:

| FR/AC | Manual TC | Test tự động (`file::name`) | Auto status | Phủ |
|-------|-----------|------------------------------|-------------|-----|
| FR-004 | TC-DEV-007 | `DeviceCatalogAppService_Tests.cs::Create_duplicate_code_rejected` | Pass | Có |
| FR-011 | TC-DEV-014 | — | chưa chạy | MANUAL |

**Nguồn của từng cột:**

- `FR/AC` — lấy từ spec gốc, cùng danh sách đã dùng ở Pha 3 (coverage matrix) và Pha 4 (manual TC).
- `Manual TC` — danh sách ID case (`TC-<PREFIX>-NNN`) phủ FR/AC đó, pivot từ cột *Truy vết* trong sheet
  Testcases.
- `Test tự động` — `file::tên_test`, pivot từ cột *Test tự động* trong sheet Testcases; `—` nếu không có
  test tự động thật nào phủ (kể cả khi cột đó là sentinel `manual-only`).
- `Auto status` — tổng hợp từ Pha 8 (kết quả chạy suite): `Pass` nếu toàn bộ test phủ FR/AC đó đều pass,
  `Fail` nếu có ít nhất một fail, `chưa chạy` nếu có test chưa chạy được (blocker chưa gỡ) — không được tự
  suy ra "coi như pass" khi chưa chạy thật.
- `Phủ` — script tự tính từ cột *Test tự động* của mọi case phủ FR/AC đó: `Có` nếu có ít nhất một test tự
  động thật (giá trị `file::tên_test`); `MANUAL` nếu không có test tự động thật nhưng **mọi** case phủ FR
  đó đều dùng literal `manual-only` (có chủ đích, theo lý do đã ghi ở Pha 3 — không phải lỗi); `GAP` nếu
  không có test tự động thật **và** không có sentinel `manual-only` nào — đây là gap **ngoài ý muốn** cần
  bổ sung. Cột này cho người đọc Excel phân biệt ngay "chủ đích để tay" (`MANUAL`) với "bị bỏ sót"
  (`GAP`) mà không cần lật lại lý do ở Pha 3.

**Quy tắc lấp gap ở Pha 11:** với mỗi `GAP` (không phải `MANUAL`) → đây là thiếu sót cần bổ sung (quay lại
Pha 5 author thêm test), không phải chấp nhận và bỏ qua.

**Cập nhật cột `Auto status` (nguồn là cột 12 "Kết quả tự động" ở sheet Testcases) ở Pha 8/11**: skill
regenerate lại CSV/JSON input với cột 12 điền kết quả chạy thật, rồi chạy lại
`scripts/csv_to_xlsx.py` trỏ vào cùng `<thư mục spec>/testcases-manual.xlsx`. Script merge theo `ID` nên
dữ liệu tester đã điền tay ở cột 13–16 (sheet Testcases) **không bị mất** khi re-run — xem chi tiết ở
`manual-xlsx-format.md` §6.

Ma trận này **không lập lại từ đầu** ở Pha 11 — chỉ hoàn thiện cột `Auto status`/`Phủ` dựa trên khung đã
dựng ở Pha 3–5 và kết quả chạy thật ở Pha 8/10.

## 2. State ledger `qa-run.md` — chỉ để resume

`qa-run.md` là **checklist trạng thái tiến trình**, đặt cạnh spec (`<thư mục spec>/qa-run.md`), tạo ở Pha
0 (Intake) và cập nhật sau **mỗi pha**. Không ghi truy vết requirement vào đây.

### Template

```markdown
# QA run — <feature-id> (PREFIX: <PREFIX>)

Spec: <đường dẫn spec.md>
Bắt đầu: <ngày giờ>
Cập nhật lần cuối: <ngày giờ>

## Phase checklist (0–12)

| # | Pha | Trạng thái | Ghi chú |
|---|-----|-----------|---------|
| 0 | Intake | done | feature-id + PREFIX xác định |
| 1 | Context | done | qa-context.md đã có/tạo mới |
| 2 | Scan & baseline | done | framework: <...>, test đã có: <có/không> |
| 3 | Coverage matrix | done | N FR/AC → tầng đã chọn |
| 4 | Manual TC → xlsx | done | N case, xlsx tại <path> |
| 5 | Author auto test | done | N test tự động sinh |
| 6 | Quality gate | done | compile/type-check: pass |
| 7 | Readiness (no-defer) | in-progress | blocker đang gỡ: <mô tả> |
| 8 | Run + record | pending | — |
| 9 | Present | pending | — |
| 10 | Triage + bounded fix | pending | — |
| 11 | Finalize truy vết | pending | — |
| 12 | Update CLAUDE.md | pending | — |

Trạng thái hợp lệ: `pending` \| `in-progress` \| `blocked` \| `done`.

## Blockers log

| Thời điểm | Pha | Blocker | Loại (playbook #) | Trạng thái | Escalate? |
|-----------|-----|---------|-------------------|-----------|-----------|
| <ts> | 7 | 401 khi chạy E2E, chưa có session | Blocker 1 (auth) | đã gỡ | không |
| <ts> | 7 | Thiếu test id cho bảng danh sách | Blocker 2 (selector) | chờ duyệt | có — lan 4 file |

## Failure classifications (Pha 10)

| Test | Lớp | Hành động | Kết quả |
|------|-----|-----------|---------|
| `Create_duplicate_code_rejected` | test-defect | auto-fix expected message | pass sau fix |
| `List_devices_e2e` | infra-blocker | gỡ Blocker 4 (seed) | pass sau fix |
| `Update_price_rounds_correctly` | product-bug | đề xuất patch, chờ duyệt | **chờ duyệt** — chưa fix |

## Issues log (product-bug không được duyệt / còn treo)

| FR/AC | Test | Mô tả bug | Patch đề xuất | Trạng thái |
|-------|------|-----------|---------------|-----------|
| FR-014 | `Update_price_rounds_correctly` | Làm tròn giá sai 2 chữ số thập phân | <diff/mô tả> | logged, chưa duyệt |
```

### Quy tắc dùng ledger

- **Cập nhật sau mỗi pha**, không dồn cuối mới ghi — nếu phiên bị ngắt giữa chừng, `qa-run.md` phải phản
  ánh đúng pha cuối cùng đã hoàn tất.
- **Trạng thái `blocked`** dùng khi một pha đang chờ duyệt/chờ input người dùng (cổng cứng) — không đánh
  dấu `done` khi còn cổng mở.
- **Blockers log** và **Failure classifications** là nhật ký lịch sử của quá trình chạy (phục vụ resume +
  hiểu bối cảnh khi quay lại) — không thay thế ma trận truy vết trong xlsx. Không copy nội dung hai bảng
  này sang xlsx và ngược lại.

## 3. Quy tắc resume — bắt buộc khi skill được gọi lại

Khi `qa-spec-cycle` được invoke lại cho cùng một feature (spec/thư mục đã có `qa-run.md` từ trước):

1. **Đọc `qa-run.md` trước tiên** — không bắt đầu lại từ Pha 0 nếu ledger cho thấy đã có pha `done`.
2. Xác định **pha đầu tiên chưa `done`** (đầu tiên gặp `pending`, `in-progress`, hoặc `blocked`) — đây là
   điểm resume.
3. Nếu pha đó là `blocked` (đang chờ duyệt/chờ input) → trình lại đúng nội dung đang chờ (vd bug chưa
   duyệt, blocker chưa gỡ) trước khi làm gì khác — không âm thầm bỏ qua cổng đang treo.
4. Chạy tiếp từ pha đó, tiếp tục cập nhật `qa-run.md` sau mỗi pha như bình thường.
5. Không chạy lại các pha đã `done` trừ khi có thay đổi rõ ràng ở input của pha đó (vd spec đổi → cần
   chạy lại Pha 3 trở đi).
