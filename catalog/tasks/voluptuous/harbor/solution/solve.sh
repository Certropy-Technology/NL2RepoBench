#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream voluptuous source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/voluptuous-src >/dev/null
git -C /tmp/voluptuous-src remote add origin https://github.com/alecthomas/voluptuous
git -C /tmp/voluptuous-src fetch --depth 1 origin dcaaf3dd68be156253518a045feb1c4172dbd2d5 >/dev/null
git -C /tmp/voluptuous-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/voluptuous-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
