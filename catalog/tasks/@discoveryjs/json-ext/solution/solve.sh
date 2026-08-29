#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/discoveryjs/json-ext"
UPSTREAM_REVISION="457d4d9d4e55bb1e14fde192715114b80e20c4c9"
SOURCE_ARCHIVE_SHA256="dbc66fd6d20e59d441667a70b99d11d1f96a50d24ee2b43479db882070531894"
SOURCE_DIR="/tmp/json-ext-source"
SOURCE_ARCHIVE="/tmp/json-ext-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD

resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
  echo "unexpected source revision: $resolved_revision" >&2
  exit 1
fi

git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

node - "$SOURCE_DIR" <<'NODE'
const fs = require("node:fs");
const root = process.argv[2];
const manifest = JSON.parse(fs.readFileSync(`${root}/package.json`, "utf8"));
if (manifest.name !== "@discoveryjs/json-ext" || manifest.version !== "1.1.0" || manifest.license !== "MIT") process.exit(1);
if (!fs.readFileSync(`${root}/LICENSE`, "utf8").includes("MIT License")) process.exit(1);
NODE

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src
cp "$SOURCE_DIR"/src/{index.js,parse-chunked.js,stringify-chunked.js,stringify-info.js,utils.js,web-streams.js} /workspace/src/
cp "$SOURCE_DIR/index.d.ts" "$SOURCE_DIR/LICENSE" /workspace/

cat > /workspace/package.json <<'JSON'
{
  "name": "@discoveryjs/json-ext",
  "version": "1.1.0",
  "type": "module",
  "main": "./src/index.js",
  "module": "./src/index.js",
  "types": "./index.d.ts",
  "exports": {
    ".": {
      "types": "./index.d.ts",
      "import": "./src/index.js"
    },
    "./package.json": "./package.json"
  },
  "files": [
    "src",
    "index.d.ts",
    "LICENSE"
  ],
  "engines": {
    "node": ">=14.17.0"
  },
  "license": "MIT"
}
JSON

cat > /workspace/package-lock.json <<'JSON'
{
  "name": "@discoveryjs/json-ext",
  "version": "1.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "@discoveryjs/json-ext",
      "version": "1.1.0",
      "license": "MIT",
      "engines": {
        "node": ">=14.17.0"
      }
    }
  }
}
JSON

node - <<'NODE'
const fs = require("node:fs");
const manifest = JSON.parse(fs.readFileSync("/workspace/package.json", "utf8"));
const lock = JSON.parse(fs.readFileSync("/workspace/package-lock.json", "utf8"));
if (manifest.name !== "@discoveryjs/json-ext" || manifest.version !== "1.1.0" || manifest.type !== "module") process.exit(1);
if (Object.hasOwn(manifest, "scripts") || Object.hasOwn(manifest, "dependencies") || Object.hasOwn(manifest, "devDependencies")) process.exit(1);
if (lock.lockfileVersion !== 3 || Object.keys(lock.packages || {}).join("") !== "") process.exit(1);
NODE
