#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/com/cedarsoftware/util
cp "$tmp/src/main/java/com/cedarsoftware/util/ByteUtilities.java" /workspace/src/main/java/com/cedarsoftware/util/ByteUtilities.java
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>java-util</artifactId><version>1.0.0</version></project>' > /workspace/pom.xml
