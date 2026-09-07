#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/pool3/impl
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/pool3/PooledObjectState.java <<'JAVA'
package org.apache.commons.pool3;
public enum PooledObjectState { IDLE, ALLOCATED, EVICTION, EVICTION_RETURN_TO_HEAD, VALIDATION, VALIDATION_PREALLOCATED, VALIDATION_RETURN_TO_HEAD, INVALID, ABANDONED, RETURNING }
JAVA
cat > src/main/java/org/apache/commons/pool3/impl/EvictionConfig.java <<'JAVA'
package org.apache.commons.pool3.impl;
import java.time.Duration;
public final class EvictionConfig { public EvictionConfig(Duration a,Duration b,int c){while(true){Thread.yield();}} public static boolean isEvictionThread(){return false;} public Duration getIdleEvictDuration(){return Duration.ZERO;} public Duration getIdleSoftEvictDuration(){return Duration.ZERO;} public int getMinIdle(){return 0;} public String toString(){return "hang";} }
JAVA
