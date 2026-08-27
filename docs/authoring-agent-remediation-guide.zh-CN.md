# 出题 Agent Remediation Guide

本文件是 Raw Package -> Harbor 出题 Loop 的 Worker contract。Loop 每次 claim
直接启动一个独立的顶层 `pi --print` 会话，并在独立的磁盘 worktree 中执行本
contract；它不是主 Pi 通过 `pi-subagents` 批量派生的子会话。Worker 的终点是把
经过前置门禁的 task 放进 catalog，状态为 `awaiting-agent-run`。默认不向顶层
session 暴露 `subagent`；只有显式启用且确有 bounded parallel probe 需要时才可
由单个 Pi Agent 内部使用。后续 Harbor 模型评测由独立 Agent Run Loop 消费 catalog。

## Queue refill

`run_authoring_loop.py` 默认先执行 plan 中的指定 task；plan 耗尽后，自动从同一个
`--queue`/`--queue-state` 按语言领取仍为 pending 的 candidate，直到 queue 没有可领取
项。claim 仍由 `package_queue_loop.py` 的文件锁和 lease 串行保护，因此多个 authoring
controller 可以共享一个 queue，不会重复领取 running/complete candidate。已有
`catalog/sources/<package>` 或 generated `catalog/tasks/<package>` 的 candidate 会跳过，
避免把已存在的旧题重新送入新 Loop。

可用 `--no-refill-queue` 关闭这一行为。通常不需要为每一小批任务手工重新生成 plan；
保留一个带正确 `language`、`batch_id` 和公共 remediation metadata 的 plan 即可让 Loop
持续消费 queue。每个 candidate 在单次 controller 运行中最多被调度一次；失败会回到
queue，由下一次 controller/attempt 按 lease 和 `--max-attempts` 规则处理。

## 存储纪律

大型 source clone、wheelhouse、npm cache、Docker build context、test bundle 和
Oracle artifact 必须放在项目磁盘（推荐 `.nl2repo/authoring-work/<batch>/<package>/`），
不要放 `/tmp` tmpfs。`/tmp` 只允许小型、bounded 的进程 socket/短期日志，单个 worker
不得超过 256 MiB；每个 stage 完成后立即清理。Worker brief 必须记录工作目录和 cleanup
结果。这样可以避免多个并发 Package 把 tmpfs 打满，误报为 Docker/依赖/模型故障。

## 核心规则

下面这些不是 Block 原因，而是 Worker 必须完成的 remediation：

- 没有 immutable verifier image、base-image digest 或完整 environment lock；
- runtime/dev dependency 没有 pin、hash 或 offline wheelhouse；
- 没有 build backend、Dockerfile、package lock、submodule materialization 或测试闭包；
- native、network、database、browser、TTY、interactive 等 risk flag；
- 上游测试 runner、Python/Node 版本和当前镜像不兼容。

Worker 应先固定 revision 和 license，再选择兼容 runtime，补 lock/wheelhouse、系统包、
Dockerfile、build backend、candidate boundary 和 verifier。每次尝试必须写入 task-local
`provenance/` 或 `evidence/`：命令、版本、exit code、stdout/stderr 路径、digest、
下一步动作。网络安装成功不等于 offline closure；必须重新下载/清空 cache 后用
`--no-index` 或等价方式验证。

只有以下情况，在 remediation attempts 已经有证据后才可以 `blocked`/`excluded`：

1. 没有任何可执行测试，无法形成固定分母；
2. license 不清楚或不允许需要的分发方式；
3. 经过 fetch/checkout 尝试仍不能固定 immutable revision；
4. 依赖付费账号、不可冻结远端服务或不可复现的外部数据；
5. 在 bounded build/test probe 后仍明显超过资源预算。

“没有材料”本身不能写成 Block。若 remediation 失败，报告必须包含
`attempted_commands`、`tool_versions`、`exit_codes`、`failure_logs`、`failure_class` 和
`next_unblock_action`。没有这些字段的 Block handoff 不可合入。

## Agent Run 网络安全门禁

出题 Agent 可以在 source freeze、image build 和依赖 remediation 阶段使用网络，但最终
Harbor Agent Run 的 baseline 必须是 `no-network`。普通 Python/Node runtime、build、
test、native library 和 package-manager 依赖必须在 Agent `environment/Dockerfile` 中
安装，或作为锁定的 wheelhouse/npm cache/private artifact 复制进 image；评测 Agent
运行时不能再依赖 PyPI、npm registry 或 source site。

特殊 Package 需要额外系统库、native toolchain、可选依赖或非标准 build backend 时，
由出题 Worker 自己修改 task-local `environment/Dockerfile`、build context 和 lock/私有
artifact，完成 image build 和 no-network probe。不能把“让后续评测 Agent 自己联网安装”
当作解决方案。

LLM Provider hostname 由 model runner 根据实际 HTTPS base URL 通过 Harbor 的
run-scoped `--allow-agent-host` 注入，仅在 Agent phase 生效；它不写入 task metadata。
Oracle 是受信任的参考实现运行，不是被评测的模型 Agent。Oracle runner 根据 frozen
`[source].upstream_url` 取 exact source hostname，并只在 `harbor run -a oracle` 时通过
同一个 run-scoped `--allow-agent-host` 注入；因此 `solution/solve.sh` 可以在 Oracle
阶段 checkout frozen revision。模型 Agent 绝不能使用这个 source-host override，也不能
通过 GitHub/source host 获取参考实现。

题目 metadata 的 Agent baseline 永远保持 `agent_network_mode = "no-network"`，
`agent_allowed_hosts = []`；不要把 GitHub、source host、PyPI/npm 或 LLM Provider 写入
静态 allowlist。Verifier 使用独立 image，Verifier runtime、hidden test、grader、native
library 和 candidate dependency bundle 必须在 `tests/Dockerfile`/private bundle 中准备好，
Verifier phase 保持 `no-network`。这样 Oracle、model Agent、Verifier 共享同一份 task
environment 定义，只通过 phase/run-scoped policy 区分权限。

Worker handoff 前必须执行（只验证 task 的静态 baseline，不授予 Oracle 或模型网络权限）：

```bash
python scripts/check_agent_network_policy.py \
  --task-root catalog/tasks/<task-id>
```

该检查失败时不得进入新的 Harbor Agent Run。它用于防止模型在评测时直接从上游
GitHub clone/reference source；已经在途的 trial 不因规则更新而改变身份，后续 trial
必须通过该 preflight。

## 执行顺序

```text
source-freeze
  -> ast-inventory + test-inventory
  -> dependency-probe
  -> environment-remediation
  -> dependency-closure
  -> Harbor package
  -> verifier build/offline smoke
  -> Oracle once
  -> empty/stub/forgery/timeout/offline controls
  -> blind/spec review
  -> catalog handoff
```

### Environment remediation

1. 记录 `python --version`/`node --version`、package manager、OS/arch/libc 和基础镜像。
2. 选择与 frozen revision 和测试 runner 都兼容的 runtime；必要时建立 task-local lock。
3. 补系统包和 build backend 到 Dockerfile，并使用 digest-pinned base image。
4. 对 lifecycle/build/native/network 行为做 bounded probe；能隔离就设计 adapter，
   不要因为风险标记自动退出。

### Dependency closure

1. 从 lock/metadata 解析 runtime、dev、test 和 build dependencies。
2. 生成带 hash 的 wheel/tarball/module closure；依赖必须落在 verifier context 可访问的
   private artifact bundle 中。
3. 清空 package cache，在 no-network verifier 中重新安装；保存每个 artifact 的 size
   和 SHA-256。
4. Candidate dependencies 必须安装到 candidate-owned site，不能覆盖 trusted verifier
   的 pytest、pydantic 或其他 runtime。

### Verifier boundary

优先使用 generic candidate client。JSON/回调/生成代码/状态 session 无法表达时使用
`verifier.protocol = "custom-json-v1"`：task TOML 只保存 private bundle digest、URI
和安全相对 entrypoint。hidden tests、adapter、fixture、grader 和 wheelhouse 不得进入
public `catalog/sources`。custom report 必须包含固定数量的唯一 leaf ID 和
`passed|failed|skipped` 状态；wrapper 负责 timeout、UID、no-network、JUnit/collection
和 reward。

## QA 门禁

Worker 在 handoff 前至少运行并保存：

```bash
python -m py_compile <verifier-python-files>
bash -n <solution-and-test-scripts>
uv run nl2repo task validate-source catalog/sources/<task>
uv run nl2repo harbor compile catalog/sources/<task> \
  --output catalog/tasks \
  --toolchain toolchain.lock.toml --allow-private
```

然后在最终 compiled bundle 中运行一次 Oracle，要求 `valid=true`、collection 等于
frozen denominator、reward `>=0.80`。再运行 empty/stub/forgery/timeout/offline controls。
只要 verifier/image/build 自身失败，分类为 `verifier`/`environment`/`infrastructure`，
不能当作模型 0 分；只有 candidate workspace/install/behavior 已真实执行后才分类为
`model`。

## Handoff 格式

```text
task_id / language / source revision
changed files: catalog/sources/<task>/** only
source/license/environment/dependency digests
commands + versions + exit codes
frozen collection and denominator
verifier protocol and private artifact refs
Oracle grading.json path
control matrix paths
status: awaiting-agent-run | blocked | excluded
BLOCKERS: none or precise evidence-backed reason
```

Integrator 才能修改 dataset、canonical manifest、campaign report、共享 toolchain 和
发布 projection。Worker 不启动 Harbor Agent Run，不写 Harbor 模型结果，不修改
其他 task；Loop 本身负责顶层 Pi 会话的并发、session、lease 和回收。
