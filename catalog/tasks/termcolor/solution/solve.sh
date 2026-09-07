#!/usr/bin/env bash
set -euo pipefail

echo "[oracle] Starting termcolor Oracle solution"

# Verify we have the source archive
SOURCE_ARCHIVE="/solution/source.tar.gz"
EXPECTED_SHA256="c43f9ad2ed38f168bb84666a70ac8c645b648eac1cab10b79438971af48f2290"

if [ ! -f "$SOURCE_ARCHIVE" ]; then
    echo "[oracle] ERROR: Source archive not found at $SOURCE_ARCHIVE" >&2
    exit 1
fi

# Verify SHA-256
echo "[oracle] Verifying source archive integrity"
ACTUAL_SHA256=$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "[oracle] ERROR: SHA-256 mismatch" >&2
    echo "[oracle]   Expected: $EXPECTED_SHA256" >&2
    echo "[oracle]   Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

echo "[oracle] SHA-256 verified: $EXPECTED_SHA256"

# Extract to temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_DIR'" EXIT

cd "$TEMP_DIR"
tar -xzf "$SOURCE_ARCHIVE"

# The archive contains a single directory termcolor-<revision>
SOURCE_DIR=$(find . -maxdepth 1 -type d -name "termcolor-*" | head -1)
if [ -z "$SOURCE_DIR" ]; then
    echo "[oracle] ERROR: Could not find extracted source directory" >&2
    exit 1
fi

echo "[oracle] Extracted source to: $SOURCE_DIR"

# Copy contents to /workspace (the package root should be at /workspace/)
cd "$SOURCE_DIR"
cp -r * /workspace/
cp -r .* /workspace/ 2>/dev/null || true

cd /workspace

# Verify essential files exist
if [ ! -f "pyproject.toml" ]; then
    echo "[oracle] ERROR: pyproject.toml not found in workspace" >&2
    exit 1
fi

if [ ! -d "src/termcolor" ]; then
    echo "[oracle] ERROR: src/termcolor/ directory not found" >&2
    exit 1
fi

echo "[oracle] Source files installed to /workspace"
echo "[oracle] Installing package..."

# Install the package with version override for hatch-vcs
# Use --no-build-isolation to reuse preinstalled build backends
export SETUPTOOLS_SCM_PRETEND_VERSION=3.3.0
python -m pip install --no-build-isolation --no-deps --no-index -e . || {
    echo "[oracle] ERROR: pip install failed" >&2
    exit 1
}

echo "[oracle] Installation complete"

# Verify installation
python3 -c "import termcolor; print('[oracle] termcolor imported successfully')" || {
    echo "[oracle] ERROR: Failed to import termcolor" >&2
    exit 1
}

python3 -c "from termcolor import colored, cprint, can_colorize, COLORS, HIGHLIGHTS, ATTRIBUTES, RESET; print('[oracle] All exports verified')" || {
    echo "[oracle] ERROR: Failed to import termcolor exports" >&2
    exit 1
}

echo "[oracle] Oracle verification complete"
