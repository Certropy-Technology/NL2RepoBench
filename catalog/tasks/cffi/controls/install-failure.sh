#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/cffi
printf 'this is not a Python project\n' > /workspace/README.txt
