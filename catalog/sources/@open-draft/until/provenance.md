# `@open-draft/until` / `until-async` Provenance

- Catalog source path: `catalog/sources/@open-draft/until`
- Canonical task id: `open-draft-until` (the schema does not permit scoped npm
  punctuation in `task_id`)
- Discovery package: `@open-draft/until`
- Frozen npm package identity: `until-async@3.0.2`
- Upstream: `https://github.com/open-draft/until`
- Revision: `213f19957095cd0e4219e671c159068f451d9661`
- Git archive SHA-256:
  `45017ae63db183e97f725607cd6e01e5f543241d187b8f44407bd89372605178`
- License: MIT; LICENSE SHA-256:
  `40fa61cad189e31256c0483cf454045dbef07b098d9f02642a4e9517b3c13f59`
- Source `src/index.ts` SHA-256:
  `655e92c1944a5fd38febb94df51b531a452b267e8c3b0974d7b937e937bd6665`
- Submodules: none
- Locked runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm glibc,
  `linux/amd64`
- Base image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
- Upstream package manager: pnpm `9.15.0`, frozen `pnpm-lock.yaml` SHA-256
  `330b85028e179f232631ba98b77ffd108540856fc2ab99c3d0499ce1dce77bae`
- Candidate closure: npm `11.17.0`, root-only lockfile v3, empty cache,
  lifecycle scripts ignored

The package rename occurred at upstream commit
`231d1f838ae41511323193ce44a64695d4e9bdb4`; the claimed revision is later and
its `package.json`, README, exports, and repository metadata consistently use
`until-async`. The historical scoped package is retained only as the discovery
and source-directory identity.

## Authoring baseline

The pinned Node image installed the exact upstream pnpm lock with pnpm 9.15.0.
Vitest 3.2.6 then passed two runtime and two type-test leaves, tsdown
0.17.0-beta.1 produced ESM JavaScript and declarations, and publint 0.3.13
reported `All good!`. A second `--network none` run passed the runtime/type
tests and build directly from the installed closure; its publint subprocess
could not locate a global `pnpm` executable, an environment-only lint wrapper
limitation already covered by the successful online baseline.

The trusted Oracle fetches only the exact commit, verifies the git archive and
runtime source digest, and copies the output generated and hash-checked during
that baseline. The model Agent receives neither the Oracle bundle nor an
upstream-host allowlist.

## Authoring runtime gates (2026-08-27)

- `uv run nl2repo task validate-source
  catalog/sources/@open-draft/until` exited `0` at packaged status.
- Production compile with `toolchain.node.lock.toml`, task-local
  `.nl2repo/artifacts`, and `--allow-private` exited `0`. Its initial closed
  bundle had 79 manifest entries and zero digest mismatches.
- The generated Agent and verifier Dockerfiles built successfully. Direct
  Docker Oracle execution fetched and verified the exact source, then the
  verifier ran with `--network none` and produced `valid=true`, 18/18 passed,
  reward `1.0`, and `public_network_available=false`.
- Official Harbor `0.21.0` final-bundle Oracle trial
  `open-draft-until__a2Pfboq` exited `0`
  with no exception, 18/18 passed, reward `1.0`, and a verifier-owned offline
  network receipt. Only that Oracle invocation received run-scoped
  `--allow-agent-host github.com`.
- Direct final-bundle controls under verifier `--network none` all exited `0`:
  empty `0/0` reward `0.0`; stub and forgery `3/18` reward `1/6`; hang `2/18`
  reward `1/9`; install-script `0/0` reward `0.0`; loader-hook `3/18` reward
  `1/6`; offline `2/18` reward `1/9`. Every network receipt reported both
  DNS and numeric-IP probes unavailable. The forgery's trusted reward remained
  `1/6`, not the workspace's forged `1.0`.
- Final source validation exited `0` at `controls-passed`. Full source-root
  network lint scanned 235 tasks with zero errors, 136 unrelated warnings, and
  no finding for this task.
- A post-evidence production compile was byte-identical to the final executed
  bundle; both bundle manifest files have SHA-256
  `654a870b35ffb4fd8d7935721ed8b78ee394b9025ed62da4855635cd02657fa7`.
- Focused Node foundation, control, control-summary, and production-gate tests
  completed with `50 passed`.

These authoring controls are not a model Agent Run. Review, pilot, dataset
integration, publication, and any model capability claims remain out of scope.
