#!/usr/bin/env bash
set -euo pipefail
URL="https://github.com/horejsek/python-fastjsonschema"
REVISION="b88fa37cd46bb81e8d9dce91a7e1bc4debedd3a2"
SUITE_REVISION="9fc880bfb6d8ccd093bc82431f17d13681ffae8e"
SOURCE_DIR=/tmp/fastjsonschema-source
rm -rf "$SOURCE_DIR"; git init -q "$SOURCE_DIR"; git -C "$SOURCE_DIR" remote add origin "$URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$REVISION"; git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
test "$(git -C "$SOURCE_DIR" rev-parse HEAD)" = "$REVISION"
git -C "$SOURCE_DIR" submodule update --init --depth 1 JSON-Schema-Test-Suite
test "$(git -C "$SOURCE_DIR/JSON-Schema-Test-Suite" rev-parse HEAD)" = "$SUITE_REVISION"
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
git -C "$SOURCE_DIR" archive --format=tar "$REVISION" | tar -xf - -C /workspace
