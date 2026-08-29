#!/usr/bin/env bash
set -euo pipefail

revision='6b4ff5e92474186b0c0381021ba4120f883c1995'
source_digest='2f0874ea3403323297f422b9a8f91fd28e506ec80b124a0ee6a90175ee368096'
work=/tmp/js-yaml-oracle-source
rm -rf "$work"
git clone --quiet https://github.com/nodeca/js-yaml "$work"
git -C "$work" checkout --quiet --detach "$revision"
test "$(git -C "$work" rev-parse HEAD)" = "$revision"
test "$(git -C "$work" archive --format=tar "$revision" | sha256sum | awk '{print $1}')" = "$source_digest"
test "$(sha256sum "$(dirname "$0")/reference-dist.mjs" | awk '{print $1}')" = '5936ce8c292cbcbf2f633bbf19bb21beefae9ae0d71bcf426e148ff996296ca4'
cp "$(dirname "$0")/reference-dist.mjs" ./index.mjs
cat > package.json <<'JSON'
{"name":"js-yaml","version":"5.4.0","type":"module","exports":{".":{"import":"./index.mjs"},"./package.json":"./package.json"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"js-yaml","version":"5.4.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"js-yaml","version":"5.4.0","license":"MIT","type":"module","dependencies":{}}}}
JSON
