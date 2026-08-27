#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/date-fns/date-fns'
UPSTREAM_REVISION='a0a39220522ed1228445792c768ed887709aea5f'
SOURCE_ARCHIVE_SHA256='636db05bafd090414a7d3f6d72aa8f50a4e9afdd0624f86c92f46a3084be170d'
SOURCE_REPO=/tmp/date-fns-source
SOURCE_ARCHIVE=/tmp/date-fns-source.tar
SOURCE_TREE=/tmp/date-fns-tree

rm -rf "$SOURCE_REPO" "$SOURCE_TREE" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_REPO"
git -C "$SOURCE_REPO" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_REPO" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_REPO" rev-parse FETCH_HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
  printf 'resolved revision mismatch: %s\n' "$resolved_revision" >&2
  exit 1
fi
git -C "$SOURCE_REPO" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

mkdir -p "$SOURCE_TREE"
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_TREE"
node --disable-warning=ExperimentalWarning /solution/build.mjs \
  "$SOURCE_TREE/pkgs/core" /workspace
