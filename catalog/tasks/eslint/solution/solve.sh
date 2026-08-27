#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="c27bc926e496985eb7911c09eb60914b2e4b5d0f"
readonly SOURCE_URL="https://codeload.github.com/eslint/eslint/tar.gz"
readonly SOURCE_ARCHIVE_SHA256="a02160c6f87fa83ba6082361d085ea32d5937dd2063bb6735b8d649d04b03ca0"
readonly SOURCE_CODELOAD_SHA256="0fa7691ed4b4efe49b7789410d6763c6d27f6f4b8dada81f28377a08a97e3a0f"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly WORK_DIR="$(mktemp -d /tmp/eslint-oracle.XXXXXX)"
trap 'rm -rf "$WORK_DIR"' EXIT

node - "$WORK_DIR/source.tar.gz" "$SOURCE_URL/$REVISION" <<'NODE'
const fs = require("node:fs");
const https = require("node:https");
const output = process.argv[2];
const url = process.argv[3];
const maxBytes = 64 * 1024 * 1024;
const request = https.get(url, { headers: { "user-agent": "nl2repobench-oracle/1" } }, (response) => {
  if (response.statusCode !== 200) {
    response.resume();
    process.exit(70);
  }
  let total = 0;
  const chunks = [];
  response.on("data", (chunk) => {
    total += chunk.length;
    if (total > maxBytes) process.exit(70);
    chunks.push(chunk);
  });
  response.on("end", () => fs.writeFileSync(output, Buffer.concat(chunks), { mode: 0o400 }));
});
request.setTimeout(120_000, () => request.destroy(new Error("source fetch timeout")));
request.on("error", () => process.exit(70));
NODE
test -s "$WORK_DIR/source.tar.gz"
printf '%s  %s\n' "$SOURCE_CODELOAD_SHA256" "$WORK_DIR/source.tar.gz" | sha256sum --check --strict
tar -xzf "$WORK_DIR/source.tar.gz" -C "$WORK_DIR"
source_root="$(find "$WORK_DIR" -mindepth 1 -maxdepth 1 -type d -name 'eslint-*' -print -quit)"
test -n "$source_root"
test -f "$source_root/package.json"
test "$(node -e 'const p=require(process.argv[1]); process.stdout.write(p.version)' "$source_root/package.json")" = "10.9.0"
test "$(node -e 'const p=require(process.argv[1]); process.stdout.write(p.name)' "$source_root/package.json")" = "eslint"

mkdir -p /workspace
rm -rf /workspace/*
cd "$source_root"
npm pack --ignore-scripts --pack-destination "$WORK_DIR" >/dev/null
tarball="$(find "$WORK_DIR" -maxdepth 1 -name 'eslint-10.9.0.tgz' -type f -print -quit)"
test -n "$tarball"
tar -xzf "$tarball" -C /workspace --strip-components=1

node - /workspace/package.json <<'NODE'
const fs = require("node:fs");
const path = process.argv[2];
const pkg = JSON.parse(fs.readFileSync(path, "utf8"));
delete pkg.scripts;
delete pkg.devDependencies;
delete pkg.workspaces;
pkg.private = true;
fs.writeFileSync(path, `${JSON.stringify(pkg, null, 2)}\n`);
NODE
cp "$SCRIPT_DIR/oracle-package-lock.json" /workspace/package-lock.json
