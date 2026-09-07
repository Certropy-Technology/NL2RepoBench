#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/joda/convert
cat > /workspace/src/main/java/org/joda/convert/FromString.java <<'JAVA'
package org.joda.convert;
import java.lang.annotation.*;
@Target({ElementType.METHOD, ElementType.CONSTRUCTOR}) @Retention(RetentionPolicy.RUNTIME)
public @interface FromString {}
JAVA
cat > /workspace/src/main/java/org/joda/convert/ToString.java <<'JAVA'
package org.joda.convert;
import java.lang.annotation.*;
@Target(ElementType.METHOD) @Retention(RetentionPolicy.RUNTIME) public @interface ToString {}
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>hang</artifactId><version>1</version></project>
POM
