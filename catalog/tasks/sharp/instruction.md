# Build `sharp`

## Project Description

Create an installable npm package named `sharp`, version `0.35.3`, from an
empty workspace. It is a CommonJS-and-ESM image processing package backed by
the frozen Linux x64 libvips runtime described below. The scored production
slice covers package shape, static runtime metadata, raw/create inputs,
deterministic transforms, buffer encoders, and parameter errors.

Reproduce the specified observable behavior with your own package files. This
is repository generation, not a request to retrieve the pinned upstream source
or hidden tests.

## Supports

- Run on Node `24.19.0`, npm `11.17.0`, `linux/amd64`, and glibc.
- Use `"type": "commonjs"` and expose the package root through exactly this
  dual-mode map:

  ```json
  {
    "main": "./dist/index.cjs",
    "types": "./dist/index.d.mts",
    "exports": {
      ".": {
        "import": {
          "types": "./dist/index.d.mts",
          "default": "./dist/index.mjs"
        },
        "require": {
          "types": "./dist/index.d.cts",
          "default": "./dist/index.cjs"
        }
      }
    }
  }
  ```

- Both root modes export the callable `sharp` constructor as their default
  value. `require("sharp")` returns the function directly; ESM default import
  returns the same API.
- Include only `dist` in the package `files` list. Include runtime JavaScript
  and both `.d.cts` and `.d.mts` declarations. Do not require a build step
  after installation.
- Set `engines.node` to `>=20.9.0`, `license` to `Apache-2.0`, and
  `config.libvips` to `>=8.18.3`.
- Include a v3 `package-lock.json` that agrees with `package.json`. Pin exactly
  these five runtime dependencies:

  ```json
  {
    "@img/colour": "1.1.0",
    "@img/sharp-libvips-linux-x64": "1.3.2",
    "@img/sharp-linux-x64": "0.35.3",
    "detect-libc": "2.1.2",
    "semver": "7.8.5"
  }
  ```

  The verifier owns an integrity-checked npm cache and runs:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The two `@img/sharp-*` packages are the only native/platform dependencies.
  They are fixed to Linux x64 glibc and installed by the verifier with scripts
  disabled. Do not add a native binary, `binding.gyp`, prebuild directory,
  install hook, download helper, or another platform package to your package.
- Do not add `preinstall`, `install`, `postinstall`, `prepare`, `prepublish`,
  `prepublishOnly`, `publish`, or `postpublish` scripts. Do not use workspaces,
  custom loaders, registry configuration, or network access.
- Do not add hidden tests, a grader, reward files, Oracle files, npm cache
  bytes, credentials, or private verifier material to the candidate repository.

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

These utility calls are synchronous. The verifier starts a fresh bounded child
process for each call, so mutable global tuning state is not transported
between scored calls.

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

## JSON Boundary and Determinism

The verifier-owned adapter maps JSON create/raw records to real `Buffer` and
sharp calls. Raw bytes cross as lowercase hexadecimal. Successful metadata and
output info cross as plain JSON; encoded buffers cross only as a bounded prefix
and SHA-256 receipt. Errors cross as bounded name/message records. The adapter
is not a candidate CLI or export requirement.

Inputs are limited to JSON null, booleans, finite numbers, strings, arrays, and
plain objects. Functions, callbacks, streams, paths, URLs, BigInts, symbols,
custom prototypes, cycles, file handles, and arbitrary native handles are
outside the scored transport. Each call runs as UID 10001 with a 30-second
timeout, bounded output, no network, and no inherited loader/proxy settings.

## Production Slice

The frozen 31-leaf `node:test` slice covers package and dependency shape,
runtime versions/capabilities, static utilities, create/raw metadata, exact raw
pixels for geometry/channel operations, PNG/JPEG/WebP signatures, and invalid
input behavior. The full upstream suite is authoring evidence, not the scored
denominator: on the frozen Node/libvips runtime it collected 1,822 leaves and
passed 1,820; its two environment-sensitive failures concern animated GIF page
limiting and TIFF SUBIFD decoding outside this public production slice.
