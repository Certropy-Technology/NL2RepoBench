# Project Description

Build an installable ESM npm package named `get-stream` from an empty workspace.
It consumes a Node.js `Readable`, a Web `ReadableStream`, or an async iterable and
returns the complete contents as text, a Node `Buffer`, an `ArrayBuffer`, or an
array of original chunks.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- Package name `get-stream`, version `9.0.1`, and an ESM package root export.
- A committed npm lockfile with `lockfileVersion: 3`; installation and packing
  must work with lifecycle scripts disabled and no runtime network access.
- Runtime dependencies may use the exact frozen versions of
  `@sec-ant/readable-stream` and `is-stream`, or an equivalent dependency-free
  implementation of the documented behavior.
- A JSON-safe evaluator boundary: hidden checks invoke the four package exports
  with deterministic Node streams, Web streams, async iterables, and serializable
  chunks. Do not add a CLI or fetch external data.

# API Usage Guide

The package root must export the following functions and class from ESM:

`default getStream(stream, options?): Promise<string>`

Read a stream as UTF-8 text. Accept a Node `Readable`, a Web `ReadableStream`, or
an async iterable. String chunks are concatenated directly. `Buffer`,
`ArrayBuffer`, `DataView`, and typed-array chunks are decoded as UTF-8 with a
streaming decoder, so a multi-byte character split across chunks is decoded once.
Other object-mode chunks are rejected. A non-stream first argument must reject
with a `TypeError` whose message identifies the accepted stream forms.

`getStreamAsBuffer(stream, options?): Promise<Buffer>`

Read the same supported stream forms as a Node `Buffer`. Strings are UTF-8
encoded; binary chunks preserve their bytes, including typed-array byte offsets.
Object-mode chunks are rejected. This export is Node-only and must return a
primitive `Buffer` instance.

`getStreamAsArrayBuffer(stream, options?): Promise<ArrayBuffer>`

Read text as UTF-8 bytes and preserve bytes from `Buffer`, `ArrayBuffer`,
`DataView`, and typed-array chunks. Return an `ArrayBuffer` containing exactly
the consumed bytes, not the unused portion of a larger backing buffer.

`getStreamAsArray(stream, options?): Promise<unknown[]>`

Read any supported stream or async iterable into an array. Preserve each chunk
as a separate element and preserve object identity and values in object mode.
This is the only output method that accepts arbitrary object chunks.

`MaxBufferError`

Export a class named `MaxBufferError` extending `Error`. Each method accepts an
optional `{maxBuffer?: number}`. The limit is measured in characters for text,
bytes for `Buffer` and `ArrayBuffer`, and elements for arrays. If the limit is
exceeded, reject with `MaxBufferError`, stop consuming, and expose the data
accepted before the limit as `error.bufferedData` in the method's output type.

All methods return promises, preserve deterministic chunk order, do not mutate
caller-owned buffers or arrays, and call an async iterable's cleanup protocol
when consumption fails. Stream failures must be rethrown while retaining the
already buffered data on `error.bufferedData`. Normal completion of an already
ended Node or Web stream must return its empty or accumulated contents.

# Implementation Notes

Use ESM (`"type": "module"`) with a package-root `exports` map that exposes the
default function, named functions, and `MaxBufferError`. Keep the public package
free of tests and verifier files. The evaluator runs with `TZ=UTC`, one CPU,
no network, and a bounded workspace. Do not rely on the upstream repository,
GitHub, npm registry, a custom loader, or a development-only test framework at
runtime.
