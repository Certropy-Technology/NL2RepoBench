#!/usr/bin/env bash
set -euo pipefail

revision='774a70c6bae6dd94486d3385dbd9a0f14550b709'
archive_sha256='ffbc51c1237344db6b47db8000aaa1668e89eb207f6a94b3a5b6472d5dda08d1'
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
script_root=$(cd -- "$(dirname -- "$0")" && pwd)

git -C "$temporary" init -q source
git -C "$temporary/source" remote add origin https://github.com/micromark/micromark.git
git -C "$temporary/source" fetch -q --depth=1 origin "$revision"
test "$(git -C "$temporary/source" rev-parse FETCH_HEAD)" = "$revision"
git -C "$temporary/source" checkout -q --detach "$revision"
git -C "$temporary/source" archive --format=tar --output="$temporary/source.tar" HEAD
echo "$archive_sha256  $temporary/source.tar" | sha256sum --check --status

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp -a "$temporary/source/packages/micromark-util-character/." /workspace/
cp "$script_root/reference/index.js" /workspace/index.js
cp "$script_root/reference/index.d.ts" /workspace/index.d.ts
cp "$script_root/reference/index.d.ts.map" /workspace/index.d.ts.map

node <<'JS'
import {readFileSync, writeFileSync} from 'node:fs'

const path = '/workspace/package.json'
const packageJson = JSON.parse(readFileSync(path, 'utf8'))
packageJson.types = './index.d.ts'
packageJson.dependencies = {
  'micromark-util-symbol': '2.0.1',
  'micromark-util-types': '2.0.2'
}
delete packageJson.scripts
writeFileSync(path, JSON.stringify(packageJson, null, 2) + '\n')
JS

cat > /workspace/package-lock.json <<'JSON'
{
  "name": "micromark-util-character",
  "version": "2.1.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "micromark-util-character",
      "version": "2.1.1",
      "dependencies": {
        "micromark-util-symbol": "2.0.1",
        "micromark-util-types": "2.0.2"
      }
    },
    "node_modules/micromark-util-symbol": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-symbol/-/micromark-util-symbol-2.0.1.tgz",
      "integrity": "sha512-vs5t8Apaud9N28kgCrRUdEed4UJ+wWNvicHLPxCa9ENlYuAY31M0ETy5y1vA33YoNPDFTghEbnh6efaE8h4x0Q=="
    },
    "node_modules/micromark-util-types": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/micromark-util-types/-/micromark-util-types-2.0.2.tgz",
      "integrity": "sha512-Yw0ECSpJoViF1qTU4DC6NwtC4aWGt1EkzaQB8KPPyCRR8z9TWeV0HbEFGTO+ZY1wB22zmxnJqhPyTpOVCpeHTA=="
    }
  }
}
JSON
