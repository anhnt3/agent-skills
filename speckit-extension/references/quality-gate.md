# Quality gate — chặn fake-green (Pha 6)

Cổng cơ học, chạy **sau khi sinh test tự động** (Pha 5) và **trước khi chạy suite thật + present**
(Pha 8/9). Mục tiêu: AI hay sinh test "xanh giả" — assert rỗng/tầm thường, hoặc gọi selector/endpoint
không tồn tại trong source (ảo giác). Cổng này bắt các trường hợp đó bằng kiểm tra máy móc, không suy
diễn.

> *Nếu có Task/Agent tool: chạy pha này trong subagent con, chỉ nhận summary + artifact (xem "Ủy thác
> cho subagent" trong SKILL.md). Không có tool → làm inline.*

## Nội dung

1. [Bước 1 — Compile / type-check](#bước-1--compile--type-check)
2. [Bước 2 — Grep selector/endpoint tồn tại trong source](#bước-2--grep-selectorendpoint-tồn-tại-trong-source)
3. [Bước 3 — Chặn assertion tầm thường (trivial)](#bước-3--chặn-assertion-tầm-thường-trivial)
4. [Kết quả gate](#kết-quả-gate)

**Nguyên tắc:** bất kỳ selector/endpoint MISSING nào, hoặc lỗi compile/type-check, đều coi là ảo giác
(hallucination) → phải sửa trước khi chạy suite hoặc trình bày kết quả. Không được present kết quả khi
gate chưa xanh.

## Bước 1 — Compile / type-check

Chạy lệnh compile/type-check của project (tra ở mục *Đủ-để-chạy*/*Môi trường & lệnh dựng* trong
`.agents/qa-context.md`, khối "Compile-check"). Đây là kiểm tra rẻ nhất, chạy trước tiên: nếu code test
mới sinh không compile được, dừng ngay — không cần chạy các bước sau.

- Có nhiều tầng (vd FE + BE) → chạy compile-check cho **từng tầng có test mới**.
- Lỗi compile/type-check ở bất kỳ tầng nào → gate **fail ngay**, liệt kê lỗi, quay lại Pha 5 sửa test.

**Ví dụ (repo này):** `tsc --noEmit` cho `angular/` (nếu có test FE mới); `dotnet build admin_mbf.slnx`
cho `aspnet-core/` (nếu có test BE mới).

## Bước 2 — Grep selector/endpoint tồn tại trong source

Test tự động chỉ được coi là hợp lệ nếu mọi selector/test-id và mọi endpoint/route nó tham chiếu **thật
sự tồn tại trong source code**, không phải suy đoán từ tên biến hợp lý.

**Thuật toán (agnostic):**
1. Trích danh sách selector/test-id và endpoint/route được tham chiếu trong các file test vừa sinh (regex
   theo pattern selector của project, tra ở qa-context — vd `data-testid="..."`, `getByTestId(...)`, path
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

**Ví dụ (repo này — selector FE):**

```bash
grep -rhoE 'data-testid="[a-z0-9-]+"' angular/e2e | sort -u | sed -E 's/.*"(.*)"/\1/' | while read -r sel; do
  if ! grep -rq "data-testid=\"$sel\"" angular/src; then
    echo "MISSING: $sel"
  fi
done
```

**Ví dụ (repo này — endpoint BE, ABP auto-route theo AppService method):**

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

Tổng hợp 3 bước thành một trạng thái duy nhất, ghi vào `qa-run.md` (Pha 6):

- **PASS** — compile/type-check xanh, không có dòng `MISSING`, không còn assertion tầm thường trơ trọi.
- **FAIL** — liệt kê cụ thể: lỗi compile (nếu có), từng dòng `MISSING`, từng vị trí assertion tầm
  thường. Quay lại Pha 5 sửa, chạy lại gate — **không tiến sang Pha 7/8 khi gate còn FAIL**, và không
  present kết quả dựa trên test chưa qua gate.
