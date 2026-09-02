#!/usr/bin/env bash
set -euo pipefail

revision='dc17e0e00fb39c8d52e97ce77e494cdadfa8d19c'
expected_archive='f127a1e7e44b6583ee6ae2451824fb1e4d0b886f5a3ba5282738c7700d36b380'
remote='https://github.com/RyanZim/universalify.git'
checkout='/tmp/universalify-oracle-source'
archive='/tmp/universalify-oracle-source.tar'

rm -rf "$checkout" "$archive"
git init -q "$checkout"
git -C "$checkout" remote add origin "$remote"
git -C "$checkout" fetch --depth 1 origin "$revision"
resolved="$(git -C "$checkout" rev-parse FETCH_HEAD)"
test "$resolved" = "$revision"
git -C "$checkout" archive --format=tar FETCH_HEAD -o "$archive"
test "$(sha256sum "$archive" | awk '{print $1}')" = "$expected_archive"

mkdir -p /workspace
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace
node <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const packageJson = JSON.parse(fs.readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
fs.writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);
NODE
cd /workspace
npm install --package-lock-only --offline --ignore-scripts --no-audit --no-fund
