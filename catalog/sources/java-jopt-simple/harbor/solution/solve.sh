#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/net/sf/joptsimple
cp "$tmp/src/main/java/net/sf/joptsimple/KeyValuePair.java" /workspace/src/main/java/net/sf/joptsimple/
mkdir -p /workspace/src/main/java/net/sf/joptsimple/internal
cp "$tmp/src/main/java/net/sf/joptsimple/internal/Strings.java" /workspace/src/main/java/net/sf/joptsimple/internal/
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>net.sf.jopt-simple</groupId><artifactId>jopt-simple</artifactId><version>6.0.0</version></project>
POM
