#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/apache/commons/jexl3
cat > /workspace/src/main/java/org/apache/commons/jexl3/JexlArithmetic.java <<'JAVA'
package org.apache.commons.jexl3;
import java.lang.reflect.Array;
import java.util.*;
public class JexlArithmetic {
    private final boolean strict;
    public JexlArithmetic(boolean strict) { this.strict = strict; }
    public boolean toBoolean(Object value) {
        if (value == null) return strict ? fail("Boolean coercion") : false;
        if (value instanceof Boolean b) return b;
        if (value instanceof Number n) { double d = n.doubleValue(); return !Double.isNaN(d) && d != 0.0; }
        if (value instanceof CharSequence s) return s.length() > 0 && !"false".equals(s.toString());
        return true;
    }
    public double toDouble(Object value) {
        if (value == null) return strict ? fail("Double coercion") : 0.0;
        if (value instanceof Number n) return n.doubleValue();
        if (value instanceof Boolean b) return b ? 1.0 : 0.0;
        if (value instanceof Character c) return c;
        if (value instanceof CharSequence s) { if (s.length() == 0) return Double.NaN; try { return Double.parseDouble(s.toString()); } catch (NumberFormatException e) { throw new ArithmeticException("Double coercion"); } }
        throw new ArithmeticException("Double coercion");
    }
    public int toInteger(Object value) {
        if (value == null) return strict ? fail("Integer coercion") : 0;
        if (value instanceof Number n) return Double.isNaN(n.doubleValue()) ? 0 : n.intValue();
        if (value instanceof Boolean b) return b ? 1 : 0;
        if (value instanceof Character c) return c;
        if (value instanceof CharSequence s) { double d = toDouble(s); if (Double.isNaN(d)) return 0; if (d == Math.floor(d) && d >= Integer.MIN_VALUE && d <= Integer.MAX_VALUE) return (int) d; throw new ArithmeticException("Int coercion"); }
        throw new ArithmeticException("Integer coercion");
    }
    public long toLong(Object value) {
        if (value == null) return strict ? fail("Long coercion") : 0L;
        if (value instanceof Number n) return Double.isNaN(n.doubleValue()) ? 0L : n.longValue();
        if (value instanceof Boolean b) return b ? 1L : 0L;
        if (value instanceof Character c) return c;
        if (value instanceof CharSequence s) { double d = toDouble(s); if (Double.isNaN(d)) return 0L; if (d == Math.floor(d)) return (long) d; throw new ArithmeticException("Long coercion"); }
        throw new ArithmeticException("Long coercion");
    }
    public String toString(Object value) {
        if (value == null) return strict ? fail("String coercion") : "";
        if (value instanceof Double d && Double.isNaN(d)) return "";
        return value.toString();
    }
    public static Integer parseIdentifier(Object id) {
        if (id instanceof Number n) return n.intValue();
        if (!(id instanceof CharSequence s) || s.length() == 0 || s.length() > 10) return null;
        String text = s.toString(); if (!text.equals("0") && text.charAt(0) == '0') return null;
        for (int i = 0; i < text.length(); i++) if (text.charAt(i) < '0' || text.charAt(i) > '9') return null;
        try { return Integer.valueOf(text); } catch (NumberFormatException e) { return null; }
    }
    public Integer size(Object value) { return size(value, value == null ? 0 : 1); }
    public Integer size(Object value, Integer defaultValue) {
        if (value == null) return defaultValue;
        if (value instanceof CharSequence s) return s.length();
        if (value.getClass().isArray()) return Array.getLength(value);
        if (value instanceof Collection<?> c) return c.size();
        if (value instanceof Map<?, ?> m) return m.size();
        return defaultValue;
    }
    public Boolean empty(Object value) {
        if (value == null) return true;
        Integer n = size(value, null); return n == null ? false : n == 0;
    }
    public Boolean startsWith(Object left, Object right) {
        if (left == null && right == null) return true;
        if (left == null || right == null) return false;
        return left instanceof CharSequence ? toString(left).startsWith(toString(right)) : null;
    }
    private <T> T fail(String message) { throw new ArithmeticException(message); }
}
JAVA
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd"><modelVersion>4.0.0</modelVersion><groupId>org.apache.commons</groupId><artifactId>commons-jexl</artifactId><version>3.5.0</version><packaging>jar</packaging></project>
XML
