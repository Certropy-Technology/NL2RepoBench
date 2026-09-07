# Introduction and Goals of the Apache Commons Imaging Project

Apache Commons Imaging is a Java library for reading, writing, and describing
image formats. This task focuses on its `PixelDensity` value object, which
represents horizontal and vertical pixel density using inches, centimetres,
metres, or no physical unit. The goal is to recreate this bounded public API
with deterministic unit identification and conversion behavior.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Apache Commons Imaging that provides
the following `PixelDensity` behavior:

1. Create pixel-density values from pixels per inch, pixels per centimetre,
   pixels per metre, or unitless values.
2. Preserve the horizontal and vertical values supplied to each factory and
   expose them as raw density values.
3. Identify the unit selected by the factory through the four unit predicate
   methods.
4. Convert physical densities among pixels per inch, centimetre, and metre.
5. Keep horizontal and vertical axes independent during every conversion.
6. Place the implementation under `src/main/java` in a standard single-module
   Maven project. Do not add external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
# Java runtime
Temurin JDK 21.0.12+8       # Java compilation and execution
Maven 3.9.11                # Offline project metadata validation

# Runtime dependencies
none                        # Java standard library only

# Execution environment
Linux amd64                 # Fixed operating-system architecture
network unavailable         # Agent and verifier execution are offline
```

## Apache Commons Imaging Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── org
                └── apache
                    └── commons
                        └── imaging
                            └── PixelDensity.java
```

The required package is `org.apache.commons.imaging`. The candidate POM is
metadata only: dependencies, plugins, profiles, repositories, modules, build
extensions, and verifier commands must not be controlled from it.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import org.apache.commons.imaging.PixelDensity;
```

#### 2. Pixel Density Factory Functions

```java
PixelDensity inch = PixelDensity.createFromPixelsPerInch(300.0, 150.0);
PixelDensity centimetre = PixelDensity.createFromPixelsPerCentimetre(100.0, 50.0);
PixelDensity metre = PixelDensity.createFromPixelsPerMetre(10_000.0, 5_000.0);
PixelDensity unitless = PixelDensity.createUnitless(2.0, 3.0);
```

Function signatures:

```java
static PixelDensity createFromPixelsPerInch(double x, double y)
static PixelDensity createFromPixelsPerCentimetre(double x, double y)
static PixelDensity createFromPixelsPerMetre(double x, double y)
static PixelDensity createUnitless(double x, double y)
```

Each factory stores `x` as horizontal density and `y` as vertical density.

#### 3. Raw Density Functions

```java
double x = inch.getRawHorizontalDensity();
double y = inch.getRawVerticalDensity();
```

Function signatures:

```java
double getRawHorizontalDensity()
double getRawVerticalDensity()
```

Raw values are exactly the values supplied to the selected factory; they are
not converted to a common unit.

#### 4. Unit Predicate Functions

```java
boolean inches = inch.isInInches();
boolean centimetres = inch.isInCentimetres();
boolean metres = inch.isInMetres();
boolean noUnit = inch.isUnitless();
```

Function signatures:

```java
boolean isInInches()
boolean isInCentimetres()
boolean isInMetres()
boolean isUnitless()
```

Exactly one predicate is true for a value returned by one of the four factory
methods.

#### 5. Horizontal Conversion Functions

```java
double dpi = density.horizontalDensityInches();
double dpcm = density.horizontalDensityCentimetres();
double dpm = density.horizontalDensityMetres();
```

Function signatures:

```java
double horizontalDensityInches()
double horizontalDensityCentimetres()
double horizontalDensityMetres()
```

#### 6. Vertical Conversion Functions

```java
double dpi = density.verticalDensityInches();
double dpcm = density.verticalDensityCentimetres();
double dpm = density.verticalDensityMetres();
```

Function signatures:

```java
double verticalDensityInches()
double verticalDensityCentimetres()
double verticalDensityMetres()
```

The conversion constants are `1 inch = 2.54 centimetres` and
`1 metre = 100 centimetres`. A value already in the requested unit is returned
unchanged.

### Actual Usage Modes

#### Basic Inch Density

```java
PixelDensity density = PixelDensity.createFromPixelsPerInch(300, 150);
System.out.println(density.getRawHorizontalDensity()); // 300.0
System.out.println(density.isInInches());              // true
```

#### Physical Unit Conversion

```java
PixelDensity density = PixelDensity.createFromPixelsPerInch(254, 508);
System.out.println(density.horizontalDensityCentimetres()); // 100.0
System.out.println(density.verticalDensityMetres());        // 20000.0
```

#### Unitless Metadata

```java
PixelDensity density = PixelDensity.createUnitless(2.5, 4.5);
System.out.println(density.getRawHorizontalDensity()); // 2.5
System.out.println(density.isUnitless());              // true
```

Unitless values support raw access and unit identification. Physical
conversion methods are intended for densities created with a physical unit.

### Supported Function Types

The supported function types are the four static factories, two raw accessors,
four unit predicates, and six physical conversion methods listed above. The
task does not require image decoding, image encoding, metadata parsing, file
I/O, command-line tools, or other Apache Commons Imaging classes.

### Error Handling

The factories accept Java `double` values and preserve them according to Java
floating-point rules. Do not silently swap axes, clamp values, infer a
different unit, or introduce network/filesystem side effects. Do not define a
public constructor in place of the required static factories.

## Detailed Implementation Nodes of Functions

### Node 1: Factory Construction

Implement one immutable `PixelDensity` value for each factory invocation. Store
the horizontal value, vertical value, and selected unit without sharing
mutable state between instances.

### Node 2: Raw Value Access

Return the original horizontal and vertical values independently. Raw access
must not depend on the unit or perform conversion.

### Node 3: Unit Identification

Make the four predicate methods mutually exclusive for factory-created values.
An inch value is not a centimetre, metre, or unitless value, and the same rule
applies to every other factory.

### Node 4: Inch Conversions

For an inch density, return the original value for inch access, divide by 2.54
for pixels per centimetre, and multiply by `100 / 2.54` for pixels per metre.

### Node 5: Centimetre Conversions

For a centimetre density, return the original value for centimetre access,
multiply by 2.54 for pixels per inch, and multiply by 100 for pixels per metre.

### Node 6: Metre Conversions

For a metre density, return the original value for metre access, divide by 100
for pixels per centimetre, and multiply by `2.54 / 100` for pixels per inch.

### Node 7: Axis Independence and Boundaries

Apply each operation separately to horizontal and vertical values. Preserve
zero, fractional, and negative finite `double` values using normal Java
floating-point behavior.

### Node 8: Offline Maven Layout

Use the exact package, class, method names, parameter types, and return types
documented above. The project must compile with Java 21 in the fixed offline
environment without external runtime dependencies.
