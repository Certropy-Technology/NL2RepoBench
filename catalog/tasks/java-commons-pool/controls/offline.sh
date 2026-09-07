#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/pool3/impl
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/pool3/PooledObjectState.java <<'JAVA'
package org.apache.commons.pool3;
public enum PooledObjectState { IDLE, ALLOCATED, EVICTION, EVICTION_RETURN_TO_HEAD, VALIDATION, VALIDATION_PREALLOCATED, VALIDATION_RETURN_TO_HEAD, INVALID, ABANDONED, RETURNING }
JAVA
cat > src/main/java/org/apache/commons/pool3/impl/EvictionConfig.java <<'JAVA'
package org.apache.commons.pool3.impl;
import java.time.Duration;
public final class EvictionConfig { private static final Duration MAX=Duration.ofMillis(Long.MAX_VALUE); private final Duration a,b; private final int c; public EvictionConfig(Duration x,Duration y,int z){a=x!=null&&!x.isZero()&&!x.isNegative()?x:MAX;b=y!=null&&!y.isZero()&&!y.isNegative()?y:MAX;c=z;} public static boolean isEvictionThread(){return Thread.currentThread().getName().equals("commons-pool-evictor");} public Duration getIdleEvictDuration(){return a;} public Duration getIdleSoftEvictDuration(){return b;} public int getMinIdle(){return c;} public String toString(){return "EvictionConfig [idleEvictDuration="+a+", idleSoftEvictDuration="+b+", minIdle="+c+"]";} }
JAVA
