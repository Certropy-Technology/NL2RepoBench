#!/usr/bin/env bash
set -euo pipefail

upstream_url="https://github.com/alexeyraspopov/picocolors"
revision="0e7c4af2de299dd7bc5916f2bddd151fa2f66740"
archive_digest="9d10d821b37e7b160c5d6447d3683fded0893880a2c4b95213be94903c25bb91"
source_dir="/tmp/picocolors-source"
archive="/tmp/picocolors-source.tar"

rm -rf "$source_dir" "$archive"
git init -q "$source_dir"
git -C "$source_dir" remote add origin "$upstream_url"
git -C "$source_dir" fetch -q --depth 1 origin "$revision"
test "$(git -C "$source_dir" rev-parse FETCH_HEAD)" = "$revision"
git -C "$source_dir" archive --format=tar "$revision" > "$archive"
printf '%s  %s\n' "$archive_digest" "$archive" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace

# The upstream package has no runtime dependencies. Keep the Oracle install
# contract identical to the candidate contract and avoid development packages.
node - <<'NODE'
const fs = require('node:fs');
const path = '/workspace/package.json';
const packageJson = JSON.parse(fs.readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
fs.writeFileSync(path, JSON.stringify(packageJson, null, 2) + '\n');
NODE
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "picocolors",
  "version": "1.1.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {"name": "picocolors", "version": "1.1.1", "license": "ISC"}
  }
}
JSON
rm -f /workspace/.npmrc
