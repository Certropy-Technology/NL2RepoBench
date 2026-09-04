#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE_ARCHIVE=/solution/source.tar
readonly SOURCE_SHA256=261528522499c80a3a264c33028a582476c8c460ef6411dea52b33946ad52d0b
printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" --strip-components=1 -C /workspace
test -f /workspace/pyproject.toml
printf '%s\n' 'restored opentelemetry-semantic-conventions from frozen source archive'
