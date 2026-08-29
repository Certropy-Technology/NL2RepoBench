#!/usr/bin/env bash
set -euo pipefail

readonly revision='35681f6c70f8ca2bdcb9542281147679184269fa'
readonly archive_sha256='3eabac5b48586a9a65714ad4cc4685a03705e3adcf3ee57d7ce9dabf5beb8278'
readonly index_sha256='56233d1d87da3899c15639a0dc5756546184f311ddcd7e3e6de91450bed7c55c'
readonly types_sha256='7a4e8b85a9fef02b7db31646d91b3dbc12dd81f334c20ced9d8728876e19a329'

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
checkout=$(mktemp -d /tmp/p-retry-oracle.XXXXXX)
archive=$(mktemp /tmp/p-retry-source.XXXXXX.tar)
trap 'rm -rf -- "$checkout" "$archive"' EXIT

git -C "$checkout" init --quiet
git -C "$checkout" remote add origin https://github.com/sindresorhus/p-retry.git
GIT_TERMINAL_PROMPT=0 git -C "$checkout" fetch --no-tags --depth 1 origin "$revision"
test "$(git -C "$checkout" rev-parse FETCH_HEAD)" = "$revision"
git -C "$checkout" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$checkout" rev-parse HEAD)" = "$revision"
git -C "$checkout" archive --format=tar --output="$archive" HEAD
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace
cp "$script_dir/package.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json

test "$(sha256sum /workspace/index.js | awk '{print $1}')" = "$index_sha256"
test "$(sha256sum /workspace/index.d.ts | awk '{print $1}')" = "$types_sha256"
test "$(sha256sum /workspace/package.json | awk '{print $1}')" = \
  '0991289c40ed3817b28bc02437a6eb18b53b984c6db3bf420281072b64016c07'
test "$(sha256sum /workspace/package-lock.json | awk '{print $1}')" = \
  'e20de62fe1faadd85bd26d0ca715c0defe8ad3cb737d606ae7e4c48729ba9343'

rm -rf /workspace/.git /workspace/.github /workspace/node_modules
