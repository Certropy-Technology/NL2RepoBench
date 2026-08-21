#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream deepdiff source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/deepdiff-src >/dev/null
git -C /tmp/deepdiff-src remote add origin https://github.com/seperman/deepdiff
git -C /tmp/deepdiff-src fetch --depth 1 origin ba85943dc0d188f631f7c0f37d64241d489ad1e1 >/dev/null
git -C /tmp/deepdiff-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/deepdiff-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
