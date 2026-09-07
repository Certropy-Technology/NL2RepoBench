#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/de/svenkubiak/http
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>bad</artifactId><version>1</version><dependencies><dependency><groupId>forbidden</groupId><artifactId>network</artifactId><version>1</version></dependency></dependencies></project>
POM
printf '%s\n' 'package de.svenkubiak.http; public class Result {}' > /workspace/src/main/java/de/svenkubiak/http/Result.java
