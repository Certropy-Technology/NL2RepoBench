#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/kennethreitz/records"
UPSTREAM_REVISION="72efce67874d1b40ac2a35542127e8830da49707"
SOURCE_ARCHIVE_SHA256="4e0a1b23d7d38f96182d2be29d915fa45165fddd8ec14f193acb5304a57b0e04"
SOURCE_DIR="/tmp/records-source"
SOURCE_ARCHIVE="/tmp/records-source.tar"

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
