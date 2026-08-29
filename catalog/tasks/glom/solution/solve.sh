#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
readonly SOURCE_SHA256="sha256:2d63af893e86e1118fefb36f94323a1d09b3a4410132aca61f00d2f45d90e408"

printf '%s  %s\n' "${SOURCE_SHA256#sha256:}" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$SOURCE_ARCHIVE" -C /workspace
