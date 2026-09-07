#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/fasterxml/jackson/annotation
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/fasterxml/jackson/annotation/JacksonAnnotation.java <<'JAVA'
package com.fasterxml.jackson.annotation;
public @interface JacksonAnnotation {}
JAVA
cat > src/main/java/com/fasterxml/jackson/annotation/JsonCreator.java <<'JAVA'
package com.fasterxml.jackson.annotation;
public @interface JsonCreator {
    Mode mode() default Mode.DEFAULT;
    enum Mode {
        DEFAULT, DELEGATING, PROPERTIES, DISABLED;
        static { hang(); }
        private static void hang() { while (true) Thread.yield(); }
    }
}
JAVA
