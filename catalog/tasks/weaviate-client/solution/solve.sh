#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly SOURCE_ARCHIVE_SHA256="4f8ef5b9b30a22a4503895fea6cc77fa7280d4fcf2378a92650abb0d75315152"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace --strip-components=1
python - <<'PY'
from pathlib import Path

config = Path("/workspace/setup.cfg")
text = config.read_text(encoding="utf-8")
start = text.index("packages =\n")
end = text.index("\n\nplatforms =", start)
text = text[:start] + "packages = find_namespace:" + text[end:]
text += "\n[options.packages.find]\ninclude =\n    weaviate*\n"
config.write_text(text, encoding="utf-8")
PY
rm -rf \
  /workspace/.github \
  /workspace/benchmark \
  /workspace/ci \
  /workspace/docs \
  /workspace/integration \
  /workspace/integration_embedded \
  /workspace/journey_tests \
  /workspace/mock_tests \
  /workspace/profiling \
  /workspace/proto_test \
  /workspace/test
printf '%s\n' \
  'restored weaviate-client 9f59a367f09a433826fbb045065bfcc958ff69a5'
