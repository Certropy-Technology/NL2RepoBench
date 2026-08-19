#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/treykeown/arguably'
UPSTREAM_REVISION='86648796c4a28fa59f6f059b673694929c7df534'
SOURCE_DIR=/tmp/arguably-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
