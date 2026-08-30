# `strtok3` traceability

Frozen source revision: `acac939a405a6dfebcf3fe9b9caba3641c491c95`
(`10.3.5`).

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1-4 | ESM package identity, root factories/classes/errors, exact runtime dependency | package metadata, `lib/index.ts`, `lib/core.ts` |
| 5-6 | buffer metadata, initial position, random access, caller metadata | `BufferTokenizer` constructor and upstream matrix |
| 7-16 | read/peek defaults, length, position, partial reads, EOF, state | upstream read/peek option matrix and tokenizer interfaces |
| 17-20 | ignore, range errors, clamping, direct random positioning | `AbstractTokenizer.ignore`, random-access interface |
| 21-26 | token and numeric decoding, read/peek position, partial-token EOF | `AbstractTokenizer` token helpers and upstream numeric matrix |
| 27-32 | Blob, WHATWG stream, and Node stream read/peek parity | upstream five-factory matrix |
| 33-36 | Blob metadata, sequential capability, backward-position rejection | factory implementations and stream constraints |
| 37-39 | local file and fs.ReadStream metadata/random reads | `FileTokenizer`, Node root `fromStream`, upstream file tests |
| 40-44 | abort, close, empty source behavior, deterministic sessions | tokenizer lifecycle and EOF tests |

Trusted tests never import the candidate. Object construction and all candidate
calls happen in a bounded UID-separated Node child. The contract does not
cover private stream reader classes, timing-sensitive delayed abort races,
arbitrary user callbacks, HTTP/S3 adapters, Bun, browser bundlers, or native
addons.
