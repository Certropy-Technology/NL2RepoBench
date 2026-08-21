#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream emoji source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/emoji-src >/dev/null
git -C /tmp/emoji-src remote add origin https://github.com/carpedm20/emoji
git -C /tmp/emoji-src fetch --depth 1 origin d26c675190a6b6c0edee959d7b896721a9c3641d >/dev/null
git -C /tmp/emoji-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/emoji-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
