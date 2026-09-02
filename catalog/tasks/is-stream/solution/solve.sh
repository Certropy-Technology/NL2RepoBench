#!/usr/bin/env bash
set -euo pipefail

REVISION="ab06c4acc9dce4dcadc9dfc6416e1be2c836862d"
ARCHIVE_SHA256="465680c19959fc1c1f85702de085b7118845e584ea797653f90c1130d550e3fd"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(mktemp -d)"
ARCHIVE="$(mktemp)"
trap 'rm -rf -- "$SOURCE_DIR" "$ARCHIVE"' EXIT

git -C "$SOURCE_DIR" init -q
git -C "$SOURCE_DIR" remote add origin https://github.com/sindresorhus/is-stream
git -C "$SOURCE_DIR" fetch --depth 1 origin "$REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)" = "$REVISION"
git -C "$SOURCE_DIR" checkout --detach -q FETCH_HEAD
test "$(git -C "$SOURCE_DIR" rev-parse HEAD)" = "$REVISION"
git -C "$SOURCE_DIR" archive --format=tar --prefix=is-stream/ HEAD > "$ARCHIVE"
printf '%s  %s\n' "$ARCHIVE_SHA256" "$ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$SOURCE_DIR/". /workspace/
rm -rf /workspace/.git
mv /workspace/index.js /workspace/upstream.js
cp "$SCRIPT_DIR/index-wrapper.js" /workspace/index.js
cp "$SCRIPT_DIR/adapter.js" /workspace/adapter.js
cp "$SCRIPT_DIR/package-lock.json" /workspace/package-lock.json

node -e '
const fs = require("node:fs");
const path = "/workspace/package.json";
const data = JSON.parse(fs.readFileSync(path, "utf8"));
delete data.scripts;
delete data.devDependencies;
data.main = "./index.js";
data.exports = {types: "./index.d.ts", default: "./index.js"};
data.files = ["index.js", "upstream.js", "adapter.js", "index.d.ts"];
fs.writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
'
