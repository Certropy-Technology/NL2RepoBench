#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")" && pwd)
rm -rf /workspace/*
mkdir -p /workspace/build
cp "$root/package.json" "$root/package-lock.json" /workspace/
cp "$root/build"/* /workspace/build/
