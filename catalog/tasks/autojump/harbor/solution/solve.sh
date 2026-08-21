#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/wting/autojump"
UPSTREAM_REVISION="ee21082751da739c65fe0ec2d02ca95d4266aebc"
SOURCE_ARCHIVE_SHA256="a91e88d3d72b8abd2328d1f990d6e360d27736b49375e5c1e3fd8db576752cd9"
SOURCE_DIR="/tmp/autojump-source"
SOURCE_ARCHIVE="/tmp/autojump-source.tar"

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
