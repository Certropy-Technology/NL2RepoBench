#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/sindresorhus/dot-prop'
UPSTREAM_REVISION='d5d11c71a70bfb643a45d22821ed6d284240fce5'
SOURCE_ARCHIVE_SHA256='8260136eb763c56d5b073b0365ed875ccf9ce6aaad81c8647af2f51b0f53019c'
SOURCE_INDEX_SHA256='b4c6d5b46b25510e1a05472a76abdb113b2a120cad2f05b226f5449786a0ddb7'
SOURCE_REPO=/tmp/dot-prop-source
SOURCE_ARCHIVE=/tmp/dot-prop-source.tar
SOURCE_TREE=/tmp/dot-prop-tree
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "$SOURCE_REPO" "$SOURCE_TREE" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_REPO"
git -C "$SOURCE_REPO" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_REPO" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_REPO" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_REPO" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
mkdir -p "$SOURCE_TREE"
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_TREE"
printf '%s  %s\n' "$SOURCE_INDEX_SHA256" "$SOURCE_TREE/index.js" | sha256sum --check --strict

rm -rf /workspace/*
cp "$here/package.json" "$here/package-lock.json" "$here/license" /workspace/
cp "$here/index.js" "$here/index.d.ts" /workspace/
test "$(node -p "require('/workspace/package.json').name")" = 'dot-prop'
test "$(node -p "require('/workspace/package.json').version")" = '10.2.0'
