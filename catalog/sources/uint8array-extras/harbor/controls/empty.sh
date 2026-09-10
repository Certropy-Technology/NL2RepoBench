#!/usr/bin/env bash
set -euo pipefail
find . -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
