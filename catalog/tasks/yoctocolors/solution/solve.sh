#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/sindresorhus/yoctocolors"
readonly UPSTREAM_REVISION="a02a16ec36fbd58a0848e95598fb4913c54c7591"
readonly SOURCE_ARCHIVE_SHA256="eae1cee24fce2d4242f126fcb614bd4d446c4390b2ee299674425cf35f69e640"
readonly SOURCE_DIR="/tmp/yoctocolors-source"
readonly SOURCE_ARCHIVE="/tmp/yoctocolors-source.tar"
readonly ROOT="/workspace"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmrc" \
  "$ROOT/benchmark.js" "$ROOT/example.js" "$ROOT/fixture.js" \
  "$ROOT/index.test-d.ts" "$ROOT/test.js"

# Preserve implementation/declaration bytes while adapting development-only
# metadata to the exact dependency-free production install contract.
node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.funding;
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);
const lock = {
  name: packageJson.name,
  version: packageJson.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {name: packageJson.name, version: packageJson.version},
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
