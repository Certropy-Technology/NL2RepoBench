# Nl2RepoBench

## Project Overview

NL2Repo is a benchmark designed to evaluate the performance of Large Language Models (LLMs) and coding agents on **long-horizon tasks** that require generating a **complete, runnable code repository from scratch (0-to-1)**. The benchmark consists of **104 distinct tasks**, each paired with its own testing environment.

## Getting Started

- [QUICKSTART.md](QUICKSTART.md) — clone 后直接跑通 benchmark（含免 API key 的 Oracle 门禁）
- [CONTRIBUTING.md](CONTRIBUTING.md) — 怎么出题、怎么跑 Bench、注意事项、OSS 归档结构

## Task Authoring

- [中文出题、质量门禁与 Harbor 接入手册](docs/task-authoring-guide.zh-CN.md)
- [工程化改造长期路线图](docs/engineering-roadmap.zh-CN.md)
- [Metadata Core 与声明式 Catalog](docs/metadata-core.zh-CN.md)
- [Phase 2 Harbor Compiler 与通用 Verifier](docs/phase2-harbor-verifier.zh-CN.md)
- [Harbor E2E 示例题：ministats](examples/harbor/ministats/README.md)
- [运行数据 OSS 归档布局](docs/run-artifacts-oss.md)
- [Benchmark 运行、出题与排障总手册](docs/benchmark-operations-guide.zh-CN.md)
- [AST 驱动批量出题 Pipeline（当前入口）](docs/authoring-pipeline-ast.zh-CN.md)
- [Java/Maven 与 Rust/Cargo Runtime 扩展技术规格](docs/java-maven-rust-runtime-expansion-spec.zh-CN.md)
- [Modern Toolchain Policy（Polars/uv/AST/Parquet）](docs/modern-toolchain-policy.zh-CN.md)
- [Harbor/OpenHands trajectory 产物说明](docs/trajectory-artifacts.zh-CN.md)

## Modern Core

The authoring core is managed with `uv` and `pyproject.toml`; `uv.lock` is the
reproducible dependency lock. The historical OpenHands 0.56/Docker runner has
been removed from the current tree; its source and lock identity remain in Git
history and immutable archives. The current SDK fork is the `openhands/` submodule.

```bash
uv sync
uv run nl2repo doctor
uv run nl2repo task import-legacy
uv run nl2repo dataset validate authoring
uv run nl2repo harbor compile catalog/tasks/ministats --allow-incomplete
```

The current Harbor pipeline is catalog-backed. Human-maintained task sources
live under `catalog/sources/<task-id>/`; generated Harbor projections live under
`catalog/tasks/<task-id>/`. `examples/harbor/` is reserved for infrastructure
examples. Run outputs belong under `.nl2repo/runs/` and are not dataset assets.

The importer writes canonical task manifests, a SQLite state index, and
content-addressed artifacts. Private command/test-path JSON is referenced by
digest and is not embedded in public manifests. See
[`docs/metadata-core.zh-CN.md`](docs/metadata-core.zh-CN.md) for the data model
and migration contract.

## Running the Code

Task authoring is orchestrated by the active top-level model. Each task uses an
isolated git worktree; task workers prepare task-local catalog and Harbor
evidence, while the top-level model reviews, integrates, commits, pushes and
archives accepted work. The retired Python authoring Loop and auto-coordinator
must not be used to claim or integrate tasks.

```bash
uv run nl2repo task validate-source catalog/sources/<task-id>
uv run nl2repo harbor compile catalog/sources/<task-id> \
  --output .nl2repo/compiled/<task-id> \
  --toolchain toolchain.lock.toml \
  --artifact-root .nl2repo/artifacts \
  --allow-private
```

The pinned SDK fork is the `openhands/` submodule. Build and verify its runtime
image with `scripts/build_openhands_runtime.sh`. Agent and verifier runtime phases
are offline; dependencies and source locks are prepared by controlled build stages.
Existing `.nl2repo/authoring-live/` queues, worktrees and receipts remain recovery
inputs. See `docs/benchmark-operations-guide.zh-CN.md` for the manual orchestration
and recovery procedure.

## Data Layout

1. `catalog/sources/`: human-maintained authoring truth.
2. `catalog/tasks/`: compiler-generated Harbor projections.
3. `.nl2repo/artifacts/private/sha256/`: local private CAS.
4. `.nl2repo/authoring-live/`: queues, claims, worktrees, sessions and archive receipts.
5. `.nl2repo/runs/`: Harbor jobs, Agent workspaces, trajectories and verifier results.
6. `test_files/`: immutable legacy input projection retained for historical conversion only.

Agent workspaces are runtime artifacts, not tracked source. Completed workspaces,
trajectories and grading evidence are uploaded and verified in OSS before local cleanup.
