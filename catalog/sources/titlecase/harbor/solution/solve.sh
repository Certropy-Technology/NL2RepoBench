#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="7d83a277ccbbda11a2944e78a63e5ccaf3d32f828c594312e4862f9a07f635f5"
TARBALL="$BUNDLE_DIR/titlecase-2.4.1.tar.gz"

if [ ! -f "$TARBALL" ]; then
    echo "Error: tarball not found at $TARBALL" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$TARBALL" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "Error: SHA256 mismatch" >&2
    echo "Expected: $EXPECTED_SHA256" >&2
    echo "Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

cd /workspace
tar -xzf "$TARBALL" --strip-components=1

if [ ! -f "setup.py" ] && [ ! -f "pyproject.toml" ]; then
    echo "Error: No setup.py or pyproject.toml found" >&2
    exit 1
fi

python -m pip install --no-deps --no-index -e .

python -c "from titlecase import titlecase; print('Import successful')"

if [ -f "titlecase/__init__.py" ]; then
    if grep -q "setuptools_scm" pyproject.toml 2>/dev/null; then
        VERSION_FILE="titlecase/__init__.py"
        if ! grep -q "^__version__ = '2.4.1'$" "$VERSION_FILE" 2>/dev/null; then
            sed -i "s/^__version__ = .*/__version__ = '2.4.1'/" "$VERSION_FILE" || true
        fi
    fi
fi

echo "Solution installed successfully"
