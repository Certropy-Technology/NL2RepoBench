#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/dbader/schedule"
UPSTREAM_REVISION="82a43db1b938d8fdf60103bd41f329e06c8d3651"
SOURCE_ARCHIVE_SHA256="718fc6887ae9165aaf5f751780416ead8ce82844a2f615543f43acfaac7d4cff"
SOURCE_DIR="/tmp/schedule-source"
SOURCE_ARCHIVE="/tmp/schedule-source.tar"

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
