#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream pdfplumber-stable source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/pdfplumber-stable-src >/dev/null
git -C /tmp/pdfplumber-stable-src remote add origin https://github.com/jsvine/pdfplumber
git -C /tmp/pdfplumber-stable-src fetch --depth 1 origin c6a24be50d6e405e22f84b75e980737541e33732 >/dev/null
git -C /tmp/pdfplumber-stable-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/pdfplumber-stable-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
