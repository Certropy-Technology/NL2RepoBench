#!/usr/bin/env bash
set -euo pipefail

revision='93666b389e1ed07912b6c2466468da21d9f834ce'
source_url='https://github.com/sindresorhus/pretty-ms'
expected_archive_sha256='sha256:e2a108dc70512373b94d959c2084d44eef117e32091a43659705375986408dd4'
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_root=/tmp/pretty-ms-oracle-source
archive=/tmp/pretty-ms-oracle-source.tar
rm -rf "$source_root" "$archive"
git init -q "$source_root"
git -C "$source_root" remote add origin "$source_url"
git -C "$source_root" fetch --quiet --depth 1 origin "$revision"
fetched=$(git -C "$source_root" rev-parse FETCH_HEAD)
test "$fetched" = "$revision"
git -C "$source_root" archive --format=tar FETCH_HEAD > "$archive"
actual_archive_sha256=$(sha256sum "$archive" | awk '{print $1}')
printf 'oracle_source_archive_sha256=%s\n' "$actual_archive_sha256"
test "$actual_archive_sha256" = "${expected_archive_sha256#sha256:}"
rm -rf "$source_root/checkout"
mkdir "$source_root/checkout"
tar -xf "$archive" -C "$source_root/checkout"
test -f "$source_root/checkout/index.js"
test -f "$source_root/checkout/index.d.ts"
cp "$source_root/checkout/index.js" /workspace/index.js
cp "$source_root/checkout/index.d.ts" /workspace/index.d.ts
cp "$script_dir/package.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json
npm ci --offline --ignore-scripts --no-audit --no-fund
