#!/bin/bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_SHA256="ba23db109e3e93ef1999f7209a651214994cd807801addd16ac485982eb4edd7"

echo "=== Oracle: Installing isort from frozen source ==="

# Verify source archive
ACTUAL_SHA256=$(sha256sum "${BUNDLE_DIR}/source.tar.gz" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: Source digest mismatch!"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Actual:   $ACTUAL_SHA256"
    exit 1
fi
echo "Source digest verified: $EXPECTED_SHA256"

# Extract to workspace (has isort-9.0.1/ prefix, use --strip-components=1)
cd /workspace
tar -xzf "${BUNDLE_DIR}/source.tar.gz" --strip-components=1

# Apply version patch (remove vcs version, use static)
python3 << 'PYPATCH'
import re
with open('pyproject.toml', 'r') as f:
    content = f.read()
content = re.sub(r'dynamic\s*=\s*\["version"\]', 'version = "9.0.1"', content)
content = re.sub(r'\[tool\.hatch\.version\].*?\n(?=\[|\Z)', '', content, flags=re.DOTALL)
content = re.sub(r'\[tool\.hatch\.version\.raw-options\].*?\n(?=\[|\Z)', '', content, flags=re.DOTALL)
with open('pyproject.toml', 'w') as f:
    f.write(content)
PYPATCH

echo "Applied version patch to pyproject.toml"

# Install package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation
python -c "import isort; print(f'isort version: {isort.__version__}')"
python -c "from isort import Config, code, check_code, file, check_file; print('Core imports OK')"
python -c "from isort import find_imports_in_code, place_module; print('Analysis imports OK')"

echo "=== Oracle installation complete ==="
