#!/usr/bin/env bash
set -euo pipefail

here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
revision="9cbc5cf23cb2b62231bc1822a868138e4772d4e5"
archive="/tmp/basic-ftp-${revision}.tar.gz"
source_root="/tmp/basic-ftp-source"

rm -f "$archive"
rm -rf "$source_root"
mkdir -p "$source_root"
node "$here/fetch-source.mjs" "$archive"
printf '%s  %s\n' "515fbf4bfc6fed25ed9b58d5ef72d9d67cbe13cb4a2b6ca5abdcff4435ae092e" "$archive" | sha256sum --check --strict
tar -xzf "$archive" --strip-components=1 -C "$source_root"
(
  cd "$source_root"
  sha256sum --check --strict "$here/source-files.sha256"
)
node -e 'const p=require(process.argv[1]); if(p.name!=="basic-ftp"||p.version!=="6.2.0"||p.license!=="MIT") process.exit(1)' "$source_root/package.json"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$here/reference-package/." /workspace/
test -f /workspace/package.json
test -f /workspace/package-lock.json
test -f /workspace/dist/index.js
printf 'oracle source revision %s verified\n' "$revision"
