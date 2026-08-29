#!/usr/bin/env bash
set -euo pipefail

upstream_url='https://github.com/syntax-tree/mdast-util-phrasing'
revision='67d563d643f75cf4fd26bc3121ddebb89e3a0a9c'
archive_sha256='fe71915a39869c97b9a9132886ff511654b42d4109183853592b580db458650b'
package_sha256='c020a54303d9d422c9def6ba5416db74c0f30b2783f2a84b7248b0d61c2ac113'
temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

git -C "$temporary" init --quiet
git -C "$temporary" remote add origin "$upstream_url"
git -C "$temporary" fetch --quiet --depth=1 origin "$revision"
resolved="$(git -C "$temporary" rev-parse FETCH_HEAD)"
test "$resolved" = "$revision"
git -C "$temporary" archive --format=tar "$resolved" > "$temporary/source.tar"
printf '%s  %s\n' "$archive_sha256" "$temporary/source.tar" | sha256sum --check --strict
mkdir "$temporary/source"
tar -xf "$temporary/source.tar" -C "$temporary/source"
printf '%s  %s\n' "$package_sha256" "$temporary/source/package.json" | sha256sum --check --strict

rm -rf -- /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cp -a "$temporary/source/index.js" "$temporary/source/lib" "$temporary/source/license" /workspace/
cp -a "$temporary/source/package.json" /workspace/package.json
cp -a "$here/package-lock.json" /workspace/package-lock.json

node <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs'

const path = '/workspace/package.json'
const packageJson = JSON.parse(readFileSync(path, 'utf8'))
delete packageJson.devDependencies
delete packageJson.scripts
packageJson.dependencies = {
  '@types/mdast': '4.0.4',
  'unist-util-is': '6.0.1'
}
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`)
NODE

test "$(node -p "require('/workspace/package.json').name")" = 'mdast-util-phrasing'
test "$(node -p "require('/workspace/package.json').version")" = '4.1.0'
test "$(node -p "require('/workspace/package.json').license")" = 'MIT'
