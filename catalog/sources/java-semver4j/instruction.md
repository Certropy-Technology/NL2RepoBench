# Introduction and Goals of the Semver4j Project

Semver4j is a small Java library for parsing and comparing semantic versions.
It represents versions such as `1.2.3`, exposes their numeric components,
distinguishes stable releases from pre-releases, and evaluates the supported
minimum-version requirement form. The implementation should provide the
documented public behavior of the library while remaining a normal,
self-contained Maven project.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Semver4j that implements the public
semantic-versioning behavior described below:

1. Parse a version string and report malformed input with the library's normal
   `SemverException` behavior.
2. Return the normalized version text and the integer major and minor
   components.
3. Compare one version with another using greater-than, less-than, and
   equality operations.
4. Report whether a version is stable. A version is stable only when it has no
   pre-release suffix and its major version is greater than zero. Thus
   `1.2.3` is stable, while `1.2.3-alpha` and `0.1.0` are not.
5. Evaluate the supported requirement form, including expressions such as
   `>=1.0.0`.
6. Keep the implementation in `src/main/java` in a single-module Maven
   project. Do not add external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
# Java runtime
Temurin JDK 21.0.12+8       # Java compilation and execution
Maven 3.9.11                # Project metadata only; verifier uses offline tools

# Runtime dependencies
none                        # Use the Java standard library only

# Build and verification
Linux amd64                 # Fixed execution platform
network                     # Unavailable during agent and verifier runs
```

## Semver4j Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── com
                └── vdurmont
                    └── semver4j
                        └── Semver.java
```

The public package is `com.vdurmont.semver4j`. Keep the source self-contained.
The candidate POM is metadata only; do not use it to control verifier
dependencies, plugins, profiles, repositories, modules, or test commands.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import com.vdurmont.semver4j.Semver;
```

#### 2. Semver Constructor - Parse a Version

```java
Semver version = new Semver("2.4.1");
```

Signature:

```java
Semver(String value)
```

The constructor accepts a strict semantic-version string. Invalid input,
including empty or malformed versions, follows the public
`SemverException` contract.

#### 3. getValue() - Return the Version Text

```java
String value = version.getValue();
```

The returned value is the trimmed version text used for parsing. It does not
invent missing components or remove build metadata.

#### 4. getMajor() and getMinor() - Read Numeric Components

```java
Integer major = version.getMajor();
Integer minor = version.getMinor();
```

Both methods return the corresponding integer component of the parsed version.

#### 5. Comparison Functions - Compare Versions

```java
boolean newer = version.isGreaterThan("2.0.0");
boolean older = version.isLowerThan("3.0.0");
boolean same = version.isEqualTo("2.4.1");
```

Signatures:

```java
boolean isGreaterThan(String version)
boolean isLowerThan(String version)
boolean isEqualTo(String version)
```

Comparison follows semantic-version ordering, including pre-release ordering.

#### 6. isStable() - Determine Release Stability

```java
boolean stable = version.isStable();
```

The result is true only for a version without a pre-release suffix and with a
major component greater than zero.

#### 7. satisfies() - Evaluate a Requirement

```java
boolean compatible = version.satisfies(">=2.0.0");
```

Signature:

```java
boolean satisfies(String requirement)
```

The supported requirement contract is one greater-than-or-equal expression in
the form `>=<strict-semantic-version>`. Unsupported or malformed requirement
text follows the public `SemverException` behavior.

### Actual Usage Modes

#### Basic Usage

```java
Semver version = new Semver("2.4.1");
System.out.println(version.getMajor());
System.out.println(version.isGreaterThan("2.0.0"));
```

#### Stability Checking

```java
new Semver("1.2.3").isStable();       // true
new Semver("1.2.3-alpha").isStable(); // false
new Semver("0.1.0").isStable();        // false
```

#### Requirement Checking

```java
new Semver("1.2.3").satisfies(">=1.0.0"); // true
```

### Supported Function Types

The project supports strict parsing, numeric component access, semantic
comparison, stability detection, and the single supported requirement form.
All operations are deterministic and do not access the network or filesystem.

### Error Handling

Malformed versions and unsupported requirement expressions must fail through
the public exception contract rather than returning fabricated values. Do not
silently accept invalid components or change comparison semantics.

## Detailed Implementation Nodes of Functions

### Node 1: Version Parsing

Parse the trimmed input, preserve the public value behavior, extract numeric
components, and reject malformed input.

### Node 2: Semantic Comparison

Compare major, minor, patch, and pre-release information in semantic order.
Ensure equality is consistent with the comparison methods.

### Node 3: Stability Detection

Return false for pre-release versions and for versions whose major component is
zero; return true only for stable major releases.

### Node 4: Requirement Evaluation

Recognize the documented `>=` requirement form and compare it against the
current version. Reject unsupported operators and malformed thresholds.

### Node 5: Maven Project Layout

Keep public Java sources under the standard Maven path and make the project
compile with Java 21 without external runtime dependencies.

### Node 6: Deterministic Public API

Use the exact package, class, method names, parameter types, return types, and
exception behavior described above. Do not add hidden adapters or alternate
signatures in place of the requested API.

### Node 7: Boundary Conditions

Consider whitespace around input, zero-major releases, pre-release suffixes,
empty values, malformed numeric components, and unsupported requirement text.

### Node 8: Offline Build Behavior

The implementation must be buildable and executable in the fixed offline
environment. Do not download dependencies, invoke external services, or rely
on candidate-controlled Maven configuration.
