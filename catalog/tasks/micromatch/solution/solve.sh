#!/usr/bin/env bash
set -euo pipefail

SOURCE_ARCHIVE_SHA256=cfb37abf1f9134a4160f8db24574d537d533b217c9708047c995dd3d346d6239
SOURCE_ARCHIVE=/solution/source.tar

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf "$SOURCE_ARCHIVE" -C /workspace
rm -rf /workspace/.git /workspace/.github /workspace/test
rm -f /workspace/.npmrc /workspace/README.md /workspace/CHANGELOG.md
cp /solution/package-lock.json /workspace/package-lock.json
node - <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const packageJson = JSON.parse(fs.readFileSync(path, 'utf8'));
packageJson.dependencies = { braces: '3.0.3', picomatch: '2.3.1' };
delete packageJson.scripts;
delete packageJson.devDependencies;
delete packageJson.publishConfig;
fs.writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);
NODE
