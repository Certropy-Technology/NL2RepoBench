#!/usr/bin/env bash
set -euo pipefail

work=/workspace
archive=/tmp/python-discovery-source.tar
rm -rf "$work"/* "$work"/.[!.]* "$work"/..?* 2>/dev/null || true

git init -q "$work"
git -C "$work" remote add origin https://github.com/tox-dev/python-discovery.git
git -C "$work" fetch --depth=1 origin 0ef757b00a6f859529193eec31667f0ccc8b833b
test "$(git -C "$work" rev-parse FETCH_HEAD)" = "0ef757b00a6f859529193eec31667f0ccc8b833b"
git -C "$work" archive --format=tar FETCH_HEAD > "$archive"
printf '%s  %s\n' "6feb569ab3927bf2a958b4b02a667916e577b7e8565a609d9472c93072edb272" "$archive" | sha256sum --check --strict
tar -xf "$archive" -C "$work"
rm -f "$archive"
git -C "$work" status --porcelain >/dev/null

# The frozen project uses VCS-derived metadata. Make the source-only build
# reproducible in the digest-pinned image, whose candidate environment has no
# git executable; this changes packaging metadata only, not library behavior.
python - <<'PY'
from pathlib import Path

path = Path('/workspace/pyproject.toml')
text = path.read_text(encoding='utf-8')
start = text.index('requires = [', text.index('[build-system]'))
end = text.index(']\n', start) + 2
text = text[:start] + 'requires = ["hatchling==1.28.0"]\n' + text[end:]
start = text.index('dynamic = [', text.index('[project]'))
end = text.index(']\n', start) + 2
text = text[:start] + 'version = "0.1.0"\n' + text[end:]
path.write_text(text, encoding='utf-8')
PY
