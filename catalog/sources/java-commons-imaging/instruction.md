## Project Description

Apache Commons Imaging is a Java library for working with image formats. This
task exposes only one small, self-contained value-object contract from that
library: `org.apache.commons.imaging.PixelDensity`. Recreate that contract in
an offline, single-module Maven project.

The project user needs to represent horizontal and vertical pixel densities,
remember the unit selected at construction time, read the original values,
identify the unit, and convert physical densities between inches,
centimetres, and metres. The two axes are independent: an operation on the
horizontal value must never use or modify the vertical value.

The public boundary is deliberately narrow. Implement the `PixelDensity`
class and the four factories, two raw accessors, four unit predicates, and
six conversion methods documented in the API Usage Guide. The class is a
pure in-memory value object. It does not read images, write images, parse
metadata, access files, invoke a command, contact a service, or maintain a
process-wide registry.

The target project must compile as a standard Maven project with Java 21 and
no runtime dependency beyond the Java standard library. Do not add image
codec classes, metadata classes, command-line entry points, network clients,
or public APIs that are not confidently bound to this task's frozen API
inventory.

## Supports

### Natural Language Instruction

Create a Maven project rooted at `workspace/` with the package
`org.apache.commons.imaging` and a public `PixelDensity` class. Implement the
following capabilities:

1. Construct an instance from pixels per inch, pixels per centimetre, pixels
   per metre, or an explicitly unitless pair of `double` values.
2. Preserve the horizontal argument as the horizontal raw density and the
   vertical argument as the vertical raw density. Never swap, sort, clamp, or
   otherwise normalise the axes.
3. Report exactly which of the four units was selected by the factory.
4. Convert each physical axis independently to inches, centimetres, or
   metres using the fixed relationships `1 inch = 2.54 centimetres` and
   `1 metre = 100 centimetres`.
5. Keep all behavior deterministic and free of filesystem, environment,
   network, clock, randomness, and global mutable-state side effects.
6. Provide the exact package, class, method names, parameter types, return
   types, and static/instance modifiers in the API Usage Guide.

There is no CLI or executable entry point in this task. `task.toml` declares
Maven validation commands only; it does not declare a public command-line
interface. Do not invent a `main` method or a command wrapper.

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── imaging/
                            └── PixelDensity.java
```

The source file must declare package `org.apache.commons.imaging` and define
the public `PixelDensity` type. The POM must describe a single Java Maven
project suitable for offline validation. Do not use the POM to add modules,
repositories, build extensions, verifier commands, or runtime libraries.

### Environment Configuration

Use Temurin JDK `21.0.12+8`, Maven `3.9.11`, Linux `amd64`, and glibc as the
target environment. Compile and validate with the fixed offline Maven
closure. The declared runtime dependency set is empty: Java standard-library
types are sufficient.

The agent, candidate, verifier, Oracle, and controls run with no network.
They must not fetch GitHub, Maven Central, DNS data, or any external service
at runtime. The candidate workspace is isolated and starts without the
reference implementation.

### Public Scope and Exclusions

The supported class is only:

```java
org.apache.commons.imaging.PixelDensity
```

The supported methods are four public static factories, two public raw-value
accessors, four public unit predicates, and six public conversion methods.
There is no task-level CLI, file format, serializer, image decoder, image
encoder, metadata parser, resource directory, or additional public class.

## API Usage Guide

Import the class with:

```java
import org.apache.commons.imaging.PixelDensity;
```

All examples below are ordinary Java expressions. `x` always means the
horizontal density and `y` always means the vertical density. Every method
is deterministic and has no I/O, network, environment, clock, or global
state side effect.

### `PixelDensity.createFromPixelsPerInch`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public static PixelDensity createFromPixelsPerInch(double x, double y)
```

The inputs are the horizontal and vertical values expressed in pixels per
inch. The returned `PixelDensity` retains both raw values and records inches
as its unit. It returns one new value object for the call; it does not mutate
another instance or share mutable state.

Normal example:

```java
PixelDensity density = PixelDensity.createFromPixelsPerInch(300.0, 150.0);
```

Edge example:

```java
PixelDensity density = PixelDensity.createFromPixelsPerInch(0.0, -2.5);
```

The factory accepts Java `double` values, including zero, negative values,
fractional values, and the normal floating-point special values. No checked
exception is part of this method's contract, and no range validation,
clamping, or axis correction should be added.

### `PixelDensity.createFromPixelsPerCentimetre`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public static PixelDensity createFromPixelsPerCentimetre(double x, double y)
```

The inputs are horizontal and vertical pixels per centimetre. The returned
value retains the arguments as raw centimetre densities and records
centimetres as its unit.

Normal example:

```java
PixelDensity density =
        PixelDensity.createFromPixelsPerCentimetre(100.0, 50.0);
```

Edge example:

```java
PixelDensity density =
        PixelDensity.createFromPixelsPerCentimetre(Double.NaN, 0.0);
```

The method has no declared checked exception and should not reject a `double`
merely because it is zero, negative, non-integral, NaN, or infinite. Preserve
normal Java floating-point behavior.

### `PixelDensity.createFromPixelsPerMetre`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public static PixelDensity createFromPixelsPerMetre(double x, double y)
```

The inputs are horizontal and vertical pixels per metre. The returned value
retains the arguments as raw metre densities and records metres as its unit.

Normal example:

```java
PixelDensity density = PixelDensity.createFromPixelsPerMetre(10000.0, 5000.0);
```

Edge example:

```java
PixelDensity density =
        PixelDensity.createFromPixelsPerMetre(Double.POSITIVE_INFINITY, -1.0);
```

No checked exception is declared or required for the accepted Java `double`
domain. Do not silently reinterpret metre input as centimetre or inch input.

### `PixelDensity.createUnitless`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public static PixelDensity createUnitless(double x, double y)
```

The inputs are two raw values with no physical unit. The returned value
retains both values and records the unitless state. Unitless values are useful
for metadata that intentionally has no physical scale.

Normal example:

```java
PixelDensity density = PixelDensity.createUnitless(2.0, 3.0);
```

Edge example:

```java
PixelDensity density = PixelDensity.createUnitless(-0.0, Double.NaN);
```

The method accepts Java `double` values without adding positivity or finiteness
validation. It has no checked exception and no external side effect.

### `PixelDensity.getRawHorizontalDensity`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double getRawHorizontalDensity()
```

Return the horizontal value exactly as supplied to the factory, in the raw
unit selected at construction. The return type is `double`; it is a scalar,
not a converted value and not a wrapper object.

Normal example:

```java
PixelDensity density = PixelDensity.createFromPixelsPerInch(300.0, 150.0);
double horizontal = density.getRawHorizontalDensity(); // 300.0
```

Edge example:

```java
double horizontal = PixelDensity.createUnitless(0.0, 7.0)
        .getRawHorizontalDensity(); // 0.0
```

This accessor does not alter the object, perform conversion, or throw a
checked exception. Preserve signed zero, NaN, infinity, and fractional values
according to Java `double` semantics.

### `PixelDensity.getRawVerticalDensity`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double getRawVerticalDensity()
```

Return the vertical value exactly as supplied to the factory. The horizontal
value must not affect this result.

Normal example:

```java
double vertical = PixelDensity.createFromPixelsPerMetre(10000.0, 5000.0)
        .getRawVerticalDensity(); // 5000.0
```

Edge example:

```java
double vertical = PixelDensity.createUnitless(7.0, -0.25)
        .getRawVerticalDensity(); // -0.25
```

The accessor is read-only, deterministic, and has no declared checked
exception. It must not normalise or validate the stored value.

### `PixelDensity.isInInches`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public boolean isInInches()
```

Return `true` exactly when the instance was created by
`createFromPixelsPerInch`; return `false` for centimetre, metre, and unitless
instances. The result depends on the recorded unit, not on the numeric values.

Normal example:

```java
boolean inches = PixelDensity.createFromPixelsPerInch(300.0, 150.0)
        .isInInches(); // true
```

Edge example:

```java
boolean inches = PixelDensity.createUnitless(300.0, 150.0)
        .isInInches(); // false
```

This predicate has no arguments, no side effects, and no checked exception.

### `PixelDensity.isInCentimetres`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public boolean isInCentimetres()
```

Return `true` only for an instance created by
`createFromPixelsPerCentimetre`; return `false` for the other three factory
states. Numeric equality to a converted value must not change the predicate.

Normal example:

```java
boolean centimetres =
        PixelDensity.createFromPixelsPerCentimetre(100.0, 50.0)
                .isInCentimetres(); // true
```

Edge example:

```java
boolean centimetres = PixelDensity.createFromPixelsPerInch(254.0, 0.0)
        .isInCentimetres(); // false
```

The method is a deterministic read-only predicate with no checked exception.

### `PixelDensity.isInMetres`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public boolean isInMetres()
```

Return `true` only for an instance created by
`createFromPixelsPerMetre`; return `false` for inch, centimetre, and unitless
instances.

Normal example:

```java
boolean metres = PixelDensity.createFromPixelsPerMetre(10000.0, 5000.0)
        .isInMetres(); // true
```

Edge example:

```java
boolean metres = PixelDensity.createUnitless(10000.0, 5000.0)
        .isInMetres(); // false
```

This predicate has no arguments, no side effects, and no checked exception.

### `PixelDensity.isUnitless`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public boolean isUnitless()
```

Return `true` only for an instance created by `createUnitless`; return
`false` for each physical unit. Exactly one of the four unit predicates is
true for every factory-created instance.

Normal example:

```java
boolean unitless = PixelDensity.createUnitless(2.0, 3.0).isUnitless();
```

Edge example:

```java
boolean unitless = PixelDensity.createFromPixelsPerMetre(0.0, 0.0)
        .isUnitless(); // false
```

The method is deterministic and read-only and has no checked exception.

### `PixelDensity.horizontalDensityInches`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double horizontalDensityInches()
```

Return the horizontal density expressed as pixels per inch. For inch input,
return the horizontal raw value. For centimetre input, multiply the raw value
by `2.54`. For metre input, multiply the raw value by `2.54 / 100`. Unitless
values have no physical scale; preserve the source's unitless behavior and
do not invent a physical unit.

Normal example:

```java
double dpi = PixelDensity.createFromPixelsPerCentimetre(100.0, 50.0)
        .horizontalDensityInches(); // 254.0
```

Edge example:

```java
double dpi = PixelDensity.createFromPixelsPerInch(0.0, -2.0)
        .horizontalDensityInches(); // 0.0
```

Conversion uses ordinary Java `double` arithmetic. There is no checked
exception and no mutation or external side effect.

### `PixelDensity.horizontalDensityCentimetres`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double horizontalDensityCentimetres()
```

Return horizontal pixels per centimetre. For inch input, divide by `2.54`.
For centimetre input, return the raw horizontal value. For metre input,
divide by `100`. Keep the vertical value completely independent.

Normal example:

```java
double dpcm = PixelDensity.createFromPixelsPerInch(254.0, 508.0)
        .horizontalDensityCentimetres(); // 100.0
```

Edge example:

```java
double dpcm = PixelDensity.createFromPixelsPerMetre(0.0, 100.0)
        .horizontalDensityCentimetres(); // 0.0
```

The operation is deterministic Java `double` arithmetic, with no checked
exception and no side effect. Do not round or format the result.

### `PixelDensity.horizontalDensityMetres`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double horizontalDensityMetres()
```

Return horizontal pixels per metre. For inch input, multiply by `100 / 2.54`.
For centimetre input, multiply by `100`. For metre input, return the raw
horizontal value.

Normal example:

```java
double dpm = PixelDensity.createFromPixelsPerCentimetre(100.0, 50.0)
        .horizontalDensityMetres(); // 10000.0
```

Edge example:

```java
double dpm = PixelDensity.createFromPixelsPerMetre(-1.5, 2.0)
        .horizontalDensityMetres(); // -1.5
```

The method performs no rounding, I/O, or validation and has no checked
exception.

### `PixelDensity.verticalDensityInches`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double verticalDensityInches()
```

Return vertical pixels per inch using the same unit relationships as the
horizontal inch conversion, but apply them only to the vertical raw value:
inch values are unchanged, centimetre values are multiplied by `2.54`, and
metre values are multiplied by `2.54 / 100`.

Normal example:

```java
double dpi = PixelDensity.createFromPixelsPerMetre(100.0, 100.0)
        .verticalDensityInches(); // 2.54
```

Edge example:

```java
double dpi = PixelDensity.createFromPixelsPerInch(254.0, 0.0)
        .verticalDensityInches(); // 0.0
```

The method is deterministic and has no checked exception or external side
effect.

### `PixelDensity.verticalDensityCentimetres`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double verticalDensityCentimetres()
```

Return vertical pixels per centimetre. Divide inch input by `2.54`, preserve
centimetre input, and divide metre input by `100`. Apply the conversion only
to the vertical raw value.

Normal example:

```java
double dpcm = PixelDensity.createFromPixelsPerInch(254.0, 508.0)
        .verticalDensityCentimetres(); // 200.0
```

Edge example:

```java
double dpcm = PixelDensity.createFromPixelsPerMetre(100.0, -0.0)
        .verticalDensityCentimetres(); // -0.0
```

No checked exception is declared; preserve ordinary Java floating-point
behavior and do not round the result.

### `PixelDensity.verticalDensityMetres`

Import path: `org.apache.commons.imaging.PixelDensity`.

Signature:

```java
public double verticalDensityMetres()
```

Return vertical pixels per metre. Multiply inch input by `100 / 2.54`,
multiply centimetre input by `100`, and preserve metre input. The horizontal
value must not participate in the calculation.

Normal example:

```java
double dpm = PixelDensity.createFromPixelsPerCentimetre(10.0, 50.0)
        .verticalDensityMetres(); // 5000.0
```

Edge example:

```java
double dpm = PixelDensity.createFromPixelsPerMetre(10.0, -2.5)
        .verticalDensityMetres(); // -2.5
```

This read-only conversion has no checked exception and no external side
effect. Preserve Java `double` overflow, underflow, NaN, and infinity rules.

### Error and unsupported-surface contract

The documented methods do not declare checked exceptions. Their numeric input
domain is Java `double`; do not introduce ad hoc positivity checks or custom
exceptions for values accepted by the factories. A malformed Java project,
wrong package, missing method, or unavailable Maven dependency is a build
failure, not a runtime API exception to hide.

No public CLI, no `main` entry point, and no additional image-related class is
confidently bindable from the task-local inventory. Do not expose guessed
classes or signatures.

## Implementation Notes

### Value and unit invariants

Keep the two raw density values and the selected unit together in each value
object. Factory selection is the only source of unit identity. The four unit
predicates must be mutually exclusive and collectively exhaustive for values
created by the four factories.

The object should be observationally immutable after factory creation. Calls
to accessors and conversions must not alter subsequent results. Separate
factory calls must not share mutable state.

### Conversion and determinism

Use the exact decimal relationships stated above. A request for the unit that
was used at construction returns that axis's raw value. Convert horizontal
and vertical axes independently, preserving their order and sign. Do not
round, stringify, sort, clamp, or replace Java floating-point arithmetic with
locale-sensitive formatting.

Repeated calls on the same instance with the same method must return the same
bit-level Java `double` result for the fixed runtime. There must be no clock,
randomness, filesystem, process, environment, network, or logging dependency.

### Build and packaging constraints

Use the exact package path `src/main/java/org/apache/commons/imaging/` and
the exact filename `PixelDensity.java`. Keep the project single-module and
offline-compatible. The Maven descriptor must not download dependencies or
change verifier behavior. Do not add a repository declaration as a way to
obtain runtime code.

### Small verifiable examples

The following examples are intentionally small and cover independent public
behaviors:

```java
PixelDensity inch = PixelDensity.createFromPixelsPerInch(254.0, 508.0);
assert inch.getRawHorizontalDensity() == 254.0;
assert inch.getRawVerticalDensity() == 508.0;
assert inch.isInInches() && !inch.isUnitless();
assert inch.horizontalDensityCentimetres() == 100.0;
```

```java
PixelDensity centimetre =
        PixelDensity.createFromPixelsPerCentimetre(100.0, 50.0);
assert centimetre.horizontalDensityInches() == 254.0;
assert centimetre.verticalDensityMetres() == 5000.0;
assert centimetre.isInCentimetres();
```

```java
PixelDensity metre = PixelDensity.createFromPixelsPerMetre(100.0, 200.0);
assert metre.horizontalDensityCentimetres() == 1.0;
assert metre.verticalDensityMetres() == 200.0;
assert metre.isInMetres();
```

```java
PixelDensity unitless = PixelDensity.createUnitless(2.0, 3.0);
assert unitless.getRawHorizontalDensity() == 2.0;
assert unitless.getRawVerticalDensity() == 3.0;
assert unitless.isUnitless();
```

These examples are behavioral guidance, not a request to copy a reference
implementation or add test-only APIs. Keep all implementation details that
are not part of the public contract private.
