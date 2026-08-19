#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/wbolster/jsonlines'
UPSTREAM_REVISION='43d1a30b9634f8b715b6af3f2473927caa1e704d'
SOURCE_DIR=/tmp/jsonlines-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
