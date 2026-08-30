# Public Contract Traceability

The private verifier has a fixed 94-leaf `custom-json-v1` contract. It batches
predefined requests into bounded UID 10001 child processes. The trusted
verifier owns expected values, collection, JUnit, grading, network evidence,
and reward output; candidate workspace reports are ignored.

| Public contract area | Instruction section | Deterministic coverage |
| --- | --- | --- |
| Distribution and exports | Supports | exact name/version/Python/dependency metadata; root and class namespace exports |
| Authentication | Authentication | API key, bearer, client credential/password fields; string/list/default scope; negative expiration warning |
| Connection models | Connection configuration | protocol validation, HTTP/HTTPS defaults, explicit ports, gRPC security, collision and scheme errors, timeout/proxy models |
| UUID and URL utilities | Utility functions | canonical/compact/object/beacon UUIDs, malformed input, beacon/domain/object URL validation |
| Version/time/vector utilities | Utility functions | short/prefixed versions, server branch minima, UUID5, sanitization, beacons, timeout normalization, datetime encoding/decoding, list vectors |
| Filters | Filter builders | property/length/list/id/time/geo/reference/count targets, empty errors, AND/OR/NOT, non-instantiability |
| Query objects | Query builders | metadata presets, sort chains, grouping, rerank, move, MMR, BM25 operators, boost variants and blend |
| Property/schema config | Collection configuration | scalar/nested/reference properties, reserved names, text analyzer, inverted index, tenancy, replication |
| Vector config | Collection configuration | HNSW+PQ, flat+BQ, dynamic, HFresh+RQ, create/update camelCase payloads |
| Revision regression | Collection configuration | HFresh RQ merge with no PQ block, preserving unrelated fields while changing rescore limit |

The 418-leaf upstream unit collection is source/environment evidence, not the
production denominator. The focused denominator is intentionally service-free
and specifies every behavior it grades.
