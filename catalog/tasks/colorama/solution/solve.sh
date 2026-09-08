#!/usr/bin/env bash
set -euo pipefail

# Oracle solution for colorama 0.4.6 (BSD-3-Clause)

echo "[oracle] Starting colorama Oracle solution"

# Expected source digest
EXPECTED_DIGEST="4dcbc68fed507dbab180aa86538b823cb9af697280dc39aa2cba9a7b9b13a141"
EXPECTED_REVISION="4ea8b1c7cbf96cc21613bb51b38fc49831fdddb4"

# Use BUNDLE_DIR to locate artifacts (compiler extracts bundle to /solution)
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ARCHIVE="${BUNDLE_DIR}/source.tar.gz"
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

# Extract source archive (tar topology: colorama-4ea8b1c7.../ prefix)
echo "[oracle] Extracting source archive to ${WORKSPACE}"
tar -xzf "${SOURCE_ARCHIVE}" -C "${WORKSPACE}" --strip-components=1

# Verify extraction
if [[ ! -f "${WORKSPACE}/pyproject.toml" ]]; then
    echo "[oracle] ERROR: pyproject.toml not found after extraction" >&2
    exit 1
fi

if [[ ! -d "${WORKSPACE}/colorama" ]]; then
    echo "[oracle] ERROR: colorama/ directory not found after extraction" >&2
    exit 1
fi

# Verify version in __init__.py (hatchling uses path-based version)
if [[ -f "${WORKSPACE}/colorama/__init__.py" ]]; then
    echo "[oracle] Checking version metadata"
    if grep -q "__version__ = '0.4.6'" "${WORKSPACE}/colorama/__init__.py"; then
        echo "[oracle] Version 0.4.6 confirmed in __init__.py"
    else
        echo "[oracle] WARNING: Version string not found in __init__.py" >&2
    fi
fi

# Record revision
echo "[oracle] Recording source revision: ${EXPECTED_REVISION}"
echo "${EXPECTED_REVISION}" > "${WORKSPACE}/.oracle-revision"

echo "[oracle] Oracle solution completed successfully"
echo "[oracle] Workspace ready for installation at ${WORKSPACE}"
