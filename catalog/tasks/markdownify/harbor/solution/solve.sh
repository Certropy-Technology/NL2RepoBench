#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream markdownify source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/markdownify-src >/dev/null
git -C /tmp/markdownify-src remote add origin https://github.com/matthewwithanm/python-markdownify
git -C /tmp/markdownify-src fetch --depth 1 origin 8f70e3952f7f8132777e60ed098f8974e51f7cbd >/dev/null
git -C /tmp/markdownify-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/markdownify-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
