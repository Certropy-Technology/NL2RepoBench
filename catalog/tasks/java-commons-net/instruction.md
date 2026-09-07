# Introduction and Goals of the Apache Commons Net Project

Apache Commons Net provides protocol and network utility classes. This task
recreates a bounded, deterministic part of that library: the IPv4 CIDR
calculation API in `org.apache.commons.net.util.SubnetUtils`. The requested
project is a normal Java Maven project created from an empty workspace. Do not
implement network clients or make network connections; only the described
in-memory subnet calculations are in scope.

## Natural Language Instruction (Prompt)

Create a Java Maven project that provides the public API described below. The
implementation must be placed under `src/main/java` and must compile on
Temurin JDK 21.0.12+8. Use the exact package and public type names. The project
must have a metadata-only `pom.xml` and no runtime dependency outside the Java
standard library.

The central type is `org.apache.commons.net.util.SubnetUtils`. It represents an
IPv4 address and a contiguous IPv4 network mask. A `SubnetUtils` object exposes
its calculated values through a `SubnetInfo` object returned by `getInfo()`.
All calculations are deterministic and in memory. The default mode excludes a
network address and a broadcast address from the usable-host range; callers
can switch to inclusive mode with `setInclusiveHostCount(true)`.

## Environment Configuration

### Core Dependency Library Versions

```text
Java: Temurin 21.0.12+8
Maven: 3.9.11
Platform: Linux amd64, glibc
Runtime dependencies: none; Java SE classes only
Agent, candidate, verifier, Oracle, and control execution: no network
```

The candidate `pom.xml` is metadata only. Do not use it to add dependencies,
plugins, profiles, repositories, modules, build extensions, or test commands.
The verifier supplies the fixed execution contract independently of the
candidate project.

## Apache Commons Net Project Architecture

### Project Directory Structure

Use a standard single-module Maven layout:

```text
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/net/util/SubnetUtils.java
```

`SubnetInfo` is the public non-static inner class exposed by
`SubnetUtils.getInfo()`. It may be implemented in the same source file as the
outer class. No network socket, DNS lookup, server, or external data file is
needed.

## API Usage Guide

### Core APIs

#### Constructing a subnet

```java
SubnetUtils byCidr = new SubnetUtils("192.168.0.1/29");
SubnetUtils byMask = new SubnetUtils("192.168.0.1", "255.255.255.248");
SubnetUtils.SubnetInfo info = byCidr.getInfo();
```

Exact signatures:

```java
public SubnetUtils(String cidrNotation)
public SubnetUtils(String address, String mask)
public final SubnetInfo getInfo()
```

The CIDR form accepts an IPv4 dotted-decimal address followed by `/` and a
prefix length from 0 through 32, such as `10.0.0.1/24`. The address/mask form
accepts two dotted-decimal IPv4 strings and requires a contiguous netmask.
Both constructors normalize the network address using the mask but preserve
the supplied address for `SubnetInfo.getAddress()`.

Malformed addresses, octets outside 0 through 255, prefix lengths outside
0 through 32, or non-contiguous masks throw `IllegalArgumentException`.
There is no network access and construction has no external side effect.

#### Subnet state and navigation

```java
boolean inclusive = subnet.isInclusiveHostCount();
subnet.setInclusiveHostCount(true);
SubnetUtils next = subnet.getNext();
SubnetUtils previous = subnet.getPrevious();
```

Exact signatures:

```java
public boolean isInclusiveHostCount()
public void setInclusiveHostCount(boolean inclusiveHostCount)
public SubnetUtils getNext()
public SubnetUtils getPrevious()
public String toString()
```

New instances returned by `getNext()` and `getPrevious()` use the same
netmask and the next or previous address relative to the current subnet
address. The inclusive-host flag belongs to each instance and defaults to
`false`; navigation does not mutate the original object.

#### SubnetInfo scalar accessors

```java
String network = info.getNetworkAddress();
String broadcast = info.getBroadcastAddress();
String first = info.getLowAddress();
String last = info.getHighAddress();
long count = info.getAddressCountLong();
String cidr = info.getCidrSignature();
```

Exact signatures:

```java
public String getAddress()
public String getNetmask()
public String getNetworkAddress()
public String getBroadcastAddress()
public String getLowAddress()
public String getHighAddress()
public String getNextAddress()
public String getPreviousAddress()
public String getCidrSignature()
public long getAddressCountLong()
public int getAddressCount()
public int asInteger(String address)
```

Every address result uses canonical dotted-decimal form with four decimal
octets. `getCidrSignature()` preserves the configured address followed by `/`
and the number of one bits in the mask; it does not replace that address with
the normalized network address. `getAddressCountLong()` counts usable
addresses by default (`broadcast - network - 1`, clamped to zero) and counts
all addresses in inclusive mode (`broadcast - network + 1`). For `/0` and other
large ranges, use the long-returning method rather than materializing an array.

`getAddressCount()` returns the same count as an `int`; if the long count is
larger than `Integer.MAX_VALUE`, it throws `IllegalStateException`. For a
`/31` or `/32` subnet in default mode, the count and the address collection
are zero-length. In inclusive mode those ranges contain two and one address,
respectively. `asInteger(String)` packs the four octets in network order into
the signed Java `int`; for example `192.168.0.1` returns `-1062731775`.

#### Range membership

```java
boolean inside = info.isInRange("192.168.0.3");
boolean insidePacked = info.isInRange(info.asInteger("192.168.0.3"));
```

Exact signatures:

```java
public boolean isInRange(String address)
public boolean isInRange(int address)
```

String input is parsed as dotted IPv4 and malformed input throws
`IllegalArgumentException`. Integer input is interpreted as the packed
32-bit address. Membership uses the current inclusive flag: network and
broadcast addresses are excluded by default and included when the flag is
true. The special packed value zero is never treated as a usable address in
the default host-count mode.

#### Address collections and streams

```java
String[] addresses = info.getAllAddresses();
Iterable<String> iterable = info.iterableAddressStrings();
long number = info.streamAddressStrings().count();
```

Exact signatures:

```java
public String[] getAllAddresses()
public Iterable<String> iterableAddressStrings()
public java.util.stream.Stream<String> streamAddressStrings()
```

Addresses are emitted in ascending unsigned IPv4 order, from the low address
through the high address, and are deterministic across repeated calls. The
array eagerly contains every address and can be large; the iterable and stream
are lazy alternatives. The stream is sequential. Empty usable ranges produce
an empty array, iterable, and stream.

### Actual Usage Modes

Typical usage creates a `/29`, inspects its six default usable addresses, then
creates an inclusive view when the network and broadcast endpoints are also
needed:

```java
SubnetUtils subnet = new SubnetUtils("192.168.0.1/29");
SubnetUtils.SubnetInfo info = subnet.getInfo();
// network 192.168.0.0, broadcast 192.168.0.7,
// low 192.168.0.1, high 192.168.0.6, count 6
for (String address : info.iterableAddressStrings()) {
    System.out.println(address);
}
subnet.setInclusiveHostCount(true);
// count is now 8 and low/high are 192.168.0.0/192.168.0.7
```

### Supported Function Types

The required implementation is a pure IPv4 value/calculation utility:

- dotted-decimal parsing and validation;
- CIDR prefix and contiguous-mask conversion;
- packed integer conversion and unsigned range arithmetic;
- deterministic scalar summaries;
- bounded eager and lazy address traversal;
- per-instance inclusive-host state.

Do not implement FTP, NNTP, NTP, WHOIS, finger, socket factories, or any
other Commons Net protocol class for this task.

### Error Handling

Use `IllegalArgumentException` for invalid textual addresses, invalid CIDR
prefixes, and non-contiguous masks. Use `IllegalStateException` only when
`getAddressCount()` cannot represent the valid long count as an `int`. Do not
silently clamp malformed inputs, perform network retries, print diagnostics to
standard output, or return null for a valid scalar operation.

## Detailed Implementation Nodes of Functions

1. Parse each IPv4 octet as a decimal integer and reject malformed or
   out-of-range input. Pack octets in big-endian/network order and format
   packed values back as unsigned four-octet dotted strings.
2. For CIDR input, create a 32-bit contiguous mask from the prefix length;
   derive network with bitwise AND and broadcast with network OR complement.
   For dotted masks, validate contiguity before deriving the same values.
3. Keep the original packed address, network, broadcast, netmask, and
   inclusive flag as instance state. `getInfo()` exposes a view of that state,
   while the view's methods remain deterministic and side-effect free.
4. Compute low/high and counts according to the inclusive flag, using unsigned
   arithmetic so ranges crossing the signed Java `int` boundary remain correct.
5. Generate collection and stream values in ascending address order. Do not
   allocate a huge array when an iterable or stream is requested.
6. `getNext()` and `getPrevious()` construct independent objects with the
   current netmask. `toString()` should be a stable diagnostic summary and
   must not access the network.

The ten positive verifier behaviors are `cidr-summary`, `default-range`,
`inclusive-range`, `mask-constructor`, `large-count`, `invalid-input`,
`address-array`, `address-stream`, `navigation`, and `packed-integer`.
Each is directly described above; the frozen denominator is 10 and every
leaf must be collected even if another leaf fails.
