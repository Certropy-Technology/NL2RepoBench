#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly SOURCE_ARCHIVE_SHA256="4babaa40d1ee3c4c92d3d0abc9d16ca29cac08130ef60e83d820fb2961c9d53c"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
printf 'restored dnspython at b723a83a2f192deda4aa341a1447689967e97889\n'
