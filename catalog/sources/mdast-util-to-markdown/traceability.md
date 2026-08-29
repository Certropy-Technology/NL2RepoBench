# `mdast-util-to-markdown` Traceability

Frozen revision: `ee3b3458a466c3224800ac7fa688b4a160a91ea2`.
The upstream package passes 478 tests on the locked image. The production
verifier uses 72 unique `node:test` leaves that are reviewable against the
public package-root contract. Every leaf invokes the installed candidate as
UID 10001 through the one-shot JSON adapter.

| Public contract | Verifier coverage | Leaves |
| --- | --- | ---: |
| ESM package identity, root exports, declaration, no CLI/workspace/lifecycle hooks, exact direct dependencies | package inspection | 4 |
| Empty/root/paragraph, headings, blockquotes, HTML, thematic breaks, code blocks, inline code, emphasis, strong, hard breaks | direct serialization | 23 |
| Links, images, references, definitions, autolink/resource/title forms | direct serialization | 13 |
| Ordered/unordered/nested/empty/adjacent lists and indentation/marker options | direct serialization | 10 |
| Context-sensitive escaping, Unicode, character references, unsafe rules, position independence, flow separation | direct serialization | 6 |
| `defaultHandlers`, repeat determinism, input immutability, custom handlers, extensions, and joins | inspection and child-side callback adapters | 7 |
| Non-node/unknown-node failures and invalid marker/indent/repetition option domains | bounded exception records | 10 |
| **Total** | fixed collection | **72** |

Reverse traceability is complete for the supported root surface:

- `Project Description` and `Supports` map to package inspection plus the
  generic offline install/package boundary.
- Every core mdast node family named in the API guide has direct behavioral
  coverage.
- Every scalar marker/layout option is either exercised in a success case or
  validated through its documented error domain.
- `handlers`, `extensions`, and `join` use fixed child-side callbacks;
  `unsafe` uses a JSON-compatible rule. Candidate callbacks never enter the
  trusted process.
- `defaultHandlers` is checked for the exact documented key and function
  surface; internal `State` helpers are not imported by trusted tests.

The verifier intentionally does not copy the complete 478-test upstream suite.
That suite establishes the health of the frozen reference. The 72-leaf task
contract exposes a bounded, independently implementable API and does not assert
private implementation structure, formatting/lint configuration, repository
metadata, or undocumented extension internals.
