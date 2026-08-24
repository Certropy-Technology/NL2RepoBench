# P2 执行计划：统一 Leaf Report / Evaluator 与 Adapter 解耦验证

状态：proposed（2026-08-24）
适用模式：`explain` + 后续 `validate`（本计划不改题目内容、不改分母、不重跑已发布结果）

本文是 P2 的可执行 TODO。目标不是"加第三门语言"，而是**先证明 runtime adapter 抽象真的
解耦**，再决定是否扩语言。落地顺序按风险从低到高排列，每步都有可验证的门禁。

## 0. 结论先行

`docs/runtime-adapter-architecture.zh-CN.md` 和 `docs/unified-contract-migration-adr.zh-CN.md`
描述的目标架构中，以下模块**尚不存在**：

```text
verification/normalizer.py     # 缺失
verification/evaluator.py      # 缺失
runtimes/<language>.py         # 缺失（整个目录不存在）
package_managers/<manager>.py  # 缺失（整个目录不存在）
```

实际存在的是两套平行实现。已核对的重复对：

| 职责 | Python | Node | 行数 |
|---|---|---|---|
| Harbor 编译 | `harbor/compiler.py` | `harbor/node_compiler.py` | 779 / 478 |
| 评分 | `verification/grader.py` | `verification/node_grader.py` | 178 / 272 |
| candidate 边界 | `verification/candidate_client.py` | `verification/node_candidate_client.py` | 231 / 131 |
| candidate 安装 | `verification/candidate_install.py` | `verification/node_candidate_install.py` | 158 / 194 |
| command plan 白名单 | `verification/command_plan.py` | `verification/node_command_plan.py` | 46 / 67 |
| 报告/计数模型 | `verification/models.py` | `verification/node_models.py` | 76 / 111 |

唯一已经做对的是 `harbor/registry.py`：显式字典、fail closed、未注册组合报错并列出可用
identity。它是 P2 应当复制到 verifier 侧的模式，不是要重写的部分。

**ADR §5 要求"统一 leaf report + 一个 fixed-denominator metric，runtime adapter 不是新的
公开 metric family"。当前 catalog 里有两个 metric family 在同时生产分数**：

```text
contract_id = "fixed-test-pass-rate-v1"        108 个 task.toml
contract_id = "node-test-leaf-pass-rate-v1"      6 个 task.toml
```

这直接违反 ADR。P2 的核心交付就是消除这个分裂。

## 1. 必须先修的地基缺陷

以下四项是读代码核实的事实，不是推测。它们决定 P2 的起点。

### 1.1 metric contract 是死字段（最高优先）

两个 grader 的签名都只接受字符串 ID：

```python
# verification/grader.py
def grade_verification(*, expected_total: int, metric_contract: str = "fixed-test-pass-rate-v1", ...)
# verification/node_grader.py
def grade_node_test_report(*, expected_total: int, metric_contract: str = "node-test-leaf-pass-rate-v1", ...)
```

`MetricContract` / `NodeMetricContractV2` 对象从不传入 grader。`reward` 恒为
`passed / expected_total`。后果：

- `MetricContract.excluded_statuses = ("skipped",)` 声明 skipped 被排除，实际 skipped 留在
  分母。**声明与行为不一致。**
- `NodeMetricContractV2.denominator_statuses`（5 个状态全含）同样从不生效。
- 两者当前**算出的数值恰好相同**（都是 `passed / frozen_total`），所以历史分数没有被算错；
  但任何人改动这些声明字段都不会改变分数，改动会静默失效。

`rg` 验证：`excluded_statuses|passed_statuses|denominator_statuses` 在 `src/` 的 grading 路径
零引用，仅出现在 `domain/models*.py` 定义处和 `scripts/convert_testfiles_to_harbor.py` 的
字面量。

### 1.2 两套 grader 的不变量强度不对等

| 不变量 | Python | Node |
|---|---|---|
| leaf ID 唯一性 | 有检查，但在 collection 侧（`models.py:61`），非 JUnit 侧 | `_duplicate_test_id()` 在报告侧 |
| `todo` 状态 | `TestCounts` 无此字段 | `NodeTestCountsV2` 有 |
| 报告归属 | 读 pytest 产出的 JUnit XML（第三方格式） | 读 verifier 自有 JSON（更强） |
| `INTEGRITY_FAILURE` | 无 | 有 |
| model failure 集合 | `SETUP_COMMAND_FAILED` | `CANDIDATE_CALL_FAILED` |

`docs/authoring-pilot-retrospective-20260824.zh-CN.md` 声称 wrapper "固定校验：唯一 leaf
IDs"。**这条对 Python lane 成立**，已实测确认：

```text
重复 nodeid -> valid=False reason=collection-report-malformed reward=0.0
唯一 nodeid -> valid=True  reward=1.0
```

机制是 `CollectionReport.validate_nodeids`（`models.py:58-62`）抛 `ValueError`，被
`grade_verification` 捕获为 `COLLECTION_REPORT_MALFORMED`。检查位置在 collection 报告而非
JUnit，所以只读 `parse_junit` 时看不到 —— 这是我最初误判的原因。

实测 67 份含 `nodeids` 的 `grading.json`，重复数 0。

残留的真实缺口比原先描述的小：**没有人交叉校验 JUnit 的 testcase 集合与 collection 的
nodeids 集合是否一致**。两者各自与 `expected_total` 比数量，但不比身份。理论上可以数量相同
而身份不同。这个缺口两侧都有，优先级低于 1.1。

### 1.3 failure 分类无法跨语言汇总

`VerificationReason` 与 `NodeVerificationReason` 是两个不相交枚举，Node 侧字符串带 `node-`
前缀（`node-collection-mismatch` vs `collection-mismatch`）。AGENTS.md §12 要求报告
"Reliability：model/spec/environment/verifier/infra 失败数"，当前分析层无法直接聚合。

### 1.4 grader 靠 argv 形状隐式分派

```python
# verification/cli.py
node_mode = args.report is not None or args.runner_exit_code is not None
```

ADR §1 明确"`schema_version` 只描述数据形状，不能承担运行时分派"。这里是**参数形状**承担了
分派，属于同一类问题。`verification/__init__.py` 也只导出 v1 名字。

## 2. pnpm 为什么是正确的下一个实验

不是因为需要 pnpm 题，而是因为它是**最便宜的抽象伪证测试**：同语言、换 package manager，
理论上只应触碰 `package_managers/`。

当前状态已核实：

- `PackageManager.PNPM` 枚举值存在（`domain/runtime.py:36`）；
- `RuntimeDiscriminator` 接受 `node+pnpm` 组合并通过校验；
- `harbor/registry.py` **未注册** 该组合 → `UnknownRuntimeAdapterError`（fail closed，行为正确）；
- `src/` 与 `scripts/` 里 pnpm 的实现代码为 **0 行**。

已经能预判的硬阻塞（`domain/models_v2.py:129`）：

```python
lockfile_name: Literal["requirements.lock.txt", "package-lock.json"]
package_manager: Literal["uv", "pip", "npm"]
```

**pnpm 在当前 domain 里无法表达。** 必须改 `Literal` 才能加 pnpm —— 这正是"复制而非组合"的
症状：新增 package manager 需要修改 domain 层的封闭枚举，而不是注册一个 adapter。同类问题
还有 `TestManifestV2.framework = Literal["node:test"]` 和
`report_format = Literal["node-test-json-v1"]`。

因此 pnpm 排在重构之后：**先让抽象成立，再用 pnpm 验证它成立**。反过来做只会产出第三套
平行实现。

## 3. TODO

### P2-0 冻结行为基线（阻塞后续全部步骤）

- [ ] 收集当前有 Oracle 证据的 task 的 `reward.json` + `grading.json` 原始字节，落为
      golden fixtures。范围：12 个 Python `oracle-passed`、10 个 Python `packaged`、
      `canonicalize`（Node，证据在 `reports/node-canonicalize-production-gate.v1.json`）。
- [ ] 为两个 grader 补齐 pure-function 回归测试：给定 JUnit/JSON 输入 → 断言完整
      `grading.json` 字节。不依赖 Docker。
- [ ] 记录基线 commit SHA 与 fixtures digest。

门禁：没有这一步，后面任何 refactor 都无法证明"行为不变"，已有 Oracle 证据会全部作废。

### P2-1 引入统一 LeafReport 与 evaluator

- [ ] 新增 `verification/leaf_report.py`：canonical leaf 模型。字段取两侧并集 ——
      稳定 leaf id、`passed|failed|error|skipped|todo`、collection errors、trusted runner
      exit code、frozen denominator。
- [ ] 新增 `verification/evaluator.py`：唯一 fixed-denominator 评分入口。签名接收
      **`MetricContract` 对象**，不是字符串 ID。
- [ ] 共享不变量集中到 evaluator：leaf id 唯一性、collection error、`collected != expected`、
      count mismatch、exit code 与 leaf 状态一致性。
- [ ] 两个 grader 改为薄封装，内部委托 evaluator。

门禁：P2-0 全部 golden fixtures 字节不变，无例外。leaf-id 唯一性两侧都已有，不会因统一而
引入新的失败。

### P2-2 拆出 normalizer

- [ ] `verification/normalize/pytest_junit.py`：吸收 `junit.py` + `models.py` 的 pytest 语义。
- [ ] `verification/normalize/node_test_json.py`：吸收 `node_models.py` 的 `node:test` 语义。
- [ ] normalizer 只做"框架输出 → LeafReport"，**不评分、不判 failure class**。
- [ ] 为每个 normalizer 写针对畸形输入的单测（截断 XML、重复 id、collected 与数组长度不一致、
      超尺寸报告）。

门禁：`rg` 确认 `evaluator.py` 内不出现 `junit`、`pytest`、`node:test` 等框架名。

### P2-3 统一 failure taxonomy

- [ ] 合并为一个 runtime-neutral `VerificationReason`，去掉 `node-` 前缀。
- [ ] 保留一张**冻结的**历史映射表用于读旧报告，放在 `analysis/`，**不放进 verifier 运行路径**
      （ADR §2 禁止 runtime 兼容 shim，但显式允许历史 archive 阅读）。
- [ ] 统一 model-failure 集合，逐条写明每个 reason 归属哪个 `FailureClass` 及理由。
- [ ] 删除 `NodeVerificationReason` 的描述性别名（`NODE_REPORT_MISSING` 等），它们只是同一
      成员的第二个名字，会让 taxonomy 看起来比实际大。

门禁：`analysis/` 能对 Python + Node 混合结果输出单一 failure-class 分布表。

### P2-4 让 metric contract 真正生效

- [ ] evaluator 读取 `passed_statuses` / 分母状态集合 / `collection_mismatch`。
- [ ] 写一个**反向测试**：改动 contract 字段必须导致 reward 改变。这是防止 1.1 复发的唯一手段。
- [ ] 判定 `excluded_statuses = ("skipped",)` 的处置。**实测前提：扫描 393 份 `grading.json`，
      `skipped > 0` 的有 0 份。** 所以两个选项对现有全部证据算出的分数完全相同，差异只影响
      未来出现合法 skip 的题（如平台相关测试）。两个选项必须显式选一个并记录：
      - (a) 声明改为与现行为一致（skipped 留在分母，等价于算作未通过）；
      - (b) 行为改为与声明一致（skipped 从分母剔除，`passed / (frozen_total - skipped)`）——
            会改变分母定义，须升 dataset release。
      建议 (a)：现行为符合 AGENTS.md "所有已收集的非 passed leaf 留在固定分母"，且 (b) 会让
      分母随候选行为浮动 —— agent 只要把测试 skip 掉就能缩小分母，是可被利用的评分面。
- [ ] 两个 `contract_id` 合并为一个。旧 ID 只保留在历史 archive。

门禁：catalog 中 `contract_id` 取值唯一；反向测试通过。

### P2-5 显式 grader 分派

- [ ] `verification/cli.py` 去掉 `node_mode` 形状嗅探，改为显式 `--runtime` 参数。
- [ ] 建一个 verifier-侧 registry，镜像 `harbor/registry.py` 的显式字典 + fail closed 模式。
- [ ] `verification/__init__.py` 导出统一名字，不再只导出 v1。

门禁：未知 runtime 报错并列出已注册 identity；无参数形状分派。

### P2-6 抽取共享 compiler 骨架

- [ ] 比对 `compiler.py` 与 `node_compiler.py` 的 10 组同名私有方法
      （`_write_instruction` / `_write_environment` / `_write_verifier` / `_write_solution` /
      `_write_task_toml` / `_test_script` / `_extract_private_bundle` / `_copy_tree` /
      `_write_readme` / `_write_bundle_manifest`），逐个判定"通用"或"runtime 特有"。
- [ ] 通用部分进 `harbor/task_writer.py`；runtime 特有部分留在 adapter，通过 protocol 挂接。
- [ ] `_test_script` 明确归 adapter（它生成 runtime 专属命令）。
- [ ] `command_plan` 两套白名单合并为一个模型 + 每 runtime 的 allowlist 数据。Python 侧当前是
      裸 dict，缺 pydantic 模型和 `report_format`，需补齐到 Node 侧的强度。

门禁：Harbor tree golden 输出逐字节不变（含 `task.toml`、Dockerfile、bundle manifest）。
golden 只允许从 catalog source 重新生成，**禁止手改 golden 让 refactor 通过**。

### P2-7 pnpm 作为伪证实验

- [ ] 把 `DependencyBundleV2` 的 `lockfile_name` / `package_manager` `Literal` 改为由
      package-manager adapter 声明的能力集合，domain 只校验一致性。
- [ ] 实现 `package_managers/pnpm.py`：lock v9 解析、offline store 校验、install 命令。
- [ ] 注册 `(NODE, PNPM)`，选 1 道真实 pnpm 包做 vertical slice。
- [ ] 跑当前 contract 的门禁：Oracle x1（`valid=true`、collection 等于固定分母、reward ≥ 0.80）
      + empty / stub / forgery / install-failure / hang / offline 控制。
- [ ] **度量并记录**：新增 pnpm 的 diff 里，落在 `package_managers/` + registry 注册 + tests +
      docs 之外的行数。

门禁（这是 P2 的真正验收点）：上述"之外的行数"应接近 0。若需要改 evaluator、compiler 骨架或
编排层，说明抽象未成立 —— **停止扩语言，回到 P2-1..P2-6 修复**，并把实际数字写进本文。

### P2-8 才决定第三门语言

- [ ] 用 P2-7 的实测成本估算 Go/Rust adapter 成本。
- [ ] 只有 pnpm 的越界行数达标才启动。否则先修抽象。

## 4. 阻塞项（来自 P3，会污染 P2 的证据链）

这些不修，P2 的 golden/回归证据不可信：

- [ ] worktree 有 100+ 个 `catalog/sources/*/task.toml` 未提交修改，`git status` 脏。golden
      基线必须在干净 checkout 上生成。
- [ ] `.github/workflows/core.yml` 已删除、`phase2-controls.yml` 处于 staged 删除 —— 没有 CI
      看守，refactor 回归无法自动捕获。P2-1 之前至少恢复 contract/adapter 单测的 CI。
- [ ] `scripts/summarize_phase2_controls.py` 仍断言 `oracle-1/2/3`，与一次 Oracle contract
      冲突，会 `FileNotFoundError`（见 SCRATCHPAD）。

## 5. 明确不做的事

- 不改 NL2Repo 的测量对象、不改题目 instruction、不改隐藏测试内容。
- 不动 104 道 `test_files/` legacy projection。
- 不重新解释或合并历史分数。若 P2-4 选了 (b)，必须升 dataset release 而不是重算旧结果。
- 不做运行时兼容 shim。历史枚举映射只服务 archive 阅读。
- 不为了让 refactor 通过而手改 golden、放宽不变量或删除功能断言。

## 6. 验收（整个 P2）

同时满足才算完成：

1. 只有一个 `contract_id` 在 catalog 中生产分数；
2. 只有一个 evaluator 计算 reward，且它读取 contract 对象而非字符串；
3. `rg` 确认编排层（compiler 骨架、evaluator、CLI）无语言名分支，registry 是唯一路由点；
4. P2-0 全部 golden 字节不变；
5. failure taxonomy 单一，能跨 Python/Node 聚合；
6. pnpm vertical slice 明确 pass 或 blocked，且越界改动行数已实测并记录；
7. 本文的空缺数字（pnpm 越界行数、P2-4 选项）已回填。
