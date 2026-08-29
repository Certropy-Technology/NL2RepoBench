# Project Description

Build an installable npm package named `@discoveryjs/json-ext`, version
`1.1.0`, from an empty workspace. The package extends the built-in JSON APIs
with incremental parsing and serialization for chunked inputs, JSON Lines
(JSONL/NDJSON), output-size analysis, and Web Stream helpers.

The scored contract is a bounded, deterministic slice of the public package.
It covers JSON-compatible values, strings and UTF-8 byte chunks, array-form
replacers, formatting options, parser progress callbacks, circular-reference
reporting, and Web Streams. No source text, function body, loader, or other
executable value is sent across the verifier boundary.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64`.
- An ESM package with `"type": "module"` and a root import entry at
  `./src/index.js`.
- A root `exports` declaration with TypeScript declarations at `./index.d.ts`.
- Exactly these named root runtime exports:
  `parseChunked`, `stringifyChunked`, `stringifyInfo`,
  `parseFromWebStream`, and `createStringifyWebStream`.
- A scripts-stripped production distribution: `package.json` must not contain
  `scripts`, `dependencies`, or `devDependencies`. Runtime dependencies,
  native addons, workspaces, lifecycle hooks, registry configuration, custom
  loaders, and generated downloads are not allowed.
- A committed npm lockfile using lockfile version 3. The zero-dependency package
  must install with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Inputs and outputs are bounded. Ordinary scored values contain only finite
  JSON numbers, strings, booleans, nulls, arrays, and plain objects. Dedicated
  fixed operations exercise `undefined`, non-finite numbers, and circular
  references without accepting executable input.

# API Usage Guide

## `parseChunked(input, optionsOrReviver?)`

**Import path:** package root.

**Signatures:**

```ts
type Chunk = string | Uint8Array | Buffer;
type ParseMode = "json" | "jsonl" | "auto";

type ParseChunkedState = {
  readonly mode: "json" | "jsonl";
  readonly returnValue: unknown;
  readonly currentRootValue: unknown;
  readonly rootValuesCount: number;
  readonly consumed: number;
  readonly parsed: number;
};

type ParseOptions = {
  reviver?: (this: unknown, key: string, value: unknown) => unknown;
  mode?: ParseMode;
  onRootValue?: (value: unknown, state: ParseChunkedState) => void;
  onChunk?: (
    chunkParsed: number,
    chunk: string | null,
    pending: string | null,
    state: ParseChunkedState,
  ) => void;
};

parseChunked(
  input: Iterable<Chunk> | AsyncIterable<Chunk> |
    (() => Iterable<Chunk> | AsyncIterable<Chunk>),
  optionsOrReviver?: ParseOptions |
    ((this: unknown, key: string, value: unknown) => unknown),
): Promise<unknown>;
```

Parse the chunks incrementally using JSON syntax. String chunks use JavaScript
string indexing. Typed-array and Buffer chunks are UTF-8; an incomplete
multi-byte sequence at a chunk boundary must be joined with the next byte
chunk before decoding. The input may be an iterable, async iterable, generator,
async generator, or a function that returns one of those values. Any other
emitter or chunk type throws `TypeError`.

Modes are deterministic:

| Mode | Behavior |
| --- | --- |
| `json` | Default. Parse exactly one JSON root value. A second value is a syntax error. |
| `jsonl` | Parse newline-separated root values and resolve to an array. Empty input resolves to `[]`. |
| `auto` | Start as ordinary JSON. If another root value begins after a line break, switch to JSONL and resolve to all roots as an array. A single root keeps its ordinary value. |

An invalid mode throws
`TypeError('Invalid options: `mode` should be "json", "jsonl", or "auto"')`.
Malformed JSON throws `SyntaxError`; when parsing has already consumed earlier
chunks, any `at position N` location in the native error is adjusted to the
position in the complete input.

`reviver` follows `JSON.parse` post-order traversal, including deletion when it
returns `undefined`. Callback-valued inputs do not cross the scored JSON
transport, but implementations must retain the public signature.

When `onRootValue` is present, it is called once after each root is finalized
and the promise resolves to the number of processed roots instead of retaining
the values. `onChunk` is called after each input chunk and once at completion
with `(0, null, null, state)`. State counters use consumed JavaScript string
units after UTF-8 decoding; `parsed` may trail `consumed` while a token is
pending and equals it in the final callback.

Examples:

```js
await parseChunked(['{"name":', '"demo"}']);
// { name: "demo" }

await parseChunked(['{"id":1}\n', '{"id":2}'], { mode: "jsonl" });
// [{ id: 1 }, { id: 2 }]
```

## `stringifyChunked(value, optionsOrReplacer?, space?)`

**Import path:** package root.

**Signatures:**

```ts
type Replacer = ((this: unknown, key: string, value: unknown) => unknown) |
  Array<string | number> | null;
type Space = string | number | null;
type StringifyOptions = {
  replacer?: Replacer;
  space?: Space;
  mode?: "json" | "jsonl";
  highWaterMark?: number;
};

stringifyChunked(value: unknown, replacer?: Replacer, space?: Space): Generator<string>;
stringifyChunked(value: unknown, options: StringifyOptions): Generator<string>;
```

Return a synchronous generator of string chunks. Joining all yielded chunks
must produce the same JSON token order and primitive normalization as
`JSON.stringify` for supported values, except that a root value which would be
`undefined` is emitted as `"null"`. Object properties whose normalized value is
`undefined` are omitted; unsupported array elements become `null`; non-finite
numbers become `null`; `toJSON` is applied before a replacer; and circular
structures throw `TypeError("Converting circular structure to JSON")`.

An array replacer is an ordered allowlist. Convert string and number entries to
strings, remove duplicates while preserving first occurrence, and ignore other
entry types. Numeric indentation is clamped to ten spaces. String indentation
uses at most its first ten UTF-16 code units. Empty, zero, negative, and
non-finite indentation disables pretty printing.

`highWaterMark` defaults to 16 KiB. It is a flush threshold, not a promise that
every chunk has exactly that size: emit after completing a serialization state
step once the buffer meets the threshold, and always flush the final buffer.
Chunk order and boundaries are deterministic for the same input and options.

In `jsonl` mode, an array is treated as the sequence of root records. Separate
records with one `\n`, do not append a trailing newline, and yield no chunks for
an empty array. A non-array is one record. Invalid modes throw
`TypeError('Invalid options: `mode` should be "json" or "jsonl"')`.

```js
[...stringifyChunked({ a: 1, b: true })].join("");
// '{"a":1,"b":true}'

[...stringifyChunked([{ id: 1 }, { id: 2 }], { mode: "jsonl" })].join("");
// '{"id":1}\n{"id":2}'
```

## `stringifyInfo(value, optionsOrReplacer?, space?)`

**Import path:** package root.

**Signatures:**

```ts
type StringifyInfoOptions = {
  replacer?: Replacer;
  space?: Space;
  mode?: "json" | "jsonl";
  continueOnCircular?: boolean;
};

type StringifyInfoResult = {
  bytes: number;
  spaceBytes: number;
  circular: object[];
};

stringifyInfo(value: unknown, replacer?: Replacer, space?: Space): StringifyInfoResult;
stringifyInfo(value: unknown, options?: StringifyInfoOptions): StringifyInfoResult;
```

Analyze serialization without materializing the complete output. For an
acyclic supported value, `bytes` is the UTF-8 byte length of the text produced
by `stringifyChunked` with matching replacer, spacing, and mode. `spaceBytes`
is the formatting whitespace attributable to pretty indentation and the space
after object colons; JSONL record separators remain part of `bytes` but not
`spaceBytes`.

Report encountered circular objects once in insertion order. Count a circular
edge as serialized `null`. By default stop analysis after the first circular
edge. With `continueOnCircular: true`, continue walking to find additional
circular objects. The returned object references are native values; the scored
adapter reports their count because object identity is not JSON-serializable.

Replacer, spacing, JSONL, primitive normalization, key order, and invalid-mode
errors follow `stringifyChunked`. A root `undefined` has the package's observed
analysis size of 9 bytes (`"undefined"`) even though chunked serialization emits
`"null"`.

## `parseFromWebStream(stream)`

**Import path:** package root.

**Signature:**

```ts
parseFromWebStream(stream: ReadableStream<Chunk>): Promise<unknown>;
```

Consume a Web `ReadableStream` and parse it as ordinary JSON. When the stream
has an async iterator, it may be passed directly to `parseChunked`. Otherwise,
read with `getReader()` until `done`, release the reader lock in a `finally`
block, and parse the yielded chunks. Parsing and error behavior are the same as
`parseChunked` in `json` mode.

## `createStringifyWebStream(value, optionsOrReplacer?, space?)`

**Import path:** package root.

**Signatures:**

```ts
createStringifyWebStream(value: unknown, replacer?: Replacer, space?: Space): ReadableStream<string>;
createStringifyWebStream(value: unknown, options: StringifyOptions): ReadableStream<string>;
```

Return a Web `ReadableStream` over `stringifyChunked` output. Preserve the
generator's chunk boundaries and options. Closing the generator closes the
stream. Cancelling the reader stops future generation; a later read resolves
with `{ value: undefined, done: true }`.

# Implementation Notes

- Keep the package implementation independent of network access, current time,
  random state, filesystem configuration, and environment variables.
- Preserve JavaScript object key order and the native `JSON.parse`/
  `JSON.stringify` semantics explicitly referenced above.
- UTF-8 byte counts differ from JavaScript string lengths for non-ASCII text.
  Lone UTF-16 surrogates serialize as escaped `\uXXXX` sequences; valid pairs
  count as their four-byte UTF-8 scalar.
- Streaming APIs must process supplied chunks incrementally. Do not concatenate
  all input or output solely to call the native JSON method; bounded examples
  are small, but the required behavior is intended for large datasets.
- The verifier imports only the fixed package and invokes it in an unprivileged
  subprocess. It validates operation names, package entries, request shape,
  nesting depth, chunk sizes, and response size before recording results.
