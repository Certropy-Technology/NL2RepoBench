#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/jpadilla/pyjwt'
UPSTREAM_TAG='2.10.1'
SOURCE_DIR=/tmp/pyjwt-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "refs/tags/$UPSTREAM_TAG" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
