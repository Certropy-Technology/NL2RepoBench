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
| Legacy closeout | Python | 104 题终态化：70 complete、34 blocked、pending=0、running=0 |
| Node/npm v2 pilot | Node 22/npm | development-only；synthetic vertical slice 已通过，不代表 production |

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
catalog/tasks/<task-id>/task.toml
catalog/tasks/<task-id>/instruction.md
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

## 3. Ground Truth 与规格

冻结候选时保存 upstream full commit、archive/license hashes、OS/runtime/image digest、
offline dependency closure、test bundle、自动 collection、固定 denominator、
Oracle 3x、controls、traceability、review record 和 content manifest。

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
uv run --frozen --project harbor-runner harbor run \
  -p catalog/tasks/<task>/harbor -a oracle \
  --jobs-dir .nl2repo/runs/oracle/<task>/attempt-1
```

正式题要求三次独立 `valid=true`、collection 稳定、reward `>=0.80`。必须读取
`verifier/grading.json`，不能只看 Harbor CLI 的 `rc=0`。

本轮 legacy controls pilot 只得到诊断结果：`markupsafe` Oracle 3/3 为 39/39，
`schedule-master` Oracle 3/3 为 81/81；`unidecode` 两次 64/65、一次 verifier
image build timeout。三者 nop 都是 `valid=false`。没有任务被标成 controls-passed，
详情在 `reports/controls-pilot-results.v1.md`。

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
  --run-root "$PWD/.nl2repo/runs/smoke-gpt-$(date -u +%Y%m%dT%H%M%SZ)" \
  --run-prefix gpt56 \
  --lock-root "$PWD/.nl2repo/locks/gpt-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
```

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

先生成 manifest，再做远端 prefix collision check：

```bash
python3 scripts/upload_runs_to_oss.py \
  --runs-dir .nl2repo/runs/<accepted-root> --skip-tasks --dry-run \
  --manifest /tmp/<accepted-root>-manifest.json
```

不要 `--overwrite`。当前 uploader 会归一历史 `gpt56-new6-markupsafe`、把 root
`queue.log` 放进 `_queue-logs`，但远端去重仍是 existence-only skip，不能替代 hash
collision check。成功 GPT smoke 已上传；Fable invalid artifact只保留本地诊断。

## 8. 已知踩坑与收尾

| 症状 | 根因 | 处理 |
| --- | --- | --- |
| `rc=126`、没有 result | launcher mode 变成 0644 | `chmod 755`，保留 executable test |
| absolute root 重复拼接 | `cd harbor-runner` 后无条件拼 `../` | 使用 absolute/relative 分支，新 root 重跑 |
| Node/npm CodeRange/OOM | `RLIMIT_AS` 太小 | 不设置虚拟地址空间上限，保留 cgroup/CPU/process/FD/timeout |
| Node npm cache EACCES | root-owned cache 给 candidate 使用 | 复制到 candidate-owned `/tmp/npm-cache` |
| `New API` HTML | 管理根页或 provider 路由/协议错误 | Anthropic 检查 `/v1/messages` JSON 响应 |
| `junit-missing` | agent/provider/安装在 verifier 前失败 | 读 exception_info，不计模型 0 |
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
