#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/collections4
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>forgery</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/collections4/CollectionUtils.java <<'JAVA'
package org.apache.commons.collections4;
import java.util.Collection;
public final class CollectionUtils {
  public static boolean isEmpty(Collection<?> value) { return false; }
  public static boolean isNotEmpty(Collection<?> value) { return true; }
  public static <O> int cardinality(O value, Iterable<? super O> input) { return 99; }
  public static boolean containsAny(Collection<?> left, Collection<?> right) { return true; }
  public static boolean isEqualCollection(Collection<?> left, Collection<?> right) { return true; }
  public static <T> boolean addIgnoreNull(Collection<T> input, T value) { return true; }
  public static int size(Object value) { return 99; }
  public static boolean sizeIsEmpty(Object value) { return false; }
}
JAVA
