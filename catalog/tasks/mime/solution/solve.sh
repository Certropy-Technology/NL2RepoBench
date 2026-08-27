#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/broofa/mime"
UPSTREAM_REVISION="f2d1243892616c0ec1031eb5132d56e43159ecc0"
SOURCE_ARCHIVE_SHA256="8f8e826ccafe064ca20139c47422291210c5bf8998fbe32f9ef3d9706d589199"
SOURCE_ARCHIVE="/tmp/mime-source.tar"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

rm -f "$SOURCE_ARCHIVE"

# The locked runtime image intentionally contains no git.  The Oracle checks
# that the fixed commit archive endpoint is reachable, then verifies the
# task-local git archive bytes created from that exact commit before using them.
# The model agent never receives this script, archive, or source tree.
node --input-type=module - "$UPSTREAM_REVISION" <<'JS'
import {request} from 'node:https';
const revision = process.argv[2];
const url = `https://github.com/broofa/mime/archive/${revision}.tar.gz`;
const response = await new Promise((resolve, reject) => {
  const req = request(url, {headers: {'user-agent': 'nl2repobench-oracle'}}, resolve);
  req.on('error', reject);
  req.end();
});
if (response.statusCode < 300 || response.statusCode >= 400) {
  throw new Error(`source endpoint returned HTTP ${response.statusCode}`);
}
response.resume();
await new Promise((resolve) => response.once('end', resolve));
JS
cp "$SCRIPT_DIR/oracle-source.tar" "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$SCRIPT_DIR/oracle-package/." /workspace/
