#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="29a7a55c6bac1a6f705b54135dbea82d03e997c3"
readonly EXPECTED_ARCHIVE_SHA256="64c592a33b2a8e3cdd190b6bba014888aca0fe094f345c42a4c52a7fdd7e92f6"
readonly UPSTREAM_URL="https://github.com/jaraco/zipp"
readonly WORKSPACE="/workspace"

temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT

git init -q "$temporary/repository"
git -C "$temporary/repository" remote add origin "$UPSTREAM_URL"
git -C "$temporary/repository" fetch --quiet --depth 1 origin "$REVISION"
resolved="$(git -C "$temporary/repository" rev-parse FETCH_HEAD)"
test "$resolved" = "$REVISION"

git -C "$temporary/repository" archive --format=tar "$resolved" > "$temporary/source.tar"
actual_archive_sha256="$(sha256sum "$temporary/source.tar" | awk '{print $1}')"
test "$actual_archive_sha256" = "$EXPECTED_ARCHIVE_SHA256"

find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$temporary/source.tar" -C "$WORKSPACE"
rm -rf -- "$WORKSPACE/tests" "$WORKSPACE/docs" "$WORKSPACE/.github"

cat > "$WORKSPACE/LICENSE" <<'LICENSE'
MIT License

Copyright (c) 2026 Jason R. Coombs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
LICENSE
