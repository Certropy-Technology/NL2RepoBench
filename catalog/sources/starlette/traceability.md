# Starlette contract traceability

The private verifier collects exactly 24 child-side JSON leaves. Each leaf maps
to behavior stated in `instruction.md`; the trusted verifier owns collection,
JUnit, grading, reward, and network evidence.

| Contract area | Scenarios |
| --- | --- |
| package identity and safe imports | `exports`, `status`, `middleware-export` |
| URL, URLPath, query and secrets | `url`, `state`, `determinism` |
| multidicts and headers | `multidict`, `headers` |
| convertors and route compilation | `convertors`, `routing` |
| responses and ASGI message shapes | `response`, `cookies`, `response-asgi`, `streaming`, `ranges` |
| requests and cookie parsing | `request`, `stream-consumption`, `exceptions` |
| CORS middleware | `cors`, `cors-simple` |
| concurrency and background execution | `concurrency`, `background` |
| authentication/configuration | `config-and-auth` |
| WebSocket value objects | `websocket-and-status` |

Excluded upstream tests are service/client/optional-integration surfaces that
cannot be run deterministically in a no-network Agent environment. No hidden
assertion requires credentials, sockets, external files, a browser, or a
candidate-controlled trusted report.
