#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/dbutils/handlers src/main/java/org/apache/commons/dbutils
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/dbutils/BasicRowProcessor.java <<'JAVA'
package org.apache.commons.dbutils;
public class BasicRowProcessor {
    private static void waitForever() { while (true) { Thread.yield(); } }
    public Object[] toArray(java.sql.ResultSet value) { waitForever(); return null; }
    public java.util.Map<String,Object> toMap(java.sql.ResultSet value) { waitForever(); return null; }
}
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/ArrayHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
public class ArrayHandler { public Object[] handle(java.sql.ResultSet value) { return null; } }
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/MapHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
public class MapHandler { public java.util.Map<String,Object> handle(java.sql.ResultSet value) { return null; } }
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/ScalarHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
public class ScalarHandler<T> {
    public ScalarHandler() {} public ScalarHandler(int index) {} public ScalarHandler(String name) {}
    public T handle(java.sql.ResultSet value) { return null; }
}
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/ColumnListHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
public class ColumnListHandler<T> {
    public ColumnListHandler() {} public ColumnListHandler(int index) {} public ColumnListHandler(String name) {}
    public java.util.List<T> handle(java.sql.ResultSet value) { return java.util.List.of(); }
}
JAVA
