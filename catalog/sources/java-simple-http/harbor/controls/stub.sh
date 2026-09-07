#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/de/svenkubiak/http /workspace/src/main/java/de/svenkubiak/utils
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>stub</artifactId><version>1</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/de/svenkubiak/http/Result.java <<'JAVA'
package de.svenkubiak.http; public class Result { private String body=""; private int status=-1; public static Result create(){return new Result();} public Result withBody(String v){body="stub";return this;} public Result withBinaryBody(byte[] v){return this;} public Result withStatus(int v){status=0;return this;} public Result withHeader(String k,String v){return this;} public String body(){return body;} public byte[] binaryBody(){return new byte[0];} public String header(String k){return "stub";} public String error(){return body;} public int status(){return status;} public boolean isValid(){return true;} public boolean isValid(int... v){return true;} }
JAVA
cat > /workspace/src/main/java/de/svenkubiak/utils/Utils.java <<'JAVA'
package de.svenkubiak.utils; public final class Utils { private Utils(){} public static boolean isSuccessCode(int v){return true;} public static String getFormDataAsString(java.util.Map<String,String> v){return "stub";} public static String clean(String v){return "stub";} public static java.net.URI toAllowedUri(String v)throws java.net.URISyntaxException{return java.net.URI.create("http://stub");} }
JAVA
