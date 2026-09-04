#!/usr/bin/env bash
set -euo pipefail
readonly REVISION="61fe449bd5bf9ae48211e822a7eefa5cb07c11d3"
readonly ARCHIVE_SHA256="3a426232fcb6ae371250e4e54428adb7b606ba77802bcf35025d059628082f0d"
readonly ARCHIVE="/solution/source.tar"
printf '%s  %s\n' "$ARCHIVE_SHA256" "$ARCHIVE" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$ARCHIVE" -C /workspace
find /workspace -type l -delete
rm -rf /workspace/.git /workspace/.github /workspace/doc /workspace/demo
printf 'restored cffi at %s\n' "$REVISION"
