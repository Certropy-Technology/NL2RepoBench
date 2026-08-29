# s3fs contract traceability

The hidden verifier collects exactly 20 child-side JSON leaves. Candidate code
runs as UID 10001; the trusted runner owns all expected values and grading.

| Public contract | Scenarios |
| --- | --- |
| Package imports and required exports | `exports-and-metadata` |
| Constructor defaults, aliases, requester-pays and protocol | `constructor-options`, `requester-pays` |
| Constructor conflict and numeric validation | `constructor-validation` |
| s3/s3a, version-aware and ARN path parsing | `split-paths` |
| 50 MiB chunk sizing and VersionId kwargs | `chunking-and-version-helper` |
| title-case and SSE parameter serialization | `utils-serialization` |
| S3 error-code translation and exception cause | `error-translation` |
| Retryable error registration and custom handler setter | `retry-configuration` |
| Root existence and explicit cache clearing | `root-and-cache`, `cache-invalidation` |
| Sorted cached listing and detail shape | `cached-listing` |
| Head-object info through an async fake call | `fake-info` |
| Bucket/object existence through an async fake call | `fake-exists` |
| Small byte upload through `pipe_file` | `pipe-file` |
| Buffered ranged read and body closing | `buffered-read` |
| Small buffered write and one-shot PUT | `buffered-write` |
| Binary async stream and byte position | `async-stream` |
| Binary-only async open validation | `open-validation` |
| FSMap construction and root delegation | `mapping-factory` |

Every scenario maps to behavior stated in `instruction.md`. No scenario reads
private candidate files, hidden test names, source text, or trusted report
paths. Remote S3 integration and the upstream moto fixtures are excluded by
the deterministic no-network adaptation and are recorded in
`test-inventory.json`.
