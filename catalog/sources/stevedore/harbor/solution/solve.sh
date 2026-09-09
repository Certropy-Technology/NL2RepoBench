#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR=$(dirname "$0")
EXPECTED_SHA256="e97a2667923efda926e8713fde6a73616df68210a3cbc6f02b48967b676fd8bf"
ARCHIVE_NAME="stevedore-5.9.1.tar.gz"

# Verify archive exists and has correct SHA256
if [ ! -f "$BUNDLE_DIR/$ARCHIVE_NAME" ]; then
    echo "ERROR: Archive $ARCHIVE_NAME not found in bundle" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/$ARCHIVE_NAME" | cut -d' ' -f1)
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: SHA256 mismatch for $ARCHIVE_NAME" >&2
    echo "  Expected: $EXPECTED_SHA256" >&2
    echo "  Actual:   $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to /workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/$ARCHIVE_NAME" --strip-components=1

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify imports
python -c "import stevedore; from stevedore import ExtensionManager, DriverManager, NamedExtensionManager, EnabledExtensionManager, HookManager; from stevedore.exception import NoMatches, MultipleMatches, NoUniqueMatch"

echo "Oracle setup complete"
