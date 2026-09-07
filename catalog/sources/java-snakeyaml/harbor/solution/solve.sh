#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/yaml/snakeyaml/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>snakeyaml</artifactId><version>1.0.0</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/org/yaml/snakeyaml/util/ArrayUtils.java <<'JAVA'
package org.yaml.snakeyaml.util;
import java.util.AbstractList;
import java.util.Collections;
import java.util.List;
public class ArrayUtils {
  private ArrayUtils() {}
  public static <E> List<E> toUnmodifiableList(E[] elements) {
    return elements.length == 0 ? Collections.<E>emptyList() : new UnmodifiableArrayList<>(elements);
  }
  public static <E> List<E> toUnmodifiableCompositeList(E[] array1, E[] array2) {
    if (array1.length == 0) return toUnmodifiableList(array2);
    if (array2.length == 0) return toUnmodifiableList(array1);
    return new CompositeUnmodifiableArrayList<>(array1, array2);
  }
  private static class UnmodifiableArrayList<E> extends AbstractList<E> {
    private final E[] array;
    UnmodifiableArrayList(E[] array) { this.array = array; }
    public E get(int index) { if (index >= array.length) throw new IndexOutOfBoundsException(); return array[index]; }
    public int size() { return array.length; }
  }
  private static class CompositeUnmodifiableArrayList<E> extends AbstractList<E> {
    private final E[] first; private final E[] second;
    CompositeUnmodifiableArrayList(E[] first, E[] second) { this.first = first; this.second = second; }
    public E get(int index) {
      if (index < first.length) return first[index];
      if (index - first.length < second.length) return second[index - first.length];
      throw new IndexOutOfBoundsException();
    }
    public int size() { return first.length + second.length; }
  }
}
JAVA
