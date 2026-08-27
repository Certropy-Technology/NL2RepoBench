#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REVISION="2a4378bdc2eac9cf7d0cdfe0a52b1b25f779806a"
SOURCE_GIT_ARCHIVE_SHA256="3f687bc9c8904b92fecad8d73b002e879fa1d7b10543666b4daddfcdfaf4c565"
SOURCE_TARBALL_SHA256="39e592f3246a8bf8833eaf5cd173b5abc9030cd901dfdbc96bae7c68161c1260"
SOURCE_ARCHIVE="/tmp/yargs-${UPSTREAM_REVISION}.tar.gz"
SOURCE_ROOT="/tmp/yargs-source"

rm -f "$SOURCE_ARCHIVE"
rm -rf "$SOURCE_ROOT"
mkdir -p "$SOURCE_ROOT"
node /solution/fetch-source.mjs "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_TARBALL_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1 -C "$SOURCE_ROOT"

(
  cd "$SOURCE_ROOT"
  sha256sum --check --strict /solution/source-files.sha256
)

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$SOURCE_ROOT/." /workspace/
rm -rf /workspace/build
cp -a /solution/build /workspace/build
node /solution/prepare-package.mjs /workspace/package.json
cp /solution/runtime-package-lock.json /workspace/package-lock.json
chmod 0444 /workspace/package.json /workspace/package-lock.json

printf 'oracle source revision %s verified; git-archive sha256 %s\n' \
  "$UPSTREAM_REVISION" "$SOURCE_GIT_ARCHIVE_SHA256"
