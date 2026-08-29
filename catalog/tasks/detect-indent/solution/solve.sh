#!/usr/bin/env bash
set -euo pipefail

revision='25d3cf12f54807147e56ac3d4f557c9cc7904c96'
expected_archive_sha='5a7f9c31bf38023fcedd859af6ad7e212c4267b45dc7b72dd3de7c6d6070dc2e'
repo='https://github.com/sindresorhus/detect-indent.git'
work='/tmp/detect-indent-oracle'
rm -rf "$work"
git init -q "$work"
git -C "$work" remote add origin "$repo"
git -C "$work" fetch --quiet --depth=1 origin "$revision"
actual_revision="$(git -C "$work" rev-parse FETCH_HEAD^{commit})"
test "$actual_revision" = "$revision"
git -C "$work" archive --format=tar "$actual_revision" > "$work/source.tar"
actual_archive_sha="$(sha256sum "$work/source.tar" | awk '{print $1}')"
test "$actual_archive_sha" = "$expected_archive_sha"
rm -rf /workspace/*
mkdir -p /workspace
tar -xf "$work/source.tar" -C /workspace
test -f /workspace/package.json
test -f /workspace/index.js
test "$(node -p "require('/workspace/package.json').version")" = '7.0.2'
node --input-type=module <<'JS'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const manifest = JSON.parse(readFileSync(path, 'utf8'));
delete manifest.devDependencies;
delete manifest.scripts;
writeFileSync(path, `${JSON.stringify(manifest, null, '\t')}\n`);
writeFileSync('/workspace/package-lock.json', `${JSON.stringify({
  name: manifest.name,
  version: manifest.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: manifest.name,
      version: manifest.version,
      license: manifest.license,
      type: manifest.type,
      engines: manifest.engines,
    },
  },
}, null, 2)}\n`);
JS
