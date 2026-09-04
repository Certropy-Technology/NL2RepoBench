#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/vdurmont/semver4j
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version><packaging>jar</packaging></project>
XML
cat > src/main/java/com/vdurmont/semver4j/Semver.java <<'JAVA'
package com.vdurmont.semver4j;
public final class Semver {
    public enum SemverType { NPM }
    public Semver(String value) {}
    public Semver(String value, SemverType type) {}
    public String getValue() { return "stub"; }
    public Integer getMajor() { return 0; }
    public Integer getMinor() { return 0; }
    public boolean isGreaterThan(String value) { return false; }
    public boolean isLowerThan(String value) { return false; }
    public boolean isEqualTo(String value) { return false; }
    public boolean isStable() { return false; }
    public boolean satisfies(String value) { return false; }
}
JAVA
