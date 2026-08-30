# Project Description

Build an installable ESM npm package named `strtok3`, version `10.3.5`, from
an empty workspace. The package creates stateful binary tokenizers over
`Uint8Array`, `Blob`, WHATWG byte streams, Node.js readable streams, and local
files. Tokenizers support bounded reads, non-consuming peeks, custom token
decoding, random access where the underlying source permits it, position
tracking, skipping, aborting, and closing.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and pure ESM semantics.
- The package root is the Node entry. It exposes the factories and runtime
  classes described below. The `strtok3/core` subpath exposes the portable
  factories and types without `fromFile` or `FileTokenizer`.
- Provide JavaScript runtime files and matching TypeScript declarations under
  `lib/`. No compile step is run by the evaluator.
- Pin the only runtime dependency exactly as
  `"@tokenizer/token": "0.3.0"`. This dependency contains TypeScript token
  interfaces; do not add any other dependency.
- Commit an npm v3 lockfile. A clean verifier installs with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not add workspaces, native addons, registry overrides, lifecycle scripts,
  a CLI, or network behavior.

# API Usage Guide

## Factory functions

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

## Tokenizer state and metadata

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

## Buffer reads and peeks

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

## Token reads and numeric helpers

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

## Skipping and random positioning

```ts
ignore(length: number): Promise<number>;
setPosition(position: number): void; // random-access tokenizers only
```

`ignore` rejects a negative length with `RangeError`. If source size is known,
it advances only to EOF and returns the actual number skipped. Otherwise it
advances by the requested non-negative length. `setPosition` directly changes
the cursor for buffer, Blob, and file tokenizers.

## Runtime exports and errors

The root exports `AbstractTokenizer`, `FileTokenizer`, `EndOfStreamError`, and
`AbortError`. Export matching TypeScript interfaces for tokenizer options,
chunk options, file information, random-access tokenizers, and token types.
`EndOfStreamError` distinguishes strict short reads; `AbortError` represents an
aborted asynchronous stream operation.

# Implementation Notes

Use package exports so the Node root resolves to `./lib/index.js`, the default
condition resolves to `./lib/core.js`, and `./core` resolves to the portable
core module. The implementation must remain deterministic and bounded by the
provided source data. Do not read arbitrary files except through the explicit
`fromFile` or file-stream input supplied by the caller.

The evaluator constructs Uint8Arrays, Blobs, streams, files, and token objects
inside an isolated UID-separated Node child process. Trusted tests communicate
with that process only through bounded JSON and never import candidate code.
Private tests and the Oracle implementation are not part of the package to
implement.
