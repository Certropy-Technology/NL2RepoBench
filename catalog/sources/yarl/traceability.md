# `yarl` contract traceability

The private verifier has 44 leaves. Each leaf executes a JSON-safe scenario as
UID 10001 through the repository's generic candidate subprocess runner. The
trusted process owns expected values and all grading output.

| Public contract | Verifier leaf |
| --- | --- |
| Root exports, aliases, distribution identity, version | `exports-version-metadata` |
| Empty, copy, and `SplitResult` construction | `constructor-empty-copy-split` |
| Unicode canonical encoding and human form | `constructor-unicode-canonical` |
| `encoded=True` preservation | `constructor-encoded-preservation` |
| Absolute authority and authentication properties | `absolute-auth-properties` |
| IPv6 host subcomponents | `ipv6-host-properties` |
| Relative URL properties | `relative-properties` |
| Component-based `URL.build` | `build-components` |
| Authority and encoded build forms | `build-authority` |
| Invalid build combinations | `build-mutual-exclusion-errors` |
| String, bytes, bool, repr, hash | `string-bytes-data-model` |
| Equality and URL ordering | `comparison-ordering` |
| `/` path operator and encoded joining | `operators-path-division` |
| `%` query operator | `operators-query-modulo` |
| `origin()` and `relative()` | `origin-and-relative` |
| Default and explicit ports | `default-and-explicit-ports` |
| Raw/decoded path and path-query properties | `path-properties` |
| Parts, parent, name, and suffix properties | `path-parts-name-suffix-parent` |
| Ordered duplicate query properties | `query-properties-duplicates` |
| Raw/decoded fragment properties | `fragment-properties` |
| Scheme replacement and relative rejection | `with-scheme` |
| User/password replacement and clearing | `with-user-password` |
| IDNA host replacement and validation | `with-host` |
| Port replacement, clearing, and validation | `with-port` |
| Path encoding and retention flags | `with-path` |
| Mapping and keyword query replacement | `with-query-mapping` |
| Pair-sequence and raw-string query replacement | `with-query-pairs-and-string` |
| Query argument validation | `query-value-errors` |
| Duplicate-preserving query extension | `extend-query` |
| Key-replacing query update | `update-query` |
| Query-key removal and no-op identity | `without-query-params` |
| Fragment replacement and clearing | `with-fragment` |
| Name replacement, retention, validation | `with-name` |
| Suffix replacement, clearing, validation | `with-suffix` |
| RFC 3986 reference resolution | `join-rfc-cases` |
| Segment joining and slash rejection | `joinpath` |
| Malformed/incomplete percent input | `percent-and-malformed-input` |
| Dot-segment path normalization | `dot-segment-normalization` |
| Invalid IPv6, host, and port errors | `invalid-authority-errors` |
| Copy, deep-copy, and pickle behavior | `pickle-copy-roundtrip` |
| LRU configuration, clearing, and info | `cache-control` |
| Pydantic 2 field and adapter integration | `pydantic-integration` |
| IDNA and human-readable round trip | `idna-human-roundtrip` |
| Repeated deterministic construction | `deterministic-repetition` |

Reverse traceability is complete at leaf granularity: each leaf maps to at
least one behavior documented in `instruction.md`. No leaf asserts private
storage fields, generated implementation source, benchmark timing, network
availability, or C-extension internals.
