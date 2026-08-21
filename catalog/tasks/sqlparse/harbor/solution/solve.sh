#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream sqlparse source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/sqlparse-src >/dev/null
git -C /tmp/sqlparse-src remote add origin https://github.com/andialbrecht/sqlparse
git -C /tmp/sqlparse-src fetch --depth 1 origin a801100e9843786a9139bebb97c951603637129c >/dev/null
git -C /tmp/sqlparse-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/sqlparse-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
