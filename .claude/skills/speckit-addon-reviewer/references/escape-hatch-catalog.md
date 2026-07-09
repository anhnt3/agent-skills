# Escape-hatch catalog — lens trung tâm của review prompt

Prompt AI-automation không hỏng vì "viết dở" mà vì có **đường thoát**: chỗ model lười/nhanh
lách qua để "xong sớm" mà vẫn trông như tuân thủ. Review không phải đọc xuôi xem tác giả nói
gì — mà **đối kháng**: với mỗi quy tắc/gate, dựng kịch bản model né nó. Đây là lỗi giá trị
cao nhất vì tác giả (viết theo hướng "sẽ chạy đúng") gần như không tự thấy.

Cách dùng: đi qua từng gate/quy tắc "bắt buộc" trong addon, thử từng mẫu dưới. Mẫu nào áp
được mà prompt chưa bịt = finding (thường MAJOR: bỏ sót âm thầm).

## Các mẫu đường thoát

### 1. Gate đếm trạng thái nhưng không đếm tính đầy đủ
Gate kiểu "khi bảng hết dòng ⏳ thì qua". Model liệt kê thiếu ngay từ đầu (7/11 mục) → mọi
dòng thành ✅ → gate PASS → 4 mục mất không dấu vết. **Bịt**: chốt số N đếm-được từ nguồn
ngoài (đếm nguyên tắc trong file constitution, đếm màn từ router), gate đối chiếu số-dòng ≥ N.
Không có mỏ neo đếm từ nguồn = gate tự-xác-nhận, vô dụng.

### 2. N/A khống / N/A né
"Nhánh không áp dụng → N/A". Model xả N/A hàng loạt cho xong. **Bịt**: N/A phải kèm lý do
kiểm-chứng-được gắn feature cụ thể; cấm N/A trống, chung chung, hoặc "N/A vì đã làm ở chỗ
khác".

### 3. ✅ giả (đánh dấu xong mà chưa làm)
Model tự đánh "đã chốt" cho nhánh chưa thực sự hỏi/tra. **Bịt**: điều kiện đánh ✅ = có bằng
chứng (≥1 câu hỏi có phản hồi, hoặc fact tra cứu ghi rõ nguồn).

### 4. Tự tuyên bố người dùng đã xác nhận
Gate "chờ người dùng xác nhận" nhưng model (nhất là chạy tự động) tự suy "chắc đồng ý rồi"
và đi tiếp. **Bịt**: yêu cầu tin nhắn xác nhận tường minh, cấm suy diễn.

### 5. Chồng lấn phạm vi hợp lệ hóa bỏ sót
Hai giai đoạn/mục có nhánh trùng tên → model mark nhánh sau "N/A vì đã hỏi ở giai đoạn trước",
và lý do này KIỂM CHỨNG ĐƯỢC nên gate không chặn. **Bịt**: nêu trục phân biệt rõ; nhánh đã
làm ở nơi khác dùng "✅ (đã làm tại X)" kèm rà phần còn thiếu, KHÔNG dùng N/A để bỏ.

### 6. Informed-guess nuốt quyết định người dùng
Prompt (hoặc core) khuyến khích "đoán hợp lý cho phần chưa rõ". Model đoán luôn cả thứ đáng
lẽ phải hỏi. **Bịt**: ranh giới fact-vs-quyết định có VÍ DỤ cụ thể; "không chắc thuộc loại
nào → coi là quyết định, hỏi".

### 7. Danh sách tự-bịa thay vì đọc nguồn
"Liệt kê các X" mà không chỉ nguồn → model bịa từ trí nhớ, thiếu/thừa. **Bịt**: buộc liệt kê
từ nguồn cụ thể (file/router/menu/roadmap), không từ trí nhớ.

### 8. Chỉ thị mạnh ở xa thua chỉ thị mạnh ở gần
Preset đè luật core bằng câu chung ở đầu, nhưng core "MUST" nằm gần điểm hành động phía dưới.
Model theo cái gần. **Bịt**: neo lời đè vào đúng tên section core, nhắc "kể cả khi core ghi
MUST/EXECUTE vẫn không theo".

### 9. Vòng lặp không khép (phình) hoặc gate không đọc trạng thái mới nhất
Cơ chế "sổ sống, thêm nhánh khi phát sinh" nhưng gate đọc bản chụp đầu → nhánh mới bị bỏ;
hoặc không giới hạn nguồn phát sinh → phình vô hạn. **Bịt**: gate luôn đọc trạng thái hiện
tại; chỉ nhận phát sinh thuộc phạm vi, phần ngoài → ghi nợ chỗ khác.

### 10. "Trivial/nếu áp dụng" làm cửa bỏ hàng loạt
Điều kiện "trừ trivial", "nếu có" bị model dùng để loại phần lớn công việc. **Bịt**: định
nghĩa trivial hẹp lại, hoặc buộc nêu lý do khi loại.

## Câu hỏi rà nhanh cho mỗi gate

1. Gate kiểm được **tính đầy đủ** hay chỉ kiểm **trạng thái** các dòng đang có?
2. Có mỏ neo đếm/danh sách từ **nguồn ngoài** model không?
3. Mọi cửa "bỏ qua" (N/A, trivial, nếu-áp-dụng, đã-làm-chỗ-khác) có buộc **lý do kiểm chứng**?
4. Có chỉ thị nào của core/khác **chọi** lời này ở vị trí gần điểm hành động hơn không?
5. Model chạy **tự động** (không người dùng thật) có tự vượt gate "chờ xác nhận" được không?
