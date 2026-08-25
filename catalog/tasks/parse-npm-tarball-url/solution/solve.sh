#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-/workspace}"
(cd "$here" && sha256sum -c source.tar.sha256)
(cd "$here" && sha256sum -c runtime.tar.sha256)
grep -Fx 'source_revision=1cf57de3b5451ba2efd42fe8ed4eb8ede6f0f706' "$here/provenance.txt" >/dev/null
grep -Fx 'source_digest=sha256:cd10dd7f52286e08ac646447dab6312bc072f89b5deca56122bb9405f429ccf2' "$here/provenance.txt" >/dev/null
grep -Fx 'runtime_dependency=semver@7.7.4' "$here/provenance.txt" >/dev/null

test "$(sha256sum "$here/source.tar" | awk '{print $1}')" = cd10dd7f52286e08ac646447dab6312bc072f89b5deca56122bb9405f429ccf2
rm -rf "$target"
mkdir -p "$target"
tar -xf "$here/runtime.tar" -C "$target" --strip-components=1
test -f "$target/package.json"
test -f "$target/package-lock.json"
test -f "$target/lib/index.js"
test -f "$target/lib/index.d.ts"
