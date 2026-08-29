#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/chalk/slice-ansi"
readonly UPSTREAM_REVISION="50fc7781f5dd4d1421dbe061822d815708831af4"
readonly SOURCE_ARCHIVE_SHA256="178ba29b83709711b44e533074d5b8c5c16ecb79b60956ae965b6b15d724b402"
readonly SOURCE_DIR="/tmp/slice-ansi-source"
readonly SOURCE_ARCHIVE="/tmp/slice-ansi-source.tar"
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
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmrc" "$ROOT/test.js"

node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';

const packagePath = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
delete packageJson.funding;
packageJson.dependencies = {
  'ansi-styles': '6.2.3',
  'is-fullwidth-code-point': '5.1.0',
};
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);

const lock = {
  name: 'slice-ansi',
  version: '9.0.0',
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: 'slice-ansi',
      version: '9.0.0',
      dependencies: {
        'ansi-styles': '6.2.3',
        'is-fullwidth-code-point': '5.1.0',
      },
    },
    'node_modules/ansi-styles': {
      version: '6.2.3',
      resolved: 'https://registry.npmjs.org/ansi-styles/-/ansi-styles-6.2.3.tgz',
      integrity: 'sha512-4Dj6M28JB+oAH8kFkTLUo+a2jwOFkuqb3yucU0CANcRRUbxS0cP0nZYCGjcc3BNXwRIsUVmDGgzawme7zvJHvg==',
      engines: {node: '>=12'},
    },
    'node_modules/get-east-asian-width': {
      version: '1.6.0',
      resolved: 'https://registry.npmjs.org/get-east-asian-width/-/get-east-asian-width-1.6.0.tgz',
      integrity: 'sha512-QRbvDIbx6YklUe6RxeTeleMR0yv3cYH6PsPZHcnVn7xv7zO1BHN8r0XETu8n6Ye3Q+ahtSarc3WgtNWmehIBfA==',
      engines: {node: '>=18'},
    },
    'node_modules/is-fullwidth-code-point': {
      version: '5.1.0',
      resolved: 'https://registry.npmjs.org/is-fullwidth-code-point/-/is-fullwidth-code-point-5.1.0.tgz',
      integrity: 'sha512-5XHYaSyiqADb4RnZ1Bdad6cPp8Toise4TzEjcOYDHZkTCbKgiUl7WTUCpNWHuxmDt91wnsZBc9xinNzopv3JMQ==',
      dependencies: {'get-east-asian-width': '^1.3.1'},
      engines: {node: '>=18'},
    },
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
