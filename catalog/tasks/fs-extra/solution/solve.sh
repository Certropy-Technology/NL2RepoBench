#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/jprichardson/node-fs-extra"
UPSTREAM_REVISION="53a8d1a63c8eb30573110ed0f6528975f98801f0"
SOURCE_ARCHIVE_SHA256="3b7a476361ff49cdba8037c03fcc6bab044c85ff3c33e29ed8a1f489309a41f0"
SOURCE_ROOT="/tmp/fs-extra-source"
SOURCE_ARCHIVE="/tmp/fs-extra-source.tar"

rm -rf "$SOURCE_ROOT" "$SOURCE_ARCHIVE"
git init "$SOURCE_ROOT"
git -C "$SOURCE_ROOT" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_ROOT" fetch --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_ROOT" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_ROOT" checkout --detach FETCH_HEAD
git -C "$SOURCE_ROOT" archive --format=tar HEAD > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -f /workspace/.npmrc
cp /solution/runtime-package.json /workspace/package.json
cp /solution/runtime-package-lock.json /workspace/package-lock.json
chmod 0444 /workspace/package.json /workspace/package-lock.json

printf 'oracle source revision %s verified; git-archive sha256 %s\n' \
  "$UPSTREAM_REVISION" "$SOURCE_ARCHIVE_SHA256"
