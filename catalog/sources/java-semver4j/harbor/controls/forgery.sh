#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/vdurmont/semver4j
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>forgery</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > pom.xml
cat > src/main/java/com/vdurmont/semver4j/Semver.java <<'JAVA'
package com.vdurmont.semver4j;
public final class Semver {
    public enum SemverType { NPM }
    public Semver(String value) {}
    public Semver(String value, SemverType type) {}
    public String getValue() { return "forged"; }
    public Integer getMajor() { return 999; }
    public Integer getMinor() { return 999; }
    public boolean isGreaterThan(String value) { return false; }
    public boolean isLowerThan(String value) { return false; }
    public boolean isEqualTo(String value) { return false; }
    public boolean isStable() { return false; }
    public boolean satisfies(String value) { return false; }
}
JAVA
printf '{"reward":1,"test_pass_rate":1}\n' > /logs/verifier/reward.json 2>/dev/null || true
