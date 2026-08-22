# Quality gate — chặn fake-green (Pha 6)

Cổng cơ học, chạy **sau khi sinh test tự động** (Pha 5) và **trước khi chạy suite thật + present**
(Pha 8/9). Mục tiêu: AI hay sinh test "xanh giả" — assert rỗng/tầm thường, hoặc gọi selector/endpoint
không tồn tại trong source (ảo giác). Cổng này bắt các trường hợp đó bằng kiểm tra máy móc, không suy
diễn.

> *Nếu có Task/Agent tool: chạy pha này trong subagent con, chỉ nhận summary + artifact (xem "Ủy thác
> cho subagent" trong command `qa-spec-cycle.md`). Không có tool → làm inline.*

## Nội dung

1. [Bước 1 — Compile / type-check](#bước-1--compile--type-check)
2. [Bước 2 — Grep selector/endpoint tồn tại trong source](#bước-2--grep-selectorendpoint-tồn-tại-trong-source)
3. [Bước 2b — Quét locator cấm trong test E2E (chiều nghịch)](#bước-2b--quét-locator-cấm-trong-test-e2e-chiều-nghịch)
4. [Bước 3 — Chặn assertion tầm thường (trivial)](#bước-3--chặn-assertion-tầm-thường-trivial)
5. [Kết quả gate](#kết-quả-gate)

**Nguyên tắc:** bất kỳ selector/endpoint MISSING nào, **bất kỳ locator giòn nào không giải trình được**
(Bước 2b), hoặc lỗi compile/type-check, đều coi là ảo giác (hallucination) → phải sửa trước khi chạy suite hoặc trình bày kết quả. Không được present kết quả khi
gate chưa xanh.

## Bước 1 — Compile / type-check

Chạy lệnh compile/type-check của project (tra ở mục *Đủ-để-chạy*/*Môi trường & lệnh dựng* trong
`.agents/qa-context.md`, khối "Compile-check"). Đây là kiểm tra rẻ nhất, chạy trước tiên: nếu code test
mới sinh không compile được, dừng ngay — không cần chạy các bước sau.

- Có nhiều tầng (vd FE + BE) → chạy compile-check cho **từng tầng có test mới**.
- Lỗi compile/type-check ở bất kỳ tầng nào → gate **fail ngay**, liệt kê lỗi, quay lại Pha 5 sửa test.

**Ví dụ (một repo ABP + Angular):** `tsc --noEmit` cho `angular/` (nếu có test FE mới); `dotnet build admin_mbf.slnx`
cho `aspnet-core/` (nếu có test BE mới).

## Bước 2 — Grep selector/endpoint tồn tại trong source

Test tự động chỉ được coi là hợp lệ nếu mọi selector/test-id và mọi endpoint/route nó tham chiếu **thật
sự tồn tại trong source code**, không phải suy đoán từ tên biến hợp lý.

**Thuật toán (agnostic):**
1. Trích danh sách selector/test-id và endpoint/route được tham chiếu trong các file test vừa sinh (regex
   theo pattern selector của project, tra ở qa-context — **mặc định `data-testid="..."` / `getByTestId(...)`**, path
   string dạng `/api/...`).
2. Với mỗi giá trị trích được, grep trong thư mục source (không phải thư mục test) xem có định nghĩa
   khớp không.
3. Giá trị nào **không tìm thấy** → in dòng `MISSING: <giá trị> (referenced in <file test>)`.
4. Còn dòng `MISSING` nào → gate fail; đây là dấu hiệu test tham chiếu UI/API không có thật (ảo giác)
   hoặc selector đã đổi tên — sửa test hoặc xác nhận lại spec trước khi tiếp tục.

**Caveat — dynamic/templated selector hoặc route**: một dòng `MISSING` không tự động là ảo giác. Grep
literal-match có thể không tìm thấy selector/endpoint được **dựng động lúc runtime** (vd
`` `item-${id}` ``, `getByTestId(\`row-${index}\`)`, route dạng `/api/devices/{id}/history` build từ
biến, hoặc test-id sinh ra từ vòng lặp/template trong component). Trước khi coi một `MISSING` là
hallucination và fail gate: đọc lại source ở đúng vị trí liên quan để xác nhận có logic dựng động khớp
với giá trị đó không (cùng prefix/pattern). Nếu đúng là dựng động hợp lệ trong source → không fail gate
vì dòng đó, ghi chú rõ là "dynamic, đã xác nhận trong source" thay vì lặp lại việc sửa test/đổi
regex/loop lại bước 2 vô ích. Chỉ fail gate khi xác nhận **không có** logic dựng động nào trong source
khớp với giá trị bị flag.

**Template grep loop (agnostic — thay `<selector-pattern>` và `<src-dir>` theo qa-context):**

```bash
# Trích các selector/test-id được test tham chiếu (điều chỉnh regex theo pattern thật của test file)
grep -rhoE '<selector-pattern>' <test-dir> | sort -u | while read -r sel; do
  if ! grep -rq -- "$sel" <src-dir>; then
    echo "MISSING: $sel"
  fi
done
```

Áp dụng lặp lại thuật toán này 2 lần trong cùng pha: một lần cho **selector UI** (test-dir = thư mục
E2E/component test, src-dir = thư mục component/template FE), một lần cho **endpoint/route** (test-dir =
thư mục integration/API/E2E test, src-dir = thư mục controller/route/appservice BE). qa-context cung cấp
`<selector-pattern>` (chiến lược selector, vd `data-testid` kebab-case) và các `<src-dir>`/`<test-dir>`
tương ứng cho từng tầng.

**Ví dụ (một repo ABP + Angular — selector FE):**

```bash
#!/usr/bin/env bash
# `grep -E` KHÔNG có backreference \1 — đừng viết getByTestId\((["'])…\1\)
E=angular/e2e; S=angular/src
# 1. Trích cả hai cách test tham chiếu testid: thuộc tính thô và API getByTestId
#    ([^)a-zA-Z] nhận MỌI loại quote kể cả backtick `` `row-${id}` ``; đồng thời loại getByTestId(bienTran)).
{ grep -rhoE 'data-testid="[a-z0-9-]+"' "$E" | sed -E 's/.*"([a-z0-9-]+)"/\1/'
  grep -rhoE 'getByTestId\([^)a-zA-Z][a-z0-9-]+' "$E" | sed -E 's/^getByTestId\(.//' ; } | sort -u | while read -r sel; do
  grep -rqE "data-testid=\"$sel\"" "$S" && continue          # khớp tĩnh trong source -> hợp lệ
  hit=""; pre="$sel"                                          # không khớp tĩnh -> dò prefix testid ghép động
  while [ "$(echo "$pre" | tr -cd - | wc -c)" -ge 2 ]; do      # chỉ nhận prefix >= 2 đoạn, tránh khớp bừa
    pre="${pre%-*}"
    # Prefix phải đứng NGAY TRƯỚC quote hoặc ${ — tức đúng là literal của chuỗi ghép động.
    grep -rqE -- "$pre-(['\"\`]|\\\$\{)" "$S" && { hit="$pre-"; break; }
  done
  if [ -n "$hit" ]; then echo "DYNAMIC?: $sel (prefix $hit — mở source xác nhận theo Caveat trên)"
  else echo "MISSING: $sel"; fi
done
```

Bốn cái bẫy lệnh này tránh, tất cả đều đã kiểm bằng **chạy thật** (bịa `course-list-delete-all` → `MISSING`;
`` `course-list-row-${id}-edit` `` → `DYNAMIC?`; testid tĩnh có thật → im lặng):

- Chỉ trích `data-testid="…"` mà bỏ `getByTestId(…)` là Bước 2 **rỗng** với stack mặc định (test Playwright
  viết `getByTestId`) — testid **bịa** sẽ không bị bắt, mà Bước 2b chỉ bắt *né* testid chứ không bắt *bịa*.
- Chỉ nhận quote `'`/`"` mà bỏ **backtick**: testid hàng động — đúng pattern lệnh này khuyến nghị —
  viết là `` getByTestId(`course-list-row-${id}`) ``, thoát cả Bước 2 lẫn Bước 2b nếu regex bỏ backtick.
- Cho `attr.data-testid` (có mặt ở bất kỳ đâu trong source) làm điều kiện khớp thì **mọi** testid bịa đều
  pass — phải dò đúng **prefix** của chuỗi ghép động, và ra `DYNAMIC?` để xác nhận, không im lặng cho qua.
- Dò prefix bằng match trần (`grep -q "$pre-"`) thì prefix nằm trong một testid **tĩnh** khác cũng khớp:
  mọi testid bịa cùng màn (`course-list-…`) đều tụt xuống `DYNAMIC?` thay vì `MISSING` — tức cổng máy tự
  hạ về tự giác đúng ở ca hallucination phổ biến nhất. Vì thế mới có nhánh ``(['"`]|${)``.

**Ví dụ (một repo ABP + Angular — endpoint BE, ABP auto-route theo AppService method):**

```bash
grep -rhoE "'/api/[a-zA-Z0-9/{}-]+'" angular/e2e aspnet-core/test | sort -u | while read -r ep; do
  if ! grep -rq "$(basename "$ep")" aspnet-core/src/*/*/Contracts 2>/dev/null \
     && ! grep -rq "$(basename "$ep")" aspnet-core/src/*.Application*; then
    echo "MISSING: $ep"
  fi
done
```

(Điều chỉnh regex/thư mục cụ thể theo cấu trúc thật của project — mẫu trên minh hoạ ý tưởng, không phải
lệnh cố định.)

## Bước 2b — Quét locator cấm trong test E2E (chiều nghịch)

Bước 2 chỉ kiểm **chiều thuận**: testid mà test *có* tham chiếu thì phải tồn tại trong source. Test viết
bằng CSS class / xpath / text **không tham chiếu testid nào** → không sinh dòng `MISSING` nào → gate xanh
rỗng, đúng kiểu cổng mù. Bước này quét chiều nghịch: test có đang **né** testid không.

```bash
# Điều chỉnh regex theo API của framework E2E khai trong qa-context.
grep -rnE "\.nth\(|\.first\(|\.last\(|hasText|xpath=|text=|locator\(['\"\`][^[]|getByRole\(|getByText\(|getByLabel\(|getByPlaceholder\(|:has-text\(|By\.css\(|By\.xpath\(" <e2e-dir>
```

Regex bắt theo chuỗi nên **có nhiễu** (comment, API trùng tên) — phân loại từng dòng khớp vào đúng một
trong bốn nhóm, **ghi rõ nhóm nào** trong artifact của pha. Cấm bỏ qua im lặng, cũng cấm fail máy móc:

0. **Không phải locator**: dòng khớp nằm trong comment / chuỗi văn bản, hoặc là API trùng tên ngoài
   framework E2E (vd `_.nth(rows, 1)` của lodash trên mảng JS thường) → hợp lệ, ghi chú `non-locator`.
1. **Khớp text bên trong `expect(...)`**: `getByText` / `:has-text` / `text=` dùng để **đọc và so** với
   chuỗi nguyên văn QUCTHT → hợp lệ. **CSS class / xpath / `#id` nằm trong `expect(...)` KHÔNG thuộc
   nhóm này** — định vị giòn để assert thì vẫn là định vị giòn, vẫn vỡ khi đổi style → xếp nhóm 3.
2. Phần tử **ngoài source project**: DOM nội bộ của component thư viện bên thứ ba, dialog native của
   trình duyệt → hợp lệ, phải ghi **tên thư viện/thành phần** kèm dòng đó. Trừ ngoại lệ cấu hình ở đoạn dưới, đây là ô
   duy nhất `getByRole(` được chấp nhận (vd toast của thư viện → `getByRole('alert')`); `getByRole` trỏ
   phần tử **trong** source project → nhóm 3, vì accessible name đổi theo nhãn QUCTHT thì test vẫn vỡ.
3. Còn lại → **gate FAIL**: phần tử thuộc source project đang bị định vị bằng selector giòn. Xử lý theo
   Blocker 2 (`blocker-playbook.md`) — thêm testid vào source rồi sửa test, KHÔNG hợp thức hoá bằng một
   dòng lý do trong `qa-run.md`.

**Ngoại lệ cấu hình cho `getByRole(`**: qa-context đã khai override role-based hợp lệ (chiến lược **đã chạy
sẵn** trong project, có lý do trong `qa-run.md` — xem `test-generation.md`) → **bỏ `getByRole\(` khỏi regex
quét**; mọi pattern cấm còn lại vẫn quét như thường. Không có khai báo đó thì không có ngoại lệ, và ngoại lệ
này KHÔNG mở rộng sang CSS/xpath/text.

`.nth(i)` / `.first()` / `.last()` gọi **trên một locator/element** (không phải mảng JS thường — đó là
nhóm 0) không bao giờ thuộc nhóm 1 hoặc 2: luôn FAIL, vì thứ tự hàng đổi theo lọc/sắp xếp/phân trang nên
lượt chạy lại tác động nhầm hàng. `.filter({ hasText })` cũng vậy — nó là "khớp text trần để định vị"
dưới một API khác, chỉ hợp lệ khi nằm trong `expect(...)` (nhóm 1).

Không có thư mục E2E (project chưa có tầng E2E) → bước này `N/A`, ghi vào artifact; **không** được coi là
PASS ngầm.

## Bước 3 — Chặn assertion tầm thường (trivial)

Test có compile được và selector/endpoint có tồn tại vẫn có thể là "xanh giả" nếu assertion không thực
sự kiểm tra gì (assert luôn đúng). Grep các pattern tầm thường phổ biến trong toàn bộ test mới sinh và
gắn cờ:

- `toBeTruthy()` đứng một mình (không kèm assertion cụ thể khác trên cùng giá trị).
- `not.toBeNull()` / `not.toBeUndefined()` đứng một mình, không kiểm tra giá trị/attribute cụ thể.
- `toHaveURL(/.*/)` hoặc regex match-all tương đương (chấp nhận mọi URL = không kiểm tra gì).
- Test/case rỗng thân (không có assertion nào) hoặc chỉ có `expect(true).toBe(true)` / tương đương.

```bash
grep -rnE 'toBeTruthy\(\)|not\.toBeNull\(\)|not\.toBeUndefined\(\)|toHaveURL\(/\.\*/\)|expect\(true\)\.toBe\(true\)' <test-dir>
```

Mỗi dòng khớp → xem lại: có được dùng kèm assertion khác chặt hơn trên cùng biến không (chấp nhận nếu
là điều kiện phụ), hay là **assertion duy nhất** của test đó (tầm thường thật → phải sửa thành assertion
cụ thể theo acceptance criteria).

## Kết quả gate

Tổng hợp 4 bước thành một trạng thái duy nhất, ghi vào `qa-run.md` (Pha 6):

- **PASS** — compile/type-check xanh; không còn dòng `MISSING` (mọi dòng `DYNAMIC?` đã mở source xác nhận
  theo Caveat); mọi dòng khớp ở Bước 2b đã xếp vào nhóm 0, 1 hoặc 2 kèm ghi chú; không còn assertion tầm
  thường trơ trọi.
- **FAIL** — liệt kê cụ thể: lỗi compile (nếu có), từng dòng `MISSING`, từng dòng locator giòn nhóm 3,
  từng vị trí assertion tầm thường. Quay lại Pha 5 sửa, chạy lại gate — **không tiến sang Pha 7/8 khi gate còn FAIL**, và không
  present kết quả dựa trên test chưa qua gate.
