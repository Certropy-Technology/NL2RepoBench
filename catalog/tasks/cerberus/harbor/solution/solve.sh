#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/pyeve/cerberus'
UPSTREAM_REVISION='65e977de08ab76d4b40ca981972f9ff68926ed63'
SOURCE_DIR=/tmp/cerberus-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
