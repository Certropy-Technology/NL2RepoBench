# Project Description

Implement the public semantic-versioning behavior of the `com.vdurmont.semver4j`
Java library as a single Maven Java library. The project must parse semantic
versions, expose their numeric components, compare versions, determine release
stability, and evaluate a basic requirement expression. The evaluator uses a
separate offline verifier and a fixed JDK 21/Maven environment.

## Introduction and Goals

The library represents versions such as `1.2.3`, compares them using semantic
version ordering, distinguishes stable releases from pre-releases, and
supports simple expressions such as `>=1.0.0`. Implement the selected public
behavior without copying the upstream build, tests, plugins, profiles, or
repository configuration.

## Natural Language Instruction (Prompt)

Please create a Java Maven project that provides the following public behavior:

1. Parse a version string and report malformed input through the library's
   normal `SemverException` contract.
2. Return the normalized version string and the integer major and minor
   components.
3. Compare a version with another version using greater-than, less-than, and
   equality operations.
4. Report whether a version is stable. A version is stable only when it has no
   pre-release suffix and its major version is greater than zero. Therefore
   `1.2.3` is stable, while `1.2.3-alpha` and `0.1.0` are not.
5. Evaluate the supported requirement form used by the contract, including
   expressions such as `>=1.0.0`.
6. Keep the implementation under `src/main/java` in a normal single-module
   Maven project. Do not depend on external runtime libraries.

## Environment Configuration

- Java runtime: Temurin JDK `21.0.12+8`
- Maven: `3.9.11`
- Platform: Linux `amd64`
- Build and verification: offline, verifier-owned Maven/Javac harness
- Candidate compilation: `javac --release 21`
- Runtime dependencies: none
- Network access: unavailable to the agent and verifier

## Project Architecture

Use the standard Maven layout:

```text
project/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── com/vdurmont/semver4j/
                └── Semver.java
```

The public package is `com.vdurmont.semver4j`. Keep the implementation
self-contained and do not execute the upstream Maven lifecycle, profiles,
plugins, tests, or release configuration.

## API Usage Guide

Import the public class directly:

```java
import com.vdurmont.semver4j.Semver;

Semver version = new Semver("2.4.1");
String normalized = version.getValue();
Integer major = version.getMajor();
Integer minor = version.getMinor();
boolean newer = version.isGreaterThan("2.0.0");
boolean compatible = version.satisfies(">=2.0.0");
```

The required public signatures are:

```java
Semver(String value)
String getValue()
Integer getMajor()
Integer getMinor()
boolean isGreaterThan(String version)
boolean isLowerThan(String version)
boolean isEqualTo(String version)
boolean isStable()
boolean satisfies(String requirement)
```

All operations are deterministic. In the strict constructor contract,
`getValue()` returns the trimmed version text used for parsing; it does not add
missing components or remove build metadata. The selected requirement contract
accepts a single greater-than-or-equal expression in the form
`>=<strict-semantic-version>`, for example `>=1.0.0`. Invalid or unsupported
requirement text follows the library's `SemverException` behavior. Other
methods that accept a version string use the same strict parsing rules as the
constructor.

## Examples and Boundary Conditions

```java
new Semver("2.4.1").getMajor();          // 2
new Semver("2.4.1").getMinor();          // 4
new Semver("2.0.0").isGreaterThan("1.9.9"); // true
new Semver("1.2.3-alpha").isStable();    // false
new Semver("0.1.0").isStable();           // false
new Semver("1.2.3").satisfies(">=1.0.0"); // true
```

Preserve semantic ordering, pre-release handling, malformed-input errors,
empty or boundary components, and the exact boolean results of the public
operations. Do not add unrequested APIs or use network access to obtain
dependencies.

## Implementation Notes

The evaluator compiles submitted Java sources directly and calls the public
contract through a separate candidate JVM. The Maven `pom.xml` is validated as
metadata only; candidate-controlled plugins, profiles, repositories,
dependencies, modules, and custom build extensions are not part of this
profile.
