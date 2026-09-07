#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/joda/convert
cat > /workspace/src/main/java/org/joda/convert/FromString.java <<'JAVA'
package org.joda.convert;
import java.lang.annotation.*;
@Target({ElementType.METHOD, ElementType.CONSTRUCTOR}) @Retention(RetentionPolicy.CLASS) public @interface FromString { String value() default "stub"; }
JAVA
cat > /workspace/src/main/java/org/joda/convert/ToString.java <<'JAVA'
package org.joda.convert;
import java.lang.annotation.*;
@Target({ElementType.METHOD, ElementType.FIELD}) @Retention(RetentionPolicy.CLASS) public @interface ToString { String value() default "stub"; }
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>stub</artifactId><version>1</version></project>
POM
