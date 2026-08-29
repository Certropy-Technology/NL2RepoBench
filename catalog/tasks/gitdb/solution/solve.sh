#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE_ARCHIVE_SHA256="a026ca9823f88bfb5344472d380d03946cd863265560d9545eb0a27695ea73fc"
readonly SOURCE_ARCHIVE="/solution/source.tar"
printf "%s  %s\\n" "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
printf "restored gitdb at 009e227ffa19a2b84704c14e3a99fb1fbd937d5b\\n"
