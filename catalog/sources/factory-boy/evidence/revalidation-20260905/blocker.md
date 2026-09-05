# Factory-boy instruction revalidation blocker

- Task: `factory-boy`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:6b20146abdfeb400146634b0a5ad274daaf08be0aad1917d2ae970b713dfc674`
- Frozen upstream archive digest: `sha256:9a3b710c3cc5ae1b00ef8b07a6ddae7a15f8545d9f006f256993322b867c0cd0`
- Lifecycle: unchanged at `packaged`; this is not a lifecycle transition.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/factory-boy` passed with the expected catalog source digest. All three declared private CAS objects were present with matching size and SHA-256. Two production compiles using `toolchain.lock.toml`, the parent private CAS, `--allow-private`, and no runtime host authorization exited `0` and were byte-identical. The current compile has 59 files and canonical manifest digest `sha256:7f512c9aa34ab428331a2fb9a7cc6cc5d9c016afa7a2dab1b8856d81a72cc171`.

## NoNetwork blocker

The Oracle artifact `sha256:59e66008af475f70b1681c2e1ff6d0410472df63a517ce2da3789b58a71e8506` contains `solve.sh` (`sha256:a8ecac61316e06d8446843f3719845f4ded29a314efdd8312b32778eb53c9cf5`). It runs `git clone --filter=blob:none https://github.com/FactoryBoy/factory_boy`, `git fetch --no-tags origin ae9f2f4650afef0bc9b0925de97f618603233ff8`, and then verifies the archive. This is a runtime GitHub source fetch and violates this task's NoNetwork contract. Oracle and controls were not run; no reward, collection, grading, network, result, or failure receipt is claimed.

## Remediation

Register a replacement private Oracle bundle containing a local immutable source payload, or otherwise replace the Oracle payload with a revision- and archive-digest-verified source-local payload. Recompile twice against the replacement and run the complete Harbor 0.21.0 Oracle, empty, stub, forgery, and offline matrix. Do not authorize GitHub, reuse historical local smoke receipts, change the frozen denominator, or change lifecycle solely because of this artifact/verifier blocker.
