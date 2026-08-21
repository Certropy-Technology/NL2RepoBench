#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream stamina source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/stamina-src >/dev/null
git -C /tmp/stamina-src remote add origin https://github.com/hynek/stamina
git -C /tmp/stamina-src fetch --depth 1 origin 25288ed058f9723bf113768b1ae26cf8857d65c1 >/dev/null
git -C /tmp/stamina-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/stamina-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
