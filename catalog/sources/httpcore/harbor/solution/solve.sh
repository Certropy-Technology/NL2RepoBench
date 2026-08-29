#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="8af2769a68cdd7e3b25786f439228ed9b8eed2fb7fb5076d9b173d93d2bc6143"
readonly SOURCE_ARCHIVE="/solution/source.tar"
printf "%s  %s\n" "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
tar -xf "$SOURCE_ARCHIVE" -C /workspace
test "$(git -C /workspace rev-parse HEAD 2>/dev/null || true)" = "" \
  || { echo "unexpected VCS metadata in Oracle archive" >&2; exit 1; }
echo "restored httpcore at 10a658221deb38a4c5b16db55ab554b0bf731707"
