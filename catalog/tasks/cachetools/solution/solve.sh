#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="01af8e5b7ce44432b357e26c7d67eb7fa055ae72"
readonly ARCHIVE_SHA="67fe3a54397f9d1437464dfd149bdf54520a0c5a894eb4ab66eb1f37ea100449"
readonly ROOT="/workspace"
readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
readonly ARCHIVE="$BUNDLE_ROOT/source.tar"

printf '%s  %s\n' "$ARCHIVE_SHA" "$ARCHIVE" | sha256sum --check --strict
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?*
mkdir -p "$ROOT/.oracle/source"
tar -xf "$ARCHIVE" -C "$ROOT/.oracle/source"
cp -a "$ROOT/.oracle/source/src" "$ROOT/src"
cp "$ROOT/.oracle/source/LICENSE" "$ROOT/LICENSE"
cat > "$ROOT/pyproject.toml" <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "cachetools"
version = "7.1.7"
requires-python = ">=3.10"
license = {text = "MIT"}

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
cachetools = ["py.typed", "*.pyi"]
PYPROJECT
rm -rf "$ROOT/.oracle"
