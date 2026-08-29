#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/jshttp/range-parser"
UPSTREAM_REVISION="f4bf1736f28a3e574430408c18779cf7fbaf3770"
SOURCE_ARCHIVE_SHA256="cd4b795f1dd8fb3e4fab51a1cdfa276cbc8787d6d1aac19f0949de66da67da88"
FETCH_ROOT=/tmp/range-parser-oracle-source
rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C /workspace
cd /workspace
rm -f .npmrc
node --input-type=module -e 'import {readFile, writeFile} from "node:fs/promises"; const path="package.json"; const packageJson=JSON.parse(await readFile(path)); delete packageJson.devDependencies; delete packageJson.scripts; await writeFile(path, JSON.stringify(packageJson, null, 2)+"\n");'
npm install --package-lock-only --ignore-scripts --no-audit --no-fund
