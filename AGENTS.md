# NL2RepoBench Agent Guide

本文件是仓库级执行协议。它约束出题、编译、验证、运行和提交行为；详细设计以
`docs/` 和实际代码为准。遇到数字、状态或命令与旧报告不一致时，以当前 Git
checkout、声明式 catalog 和已实现 CLI 为准，不以历史记忆或旧报告为准。

## 1. 权威来源与当前架构

开始工作时按以下顺序核对：

1. 本文件，以及更具体目录中的 `AGENTS.md` 或 `CLAUDE.md`；
2. `docs/task-authoring-guide.zh-CN.md`、`docs/engineering-roadmap.zh-CN.md`、
   `docs/phase2-harbor-verifier.zh-CN.md` 和 `docs/network-policy.md`；
3. `src/nl2repobench/`、`tests/`、`harbor-runner/` 和 `examples/harbor/ministats/`；
4. 当前 `catalog/sources/`、`catalog/tasks/`、`catalog/datasets/` 和 reports。

当前的声明与生成边界是：

```text
catalog/sources/<task-id>/task.toml + instruction.md
    -> canonical catalog manifest
    -> language/package-manager compiler
    -> catalog/tasks/<task-id>/ Harbor runtime
```

- `catalog/sources/<task-id>/` 是人编辑的声明式 source。任务级 authoring truth、
  API inventory、审计记录和小型 evidence 也放在这里。
- `catalog/tasks/<task-id>/` 是 compiler 生成的、可由 Harbor 直接消费的 runtime
  projection。有效 production task 的生成 runtime 必须可追溯并提交；blocked task
  不得保留对应 runtime。
- `catalog/sources/<task-id>/harbor/` 可以是 compiler 的 source asset 或 legacy
  兼容输入。不能仅凭是否存在 `harbor/` 判断题目是否满足当前 production gate。
- `test_files/` 只是 104 题的 legacy 输入视图，不是当前 catalog 或 Harbor production
  的事实来源。旧 `main.py`/`only_test.py`/OpenHands 0.56 runner 已从 checkout 删除。

不要把当前 source 数量、valid 数量或 task 数量写死在脚本、报告或回答中。需要计数时
使用 Git：

```bash
git ls-files 'catalog/sources/*/task.toml' | wc -l
git ls-files 'catalog/sources/*/task.toml' | sort
```

`.pi-glla`、未跟踪目录和旧报告快照不计入 source 集合。若需要冻结输入，必须在所有
相关 source 改动提交后重新运行 `scripts/freeze_harbor_production_input.py`，并让
报告记录当前 HEAD、source 列表、revision、tree/content digest 和工作树状态。

当前 runtime adapter 由 `HarborCompilerRegistry` 解析，不能在 CLI 或任务中猜测语言。
已实现的 Python、Node/npm、Node/pnpm 和 Go/modules lane 必须使用各自声明的
runtime/package-manager identity；未知组合必须 fail closed。Python bundle manifest
使用 schema `1.0`，Node 使用 schema `2.0`；其他 adapter 的 schema 以对应 compiler
和 lock 文件为准。

## 2. 工作模式与不变量

开始前先说明本次属于哪一种模式：

- `author-one`：为一个固定 revision 形成 source、规格、测试和 verifier truth；
- `author-batch`：小批次并发 authoring，维护逐题状态和失败原因；
- `validate`：只做 source、compile、evidence、network 或 controls 校验；
- `run-benchmark`：只运行已经冻结的任务，不在 run 中修改 instruction、测试、镜像
  或分母；
- `analyze-results`：只汇总已保存的结果、失败分类和资源数据；
- `explain`：只解释系统，不修改 catalog。

当前生产化维护默认不运行 model pilot、blind review、traceability review、OSS
上传或 legacy harness 改造；只有用户明确要求时才进入这些阶段。不要把本轮 Oracle
或 controls 结果描述成模型能力、跨版本 parity 或完整发布批准。

固定不变量：

- 一题只能有一个 writer；不同题可以并行，shared compiler、dataset manifest、
  统一报告和发布索引由父 agent 串行集成。
- worker 只能修改自己负责的 `catalog/sources/<task-id>/` 和必要的对应 generated
  runtime；父 agent 复核 source、runtime、evidence、hash 和门禁后再提交。
- 不修改与任务无关的用户 dirty worktree。不要使用 `git reset --hard`、
  `git checkout --`、批量删除或 force-push。
- 发生镜像、Docker、网络、API、磁盘或 Harbor 调度故障时，分类为
  `infrastructure`，有限重试并保存原始失败；不能把它写成 model、source 或
  verifier 失败。
- 任何“通过”“可复现”“等价”“valid”声明都必须有实际命令、版本、路径和摘要
  证据。工具未运行时不得填推测值。

## 3. Lifecycle 与 task 终态

声明式 lifecycle 可以使用：

```text
discovered -> frozen -> inventoried -> specified -> packaged
           -> oracle-passed -> controls-passed -> reviewed -> piloted -> published
```

`blocked` 和 `excluded` 是带理由和证据的终态。`packaged`、`oracle-passed` 不是
可发布终态；至少要有当前 runtime、Oracle、固定分母和 controls evidence 才能进入
`controls-passed`。`published` 还需要 dataset/version、审批和不可变 content
manifest；不要仅因 `controls-passed` 就声称已经发布。

每题至少记录：task id、version、upstream URL、完整 commit SHA、license、source
digest、runtime identity、Python/Node/Go 版本、OS/base image digest、依赖 lock、
测试 collection、frozen denominator、命令、开始/结束时间、重试次数、exit code、
失败分类和 artifact 路径。

阻塞题必须同时满足：

- source 的 `[lifecycle] status = "blocked"` 或 `excluded`；
- 有真实 remediation，不能以“尚未处理”作为唯一理由；
- 有 `catalog/sources/<id>/production-evidence.json`；
- evidence 的 `blocked.failure_class`、`next_step`、`source_freeze` 和非空
  `commands[].log` 均存在，日志 path 是仓库相对路径且 SHA-256 与实际 bytes 一致；
- `catalog/tasks/<id>/` 不存在；
- 没有 Oracle、controls 或 reward 时不得伪造结果。blocked source 可以使用
  `expected_total = 0` 或 `unknown`，但这不构成 valid task 的分母。

blocked 的 source authority 必须明确：`source_freeze.status` 使用 `known`，或
使用 `failed` 并给出真实 reason；不能用 `unknown` 掩盖没有核实的 source authority。

## 4. Source、规格与冻结

冻结候选时至少核对：

- upstream URL 和不可变完整 commit SHA；
- license SPDX、license 文件 bytes 和 source archive/tree digest；
- package metadata、public API、CLI/entry point、fixtures 和依赖闭包；
- Python/Node/Go toolchain、OS、base image digest 和 build command；
- source-only test collection、固定分母和 collection error；
- 隐藏测试到公开行为的双向 traceability。

公开 `instruction.md` 至少包含：

```text
Project Description
Supports
API Usage Guide
Implementation Notes
```

每个核心 API 要说明 import path、完整 signature、输入域、返回类型/形状、顺序与
确定性、状态或副作用、异常契约、普通示例和必要边界。不要复制实现函数体、完整
算法、上游测试断言、private tests 或能直接取回参考源码的 endpoint。标准库模块
不能作为 PyPI runtime dependency。

如果上游行为涉及 callback、native object、filesystem、TTY、随机数、locale、
时间、multiprocessing、CLI 或不可 JSON 序列化状态，必须在 source inventory 和
verifier 设计中明确 adapter 边界。没有可靠 child-side adapter 时保持 blocked，
不能让 trusted/root pytest 直接 import candidate 来绕过边界。

## 5. Dependencies 与网络策略

每个可运行 task 必须在 source 的 `task.toml` 显式声明：

```toml
[environment.network_policy]
mode = "no-network"
offline_dependencies = "preinstalled-image"
reference_source_fetch = "forbidden"
reason = "Dependencies are installed during the Docker build phase."
```

规则如下：

- `mode` 只允许 `no-network` 或 `allowlist`；`public` 不可表达；
- allowlist 只能包含精确 hostname，不能包含通配符、URL、端口、GitHub/raw GitHub、
  code host 或 generic mirror；registry allowlist 会产生 lint warning；
- build 阶段可以从 package index 联网安装 hash-locked dependency lock；run 阶段
  的 agent 和 verifier 默认断网；
- Python verifier 只接受私有、hash-locked `requirements.lock.txt` 的
  `lock_artifact`。禁止 wheelhouse、vendor、`.whl`、`tests/dependencies/`、
  `COPY dependencies`、`--no-index` 和 `--find-links`；
- Node/npm、Node/pnpm 和 Go/modules 使用对应的 lock/cache/module contract，不把
  Python 规则机械套到其他 lane；
- agent compose 不得自行声明 `network_mode` 或 `networks`，否则 Harbor egress
  sidecar 和 run-scoped host authorization 可能失效；separate verifier 保留显式
  `network_mode: none`；
- LLM provider host 是运行时参数，不写入每个 task 的 metadata；需要时通过 Harbor
  `agent.extra_allowed_hosts` 或等价运行时配置注入。

静态网络门禁：

```bash
uv run nl2repo task lint-network
uv run nl2repo task lint-network --include-generated
```

正式生产 gate 要求 error 为零。warning 必须在报告中解释，尤其是 dependency closure、
registry allowlist 和 Oracle host authorization。

### Oracle 源码获取

Oracle 可以从 `solution/` 上传中取得冻结参考源码；模型 agent 不得取得该源码，也
不得获得 Oracle 专用 source host authorization。Oracle 的 `solve.sh` 必须：

1. fetch 固定 revision 或文档化的固定 tag ref；
2. 断言解析出的 commit 等于 source revision；
3. 生成 archive 并用 source digest 严格校验；
4. 在 Oracle run 时显式授权所需的精确 host。

`.gitattributes` 的 `export-subst` 且版本由 git 推导的项目可以使用 tag-ref 例外：
仍断言 commit，不做 `checkout --detach`，避免改变 archive bytes。除该例外外不得
使用无校验的 `git fetch` 或 floating branch。

## 6. Compiler 与 Harbor runtime

先用当前 CLI 检查命令和版本：

```bash
uv run nl2repo --help
uv run --frozen --project harbor-runner harbor --version
```

source 校验：

```bash
uv run nl2repo task validate-source catalog/sources/<task-id>
```

正式编译必须使用当前 source、锁定 toolchain、本地 artifact store 和 private read
授权，并且不得使用 `--allow-incomplete`：

```bash
uv run nl2repo harbor compile catalog/sources/<task-id> \
  --output catalog/tasks \
  --toolchain toolchain.lock.toml \
  --artifact-root .nl2repo/artifacts \
  --authorize-task-private-artifacts
```

`--allow-incomplete` 仅用于公开 synthetic/development fixture，不能用于 production
evidence。compiler 失败时先区分 source、artifact、environment、verifier 和
infrastructure 根因，不要手改 generated runtime 过门禁。

compiler 生成的 bundle 是 closed-world projection：bundle manifest 中不应有未声明
的 extra file、private run tree、用户 compose 或旧 runtime 文件。生成后至少检查：

- bundle manifest 和 runtime identity；
- task.toml、instruction.md、environment、solution、tests、controls 的完整性；
- verifier 与 candidate 的隔离；
- dependency lock、network policy 和 source digest；
- runtime 与 source evidence 的 bundle digest 一致。

控制 bundle 通过统一 registry 生成：

```bash
uv run nl2repo harbor prepare-control catalog/tasks/<task-id> stub \
  --output .nl2repo/controls/<task-id>
uv run nl2repo harbor prepare-control catalog/tasks/<task-id> forgery \
  --output .nl2repo/controls/<task-id>
```

不要手工编辑 `catalog/tasks/<id>/bundle.manifest.json`、Dockerfile、verifier runtime
或 controls 来修复 source 问题。改回 `catalog/sources/<id>/`，再重新编译。

## 7. Verifier、评分与 controls

production verifier 必须是 separate verifier。trusted/root 进程不能直接把 candidate
放入自身 `sys.path`，不能直接 import candidate，也不能让 candidate 写 trusted
reports。candidate API、CLI 和 entry point 通过 UID 隔离的 subprocess/JSON contract
调用；复杂对象必须使用题目专用 child-side adapter。

Verifier 必须：

- 自动 collection 并使用正数、冻结的 `frozen_total`；
- 生成结构化 collection、JUnit、grading 和 numeric reward；
- 检查 setup/test exit code、collection error、JUnit leaf 数量和固定分母；
- 使用固定 metric contract，不能依赖 console 正则或手工分母；
- 由 verifier 自己写 reward，不信任 candidate 写入的 reward/JUnit/collection；
- 在 verifier 内生成并校验 `network.json`，公网和 numeric IP 探测都 fail closed；
- 对 workspace、路径、symlink、special file、进程、FD、CPU、地址空间、累计 wall
  time 和 report size 设置有界约束，并清理 candidate process group；
- 把安装失败、JUnit 缺失、collection mismatch、verifier internal error 和网络
  暴露写入 grading details。

当前 Package campaign 的 Oracle gate 是一次运行：

```text
valid = true
collected = frozen_total
reward = passed / frozen_total >= 0.80
```

低于 `1.0` 时保存失败集合、原因和 Oracle ceiling。多次稳定性实验必须作为独立
experiment/version，不能与一次 Oracle gate 或历史版本直接合并。空 workspace 只允许
以 `candidate-installation-failed` 的安装失败例外得到 `0/0`；stub/forgery 必须收集
冻结分母，不能用安装失败掩盖 verifier 缺陷。

最低 controls：

```text
Oracle/reference implementation -> valid=true, fixed denominator, reward >= 0.80
empty workspace                -> near zero; only allowed empty install exception
stub                           -> frozen denominator, low score
forgery                        -> cannot change verifier-owned grading/reward
offline verifier               -> completes with public_network_available=false
network policy lint            -> zero errors
```

分数定义：

```text
task_score    = clamp(passed / frozen_total, 0, 1)
dataset_score = mean(task_score for every valid task)
```

不同题不能按 raw passed count 排名；invalid verifier、环境和 infrastructure 结果
不能无条件解释成模型得零分。当前 legacy harness 的 `score` 字段不作为跨题主指标，
应读取结构化 `grading`/`pytest_results` evidence。

## 8. Canonical evidence 与 artifact hygiene

valid task 的 `catalog/sources/<id>/production-evidence.json` 顶层应包含：

- `schema_version`、`task_id`、`terminal_kind = "valid"`；
- 当前 generated bundle manifest digest；
- `oracle`：Harbor 版本、命令、exit code、valid、grading/network 路径和摘要；
- `controls.empty/stub/forgery/offline`：每项命令、exit code、grading/network 路径
  和摘要；
- 不声称未运行的 gates，不复用旧 bundle 的 receipt。

blocked evidence 顶层使用 `terminal_kind = "blocked"`，并绑定真实 source-local
remediation log。验证方式：

```bash
python3 scripts/validate_harbor_evidence.py --report reports/<gate>.json --kind oracle
python3 scripts/validate_harbor_evidence.py --report reports/<gate>.json --kind controls
python3 scripts/validate_harbor_evidence.py --report reports/<gate>.json --kind blocked
```

完整 production catalog gate 需要使用当前冻结 input 和当前 source/task roots 运行
`scripts/validate_harbor_production_catalog.py`；参数以 `--help` 为准，不能凭旧报告
猜测 `--expected-sources`。统一 campaign quality 使用
`scripts/verify_harbor_campaign_quality.py`，输入必须是当前 gate report。

目录约束：

- private dependency、verifier、Oracle bytes 存在 `.nl2repo/artifacts` 的标准 CAS，
  不放入公开 source 或 agent image；
- 完整 Harbor run tree 放 `.nl2repo/runs`，不提交到 source；source 只保留小型、
  脱敏、hash-bound evidence；
- 用户原有 compose 或 generated runtime 若需保护，先按原 bytes/hash 迁移到
  `.nl2repo/preserved-worktree/`，不能丢弃或覆盖；
- 不把 secret、API key、private test、judge prompt、未脱敏 trajectory 或 provider
  response 写入 Git、日志、提交信息或公开 instruction。

## 9. 运行 Harbor 与 benchmark

官方 Harbor 统一入口：

```bash
uv run --frozen --project harbor-runner harbor run \
  -p catalog/tasks/<task-id> \
  -a oracle \
  --job-name <unique-name> \
  -o .nl2repo/runs/<run-id> \
  --n-concurrent 1 \
  --yes
```

Oracle 需要源码时，只在 Oracle run 显式加入精确 source host authorization；模型 run
不得继承该授权。每个 retry 使用新的 run/trial root，不能追加旧 job 或覆盖旧结果。

正式批次开始前记录 task list、dataset/version、source input digest、agent/model、
attempt 数、并发、预算、镜像/toolchain digest、network policy、停止条件和 artifact
目录。每完成一题立即保存 result；失败记录 stage、唯一 failure class、命令、exit
code、reason 和 artifact 路径。

benchmark 期间：

- 不修改 instruction、hidden tests、verifier、image、denominator 或 network policy；
- 只对纯 infrastructure failure 有界重试；
- 收到停止信号后不启动新 trial，让在途 trial 保存结果；
- 不把缺失 token/cost 当成 0；不把 timeout/crash 直接归为 model failure；
- 不在同一份结果中混合不同 task version、runtime、source revision 或 metric contract。

旧 OpenHands 0.56 批量入口已经删除。历史 experiment 只能从已冻结 archive 读取，不能
根据旧 `config.json`、`workspaces/` 或 `result/` 快照宣称当前 task 已通过 production
gate。根目录 `openhands/` 现在只表示 pinned SDK fork submodule，不是 legacy runner。

Docker 资源异常时，先停止启动新任务并记录影响范围。可以按用户约定清理未连接网络
和无用缓存，例如：

```bash
docker network prune -f
docker image prune -af
docker builder prune -f
docker volume prune -f
```

不要重启 Docker daemon，也不要删除其他 campaign 正在使用的容器、volume 或 lease。

## 10. Git 与提交

提交前只加入本题或本次明确授权的路径：

```bash
git diff --check
git add -- catalog/sources/<task-id> catalog/tasks/<task-id>
git commit -m "..." -- catalog/sources/<task-id> catalog/tasks/<task-id>
```

共享 compiler、脚本、测试和文档变更必须使用明确 pathspec 单独提交。提交前检查：

- `git status --short` 中没有误暂存的 `pyproject.toml`、`jobs/`、`temp/`、用户 workflow
  或其他 worker 文件；
- generated task 与 source/evidence 的 digest 相符；
- blocked task 没有 runtime；
- JSON/TOML/YAML 可由 parser 读取；
- `git diff --check` 通过。

push 使用已配置的 `fork` remote 和当前分支，禁止 force-push。若远端领先，先 fetch
并在干净的 integration worktree 合并、重跑受影响的 compiler/runtime/evidence gate，
再推送；不要在大量用户 dirty change 上盲目 rebase 或 reset。

## 11. LLM orchestration 与 subagent fleet

复杂工作默认采用 **Sol control plane + Qwen fleet**。主 Model 只负责规划、切分、
调度、裁决和最终集成，不作为常规实现 writer：

1. **Sol 规划**：先读取权威文档和当前代码，写出目标、非目标、依赖 DAG、风险、
   worktree 计划、停止条件和整体验收门禁。计划必须覆盖用户要求，不能把未决定的
   架构选择留给实现 worker 临场猜测。
2. **Luna 优先的侦察**：复杂任务先并行启动 4 到 8 个
   `z-open-api-gpt-openai-responses/gpt-5.6-luna` scout/worker lane；如果 Luna
   返回 `model_disabled`、401、超时或其他 provider failure，才降级到
   `aliyun-qwen-openai-responses/qwen3.8-flash`。各 lane 分别核对不同 source seam、
   schema、runtime、测试、运维或安全边界，证据必须互补，不允许只换编号的重复任务。
3. **Sol 裁决**：主 Model 汇总侦察结果，消除冲突，冻结接口、状态机、失败分类和
   acceptance contract，再启动实现。架构、security boundary、production gate 和最终
   review 由 Sol 负责。
4. **Luna/Qwen 实现**：把实现拆成尽可能多的独立窄 lane。每个 mutation lane 使用独立
   branch/worktree；同一 worktree 同时只能有一个 writer。worker 只提交本 lane 的本地
   commit，不直接 push、安装 service、执行 cutover 或修改共享 integration checkout。
   普通 worker 默认使用 Luna，发生明确 provider failure 后使用 Qwen Flash；handoff
   必须记录实际 provider/model、fallback 原因和是否使用了 fallback。
5. **Luna/Qwen 验证**：实现后并行运行独立 test、fault-injection、negative-control、diff
   audit 和 regression lane，默认仍按 Luna→Qwen 路由执行。review 必须针对固定 commit
   SHA；不要审阅 writer 正在变化的 working tree。
6. **Sol 签收**：主 Model 依据 commit、测试、review、artifact 和 residual risk 做最终
   裁决。共享 integration checkout 由单一 integrator 串行合并，重跑跨 seam gate 后才
   push、部署或启用 production lane。

每个 subagent 任务说明必须完整包含：

- objective、模式和准确的 done 条件；
- repository、cwd、base/ref、输入文档和必须读取的 source；
- 允许修改的精确路径、输出路径和 lane ownership；
- 禁止修改或禁止执行的 production/private/live 操作；
- 接口、schema、状态机、failure taxonomy、资源和并发约束；
- 必须运行的命令、预期 exit/result、artifact 与 evidence 格式；
- stop/ask 条件、剩余 blocker 和 handoff 内容。

subagent 临时数据必须写入项目磁盘或 `/data/pi-tmp/root`，不得写入 `/tmp` tmpfs。
默认环境为：

```text
TMPDIR=/data/pi-tmp/root/tmp
PI_SUBAGENTS_TEMP_ROOT=/data/pi-tmp/root/pi-subagents
PI_SUBAGENTS_WORKTREE_DIR=/data/pi-tmp/root/worktrees
```

大型 SQLite/pytest/Cargo target、source snapshot、probe 输出和 async artifact 必须使用 lane
专属目录。清理只能删除该 lane 明确创建并拥有的精确路径；禁止删除 scratch 的 parent、
共享 temp root、其他 run 目录或按宽泛 glob 清理。任务完成前记录 scratch 路径，完成后先
确认没有活跃进程引用再删除。

简单模型不能接收“实现整个功能”“修完所有问题”这类宽泛任务。先把工作拆成可独立
验证的模块、迁移、运行时、测试、review 和运维 lane，再并行派发。没有独立写入边界的
工作保持一个 writer，但同时启动多个只读 scout/test/review lane 提供证据。

主 Model 可以执行控制面动作：建立/检查 worktree、维护 task board、回复 subagent 决策、
运行最终验收、解决已审 merge conflict、串行集成、push 和按批准合同执行 cutover。常规
功能代码、测试起草和局部修复交给 subagents。模型/provider fallback 必须在 handoff 中
显式记录；fallback 运行不能冒充首选模型成功。

fleet 完成条件：所有 writer 都已停止并返回固定 commit，所有 lane 均有结构化 handoff，
测试/review 对应同一 commit，integration worktree 干净，未解决 blocker 已进入 task board，
且最终声明没有越过 F0.5、F1、Oracle、controls、pilot 或 publication 门禁。

## 12. 验证清单与汇报

窄改动至少运行对应的 source validation、runtime/evidence gate 和 `git diff --check`。
跨 compiler/verifier/network 改动应运行：

```bash
uv run pytest -q
uv run ruff check src tests scripts
uv run mypy src/nl2repobench
uv run pytest -q -p no:cacheprovider --no-cov tests/test_no_vendor_install.py
uv run nl2repo task lint-network --include-generated
```

命令必须使用当前 lock 和实际 checkout；coverage、网络、Docker 或依赖故障导致未运行
时如实报告。

汇报顺序：

1. 当前 source/task input、版本、runtime 和 network 约束；
2. 每题 status、Oracle passed/total/reward、controls、失败分类和 artifact；
3. valid、blocked、excluded 和 intermediate 的动态统计；
4. verifier/environment/infrastructure 风险和未解决 blocker；
5. 运行过的命令、版本、commit 和测试结果。

不要只报总均分，不要混合 invalid 与 model zero，不要把一次随机 attempt 当作稳定
能力，也不要把 Harbor 结果描述成论文或旧 harness 的 parity，除非已经完成同版本、
同环境、同 metric contract 的显式 parity validation。

## 13. Definition of Done

单题 production-valid 必须同时满足：

- source revision、license、环境、依赖 lock、network policy 和 image/toolchain digest
  完整；
- instruction 与 hidden assertions 双向可追溯；
- frozen denominator 正数、自动 collection 与实际 collection 一致；
- 当前 compiler 无 `--allow-incomplete` 生成 closed-world Harbor runtime；
- 一次官方 Harbor Oracle `valid=true`、固定分母一致、reward `>= 0.80`；
- empty、stub、forgery、offline controls 通过；
- verifier 是 separate、candidate 不可篡改 trusted report；
- canonical production evidence 绑定当前 bundle 和全部 receipt；
- network lint 无 error，Python verifier 无 vendor/wheelhouse 违规；
- 未声称未完成的 review、pilot、publish 或 parity。

单题 blocked 必须有真实 blocker、source-local remediation、canonical blocked evidence、
可验证日志 hash，并且没有对应 `catalog/tasks/<id>` runtime。

整批完成还要求：所有 source 达到明确终态或有排除原因，当前 frozen input 与 dataset
manifest 不含可变资源，gate report 可复现，且所有动态统计均由当前 Git source 集合
计算。
