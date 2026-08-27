# dnspython test traceability

The private verifier has 20 unique leaf IDs.  Each leaf is directly supported
by the public instruction and uses only local deterministic inputs:

| Leaf | Public contract |
| --- | --- |
| `name-presentation` | `dns.name.from_text`, labels, absolute names |
| `name-relations` | relativize, derelativize, sub/superdomain |
| `name-wire-roundtrip` | name wire and digestable encodings |
| `type-and-class-symbols` | type/class conversions and unknown errors |
| `ttl-conversion` | TTL parsing and `TTL.make` |
| `ipv4-conversion` | IPv4 packed address conversion |
| `ipv6-conversion` | IPv6 packed address conversion |
| `rrset-a-records` | textual A RRset parsing and iteration |
| `rdataset-deduplication` | Rdataset metadata and duplicate suppression |
| `zone-relative-lookup` | relative zone parsing and lookup |
| `zone-absolute-owners` | absolute-owner zone parsing |
| `query-message` | deterministic query construction |
| `message-wire-roundtrip` | message serialization and parsing |
| `flags-conversion` | mnemonic DNS flags |
| `tokenizer-comments` | master-file tokenization and comments |
| `wire-parser` | bounded integer/byte wire reads |
| `reverse-name` | IPv4 reverse-name conversion |
| `dynamic-update` | offline dynamic update construction |
| `keyring-and-edns-option` | keyring decoding and EDNS option bytes |
| `package-version-metadata` | package import and frozen version metadata |

The reference checkout passed all 20 leaves in a local child-process smoke
using the same private verifier.  Harbor Oracle, empty, stub, forgery,
timeout, and offline run receipts are intentionally not asserted here because
this authoring lane is forbidden from starting a Harbor Agent Run.
