#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-/workspace}"
archive="$here/source.tar"
expected_archive="4b815834ee052cbd62e39ae63019905344135368cd48f0dfcbbcaf7635e3ec9a"
expected_runtime="9bd765def21a6704a6d7e54ecf76004811ba7df19b387b60e04740785794e376"

printf '%s  %s\n' "$expected_archive" "$archive" | sha256sum --check --strict
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
tar -xf "$archive" -C "$scratch" lodash.js package.json LICENSE
printf '%s  %s\n' "$expected_runtime" "$scratch/lodash.js" | sha256sum --check --strict
node -e '
  const manifest = require(process.argv[1]);
  if (manifest.name !== "lodash" || manifest.version !== "4.18.1" || manifest.license !== "MIT") process.exit(1);
' "$scratch/package.json"

mkdir -p "$target"
cp "$scratch/lodash.js" "$target/lodash.js"
cp "$scratch/LICENSE" "$target/LICENSE"
cp "$here/package.json" "$target/package.json"
cp "$here/package-lock.json" "$target/package-lock.json"
