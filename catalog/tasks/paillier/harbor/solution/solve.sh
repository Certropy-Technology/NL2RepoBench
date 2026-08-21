#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream paillier source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/paillier-src >/dev/null
git -C /tmp/paillier-src remote add origin https://github.com/data61/python-paillier
git -C /tmp/paillier-src fetch --depth 1 origin 98806e24403eb6ac5d3056a979bbf5c385b90b08 >/dev/null
git -C /tmp/paillier-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/paillier-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
