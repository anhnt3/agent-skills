#!/usr/bin/env python3
"""Cây đơn vị rút đặc tả (unit) cho code-intel: tính node nào là "cha trực
tiếp của lá" (unit mặc định), sinh slug thư mục tất định, tính đường dẫn.

Thuần logic — không đọc/ghi file ngoài đọc functions.json qua CLI ở cuối file
này, không tìm code, không viết nội dung intel.md. `code-intel` (command) đọc
kết quả, LLM trình cây cho người dùng xác nhận, rồi gọi lại `units` với danh
sách root đã chốt để lấy đường dẫn + danh sách FN-ID.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import fnlist_tree as ft

def _force_utf8_console() -> None:
    """Windows mở subprocess với stdout/stderr mã cp1252 mặc định, không phải
    UTF-8 — in tiếng Việt có dấu ra đó là crash UnicodeEncodeError. Ép lại UTF-8
    khi có thể; capsys của pytest thay stdout bằng đối tượng không có
    `reconfigure` nên phải hasattr trước."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        enc = getattr(stream, "encoding", None)
        if enc and enc.lower() != "utf-8" and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_force_utf8_console()

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")
_MAX_SLUG_LEN = 60


def slugify(name: str) -> str:
    """Tên tiếng Việt có dấu → slug ASCII tất định, dùng làm tên thư mục.
    Tất định là bắt buộc: chạy lại phải ra đúng slug cũ để no-clobber còn
    khớp được thư mục — đây KHÔNG phải việc LLM tự đặt tên mỗi lần."""
    s = name.replace("Đ", "D").replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = _SLUG_STRIP_RE.sub("-", s.lower()).strip("-")
    if len(s) > _MAX_SLUG_LEN:
        s = s[:_MAX_SLUG_LEN].rstrip("-")
    return s or "khong-ten"


def dedupe_slugs(slugs: list[str]) -> list[str]:
    """Hai anh em trùng slug sau khi sinh (tên khác nhau, slug giống nhau) →
    hậu tố -2, -3… theo thứ tự xuất hiện."""
    seen: dict[str, int] = {}
    out = []
    for s in slugs:
        seen[s] = seen.get(s, 0) + 1
        out.append(s if seen[s] == 1 else f"{s}-{seen[s]}")
    return out


def is_leaf(node: dict) -> bool:
    return not node.get("children")


def is_leaf_parent(node: dict) -> bool:
    """Node có TẤT CẢ con đều là lá — điều kiện unit mặc định."""
    children = node.get("children") or []
    return bool(children) and all(is_leaf(c) for c in children)


def default_units(node: dict) -> list[dict]:
    """Từ một node, trả danh sách node là "unit" theo luật cha-trực-tiếp-của-
    lá. Một lá đứng lẻ dưới cha có con hỗn hợp (vài con là lá, vài con có
    cháu) tự thành unit riêng — nhánh `is_leaf` khớp trước khi xét
    `is_leaf_parent` nên nó không bị gộp lên cha."""
    if is_leaf(node) or is_leaf_parent(node):
        return [node]
    out = []
    for c in node["children"]:
        out.extend(default_units(c))
    return out


def compute_paths(nodes: list[dict], prefix: str = "") -> dict[str, str]:
    """Trả {FN-ID: đường dẫn thư mục} cho MỌI node trong `nodes` (đệ quy toàn
    cây). Số thứ tự lấy theo vị trí trong `children` (khớp thứ tự dòng file
    nguồn), không phải số trong FN-ID — FN-ID có thể đổi khi cấp lại theo luật
    của fnlist-import, vị trí hiển thị thì không cần khớp theo nó."""
    slugs = dedupe_slugs([slugify(n["name"]) for n in nodes])
    out: dict[str, str] = {}
    for i, (node, slug) in enumerate(zip(nodes, slugs), start=1):
        path = f"{prefix}{i:02d}-{slug}"
        out[node["id"]] = path
        out.update(compute_paths(node.get("children") or [], path + "/"))
    return out


def render_tree(nodes: list[dict], unit_ids: set[str], depth: int = 0) -> list[str]:
    """Cây thụt lề, đánh dấu `[UNIT]` ở node là ranh giới unit đề xuất — để
    LLM trình cho người dùng xác nhận/điều chỉnh trước khi quét."""
    lines = []
    for node in nodes:
        marker = "  [UNIT]" if node["id"] in unit_ids else ""
        lines.append("  " * depth + f"{node['name']} ({node['id']}){marker}")
        lines.extend(render_tree(node.get("children") or [], unit_ids, depth + 1))
    return lines


def cmd_propose(a) -> None:
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    if a.start:
        node = ft.find_by_id(tree, a.start)
        if node is None:
            raise SystemExit(f"Không có {a.start} trong {a.functions}.")
        roots = [node]
    else:
        roots = tree
    units: list[dict] = []
    for node in roots:
        units.extend(default_units(node))
    unit_ids = {u["id"] for u in units}
    out = {
        "units": [{"id": u["id"], "name": u["name"]} for u in units],
        "tree": "\n".join(render_tree(roots, unit_ids)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_units(a) -> None:
    doc = json.loads(Path(a.functions).read_text(encoding="utf-8"))
    tree = doc.get("functions") or []
    paths = compute_paths(tree)
    out = {"units": []}
    for root_id in a.roots.split(","):
        root_id = root_id.strip()
        node = ft.find_by_id(tree, root_id)
        if node is None:
            raise SystemExit(f"Không có {root_id} trong {a.functions}.")
        leaves = ft.subtree_leaves(node)
        out["units"].append({
            "id": node["id"],
            "name": node["name"],
            "path": paths[node["id"]] + "/intel.md",
            "fn_ids": [{"id": lf["id"], "name": lf["name"],
                       "status": lf.get("status", "pending")} for lf in leaves],
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description="Tính unit/slug/đường dẫn cho code-intel")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("propose", help="Đề xuất unit mặc định + cây thụt lề")
    pr.add_argument("--functions", default=".specify/docs/functions.json")
    pr.add_argument("--start", default=None,
                    help="FN-ID điểm bắt đầu; trống = toàn bộ cây")
    pr.set_defaults(func=cmd_propose)

    un = sub.add_parser("units", help="Tính đường dẫn + danh sách FN-ID cho unit đã chốt")
    un.add_argument("--functions", default=".specify/docs/functions.json")
    un.add_argument("--roots", required=True,
                    help="Danh sách FN-ID, ngăn cách bằng dấu phẩy")
    un.set_defaults(func=cmd_units)

    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
