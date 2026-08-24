#!/usr/bin/env bash
set -euo pipefail
readonly URL="https://github.com/tox-dev/platformdirs"
readonly REVISION="d3cf61ce5e729f2c35f830b69e14adb7b6970a00"
readonly TREE="9a2e1a4f3e8bfcda7896d35c4e156e3d90090dbd"
readonly ARCHIVE_SHA="01837750779cd8f90d271f9b6184cf7d8d78fac37c72ce40ac97ccfb4064d572"
readonly ROOT="/workspace"
readonly SOURCE="$ROOT/.work/source"
rm -rf "$SOURCE"
mkdir -p "$SOURCE"
git init "$SOURCE" >/dev/null
git -C "$SOURCE" remote add origin "$URL"
git -C "$SOURCE" fetch --depth 1 origin "$REVISION" >/dev/null
git -C "$SOURCE" checkout --detach FETCH_HEAD >/dev/null
[[ "$(git -C "$SOURCE" rev-parse HEAD)" == "$REVISION" ]]
[[ "$(git -C "$SOURCE" rev-parse HEAD^{tree})" == "$TREE" ]]
[[ "$(git -C "$SOURCE" archive --format=tar HEAD | sha256sum | cut -d' ' -f1)" == "$ARCHIVE_SHA" ]]
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/tox.toml" "$ROOT/.pre-commit-config.yaml" "$ROOT/.proselintrc.json" "$ROOT/.readthedocs.yml"
cp -a "$SOURCE/src" "$ROOT/src"
cp "$SOURCE/LICENSE" "$ROOT/LICENSE"
mkdir -p "$ROOT/src/platformdirs"
printf '%s\n' 'from __future__ import annotations' '__version__ = "4.11.3"' '__version_tuple__ = (4, 11, 3)' > "$ROOT/src/platformdirs/version.py"
cat > "$ROOT/pyproject.toml" <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "platformdirs"
version = "4.11.3"
requires-python = ">=3.10"
license = {text = "MIT"}

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
platformdirs = ["py.typed"]
PYPROJECT
rm -rf "$ROOT/.work"
