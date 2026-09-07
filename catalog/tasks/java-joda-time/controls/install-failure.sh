#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/joda/time/format
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>bad</artifactId><version>1</version><dependencies><dependency><groupId>x</groupId><artifactId>y</artifactId><version>1</version></dependency></dependencies></project>' > pom.xml
printf '%s\n' 'package org.joda.time.format; public final class FormatUtils {}' > src/main/java/org/joda/time/format/FormatUtils.java
