# Runtime Adapter Architecture

本文定义 unified Harbor contract 的扩展边界。目标是以后加入 Rust、Go、Java、Ruby
或其他 Package 时，只增加一个 runtime/package-manager adapter 和对应测试，不复制
一套新的 catalog、compiler、grader、state 或 CLI。

## 设计原则

1. **一个 domain contract**：任务、环境、依赖、测试、生命周期和 artifact 引用只有一套
   canonical model。
2. **显式 discriminator**：`language` 和 `package_manager` 选择 adapter；`schema_version`
   只描述数据形状，不能承担运行时分派。
3. **组合而不是继承复制**：语言 adapter 负责源码/运行时/API 语义，package-manager
   adapter 负责 lockfile、offline store 和安装；两者通过 typed protocol 组合。
4. **编排层不认识具体语言**：catalog、Harbor compiler、state、grader 和 CLI 只依赖
   protocol/registry，不出现 `if python ... elif node ...` 的业务分支。
5. **统一 report**：每种测试框架先转换成统一 leaf report，再由一个 fixed-denominator
   evaluator 评分。
6. **fail closed**：找不到 adapter、runtime 与 package manager 不匹配、依赖 closure
   不完整或 report 无法归一化，都必须产生结构化 stage error，不能静默 fallback。
7. **artifact ownership 清晰**：agent image 只能得到公开 instruction 和允许的环境资产；
   private tests、Oracle、grader 和 dependency closure 由 separate verifier 持有。

## 模块边界

```text
catalog source
    │
    ▼
domain/task_contract.py       # 唯一 canonical records + invariants
    │
    ▼
authoring/loader.py           # TOML/Markdown -> TaskSource
authoring/compiler.py         # pure manifest + artifact/state orchestration
    │
    ├── runtimes/registry.py  # (language, package_manager) -> RuntimeAdapter
    │       ├── runtimes/python.py
    │       ├── runtimes/node.py
    │       └── future runtimes/rust.py ...
    │
    ├── package_managers/registry.py
    │       ├── package_managers/uv.py
    │       ├── package_managers/npm.py
    │       ├── package_managers/pnpm.py
    │       └── future package_managers/cargo.py ...
    │
    ▼
harbor/compiler.py             # generic task writer + verifier bundle assembly
    │
    ▼
verification/runner.py         # adapter executes trusted plan
verification/normalizer.py     # framework output -> LeafReport
verification/evaluator.py      # one fixed-denominator metric
    │
    ▼
reward.json + grading.json + structured events
```

### Domain contract

`domain/task_contract.py` owns only data and validation. It must not import Harbor, Docker,
pytest, Node, subprocess, OSS or Typer. The important fields are:

```python
TaskSource(
    task_id=...,
    task_release=...,
    metadata=Metadata(language=..., category=..., difficulty=...),
    environment=EnvironmentLock(runtime=RuntimeProfile(language=..., package_manager=...)),
    dependencies=DependencyBundle(...),
    tests=TestManifest(...),
    metric=MetricContract(...),
)
```

Cross-field validation belongs here: Python cannot select npm, Node cannot select pip, pnpm
requires a v9 lock and a reviewed offline store reference, and a published task requires all
provenance/collection/artifact gates.

### Runtime adapter

Each runtime adapter implements a small protocol rather than subclassing the whole compiler:

```python
class RuntimeAdapter(Protocol):
    identity: RuntimeIdentity

    def validate_source(self, task: TaskSource) -> tuple[str, ...]: ...
    def build_candidate_plan(self, task: TaskManifest) -> CandidatePlan: ...
    def build_test_plan(self, task: TaskManifest) -> TrustedTestPlan: ...
    def normalize_report(self, raw: bytes) -> LeafReport: ...
    def write_agent_environment(self, task: TaskManifest, root: Path) -> None: ...
```

The adapter owns runtime-specific details such as Python import/install behavior, Node module
format, or a future compiled language's binary entrypoint. It does not own state transitions,
score calculation, artifact authorization, or Harbor process supervision.

### Package-manager adapter

Package-manager adapters are independent because the same runtime can use multiple managers and
some managers span runtimes. They implement:

```python
class PackageManagerAdapter(Protocol):
    identity: PackageManager

    def validate_lock(self, task: TaskSource) -> tuple[str, ...]: ...
    def validate_offline_store(self, closure: DependencyBundle) -> None: ...
    def install_candidate(self, workspace: Path, limits: ProcessLimits) -> ProcessReport: ...
```

No adapter may fall back to another manager. For example, a pnpm task cannot be silently changed
to npm because both are Node package managers.

## Control flow

The generic flow is deliberately linear and visible:

```text
load -> validate contract -> resolve adapter -> validate provenance
     -> materialize artifacts -> build Harbor tree -> run verifier
     -> normalize report -> evaluate metric -> persist result
```

Every stage returns a typed result or raises one `StageError` carrying:

```text
stage, task_id, runtime, failure_class, retryable, reason, artifact_refs
```

Retry policy is owned by the orchestrator, not by adapters. Only infrastructure errors are
retryable without changing trial identity. Model, spec, environment and verifier failures are
terminal for that attempt and remain separately classified.

## Registry rules

- Registries are explicit dictionaries created at process startup.
- Duplicate identities are errors during startup.
- Unknown identities are errors with the list of registered identities.
- Adapter registration is tested with a fake runtime; tests do not need Docker or network.
- No import-time filesystem scan or plugin auto-discovery is used in the core path.
- Optional third-party plugins may be added later behind an explicit entry-point package, but the
  compiled task records the resolved adapter identity and package/toolchain digests.

## Adding a new language

1. Add the language/runtime identity to the domain enum and validation table.
2. Implement `runtimes/<language>.py` and its focused unit tests.
3. Reuse an existing package-manager adapter or add a new one with lock/store tests.
4. Implement report normalization to the common leaf report.
5. Add one synthetic development fixture and one real candidate audit.
6. Pass the vertical gates: Oracle x3, empty, stub, forgery, install failure, hang and offline.
7. Add the adapter to the explicit registry and documentation table.
8. Only then author a batch of 10–20 tasks.

No new schema family, compiler fork, metric family or compatibility parser should be introduced
for a language.

## Testing layers

| Layer | Scope | External services |
|---|---|---|
| Domain | model invariants and discriminators | none |
| Adapter unit | lock parsing, command plans, report normalization | none |
| Compiler golden | deterministic Harbor tree and bundle manifest | none |
| Separate verifier | candidate boundary, private assets, grading | Docker/offline image |
| Vertical slice | Oracle and controls for one language/package manager | Harbor |
| Benchmark pilot | 10–20 real tasks, model trials and artifact archival | Harbor + configured model |

Tests should be named after the contract, not after an implementation version. Golden outputs are
regenerated only from catalog source and are never hand-edited to make a refactor pass.

## Documentation requirements

Every adapter module must document:

- its identity and supported lockfile/runtime versions;
- what it owns and what the generic orchestrator owns;
- offline/network assumptions;
- candidate and verifier command boundaries;
- report normalization and denominator behavior;
- known blockers and resource limits;
- exact validation commands.

The top-level operations guide should list adapters and release/dataset identities, not duplicate
language-specific execution instructions in the core compiler section.
