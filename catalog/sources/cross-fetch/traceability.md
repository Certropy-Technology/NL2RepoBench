# `cross-fetch` Traceability

| Published contract | Private bridge behavior | Leaves |
| --- | --- | ---: |
| CommonJS root, `fetch`, `default`, ponyfill flag, constructors | package export identity | 1 |
| `Headers` case-insensitive append, set, get, has, entries | normalized header operations | 3 |
| `Request` URL, normalized method, headers, cloneable body | request construction | 4 |
| `Response` metadata, headers, body, clone | response construction | 6 |
| `fetch(url, options)` to local HTTP endpoint | verifier-owned loopback request/response | 6 |
| invalid URL rejects | invalid input outcome | 1 |

The child bridge accepts only fixed operation names. It does not accept source
code, module specifiers, commands, hosts, ports, filesystem paths, or callback
objects from the private verifier. Browser, React Native, external networking,
redirect, TLS, streaming, and proxy behavior are explicitly outside both the
instruction and the private denominator.
