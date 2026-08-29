#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="b4241c8e34dd1432b9870b56f9f1056eede939b3486d9f0434c7fc6a08c5c01f"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly REVISION="3fba7d3e19c84e5bb1f15c22b1a5a6db6e8f07c7"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace

# The archive is source-only and has no SCM metadata. Pin the release value
# stated by the frozen source rather than allowing an unavailable VCS lookup.
python - <<'PY'
from pathlib import Path

path = Path("/workspace/setup.cfg")
text = path.read_text(encoding="utf-8")
if "version = attr: distro.__version__" not in text:
    raise SystemExit("unexpected distro metadata")
path.write_text(text.replace("version = attr: distro.__version__", "version = 1.9.0"), encoding="utf-8")
PY

# The upstream test fixtures intentionally contain symlink entries. They are
# outside the candidate package boundary and would be rejected by the Harbor
# workspace copier, so Oracle retains only the installable source tree.
rm -rf /workspace/tests

echo "restored python-distro/distro at $REVISION"
