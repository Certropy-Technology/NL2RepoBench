#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/net/util
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/net/util/SubnetUtils.java <<'JAVA'
package org.apache.commons.net.util;
import java.util.stream.Stream;
public class SubnetUtils {
  public SubnetUtils(String value) {} public SubnetUtils(String address,String mask) {}
  public final SubnetInfo getInfo(){return new SubnetInfo();} public SubnetUtils getNext(){return this;} public SubnetUtils getPrevious(){return this;}
  public boolean isInclusiveHostCount(){return false;} public void setInclusiveHostCount(boolean value){} public String toString(){return "";}
  public final class SubnetInfo {
    public String getAddress(){return "";} public String getNetmask(){return "";} public String getNetworkAddress(){return "";} public String getBroadcastAddress(){return "";}
    public String getLowAddress(){return "";} public String getHighAddress(){return "";} public String getNextAddress(){return "";} public String getPreviousAddress(){return "";} public String getCidrSignature(){return "";}
    public long getAddressCountLong(){return 0;} public int getAddressCount(){return 0;} public int asInteger(String value){return 0;}
    public boolean isInRange(String value){return false;} public boolean isInRange(int value){return false;} public String[] getAllAddresses(){return new String[0];}
    public Iterable<String> iterableAddressStrings(){return java.util.List.of();} public Stream<String> streamAddressStrings(){return Stream.empty();}
  }
}
JAVA
