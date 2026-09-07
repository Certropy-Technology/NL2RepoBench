#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>broken</artifactId><version>1.0.0</version><build><plugins><plugin/></plugins></build></project>' > pom.xml
