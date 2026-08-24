# lossless-json blocked remediation record

Status: **blocked**. The exact upstream source, license, and npm lock are
frozen, but the required private npm cache closure is not available. No
runtime task, verifier, Oracle bundle, hidden tests, or controls were
generated.

## Source Authority

- Repository: `https://github.com/josdejong/lossless-json`
- Revision: `7e89e3b789617e97e370dc8d923a124d6407a463`
- Git archive: 563,200 bytes,
  `sha256:9c3f1372ac81f866c6b4592011c0f1ce8c4a6b3e2411156c8992aafa2de87645`
- License: MIT, root file `LICENSE.md` (not `LICENSE`),
  `sha256:c5075e9ebeac2efabaddeb7ff8f215ef180f76da7837a79e3107868271693114`
- `package-lock.json`: lockfile v3, 754 package entries,
  `sha256:833b40aaaf45851b65c55f965b1379d7e1e61a675049eef598f2a63f5e9da378`

## Remediation Evidence

The repository contract is Node `24.19.0` with npm `11.17.0`. The worker shell
had Node `26.7.0` and npm `12.0.2`; this version mismatch is recorded as an
additional environment limitation, not hidden as a successful install.

Command:

```text
npm_config_cache=/tmp/lossless-json-install/.npm-cache npm ci --offline --ignore-scripts
```

Exit code: `1`.

The correct empty-cache install failed closed with `ENOTCACHED` because the
cache had no response for `yocto-queue@0.1.0`. The captured output is preserved
at [`evidence/remediation.log`](evidence/remediation.log), SHA-256
`sha256:e9d3f881843c1fe14230287bb12296f030856a7fc494b152d96028984f7f0184`.

Failure class: **environment**.

## Reopen Condition

Materialize and hash a complete private npm cache for every
`package-lock.json` integrity entry under the locked Node/npm toolchain, then
rerun `npm ci --offline --ignore-scripts`. Only after that succeeds may a
deterministic build, separate verifier, Oracle, and controls be authored.
