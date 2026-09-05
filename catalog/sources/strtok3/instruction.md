# Project Description

Build an installable ESM npm package named `strtok3`, version `10.3.5`, from
an empty workspace. The package creates stateful binary tokenizers over
`Uint8Array`, `Blob`, WHATWG byte streams, Node.js readable streams, and local
files. Tokenizers support bounded reads, non-consuming peeks, custom token
decoding, random access where the underlying source permits it, position
tracking, skipping, aborting, and closing.

## Natural Language Instruction

Create `strtok3` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `strtok3`. Primary import or package entry: `strtok3`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: @tokenizer/token@0.3.0. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `44` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── lib/
    ├── core.js
    ├── core.d.ts
    ├── index.js
    ├── index.d.ts
    ├── AbstractTokenizer.js
    ├── BufferTokenizer.js
    ├── FileTokenizer.js
    └── ReadStreamTokenizer.js
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### Factory functions

All factories accept optional `ITokenizerOptions` containing `fileInfo`, an
async `onClose` callback, and an `AbortSignal`.

```ts
function fromBuffer(data: Uint8Array, options?: ITokenizerOptions): BufferTokenizer;
function fromBlob(blob: Blob, options?: ITokenizerOptions): BlobTokenizer;
function fromWebStream(stream: ReadableStream<Uint8Array>, options?: ITokenizerOptions): ReadStreamTokenizer;
function fromStream(stream: import('node:stream').Readable, options?: ITokenizerOptions): Promise<ReadStreamTokenizer>;
function fromFile(path: string): Promise<FileTokenizer>;
```

`fromBuffer` and `fromBlob` are random-access tokenizers. Their `fileInfo.size`
is the byte length of the source, overriding a caller-provided size while
preserving other metadata. A Blob also supplies its MIME type, including the
empty string when no type was given.

`fromWebStream` and `fromStream` are sequential. The package-root Node
`fromStream` is asynchronous and, when given an `fs.ReadStream`, discovers the
stream path and file size. `fromFile` opens a local file and provides its path
and size. Files and streams are closed by `close()`; callers should use
`try/finally`.

```js
import {fromBuffer} from 'strtok3';

const tokenizer = fromBuffer(Uint8Array.of(5, 112, 101, 116, 101, 114));
try {
  const first = new Uint8Array(1);
  await tokenizer.readBuffer(first); // 1; first[0] === 5
  tokenizer.position; // 1
} finally {
  await tokenizer.close();
}
```

### Tokenizer state and metadata

Every tokenizer provides:

```ts
readonly fileInfo: IFileInfo;
readonly position: number;
supportsRandomAccess(): boolean;
close(): Promise<void>;
abort(): Promise<void>;
```

`position` starts at zero and counts consumed or ignored bytes. Peeks never
change it. `supportsRandomAccess()` is true for buffer, Blob, and file
tokenizers and false for stream tokenizers. `close()` aborts pending work,
releases owned resources, and invokes the optional `onClose` callback.

### Buffer reads and peeks

```ts
interface IReadChunkOptions {
  length?: number;
  position?: number;
  mayBeLess?: boolean;
}

readBuffer(target: Uint8Array, options?: IReadChunkOptions): Promise<number>;
peekBuffer(target: Uint8Array, options?: IReadChunkOptions): Promise<number>;
```

The default length is `target.length`. `length` limits how many leading bytes
of the target are filled. `position` selects the absolute source offset; a read
advances the tokenizer to the byte after the returned data, while a peek does
not advance. Random-access tokenizers may move backward. Sequential tokenizers
reject a requested position below their current position.

Without `mayBeLess`, insufficient source bytes throw `EndOfStreamError`. With
`mayBeLess: true`, the methods return the available count, including zero, and
leave the unused target suffix unchanged.

### Token reads and numeric helpers

```ts
interface IGetToken<T> {
  len: number;
  get(array: Uint8Array, offset: number): T;
}

readToken<T>(token: IGetToken<T>, position?: number): Promise<T>;
peekToken<T>(token: IGetToken<T>, position?: number): Promise<T>;
readNumber(token: IGetToken<number>): Promise<number>;
peekNumber(token: IGetToken<number>): Promise<number>;
```

The tokenizer reads exactly `token.len` bytes and calls `token.get(bytes, 0)`.
Read variants advance by the token length; peek variants do not. A partial
token throws `EndOfStreamError`. Numeric helpers reuse the same contract for
number-valued tokens.

### Skipping and random positioning

```ts
ignore(length: number): Promise<number>;
setPosition(position: number): void; // random-access tokenizers only
```

`ignore` rejects a negative length with `RangeError`. If source size is known,
it advances only to EOF and returns the actual number skipped. Otherwise it
advances by the requested non-negative length. `setPosition` directly changes
the cursor for buffer, Blob, and file tokenizers.

### Runtime exports and errors

The root exports `AbstractTokenizer`, `FileTokenizer`, `EndOfStreamError`, and
`AbortError`. Export matching TypeScript interfaces for tokenizer options,
chunk options, file information, random-access tokenizers, and token types.
`EndOfStreamError` distinguishes strict short reads; `AbortError` represents an
aborted asynchronous stream operation.

## Implementation Notes

Use package exports so the Node root resolves to `./lib/index.js`, the default
condition resolves to `./lib/core.js`, and `./core` resolves to the portable
core module. The implementation must remain deterministic and bounded by the
provided source data. Do not read arbitrary files except through the explicit
`fromFile` or file-stream input supplied by the caller.

The public API is exercised with Uint8Arrays, Blobs, streams, files, and token
objects. Keep the package independent of external services and process-global
evaluation state; only the documented package files belong in the project.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
function fromBuffer(data: Uint8Array, options?: ITokenizerOptions): BufferTokenizer;
function fromBlob(blob: Blob, options?: ITokenizerOptions): BlobTokenizer;
function fromWebStream(stream: ReadableStream<Uint8Array>, options?: ITokenizerOptions): ReadStreamTokenizer;
function fromStream(stream: import('node:stream').Readable, options?: ITokenizerOptions): Promise<ReadStreamTokenizer>;
function fromFile(path: string): Promise<FileTokenizer>;
```

```javascript
import {fromBuffer} from 'strtok3';

const tokenizer = fromBuffer(Uint8Array.of(5, 112, 101, 116, 101, 114));
try {
  const first = new Uint8Array(1);
  await tokenizer.readBuffer(first); // 1; first[0] === 5
  tokenizer.position; // 1
} finally {
  await tokenizer.close();
}
```

```javascript
readonly fileInfo: IFileInfo;
readonly position: number;
supportsRandomAccess(): boolean;
close(): Promise<void>;
abort(): Promise<void>;
```

```javascript
interface IReadChunkOptions {
  length?: number;
  position?: number;
  mayBeLess?: boolean;
}

readBuffer(target: Uint8Array, options?: IReadChunkOptions): Promise<number>;
peekBuffer(target: Uint8Array, options?: IReadChunkOptions): Promise<number>;
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
