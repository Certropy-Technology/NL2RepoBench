#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>bad</artifactId><version>1</version><build><plugins><plugin><groupId>x</groupId><artifactId>forbidden</artifactId><version>1</version></plugin></plugins></build></project>
XML
