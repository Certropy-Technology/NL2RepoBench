# NL2RepoBench 运行与出题总手册

本文是 Agent、出题人、Reviewer 和评测运维的操作入口，记录当前 checkout 的
真实架构、命令、门禁、产物、归档方式和已知故障。本文不包含 API key、hidden
tests、私有依赖 bytes、Oracle bytes 或不可复现的分数。

> **当前交付契约：unified Harbor contract。** 下文中历史性的 “Python v1” 和
> “Node/npm v2” 只用于解释已有 run、schema 或 artifact，不能作为新任务的两个
> runtime API。新题和迁移题统一由一个 canonical parser/compiler 处理；Python、npm
> 和 pnpm 仅作为 runtime/package-manager adapter。新 release 不与旧 v1/v2 分数合并。

## 当前状态

查询真实状态，不要依赖旧文档中的 active-task 数字：

```bash
cd /root/NL2RepoBench
python3 scripts/convert_testfiles_loop.py status
```

## 1. Benchmark 与安装

NL2RepoBench 测量 Agent 从自然语言规格和空 `/workspace` 出发，生成完整、可安装、
可运行代码仓库的能力。它不是已有仓库修复，也不是补一个函数。

当前有两条隔离路线：

| 路线 | 语言 | 状态 |
| --- | --- | --- |
| Legacy conversion | Python | 104 题状态文件当前为 74 complete、30 pending；catalog lifecycle 另由 reconciler 审计 |
| Node/npm lane | Node 24/npm 11 production lock；Node 22 synthetic dev fixture | `canonicalize` production compile + one Oracle + control matrix passed |

`complete` 表示 task-local Harbor 包通过静态来源和结构校验，不代表通过 Oracle、
empty/stub/forgery/offline controls。`blocked` 必须有证据，不能作为模型得分。

```bash
docker info
uv --version
git --version
uv sync --frozen
uv sync --frozen --project harbor-runner
uv run nl2repo --help
uv run --frozen --project harbor-runner harbor --version  # 0.21.0
uv run pytest -q
uv run ruff check src tests scripts
uv run mypy src/nl2repobench
```

单文件测试要关闭全项目 coverage 门禁：

```bash
uv run pytest -q --no-cov tests/test_model_runner.py
```

大型旧 verifier image 可能占用几十 GB。磁盘不足时停止新任务，不要删除其他
campaign 仍在使用的 containerd lease。

## 2. Catalog 与出题状态机

Human 只编辑：

```text
catalog/datasets/<dataset-id>/dataset.toml
catalog/sources/<task-id>/task.toml
catalog/sources/<task-id>/instruction.md
```

Canonical manifest、Harbor bundle 和 `test_files/` projection 都是下游生成物，不能
人工修改来绕过门禁。推荐状态机：

```text
discovered -> frozen -> inventoried -> specified -> packaged
           -> oracle-passed -> controls-passed -> reviewed -> piloted -> published
```

失败要归入且只归入一个主分类：`source`、`spec`、`environment`、`verifier`、
`model` 或 `infrastructure`。只有 infrastructure 可以有限重试。

Legacy writer 只写自己的 task worktree，父线程串行集成：

```bash
python3 scripts/convert_testfiles_loop.py claim --owner <owner> --limit 1 --tasks <task>
python3 scripts/convert_testfiles_loop.py validate <task>
python3 scripts/convert_testfiles_loop.py record <task> --owner <owner> \
  --status complete --reason '<evidence>' --artifact <handoff>
python3 scripts/convert_testfiles_loop.py block <task> --owner <owner> \
  --reason '<precise blocker>' --artifact <audit>
```

不能证明 commit、license、denominator、overlay provenance、offline closure 或
candidate boundary 时，写 blocked audit；不要复制 hidden tests 或伪造 bundle。

Python 与 Node 使用不同 dataset/version、schema、grader、依赖闭包和 metric：

- Python v1：pytest/JUnit，`fixed-test-pass-rate-v1`；
- Node v2：`node:test`、`node-test-json-v1`、`node-test-leaf-pass-rate-v1`、npm v3。

对于复杂 JSON/回调/状态边界，Python v1 还支持受限的
`verifier.protocol = "custom-json-v1"`。task TOML 只保存 private verifier bundle
的 digest、URI 和相对 entrypoint；suite、adapter、remote fixture、grader 和
dependency lock 不进入 public `catalog/sources`。`HarborCompiler` 只 materialize private
bundle 到 separate no-network verifier，并用固定 wrapper 校验 leaf IDs、状态集合、
固定分母和 JUnit/collection；Python verifier 的依赖只在 Docker build 阶段按
`lock_artifact` 联网安装，禁止 wheelhouse vendor。禁止把 custom `test.sh` 当作公开
task source。候选依赖安装到隔离的 candidate site，不能污染 trusted verifier 的
pydantic/pytest runtime。

## 3. Ground Truth 与规格

冻结候选时保存 upstream full commit、archive/license hashes、OS/runtime/image digest、
hash-locked build dependency lock、test bundle、自动 collection、固定 denominator、
Oracle x1、controls、traceability、review record 和 content manifest。当前 Package
campaign 使用一次 Oracle gate；历史三次稳定性实验不能直接并入新版本分数。

公开 instruction 至少包含：

```text
Project Description
Supports
API Usage Guide
Implementation Notes
```

每个 API 写清 import path、signature、输入域、返回形状、状态/副作用、确定性/顺序、
异常和边界。不要复制函数体、完整算法、上游断言或 hidden test。

## 4. Oracle、controls 与评分

```bash
PYTHONPATH=src uv run --frozen --project harbor-runner \
  python scripts/harbor_safe_entry.py run \
  -p catalog/sources/<task>/harbor -a oracle \
  --jobs-dir .nl2repo/runs/oracle/<task>/attempt-1
uv run python scripts/cleanup_harbor_trials.py \
  --jobs-dir .nl2repo/runs/oracle/<task>/attempt-1
```

正式题要求一次 `valid=true`、collection 与固定分母一致、reward `>=0.80`。必须读取
`verifier/grading.json`，不能只看 Harbor CLI 的 `rc=0`。

本轮 legacy controls pilot 是历史三次稳定性实验，不属于当前一次 Oracle campaign
gate。没有任务被标成 controls-passed，详情在 `reports/controls-pilot-results.v1.md`。

```text
task_score    = clamp(passed / frozen_total, 0, 1)
dataset_score = mean(task_score for every VALID task)
```

`valid=false` 是 verifier/environment/infrastructure 结果，不是模型 0 分；数据集
使用逐题宏平均。

## 5. GPT/Fable 安全运行

优先使用 Pi-aware wrapper；它读取 mode `600` 的 provider 文件，且不把 key 放进
Harbor/Docker argv：

```bash
python3 scripts/run_model_from_pi.py \
  --provider z-open-api-gpt-openai-responses \
  --model-id gpt-5.6-sol --harbor-model openai/gpt-5.6-sol \
  --task markupsafe \
  --concurrency 2 \
  --run-root "$PWD/.nl2repo/runs/smoke-gpt-$(date -u +%Y%m%dT%H%M%SZ)" \
  --run-prefix gpt56 \
  --lock-root "$PWD/.nl2repo/locks/gpt-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
```

编程式批次使用 `scripts/run_dual_model_queue.py`：默认每个模型同时运行 2 个不同
task，总并发 4；`--existing-inventory reports/oss-run-inventory.json` 会把 OSS
已有 task 整体跳过，不重复模型或 Oracle。资源紧张时使用
`--per-model-concurrency 1`。

聊天消息中的 key 不会自动导入本机环境。临时替换时先在受控 shell 设置环境变量，
再使用 `--credential-env`；变量名可出现在命令行，变量值绝不能出现。

OpenAI-compatible/Responses provider 通常使用 `https://host/v1`；Anthropic Messages
provider 通常使用 `https://host`，客户端调用 `/v1/messages`。`https://z.open-api.ai/`
是管理 HTML，不是模型响应；`/v1/messages` 返回 JSON `401 Invalid token` 时说明路由
正确但 token/权限/注入有问题，不要盲目再加一个 `/v1`。

每个 fresh trial 必须满足：

```text
finished_at != null
n_completed_trials = 1
n_errored_trials = 0
grading.valid = true
expected/effective_total 与 task.toml 一致
reward = passed / frozen_total
整棵 trial root secret scan 为零
```

`valid=false`、junit missing、collection mismatch、HTML provider response、trajectory
missing、VerifierTimeoutError、绝对 root 错位或 secret 命中都要停止当前 model lane。
重试必须换新 root，不能追加旧 job。

## 6. Harbor/OpenHands 产物

成功 run 通常有：

```text
<run-root>/<prefix-task>/<timestamp>/harbor__<id>/
├── agent/trajectory.json
├── agent/openhands_sdk.txt
├── agent/run_agent.py
├── artifacts/workspace/
├── result.json
├── lock.json
└── verifier/grading.json + reward.json + JUnit/collection files
```

标准产物是 ATIF `trajectory.json`，不是通用 `history.json` 或 `event.json`。成功
GPT smoke 实测为 `ATIF-v1.5`、131 steps、129 tool calls、83 observations 和 final
metrics。首次模型响应前失败时可能没有 trajectory，不能手工补写。

```bash
harbor-runner/.venv/bin/python -m harbor.utils.trajectory_validator <trajectory.json>
```

官方格式：[Harbor trajectory format](https://www.harborframework.com/docs/agents/trajectory-format)。
若需要原始 OpenHands events，要单独扩展 adapter 的 artifact collection/retention。

## 7. OSS 归档

先生成 manifest，再在实际上传时做远端 exact-key collision check；`--dry-run`
只检查本地计划，不访问 OSS：

```bash
python3 scripts/upload_runs_to_oss.py \
  --runs-dir .nl2repo/runs/<accepted-root> --skip-tasks --dry-run \
  --manifest /tmp/<accepted-root>-manifest.json
```

默认不要 `--overwrite`。上传器会把 SHA-256 写入 OSS 元数据；同名对象只有 size 和
SHA-256 都相同才 skip，否则 fail closed。上传后使用 `scripts/verify_oss_archive.py`
检查远端 payload checksum，再显式 `--delete-local` 清理本地 raw runs。成功 GPT smoke
已上传；Fable invalid artifact 只保留本地诊断。

## 8. 已知踩坑与收尾

Harbor 环境服务正常使用 `sleep infinity` 保持 agent container 存活；如果 runner 已经
退出但该容器仍在，优先检查 `result.json`、`exception.txt`、`trial.log` 和 compose
project cleanup。2026-08-22 曾因 Harbor 0.21.0/Python 3.14 的跨 asyncio context
`ContextVar.reset()` 清理异常留下 orphan environment；当前模型脚本已改用
`scripts/harbor_safe_entry.py` 和精确 jobs-dir cleanup。完整诊断和并发规则见
[`harbor-runner-cleanup-and-concurrency.zh-CN.md`](harbor-runner-cleanup-and-concurrency.zh-CN.md)。

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| `rc=126`、没有 result | launcher mode 变成 0644 | `chmod 755`，保留 executable test |
| absolute root 重复拼接 | `cd harbor-runner` 后无条件拼 `../` | 使用 absolute/relative 分支，新 root 重跑 |
| Node/npm CodeRange/OOM | `RLIMIT_AS` 太小 | 不设置虚拟地址空间上限，保留 cgroup/CPU/process/FD/timeout |
| Node npm cache EACCES | root-owned cache 给 candidate 使用 | 复制到 candidate-owned `/tmp/npm-cache` |
| `New API` HTML | 管理根页或 provider 路由/协议错误 | Anthropic 检查 `/v1/messages` JSON 响应 |
| `junit-missing` | agent/provider/安装在 verifier 前失败 | 读 exception_info，不计模型 0 |
| Fable 连续 `TerminalAction.command` 缺失、workspace 为空 | Anthropic relay 的 `thinking=enabled` 丢失 tool input；旧 run 的 grader 安装/collection 错误只是后果 | Fable 只通过 `run_model_from_pi.py` 启用 model-scoped `thinking=adaptive`；旧空 workspace run 分类为 infrastructure，不静默当模型失败 |
| Fable 长 Python instruction 仍返回空 tool/content | 受控 direct LiteLLM 与 OpenHands 两层均复现于约 15.6K system + 7.4K instruction；native tool 和 text-tool fallback 都未稳定解决 | 将该 provider/task 组合记录为 infrastructure blocker，停止无效重试；短 Node task 的 adaptive run 单独计入证据，不能外推到长 prompt |
| verifier build 的 fixture checksum mismatch | 派生 Dockerfile 的硬编码 manifest 与 pinned base image 漂移 | 在 pinned image 内重算 manifest，更新 task-local Dockerfile，再跑 Oracle；不要删掉 integrity check |
| candidate install 因 `--require-hashes` 拒绝 source directory | pip hash 校验适用于 wheel/requirements，不适用于本地 source path | build 阶段从网络按 `lock_artifact` 安装 hash-locked requirements，candidate 仍用受限 `--target --no-deps` 安装 |
| pytest 把 `request` 报为 reserved parametrize name | fixture contract 参数名与 pytest 保留名冲突 | 改为 `payload` 等非保留名并重跑 collection |

## 9. 顶层出题 Supervisor

出题 Loop 由顶层 supervisor 统一管理。Loop controller 只负责 claim 和在独立
worktree 中运行 Pi authoring；supervisor 负责定时检查进程、队列和磁盘，串行集成
完成题目，生成 Harbor projection，commit/push，并在 OSS 完整归档和回读校验后删除
worktree。watcher 与 supervisor 共用 `archive.lock`，不会同时归档或删除同一个任务。

启动一次检查并按安全门禁自动启动缺失 controller：

```bash
scripts/run_authoring_supervisor.sh
```

排障或 cron 首次部署使用一次性 dry-run：

```bash
scripts/run_authoring_supervisor.sh --once --dry-run
```

默认的 Director 是无工具、无 session 的顶层 Pi Agent。它只返回固定 JSON 动作，
由 supervisor 的白名单代码执行。`continue`、`integrate` 和 `pause` 控制现有队列；
`discover` 只能从 `reports/authoring-discovery-pool.json` 读取已登记包名，再调用固定
的 discovery 脚本，不会执行模型生成的任意 shell。没有 Director 或需要完全确定性
运行时可显式使用 `--director-mode rules`。

默认每种语言最多 3 个 `max-concurrency=1` controller，但受全局最多 3 个 controller
的磁盘保护上限约束，确保 Python、Node、Go 不会在 100 GiB 工作盘上同时无限扩张。
`/data` 剩余空间低于 12 GiB 时 supervisor 停止启动新 Loop，但仍允许归档和清理已验证
的完成题；剩余空间低于 2 GiB 时不启动 watcher。状态、动作、错误和队列快照写入
`.nl2repo/authoring-live/supervisor/status.json`。source、generated projection、
OSS manifest 或 worktree 发生冲突时 fail closed 并保留现场。

Supervisor 使用 `origin` 的 integration branch 作为唯一写入线。生产部署时应将该线
通过受控 fast-forward 或审核合并到 `main`；合并成功后只删除已确认 merged 的本地
feature branch 和已归档 worktree，保留仍有 worktree、dirty 内容、未验证 evidence
或未推送提交的 branch。

### 动态运行控制与 systemd

生产机可安装仓库内的 `ops/nl2repobench-authoring-supervisor.service`：

```bash
install -m 0644 ops/nl2repobench-authoring-supervisor.service \
  /etc/systemd/system/nl2repobench-authoring-supervisor.service
systemctl daemon-reload
systemctl enable --now nl2repobench-authoring-supervisor.service
systemctl status nl2repobench-authoring-supervisor.service
```

运行时配置位于：
`.nl2repo/authoring-live/supervisor/runtime-config.json`。使用原子更新 CLI 调整并发，
supervisor 和现有 Loop 会在下一轮读取：

```bash
scripts/authoring_runtime_config.py show
scripts/authoring_runtime_config.py set --max-total-controllers 4
scripts/authoring_runtime_config.py set --controller-concurrency 2
scripts/authoring_runtime_config.py set --enabled false
```

`max-total-controllers` 的硬上限是 6，`controller-concurrency` 的硬上限是 4；默认值
分别为 3 和 1。增加 controller 会在下一轮逐步启动新的 Loop；降低配置不会杀掉当前
正在执行的 task，当前 task 收尾后才停止继续 claim。`enabled=false` 停止新 claim，
但不终止已经运行的 task。配置非法时保留上一份有效配置并记录错误。

变更运行时配置会使 Director cache 失效，促使顶层 Agent 重新评估；LLM 仍不能绕过
Git、OSS、secret、网络、artifact 或 dirty-tree 门禁。systemd service 使用只读的 OSS
环境文件，模型 provider 凭据仍由 `/root/.pi/agent/models.json` 管理，不写入运行配置。
| Python verifier 用 `networkx`/SymPy 旧 API 失败 | pinned image 中实际版本与冻结上游 API 有 drift，或 runtime wheel 未进入 verifier context | 先记录实际版本，补兼容 shim/锁依赖并重新 Oracle；不能直接降低断言 |
| source solution 生成空 workspace | placeholder `solve.sh` 或 agent image 缺 Git/构建工具 | 先补 exact-revision materializer、工具链和 build context，再判断题目是否可行 |
| 没有 history/event | Harbor ATIF 转换是预期产物 | 验证 `trajectory.json`；需要 raw events 时扩展 adapter |
| 旧 `new6` OSS key | 历史 prefix 设计错误 | `RUN_PREFIX=gpt56/fable`，唯一性放入 RUN_ROOT |

```bash
git status --short --branch
uv run pytest -q
uv run ruff check src tests scripts
uv run mypy src/nl2repobench
python3 scripts/convert_testfiles_loop.py status
```

最终报告必须分开 Dataset、Experiment、Scores、Reliability；model、spec、
environment、verifier、infrastructure 失败不能混在一起，缺失 token/cost 不能当作 0。
