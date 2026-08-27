# Build `@jsonjoy.com/buffers`

## Project Description

Create a complete installable CommonJS npm package named `@jsonjoy.com/buffers`,
version `18.28.0`, from an empty workspace. It provides deterministic utilities
for binary data, UTF-8 text, numeric binary readers/writers, and chunked stream
readers. The package is designed to work with both `Uint8Array` and Node
`Buffer` values.

This is a repository-generation task. Implement the behavior below with your own
source files. Do not copy the reference repository or its tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- CommonJS package semantics. The package root must be importable with
  `require('@jsonjoy.com/buffers')`; implementation modules are available below
  `lib/` using the same relative module names as the APIs listed below.
- A committed npm v3 lockfile must make the package installable with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Runtime dependency `tslib` must be declared and pinned. TypeScript and Node
  type definitions may be development dependencies used to build the package.
  Do not use git, file, workspace, native-addon, or network dependencies.
- The scored behavior is deterministic and local. Benchmarks, browser-only
  integration, and the optional native `json-pack-napi` UTF-8 experiment are
  outside this task.

## API Usage Guide

### Array and byte utilities

- `require('@jsonjoy.com/buffers/lib/b').b(...octets)` returns a new
  `Uint8Array` containing the supplied numeric octets in order.
- `concat(a, b)` returns a new array containing `a` followed by `b`.
  `concatList(list)` concatenates every array in order. `listToUint8(list)`
  returns an empty array for an empty list, the original member for a one-item
  list, and a concatenated copy otherwise.
- `copy(arr)` returns a new array with the same bytes and does not alias the
  input.
- `cmpUint8Array(a, b)` returns a boolean for byte equality. `cmpUint8Array2`
  compares bytes lexicographically and uses length as the tie breaker.
  `cmpUint8Array3` compares length first and bytes second; each returns a
  negative, zero, or positive number.
- `toUint8Array(data)` accepts an existing `Uint8Array`, an `ArrayBuffer`, an
  array of octets, or a Node `Buffer`, and returns the corresponding byte view
  or copy. Incompatible values throw `UINT8ARRAY_INCOMPATIBLE`.
- `bufferToUint8Array(buf)` returns a view over the same memory as a Node
  `Buffer`, preserving its byte offset and length. `isUint8Array(value)` and
  `isArrayBuffer(value)` are type predicates.
- `printOctets(octets, max = 16)` formats bytes as lower-case, two-digit
  hexadecimal separated by spaces. If more than `max` bytes exist it appends
  `… (N more)`.
- `decodeF16(binary)` decodes an IEEE-754 half-precision bit pattern to a
  JavaScript number, including signed values, infinities, and NaN.
- `isFloat32(number)` returns true exactly when storing the number as float32
  and reading it back produces the same number.

### Text and UTF-8 utilities

- `ascii(text)` converts a string (or one-element template-string array) to
  one byte per UTF-16 code unit, retaining the low eight bits. `utf8(text)`
  converts the string to UTF-8 bytes.
- `toBuf(text)` returns UTF-8 bytes as a `Uint8Array`.
- `decodeAscii(bytes, position, length)` returns an ASCII string for the slice,
  or `undefined` when the requested bytes contain a value above `0x7f`.
- `decodeUtf8(bytes, start, length)` decodes exactly the selected byte range as
  UTF-8. `isUtf8(bytes, from, length)` validates that range and returns a
  boolean. Invalid sequences are false for `isUtf8`; decoding follows the
  deterministic replacement behavior of the JavaScript UTF-8 decoder.
- `encode(target, text, position, maxLength)` writes at most `maxLength` UTF-8
  bytes into the target and returns the number of bytes written. It does not
  write outside the selected range.

### Reader and writer classes

`Reader`, `Writer`, `StreamingReader`, `StreamingOctetReader`, `Slice`, and
`Uint8ArrayCut` are exported classes in their matching `lib/*.js` modules.
Their public methods follow the TypeScript declarations: numeric reads and
writes use big-endian `DataView` order, cursors advance by the consumed bytes,
`Reader.slice()` shares storage with independent bounds, and out-of-bounds
streaming reads throw `RangeError('OUT_OF_BOUNDS')`. `Writer` grows its buffer,
`flush()` returns newly written bytes, and `StreamingOctetReader` reads across
chunk boundaries and supports four-byte XOR masks. Implement these classes and
their public methods even though the fixed black-box slice emphasizes the
JSON-serializable utility functions.

## Implementation Notes

- Keep the public module names and CommonJS `lib/` layout stable. Preserve
  zero-copy behavior where the API promises a view, and preserve input order.
- The package root may re-export types, but callers must be able to require the
  listed utility and class modules directly under `lib/`.
- Do not include test files, benchmark files, source maps, or the monorepo's
  workspace configuration in the published package.
- Do not fetch the upstream repository, npm registry, or any external service
  during candidate installation or verification.
