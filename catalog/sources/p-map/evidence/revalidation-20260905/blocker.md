# p-map instruction-migration revalidation blocker

- Task: `p-map`
- Revalidation status: `artifact-or-verifier-blocked`
- Queue position: 196
- Current source content digest: `sha256:f47c7270617fccd7c93e4f190519755daf413912d79e0c74ca8690d5e0a00776`
- Frozen revision: `22dda61ea29037ba85af25e84bc5efba77e62f44`
- Frozen source archive digest: `sha256:ef544534472632d1bf174753ad75c21496119ff54bef8dedca45bb14cfe90ea2`
- Lifecycle and `production-evidence.json`: unchanged (`packaged` / awaiting official agent run).

## Checks completed

`uv run nl2repo task validate-source catalog/sources/p-map` exited `0` and reported the
queue-bound source content digest above. The current source declares Node `24.19.0`, npm
`11.17.0`, Harbor `0.21.0`, and `no-network` for agent, candidate, verifier, Oracle, and
controls. The exact task network lint exited `0` with no p-map findings.

The four declared private artifacts were found in the trusted local CAS and checked by
size and SHA-256:

| artifact | size | SHA-256 |
| --- | ---: | --- |
| npm dependency bundle | 10240 | `sha256:f18da9c5e7e42e47a8e09b036908c6d2928c4b22ac0caca69c1e3fcd3c867312` |
| commands bundle | 10240 | `sha256:10e70a89b271a2cd71d8dbaa6848530c6550ac4d87e65ae87d7332265e5eedd9` |
| private tests bundle | 20480 | `sha256:b2963fc16f32a1030bdc97a3965f7cdd7d564c2f596b82332cf93711e3c6d6e1` |
| Oracle bundle | 10240 | `sha256:e4c9423e54cbadf1d7eb474c063d49607c2b927e2a0d3ce1bc745afed4052276` |

The Oracle artifact was unpacked without execution. Its only file is `solve.sh` (1266
bytes, SHA-256 `sha256:b4ac5c7fa62757725346ed56ab169e22043b8683299314589827cc1af18ce090`).
The script executes `git fetch --depth=1` from the upstream GitHub URL before materializing
the candidate workspace. It contains no local `source.tar` or other frozen source payload.

A bounded search of the current CAS, catalog projections, authoring archives, historical
handoffs, run roots, and local caches found no file whose bytes match the frozen source
archive digest (and no exact 71680-byte matching archive). The checked-in generated
projection also retains this fetch-based Oracle and is not an acceptable offline
replacement. No source bytes were copied or proposed.

## Disposition

No compile, Harbor Oracle, empty, stub, forgery, or offline control was started. Running
them would either execute a runtime GitHub fetch or reuse a stale receipt, violating the
NoNetwork and migrated-instruction contracts. Historical receipts remain untouched.

## Remediation

Provide a trusted local archive for revision
`22dda61ea29037ba85af25e84bc5efba77e62f44` whose complete archive bytes verify to
`sha256:ef544534472632d1bf174753ad75c21496119ff54bef8dedca45bb14cfe90ea2`. Register it
in the parent-owned private CAS, replace the fetch-only Oracle payload, compile twice with
the locked Node toolchain, inspect both closed-world manifests for path leaks, and run a
fresh Harbor `0.21.0` NoNetwork Oracle plus empty/stub/forgery/offline controls. Keep this
source-local blocker until those receipts exist; do not change the denominator or
lifecycle to bypass the missing payload.
