#!/usr/bin/env bash
# Oracle reference solution.
#
# The frozen upstream source travels inside the private oracle bundle, which the
# compiler extracts to /solution. The agent stage is no-network, so this script
# must be purely local: fetching here would both fail and risk exposing a
# reference-source endpoint. The content is proven by the pinned archive digest,
# which equals [source].source_digest for revision
# 82a43db1b938d8fdf60103bd41f329e06c8d3651.
set -euo pipefail

SOURCE_ARCHIVE="/solution/source.tar"
SOURCE_ARCHIVE_SHA256="718fc6887ae9165aaf5f751780416ead8ce82844a2f615543f43acfaac7d4cff"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

test -f /workspace/setup.py
test -f /workspace/pyproject.toml
test -f /workspace/schedule/__init__.py
