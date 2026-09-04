#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="5a77b12a7a9f052ce5a20c335d2825658f6aea52"
readonly SOURCE_ARCHIVE_SHA256="200b6c7f01286ef30a889ff4742c93e333049821badb15b53b8d2c3af584e322"
readonly SOURCE_ARCHIVE="/solution/source.tar"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$SOURCE_ARCHIVE" -C /workspace
echo "restored tomli at $UPSTREAM_REVISION"
