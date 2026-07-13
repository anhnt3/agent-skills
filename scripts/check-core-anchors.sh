#!/usr/bin/env bash
# Kiểm các "neo" (anchor) mà dft-preset phụ thuộc vào core template của Spec Kit.
#
# Preset wrap đè luật core bằng cách neo vào TÊN SECTION / wording nguyên văn của core
# (vd "Pre-Execution Checks", "Specification Quality Validation"). Upstream đổi tên là
# preset gãy ÂM THẦM — script này bắt sớm điều đó. Chạy sau mỗi lần nâng cấp `specify`
# (trong project đã init + cài preset) hoặc trên clone spec-kit trước khi cho team nâng cấp.
#
# Dùng:
#   ./scripts/check-core-anchors.sh [đường-dẫn]
#     đường-dẫn = clone repo spec-kit (có templates/commands/ ở gốc), HOẶC project đã
#                 `specify init` + cài dft-preset (kiểm trong bản command đã materialize
#                 tại .claude/skills/speckit-<cmd>/SKILL.md — chính artifact agent chạy).
#     Mặc định: thư mục hiện tại.
#
# Exit 0 = mọi neo còn nguyên; exit 1 = có neo mất (liệt kê MISSING).
set -uo pipefail

root="${1:-.}"
fail=0
mode=""

# cmd_file <tên-core-không-prefix> -> in đường dẫn file chứa prompt command đó
cmd_file() {
  local name="$1"
  case "$mode" in
    repo)    echo "$root/templates/commands/$name.md" ;;
    project)
      # Ưu tiên bản materialize (artifact thật agent chạy); fallback layout cũ.
      if [ -f "$root/.claude/skills/speckit-$name/SKILL.md" ]; then
        echo "$root/.claude/skills/speckit-$name/SKILL.md"
      else
        echo "$root/.specify/templates/commands/$name.md"
      fi ;;
  esac
}

tpl_file() {
  local name="$1"
  case "$mode" in
    repo)    echo "$root/templates/$name.md" ;;
    project) echo "$root/.specify/templates/$name.md" ;;
  esac
}

if [ -d "$root/templates/commands" ]; then
  mode=repo
elif [ -d "$root/.specify" ]; then
  mode=project
else
  echo "LỖI: '$root' không phải clone spec-kit (templates/commands/) hay project đã init (.specify/)" >&2
  exit 2
fi
echo "Chế độ: $mode ($root)"
echo

check() { # check <file> <mô tả> <chuỗi neo...>
  local file="$1" label="$2"; shift 2
  if [ ! -f "$file" ]; then
    echo "MISSING FILE: $file ($label)"
    fail=1
    return
  fi
  local anchor
  for anchor in "$@"; do
    if grep -qF -- "$anchor" "$file"; then
      echo "OK      : $label — '$anchor'"
    else
      echo "MISSING : $label — '$anchor' không còn trong $file"
      fail=1
    fi
  done
}

# --- Neo của preset speckit.specify (wrap) ---
check "$(cmd_file specify)" "specify" \
  "Pre-Execution Checks" \
  "Specification Quality Validation" \
  "For AI Generation" \
  "NEEDS CLARIFICATION" \
  "before_specify" \
  "feature.json"

# --- Neo của preset speckit.constitution (wrap) ---
check "$(cmd_file constitution)" "constitution" \
  "RATIFICATION_DATE" \
  "less or more principles"
check "$(tpl_file constitution-template)" "constitution-template" \
  "SECTION_2_NAME" \
  "SECTION_3_NAME"

# --- Neo của preset speckit.plan (wrap) ---
check "$(tpl_file plan-template)" "plan-template" \
  "Constitution Check" \
  "Complexity Tracking"

# --- Neo của preset spec-template + tasks-template (replace, tự chứa) ---
# Không có wrap-anchor để kiểm (replace không dùng {CORE_TEMPLATE}); thay vào đó nhắc maintainer
# diff bản replace với core sau mỗi lần nâng CLI vì core đổi template sẽ KHÔNG tự lan vào bản của preset.
echo "NOTE    : spec-template & tasks-template là 'replace' tự chứa — sau khi nâng spec-kit hãy diff"
echo "          templates/{spec,tasks}-template.md của preset với core để bắt thay đổi cấu trúc."

# --- Cơ chế analyze/converge mà constitution override giải thích cho người dùng ---
check "$(cmd_file analyze)" "analyze" \
  "MUST"
cf="$(cmd_file converge)"
if [ -f "$cf" ]; then
  check "$cf" "converge" "MUST"
else
  echo "WARN    : converge không có (bản spec-kit cũ?) — constitution override nhắc tới /speckit.converge"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "✅ Mọi neo còn nguyên — preset tương thích với core này."
else
  echo "❌ Có neo bị mất — upstream đã đổi wording. Sửa neo tương ứng trong speckit-dft-preset/commands/ trước khi nâng cấp."
fi
exit "$fail"
