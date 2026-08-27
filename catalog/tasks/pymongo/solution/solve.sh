#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/mongodb/mongo-python-driver"
readonly UPSTREAM_REVISION="ebc4bffcc842464e48a3edbd04802d1a42bc818a"
readonly SOURCE_ARCHIVE="/solution/source.tar.gz"
readonly SOURCE_ARCHIVE_GZIP_SHA256="d21660869013cb919af14dfa74e5718a131db2b726dbd71cee29ca8129c8a613"
readonly SOURCE_ARCHIVE_SHA256="933f254602e0ec43f463d7a9648f46623c86ba4fd81d9c8703bbe444d13aa068"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_GZIP_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
resolved_archive_sha256="$(gzip -dc "$SOURCE_ARCHIVE" | sha256sum | awk '{print $1}')"
if [[ "$resolved_archive_sha256" != "$SOURCE_ARCHIVE_SHA256" ]]; then
  echo "source archive digest mismatch" >&2
  exit 1
fi

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xzf "$SOURCE_ARCHIVE" -C "$ROOT"
rm -rf "$ROOT/.evergreen" "$ROOT/.github" "$ROOT/doc" "$ROOT/test"

version="$(python -c 'exec(open("/workspace/pymongo/_version.py", encoding="utf-8").read()); print(__version__)')"
if [[ "$version" != "4.18.0.dev0" ]]; then
  echo "unexpected frozen package version: $version" >&2
  exit 1
fi
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
