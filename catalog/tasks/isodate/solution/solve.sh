#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/gweis/isodate"
readonly UPSTREAM_REVISION="17cb25eb7bc3556a68f3f7b241313e9bb8b23760"
readonly SOURCE_ARCHIVE_SHA256="50b897e1c615278d8f9add946f74635564c500d01503793a0663f615eedf8622"
readonly FROZEN_VERSION="0.7.3.dev3+g17cb25eb7"
readonly FETCH_ROOT="/tmp/isodate-oracle-source"
readonly ROOT="/workspace"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
mkdir -p "$ROOT/src/isodate"
printf 'version = __version__ = "%s"\n' "$FROZEN_VERSION" > "$ROOT/src/isodate/version.py"
python - "$ROOT/pyproject.toml" "$FROZEN_VERSION" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
version = sys.argv[2]
text = path.read_text()
old = 'fallback_version = "0.0.0.dev0"'
assert text.count(old) == 1
path.write_text(text.replace(old, f'fallback_version = "{version}"'))
PY
rm -rf "$ROOT/.github" "$ROOT/tests"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
