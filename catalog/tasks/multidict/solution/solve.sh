#!/usr/bin/env bash
set -euo pipefail
readonly REVISION="86351873dcc36edb11ba1a27035f2ce2e9ff8f4e"
readonly ARCHIVE_SHA256="bfdff853c97ee413df6bde23098fbef8d6232dec8c4a2a9c2dd6a26dbd93040d"
readonly ROOT="/workspace"
readonly ARCHIVE="/solution/source.tar"
printf '%s  %s\n' "$ARCHIVE_SHA256" "$ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$ARCHIVE" -C "$ROOT"
find "$ROOT" -type l -delete
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests" "$ROOT/benchmarks" "$ROOT/CHANGES"
python3 - <<'PY'
from pathlib import Path

path = Path("/workspace/setup.py")
source = path.read_text()
needle = "import os\n"
if source.count(needle) != 1:
    raise SystemExit("unexpected setup.py import layout")
path.write_text(source.replace(needle, needle + 'os.environ.setdefault("MULTIDICT_NO_EXTENSIONS", "1")\n', 1))
PY
printf '%s\n' "restored multidict at $REVISION"
