# `micromark-util-character` Traceability

The private contract independently adapts the frozen package behavior into
bounded, deterministic leaves. It does not execute candidate code in the
trusted verifier process.

| Public specification area | Private leaf family | Frozen source authority |
| --- | --- | --- |
| package name, version, ESM conditions, declaration, dependencies, exact exports, UID/GID boundary | `package metadata and exact named ESM exports` | package `package.json`, generated root files, verifier subprocess contract |
| stateless deterministic behavior | `same input is deterministic across isolated child calls` | pure predicate implementation and `sideEffects: false` |
| ASCII letters and alphanumerics | `asciiAlpha` and `asciiAlphanumeric` boundaries | `dev/index.js` regex predicates and README API |
| RFC 5322 atext | `asciiAtext` included and excluded punctuation | `dev/index.js`, README API, RFC range documentation |
| controls, digits, hex digits, punctuation | four exact boundary families | `dev/index.js` and README API ranges |
| micromark virtual endings and spaces | three virtual-code families | `dev/index.js`, symbol code inventory, README preprocessing contract |
| Unicode punctuation and symbols | representative `P` and `S` categories plus negative cases | `dev/index.js` Unicode property expression |
| ECMAScript whitespace | controls, separators, line separator, BOM, and negative cases | `dev/index.js` whitespace expression |

The trusted `node:test` process imports only `test_client.mjs`. Each request
launches a UID/GID 10001 child with an empty environment apart from bounded
runtime paths. That child loads the installed package and returns a boolean or
bounded package inventory. No candidate function, source text, object handle,
report path, or executable string crosses into trusted code.
