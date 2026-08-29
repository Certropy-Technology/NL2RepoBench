#!/usr/bin/env bash
set -euo pipefail

ref=/tmp/fast-string-width-reference
rm -rf "$ref"
git init -q "$ref"
git -C "$ref" remote add origin https://github.com/fabiospampinato/fast-string-width
git -C "$ref" fetch --depth=1 origin f49e7b7662906e0028a68a16b5358500b2f3152d
test "$(git -C "$ref" rev-parse FETCH_HEAD)" = f49e7b7662906e0028a68a16b5358500b2f3152d
git -C "$ref" checkout -q --detach FETCH_HEAD

mkdir -p /workspace/dist
node --input-type=module - "$ref" <<'JS'
import {readFileSync, writeFileSync} from 'node:fs';
const ref = process.argv[2];
const source = JSON.parse(readFileSync(`${ref}/package.json`, 'utf8'));
const pkg = {
  name: source.name,
  version: source.version,
  type: source.type,
  main: source.main,
  exports: source.exports,
  types: source.types,
  license: source.license,
  dependencies: source.dependencies,
};
writeFileSync('/workspace/package.json', `${JSON.stringify(pkg)}\n`);
JS

# The fetched revision's source is a deliberately small TypeScript wrapper;
# materialize its equivalent runtime entry point without requiring dev-only
# compiler packages in the trusted Oracle image.
cat > /workspace/dist/index.js <<'JS'
import fastStringTruncatedWidth from 'fast-string-truncated-width';
const NO_TRUNCATION = {limit: Infinity, ellipsis: '', ellipsisWidth: 0};
const fastStringWidth = (input, options = {}) =>
  fastStringTruncatedWidth(input, NO_TRUNCATION, options).width;
export default fastStringWidth;
JS
printf '%s\n' 'declare const fastStringWidth: (input: string, options?: Record<string, number>) => number;' \
  'export default fastStringWidth;' > /workspace/dist/index.d.ts
cp "$ref/license" /workspace/license
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
cp "$script_dir/oracle-package-lock.json" /workspace/package-lock.json
