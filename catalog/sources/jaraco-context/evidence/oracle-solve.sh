#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="bfcb95c784e110521fa907e890b2eea34b0ef349"
readonly SOURCE_ARCHIVE_SHA256="e228a0721648643e4d7663fc71b03cfa533d60f508fa476fcd197d41a3804328"
readonly DISTRIBUTION_VERSION="6.1.3.dev6+gbfcb95c78"
readonly ROOT="/workspace"
readonly SOURCE_ARCHIVE="/solution/source.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
python - "$DISTRIBUTION_VERSION" <<'PY'
from pathlib import Path
import sys

path = Path("/workspace/pyproject.toml")
text = path.read_text(encoding="utf-8")
needle = 'dynamic = ["version"]'
if text.count(needle) != 1:
    raise SystemExit("unexpected version metadata")
plugin = '\t"coherent.licensed",\n'
if text.count(plugin) != 1:
    raise SystemExit("unexpected coherent.licensed metadata")
text = text.replace(plugin, "")
path.write_text(text.replace(needle, f'version = "{sys.argv[1]}"'), encoding="utf-8")
PY
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests" "$ROOT/conftest.py"
echo "restored jaraco.context at $UPSTREAM_REVISION"
