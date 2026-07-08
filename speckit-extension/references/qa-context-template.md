# Template `.agents/qa-context.md` — bề mặt cấu hình đặc thù stack

## Vì sao file này tồn tại

`.agents/qa-context.md` là nơi **DUY NHẤT** chứa mọi thứ đặc thù stack: framework test từng tầng, thư
mục test, lệnh chạy/serve/migrate/seed, cách dựng môi trường, cơ chế auth E2E, chiến lược selector,
lệnh compile/type-check. Skill `qa-spec-cycle` bản thân **không hardcode** bất kỳ tên framework hay
lệnh cụ thể nào — mọi thao tác cụ thể trong các pha (author test, dựng env, quality gate...) đều **đọc
từ file này**.

**Quy tắc hai lớp:**

| Lớp | Chứa gì |
|-----|---------|
| **Skill (engine, agnostic)** | Thuật toán, 13 pha, nguyên tắc, câu hỏi phỏng vấn, format xlsx |
| **`.agents/qa-context.md` (config, per-project)** | Framework, thư mục, **lệnh**, môi trường, auth, selector — tất cả đặc thù stack |

Đổi stack (Angular → Vue, ABP → NestJS...) = sửa `qa-context.md`, **không đụng vào skill**.

Cách file này được điền: **scan trước, hỏi sau** (xem §3/§4 dưới). Thiếu field nào → thử scan để tự
suy ra và **thông báo** cho người dùng biết đã suy ra gì; chỉ hỏi khi scan không đủ tự tin.

## Nội dung

1. [Template slim (4 khối)](#1-template-slim-4-khối--chép-nguyên-khi-tạo-file-mới)
2. [Scan trước — tín hiệu tự dò để điền, không hỏi](#2-scan-trước--tín-hiệu-tự-dò-để-điền-không-hỏi)
3. [Câu hỏi phỏng vấn — chỉ hỏi khi scan không đủ](#3-câu-hỏi-phỏng-vấn--chỉ-hỏi-khi-scan-không-đủ)
4. [Sau khi điền](#4-sau-khi-điền)

> **Lưu ý quan trọng:** file đích là `.agents/qa-context.md` (slim, 4 khối). **KHÔNG** tái sử dụng hay
> tham chiếu một `qa-project-context.md` verbose có sẵn trong repo (nếu có) — đó là artefact của skill
> khác, khác mục đích và khác cấu trúc. Nếu phát hiện file đó tồn tại, vẫn tạo `.agents/qa-context.md`
> mới theo template dưới đây (có thể tham khảo nội dung cũ để rút thông tin, nhưng không copy nguyên
> cấu trúc).

## 1. Template slim (4 khối) — chép nguyên khi tạo file mới

Khi tạo `.agents/qa-context.md` cho một project, chép đúng khung dưới, thay `<placeholder>` bằng giá
trị thật đã scan/hỏi được. Không được để lại `<placeholder>` chưa điền trong file cuối cùng.

```markdown
# QA Context — <project>

## Test pyramid (phương châm)
- Unit (đáy, nhiều nhất): <FE unit framework>, <BE unit framework>. ~60% logic quan trọng.
- Integration (giữa): <BE integration>, <API test>.
- E2E (đỉnh, ít nhất): <E2E framework> — chỉ critical journeys + vài negative chính.
- Luật: đẩy assertion xuống tầng thấp nhất chứng minh được; E2E chỉ cho luồng người dùng thật.

## Công cụ test
| Tầng | Framework | Thư mục | Lệnh |
|------|-----------|---------|------|
| FE unit | <framework> | <thư mục test> | <lệnh chạy> |
| BE unit/integration | <framework> | <thư mục test> | <lệnh chạy> |
| E2E / API | <framework> | <thư mục test> | <lệnh chạy> |

## Đủ-để-chạy
- Selector: <chiến lược chọn selector, vd data-testid kebab-case>.
- Seed: <cách seed dữ liệu test + cách dọn>.
- Auth E2E: <cơ chế session/storage-state + cách lấy token/login của project>.
- Base URL: <FE base URL> / <API base URL>.

## Môi trường & lệnh dựng
- Services:        <lệnh dựng service phụ thuộc, vd DB/cache/mail>          # <ghi chú port/ready-check>
- Test DB (dùng-một-lần): <connection string/DB name/container riêng, tách biệt khỏi DB dev>
- An toàn để migrate/seed/reset? (bắt buộc = có, nếu không thì skill sẽ hỏi): <có/không>
- Migrate/seed:    <lệnh migrate + seed dữ liệu — CHỈ chạy nhắm vào "Test DB" ở trên>
- Start backend:   <lệnh chạy backend>                                       # <port, tín hiệu ready>
- Start frontend:  <lệnh chạy frontend>                                      # <port, tín hiệu ready>
- Test deps:       <lệnh cài dependency cho test, vd browser cho E2E>
- Compile-check:   <lệnh compile/type-check FE> / <lệnh compile-check BE>    # dùng ở quality gate (pha 6)
```

`Test DB (dùng-một-lần)` là field **bắt buộc** trước khi pha *Dựng môi trường* (xem
`environment-bringup.md` §3) được phép chạy bất kỳ lệnh phá-huỷ dữ liệu nào (migrate/seed/reset). Nếu
field này thiếu hoặc chỉ trỏ tới DB dev, skill **phải dừng lại và hỏi** thay vì tự ý migrate/seed/reset
DB dev — xem chi tiết gate ở `environment-bringup.md` §3.

Mỗi `<placeholder>` phải được thay bằng giá trị cụ thể của project đang xử lý — không bao giờ để
skill tự ý gán một framework/lệnh mặc định nào "cho chắc".

### Ví dụ đã điền (chỉ để minh hoạ cách điền — KHÔNG phải giá trị mặc định của skill)

```markdown
## Công cụ test
| Tầng | Framework | Thư mục | Lệnh |
|------|-----------|---------|------|
| FE unit | Vitest | co-located *.spec.ts | npm run test:unit |
| BE unit/integration | xUnit | aspnet-core/test/... | dotnet test test/admin_mbf.Application.Tests |
| E2E / API | Playwright (+APIRequestContext) | tests/e2e | npm run e2e |

## Môi trường & lệnh dựng
- Services:        docker compose up -d          # Postgres :5432, Mailpit :1026/:8026
- Test DB (dùng-một-lần): admin_mbf_test trên cùng Postgres instance (connection string riêng qua
  `ConnectionStrings__Default` khi chạy DbMigrator cho test — KHÔNG dùng conn string dev mặc định)
- An toàn để migrate/seed/reset? (bắt buộc = có, nếu không thì skill sẽ hỏi): có
- Migrate/seed:    dotnet run --project src/admin_mbf.DbMigrator  # nhắm vào admin_mbf_test, không phải admin_mbf
- Start backend:   dotnet run --project src/admin_mbf.HttpApi.Host   # :44368, ready khi Swagger 200
- Start frontend:  npm start -- --port 4300                          # ready khi app-root render
- Test deps:       npx playwright install chromium
- Compile-check:   tsc --noEmit (FE) / dotnet build (BE)
```

Đây chỉ là ví dụ của một repo cụ thể (ABP + Angular). Với project khác (Node/Express + React, Django +
Vue, v.v.), toàn bộ cột "Framework"/"Lệnh" sẽ khác hoàn toàn — skill không được giả định bất kỳ giá trị
nào trong ví dụ trên là mặc định.

## 2. Scan trước — tín hiệu tự dò để điền, không hỏi

Trước khi hỏi người dùng bất kỳ câu nào, scan các nguồn sau trong repo để tự suy ra field còn thiếu.
Khi scan thành công, **thông báo** ngắn gọn (vd: "Phát hiện `docker-compose.yml` có service `postgres`
→ dùng `docker compose up -d` cho khối Services") thay vì hỏi lại.

| Tín hiệu quét | Field được điền |
|---|---|
| `docker-compose.yml` / `compose.yaml` | Services (tên service, port expose) → khối *Môi trường & lệnh dựng* |
| `Makefile` / `Taskfile.yml` | Lệnh tổng hợp có sẵn (test, build, seed, run) — ưu tiên dùng nếu có, tránh suy diễn lại từ nguồn thấp hơn |
| `package.json` (`scripts`) | Lệnh FE: dev/start, build, test, e2e, lint, type-check (`tsc --noEmit`) |
| `*.csproj` / `*.sln` (.NET) | Project layout, lệnh `dotnet build`/`dotnet test`/`dotnet run --project ...`, migrator project |
| `pyproject.toml` / `requirements.txt` (Python) | Test runner (pytest), lệnh cài deps, entrypoint chạy app |
| `README.md` / `CONTRIBUTING.md` | Lệnh dựng môi trường, thứ tự bootstrap, ghi chú port/ready-check mà maintainer đã viết sẵn |
| CI config (`.github/workflows/*.yml`, `.gitlab-ci.yml`, v.v.) | Lệnh "nguồn sự thật" vì đã được verify chạy được — ưu tiên cao khi mâu thuẫn với suy đoán khác |
| Thư mục test hiện có (`*.spec.ts`, `test/`, `tests/`, `__tests__/`) | Framework test đang dùng thực tế (đọc import/dependency trong file mẫu), thư mục test cho khối *Công cụ test* |

Thứ tự ưu tiên khi nhiều nguồn cho kết quả khác nhau: **CI config > Makefile/Taskfile > package.json /
*.csproj script > README** (CI là thứ đã chạy thật, README có thể lỗi thời).

## 3. Câu hỏi phỏng vấn — chỉ hỏi khi scan không đủ

Khi một field không thể suy ra chắc chắn từ scan, hỏi qua `AskUserQuestion`, luôn để **phương án
Recommended lên đầu kèm lý do**. Gợi ý bộ câu hỏi theo từng khối:

### Test pyramid
- **Q:** "Tầng nào là đáy pyramid cho phần logic quan trọng của project này?"
  **Recommended:** framework unit test đã có trong repo (nếu scan thấy) — lý do: tận dụng setup sẵn,
  tránh thêm framework mới không cần thiết.

### Công cụ test
- **Q:** "FE/BE dùng framework test nào cho từng tầng (unit/integration/E2E)?"
  **Recommended:** framework tìm thấy qua scan dependency (`package.json`, `*.csproj`) — lý do: khớp
  với những gì project đã cài, không phát sinh dependency mới.
- **Q:** "Thư mục chứa test nằm ở đâu — co-located cạnh source hay thư mục `test/`/`tests/` riêng?"
  **Recommended:** theo convention đã thấy trong repo (nếu có ít nhất 1 file test mẫu) — lý do: giữ
  nhất quán với pattern hiện có.

### Đủ-để-chạy
- **Q:** "Chiến lược chọn selector cho E2E là gì (data-testid, role/text, CSS class)?"
  **Recommended:** `data-testid` — lý do: bền hơn khi refactor UI, không phụ thuộc CSS/text đổi theo
  locale.
- **Q:** "Dữ liệu test được seed và dọn dẹp thế nào (seed script, migration seed, fixture per-test)?"
  **Recommended:** script seed đã có trong repo (nếu scan thấy migrator/seed command) — lý do: tránh
  hai nguồn seed khác nhau gây lệch dữ liệu.
- **Q:** "E2E xác thực bằng cơ chế nào (session cookie, storage-state file, bearer token lấy qua API)?"
  **Recommended:** cơ chế auth thật của app (suy từ code auth hiện có) — lý do: test phải đi đúng luồng
  auth thật, không bypass để tránh false-positive.
- **Q:** "Base URL của FE/API khi chạy local là gì?"
  **Recommended:** port đọc được từ script `start`/`serve` hoặc `docker-compose.yml` — lý do: khớp với
  môi trường dev thật, tránh hard-code sai port.

### Môi trường & lệnh dựng
- **Q:** "Cần dựng service phụ thuộc nào trước khi chạy test (DB, cache, mail catcher...) và bằng lệnh
  gì?"
  **Recommended:** lệnh `docker compose up -d` (hoặc tương đương) nếu có `docker-compose.yml` — lý do:
  một lệnh dựng toàn bộ hạ tầng phụ thuộc, tránh cấu hình tay từng service.
- **Q (bắt buộc trước khi migrate/seed lần đầu):** "Database dùng để test là DB riêng dùng-một-lần
  (throwaway), hay là DB dev đang dùng hằng ngày?" — hỏi câu này **trước khi tự ý migrate/seed/reset**
  bất cứ DB nào; **không được mặc định DB dev là đích test**.
  **Recommended:** dựng một DB/container riêng dùng-một-lần cho test (vd `<project>_test` trên cùng
  instance, hoặc container Postgres ephemeral riêng) — lý do: cô lập hoàn toàn khỏi dữ liệu dev, migrate/
  seed/reset thoải mái mà không rủi ro mất dữ liệu thật.
  **Alt:** người dùng tự xác nhận một DB/connection string throwaway cụ thể đã có sẵn — dùng khi họ đã
  có sẵn hạ tầng test riêng.
  Nếu field `Test DB (dùng-một-lần)` trong §1 chưa có giá trị, hoặc câu trả lời cho thấy chỉ có DB dev
  → coi như chưa xong câu hỏi này, **không tiến hành migrate/seed** cho tới khi có đích an toàn (xem
  gate chi tiết ở `environment-bringup.md` §3).
- **Q:** "Lệnh migrate + seed database là gì (nhắm vào Test DB dùng-một-lần ở trên), và tín hiệu nào cho
  biết backend/frontend đã sẵn sàng (ready-check)?"
  **Recommended:** lệnh migrator/seed sẵn có trong repo, tham số hoá để trỏ vào Test DB thay vì DB mặc
  định, + endpoint health-check hoặc trang chủ render được — lý do: tránh polling mù, có tín hiệu rõ
  ràng để pha *Readiness* (pha 7) biết khi nào dừng chờ, và tránh mutate nhầm DB dev.
- **Q:** "Lệnh compile/type-check dùng ở quality gate là gì?"
  **Recommended:** lệnh build/type-check chuẩn của toolchain (vd `tsc --noEmit`, `dotnet build`,
  `pytest --collect-only`) — lý do: đây là cổng rẻ nhất để bắt lỗi cú pháp/type trước khi chạy test tốn
  thời gian hơn.

## 4. Sau khi điền

Ghi lại toàn bộ giá trị đã scan/hỏi vào `.agents/qa-context.md` theo đúng khung ở §1 — không giữ lại
`<placeholder>` nào. Lần chạy sau, pha *Context* chỉ cần load file này, không phải scan/hỏi lại (trừ
khi field bị thiếu hoặc project đổi stack).
