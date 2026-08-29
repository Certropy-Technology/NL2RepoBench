#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="f33dac32bd065b835b34e7f0a48025700aae1e31"
readonly ARCHIVE_SHA256="478d1cc6726b58529aa658fc873d6d5086059e17ecefba87f3ab4083868d9df1"
readonly UPSTREAM="https://github.com/requests/requests-oauthlib"
readonly REF_ROOT="/tmp/requests-oauthlib-reference"

rm -rf "$REF_ROOT" /workspace/*
git init -q "$REF_ROOT"
git -C "$REF_ROOT" remote add origin "$UPSTREAM"
git -C "$REF_ROOT" fetch --depth=1 origin "$REVISION"
test "$(git -C "$REF_ROOT" rev-parse FETCH_HEAD)" = "$REVISION"
test "$(git -C "$REF_ROOT" archive --format=tar "$REVISION" | sha256sum | awk '{print $1}')" = "$ARCHIVE_SHA256"
git -C "$REF_ROOT" archive --format=tar "$REVISION" | tar -x -C /workspace
