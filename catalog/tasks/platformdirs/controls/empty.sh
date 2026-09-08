#!/bin/bash
set -euo pipefail

echo "[control:empty] Creating empty workspace"
cd /workspace
rm -rf /workspace/*
echo "[control:empty] Workspace is empty"
