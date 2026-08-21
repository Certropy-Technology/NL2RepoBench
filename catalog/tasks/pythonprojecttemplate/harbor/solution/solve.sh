#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/franneck94/PythonProjectTemplate'
UPSTREAM_REVISION='f1c116379eb485c17fb1b6cd3e2454712e4e0585'
SOURCE_DIR=/tmp/pythonprojecttemplate-src

rm -rf "$SOURCE_DIR"
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
