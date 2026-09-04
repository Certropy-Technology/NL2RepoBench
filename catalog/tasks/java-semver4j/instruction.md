# Project Description

Implement the public semantic-versioning behavior of the `com.vdurmont.semver4j`
Java library as a single Maven Java library. The evaluator uses JDK 21 and an
offline, verifier-owned build. Keep the implementation self-contained under
`src/main/java` and do not add external runtime dependencies.

# Supports

The public package is `com.vdurmont.semver4j`.

- `Semver(String value)` constructs a semantic version. A malformed value
  raises the library's `SemverException`.
- `String getValue()` returns the normalized version value.
- `Integer getMajor()` and `Integer getMinor()` return the numeric major and
  minor components.
- `boolean isGreaterThan(String version)` and
  `boolean isLowerThan(String version)` compare this version with another
  version string.
- `boolean isEqualTo(String version)` checks semantic equality.
- `boolean isStable()` reports whether the version has no pre-release suffix.
- `boolean satisfies(String requirement)` evaluates a supported requirement
  expression such as `>=1.0.0`.

# API Usage Guide

Use the Maven project layout and import the class directly:

```java
import com.vdurmont.semver4j.Semver;

Semver version = new Semver("2.4.1");
Integer major = version.getMajor();
boolean compatible = version.satisfies(">=2.0.0");
```

Version comparisons are deterministic and preserve semantic-version ordering,
including the distinction between stable and pre-release versions. Methods
that accept a version or requirement string use the same parsing rules as the
constructor and report malformed input through `SemverException`.

# Implementation Notes

Provide a normal single-module Maven project with Java sources in
`src/main/java`. The checked behavior includes strict and pre-release parsing,
numeric component access, comparison, semantic equality, stability, and basic
requirement satisfaction. Do not depend on the upstream build plugins,
profiles, repositories, tests, or release configuration; the evaluator uses a
fixed offline harness and compiles the submitted Java sources directly.
