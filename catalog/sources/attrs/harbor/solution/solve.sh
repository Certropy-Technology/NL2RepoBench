#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/python-attrs/attrs"
readonly UPSTREAM_REVISION="c1dc5dcba16ed827aa6dcad896b41a3afedb4e32"
readonly SOURCE_ARCHIVE_SHA256="c7ebd671099d268790f83a2bc3e51b0dc3844bafd41a71b9768567e656538fac"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"

# The frozen commit precedes its release tag, so git-archive has no describe
# name and Hatch otherwise emits 0.0. Pin the release metadata stated in the
# public contract without changing the verified source archive.
python - <<'PY'
from pathlib import Path

path = Path("/workspace/pyproject.toml")
text = path.read_text(encoding="utf-8")
old = 'dynamic = ["version", "readme"]'
if text.count(old) != 1:
    raise SystemExit("unexpected attrs dynamic metadata")
path.write_text(
    text.replace(old, 'version = "26.1.0"\ndynamic = ["readme"]'),
    encoding="utf-8",
)
PY

rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/bench"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
