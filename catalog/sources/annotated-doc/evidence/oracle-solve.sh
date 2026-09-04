#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="/solution/source.tar.gz"
readonly SOURCE_ARCHIVE_SHA256="c7e58ce09192557605d8bbd92836d7e1d520ac9580096042c0bfd197efacf1bb"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xzf "$SOURCE_ARCHIVE" --strip-components=1 -C /workspace
test "$(grep -E '^version = ' /workspace/pyproject.toml | head -1)" = 'version = "0.0.5"'
printf 'restored annotated-doc 0.0.5 from frozen sdist\n'
