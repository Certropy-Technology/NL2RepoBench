#!/usr/bin/env bash
set -euo pipefail

revision="f51f378335b01dc0026dc6553a0b9e1915a8edae"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

git init "$tmp_dir/source" >/dev/null
git -C "$tmp_dir/source" remote add origin https://github.com/jcrist/msgspec
git -C "$tmp_dir/source" fetch --depth=1 origin "$revision" >/dev/null
git -C "$tmp_dir/source" checkout --detach FETCH_HEAD >/dev/null
test "$(git -C "$tmp_dir/source" rev-parse HEAD)" = "$revision"
cp -a "$tmp_dir/source"/. /workspace/
