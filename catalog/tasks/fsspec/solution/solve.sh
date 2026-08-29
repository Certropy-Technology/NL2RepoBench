#!/usr/bin/env bash
set -euo pipefail
readonly UPSTREAM_URL="https://github.com/fsspec/filesystem_spec"
readonly UPSTREAM_REVISION="9b7cd481e5d1c4395752e69653443e6b05ac9a3e"
readonly SOURCE_ARCHIVE_SHA256="9a0fc72facc3b4b8adc7ae9d6719e7d06e7a9a677ddab826931d71079e688e0a"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/fsspec-oracle-source"
rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/fsspec/tests" "$ROOT/fsspec/implementations/tests" "$ROOT/docs" "$ROOT/.github"
python - <<'PY'
from pathlib import Path
p = Path('/workspace/pyproject.toml')
s = p.read_text()
s = s.replace('dynamic = ["version"]', 'version = "2026.7.0"')
for section in ('[tool.hatch.version]', '[tool.hatch.build.hooks.vcs]'):
    start = s.find(section)
    if start >= 0:
        end = s.find('\n[', start + 1)
        s = s[:start] + (s[end + 1:] if end >= 0 else '')
p.write_text(s)
PY
echo "restored fsspec at $UPSTREAM_REVISION"
