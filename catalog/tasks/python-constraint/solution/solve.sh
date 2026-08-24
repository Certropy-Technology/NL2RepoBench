#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE_ARCHIVE_SHA256="c15171bf0b6e8271e099566d5acef4c322e2d2efa13dd1f92cb3370b5f4675ff"
readonly SOURCE_ARCHIVE="/solution/source.tar"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
echo "restored python-constraint at d91ba03d1fd6acc30d64fd9d513dc0523f697b5b"
