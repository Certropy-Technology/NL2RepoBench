# own-keys instruction revalidation blocker

## Classification

`artifact-or-verifier-blocked`

The instruction source digest after migration is `sha256:74db786657066c51ec2f86337c38d068bdd7e3886396d131bf7aedc2e0869e5a`, matching the queue entry and the successful source validation recorded below. The declared npm, test, commands, and Oracle artifacts were found in the local CAS with exact declared sizes and SHA-256 values. The Oracle artifact is only a fetch-based bundle: its `solve.sh` fetches the frozen revision from `github.com` and creates the source archive at runtime. No exact frozen source archive matching `sha256:be351a99690d1692929f1e4c5c08aba84010cee56973f16156716eab5fa0e816` was found in the bounded local source-archive search or the task's historical handoff paths. Because this lane is NoNetwork, a fresh Oracle cannot be run without violating policy.

## Frozen source and artifact checks

| item | declared value | result |
| --- | --- | --- |
| queue source digest | `sha256:74db786657066c51ec2f86337c38d068bdd7e3886396d131bf7aedc2e0869e5a` | matched `validate-source` |
| frozen archive digest | `sha256:be351a99690d1692929f1e4c5c08aba84010cee56973f16156716eab5fa0e816` | not recovered offline |
| npm dependency bundle | 624640 bytes, `sha256:a2e186ea0ffed689956a34e68a7ac1b08ca886578c24229bcd98334ce37833a9` | exact CAS match |
| private command bundle | 10240 bytes, `sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9` | exact CAS match |
| private test bundle | 20480 bytes, `sha256:1f298fbd139aa248587902f41595b6c638f60b2ea2bf91977c18d7c7ca6c5ede` | exact CAS match |
| Oracle bundle | 20480 bytes, `sha256:801c15f25447029d048cd42057e0d4dd465288596759ae99c55f6adf1295e726` | exact CAS match; fetch-only payload |

The generated `catalog/tasks/own-keys` projection and prior valid production evidence were inspected but not modified. Prior receipts are stale for the migrated instruction digest and are not reused as current revalidation evidence.

## Attempted commands

See `checks.json` for machine-readable command results and normalized command labels. The source validation, instruction quality, exact-task network lint, JSON/TOML parsing, shell syntax checks, and diff hygiene checks passed. The bounded source search completed for task-local CAS, historical handoff paths, and named `source.tar` candidates; no hash-matching own-keys archive was established. No Harbor compile or run was attempted because the required source payload is unavailable offline and the Oracle explicitly performs a forbidden runtime GitHub fetch.

## Skipped gates and failure set

- Skipped: fresh compile twice, final-manifest inspection, Oracle, empty, stub, forgery, call-hang, and offline controls.
- Failure class: `artifact-or-verifier` (missing exact offline Oracle source payload; runtime source fetch forbidden).
- No Oracle denominator, reward, or current control result is claimed.

## Remediation

Parent should recover or register an exact private source archive whose bytes hash to the frozen archive digest, replace the fetch-only Oracle payload with a source-contained bundle, compile twice using the locked Node toolchain, and rerun Harbor Oracle plus every supported control under NoNetwork. The replacement proposal must remain private and unregistered until parent CAS review; this evidence contains no private payload bytes.
