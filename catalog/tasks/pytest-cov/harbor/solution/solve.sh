#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream pytest-cov source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/pytest-cov-src >/dev/null
git -C /tmp/pytest-cov-src remote add origin https://github.com/pytest-dev/pytest-cov
git -C /tmp/pytest-cov-src fetch --depth 1 origin 55dbe43f04f839b760ea346e560276d641998c77 >/dev/null
git -C /tmp/pytest-cov-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/pytest-cov-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
