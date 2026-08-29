#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="1b3e623bb3bb86c83379df039c375108a2b468fecc4bcaf6ff02d3ee89275503"
readonly DISTRIBUTION_SHA256="595ec2246b6e7409213c7b60c850c46b89ac790d20fd2c6f626ca71afdb28c42"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" /solution/source.tar | sha256sum --check --strict
printf '%s  %s\n' "$DISTRIBUTION_SHA256" /solution/distribution.tgz | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xzf /solution/distribution.tgz -C /workspace --strip-components=1
cp /solution/package.json /workspace/package.json
cp /solution/package-lock.json /workspace/package-lock.json
rm -rf /workspace/.github /workspace/benchmark /workspace/example /workspace/test
