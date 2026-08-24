#!/usr/bin/env bash
set -euo pipefail
readonly SOURCE_ARCHIVE_SHA256="bc253cb8287fdbeae24cf78801f81024fcc4317541a6334419582378940b28ce"
readonly SOURCE_ARCHIVE="/solution/source.tar"
printf "%s  %s\\n" "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
sed -i 's/^dynamic = \["version"\]$/version = "2.12.1"/; /^\[tool\.pdm\.version\]/,/^fallback_version = "0.0.0"$/d' /workspace/pyproject.toml
echo "restored anytree at 2e0a1b956172654d75aff93277ce3d883355e0bf"
