#!/usr/bin/env bash
set -euo pipefail

revision='bacb2fc434b361b8951d1c7649c2029b1d7b6a83'
source_digest='18b19c2db580502951d0082e0215a2f6008488e6f5ed441024fa4ac4f6d0aa2b'

git init -q .
git remote add origin https://github.com/pterm/pterm.git
git fetch --quiet --no-tags --depth=1 origin "$revision"
test "$(git rev-parse FETCH_HEAD)" = "$revision"
git checkout --quiet --detach FETCH_HEAD
test "$(git archive --format=tar HEAD | sha256sum | awk '{print $1}')" = "$source_digest"

# The verifier accepts only a bounded regular-file tree. The frozen upstream
# records CLAUDE.md as a symlink to AGENTS.md; it is redundant task guidance,
# not runtime source. Git metadata is likewise unnecessary after the archive
# digest has been verified.
rm -rf .git CLAUDE.md
go mod edit -go=1.26.5
rm -rf vendor
cp -a /opt/go-module-bundle/vendor ./vendor
