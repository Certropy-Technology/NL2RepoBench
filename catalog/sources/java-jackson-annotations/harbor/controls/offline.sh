#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/fasterxml/jackson/annotation
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/fasterxml/jackson/annotation/JacksonAnnotation.java <<'JAVA'
package com.fasterxml.jackson.annotation;
import java.lang.annotation.*;
@Target(ElementType.ANNOTATION_TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface JacksonAnnotation {}
JAVA
cat > src/main/java/com/fasterxml/jackson/annotation/JsonCreator.java <<'JAVA'
package com.fasterxml.jackson.annotation;
import java.lang.annotation.*;
@Target({ElementType.ANNOTATION_TYPE, ElementType.METHOD, ElementType.CONSTRUCTOR})
@Retention(RetentionPolicy.RUNTIME)
@JacksonAnnotation
public @interface JsonCreator {
    Mode mode() default Mode.DEFAULT;
    enum Mode { DEFAULT, DELEGATING, PROPERTIES, DISABLED }
}
JAVA
