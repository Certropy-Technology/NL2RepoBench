#!/usr/bin/env bash
set -euo pipefail

revision="66518c9104b15a89225ee255fe03d906c7e4cb35"
expected_archive="3e7ba8998c9bf652f892ee871a28277e3dfb5bfb6a9a7cf6a2e7c29483a08f12"
checkout="/tmp/google-genai-oracle"
archive="/tmp/google-genai-source.tar"

rm -rf "$checkout" "$archive"
git init --quiet "$checkout"
git -C "$checkout" remote add origin https://github.com/googleapis/python-genai
git -C "$checkout" fetch --quiet --depth 1 origin "$revision"
git -C "$checkout" checkout --quiet --detach FETCH_HEAD

actual_revision="$(git -C "$checkout" rev-parse HEAD)"
test "$actual_revision" = "$revision"
git -C "$checkout" archive --format=tar --output="$archive" HEAD
actual_archive="$(sha256sum "$archive" | cut -d' ' -f1)"
test "$actual_archive" = "$expected_archive"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace
test -f /workspace/pyproject.toml
test -f /workspace/google/genai/types.py
