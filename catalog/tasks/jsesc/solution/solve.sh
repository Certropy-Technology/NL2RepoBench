#!/usr/bin/env bash
set -euo pipefail
readonly REVISION='203c8694d605b6f29d4c67d372897499ec4468fb'
readonly SOURCE_DIGEST='2f611c6a89206ce324ec112596b7aef0f76a22ddf402fb1960ac11be15532cce'
readonly URL='https://github.com/mathiasbynens/jsesc'
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git -C "$tmp" init -q
git -C "$tmp" remote add origin "$URL"
git -C "$tmp" fetch --depth=1 origin "$REVISION"
test "$(git -C "$tmp" rev-parse FETCH_HEAD)" = "$REVISION"
git -C "$tmp" archive --format=tar "$REVISION" > "$tmp/source.tar"
test "$(sha256sum "$tmp/source.tar" | cut -d' ' -f1)" = "$SOURCE_DIGEST"
tar -xf "$tmp/source.tar" -C /workspace
rm -rf /workspace/.git
node - <<'NODE'
const fs = require('node:fs');
const packageJson = JSON.parse(fs.readFileSync('/workspace/package.json', 'utf8'));
const projected = {
  name: packageJson.name,
  version: packageJson.version,
  main: packageJson.main,
  bin: packageJson.bin,
  files: packageJson.files,
};
fs.writeFileSync('/workspace/package.json', `${JSON.stringify(projected)}\n`);
fs.writeFileSync('/workspace/package-lock.json', `${JSON.stringify({
  name: projected.name,
  version: projected.version,
  lockfileVersion: 3,
  requires: true,
  packages: {'': {name: projected.name, version: projected.version}},
})}\n`);
fs.appendFileSync('/workspace/jsesc.js', '\nmodule.exports.jsesc = module.exports;\n');
NODE
