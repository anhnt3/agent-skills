#!/usr/bin/env python3
"""brd-roadmap — trích outline từ cây BRD markdown và gác cổng docs/roadmap.md.

    outline <brd-dir> [--out <json>] [--head N]
    verify <roadmap.md> --brd <dir> [--decisions <json>]
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

NODE_RE = re.compile(r"^\s*-\s*\{(.*)\}\s*$")


def _die(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def _scan_flow(body):
    """Tách các cặp `k: v` của một flow mapping một dòng, tôn trọng chuỗi có escape.

    Không dùng được `split(",")`: `title` có thể chứa dấu phẩy và `\\"` bên trong.
    """
    out, i, n = {}, 0, len(body)
    while i < n:
        while i < n and body[i] in " ,":
            i += 1
        j = body.find(":", i)
        if j < 0:
            break
        key = body[i:j].strip()
        i = j + 1
        while i < n and body[i] == " ":
            i += 1
        if i < n and body[i] == '"':
            i += 1
            buf = []
            while i < n:
                c = body[i]
                if c == "\\" and i + 1 < n:
                    buf.append(body[i + 1])
                    i += 2
                    continue
                if c == '"':
                    i += 1
                    break
                buf.append(c)
                i += 1
            val = "".join(buf)
        else:
            k = i
            while i < n and body[i] != ",":
                i += 1
            val = body[k:i].strip()
        out[key] = val
    return out


def parse_manifest(path):
    """Đọc `brd.manifest.yml` -> danh sách node theo thứ tự tài liệu."""
    path = Path(path)
    if not path.is_file():
        _die(f"Không thấy {path} — thư mục này không phải cây BRD do brd-import sinh ra.")
    nodes = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = NODE_RE.match(line)
        if not m:
            continue
        f = _scan_flow(m.group(1))
        parent = f.get("parent")
        nodes.append({
            "id": f["id"],
            "order": int(f["order"]),
            "depth": int(f["depth"]),
            "kind": f["kind"],
            "title": f["title"],
            "path": f.get("path"),
            "dir": f.get("dir"),
            "inline": f.get("inline") == "true",
            "parent": None if parent in (None, "null", "") else parent,
            "chars": int(f["chars"]),
        })
    if not nodes:
        _die(f"{path} không có node nào — manifest hỏng hoặc rỗng.")
    return nodes


def node_loc(node):
    """Vị trí của node trong cây: đường dẫn file, hoặc thư mục nếu node inline."""
    return node["path"] or node["dir"] or ""


def breadcrumbs(nodes):
    by_id = {n["id"]: n for n in nodes}
    out = {}
    for n in nodes:
        crumbs, cur = [], n["parent"]
        while cur and cur in by_id:
            crumbs.append(by_id[cur]["title"])
            cur = by_id[cur]["parent"]
        out[n["id"]] = list(reversed(crumbs))
    return out


def cmd_outline(args):
    raise NotImplementedError


def main():
    parser = argparse.ArgumentParser(
        description="Trích outline cây BRD và gác cổng docs/roadmap.md."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("outline", help="Trích outline gọn từ cây BRD markdown")
    o.add_argument("brd_dir")
    o.add_argument("--out", default=".specify/tmp/roadmap-brd/outline.json")
    o.add_argument("--head", type=int, default=15)
    o.set_defaults(func=cmd_outline)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
