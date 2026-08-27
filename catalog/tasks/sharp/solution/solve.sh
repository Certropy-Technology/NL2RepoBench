#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/lovell/sharp"
readonly UPSTREAM_REVISION="ea5bef24c187b2c7ee3fe3cad3b45c8cb67a46fd"
readonly SOURCE_ARCHIVE_SHA256="d5b8bf9290848a376a7ceeacd2c32bdd3f289d77e464d69de570919a74fae54d"
readonly SOURCE_DIR="/tmp/sharp-oracle-source"
readonly SOURCE_ARCHIVE="/tmp/sharp-oracle-source.tar"
readonly TARGET="${1:-/workspace}"
readonly HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
mkdir -p "$SOURCE_DIR" "$TARGET"
find "$TARGET" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +

git -C "$SOURCE_DIR" init -q
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

tar -xf "$SOURCE_ARCHIVE" -C "$TARGET"
node "$TARGET/scripts/build.mjs"
cp "$HERE/package.json" "$TARGET/package.json"
cp "$HERE/package-lock.json" "$TARGET/package-lock.json"

test -f "$TARGET/dist/index.cjs"
test -f "$TARGET/dist/index.mjs"
test -f "$TARGET/dist/index.d.cts"
test -f "$TARGET/dist/index.d.mts"
test "$(node -p "require('$TARGET/package.json').version")" = "0.35.3"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
