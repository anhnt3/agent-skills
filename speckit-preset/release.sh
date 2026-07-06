#!/usr/bin/env bash
# Release thủ công preset lên GitHub (không cần workflow/Action).
# Build zip -> tạo (hoặc cập nhật) GitHub Release + upload asset.
#
# Dùng:
#   ./release.sh            # đọc version từ preset.yml
#   ./release.sh 1.0.1      # ép version
#
# Yêu cầu: gh đã đăng nhập (gh auth login).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"

pkg="ba-interview-vi"
version="${1:-$(grep -E '^[[:space:]]*version:' preset.yml | head -1 | sed -E 's/.*version:[[:space:]]*"?([^"#]+)"?.*/\1/' | tr -d '[:space:]')}"
[ -n "$version" ] || { echo "Không xác định được version"; exit 1; }
tag="${pkg}-v${version}"
zip="dist/${pkg}-${version}.zip"

./build-zip.sh "$version"

notes="Spec-Kit preset. Cài:
\`\`\`bash
specify preset add --from https://github.com/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/releases/download/${tag}/${pkg}-${version}.zip
\`\`\`"

if gh release view "$tag" >/dev/null 2>&1; then
  echo "Tag $tag đã tồn tại -> cập nhật asset (--clobber)."
  gh release upload "$tag" "$zip" --clobber
else
  gh release create "$tag" "$zip" --title "${pkg} ${version}" --notes "$notes"
fi

echo "Done: $(gh release view "$tag" --json url --jq .url)"
