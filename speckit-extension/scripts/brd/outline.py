"""Phân tích cây heading trong file markdown trung gian do pandoc sinh."""

import re
import statistics

HEADING_RE = re.compile(r"^(#{1,9}) +(\S.*?)\s*$")


def parse_headings(md):
    """[{line, level, title}] theo thứ tự xuất hiện. Bỏ qua nội dung trong khối code."""
    out = []
    fence = None
    for i, line in enumerate(md.split("\n")):
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                continue
        else:
            if stripped.startswith(fence):
                fence = None
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append({"line": i, "level": len(m.group(1)), "title": m.group(2)})
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
