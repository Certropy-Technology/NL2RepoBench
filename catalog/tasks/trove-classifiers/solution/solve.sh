#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="71cb041f383cee31668d07e3302d2b09d10471a8"
readonly SOURCE_DIGEST="cf3257e1a57e7dddf0e883955c5bfb579fcd5bea3d154b6ab43748b7b78454ca"
readonly SOURCE_URL="https://github.com/pypa/trove-classifiers"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
git init -q /workspace
git -C /workspace remote add origin "$SOURCE_URL"
git -C /workspace fetch -q --depth 1 origin "$REVISION"
git -C /workspace checkout -q --detach FETCH_HEAD
test "$(git -C /workspace rev-parse HEAD)" = "$REVISION"
git -C /workspace archive --format=tar --output=/tmp/trove-classifiers-reference.tar HEAD
printf '%s  %s\n' "$SOURCE_DIGEST" /tmp/trove-classifiers-reference.tar | sha256sum -c -
