#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This file is materialized only for the
# trusted Oracle run, which receives a run-scoped github.com authorization.
readonly UPSTREAM_URL="https://github.com/npm/validate-npm-package-name"
readonly UPSTREAM_REVISION="f63469d58278635630681c2506f05176ff18a7cb"
readonly SOURCE_ARCHIVE_SHA256="9661772a73903963953effd89a95902ce3b5b4b82106c839ed3d6e938f4e8a79"
readonly SOURCE_DIR="/tmp/validate-npm-package-name-source"
readonly SOURCE_ARCHIVE="/tmp/validate-npm-package-name-source.tar"
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
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmrc" "$ROOT/test"

# The frozen source intentionally omits a package lock and has development-only
# scripts. Adapt only package metadata for the exact no-dependency offline
# candidate contract; implementation and builtin inventory bytes stay frozen.
node --input-type=commonjs <<'NODE'
const {readFileSync, writeFileSync} = require('node:fs');
const path = '/workspace/package.json';
const manifest = JSON.parse(readFileSync(path, 'utf8'));
delete manifest.devDependencies;
delete manifest.scripts;
delete manifest.templateOSS;
writeFileSync(path, `${JSON.stringify(manifest, null, 2)}\n`);
const lock = {
  name: manifest.name,
  version: manifest.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {name: manifest.name, version: manifest.version},
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
