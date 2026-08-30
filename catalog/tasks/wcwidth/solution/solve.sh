#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. This file is uploaded only to the
# trusted Oracle run. The model Agent receives no source-host authorization.
UPSTREAM_URL="https://github.com/jquast/wcwidth"
UPSTREAM_REVISION="551710eabf316ed2d9e3782c1fe9cf80ff0f6ed9"
SOURCE_ARCHIVE_SHA256="sha256:d8621c78e2a93b9f7a97ee756832a3639e8bbb87c7c79f4c8344ef7fb4bf8fb6"
SOURCE_DIR="/tmp/wcwidth-source"
SOURCE_ARCHIVE="/tmp/wcwidth-source.tar"

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
