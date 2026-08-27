#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/google/uuid"
readonly revision="0f11ee6918f41a04c201eceeadf612a377bc7fbc"
readonly archive_sha256="e24d1eb2f3787e8e47cacff5c9ef5e7286ef6406a22da2da036fd2a19fa5c049"
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
module github.com/google/uuid

go 1.26.5
MOD
: > /workspace/go.sum
mkdir -p /workspace/vendor
: > /workspace/vendor/modules.txt
