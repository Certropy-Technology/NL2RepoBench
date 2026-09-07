#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/kohsuke/github
cat > pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>bad</artifactId><version>1.0.0</version><build><plugins/></build></project>
POM
cat > src/main/java/org/kohsuke/github/GHCommitState.java <<'JAVA'
package org.kohsuke.github;
public enum GHCommitState { ERROR, FAILURE, PENDING, SUCCESS }
JAVA
