#!/usr/bin/env bash
set -euo pipefail

# Offline control for beartype task.
# This control verifies that the verifier can run without network access.
# It reuses the Oracle solution since the Oracle should work offline.

echo "[control:offline] Starting offline control"
echo "[control:offline] Reusing Oracle solution to verify offline capability"

# Run the Oracle solution
ORACLE_SCRIPT="/oracle/solve.sh"
if [[ -f "${ORACLE_SCRIPT}" ]]; then
    bash "${ORACLE_SCRIPT}"
else
    echo "[control:offline] WARNING: Oracle solution script not found at ${ORACLE_SCRIPT}"
    echo "[control:offline] Falling back to direct extraction"
    
    SOURCE_ARCHIVE="/oracle/beartype-0.22.9.tar.gz"
    WORKSPACE="/workspace"
    
    if [[ -f "${SOURCE_ARCHIVE}" ]]; then
        tar -xzf "${SOURCE_ARCHIVE}" -C "${WORKSPACE}" --strip-components=1
        echo "[control:offline] Source extracted successfully"
    else
        echo "[control:offline] ERROR: Source archive not found" >&2
        exit 1
    fi
fi

echo "[control:offline] Expected: verifier completes successfully in no-network mode"
echo "[control:offline] Offline control completed"
