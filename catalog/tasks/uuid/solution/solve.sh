#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
(cd "$SCRIPT_DIR" && sha256sum -c source.tar.sha256)
(cd "$SCRIPT_DIR" && sha256sum -c runtime.tar.sha256)
(cd "$SCRIPT_DIR" && sha512sum -c npm-release.tgz.sha512)
grep -Fx 'source_revision=fd59f0277549d22cc7ec00a7b3b5c9bccb4d3c1d' "$SCRIPT_DIR/provenance.txt" >/dev/null
grep -Fx 'source_digest=sha256:fbf7e9c3a1bd5132ab04286855533c2b5f1607c1f97e1878cd568c41d58bdda8' "$SCRIPT_DIR/provenance.txt" >/dev/null
grep -Fx 'npm_package_git_head=fd59f0277549d22cc7ec00a7b3b5c9bccb4d3c1d' "$SCRIPT_DIR/provenance.txt" >/dev/null
grep -Fx 'runtime_manifest_policy=development_lifecycle_scripts_removed' "$SCRIPT_DIR/provenance.txt" >/dev/null

staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT
tar -xf "$SCRIPT_DIR/runtime.tar" -C "$staging"
/usr/local/bin/node -e '
  const fs = require("node:fs");
  const path = process.argv[1];
  const manifest = require(path);
  if (manifest.name !== "uuid" || manifest.version !== "14.0.2") process.exit(1);
  if (manifest.type !== "module") process.exit(3);
  if (manifest.exports?.["."]?.node?.default !== "./dist-node/index.js") process.exit(4);
  delete manifest.scripts;
  delete manifest.devDependencies;
  delete manifest.optionalDevDependencies;
  delete manifest.packageManager;
  delete manifest.lintStaged;
  delete manifest.commitlint;
  delete manifest["standard-version"];
  fs.writeFileSync(path, JSON.stringify(manifest, null, 2) + "\n");
' "$staging/package/package.json"
cp -a "$staging/package/." "$PWD/"
test -f package.json
test -f package-lock.json
