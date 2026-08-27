#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
archive="$(dirname "$0")/source.tar"
printf '%s  %s\n' "9c849ab5171036e43f8cbe8bed72ca6d6a0551a2bb83876158168381c1770d39" "$archive" | sha256sum --check --strict
tar -xf "$archive" -C /workspace
cd /workspace
export SETUPTOOLS_SCM_PRETEND_VERSION=2.9.0.post1.dev32+g48bd1af
python -m pip install --no-deps --no-build-isolation .
