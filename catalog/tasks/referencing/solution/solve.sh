#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/python-jsonschema/referencing"
readonly UPSTREAM_REVISION="b081312fdf2567324d0c11fb07b630d7fcecea35"
readonly SOURCE_ARCHIVE_SHA256="b8edfe7c6ddc3e90be5a73f4fd4a72e3d9f54b60deb14bb2b55081775bb49fba"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"

# The frozen source archive contains a documentation symlink. The candidate
# workspace boundary rejects symlinks to prevent path redirection, and the
# link is outside the runtime/test contract, so remove it after verification.
find "$ROOT" -type l -delete

# The frozen revision has no release tag, so Hatch VCS metadata is unavailable
# in the archive-only Oracle environment. Pin a local build version without
# changing the implementation or the verified source archive.
python - <<'PY'
from pathlib import Path

path = Path("/workspace/pyproject.toml")
text = path.read_text(encoding="utf-8")
if text.count('dynamic = ["version"]') != 1:
    raise SystemExit("unexpected referencing dynamic metadata")
path.write_text(
    text.replace('dynamic = ["version"]', 'version = "0.0.0"'),
    encoding="utf-8",
)
PY

rm -rf "$ROOT/referencing/tests" "$ROOT/suite" "$ROOT/.github"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
