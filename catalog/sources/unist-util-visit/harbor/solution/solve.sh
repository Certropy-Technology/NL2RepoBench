#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/syntax-tree/unist-util-visit"
readonly UPSTREAM_REVISION="5d601df684ca7341646d6b57eb0f20fdfe277bc2"
readonly SOURCE_ARCHIVE_SHA256="d59ced4aa115b1ba3769a58fa82ffed6ea6f2b06cecc80cc846504399b1367ab"
readonly SOURCE_DIR="/tmp/unist-util-visit-source"
readonly SOURCE_ARCHIVE="/tmp/unist-util-visit-source.tar"
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
import {readFileSync, writeFileSync} from 'node:fs'
const root = '/workspace'
const packageJson = JSON.parse(readFileSync(`${root}/package.json`, 'utf8'))
delete packageJson.devDependencies
delete packageJson.scripts
delete packageJson.funding
packageJson.dependencies = {
  '@types/unist': '3.0.3',
  'unist-util-is': '6.0.0',
  'unist-util-visit-parents': '6.0.2'
}
packageJson.files = ['lib/', 'index.d.ts', 'index.js', 'adapter.mjs']
writeFileSync(`${root}/package.json`, `${JSON.stringify(packageJson, null, 2)}\n`)
NODE

cat > "$ROOT/adapter.mjs" <<'NODE'
import {readFileSync} from 'node:fs'
import {CONTINUE, EXIT, SKIP, visit} from './index.js'

const request = JSON.parse(readFileSync(0, 'utf8'))
const tree = structuredClone(request.tree)
const visits = []
let calls = 0
let restartCount = 0
let restarted = false
const predicate = typeof request.predicateIndexAtLeast === 'number'
  ? (_node, index) => typeof index === 'number' && index >= request.predicateIndexAtLeast
  : undefined
const test = predicate ?? request.test
const visitor = (node, index, parent) => {
  calls += 1
  const record = {type: node.type}
  if (typeof index === 'number') record.index = index
  if (parent && typeof parent.type === 'string') record.parentType = parent.type
  visits.push(record)
  if (request.markVisited) node.marked = true
  if (typeof request.exitAfter === 'number' && calls >= request.exitAfter) return EXIT
  if (request.skipType === node.type) return SKIP
  if (request.restartOnceType === node.type && !restarted) {
    restarted = true
    restartCount += 1
    return 0
  }
  if (request.jumpAtType === node.type) return [CONTINUE, request.jumpIndex]
  if (request.mode === 'undefined') return undefined
  return CONTINUE
}

const reverse = request.reverse === true
if (test === undefined) visit(tree, visitor, reverse)
else visit(tree, test, visitor, reverse)
process.stdout.write(`${JSON.stringify({ok: true, exports: ['CONTINUE', 'EXIT', 'SKIP'], visits, calls, restartCount, tree})}\n`)
NODE

cat > "$ROOT/package-lock.json" <<'JSON'
{
  "name": "unist-util-visit",
  "version": "5.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "unist-util-visit",
      "version": "5.1.0",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "3.0.3",
        "unist-util-is": "6.0.0",
        "unist-util-visit-parents": "6.0.2"
      }
    },
    "node_modules/@types/unist": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/@types/unist/-/unist-3.0.3.tgz",
      "integrity": "sha512-ko/gIFJRv177XgZsZcBwnqJN5x/Gien8qNOn0D5bQU/zAzVf9Zt3BlcUiLqhV9y4ARk0GbT3tnUiPNgnTXzc/Q==",
      "license": "MIT"
    },
    "node_modules/unist-util-is": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/unist-util-is/-/unist-util-is-6.0.0.tgz",
      "integrity": "sha512-2qCTHimwdxLfz+YzdGfkqNlH0tLi9xjTnHddPmJwtIG9MGsdbutfTc4P+haPD7l7Cjxf/WZj+we5qfVPvvxfYw==",
      "license": "MIT",
      "dependencies": {"@types/unist": "^3.0.0"}
    },
    "node_modules/unist-util-visit-parents": {
      "version": "6.0.2",
      "resolved": "https://registry.npmjs.org/unist-util-visit-parents/-/unist-util-visit-parents-6.0.2.tgz",
      "integrity": "sha512-goh1s1TBrqSqukSc8wrjwWhL0hiJxgA8m4kFxGlQ+8FYQ3C/m11FcTs4YYem7V664AhHVvgoQLk890Ssdsr2IQ==",
      "license": "MIT",
      "dependencies": {"@types/unist": "^3.0.0", "unist-util-is": "^6.0.0"}
    }
  }
}
JSON

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
