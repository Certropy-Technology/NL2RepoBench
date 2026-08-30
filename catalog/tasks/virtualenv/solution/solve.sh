#!/usr/bin/env bash
set -euo pipefail

repo_url="https://github.com/pypa/virtualenv"
revision="2a645aece0241e6dc02bf3d67acd88aa0770b601"
archive_digest="362a56eab724517cdcc3d8206bc36a562d4a51231256fd47f71dd9c6dabebe7a"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
git clone --no-checkout "$repo_url" /workspace
git -C /workspace fetch --depth=1 origin "$revision"
git -C /workspace checkout --detach "$revision"
test "$(git -C /workspace rev-parse HEAD)" = "$revision"
test "$(git -C /workspace archive --format=tar "$revision" | sha256sum | awk '{print $1}')" = "$archive_digest"
mkdir /tmp/virtualenv-source
git -C /workspace archive "$revision" | tar -x -C /tmp/virtualenv-source
rm -rf /workspace/.git /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
cp -a /tmp/virtualenv-source/. /workspace/
rm -rf /tmp/virtualenv-source
