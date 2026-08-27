# ADR：统一当前任务契约，直接迁移旧题，退出 v1/v2 运行时分裂

状态：accepted（2026-08-22）

## 背景

仓库目前同时存在：

- Python catalog/compiler/verifier 契约；
- Node/npm additive v2 契约；
- 104 道 `test_files/` legacy projection；
- 75 个 Harbor task tree；
- 多套互相独立的 manifest、report、metric 和状态记录。

`v2` 并不是单纯的命名变化：Node manifest 仍然嵌入 Python v1 的
`ArtifactRef`、`SourceLock`、生命周期和 Harbor 记录，`schema_version` 还同时承担
“选择 Python/Node compiler”的作用。这会让交付物看起来像多个产品，也使 Node、Python、
pnpm 的新增能力被迫继续附着在旧 API 上。

上游 NL2Repo 的测量对象不变：从空 workspace 和自然语言规格出发，生成完整、可安装、
可运行的真实仓库；用冻结上游测试做执行式评测。我们只把任务包装和 verifier 迁移到更
严格的 Harbor separate-verifier 格式，不改变这个测量对象。

## 决策

### 1. 采用一个当前 canonical contract

所有新发布和迁移后的任务使用同一套 canonical model。它不再区分 Python v1、Node v2，
而是使用一个明确的运行时 discriminator：

```text
environment_lock.runtime.language = python | node
environment_lock.runtime.package_manager = uv | pip | npm | pnpm | none
```

`schema_version` 只表示 canonical contract 的形状，不再选择 compiler。迁移后的当前
contract 固定为一个值；旧 v1/v2 不是当前运行时可解析的输入。

canonical task 至少包含：

```text
schema_version
task_id
task_release
metadata { difficulty, category, tags, language }
instruction
source_lock
environment_lock
dependency_bundle
build
tests
metric
execution
lifecycle
oracle_bundle
```

Python、Node/npm、Node/pnpm 只在 runtime-specific adapter 和安装/测试实现上不同，
不再拥有各自的顶层 manifest、compiler、grader 或 dataset schema。

### 2. 不保留兼容 shim

迁移完成后，以下内容不再作为当前包的公共 API：

- `domain/models_v2.py`、`harbor/models_v2.py`、`verification/models_v2.py`；
- `NodeHarborCompiler`、`TaskManifestV2`、`NodeTestReportV2` 等 v2 命名；
- `schema export --version 1.0|2.0` 这类双路 CLI；
- 通过 `schema_version` 分派的双 compiler/double parser；
- 为旧调用者保留的 package-root re-export、别名和 fallback parser。

旧模块和旧 schema 可以作为不可变历史审计资料保存在 release archive，但不能被新的
catalog/compiler/verifier 导入，也不能通过别名重新暴露。

### 3. 只保留必要的 release/version 信息

交付文档和 manifest 中只突出以下版本概念：

- `schema_version`：当前 canonical contract 的唯一形状版本；
- `task_release`：任务内容、隐藏测试、环境或 metric 改变时递增；
- `dataset_release`：数据集成员、分母或评测约束改变时递增；
- source/image/toolchain/content digest：复现所需的不可变身份。

下列字符串属于外部协议或依赖格式，不视为 NL2RepoBench 的多套产品版本，不能为了
美观而删除：Harbor task schema `1.4`、npm/pnpm lockfile version、ATIF format、
`node:test` report format，以及已有历史结果的协议标识。若要退休某个 verifier
protocol，必须整体替换 producer、validator、grader、fixtures 和基线，不能做文本级
`v1`/`v2` 替换。

### 4. 直接迁移 catalog 和旧题

迁移方式是一次性生成新 contract，而不是运行时兼容：

1. 冻结 104 道 `test_files/`、当前 conversion state、历史结果和 artifact 输入的 hash；
2. 将可恢复的 legacy metadata 转成 `catalog/sources/<task-id>/task.toml` 和
   `instruction.md`；
3. 为每题重新确认完整 commit、license、环境 digest、依赖 closure、private tests、
   frozen collection 和 subprocess boundary；
4. 重新编译 canonical manifest、Harbor bundle、verifier 和 dataset；
5. 当前 Package campaign 运行一次 Oracle 及 empty/stub/forgery/install-failure/hang/offline controls；跨运行稳定性另建实验版本；
6. 不能证明 provenance、denominator、offline closure 或 candidate boundary 的题继续
   `blocked`，不能用旧 projection 猜测补齐；
7. 迁移完成后删除旧运行时 reader/compiler/grader，而不是在新代码中保留 fallback。

旧的 `complete` 只代表静态转换完成，不自动升级为 `published`。当前 Package campaign
发布门槛是一次 `valid=true`、collection 与固定分母一致、Oracle reward 不低于 `0.80`，
以及全部控制实验通过。三次独立 Oracle 只作为另行版本化的稳定性实验，不能与当前门禁
混为一谈。

### 5. 统一 verifier report 和 metric

所有 runtime adapter 将 pytest/JUnit、`node:test`、npm/pnpm 的结果归一到一个 leaf
report：

- 稳定 leaf id；
- `passed`、`failed`、`error`、`skipped`、`todo` 状态；
- collection errors；
- trusted runner exit code；
- frozen denominator。

当前 metric contract 统一为 fixed-leaf pass rate：只有 `passed` 计入 passed，所有已经
收集的非 passed leaf 留在固定分母；collection 或 count mismatch 使 verifier 无效。
Runtime adapter 不是新的公开 metric family。

Python 和 Node 的历史报告不重新解释、不与新 release 合并；新报告只由当前 grader
生成。

### 6. 统一状态和 artifact index

State index 的主键改为 `(task_id, task_release)`，记录 manifest digest、生命周期、
stage result hashes、owner、failure reason 和 evidence。旧 conversion-loop state
作为迁移输入和历史证据保存；静态 `complete` 映射到已验证 stage，绝不直接映射到
`published`。

Artifact 仍使用 content-addressed、visibility-separated storage。迁移只复用经过 digest、
size 和 visibility 校验的 bytes，并记录 old digest -> new digest 映射。

### 7. 采用新数据集身份

由于 canonical bytes、manifest digest、denominator 或 verifier contract 会改变，迁移后
数据集必须使用新的 dataset/release identity。旧 Python v1、Node v2、论文/旧 harness
结果不能和当前 Harbor release 合并，也不能声称 score parity。

## 删除顺序

1. 提交本 ADR，并冻结旧输入与历史 artifact index；
2. 实现 unified model、runtime discriminator、report normalizer 和 one-shot migration；
3. 先迁移 Easy/Medium/Hard 各一批、Python/Node/npm/pnpm 各一种形态；
4. 通过 contract、vertical-slice、Oracle/control 和 deterministic regeneration gates；
5. 切换 CI、CLI、docs、OSS key 和 benchmark runner 到新 contract；
6. 用 `rg` 零引用检查确认旧 API 无消费者；
7. 删除 v1/v2 models/compiler/grader/legacy reader 及兼容别名；
8. 在 clean checkout 中从 catalog 重新生成 schema、manifest、Harbor bundles 和报告。

## 验收门槛

- 一个 canonical parser 和一个 canonical compiler entry point；
- 不存在按 `schema_version` 选择 Python/Node 的代码；
- Python、npm、pnpm vertical slice 都能明确通过或 blocked；
- 迁移后的 canonical bytes 和 Harbor bundle 可重复生成；
- 104 道旧题全部有 `published`、`blocked` 或 `excluded` 终态及证据；
- 新 release 的 hidden tests、private bytes、Oracle 和 grader 仍与 agent image 隔离；
- 旧 schema/结果只存在于不可变历史 archive，不被当前运行时读取；
- 只要出现 provenance gap、collection mismatch、私有资产泄漏、非确定 bundle 或未分类
  infrastructure failure，停止批量迁移并修复原因。

## 不在本 ADR 中改变的事项

- NL2Repo 的 0-to-1 repository generation 测量对象；
- 上游真实项目、冻结 revision、官方测试和执行式评分原则；
- Harbor separate verifier、agent/verifier 隔离、固定分母和控制实验；
- 外部 Harbor schema、lockfile 格式和历史 benchmark archive 的原始字节。
