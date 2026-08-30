#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This bundle is uploaded only to the trusted
# Oracle run; it is not present in the model Agent image.
readonly UPSTREAM_URL="https://github.com/syntax-tree/unist-util-visit-parents"
readonly UPSTREAM_REVISION="f06035e9161f25119fb68d178167c30003d32dfb"
readonly SOURCE_ARCHIVE_SHA256="39843fba2b73f69a59ca59e06cf646ad20c2999f4c3e2ac75b427e80f8e5d066"
readonly SOURCE_DIR="/tmp/unist-util-visit-parents-source"
readonly SOURCE_ARCHIVE="/tmp/unist-util-visit-parents-source.tar"
readonly ROOT="/workspace"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

cd /
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmrc" \
  "$ROOT/index.test-d.ts" "$ROOT/test.js" "$ROOT/tsconfig.json"

node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs'

const path = '/workspace/package.json'
const packageJson = JSON.parse(readFileSync(path, 'utf8'))
delete packageJson.devDependencies
delete packageJson.scripts
delete packageJson.funding
packageJson.dependencies = {
  '@types/unist': '3.0.3',
  'unist-util-is': '6.0.1'
}
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`)
NODE

cp "$SCRIPT_DIR/package-lock.json" "$ROOT/package-lock.json"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
