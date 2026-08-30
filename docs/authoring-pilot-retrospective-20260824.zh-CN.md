# Package -> Harbor 出题 Pilot 复盘

> 历史复盘记录，不是当前 production 操作指南。下列 pilot 命令和结果不能绕过当前
> canonical migration 或缺失的 private staging contract。

本文记录 2026-08-24 pilot 中真实遇到的失败、修复方式和 QA 门禁，供后续
Python/Node 出题 Worker 直接执行。它不是发布报告，也不把中间失败计为 Block。

## 结论先行

`No immutable verifier image`、`没有 base-image digest`、`依赖没有 pin`、`没有
hash-locked wheelhouse`、`没有 Dockerfile/build backend` 都是 **remediation 工作**，
不是 Block 原因。Worker 必须先固定 runtime、补依赖闭包、写环境和 verifier、执行
bounded probe，再决定是否完成或留下证据充分的 excluded/blocked。

本轮已经把这条规则写入：

- `docs/authoring-agent-remediation-guide.zh-CN.md`
- `scripts/author_package_loop.py`
- `scripts/run_authoring_loop.py`
- `scripts/package_queue_loop.py`

出题 Loop 只产生 `catalog` handoff，不启动 GPT/Fable。模型运行由独立 Agent Run Loop
消费完成前置门禁的 task。

## 实际问题与修复

### Python task

| 问题 | 实际修复 |
| --- | --- |
| dataclasses-json 缺 build backend，Poetry dynamic version 在 verifier 无 Git 时失败 | 固定 `poetry-dynamic-versioning`/`poetry-core`/`dunamai` 等 build wheels，写 `POETRY_DYNAMIC_VERSIONING_BYPASS`，source directory 用受限 `--target` 安装 |
| dataclasses-json 旧 dependency wheel 覆盖 trusted pydantic/typing runtime | candidate dependencies 安装到 `/opt/candidate-dependencies/site`，trusted verifier site 不被污染；candidate site 优先于 dependency site |
| fastjsonschema 缺 Git、meta-schema 和 remote fixture | Dockerfile 安装 Git；冻结并 materialize meta-schema/localhost remote fixtures，custom JSON verifier 在 no-network 下读取只读副本 |
| pytest 参数名 `request` 是保留名 | 改为 `payload`，重新 collection |
| fastjsonschema empty candidate 对 invalid cases 假通过 | adapter error 和 schema validation failure 分离；测试遇到 adapter error 直接失败，nop reward 回到 0 |
| SymPy solve unknown symbol 没有失败 | facade 显式检查 `free_symbols`，返回 documented `ValueError` |
| SymPy verifier Docker context 引用父目录文件 | 将 lock/wheelhouse 复制到各 Docker build context；Dockerfile 只 COPY context 内文件 |
| verifier hidden files root-only 导致 pytest 无法读取 | hidden tree `0555`，trusted verifier 仍 root-owned |
| candidate install 监控遇到 build backend 临时删除 `.pyc` | `tree_usage()` 对 `scandir` 到 `stat` 的竞态 `FileNotFoundError` 做可审计忽略 |
| pydantic-settings Hatchling editable hook 缺 `editables` | 把 `editables==0.5` 加入 hash lock/wheelhouse |
| pydantic-settings host 选了 cp314 native wheel | 用 Python 3.12 ABI/platform 参数重新下载 cp312 wheel |

### Node task

| 问题 | 实际修复/策略 |
| --- | --- |
| date-fns host Node/npm 高于 production lock | 本地只做 AST/contract probe，生产必须 Node 24.19.0/npm 11.17.0 |
| globby verifier `ENOTCACHED` 缺 transitive package | 不得直接 Block；补 npm lock/cache integrity closure 后重跑 offline install |
| axios/cheerio/fast-glob 复杂 network/browser/build/filesystem boundary | 先产出 evidence；后续 Worker 必须尝试 slim JSON slice、build artifact、fixture cwd 和 adapter，不能因风险标记自动 Block |

### Harbor/旧 task 与模型运行

| 问题 | 实际修复/分类 |
| --- | --- |
| Fable `TerminalAction.command` 为空、workspace 空 | `/v1/messages` preflight HTTP 200，证实不是 BaseURL；旧 Fable run 分类为 infrastructure/provider-tool-schema，不算模型安装失败 |
| Fable 长 Python prompt 仍空 tool/content | adaptive thinking、`litellm_extra_body`、native/text tool fallback 均做 direct probe；长 prompt 组合暂记 infrastructure blocker，停止无效重试；短 Node canonicalize adaptive run 单独验证 |
| pss fixture checksum stale | 在 pinned base image 内重新计算 manifest digest，修 Dockerfile，Oracle 46/46 |
| autojump grader 硬编码 4 个 xfail，但 fixture 有 5 个 | 修 verifier fixture contract，Oracle 23/23 |
| graphneuralnetwork networkx API drift | verifier-only compatibility alias，Oracle 4/4 |
| pythonprojecttemplate candidate pyproject `addopts` 要求 pytest-cov | trusted pytest 用 `-o addopts=` 隔离 candidate config，Oracle 36/36 |
| Harbor `task_name` 带 `nl2repobench/` 前缀 | result normalizer canonicalize task ID |

## 当前通用 verifier contract

复杂 JSON、回调、生成代码和 stateful adapter 使用：

```toml
[verifier]
protocol = "custom-json-v1"
bundle = { digest = "sha256:...", uri = "artifact://private/sha256:...", visibility = "private" }
entrypoint = "run.py"
```

private bundle 只由 authorized artifact resolver materialize 到 separate verifier；
public catalog 不包含 hidden tests、adapter、remote fixtures、grader、wheelhouse 或
Oracle bytes。wrapper 固定校验：唯一 leaf IDs、leaf count、`passed|failed|skipped`、
JUnit/collection、timeout、no-network 和 verifier-owned reward。

## QA Checklist

Worker handoff 至少执行：

```bash
git rev-parse HEAD
git archive --format=tar HEAD | sha256sum
sha256sum LICENSE
python -m py_compile <verifier-and-adapter-files>
bash -n <solution-and-verifier-scripts>
uv run nl2repo task validate-source catalog/sources/<task>
uv run nl2repo harbor compile catalog/sources/<task> \
  --toolchain <locked-toolchain> \
  --artifact-root .nl2repo/artifacts \
  --authorize-task-private-artifacts
```

该命令仅记录当时的 pilot 形态；当前 source 若仍处于 pre-migration 状态，必须保持
blocked，不得据此声称 production compile 已通过。

最终 compiled bundle 中执行：

```text
Oracle once: valid=true, collected=frozen_total, reward>=0.80
nop/empty: valid=true, near-zero reward, failure_class=model
stub: low reward without verifier error
forgery: candidate reward/report cannot change trusted result
timeout/hang: bounded completion, no orphan process
offline: verifier completes with network disabled and local closure only
```

看到 `valid=false` 时先读 `exception.txt`、`trial.log`、`grading.json`、install/build
stdout/stderr；不要把 verifier/image/collection failure 写成模型 0。只有 candidate
已经真实安装/执行且行为不符合 contract，才算 model failure。

## Loop 运行纪律

- `run_authoring_loop.py` 最大并发 3，claim 使用 `package_queue_loop.py` 文件锁和 lease。
- 每个 Package 一个 detached worktree，worker 只写自己的 `catalog/sources/<id>/**`。
- claim brief 同时写入主 `.nl2repo/authoring/...` 和 worker worktree 的
  `.nl2repo/authoring-claim.json`，避免 ignored state 在 worktree 中丢失。
- Worker 不运行 GPT/Fable；integrator 串行合并 catalog/private refs/dataset/report。
- 只有 infrastructure failure 可新 run-root 重试；model failure 不静默重试。
