#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ARCHIVE="$SCRIPT_DIR/source.tar"
PACKAGE_ARCHIVE="$SCRIPT_DIR/zod-4.4.3-exact.tgz"
LOCKFILE="$SCRIPT_DIR/package-lock.json"
WORKSPACE="/workspace"

printf '%s  %s\n' \
  '8d4a60e45991c6d3ca3884f0bc449a8b8229cb6af0eafcf095656037fdc81a5b' \
  "$SOURCE_ARCHIVE" | sha256sum --check --strict
printf '%s  %s\n' \
  'd9c8f500e05ab6d35d1efd0783eb1a4722416ac028924cf39d146c402a947d8c' \
  "$PACKAGE_ARCHIVE" | sha256sum --check --strict

SOURCE_DIR="$(mktemp -d)"
trap 'rm -rf -- "$SOURCE_DIR"' EXIT
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_DIR"
node -e '
  const source = require(process.argv[1]);
  if (source.name !== "zod" || source.version !== "4.4.3" || source.license !== "MIT") process.exit(1);
' "$SOURCE_DIR/packages/zod/package.json"

find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xzf "$PACKAGE_ARCHIVE" --strip-components=1 -C "$WORKSPACE"
cp "$LOCKFILE" "$WORKSPACE/package-lock.json"
node -e '
  const fs = require("node:fs");
  const path = process.argv[1];
  const built = require(path);
  if (built.name !== "zod" || built.version !== "4.4.3" || built.type !== "module") process.exit(1);
  if (built.dependencies || built.devDependencies || built.workspaces) process.exit(1);
  delete built.scripts;
  fs.writeFileSync(path, `${JSON.stringify(built, null, 2)}\n`);
' "$WORKSPACE/package.json"
