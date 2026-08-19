#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/msiemens/tinydb'
UPSTREAM_REVISION='4aa53111d72c9cbaafcdc039211caf49f4face6f'
SOURCE_DIR=/tmp/tinydb-src

git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
cp -a "$SOURCE_DIR/." /workspace/
rm -rf /workspace/.github
