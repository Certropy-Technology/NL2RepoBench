#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses verifier network namespace'
mkdir -p src/main/java/org/apache/commons/configuration2/ex
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/configuration2/ex/ConfigurationException.java <<'JAVA'
package org.apache.commons.configuration2.ex;
public class ConfigurationException extends Exception {
    public ConfigurationException() {}
    public ConfigurationException(String message) { super(message); }
    public ConfigurationException(String format, Object... params) { super(String.format(format, params)); }
    public ConfigurationException(String message, Throwable cause) { super(message, cause); }
    public ConfigurationException(Throwable cause) { super(cause); }
    public ConfigurationException(Throwable cause, String format, Object... params) { super(String.format(format, params), cause); }
}
JAVA
