#!/usr/bin/env bash
# Oracle reference solution: purely local extraction of the frozen upstream
# source. The agent image is no-network and this script must never fetch, so the
# pinned revision travels inside the private oracle bundle instead.
set -euo pipefail

SOURCE_ARCHIVE="/solution/source.tar"
SOURCE_ARCHIVE_SHA256="718fc6887ae9165aaf5f751780416ead8ce82844a2f615543f43acfaac7d4cff"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

test -f /workspace/setup.py
test -f /workspace/pyproject.toml
test -f /workspace/schedule/__init__.py
