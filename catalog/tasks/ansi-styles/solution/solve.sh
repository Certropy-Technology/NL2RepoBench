#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REVISION="c1c3dd4e017a2938807aaff0d361f46d086aeab7"
SOURCE_ARCHIVE_SHA256="80fa2b7b4faa2668694c75de5cce44e8b46fa897d31f86d90e3e4dd526c2e120"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ARCHIVE="/tmp/ansi-styles-${UPSTREAM_REVISION}.tar.gz"

# Only the trusted Oracle receives the source-host allowlist. Download the
# immutable commit archive, verify its bytes, and use its implementation files.
/usr/local/bin/node --input-type=module - "$UPSTREAM_REVISION" "$SOURCE_ARCHIVE" <<'JS'
import {createWriteStream} from 'node:fs';
import {once} from 'node:events';
import {request} from 'node:https';
const revision = process.argv[2];
const destination = process.argv[3];
const url = `https://codeload.github.com/chalk/ansi-styles/tar.gz/${revision}`;
async function download(currentUrl, depth = 0) {
  if (depth > 2) throw new Error('source endpoint redirected too many times');
  const response = await new Promise((resolve, reject) => {
    const req = request(currentUrl, {headers: {'user-agent': 'nl2repobench-oracle'}}, resolve);
    req.on('error', reject);
    req.end();
  });
  if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
    response.resume();
    return download(new URL(response.headers.location, currentUrl), depth + 1);
  }
  if (response.statusCode < 200 || response.statusCode >= 300) {
    throw new Error(`source endpoint returned HTTP ${response.statusCode}`);
  }
  const file = createWriteStream(destination, {flags: 'w', mode: 0o600});
  response.pipe(file);
  await once(file, 'finish');
}
await download(url);
JS
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

SOURCE_ROOT="/tmp/ansi-styles-source-${UPSTREAM_REVISION}"
rm -rf "$SOURCE_ROOT"
mkdir -p "$SOURCE_ROOT"
tar -xzf "$SOURCE_ARCHIVE" -C "$SOURCE_ROOT"
SOURCE_DIR="$SOURCE_ROOT/ansi-styles-${UPSTREAM_REVISION}"
test -f "$SOURCE_DIR/package.json"
test "$(node -p 'JSON.parse(require("fs").readFileSync(process.argv[1])).version' "$SOURCE_DIR/package.json")" = "7.0.0"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp "$SOURCE_DIR/index.js" /workspace/index.js
cp "$SOURCE_DIR/index.d.ts" /workspace/index.d.ts
cp "$SOURCE_DIR/license" /workspace/license
cp "$SOURCE_DIR/readme.md" /workspace/readme.md
cp "$SCRIPT_DIR/oracle-package/package.json" /workspace/package.json
cp "$SCRIPT_DIR/oracle-package/package-lock.json" /workspace/package-lock.json
