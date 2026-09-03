#!/usr/bin/env bash
set -euo pipefail

revision='2a0c02df173a8340670b59903426e741811d6ab3'
source_digest='2dbd281557752aa0463fc18e1eadaee1f5d090e1ae88149687a976afff4622e0'
repo='https://github.com/pytest-dev/pytest-xdist.git'
work='/tmp/pytest-xdist-oracle-source'
rm -rf "$work"
git clone --filter=blob:none "$repo" "$work"
test "$(git -C "$work" rev-parse HEAD)" = "$revision"
archive="$work/source.tar"
git -C "$work" archive --format=tar HEAD > "$archive"
test "$(sha256sum "$archive" | awk '{print $1}')" = "$source_digest"
rm -rf /workspace/*
tar -xf "$archive" -C /workspace
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYTEST_XDIST='3.8.1.dev93+g2a0c02df1'
python -m pip install --no-deps --no-build-isolation /workspace
python -m pytest /workspace/testing -q
