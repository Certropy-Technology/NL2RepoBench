#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
rm -rf /workspace/*
tar -xf "$script_dir/source.tar" -C /workspace
