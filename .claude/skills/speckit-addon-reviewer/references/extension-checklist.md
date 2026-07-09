# Extension checklist

Extension = thêm command/template/script/hook mới qua `extension.yml`. Command namespace
`speckit.<ext-id>.<name>`. Review theo hai trục.

## Trục tất định (lint inline)

- [ ] Mọi command khai trong `provides.commands` có file tồn tại; mọi `commands/*.md` thực có
      được khai. Không mồ côi (file không khai = command chết).
- [ ] Tên command đúng namespace `speckit.<ext-id>.<name>`, khớp `extension.id`.
- [ ] **Gotcha #1 — build-zip**: grep mọi đường dẫn command tham chiếu
      (`.specify/extensions/<id>/references/...`, `.../scripts/...`). Với MỖI thư mục hỗ trợ
      tìm được, `build-zip.sh` phải copy nó **bằng cách nào đó** — `cp -R`, hoặc `find -exec cp`
      (thường dùng khi cần loại `.venv`/`__pycache__`). Đừng chỉ grep `cp -R`: một dir copy qua
      `find` vẫn hợp lệ. Cách kiểm chắc nhất: build zip rồi `unzip -l` xem dir có trong đó không.
      Manifest `provides` **không** gate cái gì được bundle → thiếu copy = command gãy sau cài,
      build không báo lỗi. Sau cài, assert dir có mặt và đủ số file.
- [ ] `hooks.before_*` / `hooks.after_*` trỏ tới command **tồn tại** (của chính extension này
      hoặc extension khác đã khai phụ thuộc).
- [ ] `requires.speckit_version` hợp lý (vd cần AskUserQuestion → bump min version).
- [ ] `version` bump trước khi tag; tag release phải **khớp** version manifest (workflow fail
      nếu lệch).
- [ ] Frontmatter mỗi command có `description`.
- [ ] Script (`scripts/*.py`, `*.sh`) tham chiếu trong command có tồn tại + có quyền chạy;
      script tự-bootstrap venv thì ghi rõ cần mạng lần đầu.
- [ ] Đánh số bước liền mạch; tham chiếu chéo trỏ đúng.
- [ ] Thuật ngữ nhất quán giữa command ↔ README ↔ `extension.yml`.

## Trục phán đoán (critic)

### Hook design
- [ ] `optional: true` vs `false` đặt đúng ý chưa? `false` = core ép MUST-execute, không cho
      người dùng từ chối — dùng cho việc thật sự bắt buộc thôi.
- [ ] Hook có **side-effect không hoàn tác** (tạo branch, ghi file, đổi trạng thái) không? Nếu
      lệnh chính bỏ ngang giữa chừng, trạng thái để lại có bẩn không? Có nói rollback/recovery?
- [ ] Hook có `condition` không? Nhớ: core KHÔNG tự eval condition — để HookExecutor lo. Đừng
      viết command giả định condition đã được eval.
- [ ] Hook chạy trước/sau đúng chỗ chưa (trước khi lệnh chính tạo artifact hay sau)?

### An toàn
- [ ] Hook command / script có nhận input người dùng chưa lọc rồi đưa vào shell không?
- [ ] Script có `eval`/`exec` trên nội dung untrusted không?
- [ ] Không hardcode secret/token; không log thông tin nhạy cảm.

### Escape-hatch (dùng escape-hatch-catalog.md)
- [ ] Command có gate/quy tắc "bắt buộc" nào không? Đi qua 10 mẫu đường thoát, tìm chỗ model
      lách được (N/A khống, ✅ giả, danh sách tự-bịa, tự tuyên bố xác nhận...).

### Sonnet-followability
- [ ] Ambiguity 2-cách-hiểu? Chỉ thị chọi nhau?
- [ ] Chỗ suy luận nặng có ví dụ cụ thể không?
- [ ] Output format cố định có được nêu rõ (template) hay để model tự chế?

### Generic vs specific
- [ ] Giả định cứng nào về cấu trúc dự án? Chạy trên dự án khác được không? Có fallback?

### Chi phí người trả lời & độ bền vận hành (BA lens)
- [ ] Command có hỏi người dùng nhiều lượt / chạy flow dài không? Áp nguyên section cùng tên
      trong `preset-checklist.md`: worst-case số lượt hỏi + gom câu, phân tầng trọng yếu,
      recommended-bias, persist trạng thái ra file, nơi bàn giao vật lý giữa các lệnh,
      side-effect trước xác nhận, nhánh cho ngoại lệ khuôn.

### Best-practices / bloat
- [ ] SKILL/command quá dài, over-specify, nhắc lặp? Gộp lại được không?
- [ ] Có cách nào **verify** extension chạy đúng sau cài (smoke test) không? Nếu không, đề xuất.
- [ ] Degrees of freedom: mơ hồ cố ý hay vô tình?
