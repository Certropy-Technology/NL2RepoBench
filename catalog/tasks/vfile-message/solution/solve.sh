#!/usr/bin/env bash
set -euo pipefail

readonly expected_revision='2c782c8580c5b0a14baae19fa8badc628e567461'
readonly expected_source_sha='6045e2d83f208d8f3219be4840792fdaf29f128071bd2a796d22849c2b2eca02'
readonly archive='/solution/source.tar'

test "$(sha256sum "$archive" | awk '{print $1}')" = "$expected_source_sha"
rm -rf /tmp/vfm-source /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /tmp/vfm-source
tar -xf "$archive" -C /tmp/vfm-source
cp -a /tmp/vfm-source/vfile-message/. /workspace/
test -f /workspace/package.json
node --input-type=module <<'JS'
import {readFile, rm, writeFile} from 'node:fs/promises'
const packagePath = '/workspace/package.json'
const packageJson = JSON.parse(await readFile(packagePath, 'utf8'))
if (packageJson.name !== 'vfile-message' || packageJson.version !== '4.0.3') throw new Error('frozen package identity mismatch')
delete packageJson.scripts
delete packageJson.devDependencies
delete packageJson.prettier
delete packageJson.remarkConfig
delete packageJson.xo
await writeFile(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`)
await rm('/workspace/.npmrc', {force: true})
JS
cp /solution/package-lock.json /workspace/package-lock.json
printf '%s\n' "$expected_revision" > /workspace/.nl2repobench-source-revision
npm ci --offline --ignore-scripts --no-audit --no-fund --cache /opt/npm-bundle/npm-cache --prefix /workspace
