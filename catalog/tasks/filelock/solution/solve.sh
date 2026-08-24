#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="1717a58d7ef0983c84bda07efb11fe46f98accaf4ab2581961f32d5e84f7b7f1"
readonly ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
readonly SOURCE_TAR="$ROOT/source/filelock-source.tar"
readonly WORKSPACE="/workspace"

rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_TAR" | sha256sum --check --strict
tar -xf "$SOURCE_TAR" -C "$WORKSPACE"

# The upstream release derives version metadata from Git. The reference source
# is intentionally a verified Git archive, so add only its release-generated
# version module and make the PEP 621 version static for archive installation.
install -m 0444 "$ROOT/source/version.py" "$WORKSPACE/src/filelock/version.py"
python - "$WORKSPACE/pyproject.toml" <<'PY2'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = 'dynamic = [\n  "version",\n]\n'
if old not in text:
    raise SystemExit("missing expected dynamic version declaration")
path.write_text(text.replace(old, 'version = "3.32.3"\n', 1), encoding="utf-8")
PY2
rm -rf "$WORKSPACE/.git" "$WORKSPACE/.github" "$WORKSPACE/.pytest_cache"
