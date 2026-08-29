#!/usr/bin/env bash
set -euo pipefail
root=/workspace
bundle_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p "$root"
test "$(sha256sum "$bundle_dir/source-archive.tar" | cut -d' ' -f1)" = "d59c0a2beaa4fdced120056f9e7dbbdc806f7285114168b586bf40ffac2119fb"
tar -xf "$bundle_dir/source-archive.tar" -C "$root"
cp "$bundle_dir/package.json" "$root/package.json"
cp "$bundle_dir/package-lock.json" "$root/package-lock.json"
test -s "$root/index.js"
test -s "$root/package-lock.json"
