# Contract Traceability

The private verifier emits exactly 26 unique `custom-json-v1` leaves. Candidate
imports and behavior probes run in UID-10001 child processes; the root verifier
owns the report, collection, JUnit, and reward files.

| Contract area | Deterministic leaves |
| --- | --- |
| Distribution and exports | package identity, version, `__all__`, root symbols |
| Event model | defaults, JSON decoding, stable repr, field values |
| SSE parsing | multiline data, CR/LF forms, chunk boundaries, flush, comments, unknown fields, ids, retry, NUL handling |
| EventSource | response identity, content-type acceptance, content-type rejection, sync and async iteration, final partial-line flush |
| Connection helpers | sync request headers, method/path forwarding, sync event iteration, async request headers, async event iteration |
| Error contract | `SSEError` inherits `httpx.TransportError`; invalid retry and empty dispatch behavior |

The full upstream test collection is retained in task-local provenance only. The
26-leaf denominator is independently authored to avoid live services and hidden
dependency downloads while preserving the core public behavior.

The final verifier bundle is
`sha256:489634abf1fb9a28b13f2331cad9684e6463ea2d04ef2ee5596266c2c17d4237`.
Each scenario executes through `runuser` as UID 10001 with a two-second child
timeout; the trusted parent writes the collection, JUnit, grading, and reward.
The final Oracle and offline runs passed all 26 leaves. Stub, forgery, and a
hung-import control each collected the same 26 leaf IDs and scored 0/26.
