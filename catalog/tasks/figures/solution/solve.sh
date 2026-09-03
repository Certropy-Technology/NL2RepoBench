#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/sindresorhus/figures"
readonly UPSTREAM_REVISION="3da3d1713e9a09dbfcfc99eac86af8f4377597b6"
readonly SOURCE_ARCHIVE_SHA256="c1b1db9dd7ff5771b6301e85ade19184e7bf46990b95008240729c39287b3258"
readonly FETCH_ROOT="/tmp/figures-oracle-source"
readonly WORKSPACE="/workspace"

rm -rf -- "$FETCH_ROOT"
git init -q "$FETCH_ROOT"
git -C "$FETCH_ROOT" remote add origin "$UPSTREAM_URL"
git -C "$FETCH_ROOT" fetch --quiet --no-tags --depth=1 origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict

rm -rf -- "$WORKSPACE"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$WORKSPACE"
rm -rf -- "$WORKSPACE/.github"
rm -f -- "$WORKSPACE/.npmrc"

node --input-type=module <<'JS'
import {readFileSync, writeFileSync} from 'node:fs';
const packagePath = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
writeFileSync(packagePath, `${JSON.stringify(packageJson, null, '\t')}\n`);
JS

cp "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/package-lock.json" "$WORKSPACE/package-lock.json"
