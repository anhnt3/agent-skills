# Roadmap Build — mSTEM Quản trị

**Mục tiêu**: thứ tự build/hoàn thiện từng màn/chức năng.
**Cập nhật**: 2026-08-08
**Trạng thái item**: `chưa` (mặc định) / `đang` / `xong`.

## Bảng tổng (thứ tự build)

| ID | Màn | Module | Wave | Phụ thuộc | Trạng thái |
|--------|-----|--------|------|-----------|------------|
| [RM-001](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/01-dang-nhap/03-mo-ta-chuc-nang/01-dang-nhap.md) | Đăng nhập | auth | 0 | N/A | chưa |
| [RM-002](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/01-quan-ly-nguoi-quan-tri/03-mo-ta-chuc-nang/03-quan-ly-nhom-quyen.md) | Quản lý nhóm quyền | system/roles | 0 | RM-001 | chưa |
| [RM-003](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/01-quan-ly-nguoi-quan-tri/03-mo-ta-chuc-nang/02-quan-ly-nhom-nguoi-dung-quan-tri.md) | Quản lý nhóm người dùng quản trị | system/groups | 0 | RM-002 | chưa |
| [RM-004](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/01-quan-ly-nguoi-quan-tri/03-mo-ta-chuc-nang/01-quan-ly-nguoi-dung-quan-tri.md) | Quản lý người dùng quản trị | system/admins | 0 | RM-003 | chưa |
| [RM-005](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/04-thiet-lap-cai-dat/03-mo-ta-chuc-nang/01-cai-dat-chung.md) | Cài đặt chung | system/settings | 0 | RM-001 | chưa |
| [RM-006](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/04-thiet-lap-cai-dat/03-mo-ta-chuc-nang/02-cau-hinh-mail-server-sms.md) | Cấu hình Mail Server, SMS | system/settings | 0 | RM-005 | chưa |
| [RM-007](brd/02-nhom-chuc-nang-portal/01-giao-dien-trang-portal/02-dang-ky-dang-nhap/03-mo-ta-chuc-nang/01-dang-ky-dang-nhap.md) | Đăng ký đăng nhập | portal/auth | 0 | RM-001 | chưa |
| [RM-008](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/02-quan-ly-doanh-nghiep-nha-truong-trung-tam/03-mo-ta-chuc-nang/01-thong-tin-doanh-nghiep.md) | Thông tin doanh nghiệp | system/enterprises | 1 | RM-004 | chưa |
| [RM-009](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/01-quan-ly-danh-muc-thiet-bi.md) | Quản lý danh mục thiết bị | khdn/devices | 1 | RM-004 | chưa |
| [RM-010](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/02-quan-ly-goi-dich-vu/03-mo-ta-chuc-nang/01-quan-ly-goi-dich-vu-noi-dung-gia-tri.md) | Quản lý gói dịch vụ (nội dung, giá trị) | khdn/packages | 1 | RM-004 | chưa |
| [RM-011](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/02-quan-ly-thong-tin-ca-nhan/03-mo-ta-chuc-nang/01-trang-thong-tin-ca-nhan.md) | Trang thông tin cá nhân | profile | 1 | RM-001 | chưa |
| [RM-012](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/02-quan-ly-thong-tin-ca-nhan/03-mo-ta-chuc-nang/03-thong-bao-cua-he-thong.md) | Thông báo của hệ thống | notifications | 1 | RM-006 | chưa |
| [RM-013](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/02-quan-ly-nhap-thiet-bi.md) | Quản lý nhập thiết bị | khdn/devices | 2 | RM-009 | chưa |
| [RM-014](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/04-quan-ly-kho-thiet-bi.md) | Quản lý kho thiết bị | khdn/devices | 2 | RM-013 | chưa |
| [RM-015](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/03-quan-ly-ban-thiet-bi.md) | Quản lý bán thiết bị | khdn/devices | 2 | RM-014 | chưa |
| [RM-016](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/05-quan-ly-thu-hoi-doi-tra-cho-khach-hang.md) | Quản lý thu hồi đổi trả cho khách hàng | khdn/devices | 2 | RM-015 | chưa |
| [RM-017](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/02-quan-ly-doanh-nghiep-nha-truong-trung-tam/03-mo-ta-chuc-nang/02-thong-tin-ho-so-thanh-toan-cua-tai-khoan.md) | Thông tin hồ sơ thanh toán của tài khoản | system/enterprises | 2 | RM-008 | chưa |
| [RM-018](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/01-tich-hop-cong-thanh-toan-thanh-toan-qua-the-visa-ngan-hang.md) | Tích hợp cổng thanh toán (thanh toán qua thẻ visa, ngân hàng,...) | khdn/payments | 2 | RM-017, RM-010 | chưa |
| [RM-019](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/02-lich-su-doanh-nghiep-dang-ky-goi-dich-vu.md) | Lịch sử doanh nghiệp đăng ký gói dịch vụ | khdn/packages | 2 | RM-010 | chưa |
| [RM-020](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/03-lich-su-giao-dich-voi-doanh-nghiep.md) | Lịch sử giao dịch với doanh nghiệp | khdn/payments | 2 | RM-018 | chưa |
| [RM-021](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/01-quan-ly-firmware-cho-robot.md) | Quản lý firmware cho Robot | system/firmware | 2 | RM-009 | chưa |
| [RM-022](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/02-download-phien-ban-firmware-cho-robot.md) | Download phiên bản firmware cho Robot | system/firmware | 2 | RM-021 | chưa |
| [RM-023](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/03-quan-ly-firmware-cho-smart-home.md) | Quản lý firmware cho Smart Home | system/firmware | 2 | RM-009 | chưa |
| [RM-024](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/04-download-phien-ban-firmware-cho-smart-home.md) | Download phiên bản firmware cho Smart Home | system/firmware | 2 | RM-023 | chưa |
| [RM-025](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/01-quan-ly-khieu-nai.md) | Quản lý khiếu nại | khdn/complaints | 2 | RM-008 | chưa |
| [RM-026](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/02-quan-ly-cau-hoi-thuong-gap.md) | Quản lý Câu hỏi thường gặp | khdn/complaints | 2 | RM-025 | chưa |
| [RM-027](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/05-chuong-trinh-khuyen-mai/03-mo-ta-chuc-nang/01-quan-ly-chuong-trinh-khuyen-mai.md) | Quản lý chương trình khuyến mãi | khdn/promotions | 2 | RM-010 | chưa |
| [RM-028](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/06-tich-diem-doi-qua/03-mo-ta-chuc-nang/01-quan-ly-tich-diem-doi-qua.md) | Quản lý tích điểm đổi quà | khdn/loyalty | 2 | RM-010 | chưa |
| [RM-029](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/02-quan-ly-thong-tin-ca-nhan/03-mo-ta-chuc-nang/02-quan-ly-lich-su-su-dung-ca-nhan.md) | Quản lý lịch sử sử dụng cá nhân | profile | 2 | RM-011 | chưa |
| [RM-030](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/03-giam-sat-he-thong-phan-cung-phan-mem-log-truy-cap/03-mo-ta-chuc-nang/01-quan-ly-lich-su-hoat-dong.md) | Quản lý lịch sử hoạt động | system/monitoring | 2 | RM-004 | chưa |
| [RM-031](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/01-quan-ly-noi-dung-gioi-thieu-chung/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-gioi-thieu-chung.md) | Quản lý nội dung Giới thiệu chung | portal/cms | 3 | RM-004 | chưa |
| [RM-032](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/02-quan-ly-noi-dung-thong-tin-cong-dong/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-thong-tin-cong-dong.md) | Quản lý nội dung Thông tin cộng đồng | portal/cms | 3 | RM-004 | chưa |
| [RM-033](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/03-quan-ly-noi-dung-gioi-thieu-san-pham/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-gioi-thieu-san-pham.md) | Quản lý nội dung Giới thiệu sản phẩm | portal/cms | 3 | RM-004 | chưa |
| [RM-034](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/04-quan-ly-noi-dung-gioi-thieu-chuong-trinh-dao-tao/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-gioi-thieu-chuong-trinh-dao-tao.md) | Quản lý nội dung Giới thiệu chương trình đào tạo | portal/cms | 3 | RM-004 | chưa |
| [RM-035](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/05-quan-ly-noi-dung-tai-lieu-san-pham/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-tai-lieu-san-pham.md) | Quản lý nội dung Tài liệu sản phẩm | portal/cms | 3 | RM-004 | chưa |
| [RM-036](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/06-quan-ly-gian-hang/03-mo-ta-chuc-nang/01-quan-ly-gian-hang.md) | Quản lý Gian hàng | portal/cms | 3 | RM-004 | chưa |
| [RM-037](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/07-quan-ly-lien-he/03-mo-ta-chuc-nang/01-quan-ly-lien-he.md) | Quản lý Liên hệ | portal/cms | 3 | RM-004 | chưa |
| [RM-038](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/08-quan-ly-noi-dung-huong-dan-su-dung/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-huong-dan-su-dung.md) | Quản lý nội dung Hướng dẫn sử dụng | portal/cms | 3 | RM-004 | chưa |
| [RM-039](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/09-quan-ly-chinh-sach-dieu-khoan/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-chinh-sach-dieu-khoan.md) | Quản lý nội dung chính sách, điều khoản | portal/cms | 3 | RM-004 | chưa |
| [RM-040](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/10-quan-ly-dien-dan/03-mo-ta-chuc-nang/01-quan-ly-dien-dan-cau-hoi.md) | Quản lý diễn đàn câu hỏi | portal/cms | 3 | RM-007 | chưa |
| [RM-041](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/10-quan-ly-dien-dan/03-mo-ta-chuc-nang/02-quan-ly-dien-dan-bai-viet.md) | Quản lý diễn đàn bài viết | portal/cms | 3 | RM-007 | chưa |
| [RM-042](brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/10-quan-ly-dien-dan/03-mo-ta-chuc-nang/03-quan-ly-noi-dung-xau-doc.md) | Quản lý nội dung xấu độc | portal/cms | 3 | RM-040, RM-041 | chưa |
| [RM-043](brd/02-nhom-chuc-nang-portal/01-giao-dien-trang-portal/01-noi-dung-trang-portal/03-mo-ta-chuc-nang/01-noi-dung-trang-portal.md) | Nội dung trang portal | portal/site | 3 | RM-031, RM-033, RM-036 | chưa |
| [RM-044](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/03-giam-sat-he-thong-phan-cung-phan-mem-log-truy-cap/03-mo-ta-chuc-nang/02-bao-cao-giam-sat.md) | Báo cáo giám sát | system/monitoring | 4 | RM-030 | chưa |
| [RM-045](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/06-bao-cao-thiet-bi.md) | Báo cáo thiết bị | khdn/devices | 4 | RM-014 | chưa |
| [RM-046](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/02-quan-ly-goi-dich-vu/03-mo-ta-chuc-nang/02-bao-cao-lich-su-thay-doi-goi-dich-vu.md) | Báo cáo lịch sử thay đổi gói dịch vụ | khdn/packages | 4 | RM-010 | chưa |
| [RM-047](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/04-bao-cao-tong-hop-khach-hang.md) | Báo cáo tổng hợp khách hàng | khdn/payments | 4 | RM-008 | chưa |
| [RM-048](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/05-bao-cao-phat-trien-khach-hang.md) | Báo cáo phát triển khách hàng | khdn/payments | 4 | RM-008 | chưa |
| [RM-049](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/06-bao-cao-doanh-thu-san-luong-khach-hang.md) | Báo cáo doanh thu sản lượng khách hàng | khdn/payments | 4 | RM-020 | chưa |
| [RM-050](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/07-bao-cao-phan-bo-doanh-thu-khach-hang-theo-goi.md) | Báo cáo phân bổ doanh thu khách hàng theo gói | khdn/payments | 4 | RM-020 | chưa |
| [RM-051](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/03-bao-cao-tong-quan-khieu-nai-va-xu-li-khieu-nai-khach-hang.md) | Báo cáo tổng quan khiếu nại và xử lí khiếu nại khách hàng | khdn/complaints | 4 | RM-025 | chưa |
| [RM-052](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/04-bao-cao-lich-su-khieu-nai-va-xu-li-khieu-nai-khach-hang.md) | Báo cáo lịch sử khiếu nại và xử lí khiếu nại khách hàng | khdn/complaints | 4 | RM-025 | chưa |
| [RM-053](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/05-chuong-trinh-khuyen-mai/03-mo-ta-chuc-nang/02-bao-cao-chuong-trinh-khuyen-mai.md) | Báo cáo chương trình khuyến mãi | khdn/promotions | 4 | RM-027 | chưa |
| [RM-054](brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/06-tich-diem-doi-qua/03-mo-ta-chuc-nang/02-bao-cao-tich-diem-doi-qua.md) | Báo cáo tích điểm đổi quà | khdn/loyalty | 4 | RM-028 | chưa |

## Chi tiết

<!-- Mỗi item một khối. ID khớp bảng tổng. Giữ nguyên khối cũ khi cập nhật (không clobber Trạng thái + Nợ phát sinh). -->

### RM-001 — Đăng nhập (auth, Wave 0)

- **Mô tả**: Đăng nhập hệ thống quản trị: xác thực tài khoản quản trị, ghi nhận phiên làm việc, xử lý sai mật khẩu và khoá tài khoản
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/01-dang-nhap/03-mo-ta-chuc-nang/01-dang-nhap.md
- **Thực thể/CRUD**: Admin/Session — đăng nhập, đăng xuất, đổi mật khẩu
- **Phụ thuộc**: N/A
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-002 — Quản lý nhóm quyền (system/roles, Wave 0)

- **Mô tả**: Quản lý nhóm quyền: định nghĩa tập quyền theo tài nguyên và hành động, gán cho nhóm người dùng
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/01-quan-ly-nguoi-quan-tri/03-mo-ta-chuc-nang/03-quan-ly-nhom-quyen.md
- **Thực thể/CRUD**: Role/Permission — thêm, sửa, xoá, gán quyền
- **Phụ thuộc**: RM-001
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-003 — Quản lý nhóm người dùng quản trị (system/groups, Wave 0)

- **Mô tả**: Quản lý nhóm người dùng quản trị: tạo nhóm, gán nhóm quyền, phân bổ thành viên
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/01-quan-ly-nguoi-quan-tri/03-mo-ta-chuc-nang/02-quan-ly-nhom-nguoi-dung-quan-tri.md
- **Thực thể/CRUD**: AdminGroup — thêm, sửa, xoá, gán nhóm quyền
- **Phụ thuộc**: RM-002
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-004 — Quản lý người dùng quản trị (system/admins, Wave 0)

- **Mô tả**: Quản lý người dùng quản trị: tạo, khoá, phân nhóm và thiết lập quyền cho tài khoản quản trị
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/01-quan-ly-nguoi-quan-tri/03-mo-ta-chuc-nang/01-quan-ly-nguoi-dung-quan-tri.md
- **Thực thể/CRUD**: Admin — thêm, sửa, xoá, khoá/mở khoá, reset mật khẩu
- **Phụ thuộc**: RM-003
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-005 — Cài đặt chung (system/settings, Wave 0)

- **Mô tả**: Cài đặt chung của hệ thống: tham số vận hành, chính sách mật khẩu, phiên làm việc
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/04-thiet-lap-cai-dat/03-mo-ta-chuc-nang/01-cai-dat-chung.md
- **Thực thể/CRUD**: Setting — xem, sửa
- **Phụ thuộc**: RM-001
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-006 — Cấu hình Mail Server, SMS (system/settings, Wave 0)

- **Mô tả**: Cấu hình Mail Server và SMS: khai báo máy chủ gửi, mẫu thông báo, kiểm thử gửi thử
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/04-thiet-lap-cai-dat/03-mo-ta-chuc-nang/02-cau-hinh-mail-server-sms.md
- **Thực thể/CRUD**: MailConfig/SmsConfig — xem, sửa, gửi thử
- **Phụ thuộc**: RM-005
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-007 — Đăng ký đăng nhập (portal/auth, Wave 0)

- **Mô tả**: Đăng ký và đăng nhập cổng portal cho người dùng ngoài: tự đăng ký, xác thực email/SMS, quên mật khẩu
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/01-giao-dien-trang-portal/02-dang-ky-dang-nhap/03-mo-ta-chuc-nang/01-dang-ky-dang-nhap.md
- **Thực thể/CRUD**: PortalUser — đăng ký, xác thực, đăng nhập, khôi phục mật khẩu
- **Phụ thuộc**: RM-001
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-008 — Thông tin doanh nghiệp (system/enterprises, Wave 1)

- **Mô tả**: Thông tin doanh nghiệp/nhà trường/trung tâm: hồ sơ khách hàng tổ chức, trạng thái hợp tác
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/02-quan-ly-doanh-nghiep-nha-truong-trung-tam/03-mo-ta-chuc-nang/01-thong-tin-doanh-nghiep.md
- **Thực thể/CRUD**: Enterprise — thêm, sửa, xoá, tra cứu
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-009 — Quản lý danh mục thiết bị (khdn/devices, Wave 1)

- **Mô tả**: Quản lý danh mục thiết bị: khai báo chủng loại, model, thông số kỹ thuật làm gốc cho mọi nghiệp vụ kho
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/01-quan-ly-danh-muc-thiet-bi.md
- **Thực thể/CRUD**: DeviceCategory — thêm, sửa, xoá, tra cứu
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-010 — Quản lý gói dịch vụ (nội dung, giá trị) (khdn/packages, Wave 1)

- **Mô tả**: Quản lý gói dịch vụ: khai báo nội dung, giá trị, thời hạn và điều kiện áp dụng của từng gói
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/02-quan-ly-goi-dich-vu/03-mo-ta-chuc-nang/01-quan-ly-goi-dich-vu-noi-dung-gia-tri.md
- **Thực thể/CRUD**: ServicePackage — thêm, sửa, xoá, kích hoạt
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-011 — Trang thông tin cá nhân (profile, Wave 1)

- **Mô tả**: Trang thông tin cá nhân: xem và cập nhật hồ sơ, đổi mật khẩu, thiết lập cá nhân
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/02-quan-ly-thong-tin-ca-nhan/03-mo-ta-chuc-nang/01-trang-thong-tin-ca-nhan.md
- **Thực thể/CRUD**: UserProfile — xem, sửa
- **Phụ thuộc**: RM-001
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-012 — Thông báo của hệ thống (notifications, Wave 1)

- **Mô tả**: Thông báo của hệ thống: hộp thông báo, đánh dấu đã đọc, cấu hình kênh nhận
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/02-quan-ly-thong-tin-ca-nhan/03-mo-ta-chuc-nang/03-thong-bao-cua-he-thong.md
- **Thực thể/CRUD**: Notification — xem, đánh dấu đã đọc, thiết lập
- **Phụ thuộc**: RM-006
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-013 — Quản lý nhập thiết bị (khdn/devices, Wave 2)

- **Mô tả**: Quản lý nhập thiết bị: lập phiếu nhập, nhập theo lô/serial, duyệt và ghi tăng tồn kho
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/02-quan-ly-nhap-thiet-bi.md
- **Thực thể/CRUD**: DeviceInbound — thêm, sửa, duyệt, huỷ
- **Phụ thuộc**: RM-009
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-014 — Quản lý kho thiết bị (khdn/devices, Wave 2)

- **Mô tả**: Quản lý kho thiết bị: theo dõi tồn theo kho/serial, điều chuyển, kiểm kê
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/04-quan-ly-kho-thiet-bi.md
- **Thực thể/CRUD**: DeviceStock — tra cứu, điều chuyển, kiểm kê
- **Phụ thuộc**: RM-013
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-015 — Quản lý bán thiết bị (khdn/devices, Wave 2)

- **Mô tả**: Quản lý bán thiết bị: lập phiếu bán cho khách hàng, ghi giảm tồn, gắn thiết bị vào doanh nghiệp
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/03-quan-ly-ban-thiet-bi.md
- **Thực thể/CRUD**: DeviceSale — thêm, sửa, duyệt, huỷ
- **Phụ thuộc**: RM-014
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-016 — Quản lý thu hồi đổi trả cho khách hàng (khdn/devices, Wave 2)

- **Mô tả**: Quản lý thu hồi đổi trả cho khách hàng: tiếp nhận yêu cầu, xử lý đổi/trả, ghi nhận lại tồn kho
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/05-quan-ly-thu-hoi-doi-tra-cho-khach-hang.md
- **Thực thể/CRUD**: DeviceReturn — thêm, sửa, duyệt, hoàn tất
- **Phụ thuộc**: RM-015
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-017 — Thông tin hồ sơ thanh toán của tài khoản (system/enterprises, Wave 2)

- **Mô tả**: Thông tin hồ sơ thanh toán của tài khoản: phương thức thanh toán, thông tin xuất hoá đơn của doanh nghiệp
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/02-quan-ly-doanh-nghiep-nha-truong-trung-tam/03-mo-ta-chuc-nang/02-thong-tin-ho-so-thanh-toan-cua-tai-khoan.md
- **Thực thể/CRUD**: BillingProfile — thêm, sửa, xoá
- **Phụ thuộc**: RM-008
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-018 — Tích hợp cổng thanh toán (thanh toán qua thẻ visa, ngân hàng,...) (khdn/payments, Wave 2)

- **Mô tả**: Tích hợp cổng thanh toán qua thẻ visa và ngân hàng: khởi tạo giao dịch, đối soát kết quả, xử lý lỗi
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/01-tich-hop-cong-thanh-toan-thanh-toan-qua-the-visa-ngan-hang.md
- **Thực thể/CRUD**: PaymentTransaction — khởi tạo, đối soát, hoàn tiền
- **Phụ thuộc**: RM-017, RM-010
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-019 — Lịch sử doanh nghiệp đăng ký gói dịch vụ (khdn/packages, Wave 2)

- **Mô tả**: Lịch sử doanh nghiệp đăng ký gói dịch vụ: theo dõi đăng ký, gia hạn, huỷ gói theo từng doanh nghiệp
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/02-lich-su-doanh-nghiep-dang-ky-goi-dich-vu.md
- **Thực thể/CRUD**: PackageSubscription — tra cứu, xuất dữ liệu
- **Phụ thuộc**: RM-010
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-020 — Lịch sử giao dịch với doanh nghiệp (khdn/payments, Wave 2)

- **Mô tả**: Lịch sử giao dịch với doanh nghiệp: nhật ký thu chi, trạng thái thanh toán từng giao dịch
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/03-lich-su-giao-dich-voi-doanh-nghiep.md
- **Thực thể/CRUD**: PaymentTransaction — tra cứu, xuất dữ liệu
- **Phụ thuộc**: RM-018
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-021 — Quản lý firmware cho Robot (system/firmware, Wave 2)

- **Mô tả**: Quản lý firmware cho Robot: tải lên phiên bản, ghi chú thay đổi, phát hành và thu hồi bản phát hành
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/01-quan-ly-firmware-cho-robot.md
- **Thực thể/CRUD**: RobotFirmware — thêm, sửa, phát hành, thu hồi
- **Phụ thuộc**: RM-009
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-022 — Download phiên bản firmware cho Robot (system/firmware, Wave 2)

- **Mô tả**: Download phiên bản firmware cho Robot: cấp phát bản tải về cho thiết bị, theo dõi lượt tải
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/02-download-phien-ban-firmware-cho-robot.md
- **Thực thể/CRUD**: RobotFirmwareDownload — tra cứu, tải về
- **Phụ thuộc**: RM-021
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-023 — Quản lý firmware cho Smart Home (system/firmware, Wave 2)

- **Mô tả**: Quản lý firmware cho Smart Home: tải lên phiên bản, ghi chú thay đổi, phát hành và thu hồi bản phát hành
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/03-quan-ly-firmware-cho-smart-home.md
- **Thực thể/CRUD**: SmartHomeFirmware — thêm, sửa, phát hành, thu hồi
- **Phụ thuộc**: RM-009
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-024 — Download phiên bản firmware cho Smart Home (system/firmware, Wave 2)

- **Mô tả**: Download phiên bản firmware cho Smart Home: cấp phát bản tải về cho thiết bị, theo dõi lượt tải
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/05-quan-ly-phien-ban-cap-nhat-firmware/03-mo-ta-chuc-nang/04-download-phien-ban-firmware-cho-smart-home.md
- **Thực thể/CRUD**: SmartHomeFirmwareDownload — tra cứu, tải về
- **Phụ thuộc**: RM-023
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-025 — Quản lý khiếu nại (khdn/complaints, Wave 2)

- **Mô tả**: Quản lý khiếu nại: tiếp nhận, phân công xử lý, cập nhật tiến độ và đóng khiếu nại của khách hàng
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/01-quan-ly-khieu-nai.md
- **Thực thể/CRUD**: Complaint — thêm, phân công, cập nhật, đóng
- **Phụ thuộc**: RM-008
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-026 — Quản lý Câu hỏi thường gặp (khdn/complaints, Wave 2)

- **Mô tả**: Quản lý Câu hỏi thường gặp: biên tập bộ câu hỏi đáp, phân nhóm chủ đề, xuất bản ra portal
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/02-quan-ly-cau-hoi-thuong-gap.md
- **Thực thể/CRUD**: Faq — thêm, sửa, xoá, xuất bản
- **Phụ thuộc**: RM-025
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-027 — Quản lý chương trình khuyến mãi (khdn/promotions, Wave 2)

- **Mô tả**: Quản lý chương trình khuyến mãi: thiết lập điều kiện, phạm vi áp dụng, thời gian và mức ưu đãi theo gói
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/05-chuong-trinh-khuyen-mai/03-mo-ta-chuc-nang/01-quan-ly-chuong-trinh-khuyen-mai.md
- **Thực thể/CRUD**: Promotion — thêm, sửa, duyệt, kết thúc
- **Phụ thuộc**: RM-010
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-028 — Quản lý tích điểm đổi quà (khdn/loyalty, Wave 2)

- **Mô tả**: Quản lý tích điểm đổi quà: cấu hình quy tắc tích điểm, danh mục quà, duyệt yêu cầu đổi quà
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/06-tich-diem-doi-qua/03-mo-ta-chuc-nang/01-quan-ly-tich-diem-doi-qua.md
- **Thực thể/CRUD**: LoyaltyPoint/Reward — thêm, sửa, duyệt đổi quà
- **Phụ thuộc**: RM-010
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-029 — Quản lý lịch sử sử dụng cá nhân (profile, Wave 2)

- **Mô tả**: Quản lý lịch sử sử dụng cá nhân: nhật ký thao tác và phiên làm việc của chính người dùng
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/02-quan-ly-thong-tin-ca-nhan/02-quan-ly-thong-tin-ca-nhan/03-mo-ta-chuc-nang/02-quan-ly-lich-su-su-dung-ca-nhan.md
- **Thực thể/CRUD**: UserActivity — tra cứu, lọc theo thời gian
- **Phụ thuộc**: RM-011
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-030 — Quản lý lịch sử hoạt động (system/monitoring, Wave 2)

- **Mô tả**: Quản lý lịch sử hoạt động: nhật ký truy cập và thao tác toàn hệ thống phục vụ giám sát, truy vết
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/03-giam-sat-he-thong-phan-cung-phan-mem-log-truy-cap/03-mo-ta-chuc-nang/01-quan-ly-lich-su-hoat-dong.md
- **Thực thể/CRUD**: AuditLog — tra cứu, lọc, xuất dữ liệu
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-031 — Quản lý nội dung Giới thiệu chung (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung Giới thiệu chung: biên tập, duyệt và xuất bản khối nội dung giới thiệu trên portal
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/01-quan-ly-noi-dung-gioi-thieu-chung/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-gioi-thieu-chung.md
- **Thực thể/CRUD**: CmsArticle — thêm, sửa, duyệt, xuất bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-032 — Quản lý nội dung Thông tin cộng đồng (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung Thông tin cộng đồng: biên tập tin bài cộng đồng, phân loại chuyên mục, xuất bản
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/02-quan-ly-noi-dung-thong-tin-cong-dong/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-thong-tin-cong-dong.md
- **Thực thể/CRUD**: CmsArticle — thêm, sửa, duyệt, xuất bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-033 — Quản lý nội dung Giới thiệu sản phẩm (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung Giới thiệu sản phẩm: biên tập trang sản phẩm, hình ảnh, thông số hiển thị ra portal
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/03-quan-ly-noi-dung-gioi-thieu-san-pham/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-gioi-thieu-san-pham.md
- **Thực thể/CRUD**: CmsProduct — thêm, sửa, duyệt, xuất bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-034 — Quản lý nội dung Giới thiệu chương trình đào tạo (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung Giới thiệu chương trình đào tạo: biên tập khoá đào tạo, lịch, tài liệu kèm theo
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/04-quan-ly-noi-dung-gioi-thieu-chuong-trinh-dao-tao/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-gioi-thieu-chuong-trinh-dao-tao.md
- **Thực thể/CRUD**: CmsTrainingProgram — thêm, sửa, duyệt, xuất bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-035 — Quản lý nội dung Tài liệu sản phẩm (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung Tài liệu sản phẩm: kho tài liệu tải về, phân quyền truy cập theo nhóm người dùng
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/05-quan-ly-noi-dung-tai-lieu-san-pham/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-tai-lieu-san-pham.md
- **Thực thể/CRUD**: CmsDocument — thêm, sửa, xoá, phân quyền tải
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-036 — Quản lý Gian hàng (portal/cms, Wave 3)

- **Mô tả**: Quản lý Gian hàng: khai báo gian hàng đối tác, thông tin trưng bày và trạng thái hiển thị
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/06-quan-ly-gian-hang/03-mo-ta-chuc-nang/01-quan-ly-gian-hang.md
- **Thực thể/CRUD**: CmsBooth — thêm, sửa, xoá, xuất bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-037 — Quản lý Liên hệ (portal/cms, Wave 3)

- **Mô tả**: Quản lý Liên hệ: tiếp nhận yêu cầu liên hệ từ portal, phân công phản hồi, theo dõi trạng thái
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/07-quan-ly-lien-he/03-mo-ta-chuc-nang/01-quan-ly-lien-he.md
- **Thực thể/CRUD**: ContactRequest — tiếp nhận, phân công, phản hồi
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-038 — Quản lý nội dung Hướng dẫn sử dụng (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung Hướng dẫn sử dụng: biên tập bộ hướng dẫn theo sản phẩm, phiên bản tài liệu
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/08-quan-ly-noi-dung-huong-dan-su-dung/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-huong-dan-su-dung.md
- **Thực thể/CRUD**: CmsGuide — thêm, sửa, duyệt, xuất bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-039 — Quản lý nội dung chính sách, điều khoản (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung chính sách, điều khoản: biên tập và phát hành phiên bản chính sách, lưu vết thay đổi
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/09-quan-ly-chinh-sach-dieu-khoan/03-mo-ta-chuc-nang/01-quan-ly-noi-dung-chinh-sach-dieu-khoan.md
- **Thực thể/CRUD**: CmsPolicy — thêm, sửa, phát hành phiên bản
- **Phụ thuộc**: RM-004
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-040 — Quản lý diễn đàn câu hỏi (portal/cms, Wave 3)

- **Mô tả**: Quản lý diễn đàn câu hỏi: kiểm duyệt câu hỏi người dùng đăng, trả lời, ghim và khoá chủ đề
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/10-quan-ly-dien-dan/03-mo-ta-chuc-nang/01-quan-ly-dien-dan-cau-hoi.md
- **Thực thể/CRUD**: ForumQuestion — duyệt, trả lời, ghim, khoá
- **Phụ thuộc**: RM-007
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-041 — Quản lý diễn đàn bài viết (portal/cms, Wave 3)

- **Mô tả**: Quản lý diễn đàn bài viết: kiểm duyệt bài viết, phân chuyên mục, gỡ bài vi phạm
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/10-quan-ly-dien-dan/03-mo-ta-chuc-nang/02-quan-ly-dien-dan-bai-viet.md
- **Thực thể/CRUD**: ForumPost — duyệt, sửa, gỡ, phân mục
- **Phụ thuộc**: RM-007
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-042 — Quản lý nội dung xấu độc (portal/cms, Wave 3)

- **Mô tả**: Quản lý nội dung xấu độc: bộ lọc từ khoá, hàng đợi nội dung bị báo cáo, xử lý gỡ và cảnh cáo tài khoản
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/02-quan-ly-noi-dung-portal-cms/10-quan-ly-dien-dan/03-mo-ta-chuc-nang/03-quan-ly-noi-dung-xau-doc.md
- **Thực thể/CRUD**: ContentModeration — lọc, xét duyệt, gỡ, cảnh cáo
- **Phụ thuộc**: RM-040, RM-041
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-043 — Nội dung trang portal (portal/site, Wave 3)

- **Mô tả**: Nội dung trang portal: bố cục trang chủ và các khối hiển thị lấy dữ liệu từ những màn CMS đã dựng
- **Nguồn**: docs/brd/02-nhom-chuc-nang-portal/01-giao-dien-trang-portal/01-noi-dung-trang-portal/03-mo-ta-chuc-nang/01-noi-dung-trang-portal.md
- **Thực thể/CRUD**: PortalPage — cấu hình bố cục, gán khối nội dung
- **Phụ thuộc**: RM-031, RM-033, RM-036
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-044 — Báo cáo giám sát (system/monitoring, Wave 4)

- **Mô tả**: Báo cáo giám sát hệ thống phần cứng, phần mềm và log truy cập theo kỳ
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/03-quan-tri-he-thong/03-giam-sat-he-thong-phan-cung-phan-mem-log-truy-cap/03-mo-ta-chuc-nang/02-bao-cao-giam-sat.md
- **Thực thể/CRUD**: AuditLog — tổng hợp, lọc, xuất dữ liệu
- **Phụ thuộc**: RM-030
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-045 — Báo cáo thiết bị (khdn/devices, Wave 4)

- **Mô tả**: Báo cáo thiết bị: tổng hợp tồn kho, nhập, bán, thu hồi theo chủng loại và thời gian
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/01-quan-ly-thiet-bi/03-mo-ta-chuc-nang/06-bao-cao-thiet-bi.md
- **Thực thể/CRUD**: DeviceStock — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-014
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-046 — Báo cáo lịch sử thay đổi gói dịch vụ (khdn/packages, Wave 4)

- **Mô tả**: Báo cáo lịch sử thay đổi gói dịch vụ: thống kê thay đổi nội dung và giá trị gói theo thời gian
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/02-quan-ly-goi-dich-vu/03-mo-ta-chuc-nang/02-bao-cao-lich-su-thay-doi-goi-dich-vu.md
- **Thực thể/CRUD**: ServicePackage — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-010
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-047 — Báo cáo tổng hợp khách hàng (khdn/payments, Wave 4)

- **Mô tả**: Báo cáo tổng hợp khách hàng: bức tranh chung số lượng, phân loại và trạng thái khách hàng doanh nghiệp
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/04-bao-cao-tong-hop-khach-hang.md
- **Thực thể/CRUD**: Enterprise — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-008
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-048 — Báo cáo phát triển khách hàng (khdn/payments, Wave 4)

- **Mô tả**: Báo cáo phát triển khách hàng: theo dõi tăng trưởng khách hàng mới, rời bỏ theo kỳ
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/05-bao-cao-phat-trien-khach-hang.md
- **Thực thể/CRUD**: Enterprise — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-008
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-049 — Báo cáo doanh thu sản lượng khách hàng (khdn/payments, Wave 4)

- **Mô tả**: Báo cáo doanh thu sản lượng khách hàng: doanh thu và sản lượng theo từng khách hàng, từng kỳ
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/06-bao-cao-doanh-thu-san-luong-khach-hang.md
- **Thực thể/CRUD**: PaymentTransaction — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-020
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-050 — Báo cáo phân bổ doanh thu khách hàng theo gói (khdn/payments, Wave 4)

- **Mô tả**: Báo cáo phân bổ doanh thu khách hàng theo gói: cơ cấu doanh thu chia theo gói dịch vụ
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/03-quan-ly-thanh-toan-phuc-vu-khach-hang-cua-mbf-bao-gom-kh-doa/03-mo-ta-chuc-nang/07-bao-cao-phan-bo-doanh-thu-khach-hang-theo-goi.md
- **Thực thể/CRUD**: PaymentTransaction — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-020
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-051 — Báo cáo tổng quan khiếu nại và xử lí khiếu nại khách hàng (khdn/complaints, Wave 4)

- **Mô tả**: Báo cáo tổng quan khiếu nại và xử lí khiếu nại khách hàng theo kỳ
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/03-bao-cao-tong-quan-khieu-nai-va-xu-li-khieu-nai-khach-hang.md
- **Thực thể/CRUD**: Complaint — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-025
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-052 — Báo cáo lịch sử khiếu nại và xử lí khiếu nại khách hàng (khdn/complaints, Wave 4)

- **Mô tả**: Báo cáo lịch sử khiếu nại và xử lí khiếu nại khách hàng theo từng hồ sơ
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/04-quan-ly-khieu-nai/03-mo-ta-chuc-nang/04-bao-cao-lich-su-khieu-nai-va-xu-li-khieu-nai-khach-hang.md
- **Thực thể/CRUD**: Complaint — tra cứu lịch sử, xuất dữ liệu
- **Phụ thuộc**: RM-025
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-053 — Báo cáo chương trình khuyến mãi (khdn/promotions, Wave 4)

- **Mô tả**: Báo cáo chương trình khuyến mãi: hiệu quả áp dụng, số lượt và giá trị ưu đãi theo chương trình
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/05-chuong-trinh-khuyen-mai/03-mo-ta-chuc-nang/02-bao-cao-chuong-trinh-khuyen-mai.md
- **Thực thể/CRUD**: Promotion — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-027
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)

### RM-054 — Báo cáo tích điểm đổi quà (khdn/loyalty, Wave 4)

- **Mô tả**: Báo cáo tích điểm đổi quà: thống kê điểm tích luỹ, lượt đổi quà và tồn kho quà tặng
- **Nguồn**: docs/brd/01-nhom-chuc-nang-dich-vu-he-thong-nen-tang-web/04-quan-ly-dich-vu-danh-cho-khach-hang-doanh-nghiep-nha-truong/06-tich-diem-doi-qua/03-mo-ta-chuc-nang/02-bao-cao-tich-diem-doi-qua.md
- **Thực thể/CRUD**: LoyaltyPoint/Reward — tổng hợp, xuất dữ liệu
- **Phụ thuộc**: RM-028
- **Trạng thái**: chưa
- **Nợ phát sinh**:
  - (trống — mục này để specify của chức năng khác tự ghi việc dời sang item này)
