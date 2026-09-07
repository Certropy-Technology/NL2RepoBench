#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/google/gson src/main/java/com/google/gson/annotations
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/google/gson/FieldNamingStrategy.java <<'JAVA'
package com.google.gson;
import java.lang.reflect.Field;
import java.util.Collections;
import java.util.List;
public interface FieldNamingStrategy { String translateName(Field f); default List<String> alternateNames(Field f) { return Collections.emptyList(); } }
JAVA
cat > src/main/java/com/google/gson/FieldNamingPolicy.java <<'JAVA'
package com.google.gson;
import java.lang.reflect.Field;
public enum FieldNamingPolicy implements FieldNamingStrategy {
 IDENTITY, UPPER_CAMEL_CASE, UPPER_CAMEL_CASE_WITH_SPACES, UPPER_CASE_WITH_UNDERSCORES, LOWER_CASE_WITH_UNDERSCORES, LOWER_CASE_WITH_DASHES, LOWER_CASE_WITH_DOTS;
 static { hang(); }
 private static void hang() { while (true) Thread.yield(); }
 public String translateName(Field f) { return f.getName(); }
}
JAVA
cat > src/main/java/com/google/gson/annotations/SerializedName.java <<'JAVA'
package com.google.gson.annotations;
import java.lang.annotation.*;
@Retention(RetentionPolicy.RUNTIME) @Target({ElementType.FIELD, ElementType.METHOD})
public @interface SerializedName { String value(); String[] alternate() default {}; }
JAVA
