#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream python-pathspec source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/python-pathspec-src >/dev/null
git -C /tmp/python-pathspec-src remote add origin https://github.com/cpburnz/python-pathspec
git -C /tmp/python-pathspec-src fetch --depth 1 origin 6485791e1b5cf2ef4e756ae392fa80f2c5045d4c >/dev/null
git -C /tmp/python-pathspec-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/python-pathspec-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
