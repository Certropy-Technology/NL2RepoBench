#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE_ARCHIVE_SHA256="74c9fa75d3899c423d551d5cc673e470680a6b34e1a45cec99125c67e458c7da"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly REVISION="51e9a9f148cd2509a31e3fa0d2b1b3204c2b0dd7"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$SOURCE_ARCHIVE" -C /workspace --strip-components=1
python3 - <<'PY'
from pathlib import Path

path = Path("/workspace/pyproject.toml")
source = path.read_text()
needle = '[tool.setuptools_scm]\nwrite_to = "src/_pytest/_version.py"\n'
if source.count(needle) != 1:
    raise SystemExit("unexpected setuptools-scm configuration")
path.write_text(source.replace(needle, needle + 'fallback_version = "9.2.0.dev277"\n', 1))
PY
test "$REVISION" = "51e9a9f148cd2509a31e3fa0d2b1b3204c2b0dd7"
echo "restored pytest at $REVISION"
