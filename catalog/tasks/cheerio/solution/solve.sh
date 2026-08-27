#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-/workspace}"
mkdir -p "$target"
cp -a "$here/package/." "$target/"

test -f "$target/package.json"
test -f "$target/package-lock.json"
test -f "$target/dist/esm/index.js"
test -f "$target/dist/commonjs/index.js"
