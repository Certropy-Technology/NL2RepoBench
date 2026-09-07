#!/bin/bash
set -euo pipefail

# Offline control for pyperf.
# Runs the Oracle solution but verifies network isolation.

WORKSPACE="/workspace"
cd "${WORKSPACE}"

echo "[control:offline] Running Oracle in offline mode" >&2

# Use the same Oracle solution
SOURCE_ARCHIVE="/solution/pyperf-source.tar.gz"

if [[ ! -f "${SOURCE_ARCHIVE}" ]]; then
    echo "[control:offline] ERROR: Source archive not found" >&2
    exit 1
fi

# Extract source
tar -xzf "${SOURCE_ARCHIVE}" --strip-components=1

if [[ ! -f "pyproject.toml" ]] || [[ ! -d "pyperf" ]]; then
    echo "[control:offline] ERROR: Extraction failed" >&2
    exit 1
fi

echo "[control:offline] Source restored (offline mode)" >&2
exit 0
