# Metadata Core 使用说明

本文是 Phase 1 metadata core 的开发和维护说明。它解释当前代码已经实现的边界，不把路线图中尚未实现的 Harbor compiler、authoring DAG 或 verifier 功能写成现状。

## 依赖与运行

项目使用 `uv` 管理依赖：

```bash
uv sync
uv run pytest
uv run ruff check .
uv run nl2repo doctor
uv run nl2repo schema export
```

现代 core 的依赖来源只有根目录 `pyproject.toml` 和提交的 `uv.lock`。旧
OpenHands 0.56/Docker runner 及其独立 legacy 环境已经删除；历史依赖身份只保存在 archive
和 Git history 中。根目录 `openhands/` 是当前 pinned SDK fork submodule。

核心技术选择：

- `uv`：环境创建、锁定、同步和命令执行；
- Pydantic v2：严格 domain model、JSON Schema 导出和迁移边界；
- Polars：difficulty CSV、metadata gap report 和后续批量统计；
- Typer：类型驱动 CLI 和自动帮助；
- SQLite WAL：第一阶段的 durable state/index，不把 artifact bytes 放入数据库；
- 文件系统内容寻址存储：`sha256/<prefix>/<digest>`，未来可替换为对象存储。

## Canonical record

`TaskManifest` 是单题的 canonical record，当前包含：

- `TaskMetadata`：difficulty、category、tags、language；
- `ArtifactRef`：digest、size、media type、URI、visibility；
- `SourceLock`：上游 revision、license 和源码 digest；
- `EnvironmentLock`：Python、OS、基础镜像 digest、网络模式；
- `DependencyBundle`：离线依赖闭包 artifact；
- `TestManifest`：冻结测试分母和测试 bundle/私有命令 refs；
- `MetricContract`：固定分母评分语义；
- `TaskLifecycleRecord`：状态、owner、reason、evidence 和审批 refs；
- `HarborExecutionProfile`：description、keywords、timeout、network 和资源；
- `oracle_bundle`：private reference solution tar；
- `LegacyProjection`：历史四文件的输入路径，仅用于追溯。

## Human-facing Declarative Catalog

日常出题不直接编辑 `test_files/`，而是在 catalog 中编辑 TOML/Markdown：

```text
catalog/
├── datasets/<dataset-id>/dataset.toml
└── tasks/<task-id>/
    ├── task.toml
    └── instruction.md
```

Human 负责表达目标、行为契约、来源声明、环境约束、测试分母和审核状态；工具负责生成 digest、canonical JSON、artifact ref、SQLite index 和后续 Harbor bundle。

最小 `task.toml`：

```toml
schema_version = "1.0"
task_id = "example"
version = "1.0.0"
instruction = "instruction.md"

[metadata]
difficulty = "medium"
category = "utility-library"
tags = ["python"]
language = "python"

[source]
status = "known"
upstream_url = "https://github.com/example/project"
revision = "0123456789abcdef0123456789abcdef01234567"
license_spdx = "MIT"

[environment]
status = "known"
python_version = "3.12"
os_name = "debian-12"
base_image = "registry.example/project-verifier"
base_image_digest = "sha256:..."
network_mode = "no-network"

[tests]
expected_total = 120
expected_total_source = "frozen-collection"
test_bundle = { digest = "sha256:...", size_bytes = 1234, uri = "artifact://private/sha256:...", visibility = "private" }
commands_artifact = { digest = "sha256:...", size_bytes = 128, uri = "artifact://private/sha256:...", visibility = "private" }
```

生产题的 hidden tests、Oracle 和命令不应以内嵌字符串提交到公开 catalog；使用 private artifact ref。`status = "unknown"` 适合迁移初期，但不能通过发布门禁。`expected_total_source = "legacy-file"` 只允许出现在迁移结果，不代表冻结 collection。

声明式命令：

```bash
uv run nl2repo task scaffold my-task --root catalog/sources
uv run nl2repo task validate-source catalog/sources/my-task
uv run nl2repo task compile catalog/sources/my-task --output build/catalog
uv run nl2repo dataset compile catalog/datasets/my-dataset/dataset.toml --output build/catalog
uv run nl2repo dataset validate build/catalog
```

Dataset 的 `tasks` 字段只写稳定 task ID。编译器从 dataset 所在 catalog root 的 `tasks/` 目录解析它，避免 Human 在 TOML 中维护脆弱的相对路径。

所有记录都有 `schema_version`。`content_digest()` 对不包含自引用 hash 的 canonical JSON 计算 SHA-256：排序 key、紧凑分隔符、UTF-8、去除 `None`。因此同一输入的导入结果可以做 byte-level diff 和缓存 key。

`uv run nl2repo schema export` 将 canonical manifest、declarative source 和 gap report 的 JSON Schema 写入 `schemas/v1/`。这些文件供 CI、编辑器和非 Python 工具使用；Pydantic model 是生成源，CI 应拒绝生成结果发生未提交 drift。

JSON Schema 表达 known provenance、environment、dependency、test command source 和 lifecycle 的标准条件约束。复杂的跨记录 publication predicate 仍由 Pydantic runtime validator 执行；每个 schema 都带 `x-nl2repobench-runtime-validation = true` 和 model 名称，外部工具不能把仅通过结构 schema 等同于可发布。canonical task 使用 `nl2repo task validate`，declarative task 使用 `nl2repo task validate-source`，compiled dataset 使用 `nl2repo dataset validate`。

## Unknown 与 private

legacy 四文件不能证明上游 URL、完整 commit、license、base image digest 或冻结 collection。Importer 将这些字段标记为 `unknown`，不根据 `start.md` 猜测；发布 validator 后续必须拒绝仍为 unknown 的 required field。

`start.md` 是公开 instruction，作为 public artifact 保存。`test_commands.json` 和 `test_files.json` 可能暴露 verifier 细节，作为 private artifact 保存；manifest 只保存 opaque ref、digest、size 和 visibility。当前 `LocalArtifactResolver` 默认拒绝 private ref，只有显式 `allow_private=True` 才能物化。

## 导入 104 道 legacy 题

```bash
uv run nl2repo task import-legacy \
  --legacy-root test_files \
  --output authoring \
  --artifact-root .nl2repo/artifacts \
  --state-db .nl2repo/state.db \
  --difficulty-file test_files/task_difficulty.csv \
  --report .nl2repo/metadata-gap-report.json
```

导入过程：

1. 按 task ID 排序读取四个 legacy 文件；
2. 严格验证测试数量、命令列表和 protected paths；
3. 以原始 bytes 写入内容寻址 artifact store；
4. 生成 `authoring/<task-id>/manifest.json`；
5. 以 SQLite upsert 记录 task/version/status/digest；
6. 用 Polars 聚合缺失字段，写出 gap report；
7. 生成 `authoring/dataset.manifest.json`。

Importer 是幂等的：相同文件内容得到相同 artifact 和 manifest digest。它不会自动把 task 推进到 `frozen` 或 `published`；导入后的状态仍是 `discovered`，需要后续 freeze、inventory、review 和控制阶段。

迁移完成后，新的 task 只允许从 declarative catalog 编译；`import-legacy` 仅用于一次性 backfill 和历史复现。生成的 `authoring/` JSON 是机器索引，不是 Human 的编辑入口。

当前 104 题的首次基线位于 [`reports/legacy-metadata-gap.v1.md`](../reports/legacy-metadata-gap.v1.md)，逐题机器记录位于同目录 JSON。报告确认 104 题都缺失 source revision/license、环境 digest、离线依赖闭包、test bundle provenance 和冻结 collection 证据，因此不能直接标记为 production-publishable。

验证导入结果：

```bash
uv run nl2repo dataset validate authoring
uv run nl2repo task validate authoring/aiofiles/manifest.json
uv run nl2repo task show authoring/aiofiles/manifest.json
```

## 维护规则

- 修改 model 字段时提升 `schema_version`，添加 migration 和 golden fixture；
- 不在 model 中加入当前阶段无法稳定获得的猜测值；
- 不把 private bytes、API key 或完整 shell secret 写进 manifest；
- 不让 CLI 直接修改共享 dataset index 之外的 task 状态；
- 不把 generated `manifest.json` 当作 Human source；修改必须回到 `task.toml` 或 `instruction.md`；
- 不在 `task.toml` 中写 mutable Git branch、`latest` image tag 或无法校验的 digest；
- 任何新 stage 都要记录 input/output hash、tool version、owner、retry policy 和日志；
- 生成物的 canonical JSON 必须经过 parser 校验和 `git diff --check`；
- 新功能先写 domain/storage 单元测试，再接 CLI；
- Harbor task compiler 尚未接入前，不要手工声称 `manifest -> Harbor` 已经可用。
