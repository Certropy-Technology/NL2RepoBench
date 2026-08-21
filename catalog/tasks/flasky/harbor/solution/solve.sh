#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/miguelgrinberg/flasky"
UPSTREAM_REVISION="3beedd640b9146b0bd65c8c2ecf402b01798bc33"
SOURCE_ARCHIVE_SHA256="d70278ce85aadc6127ef9f997c0410076488b744c01631a45499dc03bcd698d6"
SOURCE_DIR="/tmp/flasky-source"
SOURCE_ARCHIVE="/tmp/flasky-source.tar"

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
