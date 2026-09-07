#!/usr/bin/env bash
set -euo pipefail

# Oracle solution for beartype task.
# This script extracts the frozen beartype-0.22.9 source archive bundled in this
# Oracle artifact and installs it into /workspace.

echo "[oracle] Starting beartype Oracle solution"

# Expected source digest
EXPECTED_DIGEST="8f82b54aa723a2848a56008d18875f91c1db02c32ef6a62319a002e3e25a975f"
EXPECTED_REVISION="9430c6515af3b158acacdc47fe7b1adb646f6624"

# Paths
ORACLE_ROOT="/oracle"
SOURCE_ARCHIVE="${ORACLE_ROOT}/beartype-0.22.9.tar.gz"
WORKSPACE="/workspace"

# Verify source archive exists
if [[ ! -f "${SOURCE_ARCHIVE}" ]]; then
    echo "[oracle] ERROR: Source archive not found at ${SOURCE_ARCHIVE}" >&2
    exit 1
fi

# Verify source digest
echo "[oracle] Verifying source archive digest"
ACTUAL_DIGEST=$(sha256sum "${SOURCE_ARCHIVE}" | awk '{print $1}')
if [[ "${ACTUAL_DIGEST}" != "${EXPECTED_DIGEST}" ]]; then
    echo "[oracle] ERROR: Source digest mismatch" >&2
    echo "[oracle]   Expected: ${EXPECTED_DIGEST}" >&2
    echo "[oracle]   Actual:   ${ACTUAL_DIGEST}" >&2
    exit 1
fi

echo "[oracle] Source digest verified: ${ACTUAL_DIGEST}"

# Extract source archive
echo "[oracle] Extracting source archive to ${WORKSPACE}"
tar -xzf "${SOURCE_ARCHIVE}" -C "${WORKSPACE}" --strip-components=1

# Verify extraction
if [[ ! -f "${WORKSPACE}/pyproject.toml" ]]; then
    echo "[oracle] ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi

if [[ ! -d "${WORKSPACE}/beartype" ]]; then
    echo "[oracle] ERROR: beartype/ directory not found after extraction" >&2
    exit 1
fi

# Verify version in metadata
if [[ -f "${WORKSPACE}/beartype/meta.py" ]]; then
    echo "[oracle] Checking version metadata"
    if grep -q "0.22.9" "${WORKSPACE}/beartype/meta.py"; then
        echo "[oracle] Version 0.22.9 confirmed in meta.py"
    else
        echo "[oracle] WARNING: Version 0.22.9 not found in meta.py" >&2
    fi
fi

# Record revision
echo "[oracle] Recording source revision: ${EXPECTED_REVISION}"
echo "${EXPECTED_REVISION}" > "${WORKSPACE}/.oracle-revision"

echo "[oracle] Oracle solution completed successfully"
echo "[oracle] Workspace ready for installation at ${WORKSPACE}"
