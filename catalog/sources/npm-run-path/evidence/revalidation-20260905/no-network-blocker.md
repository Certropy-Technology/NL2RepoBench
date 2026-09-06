# npm-run-path instruction revalidation blocker

The queue-bound source digest is
`sha256:2d5db52abf4195f5a69532d0b45bfb47aab5116dc5e3f2c133feda2e35ed3c02`.
`validate-source` passed before this evidence was written.

All four declared private artifacts were checked offline by exact byte count and
SHA-256. The recoverable Oracle bundle contains only `package.json` and
`solve.sh`; its `solve.sh` performs a runtime `git fetch` from `github.com` and
does not contain the frozen source archive. A bounded search of the checked-in
projection, task-local evidence, retained authoring archives, local CAS, local
package caches, and historical Git paths found no file matching the frozen
archive digest `sha256:8b7133f569873efe624778419ce87b94a9df78ac19f80a4a7217f9adbd67664f`.

## Checks and receipts

The following commands were run in the isolated worktree; all completed with
exit code 0 unless noted:

| Command | Result |
| --- | --- |
| `uv run nl2repo task validate-source catalog/sources/npm-run-path` | exit 0; queue/source digest accepted |
| offline SHA-256/size check of dependency bundle | exit 0; `eb2735cb...1de4`, 92160 bytes |
| offline SHA-256/size check of command bundle | exit 0; `ecade7e4...6552a`, 176 bytes |
| offline SHA-256/size check of test bundle | exit 0; `d6436828...d953`, 20480 bytes |
| offline SHA-256/size check of Oracle bundle | exit 0; `bfb67879...0652`, 10240 bytes |
| `uv run --frozen --project harbor-runner harbor --version` | exit 0; Harbor 0.21.0 |
| `uv run python scripts/validate_instruction_quality.py` | exit 0 |
| `uv run nl2repo task lint-network --tasks-root catalog/sources` (filtered to this task) | exit 0; 0 task findings/errors |
| JSON/TOML parsing and `bash -n` for task scripts | exit 0 |
| bounded local archive search | exit 0; no matching archive found |
| `git diff --check` | exit 0 |

The Oracle bundle's exact member listing was `./`,
`./package.json`, and `./solve.sh`. The four verified private CAS references
were dependencies `sha256:eb2735cb44d12c947427bbffca5584cef231a219fcf932310feb6d08b7801de4`
(92160 bytes), commands
`sha256:ecade7e4a7652dc33367d2c5ce2971815591d9ae5bc4482e009eb1fa3af6552a`
(176 bytes), tests
`sha256:d643682871092029801cc946b76fe08f4f473f669c7d48b2a3f0c10557ebd953`
(20480 bytes), and Oracle
`sha256:bfb67879e82bc99dfe8e2ae2ed14225ab5c8ab06e90b377b41bb0b1a3a4e0652`
(10240 bytes).

The current NoNetwork contract therefore prohibits running this Oracle. The
existing production evidence and lifecycle are intentionally unchanged; its
old receipts use a runtime GitHub authorization and are not current receipts
for the migrated instruction.

## Remediation

Recover an exact archive for revision
`b9128591fc59429d8b0df7047d5283f259dc5e77`, or construct a parent-reviewed
replacement Oracle bundle whose embedded archive hashes exactly to the frozen
digest. The parent must register any private replacement, compile twice without
`--allow-incomplete`, and rerun Oracle plus empty, stub, forgery, offline, and
all registered controls before accepting new production evidence.
