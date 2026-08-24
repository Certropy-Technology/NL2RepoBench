#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
python - <<'PY'
from pathlib import Path
import shutil
import tarfile
import urllib.request

revision = 'd26fc0c3944fe68cf169f86386988bb83e3df2d8'
archive = Path('/tmp/pydantic-settings.tar.gz')
urllib.request.urlretrieve(
    f'https://github.com/pydantic/pydantic-settings/archive/{revision}.tar.gz', archive
)
with tarfile.open(archive, 'r:gz') as source:
    source.extractall('/tmp/source', filter='data')
root = next(Path('/tmp/source').iterdir())
shutil.copytree(root, '/workspace', dirs_exist_ok=True)
PY
