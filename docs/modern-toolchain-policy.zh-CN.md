# Modern Toolchain Policy

目标不是为了追新工具而改变 benchmark 语义，而是让高规模 authoring、Harbor 运行和
结果分析在可复现前提下使用现代、高吞吐、可维护的工具链。

## 当前选择

| 工作 | 当前工具 | 原则 |
|---|---|---|
| Python 环境/依赖 | `uv` + frozen lock | 安装和 build 不使用未锁定 pip 命令 |
| Python 静态扫描 | stdlib `ast` | 不 import/执行 candidate |
| Node/TS 静态扫描 | pinned TypeScript compiler API | 不 import/执行 candidate |
| 表格/批量 metadata | Polars | lazy/dataframe/Parquet 优先，不引入 pandas |
| 结构化模型 | Pydantic | 边界校验和 schema 生成 |
| canonical JSON | stdlib JSON + canonical serializer | 不用快速 JSON 库改变字节、排序或 digest |
| Harbor 并发 | bounded Harbor/queue concurrency | 受 provider、Docker、磁盘和 cleanup gate 约束 |
| 代码质量 | Ruff + mypy + pytest | 每个 stage/adapter 都有小而确定的测试 |
| Node authoring tool | locked npm package + TypeScript | 不把 scanner 依赖带进 candidate/verifier image |

当前核心代码没有 pandas runtime dependency；已有 legacy difficulty/import path 使用
Polars。仓库中出现的 pandas 文本主要是历史任务 instruction 或候选项目描述，不能
为了搜索结果而改写上游题目内容。

## Polars 使用边界

### 适合 Polars 的场景

- 批量 discovery manifest、AST inventory、stage result 和 benchmark result 汇总；
- 分组、去重、join、宏平均、failure taxonomy 和 Parquet 输出；
- 大量 JSON/CSV/NDJSON 的 lazy scan 和列式过滤；
- 需要按 task/model/attempt 聚合但不改变原始 artifact 的只读分析。

当前高吞吐结果入口：

```bash
python3 scripts/summarize_benchmark_runs.py \
  --runs-dir .nl2repo/runs/bench-a \
  --runs-dir .nl2repo/runs/bench-b \
  --output /tmp/benchmark-summary.json \
  --parquet /tmp/benchmark-trials.parquet
```

该命令只读取 trial `result.json` 和 verifier `grading.json`，并按 valid task 的 task
score 做宏平均；不会把 raw test case 数量作为跨题权重，也不会修改原始结果。

300+ Benchmark 的 task 集合使用单独的 published manifest gate：

```bash
python3 scripts/build_published_benchmark_manifest.py \
  --dataset-release 1.0.0 \
  --output .nl2repo/datasets/nl2repobench-harbor-300/manifest.json \
  --parquet .nl2repo/datasets/nl2repobench-harbor-300/tasks.parquet
```

任务数量不足 300 时默认失败；不能用 candidate/audit/blocked 目录补齐数量。

### 不适合强行使用 Polars 的场景

- 单个小 JSON control record 的严格 schema 校验；
- canonical manifest、artifact ref 和 reward JSON 的字节身份；
- candidate subprocess 的一行 JSON request/response；
- 需要保留精确字符串、对象顺序或错误位置的 verifier protocol。

这些边界继续使用 stdlib JSON/Pydantic/canonical serializer，避免因为“更快”的序列化
库改变 digest、字段顺序或安全校验。

## 禁止的替换方式

- 不把 pandas 当作 candidate runtime 的隐含 dependency；若上游任务本身测试 pandas，
  它属于任务冻结环境，不属于 NL2RepoBench authoring core；
- 不用 `pl.DataFrame.to_dicts()` 取代所有结构化模型校验；Polars 输出进入 domain model
  前仍要经过显式 schema/类型验证；
- 不用 `orjson/ujson` 替换 canonical JSON，除非有字节级 golden 和 release 迁移；
- 不把 NumPy/Pandas/Arrow 对象直接跨 candidate subprocess boundary；必须使用 JSON、
  Arrow IPC 或明确的 tagged binary contract，并记录 adapter；
- 不为提高吞吐而取消 fixed denominator、private asset isolation、Oracle/control 或
  failure classification。

## 并发和资源管理

现代工具链的吞吐提升来自分层，而不是盲目增加 Docker 数量：

```text
AST/discovery       8–16 workers
environment probes   4–8 workers
Harbor package       4–8 workers
Oracle/control       2–4 workers initially
model trials         2–4 initially, max 8 with evidence
```

每层都有独立 run root、lock、cleanup log 和资源检查。任何 orphan container、未完成
`finished_at`、`valid=false` 未分类或 `/tmp` 低于安全阈值，都会暂停扩容。详见
[`harbor-runner-cleanup-and-concurrency.zh-CN.md`](harbor-runner-cleanup-and-concurrency.zh-CN.md)。

## 依赖和 release 规则

1. core Python dependency 必须进入 root `pyproject.toml` 和 `uv.lock`；
2. Node authoring tool 必须有自己的 `package.json`/`package-lock.json`，不进入 candidate；
3. 数据分析输出优先 Parquet，摘要 JSON 只保存 schema 化的汇总；
4. 工具链升级要跑 schema/golden/full tests，并产生新的 toolchain/release evidence；
5. 任何工具升级不能静默改变 frozen test denominator 或历史 score；
6. 新语言 adapter 复用这些基础设施，不复制 pandas-style per-language data stack。
