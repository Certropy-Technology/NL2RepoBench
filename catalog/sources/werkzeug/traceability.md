# Werkzeug Traceability

The private verifier has 35 unique leaves. Every leaf is a deterministic
behavior described in `instruction.md`; no leaf imports the candidate in the
trusted verifier process.

| Leaf family | Leaves | Public contract |
| --- | ---: | --- |
| datastructures | 8 | MultiDict, ImmutableMultiDict, Headers, Accept, ETags, Authorization, FileStorage |
| HTTP | 8 | list/dict/options headers, ETag, date, cookie serialization |
| URLs | 2 | IRI and URI conversion |
| security | 2 | safe_join and password verification |
| WSGI | 3 | host/current URL, limited stream |
| sans-IO | 4 | request properties, response status/cookie |
| wrappers | 4 | request/response and local test client |
| routing | 2 | matching and building |
| test helpers | 2 | environ builder and multipart encoding |

The full frozen upstream suite collected 1045 tests and passed 1045 tests after
the only environment issue, an overlong UNIX socket path, was remediated with
`--basetemp=/tmp/wz`. Live-server, debugger-browser, and external-service
tests are excluded from the fixed denominator because they are not bounded
local library behavior; the exclusions are recorded in `test-inventory.json`.
