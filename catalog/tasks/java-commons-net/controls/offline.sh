#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/net/util
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/net/util/SubnetUtils.java <<'JAVA'
package org.apache.commons.net.util;
import java.util.*; import java.util.stream.*;
public class SubnetUtils {
 private final int address,mask,network,broadcast; private boolean inclusive;
 public SubnetUtils(String cidr){String[] p=cidr.split("/",-1);if(p.length!=2)throw new IllegalArgumentException();address=ip(p[0]);int bits=Integer.parseInt(p[1]);if(bits<0||bits>32)throw new IllegalArgumentException();mask=bits==0?0:-1<<(32-bits);network=address&mask;broadcast=network|~mask;}
 public SubnetUtils(String a,String m){address=ip(a);mask=ip(m);if((mask&-mask)-1!=~mask)throw new IllegalArgumentException();network=address&mask;broadcast=network|~mask;}
 public final SubnetInfo getInfo(){return new SubnetInfo();} public SubnetUtils getNext(){return new SubnetUtils(getInfo().getNextAddress(),getInfo().getNetmask());} public SubnetUtils getPrevious(){return new SubnetUtils(getInfo().getPreviousAddress(),getInfo().getNetmask());}
 public boolean isInclusiveHostCount(){return inclusive;} public void setInclusiveHostCount(boolean v){inclusive=v;} public String toString(){return getInfo().toString();}
 private static int ip(String s){String[] p=s.split("\\.",-1);if(p.length!=4)throw new IllegalArgumentException();int r=0;for(String x:p){int n=Integer.parseInt(x);if(n<0||n>255||!x.matches("\\d{1,3}"))throw new IllegalArgumentException();r=r<<8|n;}return r;}
 private static String fmt(int v){return ((v>>>24)&255)+"."+((v>>>16)&255)+"."+((v>>>8)&255)+"."+(v&255);}
 public final class SubnetInfo {
  private long u(int v){return v&0xffffffffL;} private int low(){return inclusive?network:(u(broadcast)-u(network)>1?network+1:0);} private int high(){return inclusive?broadcast:(u(broadcast)-u(network)>1?broadcast-1:0);}
  public String getAddress(){return fmt(address);} public String getNetmask(){return fmt(mask);} public String getNetworkAddress(){return fmt(network);} public String getBroadcastAddress(){return fmt(broadcast);} public String getLowAddress(){return fmt(low());} public String getHighAddress(){return fmt(high());} public String getNextAddress(){return fmt(address+1);} public String getPreviousAddress(){return fmt(address-1);} public String getCidrSignature(){return fmt(address)+"/"+Integer.bitCount(mask);}
  public long getAddressCountLong(){long c=u(broadcast)-u(network)+(inclusive?1:-1);return Math.max(0,c);} public int getAddressCount(){long c=getAddressCountLong();if(c>Integer.MAX_VALUE)throw new IllegalStateException();return (int)c;} public int asInteger(String v){return ip(v);}
  public boolean isInRange(String v){return isInRange(ip(v));} public boolean isInRange(int v){if(v==0)return false;return u(v)>=u(low())&&u(v)<=u(high());}
  public String[] getAllAddresses(){String[] r=new String[getAddressCount()];for(int i=0;i<r.length;i++)r[i]=fmt(low()+i);return r;} public Iterable<String> iterableAddressStrings(){return Arrays.asList(getAllAddresses());} public Stream<String> streamAddressStrings(){return Arrays.stream(getAllAddresses());} public String toString(){return "CIDR Signature:\t["+getCidrSignature()+"]";}
 }
}
JAVA
