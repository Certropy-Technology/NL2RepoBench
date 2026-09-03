#!/usr/bin/env bash
set -euo pipefail

revision='b9128591fc59429d8b0df7047d5283f259dc5e77'
archive_sha256='8b7133f569873efe624778419ce87b94a9df78ac19f80a4a7217f9adbd67664f'
checkout=$(mktemp -d)
archive=$(mktemp)
trap 'rm -rf "$checkout" "$archive"' EXIT

git -C "$checkout" init -q
git -C "$checkout" remote add origin https://github.com/sindresorhus/npm-run-path
git -C "$checkout" fetch -q --depth=1 origin "$revision"
git -C "$checkout" checkout -q --detach FETCH_HEAD
test "$(git -C "$checkout" rev-parse HEAD)" = "$revision"
git -C "$checkout" archive --format=tar --prefix=npm-run-path/ HEAD > "$archive"
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --status

tar -xf "$archive" --strip-components=1 -C /workspace
rm -f /workspace/.npmrc
cp /solution/package.json /workspace/package.json
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
