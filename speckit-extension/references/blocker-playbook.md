# Playbook gỡ blocker — auth / selector / config / seed (Pha 7, agnostic)

## Nội dung

1. [Khuôn xử lý chung cho mọi blocker](#khuôn-xử-lý-chung-cho-mọi-blocker)
2. [Blocker 1: E2E cần đăng nhập](#blocker-1-e2e-cần-đăng-nhập-test-401redirect-login-vì-chưa-có-session)
3. [Blocker 2: Thiếu selector ổn định](#blocker-2-thiếu-selector-ổn-định-test-phải-dò-bằng-textcss-dễ-vỡ-hoặc-không-định-vị-được-phần-tử)
4. [Blocker 3: Thiếu cấu hình test framework](#blocker-3-thiếu-cấu-hình-test-framework-chưa-cài-chưa-init-thiếu-config-chạy-được)
5. [Blocker 4: Thiếu dữ liệu seed](#blocker-4-thiếu-dữ-liệu-seed-test-fail-vì-db-rỗng-hoặc-thiếu-record-tiền-điều-kiện)
6. [Nhắc lại nguyên tắc no-defer](#nhắc-lại-nguyên-tắc-no-defer)

Pha Readiness không chỉ dựng service (xem `environment-bringup.md`) — nó còn phải **tự gỡ** những vướng
mắc cụ thể khiến test không chạy được thật: thiếu cách đăng nhập cho E2E, thiếu selector ổn định, thiếu
cấu hình framework test, thiếu dữ liệu seed. Đây **không phải lý do để `test.skip`/né test** — mỗi
blocker dưới đây có một đường xử lý cụ thể, agnostic, đọc chi tiết stack từ `.agents/qa-context.md`.

## Khuôn xử lý chung cho mọi blocker

Với mỗi blocker gặp phải, luôn theo đúng trình tự:

1. **Symptom** — mô tả chính xác triệu chứng quan sát được (test fail vì gì, log gì).
2. **Recommended** — đề xuất cách xử lý **được khuyến nghị trước**, kèm **lý do** ngắn gọn tại sao đây là
   lựa chọn mặc định (không liệt kê nhiều phương án ngang hàng rồi hỏi người dùng chọn — luôn dẫn bằng
   một đề xuất Recommended, người dùng chỉ cần gật hoặc chỉnh).
3. **Escalation** — chỉ dừng hỏi người dùng khi việc tự làm vượt quá phạm vi an toàn (xem tiêu chí "gate"
   ở mỗi mục), nêu rõ phần thiếu + đề xuất cụ thể, chờ phản hồi rồi tiếp tục — không bỏ ngang, không âm
   thầm coi là "N/A" hay pass.

Nguồn sự thật cho chi tiết stack (framework nào, đường auth nào, chiến lược selector nào...) luôn là
`.agents/qa-context.md` khối *Đủ-để-chạy* — playbook này chỉ mô tả **thuật toán** áp dụng, không hardcode
tên công cụ.

---

## Blocker 1: E2E cần đăng nhập (test 401/redirect login vì chưa có session)

**Symptom:** test E2E fail ngay ở bước đầu vì bị redirect sang trang login, hoặc request API trả
401/403 — chưa có session/token hợp lệ trước khi chạy kịch bản chính.

**Recommended:** dùng cơ chế lưu session sẵn có của framework E2E (kiểu "storage state" / session
snapshot tái dùng giữa các test) thay vì đăng nhập lại qua UI ở từng test. Lấy token/cookie qua **đường
auth thật của project** — đọc cơ chế cụ thể (endpoint, grant type, tài khoản test) từ mục *Auth E2E*
trong `.agents/qa-context.md`.

**Lý do:** đăng nhập qua UI ở mỗi test vừa chậm vừa giòn (phụ thuộc UI login có thể đổi); tái dùng session
đã xác thực qua đúng đường auth của hệ thống vừa nhanh vừa test đúng cơ chế thật (không bypass auth bằng
cách giả lập token sai luồng).

**Thực hiện (thuật toán, agnostic):**
1. Đọc `.agents/qa-context.md` để biết đường auth (vd: password-grant, form login, SSO...) và tài khoản
   test có sẵn.
2. Thiếu thông tin (chưa có tài khoản test, chưa rõ luồng auth) → scan repo tìm seed user/tài liệu auth
   trước; vẫn thiếu → escalate (không tự đoán credential).
3. Viết bước dựng session **một lần** (login qua đúng luồng auth, lưu lại state) và tái dùng cho các test
   cần session, theo đúng cơ chế mà framework E2E đang dùng hỗ trợ.
4. Ghi lại cách làm vào qa-context để lần chạy sau không phải dò lại.

**Escalation:** không có tài khoản test / secret cần thiết để đăng nhập (password, client secret...) và
không thể tự sinh an toàn → nêu rõ đang thiếu credential nào, đề xuất cách cung cấp (biến môi trường,
seed sẵn trong qa-context), chờ người dùng bổ sung rồi tiếp tục.

## Blocker 2: Thiếu selector ổn định (test phải dò bằng text/CSS dễ vỡ, hoặc không định vị được phần tử)

**Symptom:** test phải dùng selector giòn (CSS class có thể đổi theo style, text hiển thị có thể đổi
theo nội dung/locale, xpath theo cấu trúc DOM) để định vị phần tử, hoặc không tìm được phần tử ổn định
nào để assert/interact.

**Recommended:** thêm test id vào phần tử liên quan, theo đúng **chiến lược selector** đã khai báo trong
`.agents/qa-context.md` (mục *Đủ-để-chạy → Selector*, vd quy ước đặt tên, thuộc tính dùng).

**Lý do:** test id là hợp đồng tường minh giữa test và UI — tách rời khỏi style/nội dung nên không vỡ
khi refactor CSS hay đổi copy; nhất quán với chiến lược sẵn có trong qa-context thay vì mỗi lần bịa một
kiểu selector mới.

**Gate — khi nào KHÔNG tự sửa mà phải dừng hỏi:** nếu việc thêm test id đòi hỏi sửa **nhiều file mã
nguồn sản phẩm** (không phải file test) — vượt quá vài chỗ chạm nhỏ, lan sang nhiều component/màn hình
khác nhau — đây là thay đổi có ảnh hưởng vượt phạm vi "gỡ blocker test" thông thường. Dừng lại, liệt kê
chính xác danh sách file/vị trí cần thêm test id, đề xuất Recommended (thêm test id tối thiểu, không đổi
hành vi/markup khác), và **chờ duyệt** trước khi sửa hàng loạt.

**Thực hiện khi không bị gate (thay đổi nhỏ, cục bộ):**
1. Xác định phần tử cần selector ổn định.
2. Thêm test id đúng quy ước qa-context, không đổi behavior/style của phần tử.
3. Cập nhật test dùng test id mới.
4. Nếu qa-context chưa có mục *Selector* → suy ra từ selector đã tồn tại trong codebase (nếu có), ghi lại
   quy ước vào qa-context; hoàn toàn chưa có tiền lệ nào → escalate hỏi chọn quy ước trước khi thêm hàng
   loạt.

## Blocker 3: Thiếu cấu hình test framework (chưa cài, chưa init, thiếu config chạy được)

**Symptom:** lệnh chạy test báo thiếu framework (`command not found`, module không tồn tại), hoặc
framework đã cài nhưng chưa có file config cần thiết (vd config trình duyệt, base URL, reporter) nên
chạy ra lỗi cấu hình thay vì lỗi test thật.

**Recommended:** cài đặt/khởi tạo đúng framework và cấu hình đã khai báo trong `.agents/qa-context.md`
(mục *Công cụ test* — framework, thư mục, lệnh chạy). Nếu qa-context chưa ghi rõ, scan tín hiệu repo
(file lock, config mẫu đã tồn tại, README) để suy ra, rồi ghi lại.

**Lý do:** qa-context là nguồn sự thật duy nhất về stack test của project — cài đúng theo đó tránh việc
mỗi lần chạy lại phải đoán lại phiên bản/cấu hình, và giữ nhất quán với những gì team đã quyết định.

**Thực hiện:**
1. Đọc mục *Công cụ test* trong qa-context để biết framework + lệnh cài/chạy.
2. Thiếu → scan file lock/manifest (package.json, `*.csproj`, pyproject.toml...) xem framework đã khai
   báo dependency chưa; có → cài theo đúng version khai báo, không tự ý nâng version.
3. Chạy lệnh cài/init cần thiết (vd cài browser cho E2E, generate config mẫu).
4. Xác nhận lệnh chạy test tối thiểu (smoke) hoạt động trước khi coi blocker đã gỡ.
5. Ghi lại lệnh đã dùng vào qa-context.

**Escalation:** cài đặt đòi hỏi quyền/mạng không có (tải package bị chặn tường lửa, cần license/key cho
tool trả phí) → nêu rõ đang thiếu gì, đề xuất lệnh cụ thể người dùng cần chạy, chờ rồi tiếp tục.

## Blocker 4: Thiếu dữ liệu seed (test fail vì DB rỗng hoặc thiếu record tiền điều kiện)

**Symptom:** test fail vì không tìm thấy dữ liệu tiền điều kiện (record không tồn tại, danh sách rỗng
lẽ ra phải có item, quan hệ FK trỏ tới bản ghi chưa được tạo).

**Recommended:** seed dữ liệu qua **đường chính thức của project** (API nghiệp vụ hoặc công cụ
migrate/seed sẵn có) — đọc cách seed cụ thể từ mục *Đủ-để-chạy → Seed* trong `.agents/qa-context.md`,
**không** thao tác thẳng vào DB (insert tay/SQL trực tiếp) trừ khi đó chính là cách project quy định.

**Lý do:** seed qua API/migrator đi qua đúng validation và side-effect mà nghiệp vụ thật yêu cầu (vd
trigger, event, ràng buộc) — insert thẳng DB dễ tạo dữ liệu "giả hợp lệ" nhưng sai bất biến nghiệp vụ,
khiến test pass giả trong khi luồng thật sẽ fail.

**Thực hiện:**
1. Đọc qa-context mục *Seed* để biết cơ chế (endpoint tạo dữ liệu test, script seed, lệnh migrator kèm
   fixture...).
2. Thiếu → scan repo tìm script/lệnh seed đã tồn tại (DbMigrator, seed script, migration có sẵn fixture,
   factory trong test cũ) trước khi tự viết mới; ghi lại vào qa-context sau khi xác định.
3. Seed đúng lượng tối thiểu cần cho kịch bản, và **dọn dẹp sau khi test xong** (đọc cơ chế dọn cùng mục
   *Seed*) để không rò rỉ dữ liệu ảnh hưởng lần chạy sau.
4. Không có cơ chế dọn sẵn → seed dữ liệu có định danh rõ ràng (prefix/tag test) để có thể nhận diện và
   dọn thủ công, ghi rõ trong ma trận kết quả.

**Escalation:** không có đường seed chính thức nào (không API, không script, không migrator hỗ trợ
fixture) và việc tạo dữ liệu đòi hỏi quyết định nghiệp vụ (business rule không rõ ràng từ spec) → nêu rõ
thiếu gì, đề xuất Recommended (thường là: bổ sung endpoint/script seed tối thiểu, hoặc xin dữ liệu mẫu từ
người có domain knowledge), chờ rồi tiếp tục.

---

## Nhắc lại nguyên tắc no-defer

Không blocker nào ở trên là lý do để `test.skip`/`.only`/tương đương hay báo "Pass" giả. Không tự gỡ
được ngay → ghi "chưa chạy" kèm lý do cụ thể trong ma trận, escalate đúng phần bị chặn, chờ phản hồi, rồi
tiếp tục pha — không chuyển sang coi pha là hoàn tất trong lúc còn blocker mở.
