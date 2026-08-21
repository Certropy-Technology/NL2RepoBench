#!/usr/bin/env bash
set -euo pipefail

REV="ff3ac3838287d28bee6f6ef0302584c4f4858528"
SRC=/tmp/graphneuralnetwork-src

rm -rf "$SRC"
git init "$SRC" >/dev/null
git -C "$SRC" remote add origin https://github.com/shenweichen/GraphNeuralNetwork.git
git -C "$SRC" fetch --depth 1 origin "$REV" >/dev/null
git -C "$SRC" checkout --detach FETCH_HEAD >/dev/null

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
git -C "$SRC" archive --format=tar HEAD | tar -x -C /workspace

printf 'Materialized GraphNeuralNetwork at %s\n' "$REV"
