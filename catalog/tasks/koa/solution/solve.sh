#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/koajs/koa"
UPSTREAM_REVISION="9c202e0077f4e314795222aff1be0da0bf9b2493"
SOURCE_ARCHIVE_SHA256="069a16c6ea48c4d9e9f34fa31746c238c081fbce1f67cc99c85b75057faf5245"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SOURCE_ROOT="/workspace/.oracle-source"
SOURCE_DIR="$SOURCE_ROOT/repository"
SOURCE_ARCHIVE="$SOURCE_ROOT/source.tar"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p "$SOURCE_DIR"
git -C "$SOURCE_DIR" init -q
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse "$UPSTREAM_REVISION")"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -rf /workspace/node_modules
cp "$SCRIPT_DIR/runtime-package-lock.json" /workspace/package-lock.json
node <<'NODE'
const fs = require('node:fs')
const path = '/workspace/package.json'
const packageJson = JSON.parse(fs.readFileSync(path, 'utf8'))
delete packageJson.devDependencies
if (packageJson.scripts) delete packageJson.scripts.prepare
fs.writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`)
NODE
npm ci --offline --ignore-scripts --omit=dev --no-audit --no-fund --cache "$SCRIPT_DIR/npm-cache" --prefix /workspace
rm -rf "$SOURCE_ROOT"
