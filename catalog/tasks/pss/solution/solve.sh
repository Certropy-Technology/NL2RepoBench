#!/usr/bin/env bash
# Oracle reference solution. Purely local: the agent image has no network and
# fetching upstream here would also leak the reference implementation.
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$root/source/." /workspace/

# The candidate workspace never supplies the scored tests; the verifier copies
# its own immutable fixture. Removing the upstream tree here keeps the candidate
# from shadowing that fixture through its installed site directory.
rm -rf /workspace/.git /workspace/test
find /workspace -name '__pycache__' -type d -prune -exec rm -rf -- {} +
