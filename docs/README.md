# Documentation Map

`AGENTS.md` is the repository execution protocol. This index separates the
current contract from operational guides and non-normative historical records.
Do not infer current task counts, release gates, or CLI availability from dated
plans and status snapshots.

## Current contract

- [`task-authoring-guide.zh-CN.md`](task-authoring-guide.zh-CN.md) — task
  authoring, specification, verification, and publication gates.
- [`unified-contract-migration-adr.zh-CN.md`](unified-contract-migration-adr.zh-CN.md)
  — accepted clean-break canonical contract decision.
- [`runtime-adapter-architecture.zh-CN.md`](runtime-adapter-architecture.zh-CN.md)
  — Python, Node, Go, and future runtime/package-manager adapter architecture.
- [`metadata-core.zh-CN.md`](metadata-core.zh-CN.md) — declarative source,
  canonical manifest, schema, and metadata CLI.
- [`phase2-harbor-verifier.zh-CN.md`](phase2-harbor-verifier.zh-CN.md) — Harbor
  compiler, separate verifier, scoring, and controls.
- [`engineering-roadmap.zh-CN.md`](engineering-roadmap.zh-CN.md) — target
  architecture and migration sequencing; implemented commands must still be
  checked with `uv run nl2repo --help`.

The canonical direction is:

```text
catalog/sources/<task-id>/   # Human-maintained declarative source
        -> canonical manifest
        -> catalog/tasks/<task-id>/  # generated runnable Harbor task
```

New Package campaign releases use one Oracle gate: `valid=true`, collection
equal to the frozen denominator, and reward at least `0.80`. Multi-run Oracle
results are stability evidence for a separately declared experiment, not the
default release gate.

## Operations

- [`authoring-pipeline-ast.zh-CN.md`](authoring-pipeline-ast.zh-CN.md) — current
  scalable discovery and authoring pipeline.
- [`authoring-agent-remediation-guide.zh-CN.md`](authoring-agent-remediation-guide.zh-CN.md)
  — top-level Pi authoring worker contract.
- [`benchmark-operations-guide.zh-CN.md`](benchmark-operations-guide.zh-CN.md) —
  authoring, Harbor runs, failure classification, and troubleshooting.
- [`harbor-runner-cleanup-and-concurrency.zh-CN.md`](harbor-runner-cleanup-and-concurrency.zh-CN.md)
  — safe cancellation, cleanup, and concurrency.
- [`modern-toolchain-policy.zh-CN.md`](modern-toolchain-policy.zh-CN.md) — uv,
  Polars, AST, Parquet, and resource policy.
- [`run-artifacts-oss.md`](run-artifacts-oss.md) — OSS artifact layout and
  verified upload/deletion flow.
- [`trajectory-artifacts.zh-CN.md`](trajectory-artifacts.zh-CN.md) — trajectory
  and ATIF retention contract.
- [`oss-readme.md`](oss-readme.md) — README payload uploaded with OSS archives.

## Historical, non-normative records

- [`authoring-pilot-retrospective-20260824.zh-CN.md`](authoring-pilot-retrospective-20260824.zh-CN.md)
  — dated remediation lessons; current paths and gates come from the documents
  above.
- [`node-foundation-status.v1.md`](node-foundation-status.v1.md) — dated Node
  vertical-slice evidence.
- [`npm-node-task-feasibility.md`](npm-node-task-feasibility.md) — original Node
  feasibility analysis, retained for rationale rather than current status.
- [`node-foundation-plan.v1.md`](node-foundation-plan.v1.md) — redirect for the
  retired additive v2 plan; the full text exists only in Git history.

The superseded Python/Node scale plan, 300-task expansion plan, and historical
Harbor pilot guide were removed. The additive Node-v2 plan was reduced to a
redirect because historical blocker evidence still references its path. Git
history remains the archive for the retired content.
