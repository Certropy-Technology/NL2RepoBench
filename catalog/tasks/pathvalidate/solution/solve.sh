#!/usr/bin/env bash
set -euo pipefail

readonly revision="1ca0a50fce51d5b5bd633457a72abf74dbe3112d"
readonly expected_archive_sha256="4c83bac3feec196a0a9925d5be61bbe9581310cff4f09b6372e203ba13b81918"
readonly upstream="https://github.com/thombashi/pathvalidate"
readonly archive="/tmp/pathvalidate-${revision}.tar"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
git init --quiet /workspace
git -C /workspace remote add origin "${upstream}"
git -C /workspace fetch --quiet --depth=1 origin "${revision}"
git -C /workspace checkout --quiet --detach FETCH_HEAD

resolved="$(git -C /workspace rev-parse HEAD)"
test "${resolved}" = "${revision}"
git -C /workspace archive --format=tar --prefix=pathvalidate/ HEAD > "${archive}"
actual_archive_sha256="$(sha256sum "${archive}" | cut -d' ' -f1)"
test "${actual_archive_sha256}" = "${expected_archive_sha256}"
rm -f -- "${archive}"
