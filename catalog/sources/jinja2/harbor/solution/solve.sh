#!/usr/bin/env bash
set -euo pipefail
revision='5ef70112a1ff19c05324ff889dd30405b1002044'
expected='61082a25b5f6e7c49a0e4c12d9aa6be8e684489e0d613dc14512e8ea0c001421'
src=/tmp/jinja2-oracle-source
archive=/tmp/jinja2-oracle.tar
cd /tmp
rm -rf "$src" /workspace
git clone --quiet https://github.com/pallets/jinja "$src"
git -C "$src" checkout --quiet --detach "$revision"
test "$(git -C "$src" rev-parse HEAD)" = "$revision"
git -C "$src" archive --format=tar HEAD > "$archive"
printf '%s  %s\n' "$expected" "$archive" | sha256sum --check --strict
mkdir -p /workspace
tar -xf "$archive" -C /workspace
