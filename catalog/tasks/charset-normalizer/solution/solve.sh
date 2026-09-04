#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="e239bdc5cc1eb1f0db08d4046ad531f805dbea71"
readonly ARCHIVE="/solution/source.tar"
readonly DIGEST="4846e586d01120fcea41d4a60b8d287d28e59b3060f46476f6844b83b3eb86cf"

printf '%s  %s\n' "$DIGEST" "$ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$ARCHIVE" -C /workspace
test "$REVISION" = "e239bdc5cc1eb1f0db08d4046ad531f805dbea71"
printf 'restored charset-normalizer revision %s\n' "$REVISION"
