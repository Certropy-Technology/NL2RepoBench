#!/usr/bin/env bash
set -euo pipefail

revision='ef98e0a0e77fbef1fdf8bc3bd33288b00b3103c9'
source_digest='sha256:5003fe0f3466d3c7b6a494d5aae4df4ca87d165fbede1e50b87fceaaa7f4977d'
upstream='https://github.com/beaugunderson/ip-address.git'
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
work=/workspace/.oracle-source
rm -rf "$work"
git clone --no-checkout --filter=blob:none "$upstream" "$work" >/dev/null 2>&1
git -C "$work" checkout --detach "$revision" >/dev/null 2>&1
actual=$(git -C "$work" archive --format=tar HEAD | sha256sum | awk '{print "sha256:" $1}')
test "$actual" = "$source_digest"
test "$(git -C "$work" rev-parse HEAD)" = "$revision"
rm -rf /workspace/*
cp -a "$root/oracle-package/." /workspace/
rm -rf "$work"
