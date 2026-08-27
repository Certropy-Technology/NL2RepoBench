# Node/npm Foundation Status

> **Dated evidence snapshot, not a current contract.** Current runtime/schema
> behavior is defined by `runtime-adapter-architecture.zh-CN.md` and the actual
> CLI/compiler. The values below preserve the Node foundation gate that was run.

The historical Node/npm synthetic foundation remains development-only; the
production lane is now a separate Node 24 toolchain lock.

- Synthetic development validation remains Node `22.23.1` / npm `10.9.8`.
- `toolchain.node.lock.toml` now locks production Node `24.19.0` / npm `11.17.0`,
  Harbor `0.21.0`, schema `1.4`, and a pure Node helper/grader tree digest.
- The official Node 24 `linux/amd64` manifest is pinned as
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- `toolchain.node.dev.lock.toml` preserves the old synthetic Node 22 development
  fixture and must not be used for production tasks.

## Production Vertical Slice

- Candidate: `canonicalize`, exact source revision
  `c1b08c3771d681c8bd9c4d8765e00f2f717482f8`.
- Production compile uses Node 24.19.0/npm 11.17.0 and the private npm v3
  offline closure; `uv run nl2repo harbor compile ... --toolchain
  toolchain.node.lock.toml --allow-private` passed.
- One Oracle run passed: `valid=true`, `10/10` collected/passed, reward `1.0`.
- Node controls passed: empty, stub, forgery, install-script, loader-hook,
  hang, and offline. Machine-readable evidence is in
  `reports/node-canonicalize-production-gate.v1.json`.

## Development E2E evidence

- Harbor `0.21.0`, task schema `1.4`, Docker Compose `5.4.0`.
- Three independent Oracle trials: `3/3`, `valid=true`, reward `1.0`, collection `8`.
- Empty `nop` control: reward `0.0`, model failure `candidate-installation-failed`.
- The E2E bundle used `--allow-incomplete`; these results do not establish production
  publication or Python/Node score parity.
- The synthetic task is excluded from every Python dataset and is never used for a
  Python/Node score parity claim.

The synthetic foundation alone did not establish production readiness; the
separate production vertical-slice evidence above did.
