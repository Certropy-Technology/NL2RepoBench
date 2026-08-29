#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
ln -s /etc/passwd /workspace/candidate-controlled-link
