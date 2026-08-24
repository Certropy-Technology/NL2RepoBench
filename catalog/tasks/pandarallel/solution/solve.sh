#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/nalepae/pandarallel"
UPSTREAM_REVISION="261a652cddb219ac353ff803e81646c08b72fc6f"
SOURCE_ARCHIVE_SHA256="e6248ba2a30d551242e03df5b83d71ff4ff63c4b9ada2ab8c3ba82b051e1b5cd"
SOURCE_DIR="/tmp/pandarallel-source"
SOURCE_ARCHIVE="/tmp/pandarallel-source.tar"

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
