# `@discoveryjs/json-ext` Traceability Audit

This audit maps the frozen private verifier groups to public behavior. It does
not reproduce private test bodies or hidden assertion values.

| Public contract | Private leaves | Covered behavior |
| --- | ---: | --- |
| Supports / package shape | 1 | Scoped package identity, version, ESM entry, declarations, exact root exports, scripts and dependency absence |
| `parseChunked` | 17 | Primitive and nested JSON, split tokens, sync/async/factory emitters, string and split UTF-8 chunks, JSONL/auto modes, empty JSONL, syntax and mode errors, root callbacks, progress state, whitespace |
| `stringifyChunked` | 17 | Primitive and nested serialization, deterministic chunks, threshold flushing, number/string indentation normalization, replacer order/deduplication, JSONL records, empty JSONL, non-finite and undefined normalization, circular and mode errors |
| `stringifyInfo` | 9 | UTF-8 byte count, formatted total and whitespace count, replacer and JSONL semantics, root undefined, first/all circular reporting, invalid mode |
| `parseFromWebStream` | 3 | String chunks, UTF-8 byte chunks, reader fallback without async iteration |
| `createStringifyWebStream` | 3 | Default output, formatting/chunking options, cancellation |

Total frozen leaves: 50. Every group maps to an API entry in
`instruction.md`; no private assertion targets an unmentioned helper, source
path, benchmark fixture, generated CJS bundle, or development tool.

The public contract also documents callable revivers and ordinary
`onRootValue`/`onChunk` signatures because they are public API. The fixed JSON
transport does not accept user-supplied function bodies. Instead, verifier-owned
callbacks exercise callback state deterministically inside the candidate child.
This preserves the process boundary without silently changing callback
semantics.
