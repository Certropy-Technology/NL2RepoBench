#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-/workspace}"
mkdir -p "$target"
cp "$here/index.js" "$target/index.js"
cp "$here/package.json" "$target/package.json"
cp "$here/package-lock.json" "$target/package-lock.json"
cp "$here/LICENSE" "$target/LICENSE"

test -f "$target/index.js"
test -f "$target/package.json"
test -f "$target/package-lock.json"
