# Review Sonnet-followability toàn bộ command — round 2 (2026-07-11)

> Tiếp nối `speckit-addon-review-2026-07-11.md` (round 1: cơ chế/đóng gói/vận hành). Round này trả lời
> đúng một câu: **model giỏi-nhưng-vội (Claude Sonnet) chạy 7 command hiện tại có chính xác không, và
> cần sửa gì để chính xác nhất có thể.**
>
> Phương pháp: 3 critic độc lập (Fable, read-only, mỗi critic một cụm file, cùng lens đối kháng
> `escape-hatch-catalog.md` — đóng vai Sonnet thực thi trên kịch bản thật: CRUD 3 màn / K=0 / brownfield
> / SỬA ĐỔI / greenfield / re-run / resume / ủy thác subagent) + một pass độc lập của orchestrator.
> Mọi finding được đối chiếu nguyên văn file trước khi áp patch. **Toàn bộ patch dưới đây ĐÃ áp cùng ngày.**

## TL;DR

- Trước patch: Sonnet chạy đúng ước lượng **~70–75%** (constitution chế độ SỬA ĐỔI tệ nhất ~55–60%).
  Không lỗi nào chặn thực thi — tất cả là **bỏ-sót-âm-thầm**: gate đếm sai trục, chỉ thị chọi nhau,
  "done" của core che mất việc bắt buộc của preset.
- Điểm mạnh được cả 3 critic xác nhận: hệ neo-đếm-từ-nguồn-ngoài (K/N/A+B, Pha 0 của qa-cycle) và các
  miếng vá core đặt gần điểm hành động là **hơn hẳn mặt bằng prompt cùng loại** — các finding là vá lỗ
  ở rìa, không phải đập nền.
- 22 finding xác nhận (2 CRITICAL, 14 MAJOR, 6 MINOR) → 23 patch tối thiểu, giữ nguyên kiến trúc.

## Findings & patch đã áp

### speckit.specify.md (7 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| F1 | CRITICAL | Neo GĐ2 chỉ đếm K màn, không đếm 4 mục sàn/màn → 1 câu hỏi/màn là ✅ cả màn, gate PASS mà mất 3/4 nội dung | Neo mới `≥ 5K`: mỗi màn 1 dòng gốc + 4 dòng con ⏳ (một dòng/mục sàn); ✅ xét trên từng dòng con |
| F2 | CRITICAL | "Sau khi ghi spec" nằm SAU "Done When" của core → cuối phiên dài Sonnet báo xong theo core, bỏ bàn giao `→ plan` | Bullet mới trong mục VÔ HIỆU HÓA: Done When của core chưa đủ — 3 việc "Sau khi ghi spec" là dòng bắt buộc bổ sung |
| F3 | MAJOR | "coi như 0 marker" đọc được thành "khỏi quét" → tick khống "No markers remain" | Đổi thành: QUÉT spec thật, mỗi marker sót → hỏi (không trần 3), về 0 thật mới tick |
| F4 | MAJOR | Bước B GĐ3 đối chiếu sàn "bằng mồm", Q tự khai | Bắt in bảng đối chiếu đúng 9 dòng: mỗi mục sàn trỏ `#` dòng Bước A hoặc thêm ⏳ |
| F5 | MINOR | "không tìm ra thì hỏi vị trí" chọi Bất biến #5 "thiếu thì bỏ" | Tách 2 lớp: nguồn làm giàu → hỏi MỘT lần gộp rồi áp #5; thứ bắt buộc → hỏi lại |
| F6 | MINOR | File sổ chỉ ghi cuối giai đoạn → compaction giữa GĐ2/GĐ3 dài vẫn mất trạng thái | Ghi thêm sau mỗi lượt AskUserQuestion có quyết định chốt |
| F7 | MINOR (tự phát hiện) | HALT (Bất biến #7) bảo ghi file sổ nhưng GĐ1 cấm mutation | HALT ở GĐ1 → chỉ báo, không ghi file |

### speckit.constitution.md (8 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| C1 | MAJOR | "Gộp hẹp" (chỉ khi trùng luật) chọi "Ép ngân sách: ưu tiên gộp cùng chủ đề" — Sonnet theo lệnh gần hơn, phép cân đối hợp thức hóa gộp sai | Tách khái niệm **NHÓM ≠ GỘP**: nhóm (cột `Nhóm nguyên tắc #`, giữ nguyên dòng, thành bullet ở GĐ5) vs gộp (xóa dòng, chỉ khi trùng luật); ngân sách 7 đếm theo NHÓM |
| C2 | MAJOR | Chế độ SỬA ĐỔI: phép cân đối `= A + B` **bất khả thoả** khi có nguyên tắc cũ bị gỡ → Sonnet buộc phải âm thầm vô hiệu gate | Vế phải `= A + B + R`; định nghĩa gộp k dòng = k−1; không cân sau 1 lần rà → in ánh xạ ID từng dòng |
| C3 | MAJOR | Cột `Code đã đạt?` không có luật cho "không xác định được" → greenfield toàn bộ thành `MUST + miễn trừ` vô nghĩa; brownfield "chưa rõ" thành `MUST` thẳng → bão CRITICAL | Hai nhánh tường minh: greenfield → `MUST` thẳng; không có dữ liệu / đầy suppression → `chưa đạt` → `MUST + miễn trừ` |
| C4 | MAJOR | Tầng-2 falsifiable lách được bằng phép thử vòng tròn ("vi phạm X ⇒ trượt") | Phép thử vòng tròn ⇒ TRƯỢT; phép thử hợp lệ phải nêu artifact/thao tác mà người chưa đọc nguyên tắc vẫn chạy được |
| C5 | MAJOR | SỬA ĐỔI: Tầng-1 "sửa ngay" chọi "giữ nguyên văn từng chữ" → Sonnet viết lại đơn phương hiến chương cũ | Nguyên tắc CŨ trượt → AskUserQuestion (giữ/sửa/gỡ + hệ quả semver); "sửa ngay" chỉ áp cho nguyên tắc MỚI |
| C6 | MINOR | Bất biến #6 đọc chặt → xin xác nhận cả GĐ0→1→2 | Chốt đúng 2 điểm xác nhận bắt buộc (cuối GĐ4, cuối GĐ5) |
| C7 | MINOR | GĐ2 chế độ SỬA ĐỔI thiếu kết cục "luật đã có trong hiến chương" → phồng A | Thêm kết cục (c), không tính vào A |
| C8 | MINOR | Hook `before_constitution` của core chỉ được đọc SAU toàn bộ phỏng vấn | Thêm "Trước GĐ0: chạy Pre-Execution Checks của core" |

### speckit.checklist.md (3 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| K1 | MAJOR | Re-run: "chấm mục `[ ]` trống" vs "giữ nguyên verdict" → hai Sonnet hai kết quả (re-litigate N/A, hoặc Gap đã vá không được chấm lại) | Luật rõ: `[ ]` chưa verdict → chấm mới; `⚠️ Gap` → chấm LẠI theo spec hiện tại; `[x]`/`➖ N/A` → giữ nguyên. Luật "giữ verdict" chỉ áp cho đồng bộ text Bước 1 |
| K2 | MINOR | Re-run append `## Tổng` thứ hai; đếm Pass theo marker hay theo tick không rõ | "Tạo hoặc CẬP NHẬT"; Pass = đếm tick `[x]` kể cả mục người tự tick |
| K3 | MINOR | Fast-path DỪNG bỏ luôn extension hooks `before/after_checklist` của core | Fast-path vẫn chạy Pre/Post-Execution Checks, chỉ thay phần sinh checklist |

### speckit.plan.md (2 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| P1 | MAJOR | "Ràng buộc kế thừa = bắt buộc, không bỏ sót" nhưng không có neo đếm → phản ánh 2/5 rồi "đã đối chiếu ✓" | Đếm R, in bảng đúng R dòng ở Constitution Check: ràng buộc → nơi phản ánh / lý do không áp |
| P2 | MINOR | "Trước khi chạy core" nghĩa đen → khảo sát trước cả Setup, vớ nhầm feature dir | Chạy Setup của core trước; phần preset chèn giữa Setup và Technical Context |

### qa-spec-cycle.md (4 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| Q1 | MAJOR | `→ chi tiết:` thuần mô tả — không gì bắt ĐỌC reference trước khi làm pha (nặng nhất khi resume giữa Pha 7: bỏ gate DB an toàn, bỏ poll-ready) | Luật bắt buộc đầu Pipeline: đọc file chi tiết TRƯỚC khi bắt đầu pha, kể cả khi resume |
| Q2 | MAJOR | Bảng ủy thác không truyền reference cho subagent (con là context mới) + Pha 5 con không có danh sách TC ID → bịa ID | Prompt cho con PHẢI kèm đường dẫn reference + lệnh đọc trước; Pha 5 kèm danh sách ID manual TC |
| Q3 | MAJOR | Pha 0 tạo `qa-run.md` nhưng format ledger + quy tắc resume nằm ở traceability.md không được trỏ → ledger free-form, phiên sau không resume được | Pha 0 thêm `→ chi tiết: traceability.md §2–§3` |
| Q4 | MAJOR | Non-interactive không liệt kê cổng Pha 12 → autopilot ghi thẳng CLAUDE.md không ai duyệt | Pha 12 vào danh sách cổng cứng: ghi diff vào qa-run.md, `blocked`, HALT |

### domain-design.md (3 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| D1 | MAJOR | Doc gộp không prefix chung → tên file không suy được từ module → specify/plan tra không thấy, **im lặng** chạy không domain doc (vỡ hợp đồng chống-vênh) | Không prefix chung → hỏi tên cụm; ghi **file stub** `docs/domain/<module>.md` trỏ sang doc gộp cho từng module thành viên |
| D2 | MAJOR | On-delete: "mặc định Restrict" chọi "phải hỏi khi có nghĩa nghiệp vụ" — tiêu chí không đếm được → 0 câu hỏi, Restrict toàn bộ | Tiêu chí đếm được: FK nối 2 aggregate root khác nhau HOẶC entity cha có item roadmap thao tác Xóa → bắt buộc hỏi; mặc định chỉ cho FK danh mục thuần + ghi tường minh |
| D3 | MINOR | Fallback path template mơ hồ ("trong extension đã cài") | Ghi path tường minh `.specify/extensions/dft-speckit/templates/domain-template.md` |

### road-map-from-codebase.md (1 patch)

| # | Sev | Lỗ hổng | Patch đã áp |
|---|-----|---------|-------------|
| R1 | MAJOR | Gate bước 5 so SỐ (`≥ N`) không so DANH SÁCH → chạy lại: +1 màn mới −1 màn gỡ vẫn 12≥12 PASS | Đối chiếu theo danh sách: từng màn map vào ≥1 item; item mồ côi giữ nguyên + ghi chú "không còn thấy trong codebase" |

### Khác

- `preset.yml` + README preset: gỡ "CHK001–010" hardcode (template ui-ux đã được mở rộng CHK002b/c...,
  command chấm theo phép đếm từ file bộ nên không phụ thuộc dải số).

## Không sửa (chủ đích, confidence < 70% hoặc trade-off chấp nhận)

1. **Trigger fast-path `convention`/`ux` có thể hijack yêu cầu checklist động** ("checklist trải nghiệm
   thanh toán") — đã có mệnh đề "mơ hồ → hỏi"; siết trigger sẽ đổi hành vi người dùng quen. Theo dõi
   thực tế trước.
2. **Gap "người dùng chấp nhận để lại" không có dấu vết trong file checklist** — phiên sau không phân
   biệt gap-đã-chấp-nhận với gap-mới. Đáng cân nhắc thêm marker `⚠️ Gap (chấp nhận)` ở lần sửa sau.
3. **qa-spec-cycle không tự phát hiện spec đổi giữa 2 phiên** (không lưu hash spec vào ledger) —
   traceability §3.5 có luật "spec đổi → chạy lại Pha 3+" nhưng dựa vào người/model nhận ra.
4. **Ngân sách GĐ3 constitution "3–4 lượt" khít với sàn 5 trục** — khả thi nhờ gom 4 câu/lượt; chưa có
   kịch bản vỡ cụ thể.
5. **Prefix match `system` khớp nhầm `systemlog`** (domain-design) — chỉ xảy ra với quy ước đặt tên
   module bất thường; mệnh đề "nói rõ phạm vi khi báo" đã có.

## Kết luận

Sau patch, cả 7 command không còn finding CRITICAL/MAJOR mở nào từ 3 critic + pass độc lập. Kiến trúc
neo-đếm + persist-file + vá-core-gần-điểm-hành-động được giữ nguyên; các patch chỉ bịt đường thoát,
không thêm giai đoạn mới, không tăng số lượt hỏi (trừ những chỗ mà *thiếu* câu hỏi chính là lỗi:
on-delete giữa aggregate root, nguyên tắc cũ trượt cổng). Verify sau patch: cài thật vào project
`specify init` (0.12.4) — 4 command materialize sạch, YAML frontmatter parse OK, không còn literal
`{CORE_TEMPLATE}`, nội dung patch có mặt trong bản cài.
