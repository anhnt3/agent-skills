---
description: Bẻ một file BRD .docx lớn thành cây markdown nhỏ phản chiếu navigation pane của Word — mỗi màn hình một file, kèm manifest và kiểm chứng ghép ngược không mất một byte.
---

# Nhập BRD .docx thành cây markdown

BA giao một file BRD `.docx`. Nhiệm vụ: chuyển thành **cây markdown** dưới `docs/brd/`,
mỗi mục ở cấp đã chọn là **một file**, để `/speckit.specify` đọc trọn vẹn một màn mà
không phải đoán khoảng dòng. Toàn bộ tiếng Việt.

**Nguyên tắc lõi**: **script chép, bạn chỉ quyết ranh giới**. Bạn KHÔNG được viết lại,
tóm tắt, chuẩn hoá hay "làm đẹp" bất kỳ nội dung nào của tài liệu. Script là thứ duy nhất
ghi nội dung file markdown; việc của bạn là chạy script, đọc kết quả, hỏi người dùng
đúng chỗ cần quyết định, và báo cáo trung thực.

## User Input

`$ARGUMENTS`

Kỳ vọng: **đường dẫn tới một file `.docx`**. Trống, không tồn tại, hoặc không phải `.docx`
→ **hỏi lại**, KHÔNG tự đi tìm file trong repo.

## Quy trình (bắt buộc theo thứ tự)

Đường dẫn script: `.specify/extensions/dft-speckit/scripts/brd_import.py`.
Thư mục làm việc tạm: `.specify/tmp/brd-import/`.

### 1. Dò cấu trúc

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py probe "<đường-dẫn-docx>" \
  --work .specify/tmp/brd-import
```

Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp lỗi cho người dùng. Không tự chữa,
không thử lệnh khác.

### 2. Bậc 1–5 mù (`needs_llm: true`) — phán đoán ranh giới

`probe.json` trả về `candidates`: danh sách đoạn ứng viên, mỗi mục có `index` và `text`.

Nhiệm vụ của bạn: quyết **đoạn nào là tiêu đề mục, và ở cấp mấy**. Chỉ nhìn `text`,
`bold`, `size` — KHÔNG đọc thân bài, KHÔNG chép nội dung. Ghi kết quả ra
`.specify/tmp/brd-import/outline.json` dạng `[{"index": 0, "level": 1}, …]`:

- `level` bắt đầu từ 1, tăng dần theo độ sâu; cấp phải **liên tục** (có cấp 3 thì phải có cấp 2).
- Ứng viên KHÔNG phải tiêu đề thì **bỏ khỏi danh sách**, đừng gán cấp bừa.
- Không đủ căn cứ để phân cấp (mọi ứng viên trông như nhau) → **DỪNG**, báo người dùng
  rằng tài liệu không có tín hiệu cấu trúc nào và đề nghị BA áp Heading style rồi gửi lại.

Rồi chạy lại:

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py probe "<đường-dẫn-docx>" \
  --work .specify/tmp/brd-import --outline .specify/tmp/brd-import/outline.json
```

### 3. Chốt cấp cắt (interview)

Trình cho người dùng **bảng `levels`** từ `probe.json` — mỗi dòng: cấp, cấp Word gốc,
số mục, trung vị / nhỏ nhất / lớn nhất (ký tự). Rồi hỏi qua **AskUserQuestion**:
cắt ở cấp nào.

- Đánh `(Recommended)` cho `recommend_depth`, và **nêu thẳng con số trung vị làm căn cứ**
  ngay trong option (vd "cấp 5 — 54 mục, trung vị 23.808 ký tự, mọi mục 4k–76k").
- Đưa thêm 1–2 cấp lân cận làm option, kèm lý do vì sao kém hơn (vd "cấp 3 — 35 mục nhưng
  có mục 275k ký tự, lệch nhau quá xa").
- **Chờ phản hồi thật của người dùng.** Cấm tự tuyên bố người dùng đã đồng ý.
  Chưa có phản hồi → DỪNG, không chạy bước 4.

### 4. Cắt và kiểm chứng

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py split \
  --work .specify/tmp/brd-import --depth <cấp-đã-chọn> --dest docs/brd
```

- Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp. Script đã tự bảo đảm KHÔNG ghi gì
  ra đích khi kiểm chứng thất bại — đừng cố chạy lại với cấp khác để "cho qua".
- Ngoại lệ duy nhất: thông điệp bắt đầu bằng **"Cấp cắt … không dùng được"** là lỗi
  *chọn cấp*, không phải lỗi kiểm chứng. Lúc đó được phép quay lại bước 3 hỏi người dùng
  chọn cấp khác — nhưng vẫn phải **hỏi thật**, không tự chọn.
- `docs/brd/` đã tồn tại và **không rỗng** (dù có manifest hay không) → script tự đổi
  đích sang `docs/brd.new/` và trả thêm khoá `diff`. Đây là **cố ý**: markdown là nguồn
  sự thật, BA có thể đã sửa tay.
  Trình bảng `diff` (thêm / mất / đổi) cho người dùng tự quyết cách hợp nhất.
  **KHÔNG tự merge, KHÔNG tự xoá `docs/brd/`.**
- Báo cáo có khoá `replaced_previous_new` → một thư mục `docs/brd.new/` của lần chạy
  trước đã bị thay thế. **Nói thẳng điều này cho người dùng**, vì lần hợp nhất trước
  có thể chưa làm.

### 5. Báo cáo

Lệnh `split` **in báo cáo JSON ra stdout** (không ghi ra file `report.json` nào cả) —
đọc trực tiếp stdout của lệnh ở bước 4.

Từ báo cáo đó, báo: đường dẫn đích (`dest`), số file (`files`), số thư mục (`folders`),
cấp đã cắt (`cut_depth`), bậc dò đã dùng (`tier`), số ảnh (`media`), `roundtrip: OK`,
và **liệt kê đầy đủ `warnings`** (file quá lớn, ảnh mồ côi, trùng tiêu đề, lệch số node).
Cảnh báo không được im lặng bỏ qua.

Nhắc bước tiếp: đọc `docs/brd/brd.manifest.yml` để biết màn nào nằm ở file nào.

Nhắc dọn dẹp: `.specify/tmp/brd-import/` giữ lại markdown trung gian (`brd.md`),
`probe.json` và **toàn bộ ảnh tách ra từ docx** — có thể vài chục MB sau mỗi lần chạy.
Nói cho người dùng biết thư mục này còn đó và có thể xoá khi đã hài lòng với `docs/brd/`.
**Đừng tự xoá** khi chưa hỏi: nếu còn `docs/brd.new/` chưa hợp nhất thì vẫn cần chạy lại.

## Sai lầm thường gặp

- **Tự viết lại / tóm tắt nội dung docx** → phá hợp đồng lõi. Script chép, bạn không chép.
- **Tự chọn cấp cắt rồi chạy luôn** → cấp cắt là quyết định của người dùng, phải hỏi thật.
- **Kiểm chứng fail rồi thử cấp khác cho qua** → che lỗi. Fail nghĩa là có bug, phải báo.
- **Tự merge `docs/brd.new/` vào `docs/brd/`** → xoá công BA đã sửa tay. Chỉ trình diff.
- **Bỏ qua `warnings` cho gọn báo cáo** → người dùng mất thông tin cần để quyết.
- **Gán cấp bừa cho ứng viên ở bước 2 để chạy tiếp** → cây sai, cắt sai. Không chắc thì DỪNG.
