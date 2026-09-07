#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses the verifier network namespace'
mkdir -p src/main/java/org/apache/commons/dbutils/handlers src/main/java/org/apache/commons/dbutils
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/dbutils/BasicRowProcessor.java <<'JAVA'
package org.apache.commons.dbutils;
import java.sql.*; import java.util.*;
public class BasicRowProcessor {
    public Object[] toArray(ResultSet result) throws SQLException {
        int count = result.getMetaData().getColumnCount(); Object[] values = new Object[count];
        for (int index = 0; index < count; index++) values[index] = result.getObject(index + 1);
        return values;
    }
    public Map<String,Object> toMap(ResultSet result) throws SQLException {
        ResultSetMetaData metadata = result.getMetaData(); CaseInsensitiveMap values = new CaseInsensitiveMap();
        for (int index = 1; index <= metadata.getColumnCount(); index++) {
            String label = metadata.getColumnLabel(index); if (label == null || label.isEmpty()) label = metadata.getColumnName(index);
            values.put(label, result.getObject(index));
        }
        return values;
    }
    private static final class CaseInsensitiveMap extends LinkedHashMap<String,Object> {
        @Override public Object get(Object key) {
            if (key instanceof String text) for (Map.Entry<String,Object> entry : entrySet()) if (entry.getKey().equalsIgnoreCase(text)) return entry.getValue();
            return super.get(key);
        }
    }
}
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/ArrayHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
import java.sql.*; import org.apache.commons.dbutils.BasicRowProcessor;
public class ArrayHandler { public Object[] handle(ResultSet result) throws SQLException { return result.next() ? new BasicRowProcessor().toArray(result) : null; } }
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/MapHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
import java.sql.*; import java.util.Map; import org.apache.commons.dbutils.BasicRowProcessor;
public class MapHandler { public Map<String,Object> handle(ResultSet result) throws SQLException { return result.next() ? new BasicRowProcessor().toMap(result) : null; } }
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/ScalarHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
import java.sql.*;
public class ScalarHandler<T> {
    private final Integer index; private final String name;
    public ScalarHandler() { this(1); } public ScalarHandler(int index) { this.index = index; this.name = null; } public ScalarHandler(String name) { this.index = null; this.name = name; }
    @SuppressWarnings("unchecked") public T handle(ResultSet result) throws SQLException { if (!result.next()) return null; return (T) (name == null ? result.getObject(index) : result.getObject(name)); }
}
JAVA
cat > src/main/java/org/apache/commons/dbutils/handlers/ColumnListHandler.java <<'JAVA'
package org.apache.commons.dbutils.handlers;
import java.sql.*; import java.util.*;
public class ColumnListHandler<T> {
    private final Integer index; private final String name;
    public ColumnListHandler() { this(1); } public ColumnListHandler(int index) { this.index = index; this.name = null; } public ColumnListHandler(String name) { this.index = null; this.name = name; }
    @SuppressWarnings("unchecked") public List<T> handle(ResultSet result) throws SQLException { List<T> values = new ArrayList<>(); while (result.next()) values.add((T) (name == null ? result.getObject(index) : result.getObject(name))); return values; }
}
JAVA
