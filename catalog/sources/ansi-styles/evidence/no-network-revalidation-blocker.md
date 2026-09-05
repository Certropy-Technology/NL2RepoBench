# NoNetwork revalidation blocker

Revalidation was attempted after the public instruction migration with source
digest `sha256:49b7723d3b9587663822f93996fadaff12d380706bdbe74c81931400fed8a061`.

## Reproduction

- Harbor version: `0.21.0`.
- Two fresh private compiles were deterministic: both contained 80 files and
  bundle manifest SHA-256
  `sha256:2032897f751fcabbc0b974d42bef24da29d66149ee1dd0de6346fa6fae6e8fe0`.
- The compiled `solution/solve.sh` SHA-256 was
  `sha256:a25a9682f57205d5ad4aae719238bef8b24e4a6e3eda5df959750e8c7fad6a70`.
  Its source-host request targets `codeload.github.com`.
- The strict NoNetwork Oracle command completed with exit code 0 at the Harbor
  job layer but produced `valid=true`, `collected=0/32`, reward `0.0`, and
  failure class `candidate-installation-failed`. The agent log records a
  failed TLS connection to `codeload.github.com`; verifier network evidence
  records `public_network_available=false`.
- The source-local `harbor/solution/solve.sh` proposal was intentionally
  removed after compile inspection: the Node compiler extracts the declared
  private `oracle_bundle` from CAS and takes precedence over a source-local
  solution, so retaining it would not affect the generated runtime.

## Immutable payload binding

The existing private Oracle bundle is bound by task metadata to
`sha256:624a3021bc2b388d07ab47ee85f5ab94fa79a424945da7eb7fa719183c96f20e`.
Its archive contains `solve.sh` and an `oracle-package/` directory. The local
payload file hashes observed during this revalidation were:

```text
oracle-package/index.d.ts       sha256:09ec9006e2cea3d5ed9eb1129d3fdcce68a25dcfec953b02cef8c42c00987ee9
oracle-package/index.js         sha256:3e1556c01c17b95070535b48557145f34def2a6bc9ea08dcf084b65ae4b94779
oracle-package/license          sha256:5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3
oracle-package/package.json     sha256:7be6d4301edbaa68451eb039abd4618826b1235d8649cbfdd6c8c6f7c7128d14
oracle-package/package-lock.json sha256:c1ca5b9a98f3204e2a487d32ebcca1229402744a7adfe1640093feebdc1c60f2
oracle-package/readme.md         sha256:1574d382f0a386ab2deaf58c99ff42424f872bfae68f87afc4186412231fb003
```

The bundle itself is the existing hash-bound private artifact; Oracle payload
bytes are not copied into this public source evidence. A new CAS bundle must
combine those exact payload files with the proposed local materializer and
receive a new artifact digest before the compiler can consume the repair.

## Required remediation

The parent integrator must register a new private Oracle bundle containing the
existing hash-bound `oracle-package/` files plus the proposed materializer,
update the task's `[oracle_bundle]` digest, compile a new final manifest, and
rerun Oracle plus every declared control. No old receipt or current
`production-evidence.json` entry is valid for that new manifest.
