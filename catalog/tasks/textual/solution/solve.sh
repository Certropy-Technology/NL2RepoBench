#!/usr/bin/env bash
set -euo pipefail

# This directory is uploaded only by Harbor's trusted Oracle agent. Task
# metadata remains no-network; the Oracle run receives github.com as a
# run-scoped host authorization.
UPSTREAM_URL="https://github.com/Textualize/textual"
UPSTREAM_REVISION="06dbeef4bb70fb718236aa418ed658ef4667a126"
SOURCE_ARCHIVE_SHA256="481fcda705dcc2e3addded9d53b64c78232a7f46607621c9d0a33c4a6e0378b0"
SOURCE_DIR="/tmp/textual-source"
SOURCE_ARCHIVE="/tmp/textual-source.tar"

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
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
    | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
