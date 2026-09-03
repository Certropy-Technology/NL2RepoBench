#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/google/go-cmp"
UPSTREAM_REVISION="b133f1f1932e48f466f597a3346ce6f5a49a0dc1"
SOURCE_ARCHIVE_SHA256="0db58f99e9ff0c467df202b87cd72b97b8518b01ada824b8d9259e6a09b017fe"
SOURCE_DIR="/tmp/go-cmp-source"
SOURCE_ARCHIVE="/tmp/go-cmp-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
# The frozen module declares Go 1.21. This directive-only adaptation keeps the
# upstream source bytes intact while satisfying the locked Go runtime contract.
sed -i 's/^go 1\.21$/go 1.26.5/' /workspace/go.mod
: > /workspace/go.sum
exit 0
