#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/jd/tenacity'
UPSTREAM_REVISION='26f719dc73d3c5612b9c1b8d18a7883837790ad8'
SOURCE_DIR=/tmp/tenacity-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
