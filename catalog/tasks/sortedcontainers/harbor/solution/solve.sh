#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream sortedcontainers source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/sortedcontainers-src >/dev/null
git -C /tmp/sortedcontainers-src remote add origin https://github.com/grantjenks/python-sortedcontainers
git -C /tmp/sortedcontainers-src fetch --depth 1 origin a1f52d6713dd2c2713a881d4f4d86ed68ff71cab >/dev/null
git -C /tmp/sortedcontainers-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/sortedcontainers-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
