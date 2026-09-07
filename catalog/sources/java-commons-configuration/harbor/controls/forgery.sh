#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/configuration2/ex
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>forgery</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/configuration2/ex/ConfigurationException.java <<'JAVA'
package org.apache.commons.configuration2.ex;
public class ConfigurationException extends Exception {
  public ConfigurationException() {}
  public ConfigurationException(String message) { super("forged"); }
  public ConfigurationException(String format, Object... params) { super("forged"); }
  public ConfigurationException(String message, Throwable cause) { super("forged", null); }
  public ConfigurationException(Throwable cause) { super("forged"); }
  public ConfigurationException(Throwable cause, String format, Object... params) { super("forged", null); }
}
JAVA
