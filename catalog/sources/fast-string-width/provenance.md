# `fast-string-width` authoring provenance

## Frozen source

- Upstream: `https://github.com/fabiospampinato/fast-string-width`
- Revision: `f49e7b7662906e0028a68a16b5358500b2f3152d`
- Package version: `3.0.2`
- License: MIT; the tracked `license` file is retained by the Oracle source
  checkout and the package metadata declares MIT.
- Git tree: `e92a8e23f32a1ebeb646ed660750fa4802889393`
- Deterministic raw `git archive --format=tar --prefix=fast-string-width/ HEAD`
  digest: `sha256:352c8745134753593e770f0ffd8cb6e6ff2ef7f516b11ae56059f43e27d30698`.

The upstream implementation is a small ESM wrapper around
`fast-string-truncated-width`. Its only public export is the default function;
it passes a fixed no-truncation configuration to the dependency and forwards
the five width options.

## Test traceability

The private `node:test` adapter contains 24 deterministic leaves. It calls the
candidate only through the trusted `candidate_runner.mjs` boundary and never
imports candidate files into the verifier process.

| Leaves | Behavior frozen |
| --- | --- |
| basic-1..5 | empty, ASCII, ANSI CSI, ANSI reset, repeated calls |
| options-1..7 | tab, control, emoji, regular, wide, combined options, ignored truncation-looking fields |
| unicode-1..8 | family, skin tone, flag, keycap, CJK, full-width, combining mark, OSC 8 |
| contract-1..4 | numeric return, input immutability, deterministic option object, mixed string |

The denominator is the number of unique TAP leaves after collection: 24. A
collection mismatch is invalid rather than a partial score.

## Environment and dependency probes

The pinned checkout was built with Node `22.23.1`/npm `10.9.8` during
authoring after an online development install of its dev toolchain. The
production task runtime is separately locked to Node `24.19.0`/npm `11.17.0`.
The candidate runtime closure contains only the exact npm lock-resolved
`fast-string-truncated-width` package and uses `npm ci --offline
--ignore-scripts`; build/test tooling is not needed in the candidate image.

No network, filesystem, subprocess, clock, random, native addon, callback, or
external service is part of the scored API. ANSI and Unicode behavior is
bounded by the test adapter's fixed inputs and report limits.
