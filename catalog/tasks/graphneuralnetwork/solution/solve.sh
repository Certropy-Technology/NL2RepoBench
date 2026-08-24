#!/usr/bin/env bash
# Oracle-only reference implementation.
#
# harbor/solution/ is uploaded by the Oracle agent alone and is never part of
# the agent image build context, so the frozen source never reaches a model
# agent. This script is purely local: the agent phase is no-network and any
# fetch here would both fail and risk leaking the reference implementation.
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/shenweichen/GraphNeuralNetwork"
readonly UPSTREAM_REVISION="ff3ac3838287d28bee6f6ef0302584c4f4858528"
readonly SOURCE_ARCHIVE_SHA256="87ed47cd36eb0c977d89a44a9d7b08c12f2c0817362e92401f152c3ed1e71183"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

# source.tar is sha256(git archive --format=tar <revision>) of the pinned
# revision, recorded as [source].source_digest in the catalog task.
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"

# The upstream tests directory is the candidate-authored surface in this task;
# the hidden slice lives in the verifier image, so it is dropped here to keep
# the Oracle workspace equivalent to a completed agent submission.
rm -rf "$ROOT/tests" "$ROOT/.github"

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
