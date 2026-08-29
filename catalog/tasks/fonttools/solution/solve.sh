#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. The solution bundle is private and is never
# copied into the model Agent image.
UPSTREAM_URL="https://github.com/fonttools/fonttools"
UPSTREAM_REVISION="e7e00f1b16aef6ede850206df3c100ccde27b2d3"
SOURCE_ARCHIVE_SHA256="2c7719e06724e5f34b4677eb4e7a5cb17a9cdee1225f829b2881b097d61d666c"
SOURCE_DIR="/tmp/fonttools-source"
SOURCE_ARCHIVE="/tmp/fonttools-source.tar"

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
rm -rf /workspace/.github
rm -f /workspace/Snippets/fontTools
