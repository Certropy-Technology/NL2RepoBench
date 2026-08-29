#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM="https://github.com/jaraco/keyring"
readonly REVISION="7603e7cadc254b4c6e3fc2b2f0916a005e78087d"
readonly ARCHIVE_SHA="30dfe6cd4dcf67495e2ff1d8a3196593b5263f8d9180fe2cabc5cdc3582815a9"
readonly LICENSE_SHA="9755a18519666e5f0f4cae3daad3d7012bcae48a600b31237d75e9fe134e6683"
readonly ROOT="/workspace"
readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
readonly FETCH_ROOT="/tmp/nl2repo-keyring-oracle"
readonly SOURCE="$FETCH_ROOT/source"
readonly ARCHIVE="$FETCH_ROOT/source.tar"

rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?*
rm -rf "$FETCH_ROOT"
mkdir -p "$SOURCE"
git -C "$SOURCE" init --quiet
git -C "$SOURCE" remote add origin "$UPSTREAM"
git -C "$SOURCE" fetch --quiet --depth=1 origin "$REVISION"
git -C "$SOURCE" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$SOURCE" rev-parse HEAD)" = "$REVISION"
git -C "$SOURCE" archive --format=tar --output="$ARCHIVE" HEAD
printf '%s  %s\n' "$ARCHIVE_SHA" "$ARCHIVE" | sha256sum --check --strict
test -f "$SOURCE/keyring/core.py"
test -f "$SOURCE/keyring/backend_complete.bash"
grep -Fq 'license = "MIT"' "$SOURCE/pyproject.toml"
cp -a "$SOURCE"/. "$ROOT"/
printf '%s  %s\n' "$LICENSE_SHA" "$BUNDLE_ROOT/LICENSE" | sha256sum --check --strict
install -m 0644 "$BUNDLE_ROOT/LICENSE" "$ROOT/LICENSE"
rm -rf "$FETCH_ROOT"
