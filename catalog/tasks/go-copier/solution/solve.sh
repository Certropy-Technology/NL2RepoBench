#!/usr/bin/env bash
set -euo pipefail

revision='c6b47b092d9840406d0abc347e68a28a7b812643'
archive_sha256='11b05c7a410dc39fd2cbcfb0f6cb307c1a694d3c33fff7a422109921f704cf18'
source_dir="$(mktemp -d)"
trap 'rm -rf "$source_dir"' EXIT

git clone --no-checkout https://github.com/jinzhu/copier "$source_dir/upstream"
git -C "$source_dir/upstream" checkout --detach "$revision"
test "$(git -C "$source_dir/upstream" rev-parse HEAD)" = "$revision"
test "$(git -C "$source_dir/upstream" archive --format=tar HEAD | sha256sum | awk '{print $1}')" = "$archive_sha256"

printf '%s\n' 'module github.com/jinzhu/copier' 'go 1.26.5' > go.mod
: > go.sum
mkdir -p vendor
: > vendor/modules.txt
cp "$source_dir/upstream/copier.go" "$source_dir/upstream/errors.go" .
