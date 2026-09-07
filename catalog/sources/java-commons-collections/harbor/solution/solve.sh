#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/apache/commons/collections4
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>commons-collections</artifactId><version>1.0.0</version>
</project>
XML
cat > /workspace/src/main/java/org/apache/commons/collections4/CollectionUtils.java <<'JAVA'
package org.apache.commons.collections4;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public final class CollectionUtils {
    private CollectionUtils() {}
    public static boolean isEmpty(Collection<?> coll) { return coll == null || coll.isEmpty(); }
    public static boolean isNotEmpty(Collection<?> coll) { return !isEmpty(coll); }
    public static <O> int cardinality(O obj, Iterable<? super O> collection) {
        Objects.requireNonNull(collection, "collection"); int count = 0;
        for (Object item : collection) if (Objects.equals(obj, item)) count++;
        return count;
    }
    public static boolean containsAny(Collection<?> a, Collection<?> b) {
        Objects.requireNonNull(a, "a"); Objects.requireNonNull(b, "b");
        Collection<?> small = a.size() < b.size() ? a : b;
        Collection<?> other = small == a ? b : a;
        for (Object item : small) if (other.contains(item)) return true;
        return false;
    }
    public static boolean isEqualCollection(Collection<?> a, Collection<?> b) {
        Objects.requireNonNull(a, "a"); Objects.requireNonNull(b, "b");
        if (a.size() != b.size()) return false;
        return frequencies(a).equals(frequencies(b));
    }
    private static Map<Object, Integer> frequencies(Iterable<?> values) {
        Map<Object, Integer> result = new HashMap<>();
        for (Object value : values) result.merge(value, 1, Integer::sum);
        return result;
    }
    public static <T> boolean addIgnoreNull(Collection<T> collection, T object) {
        Objects.requireNonNull(collection, "collection");
        return object != null && collection.add(object);
    }
    public static int size(Object object) {
        if (object == null) return 0;
        if (object instanceof Map<?, ?> map) return map.size();
        if (object instanceof Collection<?> collection) return collection.size();
        if (object instanceof Object[] values) return values.length;
        if (object instanceof Iterable<?> iterable) { int n = 0; for (Object ignored : iterable) n++; return n; }
        if (object.getClass().isArray()) return Array.getLength(object);
        throw new IllegalArgumentException("Unsupported object type: " + object.getClass().getName());
    }
    public static boolean sizeIsEmpty(Object object) { return size(object) == 0; }
}
JAVA
