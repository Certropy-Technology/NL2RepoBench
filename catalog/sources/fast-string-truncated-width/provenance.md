# `fast-string-truncated-width` authoring provenance

Status: `controls-passed`; ready for independent review and later model Agent
Run by the separate campaign loop.

## Source and license freeze

- Upstream: `https://github.com/fabiospampinato/fast-string-truncated-width`.
- Frozen revision: `1d50ce0c1497c1399eed50f87926817587049358`.
- Commit tree: `1b2b80d0f4ed708130028adf3093e0ea8313882a`.
- Commit timestamp: `2026-07-16T14:48:39+01:00`.
- Raw `git archive --format=tar` SHA-256:
  `910a980a127ca70626d2bc0dbe673601e7c65c8778548cd1c3f94472c59c2f79`
  (51,200 bytes, 16 entries, no submodules).
- Root license and `package.json` declare MIT. The license bytes hash to
  `2547dead17a32b1e49a588e943d52420b4d75f1349d9afd9ecb567b2dc8911c0`.

The Oracle solution fetches only this exact revision, asserts `FETCH_HEAD`,
recreates the raw archive, and verifies the archive digest before compiling.
The source hostname is not present in task metadata and is authorized only by
the Oracle run command.

## API and test inventory

- Package: ESM `fast-string-truncated-width@3.0.3`; no runtime dependencies.
- Public runtime surface: one default synchronous function.
- Public type surface: `TruncationOptions`, `WidthOptions`, and `Result`.
- Upstream framework: Fava through Tsex. The source has 19 test groups: 18
  executable and one skipped live-network emoji-data test.
- Locked-image baseline: 18 passed, 0 failed, 1 skipped. Two subsequent
  `--network none` compile/test runs produced the same result and identical log
  bytes.
- Production verifier: 39 unique `node:test` leaves covering only the public
  contract. Its isolated reference probe passed 39/39.

## Environment and dependency closure

- Runtime image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64,
  glibc.
- Runtime dependency closure: empty.
- Build-only dependency: exact `typescript@5.9.3`, Apache-2.0, integrity
  `sha512-jl1vZzPDinLr9eUt3J/t7V6FgNEw9QjvBPdysz9KfQDD41fQrC2Y4vKQdiaUpFT4bXlb1RHhLpp8wtm6M5TgSw==`.
- Private npm v3 closure:
  `sha256:ebe44b6d18ad6a44b8f600889a1d1e6e4312fb327351562dd1f75902b7e07e14`
  (19,998,720 bytes). It contains one lock entry, four cache files, and
  per-file SHA-256 records.
- Repository validation and a clean `npm ci --offline --ignore-scripts` probe
  passed with Docker networking disabled.

The Oracle performs only a packaging adaptation: it adds `.js` to two relative
TypeScript import specifiers, compiles with exact TypeScript 5.9.3, and removes
the build dependency and source-only files. Its four principal `dist` outputs
are byte-identical to the upstream Tsex baseline.

## Verifier boundary and private artifacts

- Separate verifier, `network_mode: none`, candidate UID `10001`.
- Trusted `node:test` never imports candidate code. Candidate calls execute in
  bounded one-shot child processes with an allowlisted JSON protocol.
- Dependency bundle:
  `sha256:ebe44b6d18ad6a44b8f600889a1d1e6e4312fb327351562dd1f75902b7e07e14`.
- Command-plan bundle:
  `sha256:a832562812d78324c3ac1b16a15a9ab97c6e9e92ad7de119f2da7bb997be8661`.
- Private test bundle:
  `sha256:f5296544f016a363a96c94090987304b119d1ef451314d53f8ac7dc7eb08c3f9`.
- Oracle bundle:
  `sha256:2988312115f70e5f8b7adb941b18eaa55bff738964057cf0edf9d7006ae595da`.

Full authoring logs and CAS objects remain under task-local `.nl2repo/` and are
not copied into the public source directory.

## Production gates

- Source validation passed.
- Full source network lint passed with zero task-local findings.
- Production compile with `toolchain.node.lock.toml`, task-local private CAS,
  and `--allow-private` passed without `--allow-incomplete`.
- Harbor `0.21.0` Oracle passed `39/39`, reward `1.0`, and reported
  `public_network_available=false`.
- Empty was the permitted `0/0` candidate-installation exception; stub and
  forgery each scored `2/39`; install-script was rejected during candidate
  installation; loader-hook scored `2/39` without activating its loader;
  bounded hang terminated as `candidate-call-failed`; oversized output and the
  active offline-fetch package each scored `1/39`.
- Every control network receipt reported `public_network_available=false`.

No model Agent Run, blind/spec review, dataset projection, or publication step
was performed in this lane.

## Final production revalidation

- Final task-local compile: `.nl2repo/compiled/fast-string-truncated-width-production-final/fast-string-truncated-width`;
  bundle manifest SHA-256 `f6cf85d3af1221a040ceeb2609d59867d5555a78536daa420a3bd84372d5750f`,
  canonical manifest digest `06999a1f4c62d761401874f10d134d509a8b95ea776b469832960658f1db9c55`,
  86 manifest entries.
- Fresh final Oracle on that bundle passed 39/39 with reward 1.0 and
  `public_network_available=false`.
- Fresh final controls on task-local prepared bundles: empty 0/0 installation
  exception; stub 2/39; forgery 1/39 with verifier-owned reward; hang bounded
  as candidate-call-failed; install-script rejected during installation;
  loader-hook 2/39; oversized-output 0/39; offline 1/39. Every final control
  returned `public_network_available=false`.
