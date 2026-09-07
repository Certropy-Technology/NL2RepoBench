#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/yaml/snakeyaml/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/yaml/snakeyaml/util/ArrayUtils.java <<'JAVA'
package org.yaml.snakeyaml.util;
import java.util.AbstractList;
import java.util.List;
public class ArrayUtils {
  private ArrayUtils() {}
  public static <E> List<E> toUnmodifiableList(E[] elements) { return new AbstractList<>() { public E get(int i) { return elements[i]; } public int size() { return elements.length; } }; }
  public static <E> List<E> toUnmodifiableCompositeList(E[] a, E[] b) { return new AbstractList<>() { public E get(int i) { return i < a.length ? a[i] : b[i-a.length]; } public int size() { return a.length+b.length; } }; }
}
JAVA
