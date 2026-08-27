#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference material. Neither archive enters the model image.
UPSTREAM_REVISION="89bda2cd8e9def2ea037e7dbffaf392ce9f1ddcb"
SOURCE_ARCHIVE_SHA256="1be81f7d2cd36f7539701f6f93f107bf28eccb31a8ade43de5fd8c55137983d6"
DIST_ARCHIVE_SHA256="37df5a29280332dd46528a358356d0038f0e754e4e444959cd65f4c39214a2be"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
SOURCE_ARCHIVE="$SCRIPT_DIR/source.tar"
DIST_ARCHIVE="$SCRIPT_DIR/dist.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
printf '%s  %s\n' "$DIST_ARCHIVE_SHA256" "$DIST_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
tar -xf "$DIST_ARCHIVE" -C /workspace

node - <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const source = JSON.parse(fs.readFileSync(path, 'utf8'));
const candidate = {
  name: 'rollup',
  version: '4.62.5',
  description: source.description,
  main: 'dist/rollup.js',
  module: 'dist/es/rollup.js',
  types: 'dist/rollup.d.ts',
  bin: {rollup: 'dist/bin/rollup'},
  files: [
    'dist/**/*.js',
    'dist/**/*.d.ts',
    'dist/bin/rollup',
    'dist/wasm-node/*.wasm',
  ],
  engines: {node: '>=18.0.0', npm: '>=8.0.0'},
  exports: {
    '.': {
      types: './dist/rollup.d.ts',
      import: './dist/es/rollup.js',
      require: './dist/rollup.js',
    },
    './loadConfigFile': {
      types: './dist/loadConfigFile.d.ts',
      require: './dist/loadConfigFile.js',
      default: './dist/loadConfigFile.js',
    },
    './getLogFilter': {
      types: './dist/getLogFilter.d.ts',
      import: './dist/es/getLogFilter.js',
      require: './dist/getLogFilter.js',
    },
    './parseAst': {
      types: './dist/parseAst.d.ts',
      import: './dist/es/parseAst.js',
      require: './dist/parseAst.js',
    },
    './dist/*': './dist/*',
    './package.json': './package.json',
  },
  sideEffects: false,
  license: 'MIT',
};
fs.writeFileSync(path, JSON.stringify(candidate, null, 2) + '\n');
NODE

cp "$SCRIPT_DIR/package-lock.json" /workspace/package-lock.json
find /workspace -mindepth 1 -maxdepth 1 \
  ! -name dist \
  ! -name package.json \
  ! -name package-lock.json \
  ! -name LICENSE.md \
  ! -name README.md \
  -exec rm -rf -- {} +
