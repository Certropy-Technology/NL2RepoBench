#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. The model Agent never receives this script or
# the source-host authorization used by the trusted Oracle run.
readonly UPSTREAM_URL="https://github.com/NaturalIntelligence/strnum"
readonly UPSTREAM_REVISION="117d6a5f59fbb8f29d2f88c0c292d7dc44d67a7f"
readonly SOURCE_ARCHIVE_SHA256="af9a609e1a8e3ded71cb69e2362710a2dfbf51dfbff0d8755f8d205be9c05e04"
readonly SOURCE_DIR="/tmp/strnum-oracle-source"
readonly SOURCE_ARCHIVE="/tmp/strnum-oracle-source.tar"
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
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/algo.stflow" "$ROOT/node_modules"

# Keep only the exact runtime closure consumed by the offline candidate installer.
node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const packagePath = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.funding;
packageJson.dependencies = {anynum: '1.0.1'};
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);

const lock = {
  name: packageJson.name,
  version: packageJson.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: packageJson.name,
      version: packageJson.version,
      license: packageJson.license,
      dependencies: {anynum: '1.0.1'},
    },
    'node_modules/anynum': {
      version: '1.0.1',
      resolved: 'https://registry.npmjs.org/anynum/-/anynum-1.0.1.tgz',
      integrity: 'sha512-N6//FLET/tXYNM/F6ABca1oH6fWB+KlTt909Le28WMDBk8oaT4vY17DCrwg2MvmuqUKt3Ni4N5dGJ/EoBgcO6A==',
      license: 'MIT',
    },
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
