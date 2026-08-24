#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REVISION="fd8b4511f6ec1c8a2730b9c82188d16d0d968cd3"
ARCHIVE_URL="https://github.com/JosephCrispell/coverage_shield/archive/${UPSTREAM_REVISION}.tar.gz"
ARCHIVE_SHA256="f928adfb67c932a1b39d0071fc05e3437152fde6db54a5178561734a01e5b736"
ARCHIVE_PATH="/tmp/coverage_shield-${UPSTREAM_REVISION}.tar.gz"

curl --fail --location --silent --show-error \
    --output "$ARCHIVE_PATH" \
    "$ARCHIVE_URL"
printf '%s  %s\n' "$ARCHIVE_SHA256" "$ARCHIVE_PATH" | sha256sum --check --strict

tar --extract \
    --gzip \
    --file "$ARCHIVE_PATH" \
    --directory /workspace \
    --strip-components 1
rm -rf /workspace/.github
