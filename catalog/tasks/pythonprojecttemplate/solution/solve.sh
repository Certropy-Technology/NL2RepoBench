#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference implementation.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is never part of
# the agent image build context, so this reference source cannot reach a model
# agent. Task metadata declares no-network and this script performs no fetch:
# the frozen upstream tree ships inside the private Oracle bundle as
# source.tar, so an Oracle run needs no egress and no host authorization.
#
# source.tar is byte-identical to
#   git archive --format=tar f1c116379eb485c17fb1b6cd3e2454712e4e0585
# of https://github.com/franneck94/PythonProjectTemplate, whose sha256 is
# recorded as [source].source_digest in catalog/tasks/pythonprojecttemplate/task.toml.

SOURCE_ARCHIVE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/source.tar"
SOURCE_ARCHIVE_SHA256="c47d5545686d207763d3c21aafd6eb26b575dcc02ef62159fa21011ccde9413c"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# CI metadata is not part of the graded contract and is not shipped.
rm -rf /workspace/.github
