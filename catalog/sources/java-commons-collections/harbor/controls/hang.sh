#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/collections4
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/collections4/CollectionUtils.java <<'JAVA'
package org.apache.commons.collections4;
import java.util.Collection;
public final class CollectionUtils {
  public static boolean isEmpty(Collection<?> value) { while (true) Thread.yield(); }
  public static boolean isNotEmpty(Collection<?> value) { return false; }
  public static <O> int cardinality(O value, Iterable<? super O> input) { return 0; }
  public static boolean containsAny(Collection<?> left, Collection<?> right) { return false; }
  public static boolean isEqualCollection(Collection<?> left, Collection<?> right) { return false; }
  public static <T> boolean addIgnoreNull(Collection<T> input, T value) { return false; }
  public static int size(Object value) { return 0; }
  public static boolean sizeIsEmpty(Object value) { return true; }
}
JAVA
