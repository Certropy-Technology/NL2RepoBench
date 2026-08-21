#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/asweigart/pyperclip"
readonly UPSTREAM_REVISION="f5326bfd7c5448b40051dd261a7304657977b838"
readonly EXPECTED_ARCHIVE_SHA256="4e80effb92cd84116a2541bb5aa4df7d7832761c04600322f558265ba73c0275"
readonly SOURCE_DIR="/tmp/pyperclip-source"

rm -rf "$SOURCE_DIR"
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null

actual_revision=$(git -C "$SOURCE_DIR" rev-parse HEAD)
if [[ "$actual_revision" != "$UPSTREAM_REVISION" ]]; then
    echo "Unexpected upstream revision: $actual_revision" >&2
    exit 1
fi

actual_archive_sha256=$(git -C "$SOURCE_DIR" archive --format=tar HEAD | sha256sum | cut -d' ' -f1)
if [[ "$actual_archive_sha256" != "$EXPECTED_ARCHIVE_SHA256" ]]; then
    echo "Unexpected source archive digest: $actual_archive_sha256" >&2
    exit 1
fi

cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
