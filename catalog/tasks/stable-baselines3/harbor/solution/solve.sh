#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream stable-baselines3 source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/stable-baselines3-src >/dev/null
git -C /tmp/stable-baselines3-src remote add origin https://github.com/DLR-RM/stable-baselines3
git -C /tmp/stable-baselines3-src fetch --depth 1 origin 440ccdd2acb90168a434db955b0c0e9a1c0854e1 >/dev/null
git -C /tmp/stable-baselines3-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/stable-baselines3-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
