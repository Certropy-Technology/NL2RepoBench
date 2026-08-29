#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="sha256:7ef01289b53574ed426a959b34621ae611bf415d17b03bb9b807f5c81e1e53ff"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

actual="sha256:$(sha256sum "$SOURCE_ARCHIVE" | awk '{print $1}')"
if [[ "$actual" != "$SOURCE_ARCHIVE_SHA256" ]]; then
  echo "source archive digest mismatch: $actual" >&2
  exit 1
fi
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT" --strip-components=1
python - <<'PY'
from pathlib import Path

path = Path("/workspace/pyproject.toml")
text = path.read_text(encoding="utf-8")
old_requires = '''requires = [
\t"setuptools>=77",
\t"setuptools_scm[toml]>=3.4.1",
\t# jaraco/skeleton#174
\t"coherent.licensed",
]'''
if text.count(old_requires) != 1 or text.count('dynamic = ["version"]') != 1:
    raise SystemExit("unexpected upstream build metadata")
text = text.replace(old_requires, 'requires = ["setuptools==84.0.0", "setuptools-scm==10.2.1"]')
text = text.replace('dynamic = ["version"]', 'version = "4.6.0"')
path.write_text(text, encoding="utf-8")
PY
echo "restored jaraco.functools at f7f4f3bcac8f70e01064dee9a8bde6cc8f997a17"
