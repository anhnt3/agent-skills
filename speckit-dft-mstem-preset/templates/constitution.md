<!--
Sync Impact Report
- Version: 1.0.0 (bản generic — áp dụng cho hệ fullstack doanh nghiệp bất kỳ, không gắn 1 stack cụ thể).
- Nguyên tắc (11):
  I. Contract-First  II. Chất lượng Mã nguồn  III. Kỷ luật Kiểm thử  IV. Nhất quán UX
  V. Hiệu năng  VI. Bảo mật & Phân quyền  VII. Nghiệp vụ Tiến hóa  VIII. Observability
  IX. API Versioning  X. Toàn vẹn Dữ liệu & Bất biến  XI. Multi-tenancy (tùy chọn, xóa nếu single-tenant)
- Chi tiết stack cụ thể (ngôn ngữ, framework FE/BE, database, nhà cung cấp danh tính, UI kit,
  locale/thị trường sản phẩm...) KHÔNG nằm trong hiến chương này — ghi ở `CLAUDE.md`/`AGENTS.md`
  của dự án. Hiến chương chỉ nêu ràng buộc bất biến bất kể chọn công cụ nào.
- Nguyên tắc lọc: điều gì tự đúng khi đã chọn 1 stack/công cụ cụ thể thì KHÔNG nêu ở đây; chỉ ghi
  ràng buộc ai đó có thể làm sai và ta muốn chặn.
- Template: plan/spec/tasks-template.md ✅ tương thích; file này ✅.
- TODO còn treo: không.
-->

# Hiến chương Dự án

Hệ thống fullstack doanh nghiệp: frontend nối backend qua API/hợp đồng dữ liệu. Chi tiết stack cụ
thể (ngôn ngữ, framework, database, nhà cung cấp danh tính, UI kit, locale/thị trường sản phẩm...)
được ghi trong `CLAUDE.md`/`AGENTS.md` của dự án — hiến chương này chỉ nêu ràng buộc áp dụng bất kể
chọn công cụ nào.

## Các Nguyên tắc Cốt lõi

### I. Nối Frontend–Backend theo Hợp đồng (Contract-First)
- Mỗi domain gọi API qua đúng một service layer (client SDK/service module) dùng chung; UI
  component/view KHÔNG gọi HTTP client trực tiếp.
- Biên API dùng kiểu dữ liệu tường minh (DTO/schema có kiểu); cấm kiểu bất định (`any`/dynamic/
  object không rõ schema) ở biên công khai. Kiểu phía client ánh xạ đúng kiểu phía server, không tự
  suy diễn lại gây vênh.
- Một tính năng chỉ "xong" khi toàn bộ mock/stub/dữ liệu giả tạm thời liên quan đã bị XÓA (kể cả
  code chết), không chỉ ngừng dùng.

_Vì:_ hợp đồng là nguồn sự thật giúp mock/prototype và API thật không trôi lệch.

### II. Chất lượng Mã nguồn (KHÔNG THỎA HIỆP)
Chuẩn kỹ thuật khách quan, KHÔNG lấy codebase hiện tại (kể cả prototype/mock) làm thước đo.
- **Type safety:** giữ mức kiểm tra kiểu nghiêm ngặt nhất mà ngôn ngữ/framework hỗ trợ; cấm kiểu
  bất định ở biên công khai; nới lỏng phải biện minh.
- **Phân tích tĩnh (tách khỏi format):** mỗi tầng (frontend/backend) PHẢI bật linter/static
  analyzer phù hợp ngôn ngữ, coi cảnh báo nghiêm trọng là lỗi. Format tự động hóa bằng công cụ
  chuẩn của stack, không tranh luận thủ công. Cả hai xanh trước merge.
- **Ranh giới tầng:** logic nghiệp vụ không nằm ở controller, lớp truy cập dữ liệu, hay component
  UI.
- **Độ phức tạp tương xứng:** chọn giải pháp đơn giản nhất còn đúng; nâng cấp state/trừu tượng chỉ
  khi có nhu cầu chứng minh được. Không cấm công cụ theo tên, không trừu tượng đầu cơ.
- **DRY:** không nhân bản component/logic/kiểu đã có; trùng lặp có chủ đích phải ghi lý do.
- **Không "hoàn thành giả":** `TODO` stub, `test.skip`/`.only`, catch rỗng, nhánh chưa hiện thực là
  blocker.

_Vì:_ chất lượng đến từ ràng buộc máy kiểm được, không từ việc lặp lại lựa chọn người viết trước.

### III. Kỷ luật Kiểm thử
- Backend: mỗi domain object nghiệp vụ, service tầng ứng dụng, endpoint có phân quyền PHẢI kèm
  unit test; quy tắc nghiệp vụ có test ở tầng domain. Test scaffold/mẫu do framework sinh sẵn phải
  được thay bằng test thật, không để lẫn.
- Frontend: service/module gọi API PHẢI có unit test (mock HTTP); component/view có logic (guard,
  render theo quyền, form) PHẢI có test. Không tắt test mặc định của scaffold/generator.
- DTO/schema đổi một phía mà phía kia chưa cập nhật thì một test/kiểm tra kiểu PHẢI fail.
- **Anchor test ổn định (FE):** phần tử tương tác trên critical journey (nút, input, dòng bảng,
  dialog, nhãn trạng thái) PHẢI mang thuộc tính định danh ổn định (vd `data-testid`) **đặt ngay khi
  dựng màn** — không neo test vào text hiển thị hay markup của UI kit (vỡ khi đổi label/copy/theme).

_Vì:_ test là bản ghi hành vi đã thống nhất và rào chắn hồi quy.

### IV. Nhất quán Trải nghiệm Người dùng
Mọi spec/plan/tasks/UI PHẢI tuân thủ các nguyên lý sau; vi phạm = CRITICAL. Giá trị concrete (ngôn
ngữ/locale sản phẩm, độ dài field, dung lượng, wording chính xác, thứ tự toolbar, format ngày/tiền
tệ) do `CLAUDE.md`/design system của dự án định nghĩa, nhất quán với các nguyên lý này:

1. **Ngôn ngữ & locale nhất quán, không ngoại lệ.** Toàn bộ UI dùng đúng 1 ngôn ngữ + locale sản
   phẩm đã chọn (định nghĩa ở `CLAUDE.md`) — không trộn ngôn ngữ, không thiếu ký tự đặc biệt của
   ngôn ngữ đó. Format ngày/giờ/tiền tệ/số thập phân theo đúng 1 chuẩn locale, không tự chế mỗi màn.
   Chuỗi hiển thị không nhúng cứng vào logic (để i18n về sau khả thi).
2. **Message chuẩn hóa, không tự chế.** Phản hồi thành công/lỗi theo mẫu chung, không alert tùy
   tiện; mỗi kết quả thao tác và mỗi lỗi thống nhất về nội dung câu quy định — không paraphrase.
   Thuật ngữ hành động (sửa/tạo/xuất...) thống nhất toàn hệ thống theo bảng thuật ngữ chuẩn của dự
   án.
3. **Validation trước khi tin dữ liệu.** Trim, chặn quá max, chặn all-whitespace ở required; kiểu
   tài chính không bao giờ float; mỗi field có giới hạn và luật định dạng xác định.
4. **Vị trí quyết định ý nghĩa.** Lỗi validation field hiển thị inline dưới field (không chỉ đổi
   màu viền). Kết quả thao tác / lỗi hệ thống hiển thị qua kênh riêng (toast/banner) nhất quán vị
   trí. Không trộn hai kênh.
5. **Bố cục nhất quán, dự đoán được.** Dùng khung layout + UI kit dùng chung, UI tự chế mới cần lý
   do; list cùng cấu trúc toolbar và sort mặc định; primary action có vị trí/kiểu nhất quán; form
   trong dialog theo mẫu tiêu đề/nút chung. User không học lại layout giữa các màn.
6. **Hành động phá hủy phải xác nhận và an toàn.** Xóa qua dialog xác nhận chuẩn, không xóa trực
   tiếp 1 click; nút hành động phá hủy có style/vị trí nhất quán theo design system dự án, disable
   sau click đầu; ràng buộc nghiệp vụ chặn xóa khi cần; debounce mọi action button chống
   double-submit.
7. **Trạng thái luôn tường minh.** Mọi view dữ liệu xử lý rõ 4 trạng thái: loading, empty, error, có
   dữ liệu. Tác vụ dài có loading; trạng thái entity map cố định nhãn+màu; bảng rỗng có empty state
   và luôn hiện tổng số.
8. **Truy cập được (a11y — mốc WCAG 2.1 AA).** Control có tên truy cập được, dialog quản lý focus,
   điều hướng bàn phím đầy đủ, tooltip khi nội dung bị cắt. Không bao giờ chỉ dùng màu để truyền
   trạng thái — luôn kèm nhãn/biểu tượng. UI mới không làm giảm a11y dưới AA.
9. **Thích ứng, không mất tính năng.** Cùng chức năng chạy Desktop/Tablet/Mobile (khi dự án hỗ trợ
   đa kích thước màn hình); layout co giãn nhưng không ẩn mất hành động hay dữ liệu cốt lõi ở màn
   nhỏ.
10. **UI phản ánh quyền.** Ẩn hoặc disable hành động theo quyền; không hiển thị nút mà thao tác sẽ
    bị từ chối. Quyền kế thừa nhất quán theo mô hình phân quyền của dự án.

_Vì:_ một sản phẩm nhiều module; người dùng phải cảm nhận một hệ thống duy nhất.

### V. Hiệu năng & Tối ưu
- Tôn trọng ngân sách hiệu năng (bundle size/build budget) đã cấu hình cho dự án; thư viện nặng chỉ
  tải nơi dùng (lazy-load/code-split).
- Danh sách phân trang/lọc/sắp xếp phía server; frontend KHÔNG tải cả tập không giới hạn để lọc
  client.
- Truy vấn backend tránh N+1 và tập kết quả vô hạn; thêm index có chủ đích.
- Tác vụ dài hiện tiến trình hoặc dùng background process, không chặn UI thread.

_Vì:_ hiệu năng thiết kế từ tầng truy vấn và payload, không vá về sau.

### VI. Bảo mật & Phân quyền
- Nếu dự án dùng nhà cung cấp danh tính ngoài (external IdP/SSO): backend đóng vai resource server,
  validate token (JWT/OAuth2) qua IdP đó, không tự vận hành authorization server song song trừ khi
  có lý do rõ. Có JIT-provision user cục bộ từ IdP thì khóa theo định danh ngoài (external subject
  id) để giữ FK/audit/permission nội bộ nhất quán. Không tính năng nào ship dựa trên login
  mock/giả lập.
- Mọi endpoint nghiệp vụ được phân quyền qua cơ chế permission/policy/role của framework đang dùng;
  không endpoint ẩn danh ngoài whitelist công khai đã duyệt. Route guard/permission-check phía
  frontend phản chiếu đúng phân quyền backend, không tự suy diễn riêng.
- File upload validate phía server: loại + dung lượng theo whitelist (không tin `Content-Type`/đuôi
  client), tên file làm sạch, lưu ngoài webroot/không thực thi được. Không dựa validate client.
- Secret/connection string/chứng chỉ không vào source. Input tại biên tin cậy validate phía server
  bất kể client đã validate.

_Vì:_ hệ thống vận hành trên dữ liệu người dùng thật; phân quyền là tính năng hạng nhất.

### VII. Nghiệp vụ Tiến hóa (Sự thật Nghiệp vụ)
Khi hệ thống bắt đầu từ mock/prototype/giả định ban đầu (không phải mọi dự án đều có giai đoạn
này): quy tắc nghiệp vụ trong đó là tạm thời.
- Khi hiện thực lộ sai lệch: nêu ra và giải quyết có chủ đích (spec/clarify), không âm thầm code
  lách.
- Hợp đồng backend đã thống nhất là nguồn sự thật; frontend + mock được sửa theo, không giữ giả
  định cũ.
- Thay đổi ý nghĩa nghiệp vụ được ghi lại để module sau kế thừa.

_Vì:_ "giả định ban đầu đã sai" là kết cục bình thường khi quy tắc nghiệp vụ gặp thực tế; có ghi
nhận.

### VIII. Khả năng Quan sát (Observability)
- Backend: structured logging kèm correlation id xuyên request; log lỗi có ngữ cảnh, KHÔNG nuốt
  exception.
- Bật audit log (cơ chế có sẵn của framework hoặc tự xây) cho mọi thao tác ghi dữ liệu nghiệp vụ
  quan trọng (ai, khi nào, đổi gì, phạm vi nào).
- Frontend: interceptor log lỗi API kèm mã trace để đối chiếu backend.
- Log KHÔNG chứa secret, token, hay PII.

_Vì:_ lần lại "request nào, phạm vi nào, đổi gì" quyết định thời gian khắc phục.

### IX. Phiên bản API & Tương thích ngược (API Versioning)
Nhiều phiên bản frontend/client cùng chạy trên một backend; hợp đồng phải tiến hóa không phá client
đang triển khai.
- Thay đổi phá vỡ (xóa field, đổi kiểu/ngữ nghĩa) đi qua phiên bản mới, không sửa tại chỗ endpoint
  đang phục vụ. Thay đổi tương thích (thêm field optional) không cần version mới.
- Endpoint cũ giữ trong thời gian deprecation có công bố trước khi gỡ.
- Thay đổi contract được ghi lại (changelog/spec).

_Vì:_ frontend triển khai không đồng bộ với backend; phá contract âm thầm làm hỏng phiên bản chưa
kịp cập nhật.

### X. Toàn vẹn Dữ liệu & Bất biến Nghiệp vụ
Toàn vẹn dữ liệu quan hệ và bất biến miền cưỡng chế ở tầng domain + DB, không dựa UI/client.
- **Xóa an toàn:** xóa bị chặn khi còn tham chiếu (FK restrict mặc định); KHÔNG cascade xóa dữ liệu
  nghiệp vụ âm thầm — cascade phải có chủ đích, ghi trong spec.
- **Soft-delete nhất quán (nếu dự án dùng):** quy ước đánh dấu xóa mềm áp dụng đồng bộ — mọi truy
  vấn lọc, unique index tính tới row đã xóa mềm, xóa mềm cha xử lý con tường minh.
- **Bất biến miền:** mỗi domain object nêu bất biến của nó trong spec (trạng thái hợp lệ, số học,
  quan hệ bắt buộc, khoảng thời gian) và cưỡng chế ở domain + ràng buộc DB; validate không chỉ ở
  form.
- **Uniqueness theo ngữ cảnh:** ràng buộc duy nhất xác định rõ phạm vi (vd theo tenant nếu
  multi-tenant), cưỡng chế bằng unique index, tính tới soft-delete.
- **Mutation idempotent:** import/đồng bộ/retry không tạo trùng; double-submit chặn cả phía server
  (IV.6 debounce chỉ là bề mặt).
- **Chống ghi đè đồng thời:** record tài chính/phê duyệt/có nhiều người sửa PHẢI dùng optimistic
  concurrency (version/rowversion); xung đột báo cho người dùng, không lặng lẽ ghi đè (lost
  update). CRUD đơn giản tùy spec.

_Vì:_ hỏng toàn vẹn quan hệ hoặc ghi đè mất dữ liệu là sự cố nặng; UI confirm chỉ là bề mặt.

### XI. Đa người thuê & Cô lập Dữ liệu (Multi-tenancy — TÙY CHỌN)
> Nguyên tắc độc lập: dự án single-tenant XÓA toàn bộ mục XI này, không ảnh hưởng I–X.

Cô lập dữ liệu giữa các tenant là bất biến an toàn số một.
- Mọi entity nghiệp vụ thuộc tenant PHẢI dùng cơ chế multi-tenancy có sẵn của framework (nếu có);
  không tự viết lọc tenant thủ công rải rác.
- Truy vấn vượt biên tenant chỉ được phép có chủ đích trong ngữ cảnh cấp hệ thống (Host/Admin toàn
  cục), kèm phân quyền cấp đó rõ ràng.
- Tách rõ tính năng cấp hệ thống và cấp tenant; permission + guard + vai trò phản ánh ranh giới
  này.
- Test cô lập là BẮT BUỘC mỗi domain object: tenant A không đọc/ghi được dữ liệu tenant B.
- Migration/seed không rò rỉ dữ liệu giữa tenant.

_Vì:_ rò rỉ dữ liệu chéo tenant là sự cố nghiêm trọng nhất trong SaaS đa khách hàng; cô lập mặc
định, vượt biên tường minh.

## Ràng buộc Kiến trúc

- Lớp seam dữ liệu: một service/module frontend ↔ một service tầng ứng dụng backend cho mỗi domain,
  chia sẻ kiểu dữ liệu (DTO/schema). Một lớp interceptor/middleware HTTP duy nhất lo gắn token auth
  + chuẩn hóa lỗi.
- Environment và API base URL là cấu hình, không hardcode.
- Thay đổi schema đi qua migration tool của ORM/DB đang dùng, review như code.

## Quy trình & Cổng Chất lượng

- Specify → Plan → Tasks → Implement; cổng Constitution Check trong plan PHẢI pass trước khi hiện
  thực.
- Mỗi thay đổi: build xanh, lint + format xanh, test theo Nguyên tắc III pass.
- Review kiểm theo nguyên tắc: mock/prototype đã gỡ (I), không stub + lint (II), test (III), trạng
  thái UX + tuân thủ convention (IV), phân trang/budget (V), phân quyền (VI), toàn vẹn dữ liệu +
  bất biến (X), cô lập tenant (XI, nếu multi-tenant).
- Viết và review là hai lượt tách biệt; không tự phê duyệt.

## Điều hành (Governance)

Hiến chương thay thế thực hành tùy tiện; khi xung đột, hiến chương thắng. `CLAUDE.md`/`AGENTS.md`/
README của từng phần code cung cấp chi tiết vận hành cụ thể (stack, quy ước, công cụ) nhưng không
được mâu thuẫn hiến chương.

- Sửa đổi: qua PR sửa file này, kèm Sync Impact Report + lý do, chủ dự án phê duyệt. Template phụ
  thuộc cập nhật cùng thay đổi khi một nguyên tắc đổi thứ chúng cưỡng chế.
- Phiên bản (semantic): MAJOR = gỡ/định nghĩa lại không tương thích; MINOR = thêm/mở rộng; PATCH =
  làm rõ.
- Tuân thủ: Constitution Check là điểm cưỡng chế; vi phạm phải sửa hoặc biện minh trong Complexity
  Tracking, vi phạm không biện minh chặn merge.
- Tài liệu sống: dự kiến nhiều bản sửa MINOR khi các module được nối (Nguyên tắc VII).

**Version**: 1.0.0 | **Ratified (Phê chuẩn)**: [NGÀY PHÊ CHUẨN] | **Last Amended (Sửa gần nhất)**: [NGÀY PHÊ CHUẨN]
