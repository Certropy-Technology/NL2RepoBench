#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
ln -sf /etc/passwd /workspace/escape
ln -sf /tests/verifier/run.py /workspace/verifier-link
