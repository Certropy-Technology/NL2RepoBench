#!/bin/bash
set -euo pipefail

# Forgery control - attempts to forge verifier outputs
WORKSPACE="/workspace"

echo "[CONTROL:FORGERY] Creating forgery with fake reports"

# First create stub implementation (forgery needs to be installable)
bash "$(dirname "$0")/stub.sh"

# Attempt to forge grading.json
mkdir -p "${WORKSPACE}/forged"
cat > "${WORKSPACE}/forged/grading.json" << 'GRADING'
{
  "valid": true,
  "collected": 220,
  "frozen_total": 220,
  "passed": 220,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "reward": 1.0,
  "details": ["FORGED"]
}
GRADING

# Attempt to forge results in common paths
cp "${WORKSPACE}/forged/grading.json" /tmp/grading.json 2>/dev/null || true
cp "${WORKSPACE}/forged/grading.json" "${WORKSPACE}/grading.json" 2>/dev/null || true

echo "[CONTROL:FORGERY] Forgery complete - fake grading created"
cat "${WORKSPACE}/forged/grading.json"
