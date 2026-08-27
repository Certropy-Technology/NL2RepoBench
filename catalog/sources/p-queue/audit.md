# `p-queue` Authoring Audit

Status: `controls-passed` pending independent review and a later model pilot.
This task is a bounded 46-leaf behavioral contract, not a claim of full
upstream parity.

## Frozen Source

- Upstream: `https://github.com/sindresorhus/p-queue`.
- Revision: `180ab9e25cd10b6f548767d7176076b50d25e188` (`9.3.3`).
- Tree: `e8e63896c7368b45ead03441d007c76f2b2591e5`.
- `git archive --format=tar` SHA-256:
  `2dd1f460de3562b9c6b84f6de66ecf722ed52730dfcc877c02b6f9731351e79b`.
- No submodules or mutable source references.
- MIT license; root `license` SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.

## Baseline And Build

The exact source was exercised in
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
(Node `24.19.0`, npm `11.17.0`, Debian bookworm, glibc `2.36`). The source does
not commit a lock and sets `package-lock=false`; authoring therefore generated
a clean npm v3 development lock, populated its cache, and ran three separately
extracted no-network baselines:

```text
npm ci --offline --package-lock=true --ignore-scripts --no-audit --no-fund
npm run build
npm test
```

All three exited 0 with 206/206 runtime `node:test` leaves plus the upstream
lint, TypeScript build, and declaration tests. Generated `dist/` bytes were
identical across all three runs. Full logs and hashes are under the task-local
`.nl2repo/authoring-work/node-discovery-20260826-r1/p-queue/evidence/` tree.

## Runtime Closure

The distribution has exactly two runtime packages:

```text
eventemitter3 5.0.4
p-timeout      7.0.1
```

The production npm bundle contains a root-only v3 lock, eight cache files, and
an exact manifest of every regular file. A clean Node 24 container installed
the closure with `--network none` and imported both packages. Lifecycle scripts
are ignored and the closure contains no native or platform package.

## Verifier Boundary

The separate verifier freezes 46 deterministic `node:test` leaves. A trusted
test client starts candidate code as UID 10001 in a bounded child. Requests are
allowlisted JSON queue scenarios; source text and executable values never cross
the process boundary. The contract covers package shape, scheduling,
concurrency, pause/start, priorities, waiters, clearing, events, rejection,
timeouts, cancellation, fixed/sliding interval limits, `PriorityQueue`, and
validation errors.

Detailed assertion-to-spec traceability and the hidden adapter remain in
task-local private evidence. The public instruction discloses every behavior
required by those assertions without copying upstream implementation or tests.

## Private Artifacts

```text
npm closure  sha256:a5b2e71f921ab4178915df8c9f97e28f7f249afdc0e7da9fdaca9390e9709629  204800 bytes
commands     sha256:a832562812d78324c3ac1b16a15a9ab97c6e9e92ad7de119f2da7bb997be8661   10240 bytes
tests        sha256:c6b3310a0d30b62a2213516abd0baaaa1dc2f75a946e2e253c1a11ae90b08948   40960 bytes
Oracle       sha256:8d2e87d889edae1564656cac5f22984d7a2f282543589dd34386901dea39ecb0  317440 bytes
```

The Oracle bundle contains the digest-verified frozen source archive and the
reproducible scripts-free `dist/` adaptation. It is available only to the
trusted Oracle solution, never to the model image. Both normal task metadata
and the generated agent environment are `no-network`; allowed hosts are empty.

## Production Gates

Production source validation, network lint, compile, final Oracle, empty,
stub, forgery, timeout, and offline outcomes are recorded in
`production-evidence.json`. No Harbor model Agent Run was started. Blind review
and pilot execution remain integration-stage work.
