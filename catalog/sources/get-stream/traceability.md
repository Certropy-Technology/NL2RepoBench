# Test Traceability

The frozen private collection contains 30 unique `node:test` leaves. Every leaf
is mapped to the public contract in `instruction.md`; the adapter uses only the
package root and standard Node stream constructors.

| Contract area | Private leaves |
| --- | ---: |
| Root ESM exports and `MaxBufferError` | 1 |
| Text chunks, UTF-8 boundaries, and text limits | 7 |
| Buffer, ArrayBuffer, typed-array, and DataView conversion | 8 |
| Array output and object-mode preservation | 4 |
| Node/Web streams, async iterables, cleanup, concurrency | 5 |
| Input errors, stream errors, buffered data, and limits | 5 |

The upstream revision was also run with its own `npm test` command. Its 189
passing checks include AVA behavior tests, TypeScript declarations, and XO
linting. Harbor intentionally uses a smaller deterministic behavior slice so
the candidate boundary is JSON-safe and separate from the trusted verifier;
the source inventory records the full upstream test surface.
