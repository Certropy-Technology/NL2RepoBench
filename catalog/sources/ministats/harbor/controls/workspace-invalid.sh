#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
ln -s /etc/passwd /workspace/candidate-controlled-link
