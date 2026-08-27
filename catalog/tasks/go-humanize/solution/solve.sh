#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/dustin/go-humanize"
readonly revision="4d1d9082551ec085912e7d2253a33ae547fca000"
readonly archive_sha256="ce579ea6d7e8afd59ea2c9b3f8040984cc7ccb1fddc52e938a52ce64f265b9d4"
readonly source_dir="$(mktemp -d)"
readonly source_archive="$(mktemp)"
trap 'rm -rf "$source_dir" "$source_archive"' EXIT

git -C "$source_dir" init -q
git -C "$source_dir" remote add origin "$upstream_url"
git -C "$source_dir" fetch -q --depth 1 origin "$revision"
resolved_revision="$(git -C "$source_dir" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$revision"
git -C "$source_dir" archive --format=tar FETCH_HEAD > "$source_archive"
printf '%s  %s\n' "$archive_sha256" "$source_archive" | sha256sum --check --strict
tar -xf "$source_archive" -C /workspace

cat > /workspace/go.mod <<'MOD'
module github.com/dustin/go-humanize

go 1.26.5
MOD
: > /workspace/go.sum
mkdir -p /workspace/vendor
: > /workspace/vendor/modules.txt
