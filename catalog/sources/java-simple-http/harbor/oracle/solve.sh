#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/de/svenkubiak/http /workspace/src/main/java/de/svenkubiak/utils
cp "$tmp/src/main/java/de/svenkubiak/http/Result.java" /workspace/src/main/java/de/svenkubiak/http/Result.java
cp "$tmp/src/main/java/de/svenkubiak/utils/Utils.java" /workspace/src/main/java/de/svenkubiak/utils/Utils.java
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>de.svenkubiak</groupId><artifactId>simple-http</artifactId><version>1</version></project>' > /workspace/pom.xml
