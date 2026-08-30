#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="ee078d644cd1e414f7a27a3085124577584dccbdeb4bc3f0addc4b065bc4b2d1"
readonly UPSTREAM_URL="https://github.com/huggingface/tokenizers"
readonly UPSTREAM_REVISION="d5827816baedcbf1cb5b452dea8048150b6872df"
readonly WHEEL_SHA256="c7bab66836ce7eb1b7a22a0a1e11790712ca0cac6ac4cff97cbbb3ec5be51b58"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly WHEEL="/solution/tokenizers-0.23.2.dev0-cp310-abi3-manylinux_2_34_x86_64.whl"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
printf '%s  %s\n' "$WHEEL_SHA256" "$WHEEL" | sha256sum --check --strict
rm -rf /tmp/frozen-tokenizers-git /tmp/frozen-tokenizers-source
git init -q /tmp/frozen-tokenizers-git
git -C /tmp/frozen-tokenizers-git fetch --quiet --depth 1 "$UPSTREAM_URL" "$UPSTREAM_REVISION"
git -C /tmp/frozen-tokenizers-git checkout -q --detach FETCH_HEAD
test "$(git -C /tmp/frozen-tokenizers-git rev-parse HEAD)" = "$UPSTREAM_REVISION"
git -C /tmp/frozen-tokenizers-git archive --format=tar HEAD > /tmp/fetched-source.tar
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" /tmp/fetched-source.tar | sha256sum --check --strict
cmp --silent "$SOURCE_ARCHIVE" /tmp/fetched-source.tar
mkdir -p /tmp/frozen-tokenizers-source
tar -xf /tmp/fetched-source.tar -C /tmp/frozen-tokenizers-source
test -f /tmp/frozen-tokenizers-source/bindings/python/pyproject.toml
test -f /tmp/frozen-tokenizers-source/bindings/python/Cargo.toml
test -f /tmp/frozen-tokenizers-source/LICENSE

# The wheel was built from the verified archive with the pinned Rust/PyO3
# source. Unpack it into the workspace and add a local setuptools wrapper so
# Harbor's normal candidate installer can install the reference without a
# crates.io dependency during the no-network verifier phase.
python - "$WHEEL" <<'PY'
import sys
import zipfile
from pathlib import PurePosixPath

with zipfile.ZipFile(sys.argv[1]) as archive:
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts:
            raise SystemExit(f"unsafe wheel member: {member.filename}")
    archive.extractall("/workspace")
PY
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.10.2"]
build-backend = "setuptools.build_meta"

[project]
name = "tokenizers"
version = "0.23.2.dev0"
requires-python = ">=3.10"
dependencies = ["huggingface_hub>=0.16.4,<2.0"]

[tool.setuptools]
packages = ["tokenizers", "tokenizers.decoders", "tokenizers.implementations", "tokenizers.models", "tokenizers.normalizers", "tokenizers.pre_tokenizers", "tokenizers.processors", "tokenizers.tools", "tokenizers.trainers"]
package-data = {tokenizers = ["*.so"]}
TOML
printf '%s\n' "reference wheel unpacked from $SOURCE_ARCHIVE_SHA256"
