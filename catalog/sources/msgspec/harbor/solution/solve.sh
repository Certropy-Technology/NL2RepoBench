#!/usr/bin/env bash
set -euo pipefail

revision="f51f378335b01dc0026dc6553a0b9e1915a8edae"
source_archive_sha256="0583e9ecf3d8f3f233722ba02361894e01f4bdc470e8fbe74d797ae758004390"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

git init "$tmp_dir/source" >/dev/null
git -C "$tmp_dir/source" remote add origin https://github.com/jcrist/msgspec
git -C "$tmp_dir/source" fetch --depth=1 origin "$revision" >/dev/null
git -C "$tmp_dir/source" checkout --detach FETCH_HEAD >/dev/null
test "$(git -C "$tmp_dir/source" rev-parse HEAD)" = "$revision"
git -C "$tmp_dir/source" archive --format=tar "$revision" > "$tmp_dir/source.tar"
printf '%s  %s\n' "$source_archive_sha256" "$tmp_dir/source.tar" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$tmp_dir/source.tar" -C /workspace
