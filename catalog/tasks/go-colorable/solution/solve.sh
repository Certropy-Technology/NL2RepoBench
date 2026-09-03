#!/usr/bin/env bash
set -euo pipefail

revision="8bf39a204f13f0cfcf86ab9b297c3d6e0668e54a"
upstream="https://github.com/mattn/go-colorable"
expected_source_digest="sha256:920a15ba309669f30091349025493e370edc0aeee39eec63642c2e44a848197a"
workspace="${ORACLE_WORKSPACE:-/workspace}"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git -C "$work" init -q
git -C "$work" remote add origin "$upstream"
git -C "$work" fetch --depth=1 origin "$revision"
test "$(git -C "$work" rev-parse FETCH_HEAD)" = "$revision"

actual_source_digest="$(git -C "$work" archive --format=tar --prefix=source/ "$revision" | sha256sum | awk '{print $1}')"
if [[ "${AUTHORING_PROBE:-0}" == "1" ]]; then
  printf 'source_digest=sha256:%s\n' "$actual_source_digest"
  exit 0
fi
test "sha256:$actual_source_digest" = "$expected_source_digest"

mkdir -p "$workspace"
git -C "$work" archive --format=tar "$revision" | tar -x -C "$workspace"
python3 - "$workspace/go.mod" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
path.write_text(
    "\n".join("go 1.26.5" if line.startswith("go ") else line for line in lines) + "\n",
    encoding="utf-8",
)
PY
