#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/de/svenkubiak/http /workspace/src/main/java/de/svenkubiak/utils
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>hang</artifactId><version>1</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/de/svenkubiak/http/Result.java <<'JAVA'
package de.svenkubiak.http; public class Result { private static void hang(){for(;;)Thread.onSpinWait();} public static Result create(){hang();return null;} public Result withBody(String v){return this;} public Result withBinaryBody(byte[] v){return this;} public Result withStatus(int v){return this;} public Result withHeader(String k,String v){return this;} public String body(){return "";} public byte[] binaryBody(){return null;} public String header(String k){return null;} public String error(){return "";} public int status(){return -1;} public boolean isValid(){return false;} public boolean isValid(int... v){return false;} }
JAVA
cat > /workspace/src/main/java/de/svenkubiak/utils/Utils.java <<'JAVA'
package de.svenkubiak.utils; public final class Utils { private Utils(){} public static boolean isSuccessCode(int v){return false;} public static String getFormDataAsString(java.util.Map<String,String> v){return "";} public static String clean(String v){return v;} public static java.net.URI toAllowedUri(String v)throws java.net.URISyntaxException{return new java.net.URI(v);} }
JAVA
