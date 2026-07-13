# Phân tầng requirement để không trùng lặp — chuẩn & áp dụng vào spec-template

> Nghiên cứu ngày 2026-07-13. Trả lời: **spec-template DFT sao cho hợp chuẩn và không trùng lặp** khi nó
> trộn ba paradigm — agile (User Story + Acceptance Criteria), SRS cổ điển (Functional Requirements), và
> đặc tả màn (field validation, trạng thái, cột). Đối chiếu: ISO/IEC/IEEE 29148:2018, Wiegers & Beatty
> *Software Requirements* 3e, BABOK v3, Business Rules Manifesto (Ross), Volere. Mọi kết luận có nguồn URL.

## TL;DR

Mỗi sự thật đúng **một nhà**; chỗ khác **trỏ theo ID**, không chép. Năm tầng, thứ tự ưu tiên khi mâu thuẫn
**Data Dictionary > Functional Requirements > Đặc tả màn hình > Acceptance Criteria** (Business Rule phát
biểu như FR trong bản pragmatic). Chép lại một hằng số hay một luật ở tầng dưới = **lỗi lint**, không phải
"nhấn mạnh" (29148 *Consistent/Singular*; Manifesto 2.3 "one cohesive body of rules"; Wiegers "reference
the rules, maintained separately").

## Năm tầng & test phân biệt

| Tầng | Sở hữu | Test phân biệt | Nguồn |
|---|---|---|---|
| **Business Rule** | chính sách/ràng buộc đúng **dù không có phần mềm** (duy nhất, ngưỡng duyệt, "email nội bộ") | "nhập bằng import/API vẫn đúng?" → đúng ⇒ rule | Wiegers (rule là *nguồn* của requirement, không phải requirement); Manifesto 2.2/2.3 |
| **Data Dictionary** | thuộc tính field: kiểu, độ dài, định dạng, giá trị hợp lệ, default — **nhà duy nhất của hằng số** | là *định nghĩa dữ liệu*, không phải hành vi | Wiegers ch. data; Volere Data Dictionary; 29148 logical-data |
| **Functional Requirement** | **hành vi hệ thống** ("system shall…"), singular + verifiable, trace tới BR + đọc/ghi DD | là *behavior* | 29148 (Singular/Verifiable); BABOK solution-functional |
| **Screen/UI Spec** | **trình bày & ranh giới**: trạng thái, cột, lọc, action, layout; bảng validation **trỏ** DD/FR | về *hiển thị/biên*, không phải capability | 29148 External Interface (tách khỏi Functions) |
| **Acceptance Criteria** | ví dụ Given/When/Then **kiểm chứng**, trỏ FR/BR | *test/ví dụ*, không định nghĩa | agile practice; "AC không thay thế requirement" |

**"Email: bắt buộc, ≤255, đúng định dạng, phải là mail nội bộ"** — thực chất ba loại: `≤255/định dạng` = **Data
Dictionary**; `mail nội bộ` = **Business Rule**; `bắt buộc + báo lỗi inline` = **UI spec trỏ DD+BR**. (Wiegers)

## Tám quy tắc khử trùng (áp cho template)

- **R1** Hằng số validation → viết một lần ở **Data Dictionary**; FR/màn **trỏ tên field**, không ghi lại số.
- **R2** Business policy → một lần ở **Rule/FR**; UI & AC nói "theo FR-###", không paraphrase luật.
- **R3** Hành vi hệ thống → một lần ở **FR-###**; màn trỏ FR, chỉ thêm *control nào + trình bày*.
- **R4** "Bắt buộc/định dạng hiển thị lỗi/loại control" ở **UI spec**, trỏ DD/FR; cùng field trên hai màn trỏ **cùng** field DD — không định nghĩa lại mỗi màn.
- **R5** Cột danh sách trỏ **field DD**; không ghi lại ý nghĩa/giá trị hợp lệ ở định nghĩa cột.
- **R6** AC là **ví dụ trỏ FR/BR**; nếu một luật chỉ xuất hiện trong AC → chuyển lên FR rồi để AC trỏ.
- **R7** Mỗi FR truy vết lên một BR (hoặc "thuần UX"), xuống màn surface nó; một luật lặp verbatim ở ba màn = defect, gom về một FR + ba tham chiếu.
- **R8** Ưu tiên khi mâu thuẫn: **Rule > DD > FR > Screen > AC**; tầng dưới chép tầng trên = lint fail (Manifesto Art.4 declarative; 29148 Consistent).

## Audit spec-template (trước sửa) — 6 điểm trùng, đã vá

Gốc: mục "Đặc tả màn hình" ban đầu trộn behavior + data + rule + presentation, đè lên FR/AC/Key Entities.

| # | Trùng | Vá |
|---|---|---|
| 1 | Hằng số validation (max 255) nằm ở bảng screen | Nâng "Key Entities" → **`## Thực thể & Từ điển dữ liệu`** (nhà hằng số); screen trỏ tên field |
| 2 | Bảng "Hành động" của screen ⟷ FR | FR sở hữu hành vi; bảng Hành động có cột **"Hành vi (trỏ FR)"** |
| 3 | Business rule (duy nhất/liên trường) không có nhà rõ | Phát biểu ở **FR** (bằng lời, singular); bỏ "nhà thứ ba" |
| 4 | Acceptance Scenarios lặp luật/hằng số | Comment hướng dẫn: AC = ví dụ **trỏ FR**, không chốt số |
| 5 | "Trạng thái màn" ⟷ "Edge Cases" | Edge Cases = story-level; Trạng thái màn = trình bày; ghi chú tách vai trò |
| 6 | "Vai trò & quyền" ⟷ FR phân quyền | Luật phân quyền ở FR; màn chỉ mô tả *ẩn/khóa trên UI*, trỏ FR |

## Áp dụng (bản pragmatic single-home — không ép cú pháp ID cứng)

- **`## Thực thể & Từ điển dữ liệu`**: bảng mỗi thực thể `| Field | Kiểu | Bắt buộc | Giới hạn (min–max) | Giá trị hợp lệ/Ghi chú |`; "Giới hạn" ghi rõ toán tử (`≤ 255`, `0 ≤ x`) cho boundary test.
- **`### Functional Requirements`**: FR-### hành vi + business rule bằng lời, singular.
- **`## Đặc tả màn hình`**: chỉ trình bày; bảng *Hành động* trỏ FR, bảng *Nhập liệu*/*Cột* nhắc tên field DD, *Vai trò* trỏ FR phân quyền; comment cấm chép hằng số/luật.
- **Định tuyến phỏng vấn** (`/speckit.specify`): GĐ2 → Đặc tả màn hình; GĐ3 (nghiệp vụ nền/luật) → FR; dữ liệu/field → Từ điển dữ liệu.
- Vẫn giữ phương châm cũ: spec nêu **bằng lời**, cơ chế (thư viện, resource string, testid, kiểu cột DB) để plan/tasks; quy ước UI/UX chung toàn chương trình do **frontend agent** (`.claude/agents/engineering-frontend-developer.md`), không lặp trong spec.

Không chọn bản "full 29148/Wiegers rigor" (catalog BR-### + DD-ID + trace link chặt) vì overhead BA nặng,
không hợp spec do AI điền một lượt; pragmatic single-home đã khử đủ trùng lặp mà giữ nhẹ.

## Nguồn

ISO/IEC/IEEE 29148:2018 (iso.org/standard/72089; reqview.com/doc/iso-iec-ieee-29148-templates) ·
Wiegers & Beatty *Software Requirements* 3e (oreilly; craigtp/BookDigests; medium.com/analysts-corner
"identifying-and-documenting-business-rules") · BABOK v3 §2.3 (iiba.org) · Business Rules Manifesto
(businessrulesgroup.org/brmanifesto.htm) · Volere Atomic Requirements + Data Dictionary (volere.org) ·
AC vs requirement (techtarget searchsoftwarequality; altexsoft acceptance-criteria).
