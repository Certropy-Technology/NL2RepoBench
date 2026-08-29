#!/usr/bin/env bash
set -euo pipefail

revision="d652a1b1909d3520389b2c287ca3cf3aa3791451"
expected_archive="e7d863c47fbe692c97f5148a75dcda72695fca9dc672642dcdb4a22da28861a2"
source_url="https://github.com/valyala/fastjson"
clone_dir="$(mktemp -d)"
archive="$(mktemp)"
trap 'rm -rf "$clone_dir" "$archive"' EXIT

git -C "$clone_dir" init -q
git -C "$clone_dir" remote add origin "$source_url"
git -C "$clone_dir" fetch -q --depth 1 origin "$revision"
resolved="$(git -C "$clone_dir" rev-parse FETCH_HEAD)"
test "$resolved" = "$revision"
git -C "$clone_dir" archive --format=tar "$resolved" > "$archive"
printf '%s  %s\n' "$expected_archive" "$archive" | sha256sum -c -

tar -xf "$archive" -C .
cat > go.mod <<'MOD'
module github.com/valyala/fastjson

go 1.26.5
MOD
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
