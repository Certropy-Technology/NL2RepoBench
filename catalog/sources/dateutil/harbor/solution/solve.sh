#!/bin/bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_SHA256="37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3"

# Verify source archive
if [ ! -f "$BUNDLE_DIR/source.tar.gz" ]; then
    echo "Error: source.tar.gz not found in $BUNDLE_DIR" >&2
    exit 1
fi

ACTUAL_SHA256=$(sha256sum "$BUNDLE_DIR/source.tar.gz" | awk '{print $1}')
if [ "$ACTUAL_SHA256" != "$SOURCE_SHA256" ]; then
    echo "Error: source.tar.gz checksum mismatch" >&2
    echo "  Expected: $SOURCE_SHA256" >&2
    echo "  Got:      $ACTUAL_SHA256" >&2
    exit 1
fi

# Extract to workspace
cd /workspace
tar -xzf "$BUNDLE_DIR/source.tar.gz" --strip-components=1

# Patch pyproject.toml to use static version instead of setuptools_scm
# The tarball doesn't have .git, so we need to provide a fallback version
cat > pyproject.toml << 'PYPROJECT_EOF'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
PYPROJECT_EOF

# Update setup.cfg to add static version
if grep -q "^use_scm_version" setup.py; then
    # setup.py uses scm version, we need to override it
    # Create a minimal _version.py
    mkdir -p src/dateutil
    echo '__version__ = "2.9.0.post0"' > src/dateutil/_version.py
fi

# Add version to setup.cfg if not present
if ! grep -q "^version = " setup.cfg; then
    sed -i '/^\[metadata\]/a version = 2.9.0.post0' setup.cfg
fi

# Install the package
python -m pip install --no-build-isolation --no-deps --no-index -e .

# Verify import
python -c "import dateutil; from dateutil import relativedelta, parser, rrule, easter, tz, utils; print('dateutil successfully installed')"
