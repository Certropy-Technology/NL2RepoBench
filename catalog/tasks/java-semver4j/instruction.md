## Project Description

Create a small, self-contained Java library that recreates the public behavior
of semver4j, a semantic-version parser and comparator. The library is intended
for Java applications that need to parse a version string, inspect its numeric
components, compare versions, classify stable releases, and check the supported
minimum-version requirement form.

The candidate must build a Maven project whose public package is
`com.vdurmont.semver4j` and whose public class is `Semver`. The goal is a usable
library, not a command-line application. A caller should be able to construct a
`Semver` value from text and then use the documented methods without accessing
the filesystem, environment variables, network, Maven internals, or global
mutable state.

In scope:

- Parsing a strict semantic-version string through `Semver(String)`.
- Preserving the library's public version text through `getValue()`.
- Reading the integer major and minor components.
- Comparing a version with another version string for greater-than,
  less-than, and equality.
- Determining stability from the parsed version.
- Evaluating the supported `>=` requirement expression.
- Reporting malformed versions and malformed or unsupported requirements through
  the library's normal `SemverException` behavior.
- Providing the standard Maven source layout and Java 21-compatible source.

Out of scope:

- A CLI, daemon, web service, persistence layer, or configuration file format.
- Network access, filesystem access, process execution, reflection-based
  adapters, or a database.
- Third-party runtime dependencies. The implementation must be self-contained
  and use the Java standard library where implementation support is needed.
- Maven publishing, signing, release, coverage, or repository configuration.
- Unspecified requirement-builder APIs, range/tokenizer internals, or extra
  overloads that are not part of the contract below.
- Reproducing the upstream test framework or adding a private test harness as a
  substitute for the public library.

The implementation should preserve the observable contract rather than expose
an alternative API. Keep public names, package names, parameter types, return
types, comparison semantics, and exception behavior exactly as specified.

## Natural Language Instruction

Build the Java Maven project described here from an empty `workspace/`.
Implement the `com.vdurmont.semver4j.Semver` public class and its documented
constructor and methods, preserving strict parsing, semantic ordering,
stability classification, minimum-version requirement evaluation, and
`SemverException` error behavior. Keep all public Java sources under the
standard Maven tree, keep the runtime dependency closure empty, and ensure the
same deterministic results are produced in the offline JDK 21 environment.
The POM and source layout must be sufficient for the harness to compile the
candidate without downloading artifacts. Do not substitute a CLI, a different
package name, a looser parser, or undocumented range and builder behavior for
the specified library surface.

## Supports

### Runtime and Build Contract

- Operating system: Debian Bookworm on `linux/amd64` with glibc.
- Java runtime and compiler: Temurin JDK `21.0.12+8`.
- Build tool: Apache Maven `3.9.11`.
- Project type: one Maven module with the standard `src/main/java` layout.
- Java compilation must target release 21 and must work with `CGO`-like native
  extensions absent; do not require JNI, cgo, or platform-specific libraries.
- The runtime dependency set is empty. Java standard-library classes are
  available from the JDK and must not be declared as Maven dependencies.

The candidate project must contain a valid `pom.xml`, but the verifier owns the
compilation contract. Do not rely on a remote repository, plugin download, or
candidate-controlled Maven profile to provide behavior. The project must be
compatible with offline Maven validation and with verifier-owned `javac
--release 21` compilation.

All agent, candidate, verifier, Oracle, and control execution is no-network.
Do not contact GitHub, Maven Central, DNS, a package mirror, or any other
external service at runtime. The empty private Maven closure is an environment
constraint, not an invitation to add dependencies. A clean build must use only
the checked-out candidate files and the preinstalled JDK/Maven toolchain.

### Project Directory Structure

Use `workspace/` as the project root. The minimum public layout is:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── com/
                └── vdurmont/
                    └── semver4j/
                        └── Semver.java
```

`Semver.java` must declare package `com.vdurmont.semver4j` and public class
`Semver`. The class is the library entry point. There is no required CLI entry
point and no required `main` method. Extra files are acceptable only when they
support this public contract without changing the package or introducing a
runtime dependency.

The POM should identify a single module and provide ordinary Java compiler
metadata. It must not require a repository, download, generated source tree,
service, or user-specific path. The public package path in the directory tree
must match the import path used in every example below.

### Setup Performed by the Harness

The harness supplies the fixed JDK/Maven environment and performs compilation
and contract execution outside the candidate's source package. It does not
provide a replacement `Semver` class, a network service, or candidate data.
The candidate is responsible for creating `pom.xml`, `Semver.java`, and any
ordinary source files needed by the implementation.

## API Usage Guide

### Package Import

Import the public class from the exact package below:

```java
import com.vdurmont.semver4j.Semver;
```

The package name is case-sensitive. Do not place the class in the default
package or under a different Maven artifact package. This import has no side
effects and does not perform I/O.

### `Semver(String value)`

Construct one parsed semantic version.

Signature:

```java
public Semver(String value)
```

`value` is the version text to parse. The accepted domain is a strict semantic
version represented as a string, including the numeric major, minor, and patch
components and any supported pre-release or build metadata suffix. Leading or
trailing whitespace follows the library's public normalization behavior; the
stored public value must remain consistent with `getValue()`.

The constructor returns a `Semver` object. It does not mutate caller state,
access files, access the network, or consult the clock. A null, empty, or
malformed version is invalid and must fail with the public `SemverException`
contract rather than producing a partially initialized object. Do not silently
invent missing numeric components or convert an invalid version to zero.

Ordinary example:

```java
Semver release = new Semver("2.4.1");
```

Edge example:

```java
try {
    new Semver("");
} catch (SemverException expected) {
    // Invalid version text is reported through the public exception contract.
}
```

### `getValue()`

Return the public version text associated with the parsed object.

Signature:

```java
public String getValue()
```

The method accepts no arguments and returns a non-null `String`. The returned
text is the normalized or trimmed public value used by the parser, according
to the constructor's value behavior. It must not fabricate missing components,
silently discard meaningful pre-release information, or remove build metadata
when the public value contract preserves it.

Repeated calls on the same object are deterministic and do not change object
state. The method performs no I/O and does not reparse the string.

Ordinary example:

```java
Semver version = new Semver("1.2.3");
String text = version.getValue();
// text represents the parsed public version "1.2.3".
```

Edge example:

```java
Semver prerelease = new Semver("1.2.3-alpha");
String text = prerelease.getValue();
// The pre-release suffix remains represented in the public value.
```

### `getMajor()`

Read the major numeric component.

Signature:

```java
public Integer getMajor()
```

The method accepts no arguments and returns the parsed major component as an
`Integer`. For a valid version such as `2.4.1`, the result is `2`. The result
is derived from the constructor input, is deterministic, and does not mutate
the object or perform I/O.

Ordinary example:

```java
Semver version = new Semver("2.4.1");
Integer major = version.getMajor();
// major is 2.
```

Edge example:

```java
Semver zeroMajor = new Semver("0.9.0");
Integer major = zeroMajor.getMajor();
// major is 0; zero is a valid numeric component.
```

### `getMinor()`

Read the minor numeric component.

Signature:

```java
public Integer getMinor()
```

The method accepts no arguments and returns the parsed minor component as an
`Integer`. For `2.4.1`, the result is `4`. It is deterministic for the life of
the object, has no side effects, and cannot be called successfully on a value
that the constructor rejected.

Ordinary example:

```java
Semver version = new Semver("2.4.1");
Integer minor = version.getMinor();
// minor is 4.
```

Edge example:

```java
Semver version = new Semver("1.0.0");
Integer minor = version.getMinor();
// A zero minor component is returned as the integer 0.
```

### `isGreaterThan(String version)`

Determine whether the receiver is greater than another semantic version.

Signature:

```java
public boolean isGreaterThan(String version)
```

`version` must be valid semantic-version text. The method returns `true` when
the receiver sorts after the parsed argument under semantic-version ordering,
and `false` otherwise. Ordering considers the numeric components and supported
pre-release information; it is not a lexicographic string comparison.

The argument is parsed for the call. A null, empty, or malformed argument must
follow the public `SemverException` behavior. The receiver is not mutated, and
repeating the same comparison returns the same boolean.

Ordinary example:

```java
Semver version = new Semver("2.4.1");
boolean newer = version.isGreaterThan("2.0.0");
// newer is true.
```

Edge example:

```java
Semver version = new Semver("1.2.3-alpha");
boolean newer = version.isGreaterThan("1.2.3");
// A pre-release must be ordered according to semantic-version rules.
```

### `isLowerThan(String version)`

Determine whether the receiver is less than another semantic version.

Signature:

```java
public boolean isLowerThan(String version)
```

`version` must be valid semantic-version text. The method returns `true` when
the receiver sorts before the parsed argument under semantic-version ordering,
and `false` otherwise. Numeric components take precedence over textual length,
and pre-release ordering must remain consistent with the other comparison
methods.

Invalid argument text follows the public `SemverException` contract. The
receiver remains unchanged and the result is deterministic.

Ordinary example:

```java
Semver version = new Semver("1.2.3");
boolean older = version.isLowerThan("2.0.0");
// older is true.
```

Edge example:

```java
Semver version = new Semver("2.0.0");
boolean older = version.isLowerThan("2.0.0");
// Equal versions are not lower than one another.
```

### `isEqualTo(String version)`

Determine whether the receiver is equal to another semantic version.

Signature:

```java
public boolean isEqualTo(String version)
```

`version` must be valid semantic-version text. The method returns `true` when
the parsed versions are equal under the library's semantic comparison rules,
and `false` when they differ. Equality must agree with `isGreaterThan` and
`isLowerThan`: a pair cannot be both equal and strictly ordered.

Null, empty, or malformed argument text follows the public `SemverException`
contract. The call has no I/O or mutation and is deterministic.

Ordinary example:

```java
Semver version = new Semver("1.2.3");
boolean same = version.isEqualTo("1.2.3");
// same is true.
```

Edge example:

```java
Semver version = new Semver("1.2.3");
boolean same = version.isEqualTo("1.2.4");
// same is false; a changed patch component changes the version.
```

### `isStable()`

Classify whether the receiver represents a stable release.

Signature:

```java
public boolean isStable()
```

The method accepts no arguments and returns a primitive `boolean`. It returns
`true` only when the version has no pre-release suffix and its major component
is greater than zero. Thus `1.2.3` is stable, while `1.2.3-alpha` and `0.1.0`
are not. Build metadata alone does not act as a pre-release suffix.

The result is derived from the immutable parsed value, is deterministic, and
has no side effects. A rejected constructor input cannot reach this method.

Ordinary example:

```java
boolean stable = new Semver("1.2.3").isStable();
// stable is true.
```

Edge examples:

```java
boolean prerelease = new Semver("1.2.3-alpha").isStable();
boolean zeroMajor = new Semver("0.1.0").isStable();
// Both values are false for different stability reasons.
```

### `satisfies(String requirement)`

Evaluate the supported minimum-version requirement form against the receiver.

Signature:

```java
public boolean satisfies(String requirement)
```

The supported requirement domain is one greater-than-or-equal expression in
the form `>=` followed by a strict semantic version, for example `>=1.0.0`.
The method returns `true` when the receiver is at least the threshold under the
same semantic ordering used by the comparison methods, and `false` when it is
below that threshold.

The requirement is parsed for the call. A null, empty, malformed, or
unsupported expression must follow the public `SemverException` behavior; do
not silently reinterpret another operator or a range as a minimum requirement.
The call is deterministic, does not mutate the receiver, and performs no I/O.

Ordinary example:

```java
Semver version = new Semver("1.2.3");
boolean compatible = version.satisfies(">=1.0.0");
// compatible is true.
```

Edge example:

```java
try {
    new Semver("1.2.3").satisfies("<2.0.0");
} catch (SemverException expected) {
    // The documented contract supports >=, not an unrelated operator.
}
```

## Implementation Notes

### Cross-API Consistency

Parse the receiver once at construction and make every accessor and predicate
refer to that same parsed value. The numeric accessors, comparison methods,
stability predicate, and requirement predicate must not disagree about the
major/minor components or the presence of a pre-release suffix.

Keep comparison transitive and deterministic. Numeric components must be
compared as numbers rather than as strings, so values such as `10.0.0` and
`2.0.0` retain their numeric ordering. Equality must be reflexive for a valid
object and consistent with both strict comparison methods.

Do not use the current time, locale, default charset, random numbers, process
state, filesystem contents, environment variables, or network responses. Two
processes given the same valid inputs must produce the same values and boolean
results.

### Error and State Boundaries

Reject invalid constructor input before exposing an object. Reject invalid
comparison arguments and unsupported requirement text through the documented
`SemverException` contract. Do not return null, a fabricated zero version, or
an arbitrary false result to hide malformed input.

The object should behave as a value after construction. Repeated calls to any
getter or predicate must not alter later results. No API in this contract
creates files, changes directories, starts a process, loads a network resource,
or changes global configuration.

### Small Verifiable Examples

The following examples illustrate the contract without prescribing an internal
algorithm:

```java
Semver a = new Semver("2.0.0");
Semver b = new Semver("1.9.9");
boolean ordering = a.isGreaterThan(b.getValue());
```

```java
Semver preview = new Semver("1.0.0-rc.1");
boolean stable = preview.isStable();
boolean eligible = preview.satisfies(">=1.0.0");
```

```java
Semver initial = new Semver("0.0.1");
Integer major = initial.getMajor();
Integer minor = initial.getMinor();
boolean stable = initial.isStable();
```

```java
try {
    new Semver("not-a-version");
} catch (SemverException expected) {
    // Invalid text must remain an observable error.
}
```

Keep the implementation limited to the bindable public surface above. Do not
add unverified builder variants, range APIs, tokenizer exports, publishing
configuration, or hidden adapters. The final project must compile in the
offline Java 21 environment and leave all behavior available through
`com.vdurmont.semver4j.Semver`.
