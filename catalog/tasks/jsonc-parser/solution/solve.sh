#!/usr/bin/env bash
set -euo pipefail

SOURCE_ARCHIVE=/solution/source.tar
DISTRIBUTION_ARCHIVE=/solution/distribution.tar
EXPECTED_SOURCE_SHA256=4d9fef513a7d3543b79aa9965ffe967cede24c3b675037e44374123589a2ad9b
EXPECTED_DISTRIBUTION_SHA256=99ecb53a34efa2cc74f71a0907eb732215c16a5741f733183fab715625f44260

test "$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')" = "$EXPECTED_SOURCE_SHA256"
test "$(sha256sum "$DISTRIBUTION_ARCHIVE" | awk '{print $1}')" = "$EXPECTED_DISTRIBUTION_SHA256"
rm -rf /tmp/jsonc-parser-source
mkdir -p /tmp/jsonc-parser-source
tar -xf "$SOURCE_ARCHIVE" -C /tmp/jsonc-parser-source
node - <<'NODE'
const fs = require('node:fs');
const source = JSON.parse(fs.readFileSync('/tmp/jsonc-parser-source/package.json', 'utf8'));
if (source.name !== 'jsonc-parser' || source.version !== '4.0.0-next.2' || source.license !== 'MIT') process.exit(1);
NODE
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf "$DISTRIBUTION_ARCHIVE" -C /workspace
node - <<'NODE'
const fs = require('node:fs');
const manifest = JSON.parse(fs.readFileSync('/workspace/package.json', 'utf8'));
const lock = JSON.parse(fs.readFileSync('/workspace/package-lock.json', 'utf8'));
if (manifest.name !== 'jsonc-parser' || manifest.version !== '4.0.0-next.2' || manifest.type !== 'module') process.exit(1);
if (Object.hasOwn(manifest, 'scripts') || Object.keys(manifest.dependencies || {}).length || Object.keys(manifest.devDependencies || {}).length) process.exit(1);
if (lock.lockfileVersion !== 3 || Object.keys(lock.packages || {}).join('') !== '') process.exit(1);
NODE
if find /workspace -type f \( -name '*.map' -o -path '*/test/*' -o -path '*/src/*' \) | grep -q .; then
  echo 'non-distribution file in Oracle workspace' >&2
  exit 1
fi
