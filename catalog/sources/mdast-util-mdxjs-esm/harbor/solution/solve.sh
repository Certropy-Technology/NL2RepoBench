#!/usr/bin/env bash
set -euo pipefail

revision='8d05c28d15ec5b690e7fbb08d703b0752d431109'
upstream='https://github.com/syntax-tree/mdast-util-mdxjs-esm'
expected_source_sha='a05b484b17c05730094d3b2f2458562a48d6b76fac39dcc2b7bfc5d9a33c4f87'
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
work=$(mktemp -d)
cleanup() { rm -rf "$work"; }
trap cleanup EXIT

git clone --filter=blob:none --no-checkout "$upstream" "$work/upstream"
git -C "$work/upstream" cat-file -e "${revision}^{commit}"
test "$(git -C "$work/upstream" rev-parse "${revision}^{commit}")" = "$revision"
git -C "$work/upstream" archive --format=tar "$revision" > "$work/source.tar"
printf '%s  %s\n' "$expected_source_sha" "$work/source.tar" | sha256sum --check --strict

rm -rf /workspace/*
tar -xf "$work/source.tar" -C /workspace
cp "$script_dir/package.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json
cp "$script_dir/adapter.js" /workspace/adapter.js
rm -rf /workspace/.git /workspace/node_modules
npm ci --offline --ignore-scripts --no-audit --no-fund --cache=/opt/npm-bundle/npm-cache
