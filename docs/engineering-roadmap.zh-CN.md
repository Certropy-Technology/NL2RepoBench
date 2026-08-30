# NL2RepoBench 工程化改造长期路线图

> **路线图决策已被更新。** 本文保留为历史背景；其中“保留 v1、增量添加 v2、
> legacy compatibility runtime”等设计不再是当前交付方案。当前采用单一 unified
> contract，直接迁移旧题并删除旧运行时兼容层，详见
> [`unified-contract-migration-adr.zh-CN.md`](unified-contract-migration-adr.zh-CN.md)。

## 1. 目标与结论

当前工程能够在单机上批量启动 OpenHands 并测试生成结果，但它还不是一个可持续的大规模题目生产与评测系统。主要问题不是缺少几个 metadata 字段，而是缺少四个基础能力：

1. 稳定、版本化的领域模型和 schema；
2. 可恢复、可重跑、可审计的出题流水线；
3. Harbor 原生的 Task/Dataset/Trial/Job 执行边界；
4. 不覆盖历史、能够区分模型与系统失败的实验记录。

本路线图采用以下核心决策：

- **Declarative catalog 是唯一 Human 编辑入口。** canonical manifest 是 compiler 生成的机器契约，Harbor task 和旧 `test_files/` 都是继续向下的单向生成物。
- **Harbor 是新数据集的正式 execution backend。** 旧 OpenHands harness 冻结为兼容读取器和历史复现入口。
- **公开仓库不保存 private tests 和 Oracle bytes。** 它们进入访问受控的私有仓库、对象存储或镜像 registry。
- **先完成单机可靠性，再扩展分布式能力。** 第一版使用 SQLite WAL 保存状态和索引，文件系统或对象存储保存内容寻址 artifact。
- **先完成 Python 题迁移。** schema 保留语言扩展位，但首年不同时建设多语言运行栈。
- **先做真实 vertical slice，再做批量 scheduler。** 先转换 Easy、Medium、Hard 各一题并通过全部控制。

目标不是把现有脚本一次性重写，而是建立一条可逐步替换、每阶段都能验证的迁移路径。

## 2. 当前工程差距

| 维度 | 当前状态 | 风险 | 目标状态 |
| --- | --- | --- | --- |
| 题目事实源 | `test_files/<task>/` 四个文件靠目录约定组合 | revision、license、image digest、traceability 缺失 | Human-readable catalog + 版本化 `TaskManifest` + immutable artifact refs |
| Metadata | 主要只有任务名、分母和测试命令 | 无法审计来源、版本、许可、难度和发布状态 | Dataset/Task/Source/Test/Metric/Review manifests |
| 批量出题 | 没有 authoring CLI 或 stage runtime | 无恢复、缓存、失效传播和审批点 | 幂等 authoring DAG + durable state |
| 批量运行 | 全局列表 + `ThreadPoolExecutor` | 无 claim、lease、heartbeat、resume、cancel | Experiment plan + Harbor Job/Trial + result normalizer |
| Trial ID | `<task>_bo<attempt>` | 重跑覆盖 workspace 和结果 | 全局唯一 run/trial/attempt ID |
| Agent harness | OpenHands 版本和配置硬编码 | 难以固定实验变量或切换 agent | Harbor agent adapter + resolved experiment manifest |
| Verifier | pytest 控制台文本正则 | collection/error/多命令结果不可靠 | JUnit/JSON 结构化 grader |
| Score | raw `passed` 被写入 `score` | 不同测试规模的题不可比较 | 固定分母 pass rate + dataset macro mean |
| Failure | 失败通常折叠为 0 或 `error` | 模型失败与系统失败混淆 | 版本化 failure taxonomy 和 termination reason |
| 隔离 | 测试镜像与候选仓库由自定义 Docker 流程拼接 | hidden assets、secret、残留进程边界不清 | Harbor separate verifier + artifact integrity |
| Secret | API key 写入生成的 `config.toml` | workspace/log/archive 泄漏 | runtime secret injection + redacted resolved config |
| 历史结果 | 单文件覆盖式写入 `result/` | 无法比较 attempts 或恢复批次 | append-only run store + immutable artifacts |
| 测试与 CI | 只有 Docker smoke 风格测试 | 核心 schema、grader、迁移无回归保障 | unit/golden/integration/fault-injection/E2E gates |

## 3. 目标架构

```text
Candidate sources
      |
      v
Declarative catalog (TOML + Markdown)
      |
      v
Authoring pipeline ----------------------+
  discover -> freeze -> inventory        |
  -> spec -> trace -> package            |
  -> oracle -> controls -> review        |
      |                                  |
      v                                  |
Canonical manifests + content-addressed artifacts
      |                         |
      | deterministic compile   | metadata/index
      v                         v
Harbor task bundles        Dataset manifest
      |                         |
      +------------+------------+
                   v
            Experiment planner
                   |
                   v
         Harbor Jobs / Trials / Artifacts
                   |
                   v
           Result normalization
                   |
                   v
      Macro scoring + reliability report

Legacy importer -> canonical manifests
Canonical manifests -> legacy exporter (仅历史兼容)
```

推荐代码边界：

```text
src/nl2repobench/
├── cli.py
├── domain/
│   ├── datasets.py
│   ├── tasks.py
│   ├── metrics.py
│   ├── failures.py
│   └── experiments.py
├── schemas/
│   ├── v1/
│   └── migrations/
├── storage/
│   ├── state.py
│   ├── artifacts.py
│   └── sqlite.py
├── authoring/
│   ├── pipeline.py
│   ├── stages/
│   └── approvals.py
├── verification/
│   ├── junit.py
│   ├── grader.py
│   └── contracts.py
├── harbor/
│   ├── compiler.py
│   ├── runner.py
│   └── results.py
├── legacy/
│   ├── importer.py
│   └── exporter.py
├── experiments/
│   ├── planner.py
│   └── normalization.py
└── reporting/
    ├── scores.py
    └── reliability.py
```

这是逻辑边界，不要求第一阶段一次创建所有模块。

## 4. Canonical 数据模型

### 4.1 核心记录

第一版至少定义以下 schema：

- `DatasetManifest`：dataset ID/version、task refs、metric contract、splits、content hash、发布信息；
- `TaskManifest`：task ID/version、difficulty/category/tags、公开 instruction ref、运行约束、artifact refs；
- `SourceLock`：upstream URL、完整 commit、submodules、license evidence、构建版本和 source hash；
- `EnvironmentLock`：OS、Python、系统包、基础镜像 digest、build/runtime/test dependency locks；
- `DependencyBundle`：Python build 阶段联网安装的 hash-locked requirements artifact ref；
  Python verifier 不允许 wheelhouse vendor。Node/npm lane 另有独立 lock/cache contract；
- `TestManifest`：冻结测试 bundle、命令、expected collection、test framework、test hash；
- `MetricContract`：passed/failed/error/skipped/xfail/collection mismatch 的精确定义；
- `ReviewRecord`：blind review、traceability review、reviewer、时间和结论；
- `ControlRecord`：Oracle、empty、stub、forgery、offline 的结果和 artifact refs；
- `TaskLifecycleRecord`：authoring 状态、owner、状态转换、阻塞/排除原因、evidence 和 approval refs；
- `ExperimentManifest`：dataset digest、agent/model/provider、网络、预算、attempts、并发和环境；
- `TrialRecord`：run/trial/attempt ID、状态、reward、failure class、termination reason、成本和 artifact refs；
- `ArtifactManifest`：digest、size、media type、provenance、visibility 和 storage URI。

### 4.2 Schema 规则

所有记录必须具备：

- `schema_version` 和稳定 ID；
- required/optional 字段定义；
- `unknown`、`missing` 和空值的明确区别；
- canonical serialization 和 content hash；
- migration 规则与 golden fixtures；
- 跨记录引用完整性检查；
- Pydantic 模型和导出的 JSON Schema；
- 不包含 secret 或 private artifact bytes。

不要把完整 provenance、review 和控制实验历史全部塞进 Harbor `task.toml`。建议分层：

| 层 | 保存内容 |
| --- | --- |
| Harbor `task.toml` | 执行、检索和资源调度所需的发布 metadata |
| `task.manifest.json` | 可公开的 source/test/environment provenance 和 immutable refs |
| Private authoring store | private tests、Oracle refs、license evidence、review 和 controls |
| Run store | experiment、trial、cost、trajectory、logs 和 result metadata |

### 4.3 Private Artifact Resolver

公开 manifest 只保存 private artifact 的 opaque ref、digest、size、visibility 和 provenance classification。构建器通过统一 `PrivateArtifactResolver` 获取私有内容：

```text
resolve(artifact_ref, expected_digest, credential_ref)
  -> verified read-only materialization
```

Resolver 必须：

- 通过运行时 secret injection 获取凭证，不把凭证写入 manifest、日志或 workspace；
- 下载或读取后校验 digest 和 size；
- 只返回只读内容或私有临时目录；
- 记录不含 secret 的访问审计；
- 构建结束后清理 materialized bytes 和 builder cache；
- 对无凭证、权限拒绝、对象缺失、digest/size 不匹配 fail closed；
- 支持本地加密 fixture、私有 Git、对象存储或 registry backend，而不改变领域 schema。

## 5. Authoring Stage Contract

每个 stage 统一采用以下契约：

```text
Stage(canonical input refs, immutable resolved config)
  -> StageResult(
       stage_name,
       stage_version,
       status,
       input_hash,
       output_artifacts,
       output_hash,
       started_at,
       finished_at,
       tool_versions,
       owner,
       worker_id,
       claim_id,
       lease_expires_at,
       failure_class,
       retry_count,
       retry_policy_id,
       next_retry_at,
       logs
     )
```

cache key 至少包含：

```text
stage implementation version
+ canonical input hashes
+ resolved configuration hash
+ tool and image versions
```

运行时需要提供：

- claim、lease、heartbeat 和 crash recovery；
- pending/running/succeeded/failed/blocked/skipped/cancelled 状态；
- 只对 `infrastructure` failure 自动重试；
- retry policy 必须定义 `max_retries`、backoff 和总时限，达到上限后进入稳定终态；
- retry 与新的模型 attempt 分离；
- downstream invalidation，不无条件重跑上游；
- manual approval checkpoints；
- 每 task 独立 workspace；
- shared dataset index 的单 writer publish transaction；
- 进程停止后不启动新任务，并允许在途 stage 安全收尾。

第一版 state backend 使用 SQLite WAL。artifact 使用 `sha256/<prefix>/<digest>` 内容寻址布局；大文件可切换到 S3-compatible storage，但领域模型不依赖具体 backend。

## 6. Harbor 原生适配边界

“Harbor 原生”不只是生成 `task.toml`，而是让 Harbor 负责正式执行生命周期：

- 每题编译为符合锁定 schema 的 Harbor task；
- agent 与 verifier 使用 separate environment；
- hidden tests、grader 和 verifier dependency 不进入 agent image；
- workspace 通过 Harbor artifact contract 传递；
- ExperimentManifest 编译为 Harbor Job/Trial 配置；
- 结果从 Harbor reward、artifact、ATIF trajectory 和 termination record 归一化；
- 本仓库不再为新数据集重复实现容器调度、timeout 和 agent adapter；
- Harbor 版本、schema、agent 插件和镜像 digest 写入 machine-readable `toolchain.lock`。

`toolchain.lock` 必须由 Phase 1 的 resolver 实际解析并校验，不能只停留在文档设计。Phase 2 之后的每个控制实验和 trial 都记录 lock digest。

Authoring truth 到 Harbor 是**单向确定性编译**：

```text
canonical authoring manifests -> Harbor bundle
```

禁止长期维护 Harbor bundle、`test_files/` 和 authoring manifest 的双向同步。人工只编辑 canonical source；生成目录由 CI 检查是否可重现。

旧 harness 与 Harbor 的 parity 必须通过真实实验验证，不能由结构相似推断。无法保持 parity 的改动使用新 dataset/version。

## 7. 通用 Verifier

从 `examples/harbor/ministats/tests/grade.py` 抽出极小、确定性的 verifier core 或生成模板，职责包括：

- 从冻结 `TestManifest` 获取唯一 expected count；
- 安装候选仓库并保存每条命令的 exit code、stdout 和 stderr；
- 解析 JUnit/JSON，不依赖 pytest 文本；
- 识别 missing/malformed report、collection error、collection mismatch、timeout、OOM 和 install failure；
- 根据版本化 MetricContract 计算 reward；
- 写入带 schema version 的 `reward.json` 和 `grading.json`；
- 校验 candidate artifact hash 和 verifier-owned 输出目录；
- 即使 verifier 失败也产生机器可读 failure record；
- 支持 fault injection 和伪造 reward 测试。

真实项目的 verifier image 必须预置 `EnvironmentLock` 和 `DependencyBundle` 描述的完整依赖闭包。offline control 要在清空 pip cache 后、`no-network` 环境中完成安装、collection 和测试，日志不得出现远程解析或下载。

`collected != frozen_total` 不能静默忽略。其 reward 处理由 MetricContract 定义，但 grading details 必须明确记录。

## 8. 分阶段 Roadmap

以下工期是 2 至 3 名工程师加数据审核资源的粗略估算，不是承诺日期。每阶段只有通过退出门禁后才能扩展规模。

### Phase 0：Architecture/Schema Sprint（2 周）

目标：冻结产品和实验契约，不写 scheduler。

交付物：

- ADR：canonical authoring source、Harbor execution backend、legacy retirement；
- Dataset/Task/Metric/Failure/Artifact schema v1；
- `toolchain.lock` 设计；
- `PrivateArtifactResolver`、dependency closure 和 offline install contract；
- public/private artifact boundary；
- 104 题 metadata gap report；
- 当前 instruction、test count、commands 和 image refs 的 golden snapshot；
- dataset 命名和版本策略。

退出门禁：

- schema 和 ADR 经人工批准；
- 104 题全部进入 inventory，缺失字段显式为 unknown；
- failure taxonomy 只有一个权威枚举；
- 能明确回答哪个文件是事实源、哪个是生成物；
- 确定无法补全旧 provenance 的题进入 `legacy-unverified` 还是 excluded。

### Phase 1：Metadata Core 与 CLI（3 至 4 周）

目标：建立可安装、可测试的 Python package 和确定性转换核心。

首批目标 CLI，当前尚未实现：

```text
nl2repo doctor
nl2repo task import-legacy
nl2repo task validate
nl2repo task show
nl2repo task build-harbor
nl2repo dataset validate
nl2repo dataset diff
```

交付物：

- `pyproject.toml`、`src/` package 和 typed domain models；
- Pydantic/JSON schemas 和 migrations；
- SQLite state/index repository；
- content-addressed artifact store；
- `PrivateArtifactResolver` reference implementation 和授权 fixture；
- `EnvironmentLock`、`DependencyBundle` 和 hash-locked requirements builder；
- resolved `toolchain.lock`，包含 Harbor version/commit、task schema、agent adapter 和基础镜像 digest；
- 104 题 legacy importer；
- manifest 到 Harbor bundle 的 deterministic compiler；
- redacted config serialization 和 secret scanner。

退出门禁：

- 同一输入重复导入得到 byte-identical manifest；
- 104 题 importer 可重复运行且无静默猜测；
- schema migrations 有 golden tests；
- branch revision、缺 license、mutable image、零分母、未知 metric contract 在发布校验中失败；
- Harbor bundle 可从 canonical manifest、resolved `toolchain.lock` 和授权 private artifact fixture 完全重建；
- 无凭证、对象缺失或 digest 错误时 deterministic fail closed；
- compiler fixture 通过锁定 Harbor CLI 的 schema/build validation。

### Phase 2：Production Verifier 与三题 Vertical Slice（4 周）

目标：证明单题生产链路可靠，再建设批量系统。

交付物：

- 通用 JUnit grader 和 MetricContract；
- failure classifier；
- command runner 和 artifact integrity checks；
- 自动冻结 expected collection；
- verifier image 的锁定依赖闭包和 offline install path；
- Oracle/empty/stub/forgery/offline controls；
- 真实 Easy、Medium、Hard 各一题的 Harbor bundle；
- verifier 单元测试、golden tests 和 fault injection tests。

退出门禁：

- 三题每题在独立环境重建下连续 3 次 Oracle `valid=true`、collection 稳定且 reward >= 0.80；低于 1.0 时记录 Oracle ceiling；
- 负向控制全部通过；
- missing/malformed JUnit、collection mismatch、timeout、install failure 有稳定分类；
- agent image layer history 不包含 hidden assets；
- candidate 不能伪造最终 reward。
- 清空 pip cache 后，三个 verifier 均在 `no-network` 下完成安装、collection 和测试；
- 每次控制运行保存 `toolchain.lock` digest；
- hidden-asset scan 覆盖每个 OCI layer、最终 filesystem、SBOM/build provenance、build context 清单和导出的 agent artifacts，并保存机器可读报告。

当前 `examples/harbor/ministats` 使用 mutable `python:3.12-slim` base tag，只能作为 E2E demo。在 base image digest 固定前，它不能作为 production-publishable golden fixture；Phase 1 应 pin digest 或另建 digest-pinned production fixture。

### Phase 3：可恢复 Authoring DAG（4 至 6 周）

目标：把手工阶段变成可恢复、可审计生产流水线。

目标 CLI：

```text
nl2repo author run <task> --until <stage>
nl2repo author resume <batch-id>
nl2repo author status <batch-id>
nl2repo author approve <task> <gate>
nl2repo author cancel <batch-id>
```

交付物：

- stage registry、StageResult 和 cache contract；
- claim/lease/heartbeat；
- owner/worker/claim audit 和有上限的 retry/backoff ledger；
- dependency invalidation；
- manual approval gates；
- batch manifest 和 per-task workspace；
- resume/retry/cancel；
- publish transaction 和 audit log。

退出门禁：

- 5 至 10 题 pilot 可在任意 stage 中断并恢复；
- 相同输入重跑命中 cache 且 output hash 一致；
- 两个 worker 竞争同一 task/stage 时只有一个获得 claim；
- 修改 instruction 只失效 downstream stages，不重新 freeze source；
- 只有 infrastructure failure 自动 retry；
- fault injection 证明 retry 达到上限后进入终态，恢复不会重置 retry budget；
- shared dataset index 始终由单 writer 更新。

### Phase 4：Harbor-native Dataset 与 Experiment（4 至 6 周）

目标：让 Harbor 正式承接批量执行，仓库只负责任务生产、实验规划和结果归一化。

交付物：

- dataset publisher；
- ExperimentManifest 到 Harbor Job/Trial 配置；
- Harbor result、artifact、ATIF 和 termination normalization；
- batch concurrency、stop policy 和 cost accounting；
- 旧 harness 对照 runner；
- Easy/Medium/Hard 5 至 10 题多 attempts parity report。

退出门禁：

- run/trial/attempt ID 全局唯一，重跑不覆盖；
- 每次运行保存 resolved config、toolchain lock 和 environment digest；
- passed/total、setup errors、runtime、steps 和 termination reason 均可对照；
- 所有系统性差异有解释；
- 不可 parity 的路径使用新 dataset/version，不声称复现论文。

### Phase 5：迁移现有 104 题（3 至 6 个月）

按 10 至 20 题小批次推进：

```text
metadata backfill
  -> source/image/test provenance
  -> spec and traceability review
  -> Harbor bundle
  -> Oracle
  -> negative controls
  -> blind review
  -> parity/pilot
  -> publish
```

每批覆盖不同难度、项目形态和依赖复杂度。失败题进入 blocked/excluded，不通过伪造 metadata 或放宽断言强行发布。

`TaskLifecycleRecord` 是 task 终态的权威位置。`published`、`blocked` 和 `excluded` 是 task lifecycle 状态，不是单个 stage failure 的别名。Publish transaction 只有在 `AGENTS.md` 的完整单题 Definition of Done predicate 为真时，才能原子写入 `published` 和 dataset entry；blocked/excluded 必须保存 owner、reason、evidence 和 approval refs。

退出门禁：

- 每题有 published、blocked 或 excluded 终态；
- blocked/excluded 有原因、owner 和证据；
- published task 不含 unknown required metadata；
- dataset manifest 只引用 immutable resources；
- metric contract 不一致的题拆分到不同 dataset version；
- 两名 reviewer 完成 blind/spec traceability review。

### Phase 6：正式实验与报告（4 周后持续演进）

交付物：

- experiment planner；
- attempts 与 infra retry ledger；
- macro score 和 difficulty/category slices；
- reliability/failure analysis；
- trajectory/token/cost coverage；
- reproducible report bundle；
- machine-readable result export。

退出门禁：

- 从 ExperimentManifest 到最终报告可以重建；
- 报告不使用 raw passed count 排名；
- invalid、excluded、infra 和 model failure 分开显示；
- 缺失 token/cost 为 missing，不是 0；
- 报告包含数据集、实验、分数和可靠性四层信息。

### Phase 7：Legacy Retirement（迁移达标后）

- `main.py`、`only_test.py`、`test_data_service.py` 和旧 post-processor 已从当前 tree 删除；
- 禁止新题直接编辑四文件发布视图；
- legacy importer/exporter 仅处理冻结历史输入，不提供旧运行入口；
- `docker_self/`、旧 template/config/workspaces runner 已删除；
- 默认文档只描述 Harbor/OpenHands SDK 当前入口；
- 保留固定版本 legacy runner 镜像和历史复现说明。

## 9. 测试与 CI 策略

### PR 快速门禁

- format/lint/type check；
- schema validation；
- canonical serialization golden tests；
- legacy importer fixtures；
- Harbor compiler golden diff；
- verifier unit tests；
- secret/private asset scan；
- OCI 每层、build context、SBOM/provenance 和导出 artifact 的 private digest/path scan；
- “COPY hidden fixture 后删除”的泄漏负向测试；
- generated bundle drift check。

### Nightly 门禁

- `ministats` Oracle + empty control；
- 真实 Easy/Medium/Hard smoke；
- malformed report、collection mismatch、timeout 等 fault injection；
- stage interruption/resume；
- artifact hash 和 cache determinism；
- Harbor/toolchain compatibility matrix。

### Release 门禁

- dataset manifest 全量校验；
- 当前 Package campaign 每题 Oracle 一次运行；需要稳定性证明时使用独立实验版本；
- 全控制集；
- immutable refs 和 image digest；
- private asset leakage scan；
- migration report 和 breaking-change review；
- signed release manifest 和 content hash。

## 10. 明确不在早期建设的内容

- 不先做 Web dashboard 或复杂 metadata editor；
- 不先上 Kubernetes、Celery、Ray 或自研通用分布式 scheduler；
- 不把 SQLite 当长期跨区域数据库，但也不在 schema 未稳定前上 Postgres 集群；
- 不同时支持多语言生产环境；
- 不做任意 DAG 平台，只实现固定 authoring stage protocol；
- 不允许 LLM 自动批准 license、测试覆盖、traceability 或发布；
- 不长期维护 legacy 和 Harbor 双向同步；
- 不把日志、JUnit、workspace 和镜像 blob 塞进数据库；
- 不在没有 parity 数据前一次性迁移 104 题；
- 不把 Harbor main、Git branch 或 mutable image tag 当发布依赖；
- 不默认使用 LLM judge；核心功能题优先采用确定性上游测试。

## 11. 主要风险与缓解

| 风险 | 缓解措施 |
| --- | --- |
| 旧题 revision/license/image 无法追溯 | 允许 `legacy-unverified` 或 excluded，不伪造 provenance |
| private tests/Oracle 许可不允许重新分发 | 使用私有 artifact store 和 opaque digest refs |
| 旧 instruction 泄漏源码或不足 | 逐题 traceability + blind review，不机械转换 |
| Harbor/OpenHands 升级改变行为 | `toolchain.lock`、compatibility CI、dataset version bump |
| 同时重写 authoring 和 runner 难以归因 | 先完成三题 vertical slice，再引入 DAG |
| SQLite 后期扩展不足 | storage interface 与 Stage contract 不依赖 SQLite 特性 |
| 大规模运行成本失控 | pilot、预算上限、stop policy、cost coverage 和分层 agent |
| LLM worker 误发布或修改共享索引 | per-task isolation、manual gate、single publisher transaction |

## 12. 需要尽快确认的产品决策

1. 第一目标是严格复现论文 104 题，还是建设下一代扩展数据集？两者应使用不同名称和版本。
2. Harbor 是否正式成为唯一的新 execution backend？本路线图建议是。
3. private tests、Oracle 和 license evidence 使用私有 Git、对象存储还是内部 registry？
4. 首年是否只支持 Python？本路线图建议是。
5. 目标规模是单机、多台 Docker host，还是必须立即支持云 sandbox？
6. agent 是否允许联网？不同网络策略应拆分 dataset version。
7. 谁承担两人 blind/spec review 和发布批准？
8. 无法恢复完整 provenance 的旧题如何处理：excluded 或 `legacy-unverified`？
9. skipped、xfail 和 collection mismatch 的精确 metric 语义是什么？
10. Harbor 版本、fork 和 schema migration 由谁维护？

## 13. 下一步：第一个 Architecture/Schema Sprint

暂时不要直接实现完整批量 scheduler。下一个可执行 sprint 应只完成：

1. 批准 canonical source、Harbor backend 和 legacy retirement ADR；
2. 定义 v1 metadata、metric、failure 和 artifact schema；
3. 自动生成 104 题 metadata gap report；
4. 选择一个真实 Easy 题，从 manifest 确定性生成 Harbor task；
5. 抽出并测试通用 verifier；
6. 对该题运行 Oracle、empty、stub、forgery 和 offline controls；
7. 根据结果修订 schema，再进入 Phase 1 完整实现。

这条路径能最快验证最关键的架构假设，同时避免在数据模型和发布目标尚未稳定时过早建设并发系统。
