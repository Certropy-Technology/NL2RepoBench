#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/org/kohsuke/github
cp "$tmp/src/main/java/org/kohsuke/github/GHCommitState.java" /workspace/src/main/java/org/kohsuke/github/
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>org.kohsuke</groupId><artifactId>github-api</artifactId><version>1.0.0</version></project>' > /workspace/pom.xml
