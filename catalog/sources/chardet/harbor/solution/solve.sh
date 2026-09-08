#!/bin/bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")

# Expected source digest for chardet 7.6.0
EXPECTED_SHA256="93d9df6089ded42ed1fe9f57e272c0b74bd0464d45c0c7d50f09f26f31105c3c"
TARBALL="${BUNDLE_DIR}/chardet-7.6.0.tar.gz"

# Verify source archive exists
if [ ! -f "${TARBALL}" ]; then
    echo "Error: Source tarball not found at ${TARBALL}" >&2
    exit 1
fi

# Verify SHA-256 digest
ACTUAL_SHA256=$(sha256sum "${TARBALL}" | cut -d' ' -f1)
if [ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]; then
    echo "Error: SHA-256 mismatch" >&2
    echo "  Expected: ${EXPECTED_SHA256}" >&2
    echo "  Actual:   ${ACTUAL_SHA256}" >&2
    exit 1
fi

# Extract to /workspace with correct topology
cd /workspace
tar -xzf "${TARBALL}" --strip-components=1

# Verify extraction
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found after extraction" >&2
    exit 1
fi

# Static version patch for hatch-vcs (version is managed by VCS during build)
mkdir -p src/chardet
cat > src/chardet/_version.py << 'VERSION_EOF'
"""Version information for chardet."""
__version__ = "7.6.0"
__version_tuple__ = (7, 6, 0)
VERSION_EOF

# Install package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify installation and imports
python -c "import chardet; print(f'chardet version: {chardet.__version__}')"
python -c "import chardet; result = chardet.detect(b'test'); print(f'Basic detection works: {result}')"
python -c "from chardet import UniversalDetector; print('UniversalDetector imported successfully')"
python -c "from chardet import detect, detect_all; print('Functions imported successfully')"

echo "Oracle setup complete: chardet 7.6.0 installed successfully"
