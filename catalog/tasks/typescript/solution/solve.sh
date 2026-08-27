#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR=/tmp/typescript-reference
SOURCE_ARCHIVE_SHA256=d3de9628ec8a782ccc5e0f0261a23fc642b9b20d5e614f78a324e5abf8b3be3b
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

rm -rf "$SOURCE_DIR"
mkdir -p "$SOURCE_DIR"
archive="$SCRIPT_DIR/source.tar"
test "$(sha256sum "$archive" | cut -d' ' -f1)" = "$SOURCE_ARCHIVE_SHA256"
test "$(cat "$SCRIPT_DIR/source-revision.txt")" = "d6c4afddb2c55f4a9dea7b59293a99a8fdea1799"
tar -xf "$archive" -C "$SOURCE_DIR" package.json packages/typescript/package.json LICENSE.txt
test "$(node -e 'console.log(require(process.argv[1]).license)' "$SOURCE_DIR/package.json")" = "Apache-2.0"
test "$(node -e 'console.log(require(process.argv[1]).name)' "$SOURCE_DIR/packages/typescript/package.json")" = "@typescript/typescript"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
cp -a "$SCRIPT_DIR/distribution/." /workspace/
test "$(node -e 'console.log(require(process.argv[1]).name)' /workspace/package.json)" = "@typescript/typescript"
test -f /workspace/dist/ast/scanner.js
test -f /workspace/dist/ast/spanMap.js
test -f /workspace/lib/version.cjs
