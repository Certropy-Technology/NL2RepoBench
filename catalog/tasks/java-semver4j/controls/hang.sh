#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/vdurmont/semver4j
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > pom.xml
cat > src/main/java/com/vdurmont/semver4j/Semver.java <<'JAVA'
package com.vdurmont.semver4j;
public final class Semver {
    public enum SemverType { NPM }
    public Semver(String value) { block(); }
    public Semver(String value, SemverType type) { block(); }
    public String getValue() { block(); return ""; }
    public Integer getMajor() { block(); return 0; }
    public Integer getMinor() { block(); return 0; }
    public boolean isGreaterThan(String value) { block(); return false; }
    public boolean isLowerThan(String value) { block(); return false; }
    public boolean isEqualTo(String value) { block(); return false; }
    public boolean isStable() { block(); return false; }
    public boolean satisfies(String value) { block(); return false; }
    private static void block() { while (true) { Thread.yield(); } }
}
JAVA
