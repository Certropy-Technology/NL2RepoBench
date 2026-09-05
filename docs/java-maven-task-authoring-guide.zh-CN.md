# Java/Maven 出题执行指南

本文是 Java/Maven Harbor task 的 worker 和 integrator contract。凡是新建、恢复或
批量出 Java/Maven task，先读本文，再读 `docs/task-authoring-guide.zh-CN.md`、
`docs/authoring-agent-remediation-guide.zh-CN.md` 和
`docs/phase2-harbor-verifier.zh-CN.md`。

本文回答三个问题：worker 要做什么、做到什么程度才算完成、缺材料时如何留下可重开的
证据。本文中的“完成”永远指真实命令和 artifact 证据，不指根据源码猜测的结果。

## 1. 交付目标

完整 Java task 必须形成以下闭环：

```text
immutable source
  -> license/source digest
  -> Java API inventory
  -> bounded public contract
  -> separate verifier + positive frozen denominator
  -> Maven lock/offline store/inventory
  -> private CAS registration
  -> generated Harbor runtime
  -> Oracle once + controls
  -> evidence-bound handoff
```

终态含义：

| 状态 | 含义 |
| --- | --- |
| `awaiting-integrator` | worker 已完成 task-local authoring/staging，父 agent 仍需注册 CAS、编译 runtime 或跑 gates |
| `packaged` | 当前 compiler 已生成 closed-world runtime，但 Oracle/controls 未全部完成 |
| `controls-passed` | 当前 bundle 的 Oracle 和全部必要 controls 均有真实 receipt |
| `blocked` | 有具体、可重现的 blocker，且有 hash-bound evidence 和 remediation |
| `excluded` | 有审计依据，明确不进入当前 dataset |

`packaged`、`oracle-passed` 和 `pilot` 都不能单独称为 `production-valid`；`published`
还需要独立 publication approval 和 transaction。

## 2. 固定边界

### 2.1 Runtime identity

Java task 必须使用：

```text
language = java
package_manager = maven
Temurin JDK = 21.0.12+8
Maven = 3.9.11
platform = linux/amd64
libc = glibc
```

compiler 通过 `java+maven` 路由。不要猜测 language/package-manager，也不要重新引入
旧 Python/Node/Go 专用 dependency schema。

### 2.2 一题一 writer，parent-only CAS

worker 只拥有：

```text
catalog/sources/<task-id>/**
.nl2repo/authoring-work/<task-id>/**
```

worker 不写：

```text
.nl2repo/artifacts/**
catalog/datasets/**
reports/**
toolchain*.lock.toml
src/nl2repobench/**
其他 task 目录
```

worker 可以生成待注册的 lock、store、inventory、verifier 和 Oracle bytes，但必须放在
task-local staging，并提供 manifest、size、media type、SHA-256 和注册顺序。只有 parent
integrator 可以写 shared CAS、补正式 refs、生成 `catalog/tasks/<task-id>`、运行最终 gates
及提交/推送。

### 2.3 NoNetwork 分层

parent 的 authoring freeze 阶段可以联网冻结：

```text
Git source at exact commit
LICENSE/NOTICE bytes
Maven artifacts and transitive closure
```

冻结之后以下阶段必须断网：

```text
agent / candidate / verifier / Oracle / controls
```

不要把运行期网络访问写入 task 作为补救手段。

## 3. Worker 执行步骤

### Step 0：确认输入

确认 parent 提供：task id、repository URL、完整 40-hex revision、source archive path
和 hash、license expectation、toolchain digest、task-local staging path。

**完成条件：** handoff 能逐字列出所有输入和写入边界；source archive 不存在时停止为
`needs-input`，不要凭记忆写 API 或 instruction。

### Step 1：冻结并验证 source

在 task-local staging 解压 source archive，核对：

```text
revision == parent-provided revision
archive/tree digest 可重算
LICENSE/NOTICE bytes 和 SHA-256
不是 floating branch、LATEST、RELEASE 或 SNAPSHOT
```

**完成条件：** `source-freeze.json` 包含 URL、完整 commit、archive digest、license SPDX
和 digest、toolchain digest、观察时间；所有值均可由本地 bytes 重算。

### Step 2：静态 Java API inventory

不得 import 或执行上游源码。静态记录：

```text
public class/interface/enum/record
public method signature
package/source path
imports
main/test file counts
risk flags
```

从 inventory 选择一个小而有意义的 bounded public slice。优先：纯值对象、字符串/字节
转换、集合操作、解析器的无服务部分、`java.sql` 标准接口上的可控 adapter。

**完成条件：** inventory JSON 已 hash；contract 中每个类型、方法、输入、返回值、异常、
状态和副作用都有 source path/line 证据。

### Step 3：定义 public contract

contract 必须写清：

```text
exact package and type names
exact signatures
accepted input domain
return type/shape
ordering and determinism
state/side effects
exception behavior
boundary cases
```

公开 instruction 不得包含 private test 名称或断言、verifier entrypoint、Oracle source、
完整参考实现、源码下载 endpoint 或未纳入 contract 的行为。

### Step 4：编写 instruction.md

instruction 必须采用 `autojump/start.md` 和 `autorccar/start.md` 的长格式，核心标题
顺序固定：

```markdown
# Introduction and Goals of the <Project> Project

## Natural Language Instruction (Prompt)
## Environment Configuration
### Core Dependency Library Versions
## <Project> Project Architecture
### Project Directory Structure
## API Usage Guide
### Core APIs
### Actual Usage Modes
### Supported Function Types
### Error Handling
## Detailed Implementation Nodes of Functions
```

API Guide 必须给出真实 import path、完整 signature、参数、返回值、异常和示例。Implementation
Nodes 按行为组织，不复制实现函数体、private tests 或上游算法。每个 hidden leaf 都必须
能追溯到 instruction 中的公开行为。

Environment 至少明确：Temurin 21.0.12+8、Maven 3.9.11、Linux amd64、执行期无网络、
candidate POM 仅为 metadata、runtime dependency policy。

**完成条件：** instruction 包含上述标题；inventory 和 instruction 可双向追溯；没有
private material 或可直接取回 reference source 的路径。

### Step 5：设计 separate verifier

verifier 必须从独立 candidate JVM/JSON contract 调用候选。trusted verifier 不得直接
import candidate，也不得让 candidate 写 grading、JUnit、collection 或 reward。

推荐使用 JDK 标准库 harness：

```text
javac --release 21
candidate process / JSON contract
verifier-owned Open Test XML
fixed positive denominator
```

上游测试依赖不是自动的 task 依赖。例如上游使用 H2/Mockito 时，先考虑 `java.sql` dynamic
proxy 或纯标准库 fake；只有 verifier 确实需要第三方库时，才冻结完整 closure。

每个 leaf 必须有唯一 ID、public behavior reference、输入、expected result/exception 和
`passed|failed|skipped` 状态。

**完成条件：** clean verifier environment 自动 collection，`frozen_total > 0`，实际 leaf
数与 frozen_total 一致，verifier 自己写 reward。

### Step 6：冻结 Maven offline closure

dependency contract 统一为：

```text
[dependencies].lock
[dependencies].offline_store
[dependencies].inventory
```

lock 描述精确 artifact、版本、size 和 SHA-256；offline store 保存实际 Maven repository
文件；inventory 绑定 lock/store/tree digest、toolchain、adapter version 和 offline smoke。

空闭包是合法的，但必须证明“确认无第三方依赖”，不能只是“尚未下载依赖”。禁止
floating version、未校验传递依赖、运行期下载和 `--allow-incomplete` 生产绕过。

**完成条件：** 清空 Maven cache 并关闭网络后，当前 `MavenPackageManager` 校验通过，
实际 harness 或 `mvn --offline` smoke 通过。

### Step 7：task-local staging handoff

至少保存：

```text
.nl2repo/authoring-work/<task-id>/source-freeze.json
.nl2repo/authoring-work/<task-id>/java-inventory.json
dependency-inputs/maven-lock-v1.json
dependency-inputs/offline-store.tar
dependency-inputs/maven-store.manifest.json
verifier staging
oracle/solve.sh
staging-refs.json or staging-manifest.json
provenance.md
```

未注册对象不能写成正式 `artifact://private/...` refs。推荐 worker 状态为
`inventoried/awaiting-integrator`。

**完成条件：** parent 不依赖隐式状态即可按 manifest 注册全部 bytes；worker 没有写 shared
CAS，handoff 列出未完成 gate。

## 4. Parent integration 和 controls

parent 串行执行：

1. 重算 staging bytes 的 size/SHA-256。
2. 注册 private CAS，确认返回 digest 完全一致。
3. 写正式 refs 到 `task.toml`。
4. 使用当前 toolchain 编译；production 禁用 `--allow-incomplete`。
5. 检查 closed-world manifest、runtime identity、source digest、dependency inventory、
   network policy 和 candidate/verifier isolation。
6. 构建 verifier image，执行 offline smoke。
7. 运行一次 Oracle。
8. 运行 `empty`、`stub`、`forgery`、`hang/timeout`、`install-failure`、`offline` controls。
9. 将当前 bundle digest 和所有 receipt 写入 canonical production evidence。
10. 运行 source/evidence/release/network validators 后再提交。

控制预期：

| Control | 预期 |
| --- | --- |
| Oracle | `valid=true`，collection 等于 frozen denominator，reward `>=0.80` |
| empty | 近零；仅真实 installation failure 例外可为 `0/0` |
| stub | 收集冻结分母且低分 |
| forgery | candidate 不能篡改 verifier-owned grading/reward |
| hang | bounded timeout，清理 process group |
| install-failure | 保留 `candidate-installation-failed` 和结构化 policy/category/path/message |
| offline | 完成且 `public_network_available=false` |
| network lint | error 为零，warning 有解释 |

## 5. Blocked 和 remediation

以下可以 blocked，但必须先有 bounded 尝试：

```text
revision 无法冻结
license 无法确认
完整依赖闭包仍不可重现
没有任何可执行的正数分母
native/network/database/hardware 风险无法隔离
资源预算仍超限
```

“worker worktree 没有 source/CAS”是 provisioning blocker，不是上游 task 的最终 blocker；
parent 应先预冻结输入后 reopen。上游测试需要 H2/Mockito 也不是自动 blocker，应先尝试
标准库 fake 或缩小 bounded contract。

合法 blocked evidence 必须包含：

```text
terminal_kind = blocked
failure_class = source|verifier|environment|infrastructure
真实 failure reason 和 next_step
source_freeze.status = known 或 failed + reason
commands[].command/exit_code/tool_version/log
commands[].log_sha256 与实际 bytes 一致
没有 catalog/tasks/<task-id>/ runtime
没有 Oracle/controls/reward 假声明
```

修复输入后必须重新 author、重新编译和重新生成 evidence，不得复制旧 receipt。

## 6. 必跑命令和 handoff

worker：

```bash
uv run nl2repo task validate-source catalog/sources/<task-id>
python -m py_compile <verifier-python-files>
bash -n <solution-and-control-scripts>
javac --release 21 <candidate-or-harness-sources>
git diff --check
```

parent：

```bash
uv run nl2repo harbor compile catalog/sources/<task-id> \
  --output catalog/tasks \
  --toolchain toolchain.java.lock.toml \
  --artifact-root .nl2repo/artifacts \
  --allow-private
uv run nl2repo task lint-network --include-generated
python scripts/validate_harbor_evidence.py --report <oracle-report> --kind oracle
python scripts/validate_harbor_evidence.py --report <controls-report> --kind controls
python scripts/validate_java_release.py --root . --output <release-report>
git diff --check
```

Handoff 必须列出：task id、revision、source/license digests、runtime、status、changed paths、
staged refs、frozen denominator、verifier protocol、commands/exit codes、validation、blockers
和 next step。`awaiting-integrator` 不等同于 `packaged`。

## 7. 批量 wave 和 Definition of Done

当前 Java wave 使用 **8 并行**，所有 worker 使用非 Luna 模型。每个 prompt 必须写明：

```text
Do not use Luna.
NoNetwork during agent/candidate/verifier/Oracle/controls execution.
Own exactly one task directory.
Do not write shared CAS; parent registers it serially.
Use only parent-staged immutable inputs.
```

Worker Done：source/license/API/instruction/verifier/denominator/lock-store-inventory/staging
均有证据，写入边界正确，validate-source、Java/bash checks 和 diff-check 已运行。

Parent Done：CAS refs、generated runtime、Oracle、全部 controls、offline smoke、canonical
evidence、source/evidence/release/network validators 和 digest binding 全部通过。

缺少任何 Parent Done 项，只能报告 `awaiting-integrator`、`packaged` 或 `blocked`，不能报告
完整 production task。批量统计必须动态计算 `valid`、`blocked`、`intermediate`，不能把
worker 数量当成完成题目数。
