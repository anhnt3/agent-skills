## Constitution Check — mặt Kỹ thuật (HOW) *(GATE: PHẢI pass trước Phase 0, re-check sau Phase 1)*

<!--
  ACTION REQUIRED: Đây là cổng cưỡng chế các nguyên tắc thuộc plan/tasks (HOW).
  Mặt nghiệp vụ (WHAT) đã ở spec.md — không lặp lại ở đây.
  Mỗi mục: nêu cách hiện thực cụ thể HOẶC "N/A vì ...". Vi phạm không biện minh = chặn merge (ghi Complexity Tracking).
-->

- **I. Contract-First (cơ chế)**: DTO frontend ↔ Application.Contracts map thế nào; một Angular domain service ↔ một ABP app service per aggregate; component không gọi `HttpClient` trực tiếp: [điền].
- **II. Chất lượng mã**: strict type (cấm `any` biên công khai); ESLint + backend analyzers xanh; logic nghiệp vụ không nằm ở controller/DbContext/component; không stub/`test.skip`/catch rỗng: [xác nhận cách đảm bảo].
- **III. Kiểm thử**: Test bắt buộc kèm chức năng — backend: aggregate/app service/endpoint có phân quyền (xUnit), domain rule; frontend: service gọi API (mock HTTP), component có logic. Integration dùng DB thật (Testcontainers). Thay `Sample*`/`skipTests` mặc định: [liệt kê test].
- **V. Hiệu năng (cơ chế)**: pagination/filter/sort phía server; tránh N+1; index có chủ đích; tác vụ dài background: [điền, hoặc N/A].
- **VI. Bảo mật (cơ chế)**: Keycloak Direct Grant (ROPC) / identity broker; ABP JWT resource server; permission ABP định nghĩa; rate-limit login (bù no-MFA — ADR-010); upload validate server-side (whitelist loại+dung lượng, sanitize tên, lưu ngoài webroot): [điền].
- **VIII. Observability**: structured logging + correlation id; ABP Audit Log cho thao tác ghi; interceptor FE log lỗi API kèm trace; log không chứa secret/token/PII: [điền, hoặc N/A].
- **IX. API Versioning**: thay đổi phá vỡ đi qua version mới (không sửa tại chỗ endpoint đang phục vụ); deprecation công bố; ghi changelog contract: [điền, hoặc N/A vì chỉ thêm field optional].
- **X. Toàn vẹn dữ liệu (cơ chế)**: FK restrict (chặn xóa khi còn tham chiếu); cascade có chủ đích; soft-delete `IsDeleted` nhất quán (query lọc, unique index tính row đã xóa); bất biến cưỡng chế ở domain + DB constraint; optimistic concurrency (rowversion) cho record tài chính/nhiều người sửa; mutation idempotent: [điền].
- **XI. Multi-tenancy (cơ chế)**: dùng cơ chế multi-tenancy ABP (không tự lọc `TenantId`); test cô lập mỗi aggregate (A không đọc/ghi được của B); migration/seed không rò rỉ chéo: [điền, hoặc N/A vì single-tenant].
