#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/BridgeAR/safe-stable-stringify"
readonly UPSTREAM_REVISION="8a02137ac933eff57dd6e49beb9ee766fe8dd372"
readonly SOURCE_ARCHIVE_SHA256="a526d8d5397b73055d821b524f6ae6d2a356af1e9d04526a2b568c44ef883c35"
readonly SOURCE_DIR="/tmp/safe-stable-stringify-source"
readonly SOURCE_ARCHIVE="/tmp/safe-stable-stringify-source.tar"
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
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmignore" "$ROOT/benchmark.js" "$ROOT/compare.js" "$ROOT/test.js" "$ROOT/test.json" "$ROOT/tsconfig.json"

node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.repository;
delete packageJson.bugs;
delete packageJson.homepage;
packageJson.exports = {require: './index.js', import: './esm/wrapper.js'};
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);
const lock = {
  name: packageJson.name,
  version: packageJson.version,
  lockfileVersion: 3,
  requires: true,
  packages: {'': {name: packageJson.name, version: packageJson.version}}
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE
