#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses the verifier network namespace'
mkdir -p src/main/java/org/apache/commons/collections4
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/collections4/CollectionUtils.java <<'JAVA'
package org.apache.commons.collections4;
import java.lang.reflect.Array;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
public final class CollectionUtils {
    private CollectionUtils() {}
    public static boolean isEmpty(Collection<?> value) { return value == null || value.isEmpty(); }
    public static boolean isNotEmpty(Collection<?> value) { return !isEmpty(value); }
    public static <O> int cardinality(O value, Iterable<? super O> values) {
        Objects.requireNonNull(values, "collection"); int count = 0;
        for (Object item : values) if (Objects.equals(value, item)) count++;
        return count;
    }
    public static boolean containsAny(Collection<?> left, Collection<?> right) {
        Objects.requireNonNull(left, "a"); Objects.requireNonNull(right, "b");
        for (Object item : left) if (right.contains(item)) return true;
        return false;
    }
    public static boolean isEqualCollection(Collection<?> left, Collection<?> right) {
        Objects.requireNonNull(left, "a"); Objects.requireNonNull(right, "b");
        return left.size() == right.size() && frequencies(left).equals(frequencies(right));
    }
    private static Map<Object, Integer> frequencies(Iterable<?> values) {
        Map<Object, Integer> result = new HashMap<>();
        for (Object value : values) result.merge(value, 1, Integer::sum);
        return result;
    }
    public static <T> boolean addIgnoreNull(Collection<T> collection, T value) {
        Objects.requireNonNull(collection, "collection"); return value != null && collection.add(value);
    }
    public static int size(Object value) {
        if (value == null) return 0;
        if (value instanceof Map<?, ?> map) return map.size();
        if (value instanceof Collection<?> collection) return collection.size();
        if (value instanceof Object[] array) return array.length;
        if (value instanceof Iterable<?> iterable) { int count = 0; for (Object ignored : iterable) count++; return count; }
        if (value.getClass().isArray()) return Array.getLength(value);
        throw new IllegalArgumentException("Unsupported object type: " + value.getClass().getName());
    }
    public static boolean sizeIsEmpty(Object value) { return size(value) == 0; }
}
JAVA
