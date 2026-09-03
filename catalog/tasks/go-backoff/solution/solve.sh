#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/cenkalti/backoff'
UPSTREAM_REVISION='ffcfd8ab39e2910a1180ba0b7a02a52f0485adc9'
SOURCE_DIR=/tmp/go-backoff-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
source_archive="$(mktemp)"
trap 'rm -f "$source_archive"' EXIT
git -C "$SOURCE_DIR" archive --format=tar HEAD > "$source_archive"
printf '%s  %s\n' '2cb02d3324fb2aaa1c02d0d348427bc2e5b0e27bf2b8402b30df4482adbd63ab' "$source_archive" | sha256sum --check --strict
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github /workspace/.git
sed -i 's/^go 1\.23$/go 1.26.5/' /workspace/go.mod
: > /workspace/go.sum
