# Public Contract Traceability

The task uses a fixed 42-leaf private verifier. Each leaf invokes a candidate
operation in a fresh UID-10001 child process through the generic candidate
JSON boundary. The trusted verifier owns expected observations, collection,
JUnit, grading, and reward.

| Contract area | Instruction section | Deterministic coverage |
| --- | --- | --- |
| Distribution metadata and debug state | Root package; Supports | version, metadata, debug setter/getter, root imports |
| Percent encoding and query handling | Common helpers | quote/unquote, ordered duplicate pairs, malformed escapes, URI fragments |
| Request normalization | Common helpers | case-insensitive headers, decoded body, query duplicates |
| OAuth1 parameter handling | OAuth 1.0 RFC 5849 | escaping, auth header parsing/preparation, form/query placement |
| OAuth1 signatures | OAuth 1.0 RFC 5849 | base URI, collection, normalization, HMAC-SHA1/SHA256, PLAINTEXT |
| OAuth2 scope and URI helpers | OAuth 2.0 RFC 6749 and RFC 8628 | scope conversion, URI params, host/security checks |
| OAuth2 request/response behavior | OAuth 2.0 RFC 6749 and RFC 8628 | grant/token/revocation preparation, success/error parsing, expiry parsing |
| Token and bearer behavior | OAuth 2.0 RFC 6749 and RFC 8628 | scope deltas, header/query/body placement |
| Stateful clients | OAuth 2.0 RFC 6749 and RFC 8628 | web/backend/mobile/legacy/device request construction and state |

The full upstream test suite is retained only as source health evidence. It is
not copied into the public instruction or used as the frozen production
denominator.
