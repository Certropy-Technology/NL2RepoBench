#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_archive="$script_dir/source.tar"

printf '%s  %s\n' \
  '87c578912149794beb4bd95f69199067eccab4a2b8867c95993b03187256f797' \
  "$source_archive" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$source_archive" -C /workspace
cp "$script_dir/package.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json

test "$(sha256sum /workspace/index.js | awk '{print $1}')" = \
  '30fa94b6aebe7f044f7383feee7931fc7c1a4912affadac97539cda67c14057d'
test "$(sha256sum /workspace/index.d.ts | awk '{print $1}')" = \
  '172c7feeb0cbc159e09810b076a1b6584d769ba15052b77c88e281c1221c23ca'
test "$(sha256sum /workspace/package.json | awk '{print $1}')" = \
  '4d378a1ce99db48704135b36b69422fcaa7e5bd5c4b1ca58dc37fad59ae1799c'
test "$(sha256sum /workspace/package-lock.json | awk '{print $1}')" = \
  'fb7c92ed670103eb70f595bddfb6e78e6307b5418b0a3c64f1b7d2cf9e33d688'

rm -rf /workspace/.github /workspace/node_modules
