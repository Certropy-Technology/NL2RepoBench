#!/usr/bin/env bash
set -euo pipefail

# Oracle solution for termcolor task
# Extracts frozen source archive and installs into /workspace

EXPECTED_REVISION="0980eb52aa867fc32f70859a61c0609501b73a99"
EXPECTED_SHA256="c43f9ad2ed38f168bb84666a70ac8c645b648eac1cab10b79438971af48f2290"

echo "=== Oracle: Installing termcolor from frozen source ==="

# The source archive should be bundled in the Oracle artifact
SOURCE_ARCHIVE="/oracle/source-${EXPECTED_REVISION}.tar.gz"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "ERROR: Source archive not found at $SOURCE_ARCHIVE"
    exit 1
fi

# Verify SHA-256
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: Source archive SHA-256 mismatch"
    echo "  Expected: $EXPECTED_SHA256"
    echo "  Actual:   $ACTUAL_SHA256"
    exit 1
fi

echo "Source archive SHA-256 verified: $EXPECTED_SHA256"

# Extract to temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_DIR'" EXIT

cd "$TEMP_DIR"
tar -xzf "$SOURCE_ARCHIVE"

# The archive contains a single directory termcolor-<revision>
SOURCE_DIR=$(find . -maxdepth 1 -type d -name "termcolor-*" | head -1)
if [ -z "$SOURCE_DIR" ]; then
    echo "ERROR: Could not find extracted source directory"
    exit 1
fi

echo "Extracted source to: $SOURCE_DIR"

# Copy contents to /workspace (the package root should be at /workspace/)
cd "$SOURCE_DIR"
cp -r * /workspace/
cp -r .* /workspace/ 2>/dev/null || true

cd /workspace

# Verify essential files exist
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: pyproject.toml not found in workspace"
    exit 1
fi

if [ ! -d "src/termcolor" ]; then
    echo "ERROR: src/termcolor/ directory not found"
    exit 1
fi

echo "Source files installed to /workspace"
echo "Installing package..."

# Install the package with version override for hatch-vcs
export SETUPTOOLS_SCM_PRETEND_VERSION=3.3.0
pip install --no-cache-dir . || {
    echo "ERROR: pip install failed"
    exit 1
}

echo "=== Oracle installation complete ==="

# Verify installation
python3 -c "import termcolor; print(f'termcolor imported successfully')" || {
    echo "ERROR: Failed to import termcolor"
    exit 1
}

python3 -c "from termcolor import colored, cprint, can_colorize, COLORS, HIGHLIGHTS, ATTRIBUTES, RESET; print('All exports verified')" || {
    echo "ERROR: Failed to import termcolor exports"
    exit 1
}

echo "Oracle verification complete"
