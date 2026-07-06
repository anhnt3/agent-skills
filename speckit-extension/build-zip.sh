#!/usr/bin/env bash
# Đóng gói extension dft-speckit thành zip chuẩn để cài qua:
#   specify extension add dft-speckit --from <url-tới-zip>
#
# Zip có 1 thư mục gốc "dft-speckit/" chứa extension.yml ngay bên trong
# (đúng kiểu GitHub archive wrap 1 tầng). Loại .venv/__pycache__/config.local.
#
# Dùng:
#   ./build-zip.sh [version]
# Không truyền version -> tự đọc từ extension.yml.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"

version="${1:-}"
if [ -z "$version" ]; then
  version="$(grep -E '^[[:space:]]*version:' extension.yml | head -1 | sed -E 's/.*version:[[:space:]]*"?([^"#]+)"?.*/\1/' | tr -d '[:space:]')"
fi
[ -n "$version" ] || { echo "Không xác định được version"; exit 1; }

pkg="dft-speckit"
out="${here}/dist/${pkg}-${version}.zip"
mkdir -p "${here}/dist"
rm -f "$out"

# Staging để zip có thư mục gốc dft-speckit/
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
dest="${stage}/${pkg}"
mkdir -p "$dest"

# Chỉ đưa các phần cần thiết của extension.
cp extension.yml "$dest/"
[ -f README.md ] && cp README.md "$dest/"
[ -f .extensionignore ] && cp .extensionignore "$dest/"
cp -R commands "$dest/"
[ -d templates ] && cp -R templates "$dest/"
mkdir -p "$dest/scripts"
# Copy scripts nhưng loại venv/pycache/config.local
find scripts -type f \
  ! -path 'scripts/.venv/*' \
  ! -name '*.pyc' \
  ! -path '*/__pycache__/*' \
  ! -name '*-config.local.yml' \
  -exec sh -c 'mkdir -p "$2/$(dirname "$1")"; cp "$1" "$2/$1"' _ {} "$dest" \;

( cd "$stage" && zip -rq "$out" "$pkg" )
echo "OK: $out"
unzip -l "$out" | sed -n '1,20p'
