#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream fuzzywuzzy source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/fuzzywuzzy-src >/dev/null
git -C /tmp/fuzzywuzzy-src remote add origin https://github.com/seatgeek/fuzzywuzzy
git -C /tmp/fuzzywuzzy-src fetch --depth 1 origin 749d61ab2ea35498c4d04d74dafde9248f253fb4 >/dev/null
git -C /tmp/fuzzywuzzy-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/fuzzywuzzy-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
