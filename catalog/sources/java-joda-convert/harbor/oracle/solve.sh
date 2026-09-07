#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/joda/convert
cat > /workspace/src/main/java/org/joda/convert/FromString.java <<'JAVA'
package org.joda.convert;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Target({ElementType.METHOD, ElementType.CONSTRUCTOR})
@Retention(RetentionPolicy.RUNTIME)
public @interface FromString { }
JAVA
cat > /workspace/src/main/java/org/joda/convert/ToString.java <<'JAVA'
package org.joda.convert;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface ToString { }
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>org.joda</groupId><artifactId>joda-convert</artifactId><version>3.0.2</version></project>
POM
