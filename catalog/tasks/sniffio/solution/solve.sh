#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This file is uploaded only to the trusted
# Oracle run; the model Agent has no source-host authorization.
UPSTREAM_URL="https://github.com/python-trio/sniffio"
UPSTREAM_REVISION="6996e05d9b9debe32f42f709c8041e744f850478"
SOURCE_ARCHIVE_SHA256="1bcb3387980cdb5adac666e1edacabc2976807b9c053d1c4a3781b9f648cda68"
SOURCE_DIR="/tmp/sniffio-source"
SOURCE_ARCHIVE="/tmp/sniffio-source.tar"

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
