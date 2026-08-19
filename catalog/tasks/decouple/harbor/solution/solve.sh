#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/HBNetwork/python-decouple'
UPSTREAM_REVISION='0573e6f96637f08fb4cb85e0552f0622d36827d4'
SOURCE_DIR=/tmp/decouple-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
