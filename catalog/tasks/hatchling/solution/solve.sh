#!/usr/bin/env bash
set -euo pipefail

revision="ed8e30bebf98f2fe4d70c18a32a50a8160c391cb"
source_digest="b3acd9e2fcdc976fd53eaa6f496ea2e32ad380d5046ec1bd7514c82cca5692d7"
checkout="$(mktemp -d)"
archive="$(mktemp)"
trap 'rm -rf "$checkout" "$archive"' EXIT

git -C "$checkout" init -q
git -C "$checkout" remote add origin https://github.com/pypa/hatch.git
git -C "$checkout" fetch -q --depth=1 origin "$revision"
resolved="$(git -C "$checkout" rev-parse FETCH_HEAD^{commit})"
test "$resolved" = "$revision"
git -C "$checkout" archive --format=tar FETCH_HEAD backend > "$archive"
printf '%s  %s\n' "$source_digest" "$archive" | sha256sum -c -

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" --strip-components=1 -C /workspace
