#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream mechanicalsoup source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/mechanicalsoup-src >/dev/null
git -C /tmp/mechanicalsoup-src remote add origin https://github.com/MechanicalSoup/MechanicalSoup
git -C /tmp/mechanicalsoup-src fetch --depth 1 origin 16238f4b726a09563150a2a818cded51ac7d7c1f >/dev/null
git -C /tmp/mechanicalsoup-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/mechanicalsoup-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
