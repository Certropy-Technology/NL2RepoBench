#!/usr/bin/env bash
set -euo pipefail

SOURCE_ARCHIVE=/solution/source.tar
DISTRIBUTION_ARCHIVE=/solution/distribution.tar
EXPECTED_SOURCE_SHA256=822decf848e9ef50edeca8b0f5f2e595abc18e643634d316a1f8addb5499b672
EXPECTED_DISTRIBUTION_SHA256=bf49cf6ea26e49df9b4ca81dbb83e02aba6b97a6d8762fb0b3c31a4254c00cce

test "$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')" = "$EXPECTED_SOURCE_SHA256"
test "$(sha256sum "$DISTRIBUTION_ARCHIVE" | awk '{print $1}')" = "$EXPECTED_DISTRIBUTION_SHA256"

rm -rf /tmp/ramda-source
mkdir -p /tmp/ramda-source
tar -xf "$SOURCE_ARCHIVE" -C /tmp/ramda-source
node - <<'NODE'
const fs = require("node:fs");
const source = JSON.parse(fs.readFileSync("/tmp/ramda-source/package.json", "utf8"));
if (source.name !== "ramda" || source.version !== "0.32.0" || source.license !== "MIT") process.exit(1);
NODE

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf "$DISTRIBUTION_ARCHIVE" -C /workspace
node - <<'NODE'
const fs = require("node:fs");
const manifest = JSON.parse(fs.readFileSync("/workspace/package.json", "utf8"));
const lock = JSON.parse(fs.readFileSync("/workspace/package-lock.json", "utf8"));
if (manifest.name !== "ramda" || manifest.version !== "0.32.0" || manifest.main !== "./src/index.js") process.exit(1);
if (Object.keys(manifest.dependencies || {}).length || Object.keys(manifest.devDependencies || {}).length) process.exit(1);
if (lock.lockfileVersion !== 3 || Object.keys(lock.packages || {}).join("") !== "") process.exit(1);
NODE

if find /workspace -type f \( -path '*/test/*' -o -path '*/source/*' -o -name '*.map' \) | grep -q .; then
  echo "non-distribution file in Oracle workspace" >&2
  exit 1
fi
