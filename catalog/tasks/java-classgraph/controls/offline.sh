#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/io/github/classgraph/viz
cat > /workspace/src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java <<'JAVA'
package io.github.classgraph.viz;
public final class GraphVizDotFileOptions {
 float sizeX=10.5f,sizeY=8f; boolean showFields=true,showFieldTypeDependencyEdges=true,showMethods=true,showMethodTypeDependencyEdges=true,showAnnotations=true,showAnnotationDependencyEdges=true,useSimpleNames=true; Boolean includeExternalClasses;
 public GraphVizDotFileOptions(){} public GraphVizDotFileOptions setLayoutSize(float x,float y){sizeX=x;sizeY=y;return this;}
 public GraphVizDotFileOptions showFields(){showFields=true;return this;} public GraphVizDotFileOptions hideFields(){showFields=false;return this;}
 public GraphVizDotFileOptions showFieldTypeDependencyEdges(){showFieldTypeDependencyEdges=true;return this;} public GraphVizDotFileOptions hideFieldTypeDependencyEdges(){showFieldTypeDependencyEdges=false;return this;}
 public GraphVizDotFileOptions showMethods(){showMethods=true;return this;} public GraphVizDotFileOptions hideMethods(){showMethods=false;return this;}
 public GraphVizDotFileOptions showMethodTypeDependencyEdges(){showMethodTypeDependencyEdges=true;return this;} public GraphVizDotFileOptions hideMethodTypeDependencyEdges(){showMethodTypeDependencyEdges=false;return this;}
 public GraphVizDotFileOptions showAnnotations(){showAnnotations=true;return this;} public GraphVizDotFileOptions hideAnnotations(){showAnnotations=false;return this;}
 public GraphVizDotFileOptions showAnnotationDependencyEdges(){showAnnotationDependencyEdges=true;return this;} public GraphVizDotFileOptions hideAnnotationDependencyEdges(){showAnnotationDependencyEdges=false;return this;}
 public GraphVizDotFileOptions useSimpleNames(){useSimpleNames=true;return this;} public GraphVizDotFileOptions useFullyQualifiedNames(){useSimpleNames=false;return this;}
 public GraphVizDotFileOptions includeExternalClasses(){includeExternalClasses=true;return this;} public GraphVizDotFileOptions excludeExternalClasses(){includeExternalClasses=false;return this;}
}
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>offline</artifactId><version>1</version></project>
POM
