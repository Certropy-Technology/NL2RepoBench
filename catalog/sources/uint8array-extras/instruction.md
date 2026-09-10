# Project Description

Implement `uint8array-extras@1.5.0`, a dependency-free ESM package of deterministic utilities for `Uint8Array`, `ArrayBuffer`, `DataView`, text, Base64, hexadecimal, and byte-subsequence operations.

# Supports

- Node.js 24.x on Linux amd64 with `"type": "module"`.
- Package name `uint8array-extras`, version `1.5.0`, with no runtime dependencies or lifecycle scripts.
- The package root exposes the 18 named functions below and no default export.

# API Usage Guide

- `isUint8Array(value: unknown): value is Uint8Array` returns true for `Uint8Array` and `Buffer`, false otherwise.
- `assertUint8Array(value: unknown): asserts value is Uint8Array` accepts only `Uint8Array`; otherwise throws `TypeError`.
- `assertUint8ArrayOrArrayBuffer(value: unknown): asserts value is Uint8Array | ArrayBuffer` accepts either supported type; otherwise throws `TypeError`.
- `toUint8Array(value: TypedArray | ArrayBuffer | DataView): Uint8Array` returns a byte view over the same data, respecting view offsets; unsupported values throw `TypeError`.
- `concatUint8Arrays(arrays: Uint8Array[], totalLength?: number): Uint8Array` concatenates in order, returns an empty array for no inputs, and uses an explicit destination length when supplied.
- `areUint8ArraysEqual(a, b): boolean` compares lengths and bytes. `compareUint8Arrays(a, b): 0 | 1 | -1` compares unsigned bytes lexicographically, then length.
- `uint8ArrayToString(array, encoding = 'utf8'): string` decodes a byte array or ArrayBuffer with `TextDecoder`. `stringToUint8Array(string): Uint8Array` UTF-8 encodes a string.
- `uint8ArrayToBase64(array, {urlSafe = false}): string` encodes bytes; URL-safe mode uses `-` and `_` without padding. `base64ToUint8Array(string)` accepts padded Base64 and unpadded Base64URL. `stringToBase64` and `base64ToString` compose these operations with UTF-8.
- `uint8ArrayToHex(array): string` returns lowercase two-digit hexadecimal. `hexToUint8Array(string)` accepts either case, rejects odd lengths with `Invalid Hex string length.`, and rejects invalid characters with an `Invalid Hex character` error.
- `getUintBE(view): number` reads 1 through 6 bytes from a DataView as an unsigned big-endian integer and returns `undefined` for other lengths.
- `indexOf(array, value): number` returns the first byte-sequence index or `-1`; `includes(array, value): boolean` returns the corresponding membership result. Empty needles return `-1`/`false`.

# Implementation Notes

Use platform APIs and standard JavaScript only. Do not mutate caller arrays, preserve view boundaries, keep results deterministic, and provide matching `index.d.ts` declarations including `TypedArray`. The package must install from an empty workspace with npm offline and must not require a build step.
