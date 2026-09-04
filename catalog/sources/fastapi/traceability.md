# FastAPI traceability

| Public contract section | Private leaf IDs |
| --- | --- |
| Package exports and version | `exports-version` |
| `jsonable_encoder` conversions and filters | `jsonable-primitives`, `jsonable-custom-encoder`, `jsonable-include-exclude` |
| Request parameter metadata | `params-query`, `params-path`, `params-body-form-file` |
| Dependency declarations and defaults | `depends-security-marker`, `default-placeholder` |
| Validation and HTTP exception records | `exceptions` |
| API key and HTTP security | `security-header`, `security-header-missing`, `security-http-basic`, `security-bearer`, `security-oauth-form`, `authorization-parse` |
| FastAPI and APIRouter registration | `app-registration`, `router-prefix`, `url-for` |
| OpenAPI generation and cache | `openapi-basic`, `openapi-cache`, `openapi-tags-servers`, `operation-id`, `determinism` |
| Utility behavior | `body-status-utils` |
| Server-sent events | `sse-format`, `sse-validation` |
| Response and middleware re-exports | `response-aliases`, `middleware-aliases` |
| Ordered background work | `background-order` |

Every private leaf maps to one instruction section. Conversely, each scored
instruction section has at least one leaf. The inventory explicitly excludes
unscored optional integrations rather than implying full upstream-suite parity.
