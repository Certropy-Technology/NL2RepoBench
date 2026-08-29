#!/usr/bin/env bash
set -euo pipefail

revision="20620ebfd195d384d85fc134e29cc4916297a92f"
source_sha256="be351a99690d1692929f1e4c5c08aba84010cee56973f16156716eab5fa0e816"
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
checkout=$(mktemp -d /tmp/own-keys-oracle.XXXXXX)
trap 'rm -rf "$checkout"' EXIT

git -C "$checkout" init -q
git -C "$checkout" remote add origin https://github.com/ljharb/own-keys.git
git -C "$checkout" fetch -q --depth=1 origin "$revision"
git -C "$checkout" checkout -q --detach FETCH_HEAD
test "$(git -C "$checkout" rev-parse HEAD)" = "$revision"
git -C "$checkout" archive --format=tar HEAD > "$checkout/source.tar"
printf '%s  %s\n' "$source_sha256" "$checkout/source.tar" | sha256sum -c -

install -m 0644 "$checkout/index.js" /workspace/index.js
install -m 0644 "$checkout/index.d.ts" /workspace/index.d.ts
install -m 0644 "$checkout/LICENSE" /workspace/LICENSE
install -m 0644 "$checkout/README.md" /workspace/README.md
install -m 0644 "$script_dir/candidate-package.json" /workspace/package.json
install -m 0644 "$script_dir/package-lock.json" /workspace/package-lock.json
