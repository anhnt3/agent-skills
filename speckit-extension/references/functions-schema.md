# `functions.json` — schema danh mục chức năng

Đây là **nguồn sự thật duy nhất** về danh mục chức năng của dự án. Không có bản
markdown song song; không ai sửa tay file này. `scripts/fnlist_import.py` là
chương trình duy nhất được phép ghi — mọi lệnh khác muốn đổi gì thì gọi
subcommand `update`.

Đường dẫn mặc định: `.specify/docs/functions.json`.

## Hình dạng

```json
{
  "schema_version": 1,
  "system": "Hệ thống DMS",
  "source": { "file": "FunctionList_DMS.xlsx", "sheet": "DanhMuc" },
  "updated": "2026-08-11",
  "retired_ids": ["FN-01-04"],
  "functions": [
    {
      "id": "FN-01",
      "name": "Quản lý đơn hàng",
      "description": "",
      "children": [
        {
          "id": "FN-01-01",
          "name": "Danh sách đơn",
          "description": "Xem, tìm kiếm đơn hàng",
          "status": "intel",
          "children": []
        },
        { "id": "FN-01-02", "name": "Tạo đơn mới", "description": "", "children": [] }
      ]
    },
    { "id": "FN-02", "name": "Quản lý khách hàng", "description": "", "children": [] }
  ]
}
```

## Trường ở mức tài liệu

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `schema_version` | int | Hiện là `1`. Đọc file có số khác thì dừng, đừng đoán. |
| `system` | string | Tên hệ thống, do người dùng xác nhận lúc import. |
| `source` | object | `file` (đường dẫn file nguồn) + `sheet` (tên sheet đã dùng). |
| `updated` | string | `YYYY-MM-DD`, ngày chạy lệnh import gần nhất. |
| `retired_ids` | array | ID của chức năng đã bị xoá. **Không bao giờ cấp lại**. |
| `functions` | array | Các node gốc, theo đúng thứ tự dòng của file nguồn. |

## Trường của một node

Đúng năm trường, không hơn.

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | string | Mã đa cấp, xem dưới. |
| `name` | string | Tên chức năng, **nguyên văn** ô nguồn. |
| `description` | string | Mô tả, **nguyên văn** ô nguồn. Không có thì `""`. |
| `status` | string | `intel` hoặc `srs`. **Vắng mặt = `pending`** — giá trị mặc định không được ghi ra file. |
| `children` | array | Node con; lá thì `[]`. |

`status` nghĩa là gì:

- vắng mặt / `pending` — chưa lệnh nào xử lý chức năng này
- `intel` — đã có mặt trong một `intel.md`
- `srs` — đã có mặt trong một `srs.md`

**Không có trường `cum`.** Muốn biết một FN thuộc cụm nào thì quét
`.specify/docs/*/intel.md` — chính file đó liệt kê FN-ID mà nó phủ. Lưu thêm ở
đây là tạo bản sao dễ lạc hậu hơn bản gốc.

**Không có trường `nguon_code`.** Danh sách `file:dòng` là nội dung của
`intel.md`.

**Không có `level`, `outline`, `parent`.** Cấp bậc đọc từ độ sâu lồng của
`children`; số mục lục kiểu `1.2.3` suy từ vị trí trong mảng.

**`diff` của lệnh `write` chỉ so sánh node lá (`children` rỗng).** Thay đổi tên/mô tả,
thêm, hoặc xoá một node có con (nhóm cấp cao) không hiện trong `diff` — chỉ các thay đổi
ở node lá mới được báo cáo.

## `use_cases` — use-case con trong node lá

Một node lá có thể gộp nhiều dòng nội dung (use-case, giao dịch cụ thể — không tự khai cấp
riêng trong file nguồn) thành mảng `use_cases`. **Vắng mặt** ở node không có dòng nội dung
nào; một node có thể vừa có `children` vừa có `use_cases`.

```json
{
  "id": "FN-01-01",
  "name": "Nhóm chức năng Quản trị hệ thống và Người dùng",
  "description": "",
  "children": [],
  "use_cases": [
    {
      "id": "FN-01-01-UC-01",
      "name": "Quản lý danh sách người dùng",
      "description": "1. Quản trị hệ thống thao tác tạo mới...",
      "importance": "",
      "type": "",
      "usage_timing": ""
    }
  ]
}
```

Trường của một mục `use_cases`:

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | string | `<id-node-cha>-UC-nn`, xem quy tắc ID bên dưới. |
| `name` | string | Tên use-case, nguyên văn ô nguồn. |
| `description` | string | Mô tả, nguyên văn ô nguồn. Không có thì `""`. |
| `status` | string | Giống `status` của node FN. Vắng mặt = `pending`. |
| `importance` | string | Mức quan trọng — chỉ ghi khi file nguồn có cột này. |
| `type` | string | Loại UC theo quy ước BA — chỉ ghi khi file nguồn có cột này. |
| `usage_timing` | string | Thời điểm sử dụng — chỉ ghi khi file nguồn có cột này. |

`importance`/`type`/`usage_timing` vắng mặt hoàn toàn (không ghi `""`) khi mapping không
khai cột tương ứng hoặc ô nguồn trống.

`diff` của lệnh `write` cũng so sánh `use_cases` — dưới nhãn riêng `use-case thêm`/
`use-case bỏ`/`use-case đổi mô tả`, tách khỏi diff cấp node FN.

## Quy tắc ID

Dạng `FN-01`, `FN-01-01`, `FN-01-01-01` — mỗi cấp hai chữ số, nối bằng `-`. Số
cấp bằng độ sâu trong cây (2 đến 4 cấp tuỳ dự án).

Số trong ID **không phản ánh thứ tự hiển thị**, và đó là chủ ý:

1. Lần import đầu: đánh số theo vị trí trong nhóm cha, từ `01`.
2. Import lại: node đã tồn tại (khớp theo **đường dẫn tên** — chuỗi `name` từ
   gốc xuống) giữ nguyên ID.
3. Node mới chèn vào giữa: lấy số kế tiếp chưa dùng trong nhóm cha, không dịch
   số của ai. Chèn giữa `FN-01-01` và `FN-01-02` thì thành `FN-01-03`.
4. Node bị xoá: ID vào `retired_ids`, không bao giờ cấp lại.
5. Node đổi nhóm cha: đường dẫn tên đổi → nhận ID mới. `diff` của lệnh `write`
   gắn nhãn `chuyển nhóm` kèm ID cũ → mới. **Đây là điểm gãy truy vết duy
   nhất** — tài liệu nào đang trỏ ID cũ phải sửa tay.

`use_cases` dùng LẠI đúng 5 luật trên, chỉ đổi phạm vi: đánh số/khớp lại theo **đường dẫn
tên trong phạm vi node cha** (không phải toàn cây), tiền tố ID là `<id-cha>-UC` thay vì
`FN`. Không dùng thẳng mã use-case trong file nguồn (nếu có, ví dụ `uc001`) làm `id` — mã
đó do người nhập tay, không đảm bảo ổn định giữa các lần sửa file nguồn.

## Đọc và ghi

```bash
# Đọc: chỉ cần json.load / jq, không có định dạng riêng nào.
# Ghi status (đường DUY NHẤT):
python .specify/extensions/dft-speckit/scripts/fnlist_import.py update \
  --file .specify/docs/functions.json \
  --set FN-01-01=intel --set FN-01-02=srs
```

Lệnh `update` kiểm toàn bộ trước khi ghi: một ID sai hoặc một `status` lạ là
dừng với mã thoát khác 0 và **không ghi gì**.
