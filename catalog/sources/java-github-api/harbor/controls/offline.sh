#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/kohsuke/github
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/kohsuke/github/GHCommitState.java <<'JAVA'
package org.kohsuke.github;
public enum GHCommitState { ERROR, FAILURE, PENDING, SUCCESS }
JAVA
