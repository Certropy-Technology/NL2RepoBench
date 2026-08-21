#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream unidecode source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/unidecode-src >/dev/null
git -C /tmp/unidecode-src remote add origin https://github.com/avian2/unidecode
git -C /tmp/unidecode-src fetch --depth 1 origin 8d83b7c70c39678c2b95cb0caf3d3c4425cb2cc2 >/dev/null
git -C /tmp/unidecode-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/unidecode-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
