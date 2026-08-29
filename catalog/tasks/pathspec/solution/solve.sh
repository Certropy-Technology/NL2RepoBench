#!/usr/bin/env bash
set -euo pipefail

revision=df3de4595df6e8a1cfa5782b01926b4fe461a864
archive_sha256=0d8c72748d26926b3b0e7a3a983dd3135e9ad4b462388408a1bafc936a0236d9
checkout=/tmp/pathspec-oracle-source
archive=/tmp/pathspec-oracle.tar

rm -rf "$checkout" "$archive" /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
git clone --filter=blob:none --no-checkout https://github.com/cpburnz/python-pathspec "$checkout"
git -C "$checkout" checkout --detach "$revision"
test "$(git -C "$checkout" rev-parse HEAD)" = "$revision"
git -C "$checkout" archive --format=tar HEAD > "$archive"
echo "$archive_sha256  $archive" | sha256sum --check --status
tar -xf "$archive" -C /workspace
