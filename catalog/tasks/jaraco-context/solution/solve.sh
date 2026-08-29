#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/jaraco/jaraco.context"
readonly UPSTREAM_REVISION="bfcb95c784e110521fa907e890b2eea34b0ef349"
readonly SOURCE_ARCHIVE_SHA256="e228a0721648643e4d7663fc71b03cfa533d60f508fa476fcd197d41a3804328"
readonly DISTRIBUTION_VERSION="6.1.3.dev6+gbfcb95c78"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/jaraco-context-oracle-source"

rm -rf "$FETCH_ROOT"
mkdir -p "$FETCH_ROOT"
git -C "$FETCH_ROOT" init --quiet
git -C "$FETCH_ROOT" remote add origin "$UPSTREAM_URL"
git -C "$FETCH_ROOT" fetch --quiet --depth 1 --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
python - "$DISTRIBUTION_VERSION" <<'PY'
from pathlib import Path
import sys

path = Path("/workspace/pyproject.toml")
text = path.read_text(encoding="utf-8")
needle = 'dynamic = ["version"]'
if text.count(needle) != 1:
    raise SystemExit("unexpected version metadata")
path.write_text(text.replace(needle, f'version = "{sys.argv[1]}"'), encoding="utf-8")
PY
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests" "$ROOT/conftest.py"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
