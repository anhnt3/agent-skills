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
Thư mục làm việc tạm: `.specify/tmp/brd-import/<slug-tên-docx>/` (bỏ đuôi, bỏ dấu tiếng
Việt, khoảng trắng và ký tự lạ → `-`) — **một thư mục
riêng cho mỗi tài liệu**. Dùng chung một thư mục cho hai BRD khác nhau sẽ trộn ảnh của tài
liệu trước vào tài liệu sau (pandoc không dọn `media/`). Dưới đây viết tắt là `<WORK>`.

Dùng `python3` nếu `python` không có (macOS/Linux).

### 1. Dò cấu trúc

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py probe "<đường-dẫn-docx>" \
  --work <WORK> --quiet
```

`--quiet` chỉ in tóm tắt; JSON đầy đủ luôn nằm ở `<WORK>/probe.json` — đọc file đó.

Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp lỗi cho người dùng. Không tự chữa,
không thử lệnh khác.

### 2. Bậc 1–5 mù (`needs_llm: true`) — phán đoán ranh giới

`probe.json` trả về `candidates`: danh sách đoạn ứng viên, mỗi mục có `i` (vị trí trong
mảng, 0,1,2,…), `text`, `bold`, `size`.

Nhiệm vụ của bạn: quyết **đoạn nào là tiêu đề mục, và ở cấp mấy**. Chỉ nhìn `text`,
`bold`, `size` — KHÔNG đọc thân bài, KHÔNG chép nội dung. Ghi kết quả ra
`<WORK>/outline.json` dạng `[{"i": 0, "level": 1}, …]`:

- `i` là **đúng giá trị trường `i` của ứng viên** = vị trí của nó trong mảng `candidates`.
  Không tự tính, không dùng số đoạn nào khác. Sai `i` → nâng nhầm đoạn, im lặng.
- `level` bắt đầu từ 1, tăng dần theo độ sâu; cấp phải **liên tục** (có cấp 3 thì phải có cấp 2).
- Ứng viên KHÔNG phải tiêu đề thì **bỏ khỏi danh sách**, đừng gán cấp bừa.
- Hai ứng viên trùng `text` mà gán cấp khác nhau → cấp sau đè cấp trước (Lua filter khớp
  theo text). Gặp trùng: gán cùng một cấp, hoặc bỏ cả hai và nói rõ trong báo cáo.
- Không đủ căn cứ để phân cấp (mọi ứng viên trông như nhau) → **DỪNG**, báo người dùng
  rằng tài liệu không có tín hiệu cấu trúc nào và đề nghị BA áp Heading style rồi gửi lại.

**Mỏ neo phủ (bắt buộc, chống bỏ sót đuôi tài liệu)**: đếm `N = len(candidates)` từ
`probe.json`. Phải duyệt **hết** N ứng viên; danh sách dài thì đọc theo lô 200 mục
(`i` 0–199, 200–399, …) nhưng vẫn duyệt tới lô chứa `i = N-1`. Trước khi chạy lệnh dưới,
báo ra ba thứ **kiểm được bằng mắt**:

1. Các khoảng `i` đã duyệt, liền mạch và phủ tới `N-1` (vd `0–199, 200–399, 400–537` với N=538).
2. Số đã gán cấp.
3. Phần loại **tách theo nhóm kèm lý do**, không phải một con số trần — vd
   "loại 312: 240 nhãn field trong bảng, 48 dòng ghi chú in đậm, 24 tiêu đề phụ lục".

`N` phải bằng (2) + tổng (3). Khoảng `i` hở, hoặc phần loại chỉ có một con số không có
nhóm-lý-do → chưa duyệt xong, **cấm chạy tiếp**. Roundtrip byte-for-byte KHÔNG bắt được
lỗi bỏ sót này (phần bị bỏ chỉ chảy dồn vào file trước đó), nên đây là lớp chặn duy nhất.

Rồi chạy lại:

```bash
python .specify/extensions/dft-speckit/scripts/brd_import.py probe "<đường-dẫn-docx>" \
  --work <WORK> --outline <WORK>/outline.json --quiet
```

- Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp. Riêng thông điệp
  `promote_headings: nâng được X/Y` nghĩa là vài ứng viên bạn chọn không phải đoạn văn
  độc lập (thường là ô trong bảng): thông điệp **liệt kê đích danh** các tiêu đề không
  nâng được — loại đúng chúng khỏi `outline.json` rồi chạy lại **một lần**
  (ghi rõ đã loại ứng viên nào — mỏ neo phủ ở trên phải cập nhật theo). Vẫn lệch → DỪNG
  và báo người dùng.

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
  --work <WORK> --depth <cấp-đã-chọn> --dest docs/brd
```

- Mã thoát khác 0 → **DỪNG**, in nguyên thông điệp. Script đã tự bảo đảm KHÔNG ghi gì
  ra đích khi kiểm chứng thất bại — đừng cố chạy lại với cấp khác để "cho qua".
- Ngoại lệ, **đúng hai** thông điệp sau là lỗi *chọn cấp* chứ không phải lỗi kiểm chứng:
  **"Cấp cắt … không dùng được"** và **"Cấp cắt … không tồn tại. Các cấp có thật: […]"**.
  Chỉ với hai thông điệp này mới được quay lại bước 3 hỏi người dùng chọn cấp khác (với
  cái thứ hai, lấy đúng danh sách "Các cấp có thật" làm option) — vẫn phải **hỏi thật**,
  không tự chọn. Mọi thông điệp khác là chí tử: DỪNG và báo.
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
và **liệt kê đầy đủ `warnings`** (file quá lớn, ảnh mồ côi, trùng tiêu đề, lệch số node,
**heading nằm trong khối bảng**). Cảnh báo không được im lặng bỏ qua. Hai loại cần nói
rõ hệ quả: *heading trong bảng* = cấp cắt có thể cắt đôi một bảng, nên hỏi lại người dùng
có muốn chọn cấp khác không; *hàng loạt ảnh mồ côi* = `<WORK>` còn ảnh của lần import
tài liệu khác, cần dùng thư mục làm việc riêng rồi chạy lại.

Nhắc bước tiếp: đọc `docs/brd/brd.manifest.yml` để biết màn nào nằm ở file nào.

Nhắc về định dạng: markdown sinh ra ở dạng **gfm** — ảnh là thẻ `<img src="…" />`,
bảng là HTML thô hoặc bảng pipe, nên xem trước được ngay trên VSCode/GitHub.

Nhắc về VSCode: bật `"explorer.sortOrder": "mixed"` trong `.vscode/settings.json` để
Explorer xếp file và thư mục xen kẽ, đúng thứ tự tài liệu (mặc định thư mục lên trước).

Nhắc dọn dẹp: `<WORK>` giữ lại markdown trung gian (`brd.md`),
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
