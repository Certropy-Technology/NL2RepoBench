#!/bin/bash
set -euo pipefail

# Oracle solution for croniter task
# Restores frozen source from bundled payload

EXPECTED_REVISION="9181ba7de0a91512cb77d537b7e23631ffe4f7e8"
EXPECTED_DIGEST="ac8e9d432017f5ef6c70f8660e98359353201d58383c38358c221378b74fbe77"
WORKSPACE="/workspace"
BUNDLE_DIR="$(dirname "$0")"
SOURCE_ARCHIVE="${BUNDLE_DIR}/source.tar.gz"

echo "[ORACLE] Starting croniter solution restoration"
echo "[ORACLE] Expected revision: ${EXPECTED_REVISION}"
echo "[ORACLE] Expected digest: ${EXPECTED_DIGEST}"

# Verify source archive exists
if [ ! -f "${SOURCE_ARCHIVE}" ]; then
    echo "[ORACLE] ERROR: Source archive not found at ${SOURCE_ARCHIVE}"
    exit 1
fi

# Verify digest
echo "[ORACLE] Verifying source archive digest..."
ACTUAL_DIGEST=$(sha256sum "${SOURCE_ARCHIVE}" | awk '{print $1}')
if [ "${ACTUAL_DIGEST}" != "${EXPECTED_DIGEST}" ]; then
    echo "[ORACLE] ERROR: Digest mismatch"
    echo "[ORACLE]   Expected: ${EXPECTED_DIGEST}"
    echo "[ORACLE]   Actual:   ${ACTUAL_DIGEST}"
    exit 1
fi
echo "[ORACLE] Digest verified: ${ACTUAL_DIGEST}"

# Extract to workspace
echo "[ORACLE] Extracting source to ${WORKSPACE}..."
cd "${WORKSPACE}"

# Extract with strip-components=1 to remove top-level directory
tar -xzf "${SOURCE_ARCHIVE}" --strip-components=1

# Verify extraction
if [ ! -f "${WORKSPACE}/pyproject.toml" ]; then
    echo "[ORACLE] ERROR: pyproject.toml not found after extraction"
    exit 1
fi

if [ ! -f "${WORKSPACE}/src/croniter/__init__.py" ]; then
    echo "[ORACLE] ERROR: src/croniter/__init__.py not found after extraction"
    exit 1
fi

echo "[ORACLE] Source restored successfully"
echo "[ORACLE] Contents:"
ls -la "${WORKSPACE}/" | head -20

echo "[ORACLE] Package structure:"
ls -la "${WORKSPACE}/src/croniter/" | head -20

echo "[ORACLE] Solution restoration complete"
