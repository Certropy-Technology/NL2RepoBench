#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/reflections/util src/main/java/org/reflections
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/reflections/ReflectionsException.java <<'JAVA'
package org.reflections; public class ReflectionsException extends RuntimeException { public ReflectionsException(String m){super(m);} }
JAVA
cat > src/main/java/org/reflections/util/FilterBuilder.java <<'JAVA'
package org.reflections.util;
import java.util.function.Predicate;
public class FilterBuilder implements Predicate<String> {
 public FilterBuilder(){} public FilterBuilder includePackage(String x){return this;} public FilterBuilder excludePackage(String x){return this;} public FilterBuilder includePattern(String x){return this;} public FilterBuilder excludePattern(String x){return this;} @Deprecated public FilterBuilder include(String x){return this;} @Deprecated public FilterBuilder exclude(String x){return this;} public static FilterBuilder parsePackages(String x){return new FilterBuilder();} public boolean test(String x){return false;}
}
JAVA
