# Figures Traceability

| Contract area | Public source basis | Private verification |
| --- | --- | --- |
| Package identity and ESM root | `package.json`, `index.js`, `index.d.ts` | Candidate npm pack validation and root installation |
| Unicode and fallback symbol tables | `index.js` and the README symbol catalogue | Mapping leaves covering every special fallback family and common-symbol preservation |
| `replaceSymbols` options and literal behavior | `index.js`, README API section | Explicit `true`/`false`, repeated, multiline, empty, and replacement-text leaves |
| Type surface | `index.d.ts`, `index.test-d.ts` | Public instruction requires declaration/runtime agreement; upstream type inventory is retained |
| Offline install | `package.json` dependency closure | npm lockfile v3, integrity fields, private npm cache, and `npm ci --offline --ignore-scripts` |
| Candidate isolation | Runtime package has no verifier access | Separate verifier subprocess, `NODE_ALLOWED_PACKAGE=figures`, sanitized environment, bounded timeout/output |

The fixed denominator is 24 node:test leaves. The private contract intentionally
does not copy upstream test assertions or expose the reference implementation.
