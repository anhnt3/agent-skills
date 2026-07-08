# Sinh test tự động theo tầng (Pha 5)

> *Nếu có Task/Agent tool: chạy pha này trong subagent con, chỉ nhận summary + artifact (xem "Ủy thác
> cho subagent" trong SKILL.md). Không có tool → làm inline.*

## Nội dung

1. [Đầu vào bắt buộc](#đầu-vào-bắt-buộc)
2. [Nguyên tắc chung (áp dụng mọi tầng)](#nguyên-tắc-chung-áp-dụng-mọi-tầng)
3. [Comment truy vết bắt buộc trong mọi test sinh ra](#comment-truy-vết-bắt-buộc-trong-mọi-test-sinh-ra)
4. [Chất lượng oracle (assertion) — áp dụng mọi tầng](#chất-lượng-oracle-assertion--áp-dụng-mọi-tầng)
5. [Việc phải viết cho mỗi dòng ma trận](#việc-phải-viết-cho-mỗi-dòng-ma-trận)
6. [Hướng dẫn theo tầng](#hướng-dẫn-theo-tầng-khớp-với-bảng-công-cụ-test-trong-qa-context)
7. [Requirement manual-only](#requirement-manual-only)
8. [Trước khi qua Pha 6 (quality gate)](#trước-khi-qua-pha-6-quality-gate)

## Đầu vào bắt buộc

Trước khi viết bất kỳ test nào, đọc:

1. **Ma trận coverage** (Pha 3, `coverage-matrix.md`) — nguồn duy nhất quyết định *tầng nào* cho mỗi
   FR/AC/scenario. Không tự chọn tầng lại ở đây; nếu ma trận nói `manual-only`, **không** viết test tự
   động cho dòng đó — chỉ ghi rõ trong comment/tracking là "manual-only, xem xlsx".
2. **`.agents/qa-context.md`** — bảng "Công cụ test" cho biết *framework, thư mục, lệnh* cụ thể của từng
   tầng (unit/integration/e2e/api) của project này, cộng "Đủ-để-chạy" (selector strategy, seed, auth
   E2E). **Mọi lệnh/đường dẫn/framework cụ thể lấy từ đây — không hardcode trong skill.**
3. Kết quả **scan** ở Pha 2: helper/fixture/page-object/factory đã có trong repo cho vùng tính năng liên
   quan hoặc lân cận.

Nếu qa-context thiếu field cần dùng (vd chưa ghi thư mục test tầng integration) → quay lại Pha 1/2 điền
trước, không đoán.

## Nguyên tắc chung (áp dụng mọi tầng)

- **Bám theo ma trận, không map 1:1 từ manual TC.** Một dòng ma trận có thể sinh ra 1 test, nhiều test
  (happy + boundary + negative), hoặc 0 test (manual-only).
- **Tái dùng trước khi tạo mới.** Nếu scan đã tìm thấy helper dựng dữ liệu, fixture, page object, factory
  cùng vùng tính năng → dùng lại/mở rộng chúng, không viết bản sao. Chỉ tạo helper mới khi không có gì
  tái dùng được, và đặt đúng chỗ theo convention đã thấy trong scan (cùng thư mục/naming style với test
  hiện có).
- **Selector/data test theo qa-context**, không tự bịa chiến lược khác cho riêng test này (đồng nhất
  toàn repo).
- **Không tự tạo môi trường/mock giả để né vấn đề thật** — nếu test cần DB/service thật theo đúng tầng
  (vd integration), dùng cách dựng env đã có trong qa-context (Pha 7 lo phần bring-up, ở đây chỉ viết
  test giả định env đã sẵn sàng).
- **Cấm `test.skip`/`.only`/`xit`/`xdescribe`** hay tương đương để né việc chưa chạy được — nếu thật sự
  chưa chạy được lúc author, ghi rõ lý do vào `qa-run.md`/comment và xử lý ở Pha 7, không âm thầm skip.

## Comment truy vết bắt buộc trong mọi test sinh ra

Mỗi test tự động (mỗi `it`/`Fact`/`test`/method — tuỳ ngôn ngữ mục tiêu) phải có comment ngay phía trên
(hoặc trong docstring nếu ngôn ngữ đó dùng docstring làm chuẩn) theo đúng 3 dòng, theo đúng nhãn:

```
// Requirement: FR-xxx
// Manual TC: TC-<PREFIX>-nnn (hoặc "—" nếu scenario này không có manual TC tương ứng)
// Layer: unit | integration | e2e | api
```

Đây là cách duy nhất nối test tự động với FR/AC và với dòng tương ứng trong xlsx — Pha 11 (finalize ma
trận truy vết) **grep** đúng 3 nhãn này để dựng lại "test tự động ↔ FR ↔ TC". Thiếu comment = test đó
không được tính vào ma trận truy vết dù chạy pass.

**Bắt buộc: 3 nhãn `Requirement:`, `Manual TC:`, `Layer:` phải giữ nguyên tiếng Anh, không được dịch/địa
phương hóa** — kể cả khi phần comment còn lại trong cùng file là tiếng Việt. Pha 11 grep chính xác các
chuỗi này (`Requirement:`, `Manual TC:`, `Layer:`); đổi thành `Yêu cầu:`/`Tầng:`/... sẽ khiến grep không
khớp và test đó bị coi như thiếu comment truy vết dù thực chất có.

**Ví dụ (cú pháp minh hoạ — comment style theo ngôn ngữ test thật của qa-context, ví dụ dưới dùng C#/xUnit):**

```csharp
// Requirement: FR-004
// Manual TC: TC-DEV-007
// Layer: integration
[Fact]
public async Task Create_duplicate_code_case_insensitive_including_soft_deleted_is_rejected()
{
    // Arrange: thiết bị "ABC-01" đã tồn tại (kể cả đã soft-delete)
    // Act: tạo mới với mã "abc-01"
    // Assert: bị từ chối, đúng error code nghiệp vụ — KHÔNG chỉ assert exception chung chung
}
```

## Chất lượng oracle (assertion) — áp dụng mọi tầng

- **Assert kết quả nghiệp vụ, không assert chi tiết cài đặt.** Kiểm tra cái *người dùng/hệ thống bên
  ngoài quan sát được* (giá trị trả về, trạng thái persisted, response status + body, phần tử hiển thị,
  side-effect nghiệp vụ) — không assert nội bộ implementation (private field, số lần gọi mock không liên
  quan tới hợp đồng, cấu trúc SQL cụ thể...).
- **Assertion cụ thể nhất có thể**, không assert lỏng. Ưu tiên:
  - So khớp giá trị/đối tượng chính xác thay vì chỉ "not null" hay "count > 0".
  - Assert đúng mã lỗi/thông điệp nghiệp vụ thay vì chỉ "throws exception" hay "status != 200".
  - Với danh sách/collection: assert đúng phần tử + thứ tự nếu nghiệp vụ có yêu cầu thứ tự, không chỉ
    assert độ dài.
- **Luôn có ít nhất một assertion âm (negative)** cho mỗi requirement có rule loại trừ/từ chối — không
  chỉ test happy path. Vd: input hợp lệ → chấp nhận (positive) **và** input vi phạm rule → bị từ chối
  đúng cách (negative), không chỉ dừng ở "không throw".
- **Cấm assertion tầm thường/rỗng** — `assert true`, so sánh response với chính input gửi lên mà không
  qua business logic, catch exception rồi không assert nội dung, gọi API/selector không tồn tại (đây
  cũng là điều Pha 6 quality gate sẽ chặn cơ học — nhưng phải tự tránh từ lúc author).

## Việc phải viết cho mỗi dòng ma trận

Với mỗi dòng ma trận có tầng ≠ `manual-only`, viết tối thiểu:

- **Happy path** — input hợp lệ điển hình → kết quả đúng như spec.
- **Boundary** — giá trị biên liên quan tới rule (độ dài tối đa/tối thiểu, rỗng vs có giá trị, ranh giới
  số/ngày, đầu/cuối trang phân trang...).
- **Negative** — input vi phạm rule/không hợp lệ/không có quyền → bị từ chối đúng cách (đúng mã lỗi/HTTP
  status/message nghiệp vụ, không chỉ "không crash").

Thêm khi risk trong ma trận gắn cờ:

- **Security** (risk liên quan phân quyền/lộ dữ liệu/injection) — test truy cập trái phép bị chặn, dữ
  liệu của user khác không lộ ra, input độc hại không được chấp nhận nguyên trạng.
- **Concurrency** (risk liên quan race condition/unique constraint/đồng thời sửa cùng bản ghi) — test
  hai thao tác đụng nhau (vd tạo trùng đồng thời, update đồng thời cùng entity) phải kết thúc đúng theo
  ràng buộc nghiệp vụ (một cái thắng, cái kia bị từ chối rõ ràng — không silent overwrite/không duplicate
  lọt qua).

Không thêm test ngoài phạm vi ma trận "cho chắc" — mỗi test phải trace được về đúng 1 FR/AC + lý do
trong ma trận; test không trace được là tín hiệu tầng/scope chọn sai, quay lại Pha 3 sửa ma trận trước.

## Hướng dẫn theo tầng (khớp với bảng "Công cụ test" trong qa-context)

Bảng qa-context liệt kê tối đa 4 tầng: **unit / integration / e2e / api**. Với mỗi tầng, dùng framework +
thư mục + lệnh đã ghi trong qa-context; hướng dẫn viết bên dưới là generic, áp dụng bất kể framework cụ
thể là gì.

Bộ 4 tầng này là **mặc định**, không phải danh sách đóng — nếu qa-context của project khai báo thêm tầng
first-class khác (vd `contract`, `component`, `snapshot`) kèm framework/thư mục/lệnh cụ thể, các tầng đó
vẫn hợp lệ để dùng trong nhãn `Layer:` và trong ma trận, theo đúng cách qa-context đã định nghĩa.

### Unit

- Cô lập hoàn toàn: không I/O thật (không DB/network/filesystem/clock hệ thống không kiểm soát được).
  Dùng test double (stub/fake) cho mọi dependency, theo cách project đã làm (xem helper có sẵn từ scan).
- Input/output xác định trong bộ nhớ; assert trực tiếp giá trị trả về hoặc state của object dưới test.
- Nhanh, ổn định — nếu một test "unit" cần dựng service/DB thật để chạy, nó thuộc integration, không phải
  unit (quay lại kiểm tra ma trận).
- Tái dùng builder/factory dựng object test đã có trong repo thay vì new thủ công từng field.

**Ví dụ (minh hoạ — TypeScript/Vitest):**
```ts
// Requirement: FR-002
// Manual TC: TC-DEV-003
// Layer: unit
it('maps ABP {items,totalCount} response to the existing signal shape without changing the Observable contract', () => {
  // Arrange: response giả {items:[...], totalCount:5}
  // Act: gọi service.map(...)
  // Assert: object trả về đúng field đã map + totalCount, KHÔNG chỉ assert "không undefined"
});
```

### Integration

- Chạm hạ tầng thật tối thiểu cần thiết để chứng minh scenario (DB thật/service thật/mapper thật) theo
  đúng lý do đã ghi trong ma trận — không mock phần cần chứng minh (vd không mock chính DB constraint mà
  scenario tồn tại để chứng minh nó).
- Dữ liệu test: seed/dọn theo cách "Đủ-để-chạy" trong qa-context (mỗi test tự seed dữ liệu nó cần, tự dọn
  sau khi chạy — không phụ thuộc thứ tự chạy của test khác, không để lại rác ảnh hưởng test sau).
- Assert cả kết quả trả về **và** trạng thái persisted khi rule liên quan tới persistence (vd sau khi tạo
  → query lại DB để xác nhận đúng constraint, không chỉ tin response).
- Tái dùng DbContext/test-fixture/base-class dựng sẵn nếu scan tìm thấy (vd base test class quản lý
  transaction rollback theo test, factory tạo entity).

### E2E

- Chỉ cho critical journey + vài negative chính theo ma trận (Pha 3 đã lọc — nếu thấy đang viết E2E lặp
  lại thứ integration đã chứng minh, đó là dấu hiệu sai tầng, quay lại ma trận).
- Selector theo đúng chiến lược trong qa-context (vd data-testid) — không tự chọn selector khác (text
  match dễ vỡ khi đổi ngôn ngữ/copy) trừ khi qa-context cho phép.
- Auth: dùng cơ chế session/storage-state đã định nghĩa trong qa-context, không tự chế login flow riêng
  cho từng test (chậm, dễ vỡ, không nhất quán).
- Assert trên trạng thái hiển thị cuối cùng người dùng thấy được (nội dung, điều hướng, thông báo lỗi
  inline) — không assert vào chi tiết DOM/network call nội bộ không phải hợp đồng UX.
- Dọn dữ liệu tạo ra trong lúc chạy (qua API/seed helper) để test độc lập, lặp lại được.

### API

- Assert theo hợp đồng: status code, shape response, field bắt buộc, mã lỗi nghiệp vụ khi có — dùng
  APIRequestContext/HTTP client đã có trong qa-context, không mở browser để test cái vốn chỉ cần HTTP.
- Cùng nguyên tắc happy/boundary/negative: request hợp lệ → đúng response; thiếu field/permission/id
  không tồn tại → đúng status + đúng body lỗi (không chỉ "không phải 200").
- Với phân trang/lọc (ABP `PagedAndSortedResultRequestDto`-style hoặc tương đương của qa-context): test
  boundary trang đầu/cuối, `maxResultCount` biên, sort field không hợp lệ.

## Requirement manual-only

Khi ma trận Pha 3 gán một FR/AC là `manual-only`, không viết test tự động cho nó ở pha này. Thay vào đó:

- Không tạo file/case test tự động rỗng "để giữ chỗ".
- Đảm bảo lý do manual-only từ ma trận được mang nguyên vào cột "Test tự động" (để trống) + ghi chú của
  xlsx (Pha 4/11) — không lặp lại việc giải thích ở đây, chỉ đảm bảo không có test tự động nào bị viết
  cho dòng này rồi tình cờ fail/skip.

## Trước khi qua Pha 6 (quality gate)

Tự rà nhanh mọi test vừa viết:

- Mỗi test có đủ 3 dòng comment truy vết đúng format.
- Mỗi FR ở tầng ≠ manual-only trong ma trận có ít nhất happy + negative (boundary khi áp dụng được).
- Không có `skip`/`.only`/tương đương.
- Không có assertion tầm thường (xem mục "Chất lượng oracle" ở trên) — Pha 6 sẽ chặn cơ học phần này,
  nhưng tự kiểm trước để tránh vòng lặp sửa đi sửa lại.
