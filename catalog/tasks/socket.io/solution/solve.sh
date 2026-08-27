#!/usr/bin/env bash
set -euo pipefail

readonly SOLUTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GIT_ROOT="/tmp/socketio-oracle-git"
readonly SOURCE_DIR="/tmp/socketio-oracle-source"
readonly SOURCE_ARCHIVE="/tmp/socketio-oracle-source.tar"
readonly UPSTREAM_REVISION="ae7fb46e08c5ed964b4a1ea8b1703e816511598e"
readonly SOURCE_ARCHIVE_SHA256="c3d386e859d6d51c8eb2672f1cec9db6bba05eba3cfc9bc35e5aef649f0b85eb"

rm -rf "$GIT_ROOT" "$SOURCE_DIR" "$SOURCE_ARCHIVE"
mkdir -p "$GIT_ROOT" "$SOURCE_DIR"

(
  cd "$SOLUTION_DIR/git-runtime"
  sha256sum --check --strict SHA256SUMS
)
for package in "$SOLUTION_DIR"/git-runtime/*.deb; do
  dpkg-deb --extract "$package" "$GIT_ROOT"
done

export PATH="$GIT_ROOT/usr/bin:$PATH"
export GIT_EXEC_PATH="$GIT_ROOT/usr/lib/git-core"
export GIT_TEMPLATE_DIR="$GIT_ROOT/usr/share/git-core/templates"
export GIT_SSL_CAINFO="$SOLUTION_DIR/git-runtime/ca-certificates.crt"
export LD_LIBRARY_PATH="$GIT_ROOT/lib/x86_64-linux-gnu:$GIT_ROOT/usr/lib/x86_64-linux-gnu"

git -C "$SOURCE_DIR" init -q
git -C "$SOURCE_DIR" remote add origin https://github.com/socketio/socket.io
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
if [[ "$resolved_revision" != "$UPSTREAM_REVISION" ]]; then
  printf 'resolved revision mismatch: %s\n' "$resolved_revision" >&2
  exit 1
fi
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

(
  cd "$SOLUTION_DIR/reference"
  sha256sum --check --strict SHA256SUMS
)
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$SOLUTION_DIR/reference/dist" /workspace/dist
cp "$SOLUTION_DIR/reference/package.json" /workspace/package.json
cp "$SOLUTION_DIR/reference/package-lock.json" /workspace/package-lock.json
cp "$SOLUTION_DIR/reference/wrapper.mjs" /workspace/wrapper.mjs
