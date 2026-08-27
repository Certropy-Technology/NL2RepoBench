#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source materialization. The exact git archive is
# carried in the private Oracle bundle, verified before use, and never enters
# the model Agent image.
UPSTREAM_REVISION="84a9f3b9a4f3244b8c8e818f557d64c7b964fb25"
SOURCE_ARCHIVE_SHA256="c5d3d80a6b3f09d0e35e5a4b1bc78cb47216190b4b46f745f96c63fe16f1a0eb"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
SOURCE_ARCHIVE="$SCRIPT_DIR/source.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# The evaluation slice deliberately uses the production runtime closure only;
# development tools and lifecycle hooks never enter the candidate workspace.
node - <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const source = JSON.parse(fs.readFileSync(path, 'utf8'));
const dependencies = {
  'follow-redirects': '1.16.0',
  'form-data': '4.0.6',
  'https-proxy-agent': '5.0.1',
  'proxy-from-env': '2.1.0',
};
const candidate = {
  name: source.name,
  version: source.version,
  description: source.description,
  type: 'module',
  main: './index.js',
  module: './index.js',
  exports: source.exports,
  files: ['index.js', 'index.d.ts', 'index.d.cts', 'lib/'],
  dependencies,
};
fs.writeFileSync(path, JSON.stringify(candidate, null, 2) + '\n');
NODE
cp "$SCRIPT_DIR/package-lock.json" /workspace/package-lock.json
rm -rf /workspace/.git /workspace/.github /workspace/node_modules
