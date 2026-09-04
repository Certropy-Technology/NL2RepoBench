#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE_ARCHIVE_SHA256="b38150745012d3fa9086c1df4a4ac6a2c633914796ec8bc5509bd651f1c6ccac"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
printf '%s\n' "restored portalocker at c86f80c2505de8e44fb9d2493eb94ab96201fef6"
