#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream rich-click source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/rich-click-src >/dev/null
git -C /tmp/rich-click-src remote add origin https://github.com/ewels/rich-click
git -C /tmp/rich-click-src fetch --depth 1 origin 0ea0e0a13b199cc1cf28ece1338bf0838772727b >/dev/null
git -C /tmp/rich-click-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/rich-click-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
