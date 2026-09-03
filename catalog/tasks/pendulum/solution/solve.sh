#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/sdispater/pendulum"
readonly UPSTREAM_REVISION="0d71391ab2b617b2e86d15c926e6cde9fddc5676"
readonly SOURCE_ARCHIVE_SHA256="bcc6303eabd924e272cde41cf251ef7c0a383594a67633bfd2005f8c2f777404"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/pendulum-oracle-source"
readonly BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/tests" "$ROOT/rust" "$ROOT/poetry.lock" "$ROOT/tox.ini"

# The reference uses Maturin only to build its private PyO3 accelerator. The
# frozen extension was built for this exact CPython/architecture and is copied
# with a setuptools descriptor so the no-network verifier need not carry Cargo.
install -m 0644 "$BUNDLE_ROOT/_pendulum.cpython-312-x86_64-linux-gnu.so" "$ROOT/src/pendulum/"
install -m 0644 "$BUNDLE_ROOT/pyproject.toml" "$ROOT/pyproject.toml"
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
