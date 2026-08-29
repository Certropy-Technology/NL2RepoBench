# Build `ip-address`

## Project Description

Create an installable npm package named `ip-address` from an empty workspace. It
parses and manipulates IPv4 and IPv6 addresses, CIDR networks, subnet masks,
wildcard masks, and selected IPv4-in-IPv6 forms. The package must be usable from
CommonJS on Node 24 and must expose the same root API shape as the pinned
release. Implement the behavior described below without copying upstream source
or tests.

## Supports

- Node `24.19.0` and npm `11.17.0` on Linux amd64.
- A CommonJS package: `require('ip-address')` must return the named exports
  `Address4`, `Address6`, `AddressError`, and `v6`.
- No runtime dependencies, lifecycle hooks, native addons, network access, or
  browser-only APIs.
- A v3 `package-lock.json` whose root package agrees with `package.json`.
- The verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund`
  before packing and loading your package. Keep the implementation under the
  package files selected by the package metadata.

## API Usage Guide

### Shared address behavior

`Address4` and `Address6` are classes. Constructors accept an address string,
optionally followed by `/prefix`. Host bits may be set in a CIDR input. Invalid
input throws `AddressError`, whose `name` is `AddressError` and whose `message`
describes the problem. `Address4.isValid(value)` and `Address6.isValid(value)`
return booleans and never throw for invalid strings.

Each instance exposes `address`, `addressMinusSuffix`, `parsedAddress`,
`parsedSubnet`, `subnet`, `subnetMask`, `groups`, and `v4` as applicable. IPv6
instances also expose `zone` for a `%zone` identifier and may expose
`address4`/`parsedAddress4` for dotted-quad input. Preserve the distinction
between an omitted prefix and an explicitly supplied default prefix in
`isCorrect()`.

### `Address4`

Import with `const {Address4} = require('ip-address')`.

- `new Address4(address: string): Address4` parses four decimal octets with an
  optional prefix from 0 through 32. Decimal octets are 0 through 255 and
  leading-zero octets are invalid.
- `correctForm(): string` returns normalized dotted decimal. `isCorrect()`
  reports whether the input spelling and prefix were already canonical.
- `static isValid(address: string): boolean` validates without throwing.
- `static fromInteger(value: number): Address4` accepts an integer from 0
  through `2**32 - 1`. `static fromBigInt(value: bigint): Address4` accepts the
  same range. `static fromHex(value: string): Address4` accepts exactly eight
  hexadecimal digits, with optional `:` separators. `static fromArpa(value)`
  accepts reverse `in-addr.arpa` notation.
- `static fromByteArray(bytes: number[]): Address4` and
  `static fromUnsignedByteArray(bytes: number[]): Address4` require exactly
  four integer bytes from 0 through 255.
- `static fromAddressAndMask(address, mask)` accepts a dotted contiguous mask;
  `static fromAddressAndWildcardMask(address, wildcardMask)` accepts its
  bitwise-inverse Cisco wildcard form. Non-contiguous masks throw.
- `static fromWildcard(pattern)` accepts four octets where any `*` values are
  trailing whole-octet wildcards and converts their count to a prefix.
- `toHex(): string` returns four two-digit groups separated by colons;
  `toArray(): number[]` returns four unsigned octets;
  `toGroup6(): string` returns two four-digit IPv6 groups; and `bigInt(): bigint`
  returns the numeric address.
- `startAddress()`, `startAddressExclusive()`, `endAddress()`, and
  `endAddressExclusive()` return `Address4` objects for the CIDR range.
  `subnetMaskAddress()` and `wildcardMask()` return `Address4` objects.
  `networkForm()` returns the network address plus `/prefix`.
  `mask(prefix?: number): string` returns a binary mask string.
  `reverseForm(options?: {omitSuffix?: boolean}): string` returns reverse DNS
  notation, with `.in-addr.arpa` omitted only when requested.
- `isInSubnet(other)` tests network containment and respects both prefixes;
  `isHostInSubnet(other)` tests only whether this host falls in `other`.
  `isPrivate`, `isLoopback`, `isLinkLocal`, `isUnspecified`, `isBroadcast`,
  `isMulticast`, and `isCGNAT` classify the host independent of its own CIDR
  suffix. `binaryZeroPad()` returns 32 bits and `groupForV6()` returns the
  four-hex-digit trailing group.

### `Address6`

Import with `const {Address6} = require('ip-address')`.

- `new Address6(address: string, optionalGroups?: number): Address6` parses
  eight hexadecimal groups, a single `::` elision, an optional `/prefix` from
  0 through 128, and an optional `%zone`. A trailing dotted IPv4 address is
  accepted in IPv4-in-IPv6 notation. Invalid forms throw `AddressError`.
- `correctForm()` returns the recommended lowercase form with the longest zero
  run compressed using `::`; `canonicalForm()` returns eight expanded
  four-digit lowercase groups joined by colons; `isCanonical()` and
  `isCorrect()` validate those respective spellings.
  `decimal()` returns the full decimal numeric representation as a string.
- `static isValid(address)`, `fromBigInt(bigint)`, `fromArpa(value)`,
  `fromAddress4(address)`, `fromByteArray(bytes)`, and
  `fromUnsignedByteArray(bytes)` have the analogous meanings for 128 bits.
  Signed bytes from -128 through 127 are folded to unsigned values only by
  `fromByteArray`; both byte-array methods require exactly 16 integers.
- `static fromURL(url: string)` returns `{address, port}` on success, where
  `address` is an `Address6` and `port` is a number or `null`. It accepts a
  bracketed IPv6 host with an optional port, a host with a scheme, and a bare
  IPv6 host. Invalid URLs return `{error, address: null, port: null}`; ports
  outside 0 through 65535 return `port: null` when the host itself parses.
- `static fromAddressAndMask(address, mask)`,
  `static fromAddressAndWildcardMask(address, wildcardMask)`, and
  `static fromWildcard(pattern)` are the IPv6 versions of the IPv4 helpers;
  wildcards are trailing whole groups and `::` expands before counting them.
- `to4()` returns the trailing 32 bits as `Address4`; `to4in6()` returns the
  dotted IPv4-in-IPv6 spelling. `toByteArray()` and `toUnsignedByteArray()`
  return 16 unsigned bytes. `bigInt()` returns a 128-bit bigint.
- `startAddress()`, `startAddressExclusive()`, `endAddress()`,
  `endAddressExclusive()`, `subnetMaskAddress()`, `wildcardMask()`, and
  `networkForm()` operate on the CIDR range. `mask(prefix?: number)` returns
  the binary mask, `getBits(start, end)` returns a bigint, and
  `getBitsBase2(start, end)`/`getBitsBase16(start, end)` return strings.
  `reverseForm({omitSuffix?})`, `binaryZeroPad()`, and `group()` provide the
  reverse-DNS, binary, and four-group representations.
- `getScope()` and `getType()` return the library's scope/type labels.
  `embeddedIPv4()` returns an `Address4` for IPv4-mapped or well-known NAT64
  addresses and `null` otherwise. `is4`, `isMapped4`, `isTeredo`, `is6to4`,
  `isLoopback`, `isLinkLocal`, `isMulticast`, `isULA`, `isPrivate`, `isCGNAT`,
  `isBroadcast`, `isUnspecified`, and `isDocumentation` are deterministic
  boolean classifiers; mapped/NAT64 classifiers use the embedded IPv4 host.
  `static fromAddress4Nat64(address, prefix?)`, `toAddress4Nat64(prefix?)`,
  `to6to4()`, `inspectTeredo()`, and `inspect6to4()` implement the documented
  embedded-address conversions and return `null` where the address is not in
  the requested form.

### `AddressError` and `v6.helpers`

`AddressError` is an `Error` subclass with `name === 'AddressError'` and an
optional `parseMessage` HTML-safe diagnostic string. `v6.helpers` is a plain
object containing the public IPv6 helper functions, including
`prefixLengthFromMask`, `assertByteArray`, `numberToPaddedHex`,
`stringToPaddedHex`, and `testBit`. Helper failures use `AddressError` where
specified by the operation.

## Implementation Notes

Keep conversions deterministic and byte-for-byte stable. JSON cannot transport
`bigint`, class identity, or `RegExp`, so the hidden verifier calls the package
through a bounded child-process adapter and checks their documented scalar or
projected representations. This boundary does not reduce the required public
JavaScript API: ordinary callers must receive real class instances and native
`bigint` values. Do not add a CLI, network service, test-only export, or source
checkout logic to the candidate package.
