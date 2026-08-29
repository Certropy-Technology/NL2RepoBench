#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/fabiospampinato/fast-string-truncated-width'
UPSTREAM_REVISION='1d50ce0c1497c1399eed50f87926817587049358'
SOURCE_ARCHIVE_SHA256='910a980a127ca70626d2bc0dbe673601e7c65c8778548cd1c3f94472c59c2f79'
SOURCE_REPO=/tmp/fast-string-truncated-width-source
SOURCE_ARCHIVE=/tmp/fast-string-truncated-width-source.tar
SOURCE_TREE=/tmp/fast-string-truncated-width-tree

rm -rf "$SOURCE_REPO" "$SOURCE_TREE" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_REPO"
git -C "$SOURCE_REPO" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_REPO" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_REPO" rev-parse FETCH_HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
  printf 'resolved revision mismatch: %s\n' "$resolved_revision" >&2
  exit 1
fi
git -C "$SOURCE_REPO" archive --format=tar --output="$SOURCE_ARCHIVE" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

mkdir -p "$SOURCE_TREE"
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_TREE"
rm -rf /workspace/*
cp -a "$SOURCE_TREE"/. /workspace/

node /solution/prepare-build.mjs /workspace /solution/package-lock.build.json
npm ci --offline --ignore-scripts --no-audit --no-fund --cache=/opt/npm-bundle/npm-cache
npm run build
node /solution/finalize-package.mjs /workspace
rm -rf /workspace/node_modules /workspace/src /workspace/test /workspace/tasks
rm -f /workspace/tsconfig.json /workspace/tsconfig.build.json /workspace/.editorconfig \
  /workspace/.gitignore /workspace/.npmignore
