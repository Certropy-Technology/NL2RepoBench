#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/jaraco/jaraco.classes"
readonly UPSTREAM_REVISION="eeccd0b835bccf18353c44f4b35a1a27c9284fce"
readonly SOURCE_ARCHIVE_SHA256="4c3f9931ea112ae1f06448efe329ab40a700ed8f484cf32431e2cb66b7ddd28f"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/jaraco-classes-source"

rm -rf "$FETCH_ROOT"
mkdir -p "$FETCH_ROOT"
python - <<'PY'
from pathlib import Path
from urllib.request import urlopen

revision = "eeccd0b835bccf18353c44f4b35a1a27c9284fce"
url = f"https://codeload.github.com/jaraco/jaraco.classes/tar.gz/{revision}"
data = urlopen(url, timeout=30).read()
Path("/tmp/jaraco-classes-source/source.tar.gz").write_bytes(data)
PY
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar.gz" | sha256sum --check --strict
archive_root="$(tar -tzf "$FETCH_ROOT/source.tar.gz" | sed -n '1p' | cut -d/ -f1)"
test "$archive_root" = "jaraco.classes-$UPSTREAM_REVISION"
tar -xzf "$FETCH_ROOT/source.tar.gz" -C "$FETCH_ROOT"
test -f "$FETCH_ROOT/$archive_root/pyproject.toml"
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?* 2>/dev/null || true
cp -a "$FETCH_ROOT/$archive_root"/. "$ROOT"/

# The frozen branch has no release tag in the archive. Keep the package
# installable without SCM state while leaving the verified Python sources
# unchanged.
python - <<'PY'
from pathlib import Path

path = Path("/workspace/pyproject.toml")
text = path.read_text(encoding="utf-8")
old = '''[build-system]
requires = [
	"setuptools>=77",
	"setuptools_scm[toml]>=3.4.1",
	# jaraco/skeleton#174
	"coherent.licensed",
]
build-backend = "setuptools.build_meta"'''
new = '''[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"'''
if text.count(old) != 1:
    raise SystemExit("unexpected upstream build-system block")
text = text.replace(old, new)
if text.count('dynamic = ["version"]') != 1:
    raise SystemExit("unexpected upstream dynamic version declaration")
text = text.replace('dynamic = ["version"]', 'version = "0.1.0"')
path.write_text(text, encoding="utf-8")
PY

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
