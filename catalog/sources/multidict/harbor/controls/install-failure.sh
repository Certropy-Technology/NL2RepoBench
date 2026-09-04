#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace
printf '%s\n' 'intentional install failure control' > /workspace/README.txt
