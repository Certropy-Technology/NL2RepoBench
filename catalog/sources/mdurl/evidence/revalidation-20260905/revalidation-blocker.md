# mdurl instruction revalidation blocker

## Classification

This is a revalidation artifact blocker, not a lifecycle transition. The source
digest and existing historical `production-evidence.json` remain unchanged.

The three declared private CAS objects were checked offline by exact size and
SHA-256. The dependency lock (`176` bytes), verifier bundle (`30,720` bytes),
and Oracle bundle (`10,240` bytes) all match their declarations. However, the
Oracle bundle contains only `solve.sh`; its payload clones the upstream GitHub
repository at runtime and archives the frozen revision. That is forbidden by
the current NoNetwork contract.

The generated `catalog/tasks/mdurl/` projection has no source archive. Historical
local mdurl authoring worktrees contain the same fetch-only script and installed
package modules, but no trusted archive matching the declared 81,920-byte
`f0caa116...84595` digest. The frozen revision is also absent from the current
Git object database. Installed package files cannot establish the required
upstream commit or archive bytes.

## Required remediation

Recover the exact source archive from a trusted local artifact or retained
authoring handoff, verify its size and SHA-256 against `task.toml` and the
source-freeze record, and construct a replacement Oracle bundle whose payload
does not fetch at runtime. The parent must independently inspect the inner
payload, register the replacement in CAS, compile twice, and rerun Oracle,
empty, stub, forgery, and offline/no-egress checks against the resulting final
manifest before accepting this task.

The machine-readable search record is
`evidence/revalidation-20260905/local-recovery-search.json`.

## Commands and observed results

* `uv run nl2repo task validate-source catalog/sources/mdurl` — exit `0`;
  source digest reported `sha256:a083cb9f...e429c02`.
* `uv run --frozen --project harbor-runner harbor --version` — exit `0`;
  Harbor `0.21.0`.
* Offline CAS size/hash verification — all three declared objects matched.
* `uv run nl2repo harbor compile catalog/sources/mdurl --output
  .nl2repo/mdurl-revalidation/compile-a --toolchain toolchain.lock.toml
  --artifact-root .nl2repo/artifacts --allow-private` — exit `0`.
* The same compile to `compile-b` — exit `0`; bundle manifests were
  byte-identical (`sha256:d726a3e13e48bed8293abdad41c41d3626d104d77644fd349129a9f99261c090`).
* Inner Oracle tar inspection — one member, `solve.sh`; no source archive.
* `git cat-file -e 524d2edbbcb8bb48301ba716c7482827bcabb281^{commit}` — failed:
  the frozen upstream commit is not present locally.

No Harbor run was started because the only available Oracle would violate the
NoNetwork gate. Existing production evidence was not replaced and no generated
projection was modified.
