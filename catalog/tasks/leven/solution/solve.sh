#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/sindresorhus/leven"
UPSTREAM_REVISION="fbc77137f0361b26aaa8465854e0ae8e492db6ba"
SOURCE_ARCHIVE_SHA256="14181e2e61abff5adcf7678a8a8e97cac49c90520d5f9d47e33a27687eeef055"
SOURCE_DIR="/tmp/leven-source"
SOURCE_ARCHIVE="/tmp/leven-source.tar"

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
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# The frozen source predates a committed npm lock and carries development-only
# AVA/XO dependencies. The benchmark candidate contract has no runtime
# dependencies, while the unified installer requires npm ci. Remove only the
# upstream development tooling and generate the exact zero-dependency v3 lock.
node --input-type=module <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const manifest = JSON.parse(readFileSync(path, 'utf8'));
delete manifest.devDependencies;
delete manifest.scripts;
writeFileSync(path, `${JSON.stringify(manifest, null, '\t')}\n`);
NODE
npm --prefix /workspace install --package-lock-only --offline --ignore-scripts --no-audit --no-fund
