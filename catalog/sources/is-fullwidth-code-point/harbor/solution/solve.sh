#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This script is uploaded only to the trusted
# Oracle run and is never present in the model agent image.
readonly UPSTREAM_URL="https://github.com/sindresorhus/is-fullwidth-code-point"
readonly UPSTREAM_REVISION="2696d873463fde9f6b09b49c98380bd49c67b00a"
readonly SOURCE_ARCHIVE_SHA256="fdc4bd52b082a3ac5654f92c8b6b1d50d4c105cb48b65930e2e40a7673a7fdd0"
readonly SOURCE_DIR="/tmp/is-fullwidth-code-point-source"
readonly SOURCE_ARCHIVE="/tmp/is-fullwidth-code-point-source.tar"
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

# The frozen package disables lockfile generation and declares a caret range.
# Oracle metadata is adapted to the private, exact npm closure used by the
# production candidate installer; implementation and declaration bytes remain
# from the verified source archive.
node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.funding;
packageJson.dependencies = {'get-east-asian-width': '1.6.0'};
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
      dependencies: {'get-east-asian-width': '1.6.0'},
    },
    'node_modules/get-east-asian-width': {
      version: '1.6.0',
      resolved: 'https://registry.npmjs.org/get-east-asian-width/-/get-east-asian-width-1.6.0.tgz',
      integrity: 'sha512-QRbvDIbx6YklUe6RxeTeleMR0yv3cYH6PsPZHcnVn7xv7zO1BHN8r0XETu8n6Ye3Q+ahtSarc3WgtNWmehIBfA==',
      engines: {node: '>=18'},
    },
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
