# dot-prop instruction revalidation blocker

- Expected migrated source digest: `sha256:1aefd87929070ef049a70fdfa1d690c6a917216b0795fea648d9c2f80a6f26ab`.
- Source validation passed with that exact digest.
- Harbor `0.21.0` production compilation passed twice with `toolchain.node.lock.toml`, the parent private artifact store, and `--allow-private` without `--allow-incomplete`.
- Both bundle manifests are byte-identical. Each manifest contains 78 payload entries (79 files including the manifest itself). The bundle file SHA-256 is `sha256:e671070552754f4bc0abc3fdbe15849ade455acb821008aaac47b7b66ae17101`; the canonical manifest digest is `sha256:40189e9c0156c7c1ef07afb258d3da61df1718d2f9907816af42031f36831707`.
- The generated bundle contains standalone `empty`, `stub`, `forgery`, `hang`, and `offline` controls and a frozen 36-leaf `node-test` contract.
- Payload inspection found that `solution/solve.sh` performs a runtime `git fetch` from the upstream source host before copying the reference package. No source-host authorization was provided, so Oracle and all changed-bundle controls were not run. No historical receipt was reused and `production-evidence.json` was left unchanged.

## Remediation

Materialize a local Oracle payload whose source revision and archive/index bytes are verified against the frozen source metadata, or otherwise remove the runtime source fetch while preserving the same reference bytes. Then compile the changed bundle again and run Oracle, empty, stub, forgery, and offline controls, persisting each receipt under this directory before updating production evidence.

## Commands

The executed commands and compact results are recorded in:

- `compile-a-summary.json`
- `compile-b-summary.json`
- `oracle-payload-review.json`
- `oracle-grading-summary.json`
- `oracle-collection-summary.json`
- `oracle-network-summary.json`
