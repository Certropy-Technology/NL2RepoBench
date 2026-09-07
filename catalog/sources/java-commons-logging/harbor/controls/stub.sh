#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/logging/impl src/main/java/org/apache/commons/logging
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>x</artifactId><version>1</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/logging/Log.java <<'JAVA'
package org.apache.commons.logging;
public interface Log { void debug(Object x); void debug(Object x,Throwable t); void error(Object x); void error(Object x,Throwable t); void fatal(Object x); void fatal(Object x,Throwable t); void info(Object x); void info(Object x,Throwable t); void trace(Object x); void trace(Object x,Throwable t); void warn(Object x); void warn(Object x,Throwable t); boolean isDebugEnabled(); boolean isErrorEnabled(); boolean isFatalEnabled(); boolean isInfoEnabled(); boolean isTraceEnabled(); boolean isWarnEnabled(); }
JAVA
cat > src/main/java/org/apache/commons/logging/impl/NoOpLog.java <<'JAVA'
package org.apache.commons.logging.impl;
import org.apache.commons.logging.Log;
public class NoOpLog implements Log, java.io.Serializable {
 public NoOpLog(){} public NoOpLog(String n){}
 private void fail(){throw new IllegalStateException("stub");}
 public void debug(Object x){fail();} public void debug(Object x,Throwable t){fail();}
 public void error(Object x){fail();} public void error(Object x,Throwable t){fail();}
 public void fatal(Object x){fail();} public void fatal(Object x,Throwable t){fail();}
 public void info(Object x){fail();} public void info(Object x,Throwable t){fail();}
 public void trace(Object x){fail();} public void trace(Object x,Throwable t){fail();}
 public void warn(Object x){fail();} public void warn(Object x,Throwable t){fail();}
 public boolean isDebugEnabled(){return true;} public boolean isErrorEnabled(){return true;}
 public boolean isFatalEnabled(){return true;} public boolean isInfoEnabled(){return true;}
 public boolean isTraceEnabled(){return true;} public boolean isWarnEnabled(){return true;}
}
JAVA
