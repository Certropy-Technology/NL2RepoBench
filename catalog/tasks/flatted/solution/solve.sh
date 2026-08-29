#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/WebReflection/flatted"
readonly REVISION="e6f5ca700c4ca8104a6a83472c8219e267bd5e84"
readonly SOURCE_DIGEST="e784adfcfef6c281d5700256dc1762b704eb11943cad7a46c18029c1a9e04c2a"
readonly WORK="/tmp/flatted-oracle"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* "$WORK"
mkdir -p "$WORK"
git clone --no-checkout "$UPSTREAM_URL" "$WORK/source" >/dev/null
git -C "$WORK/source" fetch --depth=1 origin "$REVISION" >/dev/null
git -C "$WORK/source" checkout --detach "$REVISION" >/dev/null
test "$(git -C "$WORK/source" rev-parse HEAD)" = "$REVISION"
git -C "$WORK/source" archive --format=tar HEAD > "$WORK/source.tar"
test "$(sha256sum "$WORK/source.tar" | cut -d' ' -f1)" = "$SOURCE_DIGEST"

mkdir -p /workspace/cjs /workspace/esm /workspace/types
cp "$WORK/source/LICENSE" /workspace/LICENSE
cp "$WORK/source/README.md" /workspace/README.md
cp "$WORK/source/cjs/index.js" /workspace/cjs/index.js
cp "$WORK/source/cjs/package.json" /workspace/cjs/package.json
cp "$WORK/source/esm/index.js" /workspace/esm/index.js
cp "$WORK/source/types/index.d.ts" /workspace/types/index.d.ts

cat > /workspace/package.json <<'JSON'
{
  "name": "flatted",
  "version": "3.4.4",
  "description": "A super light and fast circular JSON parser.",
  "license": "ISC",
  "main": "./cjs/index.js",
  "module": "./esm/index.js",
  "type": "module",
  "exports": {
    ".": {
      "types": "./types/index.d.ts",
      "import": "./esm/index.js",
      "default": "./cjs/index.js"
    }
  },
  "types": "./types/index.d.ts",
  "files": ["LICENSE", "README.md", "cjs/", "esm/", "types/"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "flatted",
  "version": "3.4.4",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "flatted", "version": "3.4.4", "license": "ISC", "type": "module"}}
}
JSON
