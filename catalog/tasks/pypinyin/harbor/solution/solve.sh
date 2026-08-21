#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream pypinyin source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/pypinyin-src >/dev/null
git -C /tmp/pypinyin-src remote add origin https://github.com/mozillazg/python-pinyin
git -C /tmp/pypinyin-src fetch --depth 1 origin df101577145af2eb1abe5656e592e34e3bb56d23 >/dev/null
git -C /tmp/pypinyin-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/pypinyin-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
