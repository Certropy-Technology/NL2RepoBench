# google-api-core Specification Traceability

| Public behavior group | Private leaf IDs | Boundary |
| --- | --- | --- |
| Package identity, namespace imports and re-exports | `package-identity-and-import-boundary` | install/import metadata |
| Client metadata and options | `client-info-user-agent-order`, `client-options-storage-and-repr`, `client-options-validation` | deterministic strings, mappings, validation |
| Datetime and RFC3339 helpers | `datetime-epoch-conversions`, `rfc3339-offset-and-format`, `nanosecond-preservation` | UTC, offsets, nanoseconds |
| Path templates and REST query serialization | `path-template-expansion-and-validation`, `path-field-read-and-delete`, `rest-query-flattening` | expansion, traversal rejection, flattening |
| Exceptions and universe domains | `http-and-grpc-exception-mapping`, `universe-domain-and-endpoint-selection` | HTTP/gRPC mapping and endpoint selection |
| Retry and timeout policies | `constant-and-exponential-timeouts`, `injected-clock-deadline-timeout`, `retry-predicates-and-backoff`, `retry-wrapper-repeats-transient-failure` | predicates, generators, decorator arguments |
| Protobuf helpers | `protobuf-field-access`, `protobuf-field-mask` | protobuf message and field masks |
| Page iterators and version headers | `page-iteration-state`, `api-version-header` | deterministic local iteration |
| Optional import boundaries and error contracts | `optional-grpc-import-boundary` | no service access, stable exception types |

These rows map exactly 21 scored leaves. Every leaf is invoked through a
subprocess adapter under the unprivileged
candidate UID. The parent verifier owns collection, nonce validation, JUnit and
reward generation. The adapter never reads a candidate-controlled report file.

The specification deliberately excludes live credentials, metadata servers,
network transports, gRPC channel construction, background bidi consumers,
filesystem side effects, and wall-clock timing. Those behaviors require external
state and are not a deterministic package contract for this task.
