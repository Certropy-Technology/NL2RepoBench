# `p-map` Authoring Provenance

## Frozen source

- Upstream: `https://github.com/sindresorhus/p-map`
- Requested and resolved revision:
  `bc26cf03f81292325236a1188063dac8e7a4de0f`
- Tree: `10297443b80a2322fe5711512aaf47af409c33f3`
- Commit subject: `7.0.6`
- Author and commit time: `2026-07-20T23:20:30+02:00`
- Submodules: none
- `git archive --format=tar <revision>` size: `61,440` bytes
- Archive SHA-256:
  `dca5fc93afc8590a18952c091d5929dfce1f175ad5517b6312b0fe6f5ae84062`

The package metadata declares `p-map` version `7.0.6`, ESM, Node `>=18`, and
MIT. The tracked `license` file contains the MIT text and has SHA-256
`5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
The declaration and file agree.

## Public API inventory

The root implementation is `index.js` (7,204 bytes, Git blob
`6948b828f255afc5b2847ff8ebd8e85b271cc3ed`, SHA-256
`7ad50a54ad1a52c120590e00fa0b2f66eca365ca3e093f1d1c25b2b6334f52d5`).
The root declaration is `index.d.ts` (6,245 bytes, Git blob
`be21e769a8726bc3070d77b9477ab4e0b4a7bbfb`, SHA-256
`69de0ba2ccff2e655e19f0402afb37547e0fe17e40b2fedbf49cec2bc8816f03`).

The public surface has three exports:

| Export | Kind | Contract |
| --- | --- | --- |
| `default` / `pMap` | async function | Map iterable or async iterable input with concurrency, skip, error, and abort options. |
| `pMapIterable` | function returning `AsyncIterable` | Stream ordered mapper results with concurrency and backpressure. |
| `pMapSkip` | symbol | Sentinel that omits a mapper result. |

The package has no runtime dependencies. The frozen repository has no lockfile;
its `.npmrc` disables package-lock generation. The production candidate closure
therefore uses a reviewed root-only npm v3 lock and empty integrity-checked
cache. Development dependencies are authoring-only and are not present in the
agent or verifier runtime closure.

## Source baseline

The pinned digest image is
`node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
with Node `24.19.0` and npm `11.17.0`. A network-backed authoring install used
`npm install --ignore-scripts --no-audit --no-fund` to materialize only the
development test environment. All corrected baselines then ran with Docker
`--network none`:

```text
npm test  # xo && ava && tsd
run 1: exit 0, 51 AVA leaves passed, xo passed, tsd passed
run 2: exit 0, 51 AVA leaves passed, xo passed, tsd passed
run 3: exit 0, 51 AVA leaves passed, xo passed, tsd passed
```

An initial read-only bind also passed all 51 AVA leaves but AVA exited nonzero
after failing to create `node_modules/.cache/ava`. That was an authoring mount
configuration error. The corrected writable, no-network runs above establish
the source baseline.

The two JavaScript suites contain 49 direct AVA declarations: 21 core `pMap`,
15 asynchronous-input, 12 `pMapIterable`, and one performance leaf. AVA reports
51 leaves because two declarations contain multiple independently reported
assertion branches. The separate `index.test-d.ts` declaration suite passed
through `tsd`.

## Production adaptation

The production verifier freezes 54 `node:test` leaves. A private adapter
constructs only fixed JSON-safe mapper behaviors, promises, iterable forms,
abort signals, and the exported skip sentinel inside an unprivileged child.
The trusted tests never import candidate code. Exact timing windows,
randomized delays, declaration-level generic inference, and the large
algorithmic performance case are not scored.

The Oracle privately carries the exact 61,440-byte Git archive, verifies its
SHA-256, and projects only `index.js`, `index.d.ts`, and `license` into a
runtime-only package manifest and root lock. The archive and solution are
private compiler artifacts and never enter the model agent image.
