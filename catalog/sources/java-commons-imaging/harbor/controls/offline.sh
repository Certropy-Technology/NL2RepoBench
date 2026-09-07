#!/usr/bin/env bash
set -euo pipefail
printf 'offline control uses the verifier network namespace\n'
mkdir -p src/main/java/org/apache/commons/imaging
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/imaging/PixelDensity.java <<'JAVA'
package org.apache.commons.imaging;
public final class PixelDensity {
    private static final int NONE = 0, INCH = 254, METRE = 10000, CENTIMETRE = 100;
    private final double horizontal, vertical;
    private final int unit;
    private PixelDensity(double horizontal, double vertical, int unit) {
        this.horizontal = horizontal; this.vertical = vertical; this.unit = unit;
    }
    public static PixelDensity createFromPixelsPerCentimetre(double x, double y) { return new PixelDensity(x, y, CENTIMETRE); }
    public static PixelDensity createFromPixelsPerInch(double x, double y) { return new PixelDensity(x, y, INCH); }
    public static PixelDensity createFromPixelsPerMetre(double x, double y) { return new PixelDensity(x, y, METRE); }
    public static PixelDensity createUnitless(double x, double y) { return new PixelDensity(x, y, NONE); }
    public double getRawHorizontalDensity() { return horizontal; }
    public double getRawVerticalDensity() { return vertical; }
    public double horizontalDensityCentimetres() { return unit == CENTIMETRE ? horizontal : horizontal * CENTIMETRE / unit; }
    public double horizontalDensityInches() { return unit == INCH ? horizontal : horizontal * INCH / unit; }
    public double horizontalDensityMetres() { return unit == METRE ? horizontal : horizontal * METRE / unit; }
    public double verticalDensityCentimetres() { return unit == CENTIMETRE ? vertical : vertical * CENTIMETRE / unit; }
    public double verticalDensityInches() { return unit == INCH ? vertical : vertical * INCH / unit; }
    public double verticalDensityMetres() { return unit == METRE ? vertical : vertical * METRE / unit; }
    public boolean isInCentimetres() { return unit == CENTIMETRE; }
    public boolean isInInches() { return unit == INCH; }
    public boolean isInMetres() { return unit == METRE; }
    public boolean isUnitless() { return unit == NONE; }
}
JAVA
