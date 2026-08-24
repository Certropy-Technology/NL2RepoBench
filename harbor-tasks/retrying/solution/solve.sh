#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference implementation, uploaded exclusively by the Oracle agent.
# harbor/solution/ is never part of the agent image build context, so this never
# reaches a model agent. The copy is purely local: the agent phase is
# no-network, and fetching upstream at run time would also leak the reference.
#
# source/ is the verbatim expansion of
#   git archive --format=tar 3a435e8ba85d85d7300a3609cb6f3ba8cb4bc170
# whose tar digest is sha256:de12f17823ab9b4d10e40e16afa94a77038c25df63b961279085948a3fffd6b3.

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$root/source/." /workspace/
# The hidden slice is supplied by the verifier; shipping the upstream copy would
# let a candidate-visible test file shadow it.
rm -rf /workspace/.git /workspace/.github /workspace/test_retrying.py
