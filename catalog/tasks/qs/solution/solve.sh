#!/usr/bin/env bash
set -euo pipefail

SOURCE_ARCHIVE=/solution/source.tar
EXPECTED_SHA256=f5bb4b5c13cb29aba6441d5781bb17de37b473f74aec203898b28f980ff95402
test "$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')" = "$EXPECTED_SHA256"
rm -rf /tmp/qs-source
mkdir -p /tmp/qs-source
tar -xf "$SOURCE_ARCHIVE" -C /tmp/qs-source
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp -a /tmp/qs-source/. /workspace/
rm -rf /workspace/.git /workspace/test /workspace/dist
rm -f /workspace/.npmrc /workspace/README.md /workspace/CHANGELOG.md
cp /solution/package-lock.json /workspace/package-lock.json
node - <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const packageJson = JSON.parse(fs.readFileSync(path, 'utf8'));
delete packageJson.scripts;
delete packageJson.devDependencies;
delete packageJson.publishConfig;
fs.writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);
NODE
