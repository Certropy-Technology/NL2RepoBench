#!/usr/bin/env bash
set -euo pipefail

git init /tmp/textual-src >/dev/null
git -C /tmp/textual-src remote add origin https://github.com/Textualize/textual
git -C /tmp/textual-src fetch --depth 1 origin 06dbeef4bb70fb718236aa418ed658ef4667a126 >/dev/null
git -C /tmp/textual-src checkout --detach FETCH_HEAD >/dev/null
cp -a /tmp/textual-src/. /workspace/
rm -rf /workspace/.git /workspace/.github
