#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly SOURCE_ARCHIVE_SHA256="1bd56621359406cb343f099072ea4e52b75277a6e097a9a6fc57c86b642c0048"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace --strip-components=1
rm -rf /workspace/.github /workspace/docs /workspace/tests /workspace/benchmarks
printf '%s\n' 'restored aiohappyeyeballs d3ba49e5359746f4364fb4732b238c430833cc0b'
