#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/jsoup/nodes
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>bad</artifactId><version>1</version><build><plugins><plugin><artifactId>maven-antrun-plugin</artifactId></plugin></plugins></build></project>
POM
printf '%s\n' 'package org.jsoup.nodes; public class Attribute {}' > /workspace/src/main/java/org/jsoup/nodes/Attribute.java
