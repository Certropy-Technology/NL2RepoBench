# Public Contract Traceability

The private verifier has 20 unique leaves. Trusted grading imports candidate
code only through a UID-10001 child adapter; collection, JUnit, grading, network
evidence, and numeric reward remain verifier-owned. The 41 upstream unittest
methods establish the frozen implementation baseline, while the scored leaves
form a bounded JSON-safe adaptation of those behavior families.

| Verifier leaf | Public instruction contract | Upstream behavior family |
| --- | --- | --- |
| `package_surface` | Supports: distribution version, root exports, import paths, `py.typed`, and native extension modules | Package imports and extension build |
| `request_basic` | `HttpRequestParser`: callback order, method/version/state getters | Ordinary request parsing |
| `request_chunked` | `HttpRequestParser`: chunk boundaries, body fragments, zero-size terminator | Chunked request tests |
| `request_upgrade` | `HttpRequestParser`: Upgrade state and tail offset exception | Request upgrade tests |
| `request_lenient` | `set_dangerous_leniencies(...)` signature and named flags | Leniency configuration |
| `request_fragmented` | Incremental one-byte feeds and observable URL/body fragments | Fragmented request/header/value tests |
| `request_input_types` | `feed_data` accepts bytes, bytearray, memoryview, and `array[int]` | Buffer input compatibility |
| `request_invalid` | Invalid method and URL exception classes | Request error tests |
| `callback_error` | Callback exceptions become `HttpParserCallbackError` with context | Request callback failure tests |
| `request_keep_alive` | HTTP version, keep-alive, and upgrade state | Request state tests |
| `response_basic` | `HttpResponseParser`: status, headers, body, callback order, getters | Ordinary response tests |
| `response_upgrade` | Response 101 Upgrade state and tail offset | Response upgrade tests |
| `response_invalid` | Generic response and invalid-status error classes | Response error tests |
| `response_input_types` | Inherited `feed_data` buffer domain | Response buffer compatibility |
| `response_callback_error` | Response callback error wrapping and context | Response callback failure tests |
| `url_components` | `parse_url`: schema, authority, port, path, query, fragment, userinfo | Absolute URL parsing |
| `url_paths` | Relative paths, query preservation, bracketed IPv6 host and port | Relative/authority URL tests |
| `url_input_types` | `parse_url` bytes-like input domain | URL buffer compatibility |
| `url_invalid` | Empty, whitespace, malformed, NUL, and over-65,535-byte errors | Invalid and overlong URL tests |
| `url_immutable` | Immutable URL attributes and `AttributeError` contract | Native URL value behavior |

Every scored leaf maps to an explicit public behavior above. Conversely, the
public core surface is covered by at least one leaf; no private helper,
filesystem path, network endpoint, or upstream test file is part of the scored
contract.
