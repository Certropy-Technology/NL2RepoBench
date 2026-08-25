#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="a1f52d6713dd2c2713a881d4f4d86ed68ff71cab"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly SOURCE_ARCHIVE_SHA256="5044ecd7cf9c94fda3eb3120b8400d335eb2df75a4c1a8c6d85dd10be4020329"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

test -f /workspace/setup.py
test -f /workspace/sortedcontainers/__init__.py
test "$(python -c 'import pathlib, re; print(re.search("__version__ = .([^\"]+).", pathlib.Path("/workspace/sortedcontainers/__init__.py").read_text()).group(1))')" = "2.4.0"
echo "restored sortedcontainers at $UPSTREAM_REVISION"
