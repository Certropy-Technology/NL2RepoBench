# Project Description

Create an installable npm package named `nanoid` (version `6.0.1`) from an empty
workspace. It is a small ESM library for generating URL-friendly random string
identifiers. The package must work on Node.js 24.19.0 with npm 11.17.0 and must
not require network access at install or run time.

## Supports

- Use an ESM package (`"type": "module"`) with the package name and version
  above.
- Provide the package root export and the `nanoid/non-secure` subpath export.
- Provide the `nanoid` executable declared by the package's `bin` field.
- Commit a valid npm lockfile using lockfile version 3. The package has no
  runtime dependencies, and `npm ci --offline --ignore-scripts` must succeed.
- Do not use lifecycle scripts, native addons, network calls, loaders, or
  registry configuration. Keep the public package self-contained.

## API Usage Guide

The package root must export these named values:

### `nanoid(size = 21)`

Return a new random string made only from the exported `urlAlphabet`. The
default length is 21; `size` is converted to a signed integer in the same way
as bitwise integer coercion, so a numeric string such as `"10"` is accepted and
fractional values are truncated. Size zero returns `""`. Negative sizes must
fail promptly with a `RangeError` (an implementation may surface the runtime's
typed-array length error for an invalid negative allocation).

The secure generator must use the platform cryptographic random source and must
support IDs larger than the platform's single-request limit by filling in
bounded chunks. Calls must not reuse characters outside the URL alphabet.

### `customAlphabet(alphabet, defaultSize = 21)`

Return a generator function. The generator uses the supplied alphabet and uses
`defaultSize` when called without a size. It accepts string alphabets and
JSON-compatible arrays of characters. A one-character alphabet always returns
that character; zero size returns `""`; numeric-string and fractional sizes
follow the same integer coercion as `nanoid`. Unicode characters must remain
valid JavaScript characters in the returned string. Alphabets larger than 256
symbols must still be safe to call for size zero and must not hang.

The generated characters must be selected without introducing a measurable
modulo-bias shortcut for ordinary bounded alphabets. Repeated calls from one
generator must not return the same stale pool slice merely because a fractional
size was requested first.

### `customRandom(alphabet, defaultSize, getRandom)`

Export this factory with the same alphabet and size semantics as
`customAlphabet`, but obtain random bytes by calling the supplied
`getRandom(byteCount)` function. The returned generator must honor rejection
sampling for non-power-of-two alphabets and must work for power-of-two
alphabets. A zero-size request returns `""` without requiring random bytes.

### `random(bytes)`

Return a `Uint8Array` containing exactly the requested number of cryptographic
random bytes. Large requests may be split into multiple platform calls.
Negative sizes must fail promptly with a `RangeError` or an equivalent invalid
typed-array length error; ordinary non-negative sizes return bytes in the
inclusive range 0 through 255.

### `urlAlphabet`

Export a string of exactly 64 distinct URL-safe symbols. It must contain only
letters, digits, `_`, and `-`, and must be the alphabet used by the default
generators.

### `nanoid/non-secure`

The subpath exports `nanoid(size = 21)` and `customAlphabet(alphabet,
defaultSize = 21)`. They have the same size, alphabet, zero-size, string-size,
Unicode, and non-hanging behavior as the secure versions, but may use a
non-cryptographic random source. For this non-secure subpath specifically, a
negative requested size returns `""` promptly rather than throwing or looping.

## CLI Usage Guide

The `nanoid` executable prints one generated ID followed by a newline. Support:

- `nanoid` for the default 21-character ID;
- `--size N` / `-s N` for a positive numeric size;
- `--alphabet TEXT` / `-a TEXT` for a custom alphabet;
- `--help` / `-h` for usage text containing `Usage` and `$ nanoid [options]`;
- `--version` / `-v` for the package version followed by a newline.

Unknown options, non-numeric sizes, and non-positive CLI sizes must exit
non-zero and print a useful error containing the rejected argument or
`Size must be positive integer`. Valid CLI output must use only the requested
alphabet and requested length.

## Implementation Notes

Keep the package root importable through its declared `exports` map and keep
the subpath importable without reaching files outside the package. The verifier
will install the packed package in a clean prefix with scripts disabled, then
exercise the public exports and CLI through isolated subprocesses. Do not rely
on the repository's development tools, test files, pnpm workspace, or a
registry during evaluation.
