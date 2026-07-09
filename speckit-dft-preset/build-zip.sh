#!/usr/bin/env bash
# Đóng gói preset dft-preset thành zip chuẩn để cài qua:
#   specify preset add --from <url-tới-zip>
#
# Zip có 1 thư mục gốc "dft-preset/" chứa preset.yml ngay bên trong
# (đúng kiểu GitHub archive wrap 1 tầng).
#
# Dùng:
#   ./build-zip.sh [version]
# Không truyền version -> tự đọc từ preset.yml (preset.version).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"

version="${1:-}"
if [ -z "$version" ]; then
  # dòng "  version:" dưới block preset: (loại speckit_version vì key khác)
  version="$(grep -E '^[[:space:]]*version:' preset.yml | head -1 | sed -E 's/.*version:[[:space:]]*"?([^"#]+)"?.*/\1/' | tr -d '[:space:]')"
fi
[ -n "$version" ] || { echo "Không xác định được version"; exit 1; }

pkg="dft-preset"
out="${here}/dist/${pkg}-${version}.zip"
mkdir -p "${here}/dist"
rm -f "$out"

# Staging để zip có thư mục gốc dft-preset/
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
dest="${stage}/${pkg}"
mkdir -p "$dest"

cp preset.yml "$dest/"
[ -f README.md ] && cp README.md "$dest/"
[ -f LICENSE ] && cp LICENSE "$dest/"
cp -R commands "$dest/"
cp -R templates "$dest/"

( cd "$stage" && zip -rq "$out" "$pkg" )
echo "OK: $out"
unzip -l "$out" | sed -n '1,20p'
