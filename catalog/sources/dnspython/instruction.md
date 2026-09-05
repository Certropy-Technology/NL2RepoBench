# Build `dnspython`

Create a complete, installable Python project named `dnspython` from an empty
workspace.  The project is a pure-Python DNS toolkit.  It must expose the
`dns` package and the public behavior below without requiring network access at
runtime.  Do not copy an existing dnspython checkout or depend on a
preinstalled copy of the package.

## Project Description

Implement deterministic DNS data modeling and wire-format utilities.  The
required slice parses and compares DNS names, converts DNS type/class/TTL
symbols, models resource-record sets, reads small authoritative zone files,
builds DNS query and dynamic-update messages, and converts IPv4/IPv6 reverse
names.  This task does not require contacting a recursive resolver, DNS-over-
HTTPS/QUIC, live zone transfers, platform-specific WMI support, or DNSSEC
cryptography.  Keep all required operations local and deterministic.

## Supports

- Support CPython 3.10 and newer Python 3.x versions.
- Provide an installable project with the import package `dns` and a
  `py.typed` marker.  A `pyproject.toml` using a standard PEP 517 backend is
  required; the package distribution name is `dnspython`.
- Declare no runtime third-party dependencies.  Build tools may be listed in
  the build-system section and must not be imported by `dns` at runtime.
- Runtime operations in this specification must not open sockets, read the
  current time, use uncontrolled randomness, invoke subprocesses, or access a
  network service.
- Preserve declaration order where a sequence is promised.  DNS names are
  case-insensitive for comparison, while their textual spelling is retained
  when rendered unless an API explicitly canonicalizes it.

## API Usage Guide

### DNS names: `dns.name`

Implement `dns.name.Name` and `dns.name.from_text(text, origin=None,
relativize=True, idna_codec=None)`.  `from_text` accepts a dotted DNS name,
returns a `Name`, and uses a trailing dot to mark an absolute name.  The root
is `dns.name.root`; `Name.labels` is a tuple of byte labels, including the
empty final label for an absolute name.  `str(name)` and `name.to_text()` use
escaped DNS presentation form.  Invalid escapes, labels longer than 63
octets, and names longer than 255 wire octets raise the package's DNS
exception types.

`Name.is_absolute()`, `Name.is_subdomain(other)`,
`Name.is_superdomain(other)`, `Name.relativize(origin)`,
`Name.derelativize(origin)`, `Name.concatenate(other)`, `Name.to_wire()` and
`Name.to_digestable(origin=None)` must be available.  Relative names may be
relativized against an absolute origin; attempting an unrelated operation
raises the documented DNS name exception.  Equality, ordering, and hashing
are case-insensitive and compare label-by-label from the DNS hierarchy.
`dns.name.from_wire(message, current=0, length=None)` returns `(name, offset)`
and handles DNS compression pointers and loop/error checks.

### Type and class symbols

`dns.rdatatype.from_text(text)`, `to_text(value)`,
`dns.rdatatype.RdataType.make(value)`, `is_singleton(value)`,
`dns.rdataclass.from_text(text)`, `dns.rdataclass.to_text(value)`, and
`dns.rdataclass.RdataClass.make(value)` convert between mnemonic
symbols and their integer wire values.  Matching is case-insensitive; `A` is
1, `NS` is 2, `CNAME` is 5, `SOA` is 6, `PTR` is 12, `MX` is 15, `TXT` is
16, `AAAA` is 28, and class `IN` is 1.  Unknown symbols raise the relevant
`UnknownRdatatype` or `UnknownRdataclass` exception rather than returning a
sentinel.

`dns.ttl.from_text(text)` parses a non-negative integer or units `w`, `d`,
`h`, `m`, and `s` (case-insensitive) into seconds.  `dns.ttl.make(value)`
accepts an integer or TTL presentation string and returns seconds.  Invalid or
negative values raise `dns.ttl.BadTTL`.

### Address conversion

`dns.ipv4.inet_aton(text)` and `dns.ipv4.inet_ntoa(packed)` convert an IPv4
address to/from exactly four bytes.  `dns.ipv6.inet_aton(text)` and
`dns.ipv6.inet_ntoa(packed)` do the same for 16-byte IPv6 addresses and accept
normal compressed IPv6 notation.  Invalid address strings or packed lengths
raise `ValueError` or the module's address exception.  The functions do not
perform DNS lookups.

### Resource records: `dns.rrset` and `dns.rdataset`

`dns.rrset.from_text(name, ttl, rdclass, rdtype, *text_rdatas)` returns an
`RRset` with the given `Name`, integer TTL, class, and type.  Each textual RDATA
item is parsed according to its type.  Iterating it yields RDATA objects,
`len(rrset)` is the number of records, and `rrset.to_text(origin=None)` uses
DNS presentation format.  `dns.rdataset.from_text(rdclass, rdtype, ttl,
*text_rdatas)` returns the corresponding `Rdataset`; its `.rdclass`, `.rdtype`,
`.ttl`, `add()`, `update_ttl()`, `__iter__`, and `__len__` are public.

For A and AAAA records, textual addresses round-trip through `str(rdata)`.
RRsets and rdatasets reject incompatible RDATA types.  Adding a duplicate
RDATA does not create a second duplicate member.

### Zone files: `dns.zone`

`dns.zone.from_text(text, origin=None, rdclass=dns.rdataclass.IN,
relativize=True, check_origin=True)` parses a small master-file string and
returns a `Zone`.  Support `$ORIGIN`, `$TTL`, owner names, omitted owner names
on continuation lines, comments, SOA, NS, A, AAAA, CNAME, MX, and TXT records.
When `check_origin=True`, the origin must contain both SOA and NS records.
`zone.origin`, `zone.nodes`, `zone.find_rdataset(name, rdtype, rdclass=IN)`,
and node/rdataset iteration expose the parsed data.  `Zone.to_text()` produces
stable presentation text.  `relativize=False` retains absolute owner names;
the default stores names relative to the origin.  Malformed records and a
missing required origin record raise the appropriate `dns.zone` exception.

### Messages and wire helpers

`dns.message.make_query(qname, rdtype, rdclass=IN, use_edns=None,
want_dnssec=False)` creates a `Message` containing one question and the
recursion-desired flag.  `Message.question`, `.answer`, `.authority`,
`.additional`, `.flags`, `.id`, `.to_wire()`, `.to_text()`, and
`dns.message.from_wire(wire)` are required.  Setting `id` to a known value
before serialization makes the round trip deterministic.  `make_query` must
not perform I/O.

`dns.flags.to_text(flags)` and `dns.flags.from_text(text)` convert mnemonic
flags, including `QR`, `RD`, and `RA`.  `dns.wire.Parser(data)` provides
bounded `get_uint8()`, `get_uint16()`, `get_uint32()`, `get_bytes(count)`, and
`remaining()` operations and raises on truncated input.

`dns.tokenizer.Tokenizer(text)` and its `Token` results provide
`get()`, `Token.is_eof()`, `Token.is_eol()`, and `Token.value`; quoted strings,
parentheses, escapes, and semicolon comments follow DNS master-file token
rules.

### Reverse names, updates, options, and keyrings

`dns.reversename.from_address(address)` returns the canonical `in-addr.arpa.`
or `ip6.arpa.` `Name`, and `to_address(name)` reverses it.  Invalid reverse
names raise `dns.reversename.InvalidIPAddress` or `dns.exception.SyntaxError`.

`dns.update.Update(zone, rdclass=IN, keyring=None, keyname=None,
keyalgorithm='hmac-sha256')` builds a dynamic-update `Message` without sending
it.  `Update.add(name, ttl, rdtype, *values)` appends the requested RRset to
the authority section and preserves its name/type/TTL.

`dns.tsigkeyring.from_text(mapping)` decodes base64 key values and returns a
keyring keyed by `dns.name.Name`; malformed base64 raises a decoding error.
`dns.edns.GenericOption(otype, data)` stores an EDNS option and
`to_wire()` returns the original option data bytes.

## Implementation Notes

Keep public imports compatible with the `dns` package layout: the verifier
imports modules directly, so do not replace them with a single monolithic
module.  Separate parsing, name, wire, message, zone, and record concerns in
maintainable modules. Use explicit bounds checks for wire input and avoid
network fallbacks. The evaluator uses a subprocess child boundary and
only the deterministic APIs described above. Do not add evaluator test files,
fake reward reports, or a dependency wheelhouse to the workspace.

# Natural Language Instruction

Create `dnspython` from an empty workspace. Implement the deterministic `dns`
package slice described above: names, type/class symbols, addresses, records,
zone parsing, wire helpers, messages, reverse names, updates, options, and
keyrings. Keep parser operations local and preserve the documented exception
contracts.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── dns/
    ├── __init__.py
    ├── name.py
    ├── rdatatype.py
    ├── rdataclass.py
    ├── ttl.py
    ├── rrset.py
    ├── rdataset.py
    ├── zone.py
    ├── message.py
    ├── wire.py
    ├── tokenizer.py
    └── py.typed
```

The root `dns` package must expose the modules and functions named in the API
guide. Keep wire, zone, name, and record concerns in importable modules; do
not add a resolver service, test bundle, or runtime network dependency.

# Examples

```python
from dns.name import from_text
from dns.rdatatype import from_text as type_code

name = from_text("www.example.")
assert name.is_absolute()
assert type_code("A") == 1
```

```python
from dns.zone import from_text

zone = from_text("$ORIGIN example.\n@ 300 IN A 192.0.2.1\n", check_origin=False)
```

```python
from dns.message import make_query

query = make_query("example.", "A")
query.id = 7
wire = query.to_wire()
```

# Error Handling and Boundary Conditions

Reject malformed names, labels, wire input, TTLs, addresses, zone records,
and unknown type/class symbols with the documented DNS exceptions or
`ValueError`. Wire parsers must fail on truncation and compression loops. Query
construction never sends packets; all APIs remain deterministic and
NoNetwork.
