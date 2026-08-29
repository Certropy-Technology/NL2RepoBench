#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="/workspace"
readonly ARCHIVE="/solution/source.tar"
readonly SOURCE_SHA256="d72b0680c99b50f5bfed07eaef12763c59e30e07e151f5181d75dbfda3d525c6"

test -f "$ARCHIVE"
printf '%s  %s\n' "$SOURCE_SHA256" "$ARCHIVE" | sha256sum --check --strict
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?* 2>/dev/null || true
tar -xf "$ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/benchmarks" "$ROOT/doc" "$ROOT/examples"
echo "restored bundled joblib revision 4ff61afd0849f18fddf5fbd137c1f02bfaed5223"
