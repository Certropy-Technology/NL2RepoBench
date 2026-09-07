# pydantic-settings instruction revalidation blocker

- Task: `pydantic-settings`
- Queue source digest: `sha256:c6b9cd7a3c56cb8d6cf846819988600671bf5075a2333432e83f09a617d411fa`
- Source authority: known; frozen revision `d26fc0c3944fe68cf169f86386988bb83e3df2d8`; declared archive digest `sha256:57b7dab78777c75bcc2c138d561dea097afe3088c0b3e7f1d67481d6b4bbd5aa`
- Classification: `artifact-or-verifier-blocked`
- Historical receipts were not reused and existing lifecycle/production evidence was not changed.

## Verified declarations

The three declared private CAS artifacts were checked against their task metadata:

| Artifact | Size | SHA-256 | Result |
|---|---:|---|---|
| dependency lock | 14,279 bytes | `sha256:b350283c9b3a343cc38b05affa57957f035da0794d4c074f3c50a666e2c86c89` | exact |
| verifier bundle | 20,480 bytes | `sha256:780ebc4eba8b4ff608530dff777a4aca692bcd7ceb6b32fc4f1bdbe81a2b0723` | exact |
| Oracle bundle | 10,240 bytes | `sha256:356386c9450c398697aabed64a487d768914a0db19f9cd14ddf4a4d42acfce4e` | exact |

The isolated worker could not resolve the private CAS by its local artifact root; parent integration CAS was read-only input for this inspection.

## Bounded recovery and compile probes

- `uv run nl2repo task validate-source catalog/sources/pydantic-settings`: exit 0; source digest matched the queue.
- Bounded search across local catalog, historical checkout, cache, and temporary recovery roots inspected 96 `source.tar` candidates; none matched the declared `sha256:57b7dab7...` archive digest.
- The exact Oracle bundle inventory contains only `solve.sh`; it has no embedded source archive and uses `git fetch` from `https://github.com/pydantic/pydantic-settings` at runtime.
- Compilation with the isolated worker artifact root failed closed because the declared dependency lock was unavailable there. Recompilation with the parent CAS read-only root succeeded twice, with identical bundle manifest bytes (`sha256:2fa7ce7204ebcad89270ca1f675a7cce1f2acaa46186b1fcd75bfc850cce7488`).
- The resulting source/manifest is not accepted as a production receipt: the Oracle remains runtime-fetching and no exact frozen source payload is locally available for safe NoNetwork execution.

## Required remediation

Provide a parent-verified replacement Oracle bundle containing exact source bytes for revision `d26fc0c3944fe68cf169f86386988bb83e3df2d8`, or recover the declared archive from a trusted local source. Parent must register any replacement in CAS, update only the source artifact reference if needed, recompile twice, and run a fresh Harbor 0.21.0 Oracle plus the complete supported controls under NoNetwork. Do not authorize source hosts, lower the frozen denominator, or reuse historical receipts.
