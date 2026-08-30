#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This bundle is uploaded only to the trusted
# Oracle run and is not present in the model agent image.
readonly UPSTREAM_URL="https://github.com/syntax-tree/unist-util-is"
readonly UPSTREAM_REVISION="82b9c2547dfa52e6078a546ab5a1c64bb9381480"
readonly SOURCE_ARCHIVE_SHA256="e9136a0d23958fc6b29161c357dcbedf2e98d9478da87a9e77c2167a938403f4"
readonly SOURCE_DIR="/tmp/unist-util-is-source"
readonly SOURCE_ARCHIVE="/tmp/unist-util-is-source.tar"
readonly ROOT="/workspace"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" |
  sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf \
  "$ROOT/.github" \
  "$ROOT/.gitignore" \
  "$ROOT/.npmrc" \
  "$ROOT/.prettierignore" \
  "$ROOT/index.test-d.ts" \
  "$ROOT/test" \
  "$ROOT/tsconfig.json"

install -m 0644 "$SCRIPT_DIR/generated/index.d.ts" "$ROOT/index.d.ts"
install -m 0644 "$SCRIPT_DIR/generated/index.d.ts.map" "$ROOT/index.d.ts.map"
install -m 0644 "$SCRIPT_DIR/generated/lib/index.d.ts" "$ROOT/lib/index.d.ts"
install -m 0644 "$SCRIPT_DIR/generated/lib/index.d.ts.map" "$ROOT/lib/index.d.ts.map"
(
  cd "$ROOT"
  printf '%s  %s\n' \
    "587d1eae1651738f8949926b88aa9a7622d81cb2fb61c5e17e38ada1ff09df3a" \
    "index.d.ts" \
    "f34f15b78a5b63e39dfd62fe3983ac43c90d45876cfc5b79278e0316db07adf0" \
    "index.d.ts.map" \
    "7552ee3d893814ec478960b5ba7e08d1dc0c64ddc6d00760bc454ee2697eba41" \
    "lib/index.d.ts" \
    "08204e9d5e9b716742fe91fca47ba619b82a3772f7d5324ddb3170933f653584" \
    "lib/index.d.ts.map" |
    sha256sum --check --strict
)

node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs'

const packagePath = '/workspace/package.json'
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'))
delete packageJson.devDependencies
delete packageJson.funding
delete packageJson.scripts
packageJson.dependencies = {'@types/unist': '3.0.3'}
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`)

const lock = {
  name: 'unist-util-is',
  version: '6.0.1',
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: 'unist-util-is',
      version: '6.0.1',
      license: 'MIT',
      dependencies: {'@types/unist': '3.0.3'}
    },
    'node_modules/@types/unist': {
      version: '3.0.3',
      resolved: 'https://registry.npmjs.org/@types/unist/-/unist-3.0.3.tgz',
      integrity: 'sha512-ko/gIFJRv177XgZsZcBwnqJN5x/Gien8qNOn0D5bQU/zAzVf9Zt3BlcUiLqhV9y4ARk0GbT3tnUiPNgnTXzc/Q==',
      license: 'MIT'
    }
  }
}
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`)
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
