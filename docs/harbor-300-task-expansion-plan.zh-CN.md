# 300 道 Harbor Task 扩展计划（Historical）

> This is a superseded historical plan. The active Package campaign targets
> 500+ cumulative publishable tasks, uses one Oracle run, and skips a task
> whenever the trusted OSS inventory already contains a finished run. The x3
> Oracle requirements below are historical evidence and must not be applied to
> the active campaign.

目标：在不伪造 provenance、测试分母、依赖 closure 或 verifier boundary 的前提下，
将 NL2RepoBench 扩展到 **300+ 道 published Harbor Task，并对同一批 300+ task_id
实际运行 Benchmark**，逐步形成新的 unified dataset release。测量对象仍然是上游
NL2Repo 的 0-to-1 repository generation；Harbor 只是更严格的执行和隔离格式。

## 目标口径

本计划区分三个数字，避免把大量静态候选误报为有效 benchmark：

| 数字 | 含义 | 是否计入 benchmark score |
|---|---|---|
| candidate | 已发现、去重、具有 exact SHA 的候选 | 否 |
| Harbor task candidate | 已有 catalog source，可确定性生成 Harbor tree，但可能 blocked | 否 |
| published task | source、环境、依赖、spec、verifier、Oracle、controls、review 全通过 | 是 |

最终目标是两个同时成立的条件：

1. 至少 300 个 `published task`；
2. 新 Benchmark dataset manifest 中至少包含同一批 300 个 task_id，并且每个 task 都
   有新 release 的真实 Harbor trial 结果。

在到达 300 之前，所有 candidate 和 blocked 记录都保留证据和 blocker，不把 blocked 当
成 0 分题，也不从旧 v1/v2 结果推导新 release 分数。

## 组合目标

初始 300 题目标组合：

| 维度 | 目标 |
|---|---:|
| Python packages | 180 |
| Node/npm packages | 90 |
| Node/pnpm/workspace packages | 30 |
| Easy | 75 |
| Medium | 135 |
| Hard | 90 |
| parser/data/serialization | >=75 |
| CLI/filesystem/devtools | >=60 |
| validation/model/schema | >=45 |
| algorithms/graph/geometry/statistics | >=45 |
| text/format/URL/security utility | >=45 |
| external-service/native-heavy candidates | 0 published（只能 conditional/blocked） |

难度按冻结 revision 的 implementation LOC 和实际行为复杂度共同审核，不从 stars 或
测试数量机械推断。

## 产能漏斗

为了得到 300 道 publishable 题，预计需要先发现约 700–900 个候选：

```text
900 discovery candidates
  -> 600 pass exact SHA/license/duplicate/size screen
  -> 450 pass AST API/test inventory
  -> 360 pass environment/dependency/offline probe
  -> 330 pass spec + bidirectional traceability
  -> 315 deterministic Harbor package candidates
  -> 300 Oracle/control/review published tasks
```

这些是规划容量，不是已经完成的数量。每个箭头都要产生可检查 artifact；任何一层
通过率异常下降都要停批并修复系统性问题，而不是放宽下一层门槛。

## 批次与并发

### Discovery/AST

- 每波 4 个 researcher lane，每 lane 25–40 个候选；
- Python 和 Node 分开扫描，pnpm 不强行转换为 npm；
- AST scanner 只解析源码，不 import/执行 candidate；
- 每波完成后做 parent-side exact URL/SHA/license/archive/dedup scan；
- 这一层可以 8–16 个 worker，主要受网络和 `/tmp` 限制。

### Authoring

- 每批 10–20 个 task-local writer；
- 每个 writer 只写 `catalog/tasks/<task-id>/`；
- blocked/audit 也是合法 stage 结果，但不会自动获得 Harbor publication；
- integrator 串行合并、验证、提交和同步 `/data/NL2RepoBench-current`；
- 每批结束立即清理已终态 worktree，防止 `/tmp` ENOSPC。

### Harbor/Oracle

- 先 2–4 个并发，确认 cleanup 和 Docker 空间稳定后再提高到 4–8；
- 每个 task/attempt 使用全新 run root；
- `run_model_from_pi.py --concurrency 2..8` 只控制模型 trial，不改变 task/attempt 身份；
- 每个 batch 必须保留 `queue.log`、`cleanup.log`、result、grading、trajectory 和
  failure classification；
- 任何 orphan compose project、缺失 `finished_at` 或 runner cleanup failure 都阻塞该批
  reliability gate。

## 每题流水线

```text
discover
  -> freeze-source
  -> AST API inventory
  -> test inventory + behavior graph
  -> ground-truth image
  -> offline dependency closure
  -> collection x3
  -> spec skeleton + semantic review
  -> hidden-test/spec traceability
  -> Harbor separate verifier
  -> Oracle x3
  -> empty/stub/forgery/hang/offline controls
  -> blind review
  -> publish
```

Python 使用标准库 AST scanner；Node 使用锁定 TypeScript compiler API scanner：

```bash
uv run nl2repo author scan-source <python-source> \
  --output authoring/api-inventory.json

cd tools/node-inventory
npm ci --ignore-scripts --offline
npm test
node dist/cli.js <node-source> --output /tmp/api-inventory.json
```

AST 只能证明结构、导出、signature、调用和风险标记，不能证明行为。异常、状态、顺序、
确定性、Unicode、空输入、CLI 副作用和外部服务都必须由 collection、执行证据和 reviewer
确认。

## 300 题的 release gates

每 25 题是一个 integration checkpoint：

1. source digest、license、full revision、duplicate report 完整；
2. 所有 task 有明确 `published`/`blocked`/`excluded` 状态；
3. published task 的 collection、固定分母和测试版本冻结；
4. Oracle 三次 `valid=true`、reward `>=0.80`、collection 稳定；
5. empty、stub、forgery、install failure、hang、offline controls 通过；
6. Harbor bundle deterministic，private tests/grader/Oracle 不在 agent image；
7. review、artifact manifest、content hash 和运行命令可复现；
8. batch cleanup 无 orphan container，模型/环境/verifier/infrastructure 分类完整。

任一 checkpoint 失败，下一批只允许做修复和重新验证，不允许继续堆数量掩盖问题。

### Benchmark dataset gate

Benchmark 不从 `catalog/tasks/` 目录数量、Harbor tree 数量或 candidate report 数量推导
题目集合。发布前必须运行：

```bash
python3 scripts/build_published_benchmark_manifest.py \
  --dataset-release 1.0.0 \
  --output .nl2repo/datasets/nl2repobench-harbor-300/manifest.json \
  --parquet .nl2repo/datasets/nl2repobench-harbor-300/tasks.parquet
```

该命令默认要求至少 300 个 source `lifecycle.status = published` 且具备完整 Harbor
tree；不足时以非零状态 fail closed。`--allow-below-target` 只用于诊断，生成的 manifest
状态为 `below-target`，不能交给 benchmark runner。

对通过 gate 的 manifest，runner 必须为每个 task_id 创建新的 run root。至少一次有效
trial 才能称为“Benchmark 已覆盖”；正式能力比较仍按预先声明的 attempts/pass@k 执行。
缺失 trial、`finished_at`、grading、trajectory、cleanup 或 `valid=true` 的 task 必须
单独列在 reliability report，不能从分母中静默删除。

## 语言与 package-manager 扩展

新增语言或 package manager 不增加一套顶层 schema/compiler/grader：

- 实现 runtime AST scanner；
- 注册 runtime/package-manager adapter；
- 输出统一 `ApiInventory`、behavior graph 和 leaf report；
- 提供 lock/store、candidate boundary、offline installer；
- 先用一个 synthetic fixture 和一个真实候选跑通 vertical slice；
- 通过后才进入 10–20 题批次。

## 当前执行顺序

当前 104 legacy 题、已有 75 个 Harbor tree、现有 catalog candidate 和新 Python/Node
discovery 报告都要先做 parent-side inventory/dedup。接下来按以下顺序扩张：

1. 继续收集 Python/Node/npm/pnpm 各 35 候选的 discovery wave；
2. 每次集成 4–10 个 task-local evidence package；
3. 选通过 AST/环境门禁的题进入 Harbor package wave；
4. 先完成 25 题 checkpoint，再提高 Oracle/model 并发；
5. 逐 checkpoint 累积到 300 个 published task。

没有 exact source、离线 closure、candidate boundary 或 Oracle/control 证据的题，仍然
会被保留在 catalog 的 blocked/audit 区，而不会被删除或伪装成已发布题。
