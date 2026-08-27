#!/usr/bin/env bash
set -euo pipefail

archive=/solution/winston-3.19.0.tgz
test -f "$archive"
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
tar -xzf "$archive" -C /workspace --strip-components=1
cp /solution/package-lock.json /workspace/package-lock.json
test -f /workspace/package.json
test -f /workspace/lib/winston.js
