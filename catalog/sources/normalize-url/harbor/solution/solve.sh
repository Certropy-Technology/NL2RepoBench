#!/usr/bin/env bash
set -euo pipefail

REV='863d275c21d6411a7494b8f728a515633bc01d84'
SOURCE_SHA='6c7fd8315e3feae64c76202281560a3b4a27f807d736371c783d921049ab5cfe'
URL='https://github.com/sindresorhus/normalize-url'
work=/workspace/.nl2repo-oracle-source
rm -rf "$work"
mkdir -p "$work" /workspace
git -C "$work" init -q
git -C "$work" remote add origin "$URL"
git -C "$work" fetch --depth=1 origin "$REV"
test "$(git -C "$work" rev-parse FETCH_HEAD)" = "$REV"
test "$(git -C "$work" rev-parse FETCH_HEAD)" = "$(git -C "$work" rev-parse "$REV")"
archive="$work/source.tar"
git -C "$work" archive --format=tar "$REV" > "$archive"
printf '%s  %s\n' "$SOURCE_SHA" "$archive" | sha256sum --check --strict
tar -xf "$archive" -C /workspace

rm -f /workspace/.npmrc /workspace/package.json /workspace/package-lock.json
cat > /workspace/package.json <<'JSON'
{
  "name": "normalize-url",
  "version": "9.0.1",
  "description": "Normalize a URL",
  "license": "MIT",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "normalize-url",
  "version": "9.0.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "normalize-url",
      "version": "9.0.1",
      "type": "module",
      "exports": {"types": "./index.d.ts", "default": "./index.js"}
    }
  }
}
JSON
rm -f /workspace/index.test-d.ts /workspace/test.js /workspace/readme.md
npm ci --offline --ignore-scripts --no-audit --no-fund
npm pack --ignore-scripts --pack-destination /workspace
