#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/pysonDB/pysonDB-v2"
readonly UPSTREAM_REVISION="4399314ecdc3f394ccc92ecd440de4b0180b12a8"
readonly SOURCE_ARCHIVE_SHA256="4a80fa0f2e29fa613bd946c536159a5769607c0bd6748d1feb7f65db71bf4f07"
readonly SOURCE_DIR="/tmp/pysondb-v2-source"
readonly SOURCE_ARCHIVE="/tmp/pysondb-v2-source.tar"

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
