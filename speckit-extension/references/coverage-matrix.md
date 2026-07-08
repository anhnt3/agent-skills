# Ma trận coverage — chọn tầng test cho từng requirement (Pha 3)

## Quy tắc cốt lõi

Kế hoạch coverage tự động được lập theo **requirement × risk × tầng-thấp-nhất-chứng-minh-được**,
**không map 1:1** từ danh sách manual test case. Manual TC (Pha 4, ghi vào xlsx cho tester) và test tự
động (Pha 5, sinh theo tầng) là **hai hình chiếu song song của cùng một tập FR/AC** — không phải một
sinh ra từ cái kia.

Hệ quả trực tiếp:

- Không được đếm "có N manual TC thì phải có N test tự động tương ứng". Một acceptance scenario có thể
  có 1 manual TC (để tester chạy tay, đảm bảo trải nghiệm thật) nhưng **0** test E2E tương ứng, vì phần
  logic cốt lõi của nó đã được chứng minh chắc chắn hơn — và rẻ hơn, nhanh hơn — ở tầng unit/integration.
- Ngược lại, một requirement có thể không có test tự động nào (manual-only) nếu bản chất là visual,
  exploratory, hoặc bị chặn bởi hạ tầng chưa sẵn sàng.
- Mỗi requirement luôn có **một quyết định automate-vs-manual tường minh kèm lý do** — không được bỏ
  trống, không được mặc định "cứ viết E2E cho chắc".

**Phản mục tiêu:** KHÔNG nhắm tới 100% automation, và KHÔNG nhắm tới "mỗi FR/AC có ít nhất 1 test tự
động". Mục tiêu là mỗi requirement được chứng minh đúng ở tầng rẻ nhất/nhanh nhất/ổn định nhất có thể,
phần còn lại (visual, exploratory, phụ thuộc hạ tầng chưa có) giao thẳng cho người, ghi rõ lý do thay vì
âm thầm bỏ qua.

## Cách lập ma trận

Với mỗi FR/AC trong spec:

1. Liệt kê **scenario** cụ thể (happy path, edge case, negative case, error case...) — một FR có thể
   sinh ra nhiều dòng scenario.
2. Gán **risk** (Cao/Trung bình/Thấp) dựa trên: mức độ ảnh hưởng khi sai (mất dữ liệu, sai nghiệp vụ,
   lộ quyền truy cập...) × khả năng xảy ra.
3. Áp dụng **heuristic chọn tầng** (bên dưới) để chọn tầng thấp nhất có thể chứng minh được scenario đó
   là đúng.
4. Ghi **lý do** — không phải diễn giải lại tên tầng, mà giải thích *vì sao tầng này chứng minh được
   scenario và vì sao không cần tầng cao hơn*.

### Bảng ma trận (mẫu khung, điền theo spec thật)

| FR/AC | Risk | Scenario | Layer (unit/integration/e2e/manual-only) | Reason |
|-------|------|----------|-------------------------------------------|--------|
| FR-xxx | Cao | ... | unit | Bất biến nghiệp vụ thuần, không cần I/O — chứng minh được bằng input/output thuần tuý. |
| FR-xxx | Cao | ... | integration | Cần phối hợp nhiều thành phần / persistence / hợp đồng API thật để chứng minh. |
| FR-xxx | Trung bình | ... | e2e | Là hành trình người dùng thật, xuyên nhiều màn hình — chỉ chứng minh được end-to-end. |
| FR-xxx | Thấp | ... | manual-only | Exploratory/visual, hoặc bị chặn bởi hạ tầng chưa sẵn sàng — ghi rõ lý do và điều kiện để tự động hoá sau. |

Ma trận này (cột FR/AC, Layer, Reason) là nguồn cho Pha 5 (author auto test theo tầng) và Pha 11
(hoàn thiện ma trận truy vết trong xlsx) — không lập lại từ đầu ở các pha sau, chỉ bổ sung trạng thái
chạy.

## Heuristic chọn tầng (agnostic — áp dụng bất kể framework)

- **Unit** — quy tắc/nghiệp vụ/bất biến (invariant) thuần tuý, không cần I/O thật, đầu vào/đầu ra xác
  định được trong bộ nhớ. Rẻ nhất, nhanh nhất, ổn định nhất → ưu tiên đẩy xuống đây trước.
- **Integration** — hành vi phụ thuộc phối hợp nhiều thành phần thật: persistence (DB), hợp đồng API,
  tương tác giữa service/repository/mapper. Dùng khi unit không chứng minh được vì bản chất cần trạng
  thái/hạ tầng thật (vd ràng buộc unique ở DB, transaction, side-effect xuyên bảng).
- **E2E** — hành trình người dùng thật, xuyên nhiều màn hình/nhiều lớp (UI → API → DB), nơi cái cần
  chứng minh chính là *trải nghiệm tích hợp* chứ không phải một quy tắc đơn lẻ. Tầng đắt nhất, chậm nhất,
  dễ vỡ nhất (flaky) → chỉ dùng cho critical journey + vài negative chính, không dùng để lặp lại thứ đã
  chứng minh ở tầng thấp hơn.
- **Manual-only** — exploratory (chưa biết trước kịch bản để script hoá), visual/thẩm mỹ (cần mắt
  người), hoặc bị chặn bởi hạ tầng/tool chưa sẵn sàng (ghi rõ lý do + điều kiện để sau này chuyển sang
  tự động khi hạ tầng đủ).

Nguyên tắc chọn: luôn thử tầng thấp nhất trước ("có chứng minh được ở unit không?" → nếu không thì mới
lên integration → rồi mới lên e2e). Đừng chọn tầng cao hơn chỉ vì "cho chắc" — mỗi tầng cao hơn tầng cần
thiết là chi phí duy trì không cần thiết và làm loãng pyramid (đáy phải dày nhất, đỉnh mỏng nhất).

## Ví dụ

Requirement: "Mã thiết bị (device code) phải duy nhất, không phân biệt hoa/thường, kể cả với bản ghi đã
xoá mềm (soft-deleted)."

- Risk: Cao (sai → trùng dữ liệu, sai nghiệp vụ nghiêm trọng).
- Scenario 1: Tạo mã trùng chữ hoa/thường với bản ghi đang active → phải báo lỗi.
- Scenario 2: Tạo mã trùng với bản ghi đã soft-delete → vẫn phải báo lỗi (không được coi là "đã xoá thì
  tự do dùng lại").

Chọn tầng: **integration**, không phải e2e. Lý do: ràng buộc unique kể cả với bản ghi soft-delete phụ
thuộc vào cách query/constraint thật chạm tới DB (vd EF Core query filter cho soft-delete, index/kiểm
tra ở tầng repository) — một unit test thuần (mock repository) sẽ không chứng minh được hành vi thật của
query filter, nên phải lên integration test chạm DB thật. Nhưng cũng **không cần** đẩy lên e2e: đây là
một quy tắc nghiệp vụ đơn lẻ, không phải một hành trình người dùng đa màn hình — dựng cả UI + browser
chỉ để lặp lại thứ integration test đã chứng minh là lãng phí và làm tăng rủi ro flaky vô ích.

Trong khi đó, manual TC tương ứng ("Thử tạo thiết bị với mã đã tồn tại (đổi hoa/thường) → xem thông báo
lỗi") vẫn được ghi vào xlsx cho tester chạy tay ít nhất một lần, để xác nhận UX của thông báo lỗi — đây
chính là "hai hình chiếu song song": integration test chứng minh *quy tắc đúng*, manual TC xác nhận
*trải nghiệm hiển thị đúng*. Không cái nào sinh ra từ cái kia.
