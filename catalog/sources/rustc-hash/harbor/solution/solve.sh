#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/src
tar -xf /solution/source.tar -C /workspace
