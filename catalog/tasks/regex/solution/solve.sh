#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/mrabarnett/mrab-regex"
UPSTREAM_REVISION="1760a20647f1c2ddcc025128407fe6f7edb905a1"
SOURCE_ARCHIVE_SHA256="380b288264f32f0ea2d5da32cf06277c5dca37681c308b97433ddf22cb882434"
SOURCE_DIR="/tmp/regex-source"
SOURCE_ARCHIVE="/tmp/regex-source.tar"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# The Oracle image owns the frozen reference and may use its preinstalled
# build toolchain. The candidate path is separately tested through the
# hash-locked build contract in the verifier image.
cd /workspace
export PYTHONPATH=/opt/candidate-dependencies/site
python -c 'import setuptools; print("oracle-setuptools", setuptools.__version__)'
python setup.py build_ext --inplace
rm -rf /tmp/regex-oracle-site
python -m pip install --no-deps --no-build-isolation --target /tmp/regex-oracle-site /workspace
export PYTHONPATH=/tmp/regex-oracle-site:/opt/candidate-dependencies/site
