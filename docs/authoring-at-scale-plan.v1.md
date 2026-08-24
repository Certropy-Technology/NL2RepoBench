# Python 与 Node/npm 批量出题计划

> **Historical plan — superseded.** 当前批量出题请使用
> [`authoring-pipeline-ast.zh-CN.md`](authoring-pipeline-ast.zh-CN.md)。本文保留旧批次的
> 候选、门禁和结果背景，不再定义新的 AST、runtime adapter 或批量调度流程。

本文定义下一阶段更高规模出题的可执行边界。Python 和 Node 是两个独立
dataset/version；它们共享编排原则，但不共享 schema、grader、依赖闭包或分数。

## 目标与不变量

每批先做 5--10 题 pilot，稳定后扩大到 10--20 题。每题必须有 immutable source
lock、license、image/runtime lock、offline dependency closure、public instruction、
private tests/commands/Oracle refs、automatic collection、Oracle、controls、review、
pilot 和 content manifest。不能证明的题进入 `blocked`，不能降低标准后发布。

## 共用流水线

```text
discover -> freeze-source -> ground-truth-image -> collect-tests
         -> API-inventory -> draft-spec -> traceability
         -> private-artifacts -> compile -> Oracle x3 -> controls
         -> blind-review -> pilot -> publish
```

每个 stage 只消费上一个 stage 的 immutable artifact。writer 一题一 worktree；
integrator 是唯一能写 dataset、canonical index、shared scripts 和总报告的角色。

## Python lane

### 候选顺序

优先使用 `reports/github-package-candidates.v1.json` 中 API 纯、外部服务少、
容易 JSON 化的候选：

```text
validators       validation API，当前已有 blocked audit
parsy            parser combinator，已有历史 blocked source
python-constraint medium solver ordering
simple-parsing   typed CLI，当前 blocked，需重做 pytest config proof
SALib            scientific analysis，当前 blocked，需锁依赖/随机性
lark             hard parser，多 backend，后置
coxeter          hard geometry，浮点/SciPy 风险高，后置
```

Spark、浏览器、付费服务、GPU、live financial API、未冻结数据集和大量 native
extension 默认延后或 blocked。

### Python 冻结门禁

1. detached checkout 固定 full SHA，保存 archive 和 LICENSE hashes；
2. 在最终 Python/OS/image 中执行 collection 和完整 suite；
3. build/runtime/test requirements 进入带 hash 的 lock；Python verifier 在 Docker build
   阶段联网安装，禁止 vendor wheelhouse；
4. pytest config、xfail/xpass/skip 语义进入 metric contract；
5. callable、async、stateful、CLI、numpy/pandas 对象使用 child-side adapter；
6. 先 Oracle，再 controls，再 blind/spec review。

## Node/npm lane

### 首批候选

优先使用 `reports/npm-package-candidates.v1.md`：

```text
jsonc-parser       Node test/ESM，需处理旧 integrity closure
canonicalize       ESM/JSON，当前 development-only specified
query-string       JSON-only parse/stringify scope
qs                 CommonJS/TAP，排除 network posttest audit
validator          CommonJS，无 runtime deps，需 pin build toolchain
stringify-object   Node test/ESM，JSON-only values/options
```

Node task 不能混进 Python dataset。使用 Node 22.23.1/npm 10.9.8、lockfile v3、
`npm ci --offline --ignore-scripts` 和 `node-test-json-v1`。

### Node 生产门禁

- agent/verifier base image digest-pinned，`linux/amd64`；
- lockfile 每个 package 有完整 integrity，拒绝 git/file/workspace/link/native addon；
- npm cache/tarball closure 使用 private artifact ref；
- hidden tests 只能通过固定 JSON subprocess boundary 调用 candidate；
- lifecycle/build scripts 默认禁用；
- test report leaf IDs 唯一，collection 与 frozen total 一致；
- Oracle 3x、nop、partial/stub、install-failure、hang、forgery、offline 全部保留。

`node-synthetic` 已证明 development vertical slice：Oracle 3/3 reward 1.0、8/8
collection；toolchain 仍 development-only，不能作为 production artifact。

## 并发与资源

不同 task 可并行；同一 task 的 source freeze、spec、tests、verifier 不并行。
建议起步配置：

| Lane | 并发 | 约束 |
| --- | ---: | --- |
| discovery/research | 8--16 | 只读，不写共享目录 |
| task-local authoring | 5--10 | 独立 worktree |
| Docker Oracle/control | 1--3 | 受内存、image build、磁盘限制 |
| shared integration | 1 | 只允许一个 writer |
| model runs | 每 model 1 serial queue | 新 root、infra-only retry |
| OSS upload | 4--8 workers | 先 manifest/hash/collision，再上传 |

## Writer handoff

每个 writer 返回 task/lane/worktree、changed files、source/archive/license hashes、
collection command/count、dependency/image evidence、candidate boundary、静态命令与
exit codes、complete/blocked recommendation、open risks 和 unblock action。

Writer 禁止修改 conversion state、共享 dataset、reports index 或其他 task；禁止提交
hidden tests、binary fixtures、Oracle bytes、credentials；禁止把网络安装成功当成
offline closure；禁止用 `--allow-incomplete` 声称 production-ready。

## Integrator gates

```bash
git diff --check
uv run pytest -q
uv run ruff check src tests scripts
uv run mypy src/nl2repobench
uv run nl2repo task validate-source catalog/sources/<task>
git status --short --branch
```

JSON/TOML/YAML 必须用解析器校验。每题完成后立即 commit/push，并 fast-forward
`/data/NL2RepoBench-current`；不等整批结束。

## 批次模板

```text
batch id: python-pilot-<UTC> / node-pilot-<UTC>
dataset/version: separate and immutable
candidate count: 5--10
models: none during authoring; Oracle first
concurrency: declared CPU/memory bound
stop: any systematic spec/environment/verifier issue
artifacts: source/image/dependency/collection/Oracle/controls/review manifests
```

只有 pilot 没有系统性 spec/environment/verifier 问题，才扩大下一批。
