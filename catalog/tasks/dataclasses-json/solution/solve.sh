#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/lidatong/dataclasses-json.git'
UPSTREAM_REVISION='dc63902eeb5e1c5ce1ea4e078c50e0eb9bc1a541'
SOURCE_ARCHIVE_SHA256='113c90da5957f13cc49f80d535cde965e66850f72559498a9ebfd934c4db449f'
SOURCE_DIR=/tmp/dataclasses-json-src
SOURCE_ARCHIVE=/tmp/dataclasses-json-source.tar

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
[[ "$resolved_revision" == "$UPSTREAM_REVISION" ]]
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -rf /workspace/.git /workspace/.github /workspace/tests
