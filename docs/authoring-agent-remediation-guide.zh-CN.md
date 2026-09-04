# 出题 Agent Remediation Guide

本文件是顶层模型直接编排的 Raw Package -> Harbor worker contract。它不负责模型
或其他模型运行；Worker 必须完成题目自己的生产门禁，包括正式 Harbor Oracle、
empty/stub/forgery/install-failure/panic/hang/oversized-output/background-process
和 offline controls。Worker 的终点是把带有完整结构化证据的 task 交给 integration，
状态为 `controls-passed`。后续模型评测由独立 Harbor Run 消费 catalog。

## 存储纪律

大型 source clone、dependency lock、npm cache、Docker build context、test bundle 和
Oracle artifact 必须放在项目磁盘（推荐 `.nl2repo/authoring-work/<batch>/<package>/`），
不要放 `/tmp` tmpfs。`/tmp` 只允许小型、bounded 的进程 socket/短期日志，单个 worker
不得超过 256 MiB；每个 stage 完成后立即清理。Worker brief 必须记录工作目录和 cleanup
结果。这样可以避免多个并发 Package 把 tmpfs 打满，误报为 Docker/依赖/模型故障。

## 核心规则

下面这些不是 Block 原因，而是 Worker 必须完成的 remediation：

- 没有 immutable verifier image、base-image digest 或完整 environment lock；
- runtime/dev dependency 没有 exact pin、hash lock 或 build-stage install contract；
- 没有 build backend、Dockerfile、package lock、submodule materialization 或测试闭包；
- native、network、database、browser、TTY、interactive 等 risk flag；
- 上游测试 runner、Python/Node 版本和当前镜像不兼容。

Worker 应先固定 revision 和 license，再选择兼容 runtime，补 requirements lock、系统包、
Dockerfile、build backend、candidate boundary 和 verifier。每次尝试必须写入 task-local
`provenance/` 或 `evidence/`：命令、版本、exit code、stdout/stderr 路径、digest、
下一步动作。Python verifier 依赖必须在 Docker build 阶段按 hash lock 联网安装；禁止
把 wheelhouse vendor 到 task，也禁止用 `--no-index` 伪造 offline verifier 安装。

只有以下情况，在 remediation attempts 已经有证据后才可以 `blocked`/`excluded`：

1. 没有任何可执行测试，无法形成固定分母；
2. license 不清楚或不允许需要的分发方式；
3. 经过 fetch/checkout 尝试仍不能固定 immutable revision；
4. 依赖付费账号、不可冻结远端服务或不可复现的外部数据；
5. 在 bounded build/test probe 后仍明显超过资源预算。

“没有材料”本身不能写成 Block。若 remediation 失败，报告必须包含
`attempted_commands`、`tool_versions`、`exit_codes`、`failure_logs`、`failure_class` 和
`next_unblock_action`。没有这些字段的 Block handoff 不可合入。

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
  -> empty/stub/forgery/install-failure/panic/hang/output/background-process/offline controls
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
和安全相对 entrypoint。hidden tests、adapter、fixture、grader 和 dependency lock 不得进入
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
  --toolchain toolchain.lock.toml --allow-private
```

然后在最终 compiled bundle 中运行一次 Oracle，要求 `valid=true`、collection 等于
frozen denominator、reward `>=0.80`。再运行 empty/stub/forgery/install-failure/
panic/hang/oversized-output/background-process/offline controls。所有运行必须保留
result、grading、network 和 reward 证据；empty/install-failure 的允许 0/0 结果必须
显式记录。只有完成这些门禁后，Worker 才能写 `controls-passed` handoff。
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
status: controls-passed | blocked | excluded
BLOCKERS: none or precise evidence-backed reason
```

Integrator 仍然负责独立复核、串行合并、dataset、canonical manifest、campaign report、
共享 toolchain、发布 projection、OSS archive 和 worktree 清理。Worker 不运行模型
Agent evaluation，不写模型结果，不修改其他 task；但 Worker 必须运行并记录本题的
trusted Oracle 和 controls。
