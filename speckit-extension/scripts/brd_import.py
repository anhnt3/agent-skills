#!/usr/bin/env python3
"""brd-import — bẻ file BRD .docx thành cây markdown.

    probe <docx> --work <dir>                    dò cấu trúc, thống kê cấp
    split --work <dir> --depth N --dest <dir>    cắt cây + kiểm chứng
"""

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from brd.convert import ConvertError, build_reference_docx, check_pandoc, run_pandoc
from brd.docx_probe import detect_tier
from brd.outline import depth_map, level_stats, parse_headings, recommend_depth
from brd.splitter import DepthError, SplitError, _breadcrumbs, plan_nodes, write_tree
from brd.verify import VerifyError, check_roundtrip, secondary_checks


def _die(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_probe(args):
    docx = Path(args.docx)
    if docx.suffix.lower() != ".docx":
        _die(f"Chỉ nhận file .docx, nhận được: {docx.name}")
    if not docx.is_file():
        _die(f"Không thấy file: {docx}")
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)

    tier = detect_tier(docx)

    from brd.docx_probe import promotions_for

    outline = None
    if args.outline:
        outline = json.loads(Path(args.outline).read_text(encoding="utf-8"))

    if tier["needs_llm"] and outline is None:
        result = {
            "tier": 0, "note": tier["note"], "needs_llm": True,
            "recommend_depth": None, "levels": [], "warnings": [],
            "candidates": tier.get("candidates", []),
            "source": {"file": docx.name, "sha256": _sha256(docx),
                       "pandoc": check_pandoc(), "path": str(docx.resolve())},
        }
        (work / "probe.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return

    promos = promotions_for(docx, outline=outline)
    if tier["tier"] == 1 and not promos:
        md_path = run_pandoc(docx, work)
    else:
        lua = Path(__file__).resolve().parent / "promote_headings.lua"
        md_path = run_pandoc(docx, work, lua_filter=lua,
                             metadata={"promotions": promos})
    effective_tier = 6 if outline is not None else tier["tier"]
    md = md_path.read_text(encoding="utf-8")
    headings = parse_headings(md)
    if not headings:
        _die("Markdown sau khi convert không có heading nào — không cắt được.")
    dmap = depth_map(headings)
    stats = level_stats(headings, md.split("\n"), dmap)

    result = {
        "tier": effective_tier,
        "note": tier["note"] if outline is None
                else "Ranh giới do LLM quyết từ ứng viên định dạng (in đậm/cỡ chữ)",
        "needs_llm": False,
        "recommend_depth": recommend_depth(stats), "levels": stats,
        "warnings": [], "candidates": [],
        "source": {"file": docx.name, "sha256": _sha256(docx),
                   "pandoc": check_pandoc(), "path": str(docx.resolve())},
    }
    (work / "probe.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


def _diff_trees(old, new):
    def snap(root):
        return {str(p.relative_to(root)).replace("\\", "/"): _sha256(p)
                for p in sorted(root.rglob("*")) if p.is_file()}
    a, b = snap(old), snap(new)
    return {
        "them": sorted(set(b) - set(a)),
        "mat": sorted(set(a) - set(b)),
        "doi": sorted(k for k in set(a) & set(b) if a[k] != b[k]),
    }


def cmd_split(args):
    work = Path(args.work)
    probe_file = work / "probe.json"
    if not probe_file.is_file():
        _die(f"Chưa có {probe_file} — chạy `probe` trước.")
    try:
        probe = json.loads(probe_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _die(f"{probe_file} hỏng, không đọc được JSON ({e}) — chạy lại `probe`.")
    if probe.get("needs_llm"):
        _die(
            f"{probe_file} là kết quả dò dở dang (needs_llm: true) — tài liệu không có "
            "Heading style, cần LLM quyết ranh giới. Hãy chạy lại `probe` với "
            "`--outline <file.json>` rồi mới `split`."
        )
    md_file = work / "brd.md"
    if not md_file.is_file():
        _die(f"Chưa có {md_file} — chạy lại `probe` để sinh markdown trung gian trước.")
    md = md_file.read_text(encoding="utf-8")
    md_lines = md.split("\n")

    headings = parse_headings(md)
    dmap = depth_map(headings)
    if args.depth not in set(dmap.values()):
        _die(f"Cấp cắt {args.depth} không tồn tại. Các cấp có thật: {sorted(set(dmap.values()))}")

    dest = Path(args.dest)
    diff = None
    final_dest = dest
    # Đích đã có bất cứ thứ gì (kể cả thư mục làm tay không manifest) -> chuyển sang
    # `.new`, tuyệt đối không xoá đè công của người dùng.
    if dest.is_dir() and any(dest.iterdir()):
        final_dest = dest.with_name(dest.name + ".new")
    replaced_new = final_dest != dest and final_dest.exists()

    staging = work / "staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    try:
        nodes = plan_nodes(headings, dmap, args.depth, len(md_lines))
        write_tree(nodes, md_lines, dmap, staging, {
            "source_file": probe["source"]["file"], "sha256": probe["source"]["sha256"],
            "imported_at": dt.date.today().isoformat(), "pandoc": probe["source"]["pandoc"],
            "cut_depth": args.depth, "tier": probe["tier"], "tier_note": probe["note"],
        })
        crumbs = _breadcrumbs(nodes)
        check_roundtrip(nodes, staging, dmap, crumbs, md)
    except DepthError as e:
        _die(
            f"Cấp cắt {args.depth} không dùng được — KHÔNG ghi gì ra {final_dest}.\n{e}\n"
            "Đây là lỗi chọn cấp cắt, không phải lỗi kiểm chứng: hãy chọn cấp cắt khác "
            "(thường là sâu hơn) rồi chạy lại."
        )
    except (SplitError, VerifyError) as e:
        _die(f"Kiểm chứng thất bại — KHÔNG ghi gì ra {final_dest}.\n{e}")

    media_src = work / "media" / "media"
    media_dst = staging / "media"
    if media_src.is_dir():
        shutil.copytree(media_src, media_dst)
    else:
        media_dst.mkdir()
    build_reference_docx(probe["source"]["path"], staging / "reference.docx")
    warnings = secondary_checks(
        nodes, staging, media_dst,
        sum(lv["count"] for lv in probe["levels"] if lv["depth"] <= args.depth),
    )

    if final_dest.exists() and not final_dest.is_dir():
        _die(f"{final_dest} đã tồn tại nhưng không phải thư mục — không ghi đè.")
    if final_dest.is_dir():
        shutil.rmtree(final_dest)
    final_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staging), str(final_dest))
    if final_dest != dest:
        diff = _diff_trees(dest, final_dest)

    report = {
        "dest": str(final_dest), "cut_depth": args.depth, "tier": probe["tier"],
        "files": sum(1 for _ in final_dest.rglob("*.md")),
        "folders": sum(1 for p in final_dest.rglob("*") if p.is_dir() and p.name != "media"),
        "roundtrip": "OK",
        "media": sum(1 for _ in (final_dest / "media").iterdir()),
        "warnings": warnings,
    }
    if diff is not None:
        report["diff"] = diff
    if replaced_new:
        report["replaced_previous_new"] = (
            f"{final_dest} của lần chạy trước đã bị thay thế (chưa hợp nhất vào {dest})"
        )
    print(json.dumps(report, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Bẻ file BRD .docx thành cây markdown.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe", help="Dò cấu trúc và thống kê cấp")
    p.add_argument("docx")
    p.add_argument("--work", required=True)
    p.add_argument("--outline", default=None,
                   help="JSON [{index, level}] do LLM quyết khi bậc 1-5 mù")
    p.set_defaults(func=cmd_probe)

    s = sub.add_parser("split", help="Cắt cây và kiểm chứng")
    s.add_argument("--work", required=True)
    s.add_argument("--depth", type=int, required=True)
    s.add_argument("--dest", required=True)
    s.set_defaults(func=cmd_split)

    args = parser.parse_args()
    try:
        args.func(args)
    except ConvertError as e:
        _die(str(e))


if __name__ == "__main__":
    main()
