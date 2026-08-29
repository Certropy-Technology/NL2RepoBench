#!/usr/bin/env bash
set -euo pipefail
readonly UPSTREAM_URL="https://github.com/eliben/pycparser"
readonly UPSTREAM_REVISION="10d17757e282d8af5426d6df4d55eb394042b550"
readonly SOURCE_ARCHIVE_SHA256="ed31469eea243e25ce86310039c174a61890d2acc7586cd06f8be38cf1baf5a1"
readonly SOURCE_DIR="/tmp/pycparser-source"
readonly SOURCE_ARCHIVE="/tmp/pycparser-source.tar"
rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
test "$(git -C "$SOURCE_DIR" rev-parse HEAD)" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -rf /workspace/.github
