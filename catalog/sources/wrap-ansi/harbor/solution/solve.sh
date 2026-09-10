#!/usr/bin/env bash
set -euo pipefail
revision='c6b6259a58843e491e8703c5010a2a517b5f5738'
source_digest='dccdb394d6c59a10e8f50aba2b8ebbbbf4f27a3a2d822e73a8fa9190934ccec6'
tmp="/tmp/wrap-ansi-source"
archive="/tmp/wrap-ansi-source.tar"
rm -rf "$tmp" "$archive"
git init -q "$tmp"
git -C "$tmp" remote add origin https://github.com/chalk/wrap-ansi.git
git -C "$tmp" fetch -q --depth 1 origin "$revision"
test "$(git -C "$tmp" rev-parse FETCH_HEAD^{commit})" = "$revision"
git -C "$tmp" archive --format=tar "$revision" > "$archive"
printf '%s  %s\n' "$source_digest" "$archive" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$archive" -C /workspace
rm -rf /workspace/.github /workspace/.git /workspace/.npmrc /workspace/index.test-d.ts /workspace/test.js

node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const packagePath = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
packageJson.dependencies = {'ansi-styles': '6.2.3', 'string-width': '8.2.0'};
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`);
const lock = {
  name: 'wrap-ansi', version: '10.0.1', lockfileVersion: 3, requires: true,
  packages: {
    '': {name: 'wrap-ansi', version: '10.0.1', dependencies: packageJson.dependencies},
    'node_modules/ansi-regex': {
      version: '6.3.0', resolved: 'https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.3.0.tgz',
      integrity: 'sha512-WpDfL7NO6j7tH88IDBNVdUJxDh9nmCteAVW9dsep846XdwF4naCBK+/tGLX3KJgcpgMRXCFlTM2hKGoK9FsdrQ==',
      license: 'MIT', engines: {node: '>=12'},
    },
    'node_modules/ansi-styles': {
      version: '6.2.3', resolved: 'https://registry.npmjs.org/ansi-styles/-/ansi-styles-6.2.3.tgz',
      integrity: 'sha512-4Dj6M28JB+oAH8kFkTLUo+a2jwOFkuqb3yucU0CANcRRUbxS0cP0nZYCGjcc3BNXwRIsUVmDGgzawme7zvJHvg==',
      license: 'MIT', engines: {node: '>=12'},
    },
    'node_modules/get-east-asian-width': {
      version: '1.6.0', resolved: 'https://registry.npmjs.org/get-east-asian-width/-/get-east-asian-width-1.6.0.tgz',
      integrity: 'sha512-QRbvDIbx6YklUe6RxeTeleMR0yv3cYH6PsPZHcnVn7xv7zO1BHN8r0XETu8n6Ye3Q+ahtSarc3WgtNWmehIBfA==',
      license: 'MIT', engines: {node: '>=18'},
    },
    'node_modules/string-width': {
      version: '8.2.0', resolved: 'https://registry.npmjs.org/string-width/-/string-width-8.2.0.tgz',
      integrity: 'sha512-6hJPQ8N0V0P3SNmP6h2J99RLuzrWz2gvT7VnK5tKvrNqJoyS9W4/Fb8mo31UiPvy00z7DQXkP2hnKBVav76thw==',
      license: 'MIT', dependencies: {'get-east-asian-width': '^1.5.0', 'strip-ansi': '^7.1.2'}, engines: {node: '>=20'},
    },
    'node_modules/strip-ansi': {
      version: '7.2.0', resolved: 'https://registry.npmjs.org/strip-ansi/-/strip-ansi-7.2.0.tgz',
      integrity: 'sha512-yDPMNjp4WyfYBkHnjIRLfca1i6KMyGCtsVgoKe/z1+6vukgaENdgGBZt+ZmKPc4gavvEZ5OgHfHdrazhgNyG7w==',
      license: 'MIT', dependencies: {'ansi-regex': '^6.2.2'}, engines: {node: '>=12'},
    },
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE
