# NL2RepoBench 出题、验题与 Harbor 接入手册

本文面向需要批量生产 NL2RepoBench 题目的出题人、审核人和评测基础设施维护者。目标不是把一个开源仓库的 README 改写成长文，而是产出一个满足以下条件的可复现实验单元：

```text
单份自然语言规格 + 空工作区
  -> Agent 从零生成完整 Python 仓库
  -> 隐藏的上游 pytest 套件验证
  -> 固定分母的 test pass rate
```

配套的最小可运行题目位于 [`examples/harbor/ministats`](../examples/harbor/ministats/README.md)。

本手册与[工程化改造长期路线图](engineering-roadmap.zh-CN.md)共同构成出题规范。路线图规定目标架构和迁移阶段；本手册规定单题如何达到发布门禁。两者冲突时，以路线图中已批准的 schema、metric contract 和 lifecycle 规则为准。

### 0. 事实源与发布边界

新题必须先建立 canonical authoring manifest。`authoring/<task-id>/` 是唯一可编辑事实源，Harbor task 和旧 `test_files/<task-id>/` 都是单向、确定性生成物；禁止长期维护三套目录的双向同步。

公开仓库只保存不含 secret/private bytes 的 manifest、schema、content digest 和公开 provenance。private tests、Oracle、license evidence 或受限依赖放在访问受控的私有 Git、对象存储或 registry 中，公开 manifest 只保存 opaque artifact ref、digest、size、visibility 和 provenance classification。

生产执行以 Harbor Task/Dataset/Job/Trial 为准。旧 OpenHands harness 只用于历史结果复现和 parity 对照，不作为新数据集的正式执行后端。

## 1. 先明确题目测什么

NL2RepoBench 测的是从 0 到 1 的完整仓库生成，不是已有仓库修复，也不是补一个函数：

- 输入只有一份自然语言规格，工作区没有实现骨架和函数签名文件。
- Agent 自己完成架构、打包、跨文件实现、依赖管理和自测。
- 最终实现使用目标项目冻结版本的上游测试验证。
- 单题主分数是通过测试数除以冻结的测试总数；数据集总分是所有单题分数的宏平均，不能让大测试集项目获得更高权重。

论文中的原始基准包含 104 个 Python 项目，题目平均输入约 18,800 tokens。论文的候选项目门槛包括 300 到 120,000 LOC、至少 10 个 GitHub stars、近三年有更新、带 pytest 测试且冻结版本能够全量通过。难度按原项目 LOC 分为 Easy（不超过 1,500）、Medium（1,500 到 4,000）和 Hard（至少 4,000）。这些是复现论文数据集时的基线；扩题时可以调整，但必须给新数据集单独命名并记录偏差。

来源：[NL2Repo-Bench 论文](https://arxiv.org/abs/2512.12730)、[项目仓库](https://github.com/multimodal-art-projection/NL2RepoBench)。

## 2. 当前仓库实际使用的 Harness

“Harness”在这里至少有三层，不能只回答 OpenHands：

| 层次 | 当前实现 | 职责 |
| --- | --- | --- |
| Agent harness | OpenHands 0.56，默认 CodeActAgent，headless batch | 接收任务、调用模型和工具、写工作区 |
| Run harness | 本仓库的 `main.py`、`test_data_service.py`、`openhands/openhands_app.py` 和 `python-on-whales` | 读任务、分配端口、启动容器、并发执行、保存结果 |
| Eval harness | `openhands/post_processor.py` 加每题 `ghcr.io/multimodal-art-projection/nl2repobench/<task>:1.0` 镜像 | 注入生成仓库、运行上游 pytest、解析通过数 |

当前执行链路如下：

```text
config.json
  -> main.py
  -> test_data_service.py 读取 test_files/<task>/{start.md,count,commands,files}
  -> ThreadPoolExecutor
  -> OpenHands 0.56 app container
  -> OpenHands 0.56 runtime container 挂载 host workspace
  -> Agent 根据 start.md 从空目录生成仓库
  -> post_processor.py 打包 workspace
  -> 删除 Agent 生成的 packaging 文件和已知 test paths
  -> FROM 每题隐藏测试镜像并 COPY workspace
  -> 执行 test_commands.json
  -> 从 pytest 文本摘要提取 passed/failed/errors
  -> result/<task>_bo1.json
```

论文主实验主要使用 OpenHands-CodeAct；Cursor CLI 和 Claude Code 是额外的 agent framework 对照。因而严谨表述应是：**这份 checkout 的默认 agent harness 是 OpenHands CodeAct，完整 benchmark harness 是仓库自带的 Python + Docker + pytest runner。它当前不是 Harbor。**

### 当前实现需要先修正的评分风险

大规模正式运行前应先处理这些问题：

1. `start_app()` 把 `pytest_results['passed']` 写入 `score`，而论文指标是 `success_rate`。不同题目的测试数不同，raw passed count 不能直接比较。
2. pytest 结果依赖正则解析控制台摘要，容易受 pytest 版本、collection error、多次 pytest 命令和输出格式影响。应改为 JUnit/JSON 或 pytest plugin 产生结构化结果。
3. `test_case_count.txt` 是人工维护分母。它必须由冻结环境中的实际 collection 自动生成并在 CI 中复核。
4. OpenHands app 容器使用 `auto_remove=True`；容器消失后代码直接假定退出码为 0，不能区分正常结束与崩溃。
5. 每题执行命令允许任意 shell 字符串。题目合入前必须在冻结镜像中审核并运行，不能只做 JSON 格式检查。
6. Agent workspace、原始输出 zip、测试输入、基础设施失败和最终 reward 要分开保存，不能把 setup/verifier 失败记成模型能力 0 分。

## 3. 单题标准目录与权威数据

每道题都必须有一份不可混淆的 canonical authoring truth。无论最终是否使用 Harbor，生产侧都不能把发布视图当作事实源：

```text
authoring/<task-id>/
  source.lock.json          # upstream URL、commit/tag、license、Python、image digest
  instruction.md            # 唯一公开给 Agent 的规格
  api-inventory.json        # AST 提取的 public API/signature 清单
  test-plan.json            # test -> API/behavior 映射及固定分母
  environment/              # 可复现的 build definition
  private-artifact.refs.json # private tests/Oracle 的 opaque refs、digest 和权限信息
  review.md                 # 人工审核、偏差、例外和签字
```

当前 `test_files/<task>/` 的四个文件只是发布/运行视图：

| 文件 | 含义 | 生产要求 |
| --- | --- | --- |
| `start.md` | 公开规格 | 必须能独立实现，不得依赖隐藏 README 或聊天补充 |
| `test_case_count.txt` | 分数分母 | 从冻结环境自动 collection，不手填 |
| `test_commands.json` | 安装和测试命令 | 所有命令逐条检查退出码；测试命令需保留 collection error |
| `test_files.json` | legacy runner 用来移除的测试路径 | 由上游测试清单生成，并防止父子路径遗漏；不是新题的事实源 |

新题禁止直接编辑 `test_files/` 作为事实源。legacy exporter 可以为历史复现生成这四个文件，但 CI 必须检查生成结果与 manifest 的内容 hash 一致。

### 3.1 必需 metadata 与 schema

每题至少关联以下版本化记录：

- `TaskManifest`：task ID/version、difficulty/category/tags、公开 instruction ref、运行约束和 artifact refs；
- `SourceLock`：upstream URL、完整 commit、submodules、license evidence 和 source hash；
- `EnvironmentLock`：OS、Python、系统包、基础镜像 digest、build/runtime/test dependency locks；
- `DependencyBundle`：离线 wheelhouse 或等价依赖闭包、文件 hash 和生成记录；
- `TestManifest`：测试 bundle、命令、冻结 collection 数、测试框架和 test hash；
- `MetricContract`：passed/failed/error/skipped/xfail/collection mismatch 的精确定义；
- `ReviewRecord`、`ControlRecord` 和 `TaskLifecycleRecord`。

所有 schema 必须包含 `schema_version`、稳定 ID、canonical serialization、content hash、required/optional 定义、migration 和跨记录引用检查。`unknown`、`missing` 和空值不能混用。

private artifact 必须通过统一的 `PrivateArtifactResolver` 物化：运行时注入凭证，校验 digest/size，返回只读临时内容，记录无 secret 的审计，并在构建后清理。无权限、对象缺失或 digest 不匹配必须 fail closed。

## 4. 批量出题流程

### 阶段 A：候选项目入池

为每个候选仓库建立 manifest，至少记录：

```yaml
task_id: ministats
upstream_url: https://github.com/example/ministats
revision: 0123456789abcdef
license: MIT
python: "3.12"
loc: 980
source_files: 12
public_api_count: 19
test_count: 86
last_upstream_update: 2026-06-01
difficulty: easy
category: utility-library
task_version: "1.0.0"
image_digest: "sha256:..."
metric_contract: fixed-test-pass-rate-v1
status: discovered
```

自动门禁：

- revision 必须是不可变 commit，而不是浮动 branch 或 `latest`。
- license 必须允许使用、修改和分发测试/派生材料。
- 排除需要真实付费账号、不可冻结远端服务、专用硬件或非确定性数据才能通过的项目。
- 排除测试主要验证 lint、文档拼写或仓库元数据而非功能的项目。
- 排除与既有题高度重复的 fork、改名包和兼容层。

人工门禁：

- 项目功能边界是否能靠文字完整说明。
- 上游测试是否真的覆盖项目核心，而不只是 smoke test。
- 是否存在无法公开描述但测试强依赖的隐式数据或行为。
- 项目名是否会让联网 Agent 直接下载完全相同的源码。若允许公网，这属于必须显式报告的 contamination 风险。

### 阶段 B：冻结 Ground Truth

1. 在干净容器里 checkout 固定 revision。
2. 按上游文档安装，再补齐确实缺失的系统依赖和版本 pin。
3. 运行完整上游测试，保存命令、stdout、stderr、JUnit、collected count 和 wall time。
4. 只修环境问题，不修改功能源码来迎合测试。
5. 对 README、LICENSE 存在性等与功能无关的构建约束，可在镜像中预置空文件或做可审计的 packaging relaxation。
6. 固定最终 Dockerfile、`EnvironmentLock`、`DependencyBundle` 和 image digest。Oracle 必须在这个最终镜像中达到 1.0。
7. verifier 必须在清空 pip cache 的 `no-network` 环境中完成安装、collection 和测试；不能依赖运行时公网下载。

基线记录必须区分：

```text
source              冻结上游实现自身失败
spec                公开规格不足、矛盾或泄漏
environment         OS/Python/依赖/构建不兼容
verifier            collection、评分、隔离或 artifact 错误
model               环境和题目有效，但 agent 未完成实现
infrastructure      image pull、disk、timeout、container runtime 等故障
```

“测试断言失败”是证据，不是独立的主分类；只有 source 为零、环境稳定且全量测试通过，候选题才能进入写题。

### 阶段 C：反向理解与 API Inventory

先机器提取，再人工解释：

- package/module 树；
- public function、class、method、property、constant 和 exception；
- 完整 signature，包括 positional-only、keyword-only、默认值和异步语义；
- re-export 和 import path；
- 每个测试引用的 API、fixture、CLI entry point 和文件格式；
- 跨模块状态、缓存、并发、I/O 和错误边界。

建立 `test -> behavior -> public contract` 映射。每个隐藏断言都必须能追溯到规格中的公开行为；反过来，规格承诺的核心行为也应有测试。

AST inventory 只能证明“名字出现了”，不能证明语义足够。最终审核要回答：一个没有源码、只有该文档的合格 Python 工程师，是否能推导出每个隐藏断言所需的行为？

### 阶段 D：写公开规格

统一使用四段结构：

1. **Project Description**：项目解决什么问题、边界是什么。
2. **Supports**：Python 版本、允许的第三方依赖、安装方式、要求的目录和入口。
3. **API Usage Guide**：逐 API 的 signature、语义、输入输出、异常、状态变化和边界。
4. **Implementation Nodes**：跨模块约束和少量可验证示例；不提供算法答案。

每个 API 条目至少包含：

```text
Import path
Signature
Input domain
Return type and shape
State/side effects
Ordering and determinism
Error contract
One ordinary example
One boundary example when relevant
```

写题时避免两种极端：

- **信息不足**：只写“实现一个类似 requests 的库”，隐藏测试却要求精确异常、排序或编码行为。
- **答案泄漏**：复制函数体、内部 helper、上游测试断言、完整算法或大量源代码片段。

当前一些 `start.md` 含有接近源码的函数体、完整内部目录和不合理的“标准库依赖版本”。扩题时应改成行为契约。标准库模块如 `asyncio`、`io`、`tempfile` 不应出现在 PyPI runtime dependencies 中。

### 阶段 E：构造隐藏测试

优先保留未修改的上游 pytest。必要修改只能发生在 runner 层，例如加入 `--continue-on-collection-errors` 或结构化报告插件，不改变断言语义。

测试分层建议：

| 层 | 目的 | 典型内容 |
| --- | --- | --- |
| Packaging | 仓库能安装和导入 | wheel/editable install、entry point、re-export |
| Contract | 公开 API 正常行为 | 代表性输入输出、类型、排序 |
| Boundary | 防止只做 happy path | 空输入、Unicode、极值、invalid type |
| Integration | 验证跨文件一致性 | CLI 到 library、serialization、plugin registration |
| Regression | 保留上游真实语义 | 冻结 revision 的历史 bug tests |

禁止：

- 用测试检查没有写入公开规格的内部 helper 名；
- 根据某个模型的输出临时添加只针对该实现的断言；
- 让测试访问公网、当前时间、随机未固定 seed 或开发机路径；
- 把 pytest collection error 当作“没有测试所以通过”；
- 仅看最后一条 shell 命令退出码，忽略前面的安装失败。

主分数应由结构化测试报告生成：

```text
passed = collected - failed - errors - skipped
reward = clamp(passed / frozen_total, 0, 1)
```

若 benchmark 的既定语义不把 skipped 视为失败，可调整，但必须全数据集一致并写入版本化 metric contract。

### 阶段 F：Oracle 与负向控制

每题至少执行以下控制：

| 控制 | 预期 |
| --- | --- |
| 冻结上游实现/Oracle | reward = 1.0 |
| 空工作区 | reward 接近 0，且 verifier 正常结束 |
| 只有 packaging 和空函数 | 只能得到很低分，不能因 import 成功获得高分 |
| 测试文件同名伪造 | 不影响隐藏 verifier |
| Agent 写假 reward 文件 | 不影响 verifier 自己生成的 reward |
| 断网 verifier | 仍能完成安装和测试 |

Oracle 失败时按顺序排查：environment、artifact 路径、安装命令、test collection、分母、reward 输出。不要通过放宽功能断言来让 Oracle 变绿。

### 阶段 G：盲审与 Pilot

1. 一名未看源码的工程师只用 `instruction.md` 实现或逐项审查。
2. 另一名审核人做 hidden-test-to-spec traceability review。
3. 至少选择 5 到 10 个候选题，用 2 到 3 个能力层次不同的 agent/model 做 pilot。
4. 对每个失败标注 `model`, `spec`, `environment`, `verifier`, `infra`。
5. 只有 `spec/environment/verifier` 问题允许改题；模型不会规划或实现不是改简单的理由。基础设施故障只按 retry policy 重试，不改变题目内容。
6. 改动 instruction、测试、镜像或 metric 后必须提升题目版本并重跑所有控制。

### 阶段 H：发布门禁

一题只有同时满足下列条件才能合入：

- source revision、license、image digest 和依赖锁完整；
- Oracle 三次独立运行均为 1.0；
- collected count 与冻结分母一致；
- 所有 hidden assertions 能映射到公开规格；
- 空实现和伪造测试不能获得异常高分；
- verifier 无公网和模型 API 依赖；
- Agent 看不到 hidden tests、Oracle 和 reward 生成逻辑；
- 结果中保存 lock、reward、JUnit、stdout/stderr、artifact manifest 和 trajectory coverage；
- 两名审核人完成签字；
- 题目 ID、版本和内容 hash 唯一。
- `TaskLifecycleRecord` 已进入 `published`，并且 publish transaction 同时写入 dataset entry；`blocked`/`excluded` 必须保存 owner、reason、evidence 和 approval refs。

## 5. 大量出题时的流水线

推荐把批量生产拆成可重跑 stage，而不是多人直接编辑 `test_files/`：

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

每个 stage 只消费上一阶段的版本化 artifact，并输出 manifest。建议 CI 至少提供这些命令：

下面是目标 CLI 契约；当前 checkout 尚未实现这些命令，不得在汇报中写成“已经可用”。

```text
validate-manifest <task>
validate-spec <task>
build-image <task>
collect-tests <task>
run-oracle <task>
run-negative-controls <task>
validate-harbor-task <task>
publish-task <task>
```

每个 stage 应记录统一的 `StageResult`：

```text
stage_name/version, status, input_hash, output_hash,
owner, worker_id, claim_id, lease_expires_at,
retry_count, max_retries, backoff, next_retry_at,
failure_class, logs, tool_versions
```

同一 task/stage 的执行必须使用 claim/lease/heartbeat；只有 `infrastructure` failure 可自动 retry，并且必须有最大次数和退避。修改 instruction 只失效 downstream stages，不重跑 source freeze。两个 worker 竞争同一 task/stage 时只能一个获得 claim。

批量 dashboard 不只显示 reward，还应显示：

- Oracle/empty/stub 分数；
- frozen/actual collected count；
- spec 覆盖的 API 比例和 test traceability 比例；
- environment/verifier/infrastructure failure rate；
- Agent 正常结束、超时和崩溃比例；
- trajectory、tokens、cost 的 coverage，而不是把缺失值记成 0。

## 6. 与 Harbor 的原生适配结论

结论：**新数据集应以 Harbor 为正式执行后端，但不是把现有四个文件改名就能获得可信的原生适配。需要 canonical manifest 到 Harbor bundle 的单向确定性 compiler，并做原 harness 与 Harbor 的 parity validation。**

映射关系：

| NL2RepoBench | Harbor |
| --- | --- |
| `start.md` | `instruction.md` |
| 每题测试基础镜像 | `[verifier.environment]` 的独立镜像或 `tests/Dockerfile` |
| 空生成目录 | Agent environment 的 `/workspace` |
| 生成仓库 zip | `artifacts = ["/workspace"]` |
| `test_commands.json` | `tests/test.sh` |
| `test_case_count.txt` | verifier 内冻结的 expected total |
| pass rate | `/logs/verifier/reward.json` 的 `reward` |
| canonical DatasetManifest | Harbor Dataset |
| ThreadPoolExecutor | Job 的 trial concurrency |
| OpenHands 0.56 | Harbor 内置 `openhands` agent，做论文复现时需 pin 版本和参数 |
| workspace/result/log | Trial artifacts、result、agent/verifier logs、lock |

Harbor 特别适合这里的原因：

- 原生 Task/Dataset/Trial/Job 模型；
- Docker 和多种 sandbox provider；
- 内置 OpenHands、Claude Code、Codex 等 agent；
- 数值 reward 和多指标 reward；
- artifact、日志、锁定配置和 ATIF trajectory；
- separate verifier 可以把上游测试和评分代码与 Agent 隔离。

正式适配应采用 separate verifier：

```text
Agent environment
  /workspace                 # 只有 Agent 生成的仓库
       |
       | Harbor configured artifact, same absolute path
       v
Separate verifier environment
  /workspace                 # 作为候选 artifact 输入，再复制到 verifier 私有临时目录
  /tests                     # verifier image 内的隐藏上游测试
  /logs/verifier/reward.json
```

不能直接使用 shared verifier 的理由不是它一定会提前泄漏 `/tests`，而是正式 benchmark 还需要隔离测试依赖、grader、secrets 和 Agent 留下的进程/环境变更；独立镜像的边界更清楚。Harbor compiler 必须解析 `EnvironmentLock`、`DependencyBundle` 和授权 private refs；无凭证、错误 digest 或对象缺失时 fail closed。

private asset leakage scan 的范围必须包括 agent image 的每个 OCI layer、最终 filesystem、SBOM/build provenance、build context 清单和导出的 agent artifacts，并保存机器可读报告。必须有“COPY hidden fixture 后删除”的负向测试，证明下层 layer 泄漏会被拒绝。

### 需要保持一致的实验变量

为了让 Harbor 分数与论文/旧 harness 可比较，至少固定：

- 104 题的精确 revision 和测试镜像 digest；
- instruction bytes；
- OpenHands 版本、CodeAct 配置、tools、browser、iteration/timeout 和模型参数；
- Agent 网络权限和能否下载同名上游项目；
- Python/OS/dependency 环境；
- test commands、collection 行为、分母和 pass-rate 公式；
- attempts 与 infrastructure retry 的区分。

Harbor 的 timeout 是 wall-clock 控制，论文主实验称不限制 interaction rounds。两者不是同一个预算；应给足 wall-clock timeout，并同时记录真实 steps，而不是声称语义天然等价。

建议迁移顺序：

1. 先转换一个 Easy 题，完成 Oracle、empty 和 stub controls。
2. 选 Easy/Medium/Hard 共 5 到 10 题，在旧 harness 和 Harbor 上使用相同 model/agent 配置各跑多次。
3. 比较逐题 passed/total、setup errors、runtime、steps 和 termination reason，不只比较总平均。
4. 解释完所有系统性差异后再批量生成 104 题。
5. Harbor 适配器、原始数据和 metric contract 分别版本化。

Harbor 版本、task schema、agent adapter 和所有基础镜像 digest 必须写入并实际解析校验的 `toolchain.lock`。当前 `examples/harbor/ministats` 使用 mutable `python:3.12-slim` base tag，只能作为 E2E demo；在 digest pin 完成前，不得把它作为 production-publishable golden fixture。不要用 mutable Harbor main、Git branch 或 image tag 作为发布依赖。

参考：[Harbor 文档](https://www.harborframework.com/docs)、[Task Structure](https://www.harborframework.com/docs/tasks)、[Agents](https://www.harborframework.com/docs/agents)、[Harbor GitHub](https://github.com/laude-institute/harbor)。

## 7. 最小 E2E 示例怎么读

[`examples/harbor/ministats`](../examples/harbor/ministats/README.md) 展示了一道小型但完整的题：

- Agent 从空 `/workspace` 创建可安装的 Python package；
- instruction 只公开行为契约；
- `/workspace` 作为 configured artifact 原路径传给 separate verifier；
- hidden tests 在 `tests/Dockerfile` 中构建，不进入 Agent 环境；
- verifier 使用 JUnit 结构化结果计算 18 个冻结测试的 pass rate；
- `solution/solve.sh` 提供 Oracle；
- `README.md` 给出 Oracle 和真实 agent 的运行方式。

它故意很小，适合先验证基础设施。生产题应替换成冻结的真实开源项目和原始上游测试，但沿用同样的隔离、reward 和验证边界。正式迁移前还要补齐 digest-pinned image、offline dependency closure、metadata manifest、通用 verifier 和控制实验；该示例本身不代表 104 题已完成 Harbor 迁移。
