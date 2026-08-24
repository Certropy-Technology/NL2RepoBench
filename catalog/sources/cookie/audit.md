# `cookie` Node 24 Authoring Evidence

Status: `controls-passed`. This file records task-local provenance and gate
evidence. It does not claim upstream parity or dataset publication.

## Frozen Source And License

- Upstream: `https://github.com/jshttp/cookie`.
- Revision: `51c485421a95ee796de6d8dab53a5ade0a20db8a` (`cookie` 2.0.1).
- Commit tree: `7beb9a2f1a9b3943c8e03c0e9fc8ce8a3e7126c1`.
- Source archive: `git archive --format=tar HEAD`.
- Source archive SHA-256:
  `e4f8342e3b6d89c5dc8d03e086d2f5faa8c5a09ca6f76b7ac9b4a06fa610d0b0`.
- The detached tree has no submodules.
- License: MIT, root `LICENSE` SHA-256
  `c02110eedc16c7114f1a9bdc026c65626ce1d9c7e27fd51a8e0feee8a48a6858`.
- Frozen `package.json` SHA-256:
  `75cd16a27d7d0018a08dcbe46eef242f5cbaae4c47efd95979c77ddad59e5fac`.

## Locked Build And Upstream Observation

The exact revision was built in
`docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`
(`linux/amd64`, Node `24.19.0`, npm `11.17.0`) using:

```text
npm ci --ignore-scripts --no-audit --no-fund
npm run build
npm test
```

The unmodified upstream command exited 0 with four Vitest files and 63,740
passed leaves. Its coverage report recorded 98.2% statements, 96.82% branches,
100% functions, and 100% lines for the runtime source. Full output is at
`.nl2repo/authoring-work/repairs/cookie/work/upstream-vitest.log`.

Generated files used by the Oracle adaptation:

```text
dist/index.js    sha256:b728aa01f45e9115920e2a92e2f3d71c1b5acfbb8bc1d702b87397860c4ba925
dist/index.d.ts  sha256:d0c80866b3a63107db0659fa609f23e8a80e53117e7b0146ae1cfd3d3aa33b27
```

## Scripts-Stripped Adaptation

The exact source package requires generated `dist/` output and declares
build/publish/test scripts plus development dependencies. The production
Oracle is a reviewed distribution adaptation containing only `LICENSE`, the
two generated `dist/` files, a scripts-free ESM `package.json`, and a root-only
npm v3 lock. It retains package name/version/license/export behavior, has no
runtime dependencies, and requires no lifecycle execution.

On the locked Node image the adaptation passed:

```text
npm ci --offline --ignore-scripts --no-audit --no-fund
npm pack --ignore-scripts
node src/nl2repobench/verification/node/validate-package.mjs cookie-2.0.1.tgz
```

The package validator exited 0. The tarball contained four publish files and
no scripts, native addon, workspace, lockfile, cache, or test bytes.

## Bounded Public Scope

The production verifier freezes 32 deterministic `node:test` leaves covering
the four named ESM functions with JSON-safe parser/serializer values. The
child receives only a bounded JSON object naming one allowlisted operation and
its data. The adapter is a fixed verifier-owned file; source text, callbacks,
functions, and other executable values never cross stdin/stdout or argv.
Candidate code runs as the unprivileged `candidate` user in a subprocess and
is not imported into the trusted test process.

Custom encode/decode callbacks, undefined values, valid `Expires`/`Date`
values, snapshots, top-site corpora, exhaustive generated Unicode cases,
benchmarks, build tooling, and size checks are explicitly outside the public
instruction and frozen denominator. A Date result is rejected rather than
implicitly converted. This is a bounded behavioral slice, not upstream parity.

## Private Artifacts

```text
npm bundle  sha256:0465771fa2162c197c01e0fbf91097cb083e1d34df867386add3c2b9399c6d34  10240 bytes
commands    sha256:fda65a1fae7a54d9433921e0c28ac2311ec9dbefc0b8c54efe69c954ad4433f7  10240 bytes
tests       sha256:fafcf9cc348d7b2d39d38862563860fc16e7dfb8968f01bd254453930bc08587  20480 bytes
Oracle      sha256:6880843c56fbb2812265e32874ede71387f6a1559c240c785c25344fac2cc0fc  40960 bytes
```

The npm v3 bundle has an empty cache and a manifest that hashes its root-only
lock. `validate_npm_dependency_bundle(..., expected_npm_version="11.17.0")`
passed. Runtime network policy is `no-network`, and reference source fetching
is forbidden.

## Production And Controls

Production compilation used the locked toolchain and private artifact resolver
without `--allow-incomplete`:

```text
uv run nl2repo harbor compile catalog/sources/cookie --output catalog/tasks \
  --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts \
  --allow-private
```

The final official Harbor Oracle run is under
`.nl2repo/authoring-work/repairs/cookie/runs/cookie-oracle-controls-final/`:

```text
valid=true
expected_total=32
collected=32
passed=32
reward=1.0
```

Negative controls used the same separate no-network verifier:

```text
empty workspace: valid=true, installation failed closed, reward=0.0
callable stub:   valid=true, 1/32 passed, reward=0.03125
forged reports:  valid=true, 1/32 passed, reward=0.03125
```

The accepted isolated stub run is `cookie-stub-isolated`; the forgery run wrote
candidate-controlled reward/grading files in the workspace, and verifier-owned
grading remained authoritative. No cross-language or upstream parity claim is
made.
