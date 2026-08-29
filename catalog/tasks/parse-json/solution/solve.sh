#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/sindresorhus/parse-json"
UPSTREAM_REVISION="6fee59751db59a539fdf53537101a1d7c6378a65"
SOURCE_ARCHIVE_SHA256="afd0b4abb4fe0d8f93ca78a7a79e338ad6be4fb428a889b5227656ce7c43e8ad"
FETCH_ROOT=/tmp/parse-json-oracle-source
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
npm install --package-lock-only --package-lock=true --ignore-scripts --no-audit --no-fund
