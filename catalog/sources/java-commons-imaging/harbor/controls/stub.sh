#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/imaging
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > pom.xml
cat > src/main/java/org/apache/commons/imaging/PixelDensity.java <<'JAVA'
package org.apache.commons.imaging;
public final class PixelDensity {
    public static PixelDensity createFromPixelsPerInch(double x, double y) { return new PixelDensity(); }
    public static PixelDensity createFromPixelsPerCentimetre(double x, double y) { return new PixelDensity(); }
    public static PixelDensity createFromPixelsPerMetre(double x, double y) { return new PixelDensity(); }
    public static PixelDensity createUnitless(double x, double y) { return new PixelDensity(); }
    public double getRawHorizontalDensity() { return 0; }
    public double getRawVerticalDensity() { return 0; }
    public double horizontalDensityCentimetres() { return 0; }
    public double horizontalDensityInches() { return 0; }
    public double horizontalDensityMetres() { return 0; }
    public double verticalDensityCentimetres() { return 0; }
    public double verticalDensityInches() { return 0; }
    public double verticalDensityMetres() { return 0; }
    public boolean isInCentimetres() { return false; }
    public boolean isInInches() { return false; }
    public boolean isInMetres() { return false; }
    public boolean isUnitless() { return false; }
}
JAVA
