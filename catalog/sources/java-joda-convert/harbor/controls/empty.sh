#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/joda/convert
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>empty</artifactId><version>1</version></project>' > /workspace/pom.xml
