#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/eliben/pss"
readonly UPSTREAM_REVISION="b40cf0b6f1b8f8cb965144317e9ab7902b5fcb0b"
readonly SOURCE_ARCHIVE_SHA256="2c86bef90a85c8d09fd0a66d64d183f9960bc46f1489fce629303a92b43bee9b"
readonly SOURCE_DIR="/tmp/pss-source"
readonly SOURCE_ARCHIVE="/tmp/pss-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null

resolved_revision=$(git -C "$SOURCE_DIR" rev-parse HEAD)
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "unexpected source revision: $resolved_revision" >&2
    exit 1
fi

git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum -c -

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
