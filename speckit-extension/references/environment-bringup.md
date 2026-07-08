# Dựng môi trường — engine chống-defer (Pha 7 — Readiness)

Pha này trả lời một câu duy nhất: **test có chạy được thật trên môi trường thật không?** Skill **không
hardcode** lệnh dựng của bất kỳ stack nào — nó tự khám phá cách dựng, tự thực thi, và **không bao giờ**
bỏ qua bước này bằng cách tuyên bố "không có môi trường" hay đánh dấu test skip để né việc dựng env.
Đây là engine hiện thực hoá nguyên tắc 6 (no-defer) của skill: **một pha không tính là "xong" khi còn
test chưa chạy thật.**

> *Nếu có Task/Agent tool: chạy pha này trong subagent con, chỉ nhận summary + artifact (xem "Ủy thác
> cho subagent" trong SKILL.md). Không có tool → làm inline.*

## Nội dung

1. [Thuật toán khám phá lệnh dựng](#1-thuật-toán-khám-phá-lệnh-dựng)
2. [Thứ tự dựng tổng quát (agnostic)](#2-thứ-tự-dựng-tổng-quát-agnostic)
3. [Phân loại lệnh: an toàn vs phá-huỷ dữ liệu — gate bắt buộc](#3-phân-loại-lệnh-an-toàn-vs-phá-huỷ-dữ-liệu--gate-bắt-buộc-trước-khi-mutate)
4. [Mẫu chạy nền + poll readiness (agnostic)](#4-mẫu-chạy-nền--poll-readiness-agnostic)
5. [Quy tắc cứng chống-defer](#5-quy-tắc-cứng-chống-defer)
6. [Hợp đồng escalation](#6-hợp-đồng-escalation--chỉ-hỏi-khi-thật-sự-không-tự-làm-được)
7. [Ví dụ (đã điền trong qa-context)](#ví-dụ-đã-điền-trong-qa-context)

## 1. Thuật toán khám phá lệnh dựng

1. **Đọc `.agents/qa-context.md`, khối *Môi trường & lệnh dựng*.** Có đủ field (Services, Migrate/seed,
   Start backend, Start frontend, Test deps, Compile-check) → dùng thẳng, không scan lại.
2. **Thiếu field nào → scan tín hiệu trong repo để tự suy ra**, theo thứ tự ưu tiên khi nhiều nguồn mâu
   thuẫn nhau (CI đã chạy thật > Makefile/Taskfile > package.json/`*.csproj` script > README, vì README
   dễ lỗi thời):

   | Tín hiệu quét | Suy ra được gì |
   |---|---|
   | `docker-compose.yml` / `compose.yaml` | Services phụ thuộc (DB/cache/mail) + lệnh dựng (`docker compose up -d`) + port expose |
   | `Makefile` / `Taskfile.yml` | Lệnh tổng hợp có sẵn (`make dev`, `task migrate`...) — ưu tiên dùng nếu có, tránh suy diễn lại từ nguồn thấp hơn |
   | `package.json` (`scripts`) | Lệnh start FE (`dev`/`start`), lệnh cài deps test (`npx playwright install`...) |
   | `*.sln` / `*.csproj` / `pyproject.toml` | Lệnh build/run/migrate của backend (`dotnet run --project ...`, `alembic upgrade head`, `manage.py migrate`...) |
   | `README.md` / `CONTRIBUTING.md` | Thứ tự bootstrap, ghi chú port/ready-check mà maintainer đã viết sẵn |
   | CI config (`.github/workflows/*.yml`, `.gitlab-ci.yml`...) | Lệnh "nguồn sự thật" vì đã verify chạy được trong pipeline — ưu tiên cao nhất khi có mâu thuẫn |

3. **Ghi lại kết quả suy ra vào `.agents/qa-context.md`** (khối *Môi trường & lệnh dựng*), kèm thông báo
   ngắn gọn đã suy ra gì và từ tín hiệu nào (vd: "Phát hiện `docker-compose.yml` có service `postgres` →
   dùng `docker compose up -d` cho Services"). Lần chạy sau không phải scan lại.
4. **Không tìm được tín hiệu nào cho một bước bắt buộc** (vd không có cách nào suy ra lệnh migrate) →
   đây là ứng viên cho escalation (§6), không phải lý do bỏ qua bước đó trong im lặng.

## 2. Thứ tự dựng tổng quát (agnostic)

Dựng theo đúng thứ tự phụ thuộc dưới đây — bỏ qua thứ tự này (vd chạy test trước khi service sẵn sàng)
là nguồn phổ biến nhất của false-negative/false-positive:

1. **Services phụ thuộc** (DB/cache/mail catcher...) — chạy nền (background/detached), không phải
   foreground, vì bước sau còn phải chạy tiếp.
2. **Migrate/seed** — chạy đồng bộ (foreground, chờ xong), vì các bước sau cần schema/dữ liệu đã sẵn.
   **Đây là lệnh phá-huỷ dữ liệu → phải qua gate an toàn ở §3 trước khi chạy.**
3. **Start backend** (background/detached).
4. **Start frontend** (background/detached).
5. **Cài browser/dependency cho test** (vd `npx playwright install`) — có thể chạy song song với bước
   3–4 nếu không phụ thuộc backend/frontend đã lên.
6. **Poll cổng/health-check tới khi ready** (§4) — bắt buộc, không được chạy suite ngay sau lệnh start
   detached vì tiến trình có thể chưa nhận request.
7. **Chạy suite test thật.**

## 3. Phân loại lệnh: an toàn vs phá-huỷ dữ liệu — gate bắt buộc trước khi mutate

Không phải mọi lệnh trong §1/§2 đều "cứ chạy": phải phân loại trước khi thực thi.

**An toàn (chạy tự do, không cần hỏi)** — read-only, khởi động tiến trình, cài đặt phụ thuộc, poll:
- Start backend/frontend (chỉ *chạy* app, không tự tạo/xoá schema).
- Cài browser/dependency cho test (`npx playwright install`...).
- Compile/type-check, health-check, poll cổng, đọc log.
- `docker compose up -d` cho service **đã tồn tại và không re-init volume** (vd chỉ start lại container
  Postgres đã có sẵn data, không kèm `-v`/`--force-recreate` xoá volume).

**Phá-huỷ dữ liệu / mutating (GATED — không được tự chạy nếu chưa qua gate dưới)**:
- Tạo/xoá/reset database (`dropdb`, `createdb`, `migrate:reset`, `docker compose down -v`...).
- Chạy migration (`dotnet run --project ...DbMigrator`, `alembic upgrade head`, `prisma migrate deploy`,
  `manage.py migrate`...).
- Seed dữ liệu test (script seed, fixture load ghi đè bảng).
- Bất kỳ `docker compose up` nào **khởi tạo lần đầu hoặc reset** một volume có state (DB volume mới,
  hoặc `up --force-recreate`/`down -v` trước đó).

### Gate cứng — bắt buộc trước khi chạy BẤT KỲ lệnh phá-huỷ dữ liệu nào

Trước khi chạy lệnh thuộc nhóm "phá-huỷ dữ liệu" ở trên, phải xác nhận **đích đang nhắm tới là môi
trường test dùng-một-lần (disposable/throwaway)**, không phải DB dev thật của người dùng:

1. **Đọc field `Test DB (dùng-một-lần)` trong khối *Môi trường & lệnh dựng* của `.agents/qa-context.md`**
   (xem template §"Môi trường & lệnh dựng" trong `qa-context-template.md`). Field này phải trỏ tới một
   connection string/DB name/container **tách biệt** khỏi DB dev (vd DB tên `*_test`, container ephemeral
   riêng, hoặc `docker compose -f docker-compose.test.yml`).
2. **Field có giá trị cụ thể VÀ được đánh dấu "An toàn để migrate/seed/reset? = có"** → coi là đích an
   toàn, tiếp tục chạy lệnh phá-huỷ nhắm vào đích đó (không hỏi lại — đây vẫn là no-defer, không phải
   escalation).
3. **Field thiếu, để trống, hoặc chỉ trỏ tới DB dev (không có DB/khối riêng cho test)** → **DỪNG LẠI,
   không chạy lệnh phá-huỷ nào**, hỏi người dùng qua `AskUserQuestion` với phương án **Recommended lên
   đầu kèm lý do**, ví dụ:
   - **Recommended:** dựng container Postgres ephemeral riêng cho test (vd
     `docker run --rm -d -p 5433:5432 -e POSTGRES_DB=admin_mbf_test postgres:16`) hoặc tạo DB
     `<project>_test` riêng trên cùng instance — lý do: cô lập hoàn toàn khỏi dữ liệu dev, migrate/seed/
     reset thoải mái mà không mất dữ liệu thật.
   - **Alt:** người dùng tự xác nhận một DB/connection string throwaway cụ thể đã có sẵn (vd một DB
     staging riêng biệt) — dùng khi họ đã có sẵn hạ tầng test.
   - **Không bao giờ** tự ý migrate/seed/reset DB dev khi chưa có xác nhận rõ ràng — kể cả khi đó là cách
     "nhanh nhất" để tiếp tục.
4. Sau khi có đích an toàn (từ scan hoặc từ câu trả lời), **ghi lại vào `.agents/qa-context.md`** (field
   `Test DB (dùng-một-lần)` + đánh dấu an toàn = có) để lần chạy sau không phải hỏi lại.

**Quan trọng — đây không phải là defer:** dừng lại để xác nhận đích test an toàn rồi tiếp tục chạy pha
này **không vi phạm** nguyên tắc no-defer ở §5. No-defer cấm việc *bỏ qua/né tránh* dựng env hoặc chạy
test; gate này chỉ chặn một hành vi cụ thể — **mutate dữ liệu vào sai đích** — trước khi làm, không phải
lý do để hoãn cả pha. Mọi bước an toàn khác (services đã tồn tại, start backend/frontend, cài dep, poll,
chạy suite) vẫn phải tự làm ngay, không chờ gate này.

## 4. Mẫu chạy nền + poll readiness (agnostic)

Nguyên tắc: lệnh start server luôn được đưa ra nền (`&`, `nohup ... &`, hoặc job control của môi trường
chạy lệnh), sau đó **poll** URL/port trong vòng lặp có timeout, **không** đoán một khoảng `sleep` cố định
rồi coi là đã sẵn sàng — sleep cố định là nguồn flaky phổ biến (máy chậm/nhanh khác nhau).

Khung mẫu (thay `<start-command>`, `<health-url-or-port>`, `<timeout-giây>` theo qa-context/tín hiệu đã
suy ra ở §1):

```bash
# 1. Start detached, không block
<start-command> > /tmp/service.log 2>&1 &
PID=$!

# 2. Poll tới khi ready hoặc hết timeout
timeout=<timeout-giây>
elapsed=0
until curl -sf <health-url-or-port> > /dev/null 2>&1; do
  sleep 2
  elapsed=$((elapsed + 2))
  if [ "$elapsed" -ge "$timeout" ]; then
    echo "TIMEOUT: <start-command> chưa sẵn sàng sau ${timeout}s — xem log: /tmp/service.log"
    exit 1
  fi
done
echo "READY sau ${elapsed}s"
```

- Không có health endpoint HTTP → poll bằng cổng TCP mở (`nc -z host port`) hoặc tín hiệu log cụ thể
  (grep log tới khi thấy dòng "listening on..."), tuỳ cái gì đáng tin hơn cho stack đó — ghi lựa chọn
  này vào qa-context để lần sau không phải suy nghĩ lại.
- **TIMEOUT không phải là lý do bỏ qua test** — đây là blocker cần chẩn đoán (xem log vừa ghi) rồi hoặc
  tự sửa (sai port, thiếu biến môi trường tự suy ra được) hoặc escalate (§6).

## 5. Quy tắc cứng chống-defer

Các hành vi sau đây **bị cấm tuyệt đối** trong pha này, bất kể lý do gì (môi trường phức tạp, thiếu
thời gian, không chắc lệnh đúng):

- **Cấm viết `test.skip` / `.only` / `xit` / `xdescribe`** (và mọi cơ chế tương đương của framework
  đang dùng) để né việc dựng môi trường. Nếu một test không chạy được vì thiếu env, vấn đề nằm ở việc
  dựng env chưa xong — không nằm ở bản thân test, không được "tạm tắt" test để qua pha.
- **Test chưa chạy được → ghi rõ "chưa chạy" trong ma trận/kết quả**, kèm lý do cụ thể (vd "chưa chạy —
  backend không lên do thiếu biến môi trường X"). **Không bao giờ** báo cáo ngầm định là "Pass" hoặc bỏ
  qua dòng đó trong bảng kết quả.
- **Một pha không được tính là "xong" khi còn test chưa chạy thật.** Không tiến sang pha tiếp theo
  (present kết quả, đóng ticket...) chỉ vì đã hết cách — phải hoặc tiếp tục chẩn đoán, hoặc escalate rõ
  ràng theo §6 và **chờ** phản hồi rồi tiếp tục, không tự ý coi như xong.

## 6. Hợp đồng escalation — chỉ hỏi khi thật sự không tự làm được

Chỉ dừng lại hỏi người dùng khi vướng vào việc **kỹ thuật không thể tự vượt qua** được, không phải vì
chưa thử đủ:

- **Engine/runtime chưa cài** trên máy chạy (Docker daemon không chạy, .NET SDK thiếu, Python version
  sai...).
- **Secret/credential cần thiết** (API key, connection string tới service ngoài, cert...) mà repo không
  chứa và không thể tự sinh an toàn.
- **Quyền mạng/tường lửa** chặn truy cập cần thiết (pull image, gọi API ngoài...).

Khi escalate:
1. Nêu đúng phần đang thiếu (không mơ hồ — vd "Docker daemon không chạy, không tự start được từ agent").
2. Đưa ra **lệnh chính xác** người dùng cần chạy để gỡ vướng (vd `open -a Docker` rồi chờ daemon sẵn
   sàng, hoặc `export DATABASE_URL=...`).
3. **Chờ** người dùng thực hiện, rồi **tiếp tục pha từ điểm dừng** — không bỏ ngang, không chuyển sang
   coi pha là hoàn tất, không tự chuyển hướng sang việc khác thay cho việc bị chặn.

Mọi thứ khác (thiếu migrate command nhưng có thể suy ra từ `*.csproj`, port sai nhưng đọc được từ
`docker-compose.yml`, thiếu bước cài dep nhưng có trong `package.json`...) — **tự làm**, không hỏi.

## Ví dụ (đã điền trong qa-context)

Ví dụ cụ thể sau minh hoạ cách áp dụng cho **repo này** (ABP + Angular) — chỉ để tham khảo cách điền,
**không phải giá trị mặc định** của skill cho project khác. **Lưu ý:** trước khi chạy bước 2
(migrate/seed) trong thực tế, phải áp dụng gate §3 — connection string của `DbMigrator` phải trỏ tới DB
`*_test` riêng (qua biến môi trường/`appsettings`), không phải connection string dev mặc định trong
`appsettings.json`.

```bash
# 1. Services (Postgres, Mailpit) — nền
docker compose up -d

# 2. Migrate + seed — đồng bộ, chờ xong
dotnet run --project src/admin_mbf.DbMigrator

# 3. Start backend — nền, ready khi Swagger trả 200
nohup dotnet run --project src/admin_mbf.HttpApi.Host > /tmp/backend.log 2>&1 &
until curl -sfk https://localhost:44368/swagger/index.html > /dev/null 2>&1; do sleep 2; done

# 4. Start frontend — nền, ready khi app-root render (poll cổng)
nohup npm start -- --port 4300 --prefix angular > /tmp/frontend.log 2>&1 &
until curl -sf http://localhost:4300 > /dev/null 2>&1; do sleep 2; done

# 5. Test deps
npx playwright install chromium

# 6. Chạy suite thật
npm run e2e
```
