#!/usr/bin/env python3
"""Cây danh mục chức năng: dựng từ lưới ô, cấp ID đa cấp, so khác biệt.

Thuần logic — không đọc/ghi file, không in ra stdout. `fnlist_import.py` lo
phần I/O và CLI. Tách ra vì đây là phần dễ sai âm thầm nhất (dựng cây từ bảng
phẳng, cấp ID ổn định) và cần test được độc lập với Excel.
"""
from __future__ import annotations

import re

STATUSES = ("pending", "intel", "srs")
ID_RE = re.compile(r"^FN(?:-\d{2})+$")


def walk(nodes, parents=()):
    """Duyệt pre-order — đúng thứ tự dòng của file nguồn. Trả (node, tuple cha).

    Đi qua cả `children` (node cây FN) lẫn `use_cases` (mục use-case con của
    một node lá) — use-case item không có khoá `children`/`use_cases` của
    riêng nó nên đệ quy tự dừng, không cần điều kiện chặn riêng."""
    for node in nodes:
        yield node, parents
        yield from walk(node.get("children") or [], parents + (node,))
        yield from walk(node.get("use_cases") or [], parents + (node,))


def is_use_case(node):
    """True nếu node là một mục use-case con (không phải node cây FN).

    Phân biệt bằng sự VẮNG MẶT của khoá `children` — mọi node cây FN đều có
    khoá này (kể cả khi rỗng `[]`), còn use-case item thì không bao giờ có."""
    return "children" not in node


def name_path(node, parents):
    """Đường dẫn tên từ gốc xuống. Đây là khoá khớp cũ↔mới khi cấp lại ID —
    dùng tên đơn thì hai chức năng cùng tên ở hai nhóm sẽ tranh ID nhau."""
    return tuple(p["name"] for p in parents) + (node["name"],)


def find_by_id(nodes, fid):
    for node, _ in walk(nodes):
        if node.get("id") == fid:
            return node
    return None


def clean_node(node):
    """Node nội bộ → node đúng schema: chỉ 5 trường, bỏ status mặc định.

    Node lúc dựng cây có mang thêm `row` (số dòng nguồn) để báo cáo; trường đó
    không thuộc schema nên phải rơi lại ở đây, không lọt vào file."""
    out = {
        "id": node["id"],
        "name": node["name"],
        "description": node.get("description", ""),
    }
    status = node.get("status")
    if status and status != "pending":
        out["status"] = status
    out["children"] = [clean_node(c) for c in node.get("children") or []]
    return out


def build_document(tree, system, source_file, sheet, updated, retired):
    return {
        "schema_version": 1,
        "system": system,
        "source": {"file": source_file, "sheet": sheet},
        "updated": updated,
        "retired_ids": sorted(retired),
        "functions": [clean_node(n) for n in tree],
    }


OUTLINE_RE = re.compile(r"^\d+(?:\.\d+)*\.?$")


def _column_cells(grid, col, first_data_row):
    return [(row[col] if col < len(row) else "") for row in grid[first_data_row:]]


def detect_hierarchy(grid, first_data_row):
    """Chấm điểm cả ba kiểu phân cấp, trả ứng viên giảm dần theo score.

    Hàm này KHÔNG quyết thay người dùng — điểm số và bằng chứng chỉ để LLM
    trình ra hỏi. Trả rỗng nghĩa là không thấy dấu hiệu phân cấp nào (danh sách
    phẳng một cấp), cũng vẫn phải hỏi chứ không mặc nhiên coi là phẳng."""
    ncols = max((len(r) for r in grid), default=0)
    total_rows = len(grid) - first_data_row
    out = []
    for col in range(ncols):
        cells = [c for c in _column_cells(grid, col, first_data_row) if c]
        if not cells:
            continue
        codes = [c for c in cells if OUTLINE_RE.match(c)]
        depth = max((c.rstrip(".").count(".") + 1 for c in codes), default=0)
        if len(codes) / len(cells) >= 0.8 and depth >= 2:
            out.append({
                "mode": "outline", "column": col,
                "score": round(len(codes) / len(cells), 2),
                "evidence": (f"cột {col}: {len(codes)}/{len(cells)} ô dạng số mục lục "
                             f"(1.2.3), sâu nhất {depth} cấp"),
            })
        nums = [c for c in cells if c.isdigit() and 1 <= int(c) <= 4]
        distinct = sorted({int(c) for c in nums})
        # `len(nums) > len(distinct)` loại cột STT thuần: 1,2,3 không lặp lại
        # giá trị nào, còn cột cấp thật thì cấp 1 phải xuất hiện nhiều lần.
        if (len(nums) == len(cells) and len(distinct) >= 2 and distinct[0] == 1
                and len(nums) > len(distinct)):
            # Score theo tỉ lệ dòng khớp/tổng số dòng, không hằng số cố định —
            # cột cấp chỉ điền vài dòng (còn lại trống) là bằng chứng yếu hơn
            # cột điền kín mọi dòng, nên phải điểm thấp hơn để so được với
            # outline/columns thay vì luôn đứng ngang 0.95.
            score = round(min(1.0, len(cells) / total_rows), 2) if total_rows else 0.0
            out.append({
                "mode": "level", "column": col, "score": score,
                "evidence": (f"cột {col}: mọi ô là số 1..4, có {len(distinct)} cấp "
                             f"khác nhau {distinct}"),
            })
    out.extend(_detect_column_runs(grid, first_data_row, ncols))
    return sorted(out, key=lambda c: -c["score"])


def _has_grouping(rows, cols):
    """Kiểu 'repeated' đòi cột cha thật sự gom nhóm — giá trị phải lặp lại ở
    nhiều dòng. Không có luật này thì một danh sách phẳng hai cột
    (Tên chức năng | Mô tả) trông y hệt kiểu repeated, vì dòng nào cũng điền đủ
    cả hai cột."""
    for col in cols[:-1]:
        values = [(r[col] if col < len(r) else "") for r in rows]
        if len(set(values)) >= len(values):
            return False
    return True


def _detect_column_runs(grid, first_data_row, ncols):
    """Kiểu 'mỗi cấp một cột'. Hai style khác nhau về cách dựng cây:

      staircase — mỗi dòng chỉ điền ĐÚNG MỘT cột cấp (kiểu bậc thang)
      repeated  — mỗi dòng điền ĐỦ mọi cột cấp (tên cha lặp lại từng dòng)

    Chỉ xét các dải cột chữ liền nhau, dài ≥2. Cột mô tả cũng là cột chữ nên có
    thể lọt vào dải — nhiễu có thể nằm ở ĐẦU, GIỮA hay CUỐI dải (không chỉ
    cuối), nên vòng lặp phải thử mọi cửa sổ con liên tiếp trong dải (không chỉ
    tiền tố `run[:size]`), ưu tiên cửa sổ dài nhất khớp thuần một style trước.
    Ví dụ [Mô tả, Nhóm, Chức năng] (nhiễu ở đầu) phải rụng xuống còn
    [Nhóm, Chức năng] chứ không được bỏ sót toàn bộ dải."""
    total_rows = len(grid) - first_data_row
    rows = [r for r in grid[first_data_row:] if any(r)]
    text_cols = []
    for col in range(ncols):
        cells = [c for c in _column_cells(grid, col, first_data_row) if c]
        if cells and not all(OUTLINE_RE.match(c) or c.isdigit() for c in cells):
            text_cols.append(col)

    runs, cur = [], []
    for col in text_cols:
        if cur and col == cur[-1] + 1:
            cur.append(col)
        else:
            if len(cur) >= 2:
                runs.append(cur)
            cur = [col]
    if len(cur) >= 2:
        runs.append(cur)

    out = []
    for run in runs:
        found = False
        for size in range(len(run), 1, -1):
            for start in range(0, len(run) - size + 1):
                cols = run[start:start + size]
                filled = [sum(1 for c in cols if c < len(r) and r[c]) for r in rows]
                if not filled:
                    continue
                if all(f == 1 for f in filled):
                    style = "staircase"
                elif all(f == len(cols) for f in filled) and _has_grouping(rows, cols):
                    style = "repeated"
                else:
                    continue
                # Score theo tỉ lệ dòng khớp/tổng số dòng, không hằng số cố
                # định — khớp trên vài dòng (còn lại là dòng trống/khác biệt)
                # là bằng chứng yếu hơn khớp trên toàn bộ dữ liệu.
                score = round(min(1.0, len(rows) / total_rows), 2) if total_rows else 0.0
                out.append({
                    "mode": "columns", "level_columns": cols, "style": style,
                    "score": score,
                    "evidence": (f"cột {cols}: mọi dòng điền "
                                 f"{'đúng một' if style == 'staircase' else 'đủ'} cột cấp"),
                })
                found = True
                break
            if found:
                break
    return out


def _cell(raw, idx):
    if idx is None or idx >= len(raw):
        return ""
    return raw[idx]


def _level_and_name(raw, mapping, rowno=None):
    """Một dòng → (cấp, tên). Cấp None nghĩa là không đọc được cấp của dòng."""
    h = mapping.get("hierarchy") or {}
    cols = mapping.get("columns") or {}
    mode = h.get("mode")
    if mode == "columns":
        filled = [(level, col) for level, col in
                  enumerate(h["level_columns"], start=1) if _cell(raw, col)]
        if h.get("style") == "staircase" and len(filled) > 1:
            cols_filled = [col for _, col in filled]
            raise ValueError(
                f"Dòng {rowno}: nhiều hơn một cột cấp có giá trị "
                f"(cột {cols_filled}). Kiểu 'staircase' đòi mỗi dòng chỉ điền "
                "một cột — có thể file này thật ra là kiểu 'repeated'.")
        if not filled:
            return (None, "")
        level, col = filled[-1]
        return (level, _cell(raw, col))
    name = _cell(raw, cols.get("name"))
    if mode == "outline":
        code = _cell(raw, h["column"]).rstrip(".")
        if code and OUTLINE_RE.match(code):
            return (code.count(".") + 1), name
        return (None, name)
    if mode == "level":
        value = _cell(raw, h["column"])
        return (int(value) if value.isdigit() else None), name
    return 1, name      # không khai hierarchy → danh sách phẳng một cấp


def build_tree(grid, mapping):
    """Lưới ô → (cây, dòng bị bỏ). Chưa cấp ID ở bước này.

    Dòng bị bỏ KHÔNG biến mất im lặng — mọi dòng bỏ đều vào `skipped` kèm lý do
    để LLM báo lại cho người dùng."""
    h = mapping.get("hierarchy") or {}
    if h.get("mode") == "columns" and h.get("style") == "repeated":
        return _build_repeated(grid, mapping)
    return _build_leveled(grid, mapping)


def _iter_data_rows(grid, mapping, skipped):
    """Sinh (rowno 1-based, raw) cho các dòng dữ liệu thật, đẩy dòng người dùng
    khai bỏ sang `skipped`."""
    first = int(mapping.get("first_data_row", 1))
    skip = {int(x) for x in mapping.get("skip_rows", [])}
    for i, raw in enumerate(grid):
        if i < first:
            continue
        rowno = i + 1      # 1-based, khớp số dòng người dùng thấy trong Excel
        if rowno in skip:
            skipped.append({"row": rowno, "reason": "người dùng khai bỏ",
                            "raw": raw[:6]})
            continue
        yield rowno, raw


UC_EXTRA_FIELDS = ("importance", "type", "usage_timing")


def _use_case_extra(raw, mapping):
    """Các trường bổ sung (Mức quan trọng/Loại UC/Thời điểm sử dụng) cho một
    dòng use-case — chỉ ghi khi mapping có khai cột VÀ ô đó có giá trị."""
    cols = mapping.get("columns") or {}
    out = {}
    for key in UC_EXTRA_FIELDS:
        col = cols.get(key)
        if col is None:
            continue
        val = _cell(raw, col)
        if val:
            out[key] = val
    return out


def _build_leveled(grid, mapping):
    desc_col = (mapping.get("columns") or {}).get("description")
    h = mapping.get("hierarchy") or {}
    unmatched = h.get("unmatched_rows", "error")
    roots, skipped, stack = [], [], []
    for rowno, raw in _iter_data_rows(grid, mapping, skipped):
        level, name = _level_and_name(raw, mapping, rowno)
        if not name:
            skipped.append({"row": rowno, "reason": "ô tên chức năng trống",
                            "raw": raw[:6]})
            continue
        if level is None:
            if unmatched == "absorb":
                if not stack:
                    raise ValueError(
                        f"Dòng {rowno} ('{name}'): không có nhóm cha nào đang "
                        "mở để gắn làm use-case con — kiểm lại dòng đầu file "
                        "nguồn hoặc mapping.")
                stack[-1].setdefault("use_cases", []).append({
                    "name": name, "description": _cell(raw, desc_col),
                    "row": rowno, **_use_case_extra(raw, mapping),
                })
                continue
            raise ValueError(
                f"Dòng {rowno} ('{name}'): không đọc được cấp của dòng — "
                "kiểm lại khối hierarchy trong mapping.")
        if level > len(stack) + 1:
            raise ValueError(
                f"Dòng {rowno} ('{name}'): nhảy từ cấp {len(stack)} xuống cấp "
                f"{level}. Cấp bậc trong file nguồn không liên tục — sửa file "
                "nguồn hoặc chọn lại kiểu phân cấp.")
        node = {"name": name, "description": _cell(raw, desc_col),
                "children": [], "row": rowno}
        del stack[level - 1:]
        (stack[-1]["children"] if stack else roots).append(node)
        stack.append(node)
    return roots, skipped


def _build_repeated(grid, mapping):
    """Kiểu tên cha lặp lại trên mọi dòng: mỗi dòng là một lá, tổ tiên suy từ
    tiền tố giá trị các cột cấp. Hai dòng cùng tiền tố dùng lại đúng node cha đó,
    không tạo node cha thứ hai trùng tên."""
    level_cols = mapping["hierarchy"]["level_columns"]
    desc_col = (mapping.get("columns") or {}).get("description")
    roots, skipped, index = [], [], {}
    for rowno, raw in _iter_data_rows(grid, mapping, skipped):
        values = [_cell(raw, c) for c in level_cols]
        if not values[-1]:
            skipped.append({"row": rowno, "reason": "ô tên chức năng trống",
                            "raw": raw[:6]})
            continue
        for depth, value in enumerate(values[:-1], start=1):
            if not value:
                raise ValueError(
                    f"Dòng {rowno}: cột cấp {depth} trống trong khi cấp sâu hơn "
                    "có giá trị. Kiểu 'repeated' đòi mọi cột cấp đều điền — "
                    "có thể file này thật ra là kiểu 'staircase'.")
        siblings = roots
        node = None
        for depth in range(len(values)):
            key = tuple(values[:depth + 1])
            node = index.get(key)
            if node is None:
                node = {"name": values[depth], "description": "",
                        "children": [], "row": rowno}
                index[key] = node
                siblings.append(node)
            siblings = node["children"]
        node["description"] = _cell(raw, desc_col)
    return roots, skipped


def assign_ids(tree, old_tree=None, retired=()):
    """Cấp ID đa cấp, sửa tại chỗ.

    Bốn luật, theo đúng thứ tự ưu tiên:
      1. Node đã có ở bản cũ (khớp theo ĐƯỜNG DẪN TÊN) giữ nguyên ID.
      2. Node mới lấy số nhỏ nhất chưa dùng trong cùng cha.
      3. Số đã khai tử không bao giờ cấp lại — hai tài liệu ở hai thời điểm
         không được trỏ cùng một ID ra hai chức năng khác nhau.
      4. Node đổi cha thì đường dẫn tên đổi theo, nên tự động rơi vào luật 2 và
         nhận ID mới — đây là điểm gãy truy vết duy nhất, `diff_trees` gắn nhãn
         'chuyển nhóm' để người dùng biết mà cập nhật tài liệu cũ.

    Hai node MỚI trùng tên dưới cùng cha: chỉ node gặp trước trong duyệt được
    khớp/tiêu thụ ID cũ theo đường dẫn tên; node trùng tên còn lại rơi vào luật
    2 và nhận số mới — tránh hai chức năng khác nhau đâm chung một ID.
    """
    old_by_path = {}
    for node, parents in walk(old_tree or []):
        old_by_path[name_path(node, parents)] = node
    retired = set(retired)
    # ID nào từng xuất hiện ở cây cũ, dù chưa từng bị khai tử ở lần import
    # trước — số đó có thể vừa chết NGAY TRONG lần chạy này (node bị xoá hoặc
    # chuyển nhóm), vì compute_retired chạy SAU assign_ids. Cấm cấp lại luôn,
    # không đợi retired_ids cập nhật, để tránh hai chức năng (một cũ vừa chết,
    # một mới) đâm chung một ID trong cùng một lần import.
    old_ids = {n["id"] for n, _ in walk(old_tree or []) if n.get("id")}

    def recurse(nodes, parents, prefix):
        used = set()
        for node in nodes:
            key = name_path(node, parents)
            old = old_by_path.get(key)
            if old and old.get("id", "").rsplit("-", 1)[0] == prefix:
                node["id"] = old["id"]
                used.add(int(old["id"].rsplit("-", 1)[1]))
                # Tiêu thụ entry — hai node MỚI cùng tên dưới cùng cha không
                # được đâm chung một ID cũ, đứa trùng tên sau phải rơi vào
                # luật 2 (số nhỏ nhất chưa dùng) như node hoàn toàn mới.
                del old_by_path[key]
        seq = 1
        for node in nodes:
            if "id" not in node:
                while (seq in used or f"{prefix}-{seq:02d}" in retired
                       or f"{prefix}-{seq:02d}" in old_ids):
                    seq += 1
                node["id"] = f"{prefix}-{seq:02d}"
                used.add(seq)
            recurse(node["children"], parents + (node,), node["id"])

    recurse(tree, (), "FN")


def compute_retired(old_tree, new_tree, prev_retired=()):
    """ID biến mất khỏi cây mới bị khai tử vĩnh viễn. Gọi SAU assign_ids."""
    alive = {n["id"] for n, _ in walk(new_tree)}
    gone = {n["id"] for n, _ in walk(old_tree or [])} - alive
    return sorted(set(prev_retired) | gone)


def carry_status(new_tree, old_tree):
    """Chép tiến độ (`status`) từ bản cũ sang theo ID. Gọi SAU assign_ids —
    không chép thì mỗi lần import lại xoá sạch tiến độ code-intel đã ghi."""
    old = {n["id"]: n.get("status") for n, _ in walk(old_tree or [])}
    for node, _ in walk(new_tree):
        status = old.get(node["id"])
        if status and status != "pending":
            node["status"] = status


def diff_trees(old_tree, new_tree):
    """So hai cây theo đường dẫn tên. Gọi SAU assign_ids trên cả hai cây.

    Chỉ so node lá (không có con) — đó mới là "chức năng" thật; node nhóm chỉ
    là tiêu đề tổ chức, nhóm biến mất/xuất hiện do các lá bên trong đổi chỗ
    không phải là một thay đổi chức năng độc lập cần báo cáo.

    Một node đổi trạng thái lá giữa hai lần import (từ có con → hết con, hoặc
    ngược lại) không phải là "bỏ"/"thêm" thật — node đó vẫn tồn tại, chỉ đổi
    vai trò. Vì vậy trước khi báo "bỏ"/"thêm" phải kiểm đường dẫn đó có mặt ở
    TOÀN BỘ cây bên kia không (kể cả node không phải lá), có thì bỏ qua."""
    old_leaf = {name_path(n, p): n for n, p in walk(old_tree or []) if not n.get("children")}
    new_leaf = {name_path(n, p): n for n, p in walk(new_tree) if not n.get("children")}
    old_all_paths = {name_path(n, p) for n, p in walk(old_tree or [])}
    new_all_paths = {name_path(n, p) for n, p in walk(new_tree)}
    out = []
    for path, node in new_leaf.items():
        old = old_leaf.get(path)
        if old is None:
            if path not in old_all_paths:
                out.append({"loai": "thêm", "id": node["id"], "ten": path[-1],
                            "duong_dan": " / ".join(path), "_node": node})
        elif (old.get("description") or "") != (node.get("description") or ""):
            out.append({"loai": "đổi mô tả", "id": node["id"], "ten": path[-1],
                        "cu": old.get("description", ""),
                        "moi": node.get("description", "")})
    for path, old in old_leaf.items():
        if path not in new_leaf and path not in new_all_paths:
            out.append({"loai": "bỏ", "id": old["id"], "ten": path[-1],
                        "duong_dan": " / ".join(path), "_node": old})
    return _merge_moves(out)


def _merge_moves(entries):
    """Một 'bỏ' và một 'thêm' cùng tên lá → gần như chắc chắn là chuyển nhóm,
    ID đã đổi. Gộp thành một dòng để người dùng biết mà cập nhật tài liệu trỏ ID
    cũ. Chỉ gộp khi tên đó xuất hiện ĐÚNG MỘT lần ở mỗi bên — nhiều hơn thì
    không đủ căn cứ ghép cặp, trình nguyên trạng còn hơn đoán sai.

    Chuyển nhóm có thể đi kèm đổi mô tả cùng lúc — entry 'bỏ'/'thêm' rời rạc
    không mang mô tả nên phải tra lại node gốc (giữ ở khoá nội bộ `_node`) để
    biết có đổi mô tả không; có thì thêm `cu`/`moi` vào entry gộp, không thì
    giữ nguyên 6 khoá cũ (không thêm khoá thừa)."""
    removed = [e for e in entries if e["loai"] == "bỏ"]
    added = [e for e in entries if e["loai"] == "thêm"]
    moved = {}
    for name in {e["ten"] for e in removed} & {e["ten"] for e in added}:
        pair_out = [e for e in removed if e["ten"] == name]
        pair_in = [e for e in added if e["ten"] == name]
        if len(pair_out) == 1 and len(pair_in) == 1:
            moved[name] = (pair_out[0], pair_in[0])
    out = [{k: v for k, v in e.items() if k != "_node"}
           for e in entries
           if not (e["loai"] in ("thêm", "bỏ") and e["ten"] in moved)]
    for name in sorted(moved):
        gone, came = moved[name]
        entry = {"loai": "chuyển nhóm", "ten": name,
                  "id_cu": gone["id"], "id_moi": came["id"],
                  "tu": gone["duong_dan"], "den": came["duong_dan"]}
        old_desc = (gone.get("_node") or {}).get("description") or ""
        new_desc = (came.get("_node") or {}).get("description") or ""
        if old_desc != new_desc:
            entry["cu"] = old_desc
            entry["moi"] = new_desc
        out.append(entry)
    return out


def subtree_leaves(node):
    """Mọi node lá thuộc nhánh của `node`, gồm cả CHÍNH NÓ nếu nó là lá. Dùng
    bởi code-intel để tính danh sách FN-ID một unit phải phủ, không đệ quy lại
    logic duyệt cây ở một chỗ khác."""
    children = node.get("children") or []
    if not children:
        return [node]
    out = []
    for c in children:
        out.extend(subtree_leaves(c))
    return out
