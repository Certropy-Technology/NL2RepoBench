#!/usr/bin/env bash
set -euo pipefail
target="${1:-/workspace}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
test "$(sha256sum "$root/source.tar" | awk '{print $1}')" = 4611a77b477cc333b75cf4f934ba6b9dae2f603a3ceabe6b89749f5c3d36c81c
 grep -Fx 'source_revision=3f304acdc5177aa119f383b3b09557bd70d7916c' "$root/provenance.txt" >/dev/null
rm -rf "$target"; mkdir -p "$target"
cp "$root/package.json" "$root/package-lock.json" "$root/index.js" "$root/index.d.ts" "$root/license" "$root/provenance.txt" "$target/"
cp -a "$root/node_modules" "$target/node_modules"
mkdir -p "$target/node_modules/camelcase-keys"
cp "$root/index.js" "$root/node_modules/camelcase-keys/index.js"
cp "$root/index.d.ts" "$root/node_modules/camelcase-keys/index.d.ts"
cp "$root/package.json" "$target/node_modules/camelcase-keys/package.json"
(cd "$target" && node --input-type=module -e "import(\"./index.js\").then(() => console.log(\"oracle runtime loaded\"))")
