#!/usr/bin/env bash
set -euo pipefail

revision='c5cf675972e68f17d0072c0e29801d09ca5c3951'
source_digest='sha256:721efc08d83c9c24c20fe61758fa379d3d6ede5dd750811289b400563946ddb9'
upstream='https://github.com/TomWright/dasel'
checkout='/tmp/go-dasel-oracle'
rm -rf "$checkout"
git init -q "$checkout"
git -C "$checkout" remote add origin "$upstream"
git -C "$checkout" fetch --quiet --depth=1 origin "$revision"
actual_revision=$(git -C "$checkout" rev-parse FETCH_HEAD)
test "$actual_revision" = "$revision"
git -C "$checkout" checkout --quiet --detach "$actual_revision"

archive=/tmp/go-dasel-source.tar
git -C "$checkout" archive --format=tar --prefix=dasel/ HEAD > "$archive"
actual_digest="sha256:$(sha256sum "$archive" | cut -d' ' -f1)"
test "$actual_digest" = "$source_digest"
tar -xf "$archive" --strip-components=1 -C /workspace
rm -rf /workspace/.git

# The frozen upstream declares Go 1.25. The task runtime is locked to 1.26.5;
# this Oracle-only normalization does not alter the selected API behavior.
cd /workspace
/usr/local/go/bin/go mod edit -go=1.26.5
# The task environment carries the digest-verified closure. Reuse it rather
# than contacting a module proxy during the Oracle solve.
rm -rf vendor
cp -a /opt/go-module-bundle/vendor vendor
cp /opt/go-module-bundle/go.sum go.sum
