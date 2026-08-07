# dft-speckit extension — command `brd-import`: bẻ BRD .docx thành cây markdown

Ngày: 2026-08-07

## Mục tiêu

BA giao một file BRD `.docx` rất lớn. Dev cần biến nó thành một **cây markdown nhỏ**
phản chiếu navigation pane của Word, để:

- mỗi màn hình / chức năng là **một file** — `/speckit.specify` đọc trọn vẹn một file,
  không phải đoán khoảng dòng trong một file 1MB;
- **markdown trở thành nguồn sự thật**: từ đây BA sửa file `.md`, không sửa `.docx` nữa;
- sau này ghép ngược ra `.docx` được (command `brd-export`, **ngoài phạm vi lần này**,
  nhưng manifest và phép kiểm ở đây phải đủ để làm mà không import lại).

Phạm vi lần này: **chỉ** command `brd-import`. Không làm `brd-export`,
không làm `road-map-from-brd`, không sửa `/speckit.specify` của preset.

## Bối cảnh đo được (BRD Mobifone, `refs/5. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Mobifone.docx`)

- 72MB, 407 file trong gói; `word/document.xml` 8.6MB; 10.592 đoạn; **298 bảng**; **387 lượt nhúng ảnh**
  ứng với **386 file ảnh** sau khi pandoc gộp trùng (hai lượt nhúng dùng chung một ảnh), ~71MB.
- Cây heading dùng Word style **Heading 1, 3, 4, 5, 6, 8** (nhảy cóc, không liên tục):
  H1 nhóm chức năng (2) → H3 phân hệ (6) → H4 module (35) → H5 (75) → **H6 màn hình (54)**
  → H8 mục con cố định (432 = 54×8).
- `pandoc 3.9.0.2` có sẵn, `+lua`.

Kích thước nếu cắt ở từng cấp (ký tự, bản `-t markdown`):

| Cấp nav | Là gì | Số file | Trung vị | Nhỏ nhất | Lớn nhất |
|---|---|---|---|---|---|
| 1 (H1) | Nhóm chức năng | 2 | 752.651 | 435.555 | 1.069.748 |
| 2 (H3) | Phân hệ | 6 | 217.765 | 1.863 | 679.614 |
| 3 (H4) | Module | 35 | 30.035 | 97 | 274.958 |
| 4 (H5) | Sơ đồ/Mục đích/Mô tả chức năng | 75 | 305 | 100 | 274.017 |
| **5 (H6)** | **Màn hình / chức năng** | **54** | **23.808** | **4.187** | **76.315** |
| 6 (H8) | Đối tượng tham gia, Kịch bản… | 432 | 174 | 38 | 64.659 |

## Bằng chứng khả thi (đã chạy thật, không suy đoán)

1. **`-t gfm` không dùng được**: sinh **270 bảng HTML thô**; pandoc chuyển md→docx sẽ vứt
   khối HTML thô ⇒ mất 270/298 bảng khi ghép ngược.
2. **`-t markdown` (flavor riêng của pandoc) dùng được**: sinh **grid table**,
   **0 bảng HTML thô**.
3. **Vòng ngược đã đo**: `docx → md → docx → md`

   | Phép đo | BRD gốc | Sau vòng ngược |
   |---|---|---|
   | Số bảng | 298 | **298** |
   | Số ảnh nhúng | 387 | **387** |
   | Từ trong thân tài liệu (đếm theo bội) | 122.526 | **122.526** — thiếu 0, thừa 0 |

   Đi 12 giây, về 5 giây. Chỉ **mục lục** thoái hoá (Word tự sinh lại được) và
   **style trình bày** mất (chữa bằng `--reference-doc`).
4. **Cấp heading là vấn đề thật**: pandoc viết heading cấp 8 thành `########` — 8 dấu thăng,
   **không phải markdown hợp lệ**; GitHub và VS Code render thành chữ thường. Phải chuẩn hoá.

## Quyết định thiết kế

| # | Quyết định | Lý do |
|---|---|---|
| D1 | **LLM chỉ quyết ranh giới, script chép nguyên văn** | Nội dung script cắt thì kiểm chứng được bằng ghép ngược; nội dung LLM viết lại thì muốn biết có sót/bịa phải đọc lại toàn bộ bằng model khác — đắt hơn cả việc sinh ra nó, mà vẫn không chắc |
| D2 | Bẻ nhỏ theo **cây navigation pane**, không giữ file lớn | File lớn buộc agent grep + đoán `limit`; đoán thiếu là cắt giữa bảng "Mô tả điều khiển" mà **không ai biết**. File trung gian dựng lại từ docx mất 12s nên không cần lưu |
| D3 | Cấp cắt do **luật đề xuất + người duyệt** | Luật: *cấp sâu nhất còn có trung vị ≥ 3.000 ký tự*. Với BRD này ra đúng cấp 5. Không hardcode "cấp 5" vì BRD sau của BA sẽ đánh heading khác. **Bẫy cài đặt: luật này không đơn điệu** — ở BRD này cấp 4 có trung vị 305 (trượt) nhưng cấp 5 có 23.808 (đạt). Phải duyệt **hết** mọi cấp rồi lấy cấp sâu nhất đạt; vòng lặp dừng sớm ở cấp trượt đầu tiên sẽ chọn nhầm cấp 3 |
| D4 | Thang dò cấu trúc **6 bậc**, mù cả 6 thì dừng | BA có thể gửi docx dùng style tự chế, gõ số tay, hoặc chỉ in đậm |
| D5 | Chạy lại khi đã có `docs/brd/` → ghi ra `docs/brd.new/` + báo khác biệt | md là nguồn sự thật; đè = xoá công BA |
| D6 | Manifest là **nhà duy nhất** của cấu trúc | Tên file không đủ: riêng "Sơ đồ các giao thức kết nối giữa các khối" xuất hiện **5 lần** |
| D7 | Không dùng subagent / không chọn model | Việc phán đoán chỉ tốn vài nghìn token (chỉ text tiêu đề ứng viên), không đáng dựng cơ chế agent |
| D8 | Ảnh giữ nguyên, **không nén** | Nén ảnh là sửa nội dung tài liệu gốc |

## Kiến trúc

Command **mỏng**, script **dày**. Việc chép nằm trong code kiểm chứng được, không nằm trong prompt.

```
speckit-extension/
├── extension.yml                       # + speckit.dft-speckit.brd-import, version 0.1.0
├── commands/brd-import.md              # quy trình (tiếng Việt), gọi script, chủ trì lượt hỏi
└── scripts/
    ├── brd_import.py                   # stdlib thuần: zipfile, re, json, subprocess. KHÔNG cần venv
    └── promote_headings.lua            # Lua filter cho bậc 2 (style tự chế → Header)
```

Phụ thuộc ngoài duy nhất: `pandoc` (đã kiểm 3.9.0.2).

### Ba lệnh con của script

```
1. probe <docx> --work <tmp>
     pandoc -f docx+styles -t markdown --extract-media  (1 lần, ~12s)
     chạy thang dò cấu trúc → probe.json:
       { levels: [{depth, word_style, count, median, min, max}],
         recommend_depth, detection_tier, warnings, needs_llm, candidates? }

2. probe --work <tmp> --outline outline.json      (chỉ khi needs_llm)
     dùng lại md đã convert, KHÔNG convert lại

3. split --work <tmp> --depth N --dest docs/brd
     cắt → cây + brd.manifest.yml + media/ + reference.docx
     chạy toàn bộ kiểm chứng → chỉ rename vào đích khi MỌI phép kiểm ĐẠT
```

Tách `probe`/`split` vì lượt hỏi "cắt ở cấp nào" nằm giữa hai bước, và đổi ý cấp cắt
thì chạy lại `split` mất ~1 giây thay vì convert lại 12 giây.

### Luồng của command

1. Kiểm `pandoc` — thiếu → **dừng**, in cách cài.
   Kiểm `docs/brd/brd.manifest.yml` đã có → đổi đích sang `docs/brd.new/`, báo trước khi chạy.
2. Chạy `probe`, đọc `probe.json`.
3. `needs_llm = true` → nạp `candidates[]` (chỉ text tiêu đề ứng viên, ≤200 ký tự/mục),
   phân loại thành `{index, level}[]`, ghi `outline.json`, chạy lại `probe`.
   Vẫn mù → **dừng**, liệt kê đã thử bậc nào và thấy gì. Cấm đoán bừa.
4. In bảng thống kê mọi cấp. Hỏi cấp cắt qua **AskUserQuestion**; `(Recommended)` là cấp
   luật D3 chọn, **nêu thẳng con số trung vị làm căn cứ** trong option.
   Chờ **phản hồi thật** của người dùng — chưa có thì không ghi gì.
5. Chạy `split`. Kiểm chứng fail → không ghi ra đích, in rõ phép kiểm nào lệch và lệch ở đâu.
6. Báo cáo: số file, số thư mục, cấp đã cắt, bậc dò đã dùng, kết quả từng phép kiểm,
   danh sách cảnh báo.

## Thang dò cấu trúc (6 bậc)

Chạy lần lượt, **dừng ở bậc đầu tiên cho ra cây dùng được** — tiêu chí dùng được:
≥ 2 cấp **và** ≥ 5 node ở cấp sâu nhất.

| Bậc | Tín hiệu | Cài đặt |
|---|---|---|
| 1 | `w:pStyle` = `Heading1..9` | pandoc nhận sẵn |
| 2 | Style tự chế có `w:outlineLvl` | đọc `word/styles.xml` dựng bảng style→cấp; `pandoc -f docx+styles` giữ `custom-style`; Lua filter nâng `Div[custom-style]` thành `Header` rồi **gỡ Div** để markdown sạch |
| 3 | Mục lục có sẵn trong docx (`TOC1..9`) | text mục lục khớp đoạn nào ⇒ đoạn đó là tiêu đề, cấp = cấp TOC |
| 4 | Mẫu đánh số trong text: `1.`, `1.2`, `1.2.3`, `I.`, `a)` | cấp = số dấu chấm; chỉ nhận khi **liên tục** (`1.2` phải có `1.` đứng trước) |
| 5 | Heuristic định dạng: đoạn < 120 ký tự, in đậm hoặc cỡ chữ > body, không kết thúc bằng `.` | đọc `rPr`; cấp suy từ cỡ chữ giảm dần |
| 6 | **LLM phán đoán** | script trả `candidates[]` (text ứng viên từ bậc 5, **không kèm thân bài**); LLM trả `{index, level}[]`; **script vẫn là thứ đi cắt** |

Không có bậc 7 "cắt theo kích thước": cắt giữa câu ra file vô nghĩa còn tệ hơn báo lỗi.
`detection.tier` ghi vào manifest để sau này biết cây này tin được đến đâu.

## Hợp đồng dữ liệu

### Bố cục

```
docs/brd/
  brd.manifest.yml
  reference.docx                      # style moi từ docx gốc, dành cho brd-export sau này
  media/image21.png                   # 386 file, ~71MB, nguyên bản
  01-nhom-chuc-nang-dich-vu-he-thong/
    _index.md
    02-quan-tri-he-thong/
      _index.md
      01-quan-ly-nguoi-quan-tri/
        _index.md                     # Sơ đồ chức năng, Mục đích chức năng
        01-quan-ly-nguoi-dung-quan-tri.md
        02-quan-ly-nhom-nguoi-dung-quan-tri.md
```

Ba quy tắc đặt tên, mỗi cái chữa một lỗi cụ thể:

- **Tiền tố số** (`01-`, `02-`) — thứ tự tài liệu nằm trong tên. Không có nó thì ghép ngược đảo mục.
- **Slug từ tiêu đề** — bỏ dấu tiếng Việt, lowercase, mọi ký tự ngoài `[a-z0-9-]` thành `-`,
  gộp `-` liền kề, cắt tối đa 60 ký tự. Trùng slug đã được tiền tố số tách ra, không cần hậu tố.
- **`_index.md`** giữ nội dung **của riêng** cấp chứa — đoạn nằm giữa tiêu đề module và
  màn đầu tiên. Đây là chỗ dễ mất nhất: cắt tuyến tính sẽ dán nó vào đuôi màn liền trước.

### Heading trong file

Chuẩn hoá **tương đối**: tiêu đề của file là `#`, con cháu là `##`, `###`… Mỗi file là
markdown hợp lệ đứng một mình. Cấp Word gốc (`Heading8`) **không** nằm trong file —
nằm ở `word_style` trong manifest.

### Frontmatter (chỉ thứ cần khi đọc lẻ một file)

```yaml
---
brd_id: BRD-0031
title: Quản lý người dùng quản trị
breadcrumb: [Nhóm chức năng dịch vụ hệ thống, Quản trị hệ thống, Quản lý Người quản trị]
---
```

`brd_id` + `title` trùng với manifest — **có chủ đích**, vì file phải tự giới thiệu được
khi agent đọc lẻ. Mọi thứ khác (`order`, `depth`, `word_style`, `chars`) **chỉ** có ở manifest,
để không có hai nguồn sự thật về cấu trúc.

### `brd.manifest.yml`

```yaml
schema_version: "1.0"
source:
  file: "5. Tài_liệu_mô_tả_giải_pháp_kỹ_thuật_phần_mềm_Mobifone.docx"
  sha256: "…"
  imported_at: "2026-08-07"
  pandoc: "3.9.0.2"
cut_depth: 5
detection: { tier: 1, note: "Heading style chuẩn, 604 heading, 6 cấp" }
nodes:
  - { id: BRD-0001, order: 1, depth: 1, word_style: Heading1, kind: folder,
      title: "Nhóm chức năng dịch vụ hệ thống (nền tảng web)",
      path: "01-nhom-chuc-nang-dich-vu-he-thong/_index.md", parent: null, chars: 1069748 }
  - { id: BRD-0031, order: 31, depth: 5, word_style: Heading6, kind: leaf,
      title: "Quản lý người dùng quản trị",
      path: "01-…/02-…/01-…/01-quan-ly-nguoi-dung-quan-tri.md", parent: BRD-0029, chars: 27583 }
```

`id` cấp **tăng dần theo thứ tự tài liệu**, ổn định trong một lần import.

## Kiểm chứng

Phép kiểm chính **không phải đếm ký tự** mà là **ghép ngược byte-for-byte**: sau khi cắt,
`split` dựng lại file markdown trung gian từ chính các mảnh vừa cắt, theo thứ tự manifest,
và đòi **giống hệt** bản trung gian.

Ghép ngược hoàn tác đúng 3 phép biến đổi đã áp khi cắt, mỗi phép **khả nghịch theo thiết kế**:

1. Gỡ frontmatter đã thêm.
2. Trả heading về cấp Word gốc (`#` → `########`) theo `word_style`.
3. Đưa đường dẫn ảnh về dạng chuẩn (`media/media/imageN.png` ↔ `../../../media/imageN.png`;
   độ sâu suy từ đường dẫn file).

Lệch dù **1 byte** → fail, **không ghi gì** ra đích. Phép kiểm này mạnh hơn đếm ký tự
(bắt được đảo thứ tự, đặt nhầm ranh giới, mất `_index.md`) và đồng thời **chứng minh
`brd-export` khả thi**.

Kiểm phụ — không chặn nhưng bắt buộc in ra:

- Mọi `![](…)` trỏ tới file có thật trong `media/`; file trong `media/` không ai tham chiếu → cảnh báo.
- Số node manifest == số heading trong md trung gian.
- File > 60.000 ký tự → cảnh báo "cân nhắc cắt sâu hơn", kèm tên file.
- Mục trùng tiêu đề (BRD này có 5 cặp) → liệt kê để BA biết mà đổi tên nếu muốn.

**Ghi ra đĩa**: cắt vào thư mục tạm, kiểm xong hết mới `rename` vào đích. Không có trạng thái nửa vời.

## Điều kiện dừng

| Tình huống | Hành vi |
|---|---|
| Không có `pandoc` | Dừng, in cách cài |
| `$ARGUMENTS` trống / file không tồn tại / không phải `.docx` | Dừng, hỏi lại đường dẫn — không tự đi tìm |
| Dò cấu trúc mù cả 6 bậc | Dừng, in đã thử bậc nào và thấy gì |
| Ghép ngược lệch | Dừng, in chỗ lệch đầu tiên (số dòng + 2 phía) |
| Người dùng chưa trả lời câu hỏi cấp cắt | Dừng, không ghi file |
| `docs/brd/brd.manifest.yml` đã có | Đổi đích sang `docs/brd.new/`, chạy tiếp, cuối cùng in bảng **thêm / mất / đổi** so bản cũ (so bằng `sha256` từng file) |

## Kiểm thử

1. **BRD thật** (`refs/5. Tài_liệu_…docx`) — bắt buộc đạt trước khi báo xong:
   54 file lá, 386 ảnh, ghép ngược khớp byte, `detection.tier == 1`, cấp đề xuất == 5.
2. **Fixture bậc 2 và bậc 4**: sinh bằng `pandoc md → docx` với `reference.docx` dùng
   style tự chế / tiêu đề gõ số tay; xác nhận thang dò rơi đúng bậc.
3. **Fixture âm**: docx không có tín hiệu nào → xác nhận dừng đúng cách, **không ghi file**.

## Đóng gói

- `extension.yml`: thêm `speckit.dft-speckit.brd-import` vào `provides.commands`;
  bump version `0.0.5` → **`0.1.0`** (thêm năng lực mới, không phá cái cũ).
- `build-zip.sh`: **không cần sửa** — `find scripts -type f` đã gói cả `brd_import.py`
  lẫn `promote_headings.lua`. Xác nhận bằng `unzip -l` chứ không tin suy luận.
- `README.md` của extension: thêm mục command mới.
- Không dùng `agents/`, không dispatch subagent.

## Ngoài phạm vi (làm sau, không phải bây giờ)

- `brd-export` (md → docx qua manifest + `reference.docx`).
- `road-map-from-brd` (cây md → `docs/roadmap.md`).
- Sửa `/speckit.specify` của `speckit-dft-preset` để đọc file BRD làm nguồn yêu cầu.

---

## Ghi chú bổ sung — 2026-08-07: ĐẢO NGƯỢC lựa chọn `-t markdown`

Kết luận "`-t markdown` dùng được, tránh `-t gfm`" ở các mục trên **đã bị đảo ngược**:
định dạng xuất chính thức nay là **`-t gfm`**.

- **Lý do**: file markdown sinh ra để **người đọc xem trước**. Grid table và
  `{width="5.0in"}` của `-t markdown` không trình xem markdown chuẩn nào dựng được.
- **Đo thật trên BRD Mobifone**: gfm cho 387/387 ảnh `<img src="./media/media/imageN.png"
  style="width:…;height:…" />`, 270 `<table>` HTML thô + 27 bảng pipe, và **604 heading**
  — y hệt bản `-t markdown`.
- **Cái giá đã biết**: `brd-export` (md → docx) **không** đi được đường
  markdown → docx bằng pandoc, vì đường đó làm **mất hẳn** các bảng HTML thô.
  Đường phải dùng là **markdown → html → docx**, đã kiểm: giữ đúng cấu trúc bảng
  và nội dung từng ô.
