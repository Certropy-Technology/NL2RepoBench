# AST 驱动的批量出题 Pipeline

本文是当前 Python/Node 批量出题的执行方案。它继承上游 NL2Repo 的任务选择原则：
真实开源 Package、固定完整 revision、自然语言规格、空 workspace、官方测试执行式评分；
只把产物和 verifier 改成更严格的 Harbor separate-verifier 格式。

旧的四文件转换和“先写 instruction、再人工补测试映射”的流程不再作为扩展主路径。
新 Pipeline 以 source/test AST inventory 为廉价前置证据，用动态 collection 和 Oracle
做后置事实确认；任何阶段都不允许用 AST 猜测未观察到的语义。

## 目标

- 在进入 Docker、模型和私有 artifact 阶段前，批量淘汰重复、规模不合格、license 不清、
  API 不可隔离、测试主要依赖外部服务的候选；
- 用统一的 Python/Node inventory 输出建立 API、CLI、fixture、dependency 和 test-to-
  behavior traceability；
- 每个 stage 消费 immutable artifact，可并发、可恢复、可重跑，不让 worker 共同编辑
  catalog/dataset/index；
- 让新增语言只需实现 scanner/runtime adapter/test normalizer，不复制一条新流水线；
- 把“静态候选”“可 author”“可 Oracle”“可发布”明确分层，避免把大量 blocked 题误报成
  production task。

## 总体流水线

```text
candidate discovery
      │
      ▼
source freeze + license + duplicate gate
      │
      ▼
language AST inventory ───────┐
test AST/import inventory ────┼─> API/test behavior graph
package/CLI metadata scan ────┘
      │
      ▼
cheap static gates (LOC/API/dynamic/native/service risk)
      │
      ▼
environment + dependency closure probe
      │
      ▼
ground-truth image + automatic collection
      │
      ▼
spec skeleton -> semantic draft -> bidirectional traceability
      │
      ▼
Harbor package + private verifier + candidate boundary
      │
      ▼
Oracle x3 -> empty/stub/forgery/hang/offline controls
      │
      ▼
blind review -> 5–10 task pilot -> publish
```

每个箭头都是 stage 边界。stage 只读上游 artifact，不读取 worker 的未提交工作目录。

## Stage 0：Candidate discovery

输入可以来自 GitHub 搜索、官方组织列表、已知 Package index 或人工推荐。每个候选必须
先写入 discovery manifest：

```json
{
  "candidate_id": "owner/name",
  "language": "python|node",
  "upstream_url": "https://github.com/owner/name",
  "revision": "full commit SHA",
  "license": "SPDX or unresolved",
  "stars_observed": 0,
  "last_activity": "date",
  "selection_source": "url/report/worker",
  "status": "candidate|rejected|needs-evidence"
}
```

规则：

- 只接受完整 commit SHA；branch、tag、latest 一律不能进入 freeze；
- 目标规模参考上游 NL2Repo：300–120,000 implementation LOC、至少 10 stars、近期有
  活跃、明确许可、官方测试可执行；边界项目记录为 conditional，不偷偷放宽；
- 与 `catalog/tasks`、已发布 source digest、候选报告和 fork/改名包做 normalized name、
  upstream URL、source hash 和 API fingerprint 去重；
- 发现阶段可以高并发，但只写自己的 report artifact。

## Stage 1：Source freeze 与廉价静态门禁

对固定 revision 生成 source archive、树清单、license 清单和 SHA-256。随后执行 AST scanner。

### Python scanner

使用标准库 `ast`，不 import candidate code。扫描：

- package/module/public `__init__` re-export；
- public functions、classes、methods、async functions、decorators；
- positional-only、keyword-only、defaults、annotations、returns；
- CLI entry points（`pyproject.toml`、`setup.cfg`、`console_scripts`）；
- dataclass/Enum/TypedDict/Protocol/Pydantic model 等数据契约；
- `__all__`、dynamic `getattr`、`exec/eval`、C extension/import fallback 标记；
- implementation LOC、test LOC、module graph 和未解析 import。

### Node scanner

使用锁定的 JavaScript/TypeScript parser（首选 tree-sitter grammar，不执行 candidate code）。
扫描：

- ESM `export`、CommonJS `module.exports/exports.*`、re-export；
- functions、classes、methods、async/generator、参数默认值；
- `package.json` exports/bin/types/main/module/files；
- workspace members、package manager 和 lockfile；
- `node:test`/Mocha/Tape/Vitest/Jest 的 test registration；
- dynamic `eval/Function/import()`、native addon、postinstall、network/process/fs 风险；
- build output 是否由 source reproducibly 生成。

### Scanner 输出

每个语言 scanner 输出同一个 `ApiInventory` 形状，语言专属字段放在 namespaced details：

```text
inventory.json
├── schema_shape
├── source_digest
├── scanner_identity + scanner_digest
├── modules[]
│   ├── import_path / export_name
│   ├── kind / signature / source_location
│   ├── public / re_exported / tested
│   └── dynamic_risk[]
├── cli_entries[]
├── data_contracts[]
├── dependency_edges[]
├── risk_flags[]
├── implementation_loc / test_loc
└── completeness {dynamic, generated, native, unresolved}
```

AST 只证明结构，不证明行为。`signature` 也不能替代异常、顺序、确定性、状态变化和
边界语义。

## Stage 2：Test inventory 与 behavior graph

测试 scanner 对测试源码做 AST/import 分析，再结合最终环境 collection：

1. 静态识别 test function/class/parameterization/fixture/import；
2. 找出测试调用的 public symbol、CLI、fixture、文件和外部资源；
3. 标注断言形状：返回值、异常、stdout/stderr、文件、排序、状态、时间、网络；
4. 在 ground-truth image 中实际 collection，生成稳定 leaf ID；
5. 将静态候选引用与实际运行 leaf 合并为 behavior graph。

输出 `behavior-map.json`：

```text
behavior_id
tested_symbols[]
test_leaf_ids[]
assertion_kinds[]
fixture_dependencies[]
external_requirements[]
public_spec_required: true|false
confidence: static|collected|executed
status: covered|missing-spec|dynamic-unresolved|blocked
```

任何 leaf 没有公开可推导的 behavior contract，或任何核心 public API 没有测试覆盖，
都不能进入 package stage。动态生成测试、参数化展开、fixture side effect 和 native
行为必须显示为风险，不得用函数名匹配伪造 traceability。

## Stage 3：Dependency/environment probe

这是 AST 后的第一个动态阶段，仍不运行模型：

- 固定 OS、runtime、architecture、libc、base image digest；
- 解析 package manager lockfile；Node 明确区分 npm/pnpm，不能互换；
- 构建 offline dependency closure，清空 cache 后验证；
- 运行 source install、collection 和完整 official suite；
- 记录每条 setup/test 命令的 exit code、stdout/stderr、wall time、collection、失败 leaf；
- 标记 native build、system package、locale、TTY、browser、DB、network、secret 和
  platform-specific tests。

三次基线 collection 必须稳定，且官方源码在最终环境通过率至少 0.80。失败只归一个主类：
source/spec/environment/verifier/model/infrastructure。

## Stage 4：Spec generation 与 traceability

先由 inventory/behavior graph 生成**不可直接发布的 spec skeleton**：

- Project Description；
- Supports；
- API Usage Guide；
- Implementation Notes。

然后由 author/reviewer 补齐语义。自动 lint 检查：

- public symbol/signature 是否与 inventory 一致；
- 每个 collected leaf 是否映射到至少一个公开 behavior；
- 每个核心 public symbol 是否有测试或明确 `untested` 解释；
- 是否泄漏函数体、测试断言、fixture 名、内部 helper 或完整算法；
- 空输入、Unicode、错误输入、顺序、异常、状态变化和 CLI/package entry point 是否覆盖；
- instruction 是否能在没有源码和测试的空 workspace 中独立推导行为。

人工 blind review 仍是必需门禁，AST 不能替代 reviewer。

## Stage 5：Harbor package

compiler 只消费 canonical task + frozen artifacts + reviewed behavior/spec manifest，生成：

- `instruction.md`；
- agent environment；
- separate verifier image/context；
- private test/command/dependency/Oracle refs；
- candidate subprocess boundary；
- fixed denominator and unified report normalizer；
- `task.toml`、bundle manifest、content hashes。

agent image 不得包含 hidden tests、grader、Oracle、private dependency bytes 或 secrets。
编译必须 deterministic；输出目录已存在、artifact digest 不一致或 private authorization
缺失时 fail closed。

## Stage 6：Oracle 与 controls

只有通过静态和环境门禁的题才消耗 Harbor/Docker 资源。顺序固定：

1. Oracle 三次独立运行；
2. empty workspace；
3. packaging + stub；
4. forged test/reward；
5. install failure/hang/call timeout；
6. offline verifier；
7. reviewer evidence pack。

Oracle 要求三次 `valid=true`、collection/分母稳定、reward `>=0.80`。任何控制异常高分、
private leakage、report mismatch 或 verifier invalid 都回退到 blocked，不修测试来过门禁。

## 批量调度策略

批量不是“所有候选同时跑到底”，而是漏斗：

| Tier | 并发规模 | 资源 | 通过条件 |
|---|---:|---|---|
| Discovery | 50–100 | web/git/静态 | exact SHA/license/去重 |
| AST inventory | 30–60 | CPU/磁盘 | API/test inventory 完整度 |
| Env probe | 15–30 | sandbox/CPU | offline closure + stable collection |
| Spec/trace | 10–20 | reviewer/LLM | 双向 traceability |
| Harbor package | 5–10 | Docker/磁盘 | deterministic bundle + boundary |
| Oracle/control | 3–5 | Harbor/模型 | Oracle x3 + controls |
| Pilot | 5–10 | Harbor/model budget | 难度/失败归因合理 |

同一 task 的 stage 只能有一个 claim；worker 只写
`catalog/tasks/<task-id>/authoring/<stage>/` 或独立 worktree。共享 catalog、dataset、
registry、报告和发布目录由 integrator 串行写入。每完成一题立即落盘 stage result。

静态失败不消耗 Docker；纯 infrastructure failure 才可有上限地重试；source/spec/
environment/verifier/model 失败保持原 trial 身份和证据，不伪装成 infra retry。

## 统一 stage artifact

每个 stage 产生：

```text
stage.json
├── task_id / stage / stage_contract
├── input_artifacts[] / input_hash
├── output_artifacts[] / output_hash
├── scanner/runner/tool versions
├── status / failure_class / reason
├── owner / worker / claim / timestamps
├── retry_count / next_retry_at
└── metrics {loc, api_count, test_count, coverage, traceability, risk_flags}
```

artifact 使用 content-addressed storage；stage contract 改变会使 downstream cache 失效，
而不会重跑 source freeze。状态机的 terminal 状态只有 `published`、`blocked`、`excluded`。

## 推荐 CLI 形状

这些是 Pipeline 的目标入口；在实现前不能声称已经可用：

```bash
nl2repo author discover --input candidates.json --output authoring/
nl2repo author scan-source TASK --output authoring/
nl2repo author scan-tests TASK --output authoring/
nl2repo author trace TASK --output authoring/
nl2repo author probe TASK --output authoring/
nl2repo author draft-spec TASK --output authoring/
nl2repo author validate-spec TASK --output authoring/
nl2repo author package TASK --output authoring/
nl2repo author oracle TASK --attempts 3
nl2repo author controls TASK
nl2repo author publish TASK
```

第一实现优先提供 `scan-source`、`scan-tests`、`trace` 的本地 deterministic 命令；Harbor
和模型阶段继续复用现有独立脚本，等 artifact contract 稳定后再接入统一 CLI。

## 新语言接入协议

新增语言不新增流水线：

1. 实现 `ApiScanner` 和 `TestScanner`；
2. 输出同一 `ApiInventory`/`BehaviorMap`；
3. 注册 runtime/package-manager adapter；
4. 提供 lock/store、candidate boundary、report normalizer；
5. 用一个 synthetic fixture 跑通所有静态阶段；
6. 用 1 个真实候选完成 Oracle/control vertical slice；
7. 才能进入 10–20 题批次。

## 成功指标

Pipeline dashboard 必须同时显示：

- 每个 tier 的输入/通过/blocked/excluded 数；
- source digest/license/duplicate rejection rate；
- AST inventory completeness 和 dynamic/native risk rate；
- API-to-test、test-to-spec 双向覆盖率；
- environment/offline/collection 稳定率；
- Oracle、empty、stub、forgery、offline control 结果；
- 每题 Docker/model wall time、tokens/cost、trajectory coverage；
- 按 task 宏平均的有效 benchmark score，不把 infra/verifier failure 当模型 0 分。

“出题更多”只有在这些指标仍可审计时才算扩展成功。
