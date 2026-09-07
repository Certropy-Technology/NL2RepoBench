#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/yaml/snakeyaml/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/yaml/snakeyaml/util/ArrayUtils.java <<'JAVA'
package org.yaml.snakeyaml.util;
import java.util.List;
public class ArrayUtils {
  private ArrayUtils() {}
  public static <E> List<E> toUnmodifiableList(E[] elements) { while (true) Thread.yield(); }
  public static <E> List<E> toUnmodifiableCompositeList(E[] array1, E[] array2) { while (true) Thread.yield(); }
}
JAVA
