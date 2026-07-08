# Phân loại fail + fix có điểm dừng (Pha 10, agnostic)

Sau khi chạy suite (Pha 8) và trình bày kết quả (Pha 9), mọi test fail phải được phân loại **trước khi
sửa bất cứ thứ gì**. Không được sửa mù theo phản xạ ("test fail thì chắc do code sai" hoặc ngược lại)
— sai lớp phân loại dẫn tới sửa nhầm nơi (vd tự ý sửa code sản phẩm để che một product-bug thật, hoặc bỏ
qua một bug thật vì tưởng là selector giòn).

## 1. Ba lớp phân loại

### test-defect — lỗi nằm ở chính test, không phải ở app

Test tự nó sai: expected value sai, selector chọn nhầm phần tử, oracle (điều kiện assert) sai logic,
test giả định sai thứ tự/side-effect không có thật trong spec.

**Cách nhận biết:** đọc lại spec (FR/AC gốc) + đọc lại test — nếu hành vi app quan sát được **khớp với
spec** nhưng test lại assert một giá trị/điều kiện khác spec, đây là test-defect.

**Cảnh báo anti-pattern:** đừng "sửa test cho xanh" (amend-until-green) — tức sửa test để nó pass mà
không xác minh hành vi app có thực sự đúng spec hay không. Đây là cách một product-bug thật bị che giấu
vĩnh viễn (suite xanh nhưng bug vẫn còn).

**Quy tắc quyết định (bắt buộc trước khi coi là test-defect):** một fail chỉ được auto-fix như test-defect
khi **cả hai** điều kiện sau đúng:
1. Hành vi thực tế (actual) của app đã được quan sát và **chứng minh khớp** với đúng một dòng FR/AC cụ thể
   trong spec — phải trích được nguyên văn dòng đó.
2. Cái sai nằm ở kỳ vọng của test (giá trị/điều kiện/selector/thứ tự trong test không khớp dòng FR/AC đó).

Nếu hành vi thực tế của app **không khớp bất kỳ dòng FR/AC nào** trong spec → đây **không phải** test-defect,
phải phân loại lại thành **product-bug** và đi qua cổng duyệt từng bug (mục product-bug bên dưới), không
được tự sửa test để né.

**Hành động: auto-fix có bằng chứng + ghi log.** Trước khi sửa bất kỳ test nào theo nhánh test-defect,
phải:
1. **Trích nguyên văn dòng FR/AC** từ spec chứng minh hành vi actual hiện tại là đúng.
2. Sửa thẳng test cho khớp spec, chạy lại.
3. **Ghi log vào `qa-run.md`** (xem `traceability.md`): tên/id test, giá trị/assert **trước → sau** khi
   sửa, kèm dòng FR/AC trích ở bước 1 làm căn cứ. Không được sửa im lặng — mọi thay đổi assertion phải để
   lại vết kiểm chứng được.

### infra-blocker — hạ tầng/môi trường test chưa sẵn sàng, không phải app sai

Element không có selector ổn định, 401/redirect vì thiếu session hợp lệ, thiếu dữ liệu seed tiền điều
kiện, môi trường (DB/service phụ thuộc) chưa dựng/chưa đúng cấu hình.

**Cách nhận biết:** lỗi xảy ra **trước khi** kịch bản nghiệp vụ thật sự được thực thi (test chưa chạm
tới logic cần kiểm chứng) — thất bại vì thứ xung quanh test, không vì hành vi app sai.

**Hành động: auto-fix theo playbook** — xem `blocker-playbook.md` để biết đúng blocker nào dùng đúng
thuật toán nào (auth/selector/config/seed). Một số blocker trong playbook có gate riêng (vd thêm test id
lan ra nhiều file sản phẩm) — theo đúng gate của playbook đó, không tự nới điều kiện. Sau khi gỡ, chạy
lại; vẫn chưa gỡ được (thiếu credential/quyền/network) → escalate đúng theo playbook, không tự "coi như
pass".

### product-bug — app trả kết quả trái spec

Hành vi app quan sát được **mâu thuẫn với FR/AC trong spec** — không phải lỗi test, không phải lỗi hạ
tầng. Đây là bug thật của sản phẩm.

**Hành động: KHÔNG BAO GIỜ tự sửa code sản phẩm.** Trình tự bắt buộc:

1. **Chẩn đoán** — nêu rõ: FR/AC nào bị vi phạm, hành vi thực tế quan sát được là gì, hành vi đúng theo
   spec phải là gì.
2. **Đề xuất patch** — viết patch cụ thể (diff hoặc mô tả thay đổi) cho từng bug, kèm lý do tại sao patch
   này sửa đúng chỗ mà không phá hành vi khác.
3. **Cổng duyệt từng bug** — trình bày từng product-bug kèm chẩn đoán + patch đề xuất, **chờ duyệt riêng
   cho từng cái** (không gộp duyệt hàng loạt "duyệt hết luôn"). Đây là **cổng cứng** — không tự ý coi im
   lặng là đồng ý.
4. **Bug được duyệt** → áp patch, chạy lại đúng test liên quan để xác nhận đã hết fail.
5. **Bug không được duyệt / chưa phản hồi** → **log thành issue** (không sửa, không xoá test, không
   `test.skip`) — ghi rõ: FR/AC vi phạm, hành vi quan sát, patch đề xuất còn treo, trạng thái test hiện
   tại (vẫn fail).
6. Sau khi xử lý xong các bug được duyệt (bước 4) và log xong phần dư (bước 5) → **dừng pha 10** (bounded
   fix — không lặp vô hạn tìm thêm bug mới ngoài phạm vi lần chạy này). Ghi trạng thái pha vào `qa-run.md`
   trước khi dừng (xem `traceability.md`).

## 2. Bảng triage nhanh: symptom → lớp → hành động

| Symptom quan sát được | Lớp | Hành động |
|---|---|---|
| Assert sai giá trị/format nhưng app trả đúng theo spec | test-defect | Trích FR/AC chứng minh app đúng + auto-fix test + log diff vào `qa-run.md` |
| Selector không khớp DOM hiện tại (đổi cấu trúc) nhưng phần tử vẫn ở đúng chỗ, hành vi đúng | test-defect | Trích FR/AC chứng minh app đúng + auto-fix test (chọn lại selector) + log diff vào `qa-run.md` |
| Test giả định thứ tự/dữ liệu không có trong spec | test-defect | Trích FR/AC chứng minh app đúng + auto-fix test (sửa oracle) + log diff vào `qa-run.md` |
| Redirect login / 401 / 403 ngay đầu kịch bản | infra-blocker | Auto-fix theo Blocker 1 (`blocker-playbook.md`) |
| Không tìm được phần tử ổn định để định vị | infra-blocker | Auto-fix theo Blocker 2, theo đúng gate nếu lan nhiều file |
| `command not found` / thiếu config framework test | infra-blocker | Auto-fix theo Blocker 3 |
| Fail vì thiếu record/dữ liệu tiền điều kiện | infra-blocker | Auto-fix theo Blocker 4 |
| Response/UI trả sai giá trị nghiệp vụ so với FR/AC | product-bug | Chẩn đoán + đề xuất patch → chờ duyệt → fix cái duyệt + log phần dư → dừng |
| Ràng buộc nghiệp vụ (unique, quyền, tính toán) sai kết quả so với spec | product-bug | Như trên |
| Không chắc là test sai hay app sai (nghi ngờ cả hai) | — | Đọc lại spec trước, không đoán; nếu vẫn mơ hồ hoặc không trích được dòng FR/AC chứng minh app đúng, **luôn coi như product-bug** (thiên về an toàn — không tự sửa test lẫn app khi chưa chắc, không auto-fix test khi thiếu bằng chứng) |

## 3. Nguyên tắc chốt

- **Không tự sửa code sản phẩm** ngoài phạm vi product-bug đã được duyệt tường minh.
- **Không gộp fail khác lớp vào cùng một lô xử lý** — mỗi fail phải được gán đúng 1 trong 3 lớp trước khi
  quyết định hành động.
- **Bounded, không phải vòng lặp vô hạn**: pha 10 xử lý đúng tập fail của lần chạy hiện tại (từ Pha 8/9),
  fix + log xong là dừng, không tự mở rộng sang săn thêm bug mới chưa được phát hiện qua suite.
- Sau khi dừng, Pha 11 (traceability) và Pha 12 (cập nhật CLAUDE.md) mới tiếp tục — xem `traceability.md`.
