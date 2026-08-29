#!/usr/bin/env bash
set -euo pipefail

revision="eea2581b131685f2c21de777fd037c8ddd343354"
archive_digest="ecd2011652df85d6d95d08e80d8d1d2ce06ac5dfcc9aca7ef3f28eace03c01f9"
source_dir="/workspace/.oracle-source"
rm -rf /workspace/.oracle-source /workspace/.oracle-source.tar /workspace/.oracle-source.sha256 /workspace/src /workspace/build
git init -q "$source_dir"
git -C "$source_dir" remote add origin https://github.com/eventualbuddha/lines-and-columns
git -C "$source_dir" fetch --quiet --depth=1 origin "$revision"
git -C "$source_dir" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$source_dir" rev-parse HEAD)" = "$revision"
git -C "$source_dir" archive --format=tar HEAD > /workspace/.oracle-source.tar
printf '%s  %s\n' "$archive_digest" /workspace/.oracle-source.tar > /workspace/.oracle-source.sha256
sha256sum --check --strict /workspace/.oracle-source.sha256

mkdir -p /workspace/src
cp "$source_dir/src/index.ts" /workspace/src/index.ts
cp "$source_dir/LICENSE" /workspace/LICENSE
mkdir -p /workspace/build
sed \
  -e '/^export interface SourceLocation {$/,/^}$/d' \
  -e '/private readonly length: number/d' \
  -e '/private readonly offsets: ReadonlyArray<number>/d' \
  -e 's/const offsets: ReadonlyArray<number>/const offsets/' \
  -e 's/constructor(string: string)/constructor(string)/' \
  -e 's/locationForIndex(index: number): SourceLocation | null/locationForIndex(index)/' \
  -e 's/indexForLocation(location: SourceLocation): number | null/indexForLocation(location)/' \
  -e 's/private lengthOfLine/lengthOfLine/' \
  -e 's/: number//g' \
  "$source_dir/src/index.ts" > /workspace/build/index.mjs
sed 's/^export class/class/' /workspace/build/index.mjs > /workspace/build/index.cjs
printf '\nmodule.exports = {LinesAndColumns};\n' >> /workspace/build/index.cjs
cat > /workspace/package.json <<'JSON'
{
  "name": "lines-and-columns",
  "version": "0.0.0-dev",
  "description": "Maps lines and columns to character offsets and back.",
  "license": "MIT",
  "type": "module",
  "main": "./build/index.cjs",
  "exports": {
    "import": "./build/index.mjs",
    "require": "./build/index.cjs",
    "types": "./src/index.ts"
  },
  "files": ["build", "src", "LICENSE"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "lines-and-columns",
  "version": "0.0.0-dev",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "lines-and-columns",
      "version": "0.0.0-dev",
      "license": "MIT",
      "type": "module",
      "main": "./build/index.cjs",
      "exports": {
        "import": "./build/index.mjs",
        "require": "./build/index.cjs",
        "types": "./src/index.ts"
      }
    }
  }
}
JSON
