#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/sindresorhus/get-stream"
readonly UPSTREAM_REVISION="cdbd77bebf332f28a2949613fc1534d8a7a04c95"
readonly SOURCE_ARCHIVE_SHA256="85c68c24e1216863eb41e79754b10b50dcdbf94137b2f0b7821f802fd7ec2a06"
readonly FETCH_ROOT="/tmp/get-stream-oracle-source"

rm -rf "$FETCH_ROOT"
git init -q "$FETCH_ROOT"
git -C "$FETCH_ROOT" remote add origin "$UPSTREAM_URL"
git -C "$FETCH_ROOT" fetch --quiet --no-tags --depth=1 origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$FETCH_ROOT/source.tar" -C /workspace
rm -rf /workspace/.github /workspace/benchmarks /workspace/test
rm -f /workspace/.npmrc
node --input-type=module <<'JS'
import {readFileSync, writeFileSync} from 'node:fs';
const packagePath = '/workspace/package.json';
const manifest = JSON.parse(readFileSync(packagePath, 'utf8'));
delete manifest.devDependencies;
delete manifest.scripts;
writeFileSync(packagePath, `${JSON.stringify(manifest, null, '\t')}\n`);
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
      dependencies: manifest.dependencies,
      engines: manifest.engines,
    },
    'node_modules/@sec-ant/readable-stream': {
      version: '0.6.1',
      resolved: 'https://registry.npmjs.org/@sec-ant/readable-stream/-/readable-stream-0.6.1.tgz',
      integrity: 'sha512-dr6XYxZdp5PU+dqnnfI2cNgzLv+YMu5F1RSZDkHIisysUBAqYwfrXz42HhFvGE5UTzaa/E8Nwl50zMCrjL18CQ==',
      license: 'MIT',
    },
    'node_modules/is-stream': {
      version: '4.0.1',
      resolved: 'https://registry.npmjs.org/is-stream/-/is-stream-4.0.1.tgz',
      integrity: 'sha512-Dnz92NInDqYckGEUJv689RbRiTSEHCQ7wOVeALbkOz999YpqT46yMRIGtSNl2iCL1waAZSx40+h59NV/EwzV/A==',
      license: 'MIT',
      engines: {node: '>=18'},
    },
  },
}, null, '\t')}\n`);
JS
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
