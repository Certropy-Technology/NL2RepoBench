#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. This script is uploaded only to
# the trusted Oracle run; it is never part of the model agent image.
readonly UPSTREAM_URL="https://github.com/pfmoore/editables"
readonly UPSTREAM_REVISION="e54908a593a1062be201d1acdb80e379e0776d4b"
readonly SOURCE_ARCHIVE_SHA256="d82a26dd246c6b5f37bc9881975d3fe2af535b390f90dc452575c0ebfea5f2aa"
readonly SOURCE_DIR="/tmp/editables-source"
readonly SOURCE_ARCHIVE="/tmp/editables-source.tar"

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
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
