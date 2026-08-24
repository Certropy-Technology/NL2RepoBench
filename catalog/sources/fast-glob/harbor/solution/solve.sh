#!/usr/bin/env bash
# Oracle for `fast-glob` 4.0.0 at revision
# 467b65a79ed1b84fd9fd18966deda8a4e57b8e0e.
#
# The frozen revision is TypeScript-only (`main: "out/index.js"`, no committed
# `out/`), and the verifier lane forbids lifecycle/build scripts. This Oracle is
# therefore a precompiled, scripts-stripped distribution: `tsc` ran during the
# authoring build phase under the locked Node 24.19.0 / npm 11.17.0 toolchain,
# and the emitted runtime JS is shipped here. No source is fetched at run time,
# so the Oracle is compatible with `no-network`.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-/workspace}"
mkdir -p "$target"
cd "$target"

cp -a "$here/dist-out" ./out
cp "$here/dist-package.json" ./package.json
cp "$here/dist-package-lock.json" ./package-lock.json
cp "$here/LICENSE" ./LICENSE

test -f ./out/index.js
test -f ./package.json
test -f ./package-lock.json
