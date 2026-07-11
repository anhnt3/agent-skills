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

pkg="dft-preset"
version="${1:-$(grep -E '^[[:space:]]*version:' preset.yml | head -1 | sed -E 's/.*version:[[:space:]]*"?([^"#]+)"?.*/\1/' | tr -d '[:space:]')}"
[ -n "$version" ] || { echo "Không xác định được version"; exit 1; }
tag="${pkg}-v${version}"
zip="dist/${pkg}-${version}.zip"
repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
url="https://github.com/${repo}/releases/download/${tag}/${pkg}-${version}.zip"

./build-zip.sh "$version"

notes="Spec-Kit preset. Cài:
\`\`\`bash
specify preset add --from ${url}
\`\`\`"

if gh release view "$tag" >/dev/null 2>&1; then
  echo "Tag $tag đã tồn tại -> cập nhật asset (--clobber)."
  gh release upload "$tag" "$zip" --clobber
else
  gh release create "$tag" "$zip" --title "${pkg} ${version}" --notes "$notes"
fi

# Cập nhật URL cài trong README về đúng release vừa tạo (perl -pi: portable macOS/Linux,
# sed -i khác cú pháp giữa BSD và GNU).
if [ -f README.md ]; then
  URL_NEW="$url" PKG="$pkg" perl -pi -e 's#https://github\.com/[^ )]*/releases/download/$ENV{PKG}-v[^ )/]*/$ENV{PKG}-[^ )]*\.zip#$ENV{URL_NEW}#g' README.md
  echo "README: cập nhật URL -> $url"
fi

echo "Done: $(gh release view "$tag" --json url --jq .url)"
