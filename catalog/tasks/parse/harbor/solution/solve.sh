#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/r1chardj0n3s/parse'
UPSTREAM_REVISION='8059e320eccf40d750843006dd2ef25197bbff74'
SOURCE_DIR=/tmp/parse-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
