# Project Description

Create an installable npm package named `sharp`, version `0.35.3`, from an
empty workspace. It is a CommonJS-and-ESM image processing package backed by
the frozen Linux x64 libvips runtime described below. The scored production
slice covers package shape, static runtime metadata, raw/create inputs,
deterministic transforms, buffer encoders, and parameter errors.

Reproduce the specified observable behavior with your own package files. This
is repository generation, not a request to retrieve the pinned upstream source

## Natural Language Instruction

Create `sharp` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `sharp`. Primary import or package entry: `sharp`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: @img/colour, @img/sharp-libvips-linux-x64, @img/sharp-linux-x64, detect-libc, semver. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `31` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── lib/
    ├── constructor.js
    ├── input.js
    ├── operation.js
    ├── output.js
    └── utility.js
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### Constructor and input

**Import path:** the package root default value.

```js
const sharp = require("sharp");
// or: import sharp from "sharp";
```

**Signatures:**

```ts
sharp(options?: SharpOptions): Sharp
sharp(input?: SharpInput | SharpInput[], options?: SharpOptions): Sharp
```

The scored boundary uses deterministic in-memory inputs only:

- `create`: `{ create: { width, height, channels, background } }`, where
  width and height are positive integers, channels is `3` or `4`, and
  background is a CSS colour string or `{r, g, b, alpha?}` object.
- `raw`: a `Buffer` plus `{ raw: { width, height, channels } }`, where channels
  is `1..4` and the buffer contains exactly `width * height * channels`
  unsigned 8-bit bytes in row-major interleaved channel order.

Created and raw images have format `raw`, depth `uchar`, and sRGB/greyscale
metadata appropriate to their channels. A three-channel created image has no
alpha; a four-channel created image has alpha. An alpha of `0.5` supplied to a
create background becomes byte `128`; an alpha of `0.5` supplied to
`ensureAlpha` becomes byte `127`, matching the frozen implementation's
conversion paths.

### Static properties and utilities

The constructor exposes:

- `versions.sharp === "0.35.3"` and `versions.vips === "8.18.3"`;
- `format` capability records. JPEG, PNG, WebP, and GIF all accept buffer input
  and support buffer output in this runtime;
- enum objects including `fit.cover`, `fit.contain`, `kernel.lanczos3`, and
  `gravity.centre === 0`;
- `cache()` returning `{memory, files, items}` records with numeric current/max
  counters;
- `concurrency()` returning a positive integer; and
- `simd()` returning a boolean.

These utility calls are synchronous. Keep mutable tuning state explicit and
avoid relying on unrelated process-global state between calls.

### `metadata()`

```ts
metadata(): Promise<Metadata>
```

For the in-memory inputs above, return format, dimensions, colour space,
channel count, depth, alpha/profile/progressive flags, and other applicable
metadata. Examples:

```js
await sharp({ create: { width: 3, height: 2, channels: 3, background: "red" } }).metadata()
// includes {format: "raw", width: 3, height: 2, space: "srgb",
//           channels: 3, depth: "uchar", hasAlpha: false,
//           hasProfile: false, isProgressive: false}
```

```js
await sharp(Buffer.from("ff000000ff00", "hex"), {
  raw: { width: 2, height: 1, channels: 3 }
}).metadata()
// includes {format: "raw", width: 2, height: 1, channels: 3}
```

### Geometry

All methods return the same chainable `Sharp` instance.

```ts
resize(options: ResizeOptions): Sharp
rotate(angle?: number, options?: RotateOptions): Sharp
flip(): Sharp
flop(): Sharp
extract(options: {left: number, top: number, width: number, height: number}): Sharp
```

- `resize({width, height, fit, kernel, position, background})` implements
  `fill`, `contain`, and `cover`. `nearest` preserves exact source pixels.
  `contain` pads with the requested background and `cover` crops by position.
- `rotate(90)` swaps width and height and rotates clockwise.
- `flip()` reverses rows vertically; `flop()` reverses columns horizontally.
- `extract()` selects the exact zero-based rectangle and rejects out-of-range
  geometry.

For example, a `3x1` RGB row containing red, green, and blue, resized to `1x1`
with `fit: "cover"`, `position: "centre"`, and `kernel: "nearest"`, yields the
green pixel.

### Channel and pixel operations

```ts
ensureAlpha(alpha?: number): Sharp
removeAlpha(): Sharp
greyscale(): Sharp
negate(options?: {alpha?: boolean}): Sharp
threshold(value?: number, options?: {greyscale?: boolean}): Sharp
linear(a?: number | number[], b?: number | number[]): Sharp
flatten(options?: {background?: string | object}): Sharp
blur(options?: number | BlurOptions): Sharp
sharpen(options?: number | SharpenOptions): Sharp
tint(colour: string | object): Sharp
modulate(options?: ModulateOptions): Sharp
```

- `ensureAlpha` adds an alpha channel; `removeAlpha` drops it.
- `greyscale` converts to one-channel output when followed by `raw()`.
- `negate` inverts colour bytes, so RGB `0a141e` becomes `f5ebe1`.
- `threshold(100, {greyscale: true})` maps values below 100 to black and values
  at or above 100 to white. Raw output is three-channel RGB.
- `linear([2,2,2], [1,1,1])` maps RGB `0a141e` to `15293d`, clamping to byte
  range.
- `flatten({background: "#0000ff"})` composites alpha onto blue and removes the
  alpha channel.
- Blur, sharpen, tint, and modulate follow the documented sharp chain semantics
  and validate their option domains even when they are not used in an exact
  byte example.

### Buffer output

```ts
raw(options?): Sharp
png(options?): Sharp
jpeg(options?): Sharp
webp(options?): Sharp
toBuffer(options?: {resolveWithObject?: boolean}): Promise<Buffer | {data: Buffer, info: OutputInfo}>
```

- `raw().toBuffer({resolveWithObject: true})` returns interleaved bytes and
  `info` with `format`, dimensions, channels, size, and premultiplication.
- PNG output starts with the standard `89504e470d0a1a0a` signature.
- JPEG output starts with `ffd8ff`.
- WebP output is RIFF data whose bytes 8 through 11 are `WEBP`.
- Output info reports the selected format and actual dimensions/channels.
  Encoding is local and does not contact a service.

### Errors

Invalid dimensions, raw byte length, transform geometry, method options, and
encoder options must reject deterministically rather than crash or hang.
Examples include a non-positive resize width and JPEG quality outside `1..100`.
Preserve the upstream distinction among `TypeError`, `RangeError`, and ordinary
`Error` where specified by the API. Exact wording is checked only for the
documented sharp parameter phrase, such as `Expected positive integer for width`.

### JSON Boundary and Determinism

sharp calls. Raw bytes cross as lowercase hexadecimal. Successful metadata and
output information must remain representable through the documented public
return values. Errors should retain their documented names and messages; no
additional CLI or export is required.

Inputs are limited to JSON null, booleans, finite numbers, strings, arrays, and
plain objects. Functions, callbacks, streams, paths, URLs, BigInts, symbols,
custom prototypes, cycles, file handles, and arbitrary native handles are
outside the scored transport. Each call runs as UID 10001 with a 30-second
timeout, bounded output, no network, and no inherited loader/proxy settings.

### Production Slice

The frozen 31-leaf `node:test` slice covers package and dependency shape,
runtime versions/capabilities, static utilities, create/raw metadata, exact raw
pixels for geometry/channel operations, PNG/JPEG/WebP signatures, and invalid
input behavior. The full upstream suite is authoring evidence, not the scored
denominator: on the frozen Node/libvips runtime it collected 1,822 leaves and
passed 1,820; its two environment-sensitive failures concern animated GIF page
limiting and TIFF SUBIFD decoding outside this public production slice.

## Implementation Notes

Preserve all public return shapes, ordering, state transitions, and exception contracts described above. Keep installation metadata and public imports consistent and deterministic.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
const sharp = require("sharp");
// or: import sharp from "sharp";
```

```javascript
sharp(options?: SharpOptions): Sharp
sharp(input?: SharpInput | SharpInput[], options?: SharpOptions): Sharp
```

```javascript
metadata(): Promise<Metadata>
```

```javascript
await sharp({ create: { width: 3, height: 2, channels: 3, background: "red" } }).metadata()
// includes {format: "raw", width: 3, height: 2, space: "srgb",
//           channels: 3, depth: "uchar", hasAlpha: false,
//           hasProfile: false, isProgressive: false}
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
