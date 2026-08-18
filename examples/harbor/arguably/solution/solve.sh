#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream arguably source code ==="

# Clone upstream repository
git clone --depth 1 https://github.com/treykeown/arguably.git /tmp/arguably-src

# Copy entire source tree to workspace
cd /tmp/arguably-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Remove git directory and unnecessary files
rm -rf /workspace/.git
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
