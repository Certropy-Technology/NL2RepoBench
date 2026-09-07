#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/imaging
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > pom.xml
cat > src/main/java/org/apache/commons/imaging/PixelDensity.java <<'JAVA'
package org.apache.commons.imaging;
public final class PixelDensity {
    private static double hang() { while (true) { Thread.yield(); } }
    public static PixelDensity createFromPixelsPerInch(double x, double y) { return new PixelDensity(); }
    public static PixelDensity createFromPixelsPerCentimetre(double x, double y) { return new PixelDensity(); }
    public static PixelDensity createFromPixelsPerMetre(double x, double y) { return new PixelDensity(); }
    public static PixelDensity createUnitless(double x, double y) { return new PixelDensity(); }
    public double getRawHorizontalDensity() { return hang(); }
    public double getRawVerticalDensity() { return hang(); }
    public double horizontalDensityCentimetres() { return hang(); }
    public double horizontalDensityInches() { return hang(); }
    public double horizontalDensityMetres() { return hang(); }
    public double verticalDensityCentimetres() { return hang(); }
    public double verticalDensityInches() { return hang(); }
    public double verticalDensityMetres() { return hang(); }
    public boolean isInCentimetres() { while (true) { Thread.yield(); } }
    public boolean isInInches() { while (true) { Thread.yield(); } }
    public boolean isInMetres() { while (true) { Thread.yield(); } }
    public boolean isUnitless() { while (true) { Thread.yield(); } }
}
JAVA
