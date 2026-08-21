#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream cachier source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/cachier-src >/dev/null
git -C /tmp/cachier-src remote add origin https://github.com/python-cachier/cachier
git -C /tmp/cachier-src fetch --depth 1 origin 36478c366675231438ddb1f96e520b44cea057c6 >/dev/null
git -C /tmp/cachier-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/cachier-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
