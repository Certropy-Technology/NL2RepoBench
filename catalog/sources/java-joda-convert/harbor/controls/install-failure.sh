#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/joda/convert
cat > /workspace/src/main/java/org/joda/convert/FromString.java <<'JAVA'
package org.joda.convert;
public @interface FromString {}
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>bad</artifactId><version>1</version><dependencies><dependency><groupId>evil</groupId><artifactId>network</artifactId><version>1</version></dependency></dependencies></project>
POM
