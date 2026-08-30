#!/usr/bin/env bash
set -euo pipefail

# Uploaded only to the trusted Oracle run. The model Agent never receives this
# script or the run-scoped source-host authorization.
readonly UPSTREAM_URL="https://github.com/sindresorhus/strip-indent"
readonly UPSTREAM_REVISION="102b553f9efaec1c2451cd9ac2385269768f1fed"
readonly SOURCE_ARCHIVE_SHA256="9a3784a247647b173270b316dbd024f6a267e8eea6cb23dcaf5fb0339ba6e4dd"
readonly SOURCE_DIR="/tmp/strip-indent-source"
readonly SOURCE_ARCHIVE="/tmp/strip-indent-source.tar"
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
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmrc" "$ROOT/index.test-d.ts" "$ROOT/test.js"

node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.funding;
delete packageJson.xo;
packageJson.dependencies = {};
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);
const lock = {
  name: packageJson.name,
  version: packageJson.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: packageJson.name,
      version: packageJson.version,
    },
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
