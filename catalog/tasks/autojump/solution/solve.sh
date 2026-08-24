#!/usr/bin/env bash
# Oracle reference solution. Purely local: the agent image has no network and
# fetching upstream here would also leak the reference implementation.
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$root/source/." /workspace/

# The frozen upstream revision ships no test tree in the candidate workspace;
# the verifier supplies its own immutable fixture.
rm -rf /workspace/.git /workspace/tests
find /workspace -name '__pycache__' -type d -prune -exec rm -rf -- {} +
