## Project Description

Create a small Java Maven project that recreates the bounded, deterministic IPv4
calculation API of Apache Commons Net's `SubnetUtils`. The project is a pure
standard-library exercise. It must not implement FTP, NNTP, NTP, WHOIS, finger,
socket factories, DNS lookups, or any other network protocol class.

The required public type is `org.apache.commons.net.util.SubnetUtils`. It models
an IPv4 address together with a contiguous IPv4 netmask. Its `getInfo()` method
returns a public `SubnetInfo` view containing scalar address summaries, range
membership checks, and deterministic address traversal operations.

Implement the exact package and public names described in this document under a
standard Maven source tree. Candidate code must compile with Temurin JDK
21.0.12+8. The candidate `pom.xml` is metadata only and must not add runtime
dependencies, repositories, plugins, profiles, modules, build extensions, or
network-dependent commands.

All behavior is local and deterministic. Repeated calls with the same object
state and arguments must produce the same values and ordering. The verifier
will exercise the public contract through a separate Java process; do not add a
test-only API or a verifier-specific entry point.

### Natural Language Instruction (Prompt)

Implement the Java Maven project described here from an empty `workspace/`.
Create the exact `SubnetUtils` and `SubnetInfo` API, keep the implementation
under `src/main/java`, and satisfy the documented IPv4 calculations,
validation, navigation, membership, and traversal behavior. The result must
build offline with JDK 21 and must not depend on network services or third-party
runtime libraries.

## Supports

### Runtime and dependency contract

Use the following environment assumptions:

```text
Java: Temurin 21.0.12+8
Maven: 3.9.11
Platform: Linux amd64, glibc
Runtime dependencies: none; Java SE classes only
Execution network: disabled for agent, candidate, verifier, Oracle, and controls
```

The project may use Java SE types such as `java.util.Iterator`, regular
expression classes, and sequential `java.util.stream.Stream`. Do not download
artifacts at build or run time. A minimal metadata-only `pom.xml` is sufficient.

### Project directory structure

Use this layout, with `workspace/` as the project root:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── net/
                            └── util/
                                └── SubnetUtils.java
```

`SubnetInfo` is the public non-static inner class returned by
`SubnetUtils.getInfo()`. It may be declared in the same source file as the
outer class. No socket, DNS, configuration file, external process, or external
data file is required.

### Supported behavior

Support dotted-decimal IPv4 parsing, CIDR prefix notation, contiguous dotted
netmasks, network and broadcast calculation, usable-host ranges, inclusive
host-count mode, packed integer conversion, navigation to adjacent subnets,
range membership, eager address arrays, lazy iterables, and sequential streams.

The default host mode excludes the network and broadcast endpoints. Inclusive
mode includes both endpoints. Very large ranges must be representable through
the long count method and lazy traversal without requiring an eager array.

### Error and side-effect policy

Reject malformed addresses, invalid octets, invalid CIDR prefixes, and
non-contiguous masks with `IllegalArgumentException`. If a valid address count
cannot fit in a Java `int`, `getAddressCount()` must throw
`IllegalStateException`. Do not silently repair malformed input, return null
for a valid scalar operation, print diagnostics, access the network, or mutate
global state.

## API Usage Guide

Import the outer type with:

```java
import org.apache.commons.net.util.SubnetUtils;
```

The following are the complete confidently bindable public APIs from the task
inventory. Do not add public types or methods outside this surface.

### `org.apache.commons.net.util.SubnetUtils(String)`

Signature:

```java
public SubnetUtils(String cidrNotation)
```

The argument is an IPv4 dotted-decimal address followed by `/` and a prefix
length from 0 through 32, such as `10.0.0.7/29`. Construction stores the
configured address and derives a network and broadcast address using the mask.
It has no external side effect and is deterministic. A malformed address,
missing separator, non-decimal prefix, or prefix outside 0 through 32 throws
`IllegalArgumentException`.

Normal example: `new SubnetUtils("192.168.0.1/29")` creates a range with
network `192.168.0.0` and broadcast `192.168.0.7`. Edge example:
`new SubnetUtils("0.0.0.0/0")` is valid and represents the complete IPv4
address space; malformed input such as `"192.168.1.1/33"` is rejected.

### `org.apache.commons.net.util.SubnetUtils(String, String)`

Signature:

```java
public SubnetUtils(String address, String mask)
```

Both arguments are dotted-decimal IPv4 strings. The mask must be contiguous,
with all one bits preceding all zero bits. The supplied address is retained for
the information view while network and broadcast values are derived from the
mask. Construction is local and deterministic. Invalid octets, malformed
strings, or a non-contiguous mask throw `IllegalArgumentException`.

Normal example: `new SubnetUtils("192.168.0.1", "255.255.255.248")` describes
the same `/29` as the CIDR example. Edge example: `new SubnetUtils("10.0.0.1",
"255.255.255.254")` is valid; `"255.0.255.0"` must be rejected.

### `SubnetUtils.getInfo()`

Signature:

```java
public final SubnetInfo getInfo()
```

Return the public non-static inner `SubnetInfo` view for the current subnet.
The view reflects the owning object's current inclusive-host flag, and calling
this method does not perform I/O or change the subnet. Normal example:
`SubnetUtils.SubnetInfo info = subnet.getInfo()`. Edge example: obtain a new
view after `setInclusiveHostCount(true)` and observe the changed endpoints and
count.

### `SubnetUtils.isInclusiveHostCount()`

Signature:

```java
public boolean isInclusiveHostCount()
```

Return whether network and broadcast addresses are included in range counts,
membership, and traversal. The default is `false`; the method has no side
effect. Normal example: a new `/29` reports `false`. Edge example: a `/32`
reports zero usable addresses while this flag is false.

### `SubnetUtils.setInclusiveHostCount(boolean)`

Signature:

```java
public void setInclusiveHostCount(boolean inclusiveHostCount)
```

Set the per-instance inclusion mode. The argument is any boolean and the
method returns no value. It changes only this `SubnetUtils` instance and does
not perform I/O. Normal example: `subnet.setInclusiveHostCount(true)` makes a
`/29` count eight addresses. Edge example: setting `false` again restores the
default six-address usable range for that `/29`.

### `SubnetUtils.getNext()`

Signature:

```java
public SubnetUtils getNext()
```

Return an independent `SubnetUtils` using the same mask and the next subnet
address relative to the configured subnet address. The original object is not
mutated. The returned object's inclusive flag is independent and defaults to
the normal non-inclusive mode. Normal example: navigating from
`192.168.0.1/29` yields the next `/29` address block. Edge example: navigation
near the upper IPv4 boundary must remain deterministic and must not access a
network service.

### `SubnetUtils.getPrevious()`

Signature:

```java
public SubnetUtils getPrevious()
```

Return an independent object for the preceding subnet address with the same
mask. The original object is not mutated and no external side effect occurs.
Normal example: `new SubnetUtils("192.168.0.9/29").getPrevious()` navigates to
the preceding `/29` block. Edge example: navigating from a low-boundary subnet
must remain a valid deterministic calculation rather than performing I/O.

### `SubnetUtils.toString()`

Signature:

```java
public String toString()
```

Return a stable diagnostic representation of the configured subnet. It must be
deterministic for the same state and must not access the network or mutate the
object. Normal example: calling it twice on an unchanged `/29` returns equal
strings. Edge example: its result may change after the inclusive flag changes,
but it must still be a non-null string.

### `SubnetUtils.SubnetInfo.getAddress()`

Signature:

```java
public String getAddress()
```

Return the configured IPv4 address in canonical dotted-decimal form. This is
the supplied address, not necessarily the normalized network address. Normal
example: a subnet configured with `192.168.0.1/29` returns `192.168.0.1`.
Edge example: leading-zero or non-canonical input must not produce malformed
output; invalid input was rejected by the constructor.

### `SubnetUtils.SubnetInfo.getNetmask()`

Signature:

```java
public String getNetmask()
```

Return the contiguous mask as canonical dotted-decimal text. The result is
stable and has no side effect. Normal example: a `/29` returns
`255.255.255.248`. Edge example: `/0` returns `0.0.0.0` and `/32` returns
`255.255.255.255`.

### `SubnetUtils.SubnetInfo.getNetworkAddress()`

Signature:

```java
public String getNetworkAddress()
```

Return the lowest address obtained by applying the mask to the configured
address. The result is canonical dotted decimal and deterministic. Normal
example: `192.168.0.1/29` returns `192.168.0.0`. Edge example: a `/32` has a
network address equal to its configured address.

### `SubnetUtils.SubnetInfo.getBroadcastAddress()`

Signature:

```java
public String getBroadcastAddress()
```

Return the highest address in the subnet as canonical dotted decimal. Normal
example: `192.168.0.1/29` returns `192.168.0.7`. Edge example: `/0` returns
`255.255.255.255`.

### `SubnetUtils.SubnetInfo.getLowAddress()`

Signature:

```java
public String getLowAddress()
```

Return the first address included by the current host-count mode. In default
mode it is the address after network; in inclusive mode it is network. Normal
example: a `/29` returns `192.168.0.1` by default. Edge example: a `/31` in
default mode has an empty usable range and must use a consistent boundary
representation; inclusive mode starts at its network address.

### `SubnetUtils.SubnetInfo.getHighAddress()`

Signature:

```java
public String getHighAddress()
```

Return the last address included by the current host-count mode. In default
mode it is before broadcast; in inclusive mode it is broadcast. Normal
example: a `/29` returns `192.168.0.6` by default. Edge example: inclusive
`/31` includes both addresses while default `/32` has no usable hosts.

### `SubnetUtils.SubnetInfo.getNextAddress()`

Signature:

```java
public String getNextAddress()
```

Return the address immediately after the configured address in the subnet's
address arithmetic. The result is canonical and deterministic. Normal example:
for configured `192.168.0.1`, return `192.168.0.2`. Edge example: the method
must retain stable IPv4 boundary behavior and must not perform I/O.

### `SubnetUtils.SubnetInfo.getPreviousAddress()`

Signature:

```java
public String getPreviousAddress()
```

Return the address immediately before the configured address in the subnet's
address arithmetic. Normal example: for configured `192.168.0.1`, return
`192.168.0.0`. Edge example: a low-boundary address must be handled
deterministically without signed-integer ordering mistakes.

### `SubnetUtils.SubnetInfo.getCidrSignature()`

Signature:

```java
public String getCidrSignature()
```

Return the configured address followed by `/` and the number of one bits in
the mask. Preserve the configured address rather than replacing it with the
network address. Normal example: `192.168.0.1/29` returns that same signature.
Edge example: a mask of `0.0.0.0` produces a `/0` suffix.

### `SubnetUtils.SubnetInfo.getAddressCountLong()`

Signature:

```java
public long getAddressCountLong()
```

Return the number of addresses included by the current mode. Default mode is
`broadcast - network - 1`, clamped to zero; inclusive mode is
`broadcast - network + 1`. Normal example: a `/29` returns `6` by default and
`8` when inclusive. Edge example: `/0` must return its large valid count as a
`long` without allocating an array.

### `SubnetUtils.SubnetInfo.getAddressCount()`

Signature:

```java
public int getAddressCount()
```

Return the same count as an `int` when representable. If the valid long count
is greater than `Integer.MAX_VALUE`, throw `IllegalStateException` rather than
overflowing or silently truncating. Normal example: a `/29` returns `6`.
Edge example: default `/0` cannot fit and must raise the documented exception.

### `SubnetUtils.SubnetInfo.asInteger(String)`

Signature:

```java
public int asInteger(String address)
```

Parse a dotted IPv4 address and pack its four octets in network order into a
signed Java `int`. The bit pattern, not signed numeric ordering, represents the
address. Normal example: `asInteger("192.168.0.1")` returns the packed bit
pattern for that address. Edge example: `255.255.255.255` is a valid packed
value even though its signed `int` value is negative; malformed text throws
`IllegalArgumentException`.

### `SubnetUtils.SubnetInfo.isInRange(String)`

Signature:

```java
public boolean isInRange(String address)
```

Parse the dotted IPv4 argument and report whether it lies in the current
subnet and current inclusive-host range. Default mode excludes network and
broadcast; inclusive mode includes them. Normal example: a `/29` reports true
for `192.168.0.3`. Edge example: the same subnet reports false for
`192.168.0.0` by default and true after enabling inclusive mode. Malformed text
throws `IllegalArgumentException`.

### `SubnetUtils.SubnetInfo.isInRange(int)`

Signature:

```java
public boolean isInRange(int address)
```

Interpret the signed argument as a packed 32-bit IPv4 address and apply the
same subnet and inclusive-host range rules as the string overload. The method
is deterministic and side-effect free. Normal example: pass the result of
`asInteger("192.168.0.3")`. Edge example: a negative packed value must still
be compared as an unsigned IPv4 bit pattern, not rejected because it is
negative.

### `SubnetUtils.SubnetInfo.getAllAddresses()`

Signature:

```java
public String[] getAllAddresses()
```

Eagerly return every address in the current range as canonical dotted-decimal
strings in ascending unsigned IPv4 order. Repeated calls are deterministic;
the returned array is independent. Normal example: a default `/30` returns its
two usable addresses in order. Edge example: an empty default `/31` or `/32`
returns a zero-length array, and callers should use lazy APIs for very large
ranges.

### `SubnetUtils.SubnetInfo.iterableAddressStrings()`

Signature:

```java
public Iterable<String> iterableAddressStrings()
```

Return a lazy iterable over the current range in ascending unsigned IPv4 order.
Iteration is deterministic and does not require eager materialization. The
iterable must reflect the `SubnetInfo` state used to create it and must not
perform I/O. Normal example: use it in a for-each loop over a `/29`. Edge
example: an empty usable range produces no elements.

### `SubnetUtils.SubnetInfo.streamAddressStrings()`

Signature:

```java
public java.util.stream.Stream<String> streamAddressStrings()
```

Return a lazy sequential stream of canonical addresses in ascending unsigned
IPv4 order. The stream is deterministic and suitable for counting or bounded
consumption. Normal example: `info.streamAddressStrings().count()` equals
`getAddressCountLong()`. Edge example: an empty range yields a stream with no
elements; a caller must close or fully consume the stream according to normal
Java stream ownership rules.

### Public API boundary

The inventory confidently binds only `SubnetUtils` and its `SubnetInfo` public
methods listed above. No other Commons Net class, protocol client, CLI, or
public entry point is confidently bindable for this task, so none is required.

## Implementation Notes

Use a single-module Maven project and keep all candidate code under
`src/main/java`. The implementation must compile with `javac --release 21` and
with Maven offline. The verifier owns its process contract and reports; the
candidate must not write verifier-owned grading, JUnit, collection, or reward
files.

Treat IPv4 values as four unsigned octets even when an internal packed value is
a signed Java `int`. Preserve the configured address separately from the
normalized network address so `getAddress()` and `getCidrSignature()` retain
the caller's address. Keep inclusive-host state per `SubnetUtils` instance and
avoid global mutable state.

The following small examples must be made possible by the public contract:

1. `new SubnetUtils("192.168.0.1/29").getInfo()` reports network
   `192.168.0.0`, broadcast `192.168.0.7`, and default count `6`.
2. Enabling inclusive mode for that object changes the count to `8`, includes
   both endpoints, and leaves a separately created object non-inclusive.
3. `new SubnetUtils("192.168.0.1", "255.255.255.248")` has the same mask and
   range as the CIDR form.
4. A `/31` has zero default usable addresses and two inclusive addresses, while
   a `/32` has one inclusive address.

Keep address collection order ascending and stable across calls. Use the long
count API and lazy iterable/stream APIs for large ranges. Reject invalid text
early with `IllegalArgumentException`; do not silently normalize malformed
octets or masks. Do not copy an upstream implementation, expose private test
names, describe verifier assertions, add a source download endpoint, or give a
step-by-step algorithm that bypasses the requested engineering work.
