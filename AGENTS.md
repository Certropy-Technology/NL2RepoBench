# NL2RepoBench Agent Guide

本文件是仓库级执行协议，供需要解释 Benchmark、批量生产题目、验证题目或运行评测的 LLM/coding agent 使用。它不替代详细设计文档；遇到冲突时，按下面的权威顺序执行。

## 1. 权威来源与仓库现状

按以下顺序读取并核对：

1. `AGENTS.md`：工作方式、门禁和汇报格式。
2. `docs/task-authoring-guide.zh-CN.md`：出题原理、质量门禁、评分风险和 Harbor 迁移设计。
3. `docs/engineering-roadmap.zh-CN.md`：目标架构、metadata schema、实施阶段和 legacy 退出计划。
4. `docs/metadata-core.zh-CN.md`：现代 uv 技术栈、声明式 catalog、schema 和 Phase 1 CLI。
5. `examples/harbor/ministats/`：Harbor `0.21.0`、task schema `1.4` 的已验证 E2E 示例。
6. `readme.md`：当前 OpenHands 批量运行入口和数据目录。
7. 实际代码：`src/nl2repobench/` 优先；legacy 兼容代码包括 `main.py`、`test_data_service.py`、`openhands/openhands_app.py`、`openhands/post_processor.py`。

当前 checkout 有 104 道发布题，位于 `test_files/<task-id>/`，共声明 25,640 个测试。每题现有发布视图固定为：

```text
test_files/<task-id>/
├── start.md
├── test_case_count.txt
├── test_commands.json
└── test_files.json
```

不要把当前实现描述成 Harbor。当前默认 agent harness 是 OpenHands 0.56 CodeAct，run/eval harness 是本仓库的 Python、Docker 和 pytest 后处理代码。`examples/harbor/ministats` 是迁移示例，不代表 104 题已经完成 Harbor 转换。

## 2. Benchmark 的固定解释

NL2RepoBench 测量 LLM/coding agent 从一份自然语言规格和空工作区出发，生成完整、可安装、可运行代码仓库的能力。它是 0-to-1 repository generation，不是已有仓库修复、补函数或根据公开测试做 test-driven patch。

一次可信评测必须同时固定：

- 公开 instruction 的精确内容；
- 上游仓库 revision、license 和测试版本；
- OS、Python、依赖锁和镜像 digest；
- agent framework、版本、工具、网络和预算；
- 隐藏测试、collection 行为、固定分母和评分公式；
- attempts、infra retry、timeout 和 termination reason。

单题主指标是固定隐藏测试的 pass rate：

```text
task_score = clamp(passed / frozen_total, 0, 1)
dataset_score = mean(task_score for every valid task)
```

数据集使用逐题宏平均，不能汇总所有 passed 后再除以所有测试数，否则测试多的项目会获得更高权重。环境、verifier 或基础设施失败必须单独标注，不能无条件当作模型得 0 分。

论文复现、现有 104 题扩展和新版本数据集是三种不同声明。只要候选门槛、题目内容、网络、agent、环境或 metric contract 有变化，就使用新的 dataset/version 名称，不声称与论文结果直接等价。

## 3. 先识别工作模式

开始工作前明确属于哪种模式；不明确时先询问范围、候选来源、目标题数、输出格式和算力预算。

- `explain`：只解释 Benchmark、架构、指标、局限和运行方式，不修改题目。
- `author-one`：为一个固定 revision 创建完整 authoring truth、发布视图或 Harbor task。
- `author-batch`：按本文件的状态机批量出题，必须维护逐题状态和失败原因。
- `validate`：只运行静态校验、Oracle、负向控制、盲审或 parity 检查。
- `run-benchmark`：运行已发布题，不在运行过程中改题。
- `analyze-results`：汇总 reward、失败类型、成本和覆盖率，不混入 authoring 改动。

不要在同一次正式 benchmark run 中边跑边修改 instruction、测试、镜像或分母。任何此类修改都使已产生结果失效，必须提升版本并从头重跑受影响的控制和 trials。

## 4. 批量出题总原则

大规模出题采用“小批次、可重跑 stage、单题隔离、统一集成”的方式：

1. 首批只做 5 到 10 题 pilot，覆盖 Easy、Medium、Hard 和不同项目形态。
2. pilot 稳定后，每批建议 10 到 20 题；并发受 Docker、磁盘、API rate limit 和 reviewer 数量约束。
3. 不同 task 可以并发；同一 task 的 source freeze、spec、tests 和 verifier 不允许多个 writer 并发修改。
4. 并行 worker 只写各自 `catalog/tasks/<task-id>/` 或独立 worktree。canonical manifest、共享索引、dataset manifest、`config.json` 和发布目录由 compiler/integrator 串行更新。
5. 每个 stage 只消费上一阶段已版本化 artifact。失败后从最后一个可信 stage 恢复，不从头盲目重做。
6. LLM 可起草规格和 traceability，但不能自行批准 license、Oracle、测试覆盖或最终发布门禁。

推荐流水线：

```text
discover
  -> freeze-source
  -> build-ground-truth-image
  -> collect-tests
  -> extract-api-inventory
  -> draft-spec
  -> trace-tests-to-spec
  -> build-task-package
  -> oracle
  -> negative-controls
  -> blind-review
  -> pilot
  -> publish
```

## 5. 单题状态机与产物

每题只能按下面状态向前推进。记录 `status`、`owner`、输入 hash、输出 hash、开始/结束时间、重试次数和失败分类。

| 状态 | 必需输出 | 通过条件 |
| --- | --- | --- |
| `discovered` | 候选 manifest | revision 不可变，license 可接受，项目不与现有题重复 |
| `frozen` | source lock、镜像定义、baseline logs | 冻结上游代码在最终环境全量通过 |
| `inventoried` | API inventory、test plan | public API、CLI、fixtures、test-to-behavior 映射完整 |
| `specified` | `instruction.md` | 只看规格可推导所有隐藏断言，不泄漏实现 |
| `packaged` | private tests、verifier、发布视图/Harbor task | 隐藏资产与 agent 环境隔离 |
| `oracle-passed` | Oracle reward、JUnit、日志 | 至少一次 1.0；发布前要求三次独立 1.0 |
| `controls-passed` | empty/stub/forgery/offline 结果 | 无异常高分，verifier 不被候选篡改 |
| `reviewed` | 两份 review 记录 | blind review 和 traceability review 均通过 |
| `piloted` | 多 agent/model 结果 | 难度和失败归因合理，无系统性 spec/env/verifier 问题 |
| `published` | version、content hash、dataset entry | 所有门禁完整，发布内容不可变 |

Human 只编辑声明式 catalog；canonical manifest 是 compiler 的机器输出，`test_files/` 是 legacy projection：

```text
catalog/
├── datasets/<dataset-id>/dataset.toml
└── tasks/<task-id>/
    ├── task.toml
    └── instruction.md

catalog source -> canonical manifest -> Harbor bundle / legacy projection
```

禁止人工修改 generated `manifest.json`、Harbor bundle 或 `test_files/` 来绕过 catalog。当前可用命令以 `uv run nl2repo --help` 为准；不要声称路线图中的未实现命令已经可用。

## 6. Candidate 与 Ground Truth 门禁

候选 manifest 至少包含：`task_id`、`upstream_url`、完整 commit SHA、license、Python 版本、LOC、public API 数、test count、最近更新时间、difficulty 和 category。

拒绝或暂停以下候选：

- revision 是 branch、`latest` 或其他浮动引用；
- license 不清楚或不允许所需分发方式；
- 依赖真实付费账号、不可冻结服务、专用硬件或不确定远端数据；
- 冻结源码无法在最终环境全量通过；
- 测试主要检查 lint、文档、元数据，不能代表核心行为；
- 是既有题的 fork、改名包、兼容层或高度近似实现；
- 隐藏断言依赖无法在公开规格中合法说明的信息。

冻结时保存 commit、submodule、lockfile、build command、test command、stdout、stderr、JUnit、collected count、wall time 和 image digest。只允许修复环境，不允许修改功能源码来迎合测试。

错误必须归入且只归入一个主类：

- `source`：冻结上游实现自身失败；
- `spec`：公开规格不足、矛盾或泄漏；
- `environment`：OS/Python/依赖/构建不兼容；
- `verifier`：collection、评分、隔离或 artifact 错误；
- `model`：环境与题目有效，但 agent 未完成实现；
- `infrastructure`：镜像拉取、磁盘、容器、API、机器故障。

只有 `infrastructure` 可在不改变 trial 身份的前提下自动重试。其他类别先修题或接受模型失败，并保留审计记录。

## 7. 规格撰写协议

公开规格统一包含：

1. `Project Description`：目标、用户和边界；
2. `Supports`：Python、依赖、安装、目录和入口要求；
3. `API Usage Guide`：逐个 public API/CLI 的行为契约；
4. `Implementation Notes`：跨模块约束和少量可验证示例，不给算法答案。

每个 API 条目至少写清 import path、完整 signature、输入域、返回类型与形状、状态/副作用、顺序与确定性、异常契约、普通示例和必要的边界示例。

规格审核采用双向 traceability：

- 每个隐藏 assertion 都能映射到公开行为；
- 每个核心公开承诺至少有一个测试覆盖；
- packaging、re-export、CLI entry point、Unicode、空输入、错误输入和状态变化不能因只提取 AST 而遗漏。

禁止复制函数体、内部 helper、上游测试断言、完整算法或大段源码。也禁止只写“实现一个类似 X 的库”却在隐藏测试中要求未公开的精确行为。标准库模块不得列为 PyPI runtime dependency。

## 8. Verifier 与评分协议

优先保留冻结 revision 的原始上游 pytest，只在 runner 层增加结构化报告和隔离。Verifier 必须：

- 使用固定、自动 collection 得到的 `frozen_total`；
- 生成 JUnit/JSON 等结构化结果，不依赖 pytest 控制台正则；
- 检查每条 setup/test 命令退出码和 collection error；
- 由 verifier 自己写 `/logs/verifier/reward.json`；
- 默认断网运行，依赖已预置或锁定；
- 看不到 agent 写入的伪造 reward，并防止隐藏测试被覆盖；
- 把安装失败、JUnit 缺失和 collection error 记录到 grading details。

当前旧 harness 的 `start_app()` 和 `only_test.py` 把 raw `passed` 写入 `score`。在该代码修复前，结果分析必须读取 `post_process_result.pytest_results.success_rate`，不能跨题比较 `score`。旧 harness 还使用 pytest 文本正则和人工分母，因此正式新数据集优先采用结构化 verifier，并明确声明与旧结果的差异。

每题最低控制集：

```text
Oracle/upstream implementation -> 1.0
empty workspace                -> near 0
packaging + stub functions     -> low score
forged test/reward files       -> cannot affect grading
offline verifier               -> completes successfully
```

Oracle 失败时依次检查 environment、artifact 路径、安装、collection、固定分母和 reward 输出。不得通过删除真实功能断言来让 Oracle 变绿。

## 9. Harbor 任务协议

生产题优先使用 separate verifier。参考 `examples/harbor/ministats/`，但用冻结真实项目和上游测试替换示例内容。

标准布局：

```text
<task>/
├── instruction.md
├── task.toml
├── environment/Dockerfile
├── solution/solve.sh
└── tests/
    ├── Dockerfile
    ├── test.sh
    ├── grade.py
    └── <hidden tests>
```

`task.toml` 必须填写 task name/version、3 到 8 个 keywords、difficulty/category/tags、metric contract、expected count、agent/verifier timeout、资源、network mode、artifact 和 separate verifier。Oracle、隐藏测试、judge prompt、API key 和 grader dependency 不得进入 agent image。

先检查 CLI 版本。该仓库示例要求 Harbor `0.21.0` 和 schema `1.4`；旧的 `0.15.0` CLI 不兼容。实际命令为：

```bash
harbor run -p examples/harbor/ministats -a oracle
harbor run -p examples/harbor/ministats -a openhands -m '<provider>/<model>'
```

新题先运行 Oracle，再运行 empty/nop 和 stub 控制，最后才运行真实 agent。不要仅因 Harbor 能执行就声称与旧 harness parity；必须在 Easy/Medium/Hard 的 5 到 10 题上比较 passed/total、setup errors、runtime、steps 和 termination reason。

## 10. 旧 OpenHands Harness 的运行协议

旧 harness 从 `config.json` 读取模型节点、`proNameList` 和 `max_pool_size`，然后执行：

```bash
python main.py
```

运行前：

- 确认 Docker daemon、OpenHands app/runtime 镜像和每题测试镜像存在；
- 确认 `proNameList` 与 `test_files/` 目录名完全一致；
- 根据 CPU、内存、磁盘和模型 rate limit 设置并发，不机械使用 20；
- 不在日志、提交或汇报中暴露 `sk`；
- 为多机运行准备共享文件系统或显式 artifact 传输。

`only_test.py` 当前硬编码 task UUID 和项目名，不是通用批量入口。不要直接用它批量跑题，除非先把参数化改造作为独立、经过测试的代码变更。

运行产物位于 `workspaces/` 和 `result/`。保留 workspace zip、agent trajectory、post-process log、每条命令结果和 pytest details。当前 app 容器 `auto_remove=True` 后代码假定 exit code 为 0，因此分析时不能把记录的 0 当作可靠的 agent 正常退出证据。

## 11. 批量执行与恢复

批量 orchestration 必须满足：

- 先输出本批 task list、版本、模型、attempt 数、并发、预计成本和停止条件；
- 任务 ID 唯一，重复运行使用新的 run/trial ID，不覆盖旧结果；
- 同一 task 的多个 attempts 相互隔离；
- 每完成一题立即持久化结果，不等整批结束；
- 失败记录 stage、分类、命令、exit code 和 artifact 路径；
- infra retry 有上限和退避，不能无限循环；
- 收到停止信号后不再启动新任务，允许在途任务收尾并保存状态；
- 恢复时只重跑未完成或纯 infra 失败的 trials。

并发 worker 不得共同编辑 `config.json`。需要不同模型或批次时，为每次运行生成独立配置或串行切换，并保存脱敏后的 resolved config。

## 12. 结果分析与讲解

报告至少包含四层：

1. **Dataset**：名称、版本、题数、难度分布、有效题数、排除题及原因；
2. **Experiment**：agent/model/version、网络、预算、attempts、并发和环境 digest；
3. **Scores**：逐题 passed/total/pass rate、宏平均、按难度/类别分组；
4. **Reliability**：model/spec/environment/verifier/infra 失败数，timeout/crash 数，trajectory/token/cost 覆盖率。

不要：

- 用 raw passed count 排名不同题；
- 把缺失 token/cost 当作 0；
- 把 infra failure 解释成模型不会做；
- 只报总均分而隐藏有效题数和 excluded tasks；
- 用一次随机 attempt 推断稳定能力；
- 在未做 parity validation 时把 Harbor 与论文/旧 harness 分数直接合并。

推荐批次汇报表：

```text
task_id | version | status | oracle | empty | pilot mean | failure class | artifacts
```

推荐 benchmark 结论顺序：先说明测量对象和实验约束，再给总体与分组结果，然后解释失败构成、成本/覆盖率和不可比较因素，最后列出下一步。把“模型失败”和“题/系统无效”明确分开。

## 13. LLM 工作纪律

- 开始前读取相关文档和一个最接近的完整样例，不凭记忆发明 Harbor schema 或仓库命令。
- 复杂批次先建立任务清单，始终只有一个共享集成任务处于写入状态。
- 可以让子 agent 并行分析不同候选，但要求结构化交付；主 agent 负责合并、验证和最终决定。
- 不修改与当前 task 无关的用户变更，不重置 dirty worktree。
- 不提交 secret、私有测试内容到公开位置，也不在公开 instruction 中透露 grader。
- 生成的 JSON/TOML/YAML 必须用解析器校验；shell 使用 `set -euo pipefail` 或显式处理所有退出码。
- 任何“已通过”“可复现”“等价”声明都必须附实际命令、版本和 artifact 证据。
- 工具或版本不可用时明确阻塞原因；不要伪造测试结果或把未运行写成已验证。

## 14. Definition of Done

单题完成必须同时满足：

- source lock、license、依赖和 image digest 完整；
- instruction 与 hidden assertions 双向可追溯；
- frozen total 自动生成并与实际 collection 一致；
- Oracle 三次独立运行为 1.0；
- empty、stub、forgery 和 offline 控制通过；
- 两名审核人完成 blind/spec traceability review；
- pilot 没有未解决的 spec/environment/verifier 系统性问题；
- task version、content hash、日志、JUnit、reward details 和 artifact manifest 可追踪；
- README 或任务说明包含准确的运行命令和 verifier 维度。

整批完成还要求：所有题达到终态；失败和排除项有原因；dataset manifest 不引用可变资源；宏平均只使用有效且 metric contract 一致的题；最终报告能复现本批使用的配置、版本和输入集合。
