#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. The solution directory is uploaded
# only for `-a oracle`; model Agent Runs receive neither this script nor a
# source-host authorization.
UPSTREAM_URL="https://github.com/websockets/ws"
UPSTREAM_REVISION="d9b89544e627f2a260fb85a6f42c8ecba98d7615"
SOURCE_ARCHIVE_SHA256="ef59e63af8772e6cc00100a743fa267f53fff2022ca32f4b1e303c5fc57140f3"
SOURCE_DIR="/tmp/ws-source"
SOURCE_ARCHIVE="/tmp/ws-source.tar"
TARGET="${1:-/workspace}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

mkdir -p "$TARGET"
find "$TARGET" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$TARGET"
node "$HERE/prepare-oracle.mjs" "$TARGET"

test -f "$TARGET/index.js"
test -f "$TARGET/wrapper.mjs"
test -f "$TARGET/package.json"
test -f "$TARGET/package-lock.json"
