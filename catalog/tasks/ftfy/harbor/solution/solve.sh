#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/rspeer/python-ftfy'
UPSTREAM_REVISION='74dd0452b48286a3770013b3a02755313bd5575e'
SOURCE_DIR=/tmp/ftfy-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
