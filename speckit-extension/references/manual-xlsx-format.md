# Định dạng CSV → xlsx cho testcase thủ công

Tài liệu này là hợp đồng dữ liệu cho Pha 4 (author testcase thủ công) của command `qa-spec-cycle`.
CSV bạn tạo ra PHẢI đúng 17 cột theo đúng thứ tự bên dưới — script `scripts/csv_to_xlsx.py`
validate header cứng (`EXPECTED_HEADER`) và sẽ **raise lỗi, không tự sửa**, nếu sai tên cột/thứ tự/số
lượng field trên bất kỳ dòng nào.

## Nội dung

1. [Bảng 17 cột (đúng thứ tự)](#1-bảng-17-cột-đúng-thứ-tự)
2. [Ai sở hữu cột nào](#2-ai-sở-hữu-cột-nào-và-vì-sao-tester-cần-nhìn-thấy-cả-3-nhóm)
3. [Quy tắc chất lượng nội dung](#3-quy-tắc-chất-lượng-nội-dung)
4. [Chạy script sinh xlsx](#4-chạy-script-sinh-xlsx)
5. [Output: 2 sheet](#5-output-2-sheet)
6. [Cập nhật `Kết quả tự động` (cột 12) ở Pha 8](#6-cập-nhật-kết-quả-tự-động-cột-12-ở-pha-8--không-mất-dữ-liệu-tester)

## 1. Bảng 17 cột (đúng thứ tự)

| # | Cột | Ai điền | Quy tắc |
|---|-----|---------|---------|
| 1 | `ID` | Command | `TC-<PREFIX>-001`, `TC-<PREFIX>-002`, ... — `<PREFIX>` là mã ngắn viết hoa của feature/module (vd `TC-LOGIN-001`). Không trùng, không nhảy số vô lý. |
| 2 | `Tiêu đề` | Command | Câu ngắn mô tả case, tiếng Việt, không lặp lại ID. |
| 3 | `Nhóm` | Command | Nhóm chức năng/màn hình con để lọc/sort (vd `Đăng nhập`, `Danh sách thiết bị`). |
| 4 | `Ưu tiên` | Command | Chỉ nhận `P1` \| `P2` \| `P3`. P1 = chặn release nếu fail. |
| 5 | `Loại` | Command | Chỉ nhận một trong: `Happy path`, `Negative`, `Boundary`, `Security`, `State transition`, `Edge case`. |
| 6 | `Tiền điều kiện` | Command | Trạng thái hệ thống/dữ liệu/quyền cần có trước khi chạy case. |
| 7 | `Dữ liệu test` | Command | Input cụ thể (giá trị thật, không viết "dữ liệu hợp lệ" chung chung). |
| 8 | `Các bước thực hiện` | Command | Đánh số `1.`, `2.`, `3.`... mỗi bước một hành động. Số bước phải khớp 1-1 với số dòng ở cột *Kết quả mong đợi*. |
| 9 | `Kết quả mong đợi` | Command | Đánh số khớp với *Các bước thực hiện* (bước 1 → kết quả 1, ...). Phải verifiable (xem §3). |
| 10 | `Truy vết` | Command | Danh sách mã neo, phân tách bằng `,` hoặc `;`. `SOURCE = brd` → `QT-<nn>` (quy tắc) · `TR-<nn>` (trường) · `S-<n><a>` (bước/ngoại lệ) · `SC-<nn>` · `DK-<nn>` (tiền điều kiện) · `CTRL-<nn>` (điều khiển) — `DK`/`CTRL` là id chạy định nghĩa trong `qa-run.md`, KHÔNG có trong BRD. `SOURCE = spec` → `FR-<nn>` · `SC-<nn>`. Dùng để dựng sheet "Ma trận truy vết". |
| 11 | `Test tự động` | Command | `file::tên_test` nếu case đã có test tự động phủ (vd `login.spec.ts::should reject wrong password`). Nếu case này **có chủ đích** chỉ test tay (không định viết test tự động), điền literal `manual-only` — KHÔNG được để trống. **Để trống** chỉ có nghĩa là gap ngoài ý muốn (chưa viết test tự động cho case đáng lẽ nên có), sẽ bị sheet "Ma trận truy vết" đánh dấu `GAP`. |
| 12 | `Kết quả tự động` | Command (chỉ-đọc) | `Pass` \| `Fail` \| `N/A` + commit/thời điểm chạy gần nhất (vd `Pass @ a1b2c3d, 2026-07-08`). Tô màu riêng, tester **không sửa** — đây là kết quả do command/CI cập nhật, không phải nơi tester ghi nhận thủ công. |
| 13 | `Kết quả thực tế` | **Tester** | Để trống. Tester điền khi thực thi tay. |
| 14 | `Trạng thái` | **Tester** | Để trống. Trong xlsx cột này có dropdown: `Pass`, `Fail`, `Blocked`, `N/A`, `Chưa chạy`. |
| 15 | `Bug ID` | **Tester** | Để trống. Tester điền mã bug nếu Trạng thái = Fail/Blocked. |
| 16 | `Ghi chú` | **Tester** | Để trống. Ghi chú thêm của tester. |
| 17 | `Nguồn BRD` | Command | Đúng MỘT trong **bốn** giá trị, **không để trống**: (a) `docs/brd/<đường-dẫn>.md#<anchor>` — case truy về mục **do BA viết**, đường dẫn tương đối **gốc repo**, anchor = slug của heading (chữ thường, giữ dấu tiếng Việt, khoảng trắng → `-`, bỏ ký tự không phải chữ/số — cùng luật `slugify_anchor()` của `brd_roadmap.py`); (b) `docs/brd/<đường-dẫn>.md#<anchor> (SPEC)` — case truy về mục do `/speckit.specify` **chèn thêm** (`Từ điển dữ liệu`, `Đặc tả màn hình`, `Quy ước chung áp dụng`, `Chất lượng phi chức năng`, `Tiêu chí chấp nhận`, `Giả định · Phụ thuộc · Ngoài phạm vi`, `Nhật ký cập nhật`, và các khối chèn trong mục gốc: tiền/hậu điều kiện, `### Luồng ngoại lệ`, `#### Bổ sung từ phỏng vấn`, hộp cảnh báo nhãn lệch `> ⚠️` — case truy về hộp dùng anchor mục chứa nó + hậu tố). **Mọi mục H2 vốn có của BA → KHÔNG hậu tố** — phân định theo `## Nhật ký cập nhật`: mục có tên trong danh sách `- **Mục mới chèn**` → hậu tố ` (SPEC)`, mục KHÔNG có trong danh sách = mục BA → không hậu tố; CẤM đoán theo số hiệu (khuôn BRD mỗi dự án một khác); **hậu tố ` (SPEC)` bắt buộc**, vì không có nó thì (a) và (b) cùng hình dạng và không còn phân biệt được "BA viết" với "công cụ chiếu"; (c) `QUCTHT §<n>` — case sinh từ đối chiếu quy ước chung, không truy về BRD; (d) `N/A` — feature không có BRD và case không từ QUCTHT. Nhiều mục → phân tách bằng ` · ` (CẤM `,`/`;` — tránh nhầm với cú pháp cột 10). |

<!-- Cột 17 được thêm sau cột tester (không chèn vào giữa) là CỐ Ý: cột 13-16 giữ
     nguyên vị trí nên logic merge dữ liệu tester không đổi, và file xlsx cũ 16 cột
     vẫn merge đúng. Chèn vào giữa sẽ dịch chỉ số cột thực thi = mất dữ liệu tester. -->

## 2. Ai sở hữu cột nào (và vì sao tester cần nhìn thấy cả 3 nhóm)

- **Cột 1–11 + 17 (thiết kế)** — command author toàn bộ khi viết CSV testcase. Đây là "kịch bản" cố định,
  không đổi giữa các lần chạy trừ khi spec/BRD đổi.
- **Cột 12 (auto, chỉ-đọc)** — command/CI điền, KHÔNG phải chỗ tester gõ tay. Trong xlsx cột này được tô
  màu xanh nhạt (khác màu cột thực thi) để phân biệt trực quan.
- **Cột 13–16 (thực thi)** — để trống hoàn toàn cho tester, tô màu vàng nhạt trong xlsx.

**Cột 17 `Nguồn BRD` khác cột 10 `Truy vết` thế nào**: cột 10 trỏ **yêu cầu trong spec** (FR/AC) và
được script **parse** để dựng sheet Ma trận truy vết — nên nó chỉ nhận token mã, dấu phẩy trong đó sẽ
tách thành nhiều dòng ma trận. Cột 17 trỏ **văn bản nghiệp vụ gốc** (BRD của BA), chỉ để người đọc lần
ngược về tài liệu — script KHÔNG parse nó, nên tiêu đề mục có dấu phẩy vẫn an toàn. Hai cột trả lời hai
câu khác nhau: *"case này phủ yêu cầu nào"* và *"yêu cầu này BA viết ở đâu"*.

**Vì sao tester cần thấy cả cột 11–12 chứ không chỉ cột thực thi**: mở file lên, tester phải biết ngay
*case nào đã có test tự động phủ rồi* (cột 11 là `file::tên_test`) và *test tự động đó đang pass hay
fail* (cột 12), để không mất công test tay lại cái đã có auto pass, đồng thời biết chắc case nào **bắt
buộc phải test tay** (cột 11 = literal `manual-only`). Không tách 2 nhóm này ra sheet riêng vì tester cần
nhìn theo từng dòng case, không phải tra chéo.

## 3. Quy tắc chất lượng nội dung

- **Một rule = một case.** Không gộp nhiều điều kiện/rule vào 1 case duy nhất — nếu spec có 2 rule khác
  nhau, tách thành 2 testcase riêng, mỗi case 1 ID.
- **Một assertion mỗi bước.** Mỗi bước ở *Các bước thực hiện* chỉ nên dẫn tới đúng một kết quả kiểm tra
  được ở dòng tương ứng trong *Kết quả mong đợi*. Không nhồi "làm A và B rồi kiểm tra C, D, E" vào một
  bước.
- **Kết quả mong đợi phải verifiable** — mô tả bằng trạng thái/giá trị/thông điệp cụ thể có thể đối
  chiếu true/false. **Cấm dùng các cụm mơ hồ**: "hoạt động tốt", "hoạt động ổn", "hiển thị đúng", "chờ
  một lúc". Thay vào đó viết cụ thể, vd: "Hệ thống hiển thị thông báo lỗi 'Sai tài khoản hoặc mật khẩu'
  màu đỏ dưới ô mật khẩu" thay vì "hiển thị đúng thông báo lỗi".
- **CSV multiline quoting**: nếu *Các bước thực hiện* hoặc *Kết quả mong đợi* có nhiều dòng (nhiều bước
  đánh số trong cùng 1 cell), phải bọc cell đó bằng dấu `"` và giữ ký tự xuống dòng bên trong theo đúng
  chuẩn CSV (RFC 4180) — không escape thủ công bằng `\n` dạng text, để `csv.reader` parse đúng số field
  trên mỗi dòng.

## 4. Chạy script sinh xlsx

```bash
python3 .specify/extensions/dft-speckit/scripts/csv_to_xlsx.py <input.csv-hoặc.json> <output.xlsx> --sheet "<Tên feature>"
```

- **Runtime prereq**: chỉ cần có sẵn `python3` trên máy. Lần chạy đầu tiên script tự dựng `.venv` cục bộ
  trong thư mục `scripts/` và tự `pip install openpyxl` — cần mạng ở lần chạy đầu đó; các lần sau chạy
  offline vì đã có venv.
- Script validate header phải khớp **chính xác** `EXPECTED_HEADER` (đúng 17 tên cột, đúng thứ tự, đúng
  dấu tiếng Việt) và mỗi dòng dữ liệu phải có đủ 17 field — sai sẽ raise lỗi và dừng, không sinh file lỗi.
- `--sheet` đặt tên sheet đầu tiên (mặc định `"Testcases"`). Tên sheet **không được chứa** các ký tự:
  `: \ / ? * [ ]` (giới hạn của Excel). Nếu bạn lỡ truyền tên chứa các ký tự này, script sẽ tự thay bằng
  khoảng trắng và cắt còn tối đa 31 ký tự — nhưng nên tránh, đặt tên sạch ngay từ đầu.

### JSON authoring (khuyến nghị)

Thay vì tự tay quote/escape CSV, **khuyến nghị author input dạng JSON** — một mảng object, mỗi object
đủ đúng **17 key** trùng tên với `EXPECTED_HEADER` (kể cả các cột thực thi 13–16, để giá trị `""`):

```json
[
  {
    "ID": "TC-LOGIN-001",
    "Tiêu đề": "Đăng nhập sai mật khẩu bị từ chối",
    "Nhóm": "Đăng nhập",
    "Ưu tiên": "P1",
    "Loại": "Negative",
    "Tiền điều kiện": "Tài khoản test đã tồn tại",
    "Dữ liệu test": "user: qa_test / pass: sai_password",
    "Các bước thực hiện": "1. Nhập sai mật khẩu\n2. Bấm Đăng nhập",
    "Kết quả mong đợi": "1. Không có gì xảy ra\n2. Hiển thị lỗi 'Sai tài khoản hoặc mật khẩu' màu đỏ",
    "Truy vết": "FR-01",
    "Test tự động": "login.spec.ts::should reject wrong password",
    "Kết quả tự động": "",
    "Kết quả thực tế": "",
    "Trạng thái": "",
    "Bug ID": "",
    "Ghi chú": "",
    "Nguồn BRD": "docs/brd/02-quan-ly-chung/01-dang-nhap.md#mô-tả-điều-khiển"
  }
]
```

Chạy với input `.json` (script tự nhận diện qua đuôi file):

```bash
python3 .specify/extensions/dft-speckit/scripts/csv_to_xlsx.py testcases-manual.json testcases-manual.xlsx --sheet "<Tên feature>"
```

JSON tránh được lỗi quoting/escape newline/dấu phẩy trong tiếng Việt vốn rất dễ sai khi tự tay soạn CSV
đa dòng (xem §3 "CSV multiline quoting"). **CSV vẫn được hỗ trợ đầy đủ** — nếu chọn CSV, phải tuân thủ
đúng chuẩn RFC 4180 (bọc `"` khi cell có xuống dòng/dấu phẩy) vì script validate cứng số field, không tự
sửa lỗi quoting sai.

## 5. Output: 2 sheet

**Sheet "Testcases"** (tên tùy chỉnh qua `--sheet`):
- Header tô xanh đậm chữ trắng, đóng băng dòng 1 (`freeze_panes = A2`).
- Cột 11–12 (`Test tự động`, `Kết quả tự động`) tô nền xanh nhạt = vùng máy điền, chỉ-đọc.
- Cột 13–16 (`Kết quả thực tế`, `Trạng thái`, `Bug ID`, `Ghi chú`) tô nền vàng nhạt = vùng tester điền.
- Cột 17 (`Nguồn BRD`) không tô nền = vùng thiết kế, cùng nhóm với cột 1–11 (nó nằm sau vùng vàng vì
  cột tester phải giữ nguyên vị trí 13–16, xem chú thích ở §1).
- Cột `Trạng thái` có dropdown validation với các giá trị: `Pass`, `Fail`, `Blocked`, `N/A`, `Chưa chạy`.
- Có dòng chú thích (legend) ngay dưới bảng giải thích ý nghĩa 2 màu tô.

**Sheet "Ma trận truy vết"** — script tự pivot từ cột *Truy vết* (cột 10) và *Test tự động* (cột 11)
của mọi dòng: mỗi FR/AC xuất hiện 1 dòng, gồm các cột `FR/AC`, `Manual TC` (danh sách ID case phủ),
`Test tự động` (danh sách test tự động phủ, `—` nếu không có), `Auto status` (`Pass`/`Fail`/`chưa chạy`,
tổng hợp từ tất cả case cùng FR — fail nếu có bất kỳ case nào fail, chưa chạy nếu có case nào rỗng, pass
chỉ khi toàn bộ đều pass), `Phủ` (`Có` nếu FR/AC có ít nhất một test tự động thật phủ; `MANUAL` nếu mọi
case phủ FR/AC đó đều dùng sentinel `manual-only` — có chủ đích, không phải lỗi; `GAP` nếu không có test
tự động thật **và** không có sentinel `manual-only` nào — đây là thiếu sót ngoài ý muốn cần bổ sung). Đây
là chỗ nhìn nhanh requirement nào còn thiếu test tự động thật sự (`GAP`), phân biệt với chỗ đã chủ đích
để tay (`MANUAL`), không cần lật từng dòng ở sheet Testcases.

## 6. Cập nhật `Kết quả tự động` (cột 12) ở Pha 8 — không mất dữ liệu tester

Cột 12 do command/CI điền sau khi chạy suite thật (Pha 8), không phải tay tester gõ. Cách cập nhật: command
**regenerate lại CSV/JSON gốc** (cùng input đã dùng để sinh xlsx lần đầu) với cột 12 điền kết quả mới
(`Pass`/`Fail`/`N/A` + commit/thời điểm), rồi **chạy lại đúng lệnh** `csv_to_xlsx.py` trỏ vào cùng file
xlsx output — đường dẫn chuẩn là `<thư mục spec>/testcases-manual.xlsx`.

Script **merge, không ghi đè**: khi output xlsx đã tồn tại, script đọc lại cột 13–16 (thực thi của
tester, khớp theo `ID` ở cột 1) từ file cũ và giữ nguyên các ô đó nếu input mới để trống — nghĩa là
chạy lại script để cập nhật cột 12 **không xóa mất** `Kết quả thực tế`/`Trạng thái`/`Bug ID`/`Ghi chú`
mà tester đã điền tay trước đó. Chỉ ghi đè cột 13–16 nếu input mới có giá trị khác trống ở cột đó.

**Hai cổng bảo vệ dữ liệu tester** — vi phạm → script **KHÔNG ghi file** (xlsx cũ nguyên vẹn), thoát ≠ 0:

| Mã thoát | Ca | Cờ mở (CHỈ người dùng bật) | Cách sửa |
|---|---|---|---|
| `0` | ghi thành công | — | — |
| `2` | ID có dữ liệu tester **biến mất** khỏi input (`IdLossError`) | `--allow-id-loss` — chỉ khi CHỦ ĐÍCH bỏ hẳn case | đọc lại ID từ chính xlsx, tái dùng nguyên văn, chạy lại |
| `3` | ID giữ nguyên nhưng **Tiêu đề đổi** trong khi đã có dữ liệu tester (`ContentShiftError`) | `--allow-content-shift` — chỉ khi CHỦ ĐÍCH đổi nội dung mà giữ kết quả cũ | gắn lại ID với ĐÚNG case cũ theo thứ tự trong xlsx, chạy lại |

Luật đi kèm:

- `ID` là khóa merge: tái dùng NGUYÊN VĂN; CẤM renumber, CẤM đổi PREFIX.
- Case mới → cấp số tiếp theo **ở cuối**; bỏ case → **để trống số đó**, không dồn số. Theo luật này thì không bao giờ chạm cổng nào.
- Agent CẤM tự thêm 2 cờ trên để né lỗi.
- Cổng `3` bỏ qua khác biệt khoảng trắng thừa, và KHÔNG chặn khi tester chưa chấm gì (sửa case theo spec mới là bình thường).
- Khi cả hai điều kiện cùng dính: cổng `2` kiểm trước → exit 2; sửa xong chạy lại có thể gặp tiếp exit 3 — không phải cờ "không ăn".
- Cần đổi ID thật (vd đổi PREFIX toàn bộ): sửa cột `ID` **trong chính file xlsx** trước (dữ liệu tester đi theo ID mới), rồi regenerate input — không dùng cờ.

<!-- Rationale: exit 3 tồn tại vì ca "bỏ/chèn case ở giữa rồi đánh số lại" — số ID vẫn đủ nên cổng 2 im
     lặng, nhưng TC-002 giờ là kịch bản của case 003 cũ mà vẫn mang kết quả tester chấm cho kịch bản cũ:
     không mất dữ liệu mà GẮN SANG CASE KHÁC, tệ hơn mất vì không hiện ra ở đâu. Trước đây script chỉ
     print WARNING rồi vẫn ghi đè (exit 0) — luật "gặp WARNING thì dừng" phụ thuộc agent tự giác.
     Test: scripts/tests/test_csv_to_xlsx.py -->

