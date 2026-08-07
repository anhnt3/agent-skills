"""Phân tích cây heading trong file markdown trung gian do pandoc sinh."""

import re
import statistics

HEADING_RE = re.compile(r"^(#{1,9})( +\S.*)$")


def iter_code_aware(lines):
    """Duyệt từng dòng, trả (chỉ_số, dòng, trong_khối_code).

    Nguồn duy nhất quyết định dòng nào nằm trong khối code có rào (``` hoặc ~~~).
    Dòng mở/đóng rào cũng tính là trong khối code. Cả ba nơi đụng tới heading
    (parse_headings, splitter._normalize_headings, verify._denormalize) PHẢI
    dùng chung hàm này để không bao giờ lệch nhau.

    CỐ Ý không nhận diện khối HTML thô (`<table>` do `-t gfm` sinh). Hệ quả nếu
    một dòng `#` lọt vào trong `<table>` thì KHÔNG phải chỉ "thừa một node" —
    ghép ngược vẫn khớp byte-for-byte, nhưng có hai hậu quả thật, rộng hơn nhiều:

    1. Heading giả đi vào `parse_headings` -> `depth_map`. Nếu số dấu `#` của nó
       là một cấp Word chưa từng có, MỌI độ sâu dưới nó bị đẩy đi một bậc, làm
       lệch `level_stats` và `recommend_depth` — tức lệch cấp cắt đề xuất cho
       người dùng. Ảnh hưởng toàn tài liệu, không phải một node.
    2. Nếu nó rơi vào độ sâu <= cấp cắt, `plan_nodes` mở segment ngay tại đó và
       **cắt đôi một `<table>` sang hai file**. Byte vẫn ghép ngược khớp, nhưng
       cả hai file dựng ra HTML hỏng — đúng thứ mà việc chuyển sang gfm muốn
       tránh, và làm hỏng luôn đường xuất markdown -> html -> docx sau này.

    Vẫn chọn KHÔNG đoán khối HTML ở đây: ranh giới khối HTML trong markdown là
    heuristic mập mờ (thẻ lồng nhau, dòng trắng, HTML nội dòng), đoán sai sẽ làm
    lệch chính số heading — hỏng đúng cái đang muốn bảo vệ, và im lặng. Đánh đổi
    đã chọn là **phát hiện thay vì né**: `verify.secondary_checks` quét riêng và
    cảnh báo khi thấy dòng heading nằm giữa `<table>` và `</table>`, để người
    dùng biết mà xử lý. Phần quét đó KHÔNG đụng vào việc phân tích heading hay
    số đếm heading. Đo trên BRD thật: không có dòng `#` nào nằm trong `<table>`.
    """
    fence = None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                yield i, line, True
                continue
            yield i, line, False
        else:
            if stripped.startswith(fence):
                fence = None
            yield i, line, True


def parse_headings(md):
    """[{line, level, title}] theo thứ tự xuất hiện. Bỏ qua nội dung trong khối code."""
    out = []
    for i, line, in_code in iter_code_aware(md.split("\n")):
        if in_code:
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append({"line": i, "level": len(m.group(1)), "title": m.group(2).strip()})
    return out


def depth_map(headings):
    """Cấp Word thưa (vd 1,3,4,5,6,8) -> độ sâu liên tục 1..n."""
    levels = sorted({h["level"] for h in headings})
    return {lv: i + 1 for i, lv in enumerate(levels)}


def segment_ends(headings, total_lines):
    """Dòng kết thúc (loại trừ) của segment mỗi heading."""
    ends = []
    for k, h in enumerate(headings):
        end = total_lines
        for nxt in headings[k + 1:]:
            if nxt["level"] <= h["level"]:
                end = nxt["line"]
                break
        ends.append(end)
    return ends


def level_stats(headings, md_lines, dmap):
    """Thống kê kích thước segment theo từng độ sâu, tăng dần."""
    ends = segment_ends(headings, len(md_lines))
    buckets = {}
    for h, end in zip(headings, ends):
        size = sum(len(x) + 1 for x in md_lines[h["line"]:end])
        buckets.setdefault(dmap[h["level"]], {"word_level": h["level"], "sizes": []})
        buckets[dmap[h["level"]]]["sizes"].append(size)
    stats = []
    for depth in sorted(buckets):
        sizes = buckets[depth]["sizes"]
        stats.append({
            "depth": depth,
            "word_level": buckets[depth]["word_level"],
            "count": len(sizes),
            "median": int(statistics.median(sizes)),
            "min": min(sizes),
            "max": max(sizes),
        })
    return stats


def recommend_depth(stats, min_median=3000):
    """Cấp SÂU NHẤT còn có trung vị >= nguong.

    Luật KHÔNG đơn điệu: ở BRD Mobifone cấp 4 có trung vị 305 (trượt) nhưng
    cấp 5 có 23.808 (đạt). Phải duyệt HẾT rồi lấy max — dừng sớm ở cấp trượt
    đầu tiên sẽ chọn nhầm cấp 3.
    """
    ok = [s["depth"] for s in stats if s["median"] >= min_median]
    return max(ok) if ok else 1
