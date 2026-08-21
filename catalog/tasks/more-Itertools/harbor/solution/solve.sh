#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream more-Itertools source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/more-Itertools-src >/dev/null
git -C /tmp/more-Itertools-src remote add origin https://github.com/more-itertools/more-itertools
git -C /tmp/more-Itertools-src fetch --depth 1 origin f7134fa18cdf30b9b39545104d9f75aab38818a0 >/dev/null
git -C /tmp/more-Itertools-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/more-Itertools-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
