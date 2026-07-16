#!/usr/bin/env python3
"""Kiểm bộ agent của speckit-extension trước khi release.

Bắt đúng các lỗi im lặng đã từng xảy ra:
  - Frontmatter KHÔNG phải YAML hợp lệ (vd chuỗi chứa ": " không được trích dẫn
    -> Claude Code không load được agent, agent-assign parse trượt).
  - `name` không phải slug (Claude Code yêu cầu chữ thường + gạch ngang;
    agent-assign khớp agent THEO `name` này).
  - Thiếu `description` (agent-assign dùng nó để tự khớp task -> agent).
  - File .md có nhưng thiếu mục trong registry.yml (agent sẽ không bao giờ
    được dò ra) và ngược lại.

Dùng:  python3 scripts/check-agents.py
Trả 0 nếu sạch, 1 nếu có lỗi.
"""
import os
import re
import sys

import yaml

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AGENTS = os.path.join(ROOT, "speckit-extension", "agents")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors = []


def err(msg):
    errors.append(msg)


registry_path = os.path.join(AGENTS, "registry.yml")
if not os.path.exists(registry_path):
    err("thiếu agents/registry.yml")
    print("LỖI: thiếu agents/registry.yml")
    sys.exit(1)

registry = yaml.safe_load(open(registry_path))
reg_by_name = {a["name"]: a for a in registry.get("agents", [])}

md_files = sorted(f for f in os.listdir(AGENTS) if f.endswith(".md"))

for fname in md_files:
    raw = open(os.path.join(AGENTS, fname)).read()
    m = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
    if not m:
        err(f"{fname}: không có YAML frontmatter")
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        err(f"{fname}: frontmatter KHÔNG phải YAML hợp lệ -> {e}")
        continue

    name = fm.get("name")
    if not name:
        err(f"{fname}: thiếu `name`")
    elif not SLUG.match(str(name)):
        err(f"{fname}: `name` = {name!r} không phải slug (cần chữ thường + gạch ngang)")
    elif name not in reg_by_name:
        err(f"{fname}: `name` = {name!r} KHÔNG có mục trong registry.yml -> sẽ không bao giờ được dò ra")
    elif reg_by_name[name]["file"] != fname:
        err(f"{fname}: registry trỏ tới file {reg_by_name[name]['file']!r}, lệch tên")

    if not fm.get("description"):
        err(f"{fname}: thiếu `description` -> agent-assign không khớp task được")

for a in registry.get("agents", []):
    if not os.path.exists(os.path.join(AGENTS, a["file"])):
        err(f"registry.yml: mục {a['name']!r} trỏ tới {a['file']!r} không tồn tại")
    if not a.get("detect", {}).get("any"):
        err(f"registry.yml: mục {a['name']!r} thiếu `detect.any` -> không dò được stack")

if errors:
    print(f"LỖI ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: {len(md_files)} agent, frontmatter hợp lệ, khớp registry.")
sys.exit(0)
