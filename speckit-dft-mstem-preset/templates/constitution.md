<!--
Sync Impact Report
- Version: 1.0.0 (bản đầu).
- Nguyên tắc (11):
  I. Contract-First  II. Chất lượng Mã nguồn  III. Kỷ luật Kiểm thử  IV. Nhất quán UX
  V. Hiệu năng  VI. Bảo mật & Phân quyền  VII. Nghiệp vụ Tiến hóa  VIII. Observability
  IX. API Versioning  X. Toàn vẹn Dữ liệu & Bất biến  XI. Multi-tenancy (tùy chọn, xóa nếu single-tenant)
- Template: plan/spec/tasks-template.md ✅ tương thích; file này ✅.
- Nguyên tắc lọc: điều gì tự đúng khi đã chọn Angular/ABP thì KHÔNG nêu; chỉ ghi ràng buộc ai
  đó có thể làm sai và ta muốn chặn.
- TODO còn treo: không.
-->

# Hiến chương Dự án

Nền tảng quản trị fullstack: Angular 21 SPA (hiện là mockup) nối backend greenfield ABP 10.5 / .NET 10 / PostgreSQL. Giai đoạn này: xây backend thật, thay toàn bộ mock bằng API thật.

## Các Nguyên tắc Cốt lõi

### I. Nối Frontend–Backend theo Hợp đồng (Contract-First)
- Mỗi domain gọi API qua đúng một Angular service; component KHÔNG gọi `HttpClient` trực tiếp.
- Biên API dùng DTO có kiểu tường minh; cấm `any`. DTO frontend ánh xạ DTO Application.Contracts.
- Một tính năng chỉ "xong" khi mock đã bị XÓA (kể cả mock service chết), không chỉ bị bỏ qua.

_Vì:_ hợp đồng là nguồn sự thật giúp mock và API không trôi lệch.

### II. Chất lượng Mã nguồn (KHÔNG THỎA HIỆP)
Chuẩn kỹ thuật khách quan, KHÔNG lấy codebase mockup hiện tại làm thước đo.
- **Type safety:** giữ strict nghiêm ngặt nhất; cấm `any` ở biên công khai; nới lỏng phải biện minh.
- **Phân tích tĩnh (tách khỏi format):** frontend PHẢI có ESLint, backend bật analyzers coi cảnh báo nghiêm trọng là lỗi. Format (Prettier/.DotSettings) không tranh luận. Cả hai xanh trước merge.
- **Ranh giới tầng:** logic nghiệp vụ không nằm ở controller, DbContext, hay component UI.
- **Độ phức tạp tương xứng:** chọn giải pháp đơn giản nhất còn đúng; nâng cấp state/trừu tượng chỉ khi có nhu cầu chứng minh được. Không cấm công cụ theo tên, không trừu tượng đầu cơ.
- **DRY:** không nhân bản component/logic/kiểu đã có; trùng lặp có chủ đích phải ghi lý do.
- **Không "hoàn thành giả":** `TODO` stub, `test.skip`/`.only`, catch rỗng, nhánh chưa hiện thực là blocker.

_Vì:_ chất lượng đến từ ràng buộc máy kiểm được, không từ việc lặp lại lựa chọn người viết trước.

### III. Kỷ luật Kiểm thử
- Backend: mỗi aggregate, app service, endpoint có phân quyền PHẢI kèm unit test; quy tắc nghiệp vụ có test tầng domain. Thay test `Sample*` mặc định bằng test thật, không để lẫn.
- Frontend: service gọi API PHẢI có unit test (mock HTTP); component có logic (guard, render theo quyền, form) PHẢI có test. Ghi đè mặc định `skipTests`.
- DTO đổi một phía mà phía kia chưa cập nhật thì một test/kiểm tra kiểu PHẢI fail.
- **Anchor test ổn định (FE):** phần tử tương tác trên critical journey (nút, input, dòng bảng, dialog, nhãn trạng thái) PHẢI mang `data-testid` **đặt ngay khi dựng màn** — không neo test vào text tiếng Việt hay markup PrimeNG (vỡ khi đổi label/copy). 

_Vì:_ test là bản ghi hành vi đã thống nhất và rào chắn hồi quy.

### IV. Nhất quán Trải nghiệm Người dùng
Mọi spec/plan/tasks/UI PHẢI tuân thủ các nguyên lý sau; vi phạm = CRITICAL. Giá trị concrete (độ dài field, dung lượng, wording chính xác, thứ tự toolbar, format ngày) do từng tính năng định trong spec, nhất quán với các nguyên lý này:

1. **Tiếng Việt bản địa, không ngoại lệ.** Tiếng Việt là ngôn ngữ sản phẩm; mọi text UI có dấu; `vi-VN`, UTC+7; ngày `dd/MM/yyyy`, tiền `VNĐ`, thập phân dấu `,`. Không màn hình/thông báo nào tiếng Anh hay thiếu dấu. Chuỗi không nhúng vào logic (để i18n về sau khả thi).
2. **Message chuẩn hóa, không tự chế.** Phản hồi thành công/lỗi theo mẫu chung, không alert tùy tiện; mỗi kết quả thao tác và mỗi lỗi thống nhất về nội dung câu quy định — không paraphrase. Thuật ngữ cố định: "Chỉnh sửa", "Tạo mới", "Xuất tài liệu" (không "Sửa/Edit/Cập nhật", không "Xuất CSV/Excel").
3. **Validation trước khi tin dữ liệu.** Trim, chặn quá max, chặn all-whitespace ở required; kiểu tài chính không bao giờ float; mỗi field có giới hạn và luật định dạng xác định.
4. **Vị trí quyết định ý nghĩa.** Lỗi validation field hiển thị inline dưới field (không đổi màu viền). Kết quả thao tác / lỗi hệ thống hiển thị toast góc dưới phải. Không trộn hai kênh.
5. **Bố cục nhất quán, dự đoán được.** Dùng khung layout + UI kit dùng chung, UI tự chế mới cần lý do; list cùng cấu trúc toolbar và sort mặc định; primary action solid accent ngoài cùng phải; form trong Dialog với tiêu đề/nút theo mẫu. User không học lại layout giữa các màn.
6. **Hành động phá hủy phải xác nhận và an toàn.** Xóa qua Alert Dialog xác nhận chuẩn, nút đỏ phải, disable sau click đầu; ràng buộc chặn xóa; debounce mọi action button chống double-submit.
7. **Trạng thái luôn tường minh.** Mọi view dữ liệu xử lý rõ 4 trạng thái: loading, empty, error, có dữ liệu. Tác vụ dài có loading; trạng thái entity map cố định nhãn+màu; bảng rỗng có empty state và luôn hiện tổng số.
8. **Truy cập được (a11y — mốc WCAG 2.1 AA).** Control có tên truy cập được, dialog quản lý focus, điều hướng bàn phím đầy đủ, tooltip khi nội dung bị cắt. Không bao giờ chỉ dùng màu để truyền trạng thái — luôn kèm nhãn/biểu tượng. UI mới không làm giảm a11y dưới AA.
9. **Thích ứng, không mất tính năng.** Cùng chức năng chạy Desktop/Tablet/Mobile; layout co giãn nhưng không ẩn mất hành động hay dữ liệu cốt lõi ở màn nhỏ.
10. **UI phản ánh quyền.** Ẩn hoặc disable hành động theo quyền; không hiển thị nút mà thao tác sẽ bị từ chối. Quyền kế thừa nhất quán (tick Thêm/Sửa/Xóa auto-tick Xem).

_Vì:_ một sản phẩm nhiều module; người dùng phải cảm nhận một hệ thống duy nhất.

### V. Hiệu năng & Tối ưu
- Tôn trọng build budget cấu hình trong `angular.json`; thư viện nặng chỉ tải nơi dùng.
- Danh sách phân trang/lọc/sắp xếp phía server; frontend KHÔNG tải cả tập không giới hạn để lọc client.
- Truy vấn backend tránh N+1 và tập kết quả vô hạn; thêm index có chủ đích.
- Tác vụ dài hiện tiến trình hoặc dùng background process, không chặn UI thread.

_Vì:_ hiệu năng thiết kế từ tầng truy vấn và payload, không vá về sau.

### VI. Bảo mật & Phân quyền
- Auth qua Keycloak (external IdP, source of truth user/pass/role): user/pass qua backend-mediated Direct Grant (ROPC), social qua identity broker redirect. ABP là resource server validate JWT (`AddJwtBearer`, Authority = Keycloak realm), KHÔNG chạy OpenIddict server. JIT shadow-user (AbpUser Id = Keycloak `sub`) giữ FK/audit/permission. Không tính năng nào ship dựa login mock.
- Mọi endpoint nghiệp vụ được phân quyền qua ABP permission (định nghĩa theo từng tính năng); không endpoint ẩn danh. Route guard frontend phản chiếu permission backend.
- File upload validate phía server: loại + dung lượng theo whitelist (không tin `Content-Type`/đuôi client), tên file làm sạch, lưu ngoài webroot/không thực thi được. Không dựa validate client.
- Secret/connection string/chứng chỉ không vào source. Input tại biên tin cậy validate phía server bất kể client đã validate.

_Vì:_ console vận hành trên dữ liệu khách hàng doanh nghiệp; phân quyền là tính năng hạng nhất.

### VII. Nghiệp vụ Tiến hóa (Sự thật Nghiệp vụ)
Frontend là mockup; quy tắc nghiệp vụ của nó là tạm thời.
- Khi hiện thực lộ sai lệch: nêu ra và giải quyết có chủ đích (spec/clarify), không âm thầm code lách.
- Hợp đồng backend đã thống nhất là nguồn sự thật; frontend + mock được sửa theo, không giữ giả định cũ.
- Thay đổi ý nghĩa nghiệp vụ được ghi lại để module sau kế thừa.

_Vì:_ "mock đã sai" là kết cục bình thường khi quy tắc nghiệp vụ gặp thực tế; có ghi nhận.

### VIII. Khả năng Quan sát (Observability)
- Backend: structured logging kèm correlation id xuyên request; log lỗi có ngữ cảnh, KHÔNG nuốt exception.
- Bật ABP Audit Log cho mọi thao tác ghi dữ liệu nghiệp vụ (ai, khi nào, đổi gì, tenant nào).
- Frontend: interceptor log lỗi API kèm mã trace để đối chiếu backend.
- Log KHÔNG chứa secret, token, hay PII.

_Vì:_ lần lại "request nào, tenant nào, đổi gì" quyết định thời gian khắc phục.

### IX. Phiên bản API & Tương thích ngược (API Versioning)
Nhiều phiên bản frontend/client cùng chạy trên một backend; hợp đồng phải tiến hóa không phá client đang triển khai.
- Thay đổi phá vỡ (xóa field, đổi kiểu/ngữ nghĩa) đi qua phiên bản mới, không sửa tại chỗ endpoint đang phục vụ. Thay đổi tương thích (thêm field optional) không cần version mới.
- Endpoint cũ giữ trong thời gian deprecation có công bố trước khi gỡ.
- Thay đổi contract được ghi lại (changelog/spec).

_Vì:_ frontend triển khai không đồng bộ với backend; phá contract âm thầm làm hỏng phiên bản chưa kịp cập nhật.

### X. Toàn vẹn Dữ liệu & Bất biến Nghiệp vụ
Toàn vẹn dữ liệu quan hệ và bất biến miền cưỡng chế ở tầng domain + DB, không dựa UI/client.
- **Xóa an toàn:** xóa bị chặn khi còn tham chiếu (FK restrict mặc định); KHÔNG cascade xóa dữ liệu nghiệp vụ âm thầm — cascade phải có chủ đích, ghi trong spec.
- **Soft-delete nhất quán:** quy ước `IsDeleted` áp dụng đồng bộ — mọi truy vấn lọc, unique index tính tới row đã xóa mềm, xóa mềm cha xử lý con tường minh.
- **Bất biến miền:** mỗi aggregate nêu bất biến của nó trong spec (trạng thái hợp lệ, số học, quan hệ bắt buộc, khoảng thời gian) và cưỡng chế ở domain + ràng buộc DB; validate không chỉ ở form.
- **Uniqueness theo ngữ cảnh:** ràng buộc duy nhất xác định rõ phạm vi (thường theo tenant), cưỡng chế bằng unique index, tính tới soft-delete.
- **Mutation idempotent:** import/đồng bộ/retry không tạo trùng; double-submit chặn cả phía server (IV.6 debounce chỉ là bề mặt).
- **Chống ghi đè đồng thời:** record tài chính/phê duyệt/có nhiều người sửa PHẢI dùng optimistic concurrency (version/rowversion); xung đột báo cho người dùng, không lặng lẽ ghi đè (lost update). CRUD đơn giản tùy spec.

_Vì:_ hỏng toàn vẹn quan hệ hoặc ghi đè mất dữ liệu là sự cố nặng ngang rò rỉ tenant; UI confirm chỉ là bề mặt.

### XI. Đa người thuê & Cô lập Dữ liệu (Multi-tenancy — TÙY CHỌN)
> Nguyên tắc độc lập: dự án single-tenant XÓA toàn bộ mục XI này, không ảnh hưởng I–X.

Cô lập dữ liệu giữa các tenant là bất biến an toàn số một.
- Mọi entity nghiệp vụ thuộc tenant PHẢI dùng cơ chế multi-tenancy của ABP; không tự viết lọc `TenantId` thủ công.
- Truy vấn vượt biên tenant chỉ được phép có chủ đích trong ngữ cảnh Host, kèm phân quyền cấp Host rõ ràng.
- Tách rõ tính năng cấp Host và cấp Tenant; permission + guard + vai trò phản ánh ranh giới này.
- Test cô lập là BẮT BUỘC mỗi aggregate: tenant A không đọc/ghi được dữ liệu tenant B.
- Migration/seed không rò rỉ dữ liệu giữa tenant.

_Vì:_ rò rỉ dữ liệu chéo tenant là sự cố nghiêm trọng nhất trong SaaS enterprise; cô lập mặc định, vượt biên tường minh.

## Ràng buộc Kiến trúc

- Lớp seam dữ liệu: một domain service frontend ↔ một ABP app service backend cho mỗi aggregate, chia sẻ DTO. Một HTTP interceptor duy nhất lo token auth + chuẩn hóa lỗi.
- Environment và API base URL là cấu hình, không hardcode.
- Thay đổi schema đi qua EF Core migration, review như code.

## Quy trình & Cổng Chất lượng

- Specify → Plan → Tasks → Implement; cổng Constitution Check trong plan PHẢI pass trước khi hiện thực.
- Mỗi thay đổi: build xanh, lint + format xanh, test theo Nguyên tắc III pass.
- Review kiểm theo nguyên tắc: mock đã gỡ (I), không stub + lint (II), test (III), trạng thái UX + tuân thủ convention (IV), phân trang/budget (V), phân quyền (VI), toàn vẹn dữ liệu + bất biến (X), cô lập tenant (XI, nếu multi-tenant).
- Viết và review là hai lượt tách biệt; không tự phê duyệt.

## Điều hành (Governance)

Hiến chương thay thế thực hành tùy tiện; khi xung đột, hiến chương thắng. File hướng dẫn theo agent (`angular/CLAUDE.md`, `aspnet-core/README.md`) cung cấp chi tiết vận hành nhưng không được mâu thuẫn.

- Sửa đổi: qua PR sửa file này, kèm Sync Impact Report + lý do, chủ dự án phê duyệt. Template phụ thuộc cập nhật cùng thay đổi khi một nguyên tắc đổi thứ chúng cưỡng chế.
- Phiên bản (semantic): MAJOR = gỡ/định nghĩa lại không tương thích; MINOR = thêm/mở rộng; PATCH = làm rõ.
- Tuân thủ: Constitution Check là điểm cưỡng chế; vi phạm phải sửa hoặc biện minh trong Complexity Tracking, vi phạm không biện minh chặn merge.
- Tài liệu sống: dự kiến nhiều bản sửa MINOR khi các module được nối (Nguyên tắc VII).

**Version**: 1.0.0 | **Ratified (Phê chuẩn)**: 2026-07-06 | **Last Amended (Sửa gần nhất)**: 2026-07-06
