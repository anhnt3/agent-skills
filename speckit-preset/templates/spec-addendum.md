## Tuân thủ Hiến chương — mặt Nghiệp vụ *(bắt buộc — điền hoặc N/A có lý do)*

<!--
  ACTION REQUIRED: Chỉ ghi mặt WHAT/hành vi/business-rule (spec = WHAT + WHY, không HOW).
  Cơ chế kỹ thuật (test, versioning, observability, DTO map, DB constraint...) thuộc plan.md — KHÔNG ghi ở đây.
  Mỗi mục: điền ràng buộc cụ thể HOẶC "N/A vì ...". Đánh dấu nguồn: [từ mock] / [suy luận] / [cần bạn quyết].
-->

- **I. Contract-First (định nghĩa Done)**: Mock service/data phải XÓA khi xong: [liệt kê mock của chức năng]. (Cơ chế map DTO → plan.)
- **IV. Nhất quán UX**: Theo TỪNG màn —
  - Message thành công/lỗi (nội dung câu chính xác, không paraphrase; thuật ngữ "Chỉnh sửa"/"Tạo mới"/"Xuất tài liệu"): [điền]
  - Field limit + luật validate (max, all-whitespace, kiểu tài chính không float): [điền]
  - Vị trí lỗi: validation inline dưới field / kết quả-thao-tác + lỗi hệ thống ở toast góc dưới phải
  - 4 trạng thái: loading / empty / error / có dữ liệu; bảng luôn hiện tổng số
  - a11y AA; UI phản ánh quyền (ẩn/disable theo permission)
  - Format: dd/MM/yyyy, VNĐ, thập phân `,`
- **V. Hiệu năng (chỉ Success Criteria đo được)**: [vd "danh sách trả về <1s", "chịu N bản ghi không giảm hiệu năng"; hoặc N/A]. (N+1/index/pagination cơ chế → plan.)
- **VI. Phân quyền (yêu cầu nghiệp vụ)**: Ai được làm gì — permission theo hành động: [vd "chỉ role Quản trị được Xóa"]. Upload cho phép loại/dung lượng nào (nếu có): [điền]. (Keycloak/JWT/rate-limit cơ chế → plan.)
- **VII. Sai lệch nghiệp vụ (ghi chú)**: Sai lệch mock vs contract phát hiện khi phỏng vấn, và quyết định: [ghi lại, hoặc N/A].
- **X. Bất biến nghiệp vụ (WHAT)**: Mỗi aggregate — trạng thái hợp lệ, quan hệ bắt buộc, luật số học (thuế/tổng), phạm vi uniqueness (theo tenant?): [điền]. (rowversion/DB constraint/soft-delete cơ chế → plan.)
- **XI. Cô lập tenant (yêu cầu)**: Chức năng thuộc Host hay Tenant; dữ liệu tenant A không lộ cho B: [điền, hoặc N/A vì single-tenant]. (ABP mechanism + isolation test → plan.)

### Wire mock → backend (theo màn) *(bắt buộc)*

<!-- Mỗi function/button/action/label/text đang mock cần wire backend. Liệt kê theo từng màn (trừ trivial). -->

| Màn | Phần tử mock | Hành vi mong đợi | Permission | Ghi chú/nguồn |
|-----|--------------|------------------|------------|---------------|
| [tên màn] | [nút/field/action] | [điều xảy ra khi wire thật] | [permission] | [nguồn] |
