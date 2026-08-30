# `unist-util-is` traceability

Frozen source revision: `82b9c2547dfa52e6078a546ab5a1c64bb9381480`
(`6.0.1`). Production denominator: 56 `node:test` leaves.

| Leaf range | Public contract | Frozen source/test basis |
| --- | --- | --- |
| 1-4 | exact package metadata, named exports, declaration entry, UID/GID isolation | `package.json`, `index.js`, generated declarations, verifier boundary |
| 5-12 | nullish and malformed inputs, node-like `type` presence, field independence, no mutation | `looksLikeANode`, upstream omitted/object tests |
| 13-16 | exact case-sensitive string matching without coercion | `typeFactory`, upstream type tests |
| 17-24 | subset object matching, strict equality, undefined/missing behavior, nested reference identity | `propertiesFactory`, upstream partial-match tests |
| 25-30 | ordered array OR, empty arrays, mixed forms, callback ordering and short-circuiting | `anyFactory`, upstream array tests |
| 31-38 | callback boolean conversion plus node/index/parent/context arguments | `castFactory`, upstream callback and context tests |
| 39-47 | invalid selector, index, parent, and index/parent pair errors | `is` validation branches and upstream error tests |
| 48-56 | unconditional nullish checks, reusable string/object/array/function checks, determinism, normalization, eager selector validation | `convert`, `ok`, `castFactory`, exported `Check` contract |

The trusted verifier reads the private adapter source and writes it once to a
root-owned, non-writable temporary path. Every request then launches that
adapter under UID/GID 10001 with an empty environment, bounded process and file
descriptor limits, no addons, no network, bounded JSON input/output, and a hard
timeout. No candidate object, function, source text, or report path crosses
into trusted code.
