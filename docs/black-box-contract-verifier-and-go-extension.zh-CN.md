# NL2RepoBench 黑盒公开契约 Verifier 与 Go 扩展决策

本文总结关于 NL2RepoBench 隐藏测试、公开行为评分、AST inventory 和下一语言扩展的设计讨论。
它是一份设计决策与实施边界说明，不表示 Go adapter 已经实现，也不改变现有已发布数据集的
metric contract。

## 1. 核心结论

NL2RepoBench 测量的是：LLM/coding agent 能否只根据一份自然语言规格，从空 workspace
生成一个可安装、可运行、对外行为正确的完整代码仓库。

因此评分对象应是 **公开契约的外部可观察行为**，而不是候选实现是否复刻上游仓库的内部
函数、私有类型、文件组织、缓存结构或算法步骤。

生产 Verifier 应遵循以下原则：

1. Agent 阶段看不到隐藏测试、Oracle、grader 和 reward 生成逻辑。
2. 隐藏测试不直接 import、require 或链接 candidate 实现，而是通过受限的
   subprocess protocol、CLI 或任务专用 RPC bridge 调用它。
3. Candidate 可以看到本次公开 API 调用的输入，但看不到测试断言、预期值、其他测试用例
   和 trusted report。
4. Candidate 的崩溃、退出、超时、后台进程和伪造输出只能影响该次 candidate operation，
   不能终止 trusted test runner 或修改评分产物。
5. 每条隐藏 assertion 都必须能映射到公开 instruction 中的行为承诺；无法映射的内部实现
   测试不能进入分数。
6. 不适合黑盒适配的项目保持 `blocked`，不能为了扩大题量退回同进程 trusted test。

这意味着上游测试是 authoring truth 和行为证据的重要来源，但不是可以不经审核、整体复制的
最终评分资产。

## 2. 为什么必须按公开行为评分

同一份公开规格可能存在多个完全正确的实现：

- 函数可以拆成不同数量的 private helper；
- 数据可以保存在 list、map、tree、database 或其他内部结构中；
- 模块和文件可以采用不同但仍满足公开 import path 的组织方式；
- 可以使用不同算法，只要结果、异常、顺序、确定性和资源边界满足规格；
- 可以不实现上游只为自身维护而存在的 internal API。

如果 hidden tests 直接断言上游 private helper、内部字段或源码布局，分数测量的将是“源码
复刻程度”，而不是“从规格生成等价仓库的能力”。这种题还会系统性惩罚合理的替代实现。

公开契约并不只等于一个函数返回值。可以评分的外部表现包括：

- package 安装、module/import path、re-export 和 distribution metadata；
- public function、class、method 和 property 的参数及返回值；
- 异常类型、必要的错误信息和失败时副作用；
- CLI 参数、stdin、stdout、stderr 和 exit code；
- 文件创建、序列化格式、权限和目录副作用；
- Unicode、空输入、错误输入、边界值和顺序；
- 状态变化、幂等性、确定性和公开并发语义；
- 在固定环境、离线依赖和资源限制下的可构建、可运行性。

## 3. 必须区分的四个身份

“隐藏测试不可见”需要明确对谁不可见：

| 身份 | 能看到什么 | 不能看到什么 |
|---|---|---|
| Agent | instruction、agent image、自己的 `/workspace` | private tests、Oracle、grader、reward |
| Candidate source | Agent 最终生成的 repository | verifier private artifact |
| Candidate process | 本次调用输入、安装后的自身代码、受限临时目录 | `/tests/private`、trusted reports、预期答案 |
| Trusted verifier | private tests、command plan、candidate client、reports | 不应在自身进程加载 candidate code |

Agent 结束后，Harbor 将最终 workspace artifact 交给 separate verifier。这里传递的是 workspace
快照，不是重新从 Git remote clone；重新 clone 会丢失 Agent 未 commit 的文件和生成物。

## 4. 当前 Python Verifier

当前 Python compiler/verifier 的目标链路为：

```text
Agent image
  instruction + /workspace
          |
          | final workspace artifact
          v
Separate verifier image
  /tests/private              root-only hidden pytest
  /tmp/candidate              bounded workspace copy
  /tmp/candidate-site         isolated candidate installation
          |
          v
root pytest -> candidate_client -> UID 10001 candidate_runner -> candidate package
          |
          v
root-owned collection/JUnit -> fixed-denominator grader -> reward.json/grading.json
```

实现要点：

1. Agent environment 只设置 `/workspace`，不复制 private tests。
2. Compiler 从授权的 `tests.test_bundle` 解包测试到 verifier image 的 `/tests/private`，并将
   权限设为 root-only `0500`。
3. Verifier 使用 bounded regular-tree copier 接收 `/workspace`，拒绝 symlink、device、过长
   路径、过大文件、过多 entry 和总体积超限。
4. Candidate build/install 以 UID `10001` 执行，并安装到 `/tmp/candidate-site`；trusted pytest
   不把该目录加入自身 `sys.path`。
5. Hidden pytest 只 import `candidate_client`。每次 public API、module CLI 或 console entry
   调用都会启动一个新的低权限 `candidate_runner` 子进程。
6. Request 和 response 使用有大小限制的 JSON。这里的“RPC”是项目内的 stdin/stdout
   request-response protocol，不是网络服务，也不是 JSON-RPC 标准。
7. Candidate 子进程具有单次 timeout、累计 wall budget、内存、CPU、FD、process 和输出
   限制；结束后 verifier 清理 UID `10001` 的残留进程。
8. Collection JSON 和 JUnit 由 root pytest 写入 `/tmp/trusted-results`。Candidate 对该目录
   没有写权限。
9. Verifier 在 candidate execution 前后校验 private tests、command plan 和 runtime 的
   hash/mode snapshot。
10. Grader 逐个读取 JUnit `testcase`，检查 collection、固定分母、case 数量和 pytest exit
    code 一致性，再计算 `passed / frozen_total`。

相关实现：

- [`harbor/compiler.py`](../src/nl2repobench/harbor/compiler.py)
- [`verification/workspace_copy.py`](../src/nl2repobench/verification/workspace_copy.py)
- [`verification/candidate_install.py`](../src/nl2repobench/verification/candidate_install.py)
- [`verification/candidate_client.py`](../src/nl2repobench/verification/candidate_client.py)
- [`verification/candidate_runner.py`](../src/nl2repobench/verification/candidate_runner.py)
- [`verification/run_pytest.py`](../src/nl2repobench/verification/run_pytest.py)
- [`verification/grader.py`](../src/nl2repobench/verification/grader.py)

当前 synthetic `ministats` 已验证这条安全路径，但这不能替代真实 104 题的 source、dependency、
test provenance、Oracle 和 parity 迁移证据。

## 5. 当前 Node Verifier

Node development slice 使用相同的总体边界：

```text
/workspace
    -> bounded copy /tmp/candidate-source
    -> npm ci --offline --ignore-scripts
    -> npm pack + tar validation
    -> offline install /tmp/candidate-site

root node:test in /tests/private
    -> private test_client.mjs
    -> runuser -u candidate
    -> candidate_runner.mjs
    -> require/import candidate export
    -> JSON response
```

具体约束：

- private tests 只进入 verifier image 的 `/tests/private`，权限为 root-only `0500`；
- candidate install 默认离线并忽略 lifecycle scripts；
- `NODE_PATH`、`NODE_OPTIONS`、proxy、registry、`LD_PRELOAD` 等环境入口被清除；
- candidate runner 使用 package/export allowlist、参数数量、request/response 大小和 timeout；
- root-owned runner 逐个运行 hidden `node:test` 文件并解析 TAP leaf；
- grader 检查 leaf ID 唯一性、collection、expected total、各状态计数和 runner exit code；
- Candidate 无法写 `/logs/verifier/report.json`、`reward.json` 或 `grading.json`。

相关实现：

- [`harbor/node_compiler.py`](../src/nl2repobench/harbor/node_compiler.py)
- [`verification/node_candidate_install.py`](../src/nl2repobench/verification/node_candidate_install.py)
- [`verification/node_candidate_client.py`](../src/nl2repobench/verification/node_candidate_client.py)
- [`verification/node/candidate_runner.mjs`](../src/nl2repobench/verification/node/candidate_runner.mjs)
- [`verification/node/run_tests.mjs`](../src/nl2repobench/verification/node/run_tests.mjs)
- [`verification/node_grader.py`](../src/nl2repobench/verification/node_grader.py)

必须准确描述当前状态：Node 目前是 development/synthetic vertical slice，production compile
仍然 fail closed；它不能被描述成已经发布的 Node production dataset。

## 6. Upstream Tests 的处理规则

每条上游测试进入 hidden bundle 前必须经过分类：

| 上游测试类型 | 处理方式 | 原因 |
|---|---|---|
| 只调用 public API/CLI 并断言外部结果 | 保留断言语义，适配 candidate client | 正确测量公开契约 |
| 公开行为测试但直接 import candidate | 只改 transport，不改输入和期望 | 保持原测试强度与 subprocess boundary |
| private helper、内部字段、内部文件布局 | 排除 | 不属于公开规格 |
| 通过内部状态间接验证公开行为 | 重写为公开结果或副作用断言 | 避免实现绑定 |
| 复杂对象、callback、stream、stateful session | 增加任务级 protocol；否则 blocked | JSON 单次调用无法表达完整语义 |
| 网络、账号、当前时间、非固定随机数据 | 冻结环境或排除 | 无法离线稳定复现 |
| lint、README、拼写、内部 metadata 为主 | 不作为核心评分 | 不能代表 package 核心能力 |

适配后的每条 leaf 必须记录：

```text
upstream test evidence
  -> public symbol / CLI
  -> observable behavior
  -> instruction section
  -> adapted hidden assertion
  -> frozen leaf ID
```

只改变调用 transport 不等于可以改变断言语义。若为了适配而删除边界情况、降低精度或把
复杂状态压缩成不等价的 JSON，任务应保持 `blocked`。

## 7. AST Inventory 的正确角色

AST scanner 是 authoring 的廉价结构证据，不是行为 Oracle，也不是自动规格生成器。

它适合提取：

- package/module 树和 public symbols；
- signature、默认值、annotations/types 和 decorators；
- import/export/re-export 和 CLI entry point；
- test function、fixture、parameterization 和 public symbol references；
- dynamic execution、native extension、generated code、network/process/fs 风险；
- test-to-symbol 的静态候选边。

它不能单独证明：

- 返回值的精确内容；
- 异常、排序、Unicode 和边界行为；
- 缓存、TTL、状态、并发和副作用语义；
- 动态 dispatch 或 runtime-generated tests 的实际 leaf 集；
- instruction 是否足以让未看源码的实现者推导 hidden assertion。

因此 Pipeline 应保持：

```text
AST inventory
  -> test/source review
  -> behavior graph
  -> semantic instruction
  -> dynamic collection + Oracle
  -> bidirectional traceability review
```

这与现有 [`authoring-pipeline-ast.zh-CN.md`](authoring-pipeline-ast.zh-CN.md) 的 stage
边界一致。

## 8. 下一语言选择：Go Modules

下一门语言优先选择 Go，而不是仅按生态流行度选择。主要原因是 Go 官方工具链能够同时提供
语法、类型、package、测试和依赖事实，降低 scanner 与 runtime adapter 的不确定性。

推荐工具组合：

| 能力 | 官方组件 | 用途 |
|---|---|---|
| Syntax | [`go/parser`](https://pkg.go.dev/go/parser)、[`go/ast`](https://pkg.go.dev/go/ast)、`go/token` | 不执行源码的 AST 与位置 |
| 批量遍历 | [`x/tools/go/ast/inspector`](https://pkg.go.dev/golang.org/x/tools/go/ast/inspector) | 多文件节点过滤和父子关系 |
| Package loading | [`x/tools/go/packages`](https://pkg.go.dev/golang.org/x/tools/go/packages) | build tags、test variants、imports、Syntax、TypesInfo |
| Public API | [`go/types`](https://pkg.go.dev/go/types) | signature、generic、alias、method set、interface |
| Behavior candidates | [`x/tools/go/ssa`](https://pkg.go.dev/golang.org/x/tools/go/ssa)、[`callgraph`](https://pkg.go.dev/golang.org/x/tools/go/callgraph) | test-to-public-call 静态候选图 |
| Dynamic tests | `go test -list`、`go test -json` | 顶层测试枚举和结构化执行事件 |
| Dependencies | [`Go Modules`](https://go.dev/ref/mod) | `go.mod`、`go.sum`、vendor、verify、offline build |

`go/packages` 应作为 scanner 主入口，不能只对所有 `.go` 文件机械运行 `go/parser`。它能在
固定 `GOOS`、`GOARCH`、build tags 和 test mode 下给出实际参与 package 的文件、imports、
typed syntax 和 test variants。

Authoring scanner 必须固定 Go toolchain 和 `x/tools` 版本，并清理可能改变加载路径的环境：
`GOWORK`、`GOPACKAGESDRIVER`、proxy、toolchain auto-download 和非声明 build flags。静态阶段
不得运行 `go generate`。

## 9. Go Candidate Bridge

Go 不支持像 Python/Node 那样按字符串动态调用任意 package export，因此不能只写一个完全
通用的反射 runner。推荐根据 `go/types` inventory 为每道题生成并审核一个 typed bridge。

生产链路：

```text
Agent Go module
    -> bounded workspace ingestion
    -> validate go.mod/module path/toolchain
    -> offline build candidate + public typed bridge as UID 10001
    -> candidate bridge binary

root-owned hidden contract tests
    -> JSON/NDJSON request
    -> candidate bridge subprocess
    -> typed Go function/method call
    -> canonical JSON response
    -> trusted assertion/report/grader
```

示意协议：

```json
{"id":"1","operation":"call","package":"example.com/text","symbol":"Normalize","args":["  Hello  "]}
```

```json
{"id":"1","ok":true,"value":"hello"}
```

异常结果应使用结构化 error contract，而不是依赖整段 panic 文本：

```json
{"id":"1","ok":false,"error_type":"InvalidInput","message":"input must not be empty"}
```

Bridge source只包含公开 API mapping 和序列化逻辑，不包含 hidden input、expected value、
assertion 或 grader。Hidden tests 可以用 Go 或 Python 编写，但必须在 trusted process 中通过
bridge 调用，不得 import/link candidate package。

### 9.1 首批支持范围

首个 Go vertical slice 只接纳：

- 单一 `go.mod` module；
- 固定 Linux/amd64 和精确 Go toolchain；
- pure Go，无 cgo、plugin、专用硬件和外部服务；
- 不需要执行 `go generate`；
- 标准库依赖或完整、锁定、验证过的离线 module closure；
- CLI 或输入输出可稳定序列化的 public function；
- string、bool、明确位宽 number、slice、map、公开 struct、nullable pointer 和结构化 error；
- collection 和 leaf ID 能在三次 Oracle 中保持稳定。

首批延后：

- callback 和 reverse call；
- channel、goroutine lifecycle 和 timing-sensitive API；
- `io.Reader`/`io.Writer` 等流式对象；
- 任意 interface implementation；
- plugin、cgo、unsafe/native-heavy package；
- workspace、多 module 和 repo 外 `replace`；
- 需要不可冻结远端服务的 integration tests。

### 9.2 后续协议扩展

Stateful object 可以通过 session-scoped handle 表达：

```text
create(type, args) -> handle
call_method(handle, method, args) -> value/error
read_property(handle, name) -> value
drop(handle)
```

文件 API 使用 verifier 分配的每次调用临时目录；streaming API 使用 bounded NDJSON；callback
需要显式 reverse-RPC contract。任何扩展都必须保留 candidate process 与 private tests 的
权限和进程边界。

## 10. Go Test Collection 与固定分母

`go test -list` 只列顶层 test、benchmark、fuzz target 和 example，不列 `t.Run` subtest。
因此不能看到 `-json` 就假设固定分母问题已经解决。

建议首版 metric contract：

1. 不把 benchmark 当评分 leaf。
2. 默认以 verifier-owned contract test leaf 为固定分母，而不是直接采用 upstream `_test.go`
   的所有 leaf。
3. 若保留动态 subtest，只接受三次 Oracle 中完整 leaf ID 集、顺序无关集合和状态均稳定的题。
4. Missing leaf、duplicate leaf、collection error、report/exit mismatch 必须结构化处理。
5. Candidate build failure 是有效的 model zero；trusted runner/report failure 是 verifier invalid。
6. Reward 仍为 `clamp(passed / frozen_total, 0, 1)`，dataset 仍按逐题宏平均。

## 11. 为什么不直接把 Hidden Tests 放进 Candidate Repository

讨论过的简化方案是：Agent 结束后复制最终 repository，把上游 `_test.go` 放进同一目录，直接
运行 `go test`。

它的优点是实现快、几乎不用改上游测试，并天然支持复杂 Go 类型、callback 和 package 内状态。
但它不适合作为当前 production contract：

1. 上游 suite 往往包含 private helper、unexported field 和内部 package 测试，会错误惩罚
   与规格等价但结构不同的实现。
2. Candidate 与 hidden tests 被链接进同一个 test binary；candidate `init`、`os.Exit`、panic、
   hang、background process 或 unsafe 行为可以影响 trusted test runner。
3. Candidate 自带的 `_test.go`、`TestMain`、同名 test 和 build tags 可能改变 collection。
4. Hidden assertions 和 expected constants 会进入与 candidate 同进程的 binary，不能维持当前
   “candidate 看不到 private tests”的强边界。
5. Report 和 individual leaf event 更容易被同进程 candidate 干扰。

直接运行原始 upstream suite 仍然有价值，但应限于：

- source freeze 和 Ground Truth baseline；
- 发现行为、风险、测试覆盖和 Oracle ceiling；
- 对 adapted contract tests 做 assertion-parity review；
- 非生产的诊断实验。

它不能直接替代 published task 的 subprocess verifier。若未来决定提供 direct-test lane，必须
使用新的 verifier profile 和 dataset/version，明确 `candidate_execution=in-process`，并与当前
hardened lane 分开报告。

## 12. Go Adapter 的实施顺序

按照现有 [`runtime-adapter-architecture.zh-CN.md`](runtime-adapter-architecture.zh-CN.md)，
新增 Go 不应复制顶层 schema、compiler 或 grader：

1. 在 unified domain contract 中增加 `language=go` 和 `package_manager=go-modules`。
2. 建立独立、锁定的 Go authoring tool，输出现有 `ApiInventory`/`BehaviorMap` 核心形状。
3. 实现 Go Modules lock/offline closure validator，固定 toolchain、module cache/vendor 和 hash。
4. 实现 typed bridge IR、代码生成器和只含公开 mapping 的 candidate runner。
5. 实现 Go subprocess supervisor：UID、timeout、CPU、memory、process、FD、output、temp storage
   和残留进程清理。
6. 实现 verifier-owned contract test runner 与统一 `LeafReport` normalizer。
7. 扩展 generic Harbor compiler registry，不创建 Go 专用 dataset/compiler schema 分叉。
8. 用一个 synthetic fixture 跑通 compile、install、call、report 和 fixed denominator。
9. 用一个真实 public-API package 完成 Oracle 三次和全控制矩阵。
10. 通过后进入 5 到 10 题 pilot，再决定是否批量 author 10 到 20 题。

## 13. Go Vertical Slice 门禁

一题只有同时满足以下条件，才可从 Go candidate 进入 published dataset：

- exact source revision、license、source digest 和 Go toolchain 完整；
- `go.mod`/`go.sum` 与离线 closure 一致，Verifier 断网仍能构建；
- scanner 对 build tags、public API、test variants 和 dynamic/native risk 有明确记录；
- 每条 hidden assertion 都映射到 instruction 中的公开行为；
- bridge 不包含 hidden data，并在 candidate UID 下独立构建和运行；
- trusted tests 不 import/link candidate，candidate 无法读取 private tests 和 reports；
- frozen leaf collection 与 expected total 一致；
- Oracle 三次均 `valid=true`、collection 稳定、reward 不低于 `0.80`；
- empty、stub、forgery、early-exit、panic、hang、background-process、oversized-output 和 offline
  controls 通过；
- blind review 证明不同内部实现仍可从 instruction 推导并通过测试；
- task version、content hash、tool versions、reports 和 artifacts 可追踪。

## 14. 已决定与尚未决定

已经决定：

- 评分应面向公开行为，而不是上游内部结构；
- hidden tests 与 candidate 应保持进程和权限隔离；
- upstream tests 需要 contract-level 筛选和 transport adaptation；
- AST 负责 inventory/traceability，不负责证明语义；
- 下一语言优先探索 Go Modules；
- Go production path 使用 typed subprocess bridge，不直接链接 hidden tests；
- 首批只覆盖 CLI 和可序列化 public API。

仍需通过 vertical slice 决定：

- Go bridge 的 canonical type encoding 和 error taxonomy；
- hidden contract tests 使用 Go runner 还是复用 Python trusted runner；
- module cache 与 vendor artifact 的最终 offline closure 形式；
- stable subtest leaf 的具体冻结规则；
- stateful handle protocol 是否进入首个 pilot 后的第二阶段；
- Go lane 是否与 Python/Node 使用完全相同的 metric contract ID，还是先发布独立 contract。

这些问题不能只靠设计文档关闭；最终结论必须来自 synthetic fixture、真实 package、Oracle
三次、负向控制和多模型 pilot 的实际 artifact。
