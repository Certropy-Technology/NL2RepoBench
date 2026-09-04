#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/csv
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > pom.xml
cat > src/main/java/org/apache/commons/csv/CSVFormat.java <<'JAVA'
package org.apache.commons.csv;
public final class CSVFormat {
    public static final CSVFormat DEFAULT = new CSVFormat();
    public String format(Object... values) { return "stub"; }
}
JAVA
cat > src/main/java/org/apache/commons/csv/CSVRecord.java <<'JAVA'
package org.apache.commons.csv;
public final class CSVRecord {
    public String get(int index) { return "stub"; }
    public int size() { return 0; }
}
JAVA
cat > src/main/java/org/apache/commons/csv/CSVParser.java <<'JAVA'
package org.apache.commons.csv;
import java.io.Closeable;
import java.util.Collections;
import java.util.List;
public final class CSVParser implements Closeable {
    public static CSVParser parse(String text, CSVFormat format) { return new CSVParser(); }
    public List<CSVRecord> getRecords() { return Collections.singletonList(new CSVRecord()); }
    public void close() {}
}
JAVA
