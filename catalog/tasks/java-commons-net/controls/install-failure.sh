#!/usr/bin/env bash
set -euo pipefail
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>invalid</artifactId><version>1.0.0</version><build><plugins><plugin/></plugins></build></project>
XML
