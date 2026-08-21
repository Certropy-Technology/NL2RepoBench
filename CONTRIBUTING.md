# Contributing to NL2RepoBench

本文档介绍如何为 NL2RepoBench 创建新题目、运行 benchmark、分析结果，以及如何将数据归档到 OSS。

## 目录

- [创建新题目（Task Authoring）](#创建新题目task-authoring)
- [运行 Benchmark](#运行-benchmark)
- [分析结果](#分析结果)
- [OSS 数据归档](#oss-数据归档)
- [注意事项](#注意事项)

## 创建新题目（Task Authoring）

### 完整流程

遵循 `AGENTS.md` 和 `docs/task-authoring-guide.zh-CN.md` 记录的状态机：

```text
discovered → frozen → inventoried → specified → packaged
  → oracle-passed → controls-passed → reviewed → piloted → published
```

每个状态有明确的通过条件和产物要求。

### 快速开始：从 legacy 镜像转换

如果候选任务已有 Docker 镜像（位于 `ghcr.io/multimodal-art-projection/nl2repobench/<task>:1.0`），使用转换脚本：

```bash
# 1. 更新 scripts/gen_harbor_from_legacy.py
# - IMAGE_DIGESTS：添加 <task> -> 镜像 sha256（不带 "sha256:" 前缀）
# - TASKS：添加 <task> 配置（paths、pytest、expected，
#   可选 image / docker_prepare / prepare）

# 2. 拉取镜像
docker pull ghcr.io/multimodal-art-projection/nl2repobench/<task>:1.0

# 3. 生成 Harbor 结构
python3 scripts/gen_harbor_from_legacy.py

# 4. 解析上游 commit
# 使用 git blob 匹配找到与镜像测试文件完全一致的上游 revision
git clone <upstream-url> /tmp/<task>-source
cd /tmp/<task>-source
# 对比镜像内测试文件与 git 历史中的 blob hash

# 5. 转换为 catalog 任务（task_id 是位置参数）
python scripts/convert_testfiles_to_harbor.py <task> \
  --upstream-url <url> \
  --upstream-revision <full-sha> \
  --python-version <X.Y> \
  --source-digest sha256:$(cd /tmp/<task>-source && git archive <sha> | sha256sum | cut -d' ' -f1)

# 6. 验证 catalog source
uv run nl2repo task validate-source catalog/tasks/<task>
```

生成的结构：

```text
catalog/tasks/<task>/
├── task.toml                          # catalog 元数据
├── instruction.md                     # 公开规格（agent 唯一输入）
└── harbor/
    ├── task.toml                      # Harbor 任务定义
    ├── instruction.md -> ../instruction.md
    ├── environment/Dockerfile         # agent 容器
    ├── solution/solve.sh              # Oracle 脚本
    └── tests/
        ├── Dockerfile                 # verifier 容器
        ├── test.sh                    # 测试入口
        ├── grade.py                   # 判分脚本
        └── <hidden test files>        # 冻结的上游测试
```

### Oracle 门禁

**Oracle 必须三次独立运行为 1.0**，才能加入 active dataset：

```bash
cd harbor-runner
for i in 1 2 3; do
  uv run --frozen harbor run \
    -p ../catalog/tasks/<task>/harbor \
    -a oracle \
    --jobs-dir ../.nl2repo/runs/oracle-<task>-gate-$i
done

# 检查每次的 grading.json
find ../.nl2repo/runs/oracle-<task>-gate-* -name grading.json -exec jq '.reward,.valid' {} \;
```

`grading.json` 格式：

```json
{
  "reward": 1.0,
  "valid": true,
  "passed": 336,
  "expected": 336,
  "collected": 336,
  "skipped": 0,
  "reason": null
}
```

`valid: false` 表示题目/环境问题，不是模型分数：

| `reason` | 含义 | 处理 |
|---|---|---|
| `collection-mismatch` | collected − skipped ≠ expected | 检查环境、依赖或上游版本 |
| `junit-missing` | 测试未产出 JUnit | 检查 verifier 日志 |
| `installation-failed` | 候选包安装失败 | 检查 solve.sh 和依赖 |
| `pytest-abnormal-exit` | pytest 崩溃 | verifier 或基础设施问题 |

### 负向控制

Oracle 通过后，运行控制实验验证 verifier 可靠性：

1. **empty** — 空 workspace → 期望接近 0
2. **stub** — packaging + 空函数实现 → 期望低分
3. **forgery** — 伪造 grading.json/reward.json → verifier 不应被篡改
4. **offline** — 断网运行 → verifier 完成判分

### 添加到 dataset

全部门禁通过后：

```bash
# 编辑 catalog/datasets/nl2repobench-harbor-pilot/dataset.toml
# 在 tasks 数组中按字母序添加新任务 id

uv run nl2repo dataset compile \
  catalog/datasets/nl2repobench-harbor-pilot/dataset.toml \
  --output build/catalog/nl2repobench-harbor-pilot

# 输出应显示 task_count 与 tasks 数组长度一致
```

### Blocked 候选

无法通过 Oracle 或控制的候选记录在 `catalog/datasets/nl2repobench-harbor-pilot/blocked.md`：

```markdown
## <task-id>

**Reason**: <collection-mismatch | version-drift | flaky | timeout>

**Evidence**:
- Oracle run 1: reward=0.98, passed=181/209
- Oracle run 2: reward=0.86, passed=179/209
- Root cause: 30 CLI tests fail due to upstream version drift
```

不要把 blocked 候选放进 `tasks` 数组。`dataset.toml` 的 schema 不接受额外字段，
blocked 说明必须写在 `blocked.md`，否则 `dataset compile` 会失败。

## 运行 Benchmark

### 单任务测试

推荐用封装好的脚本（它会使用 file-backed adapter，避免长 instruction 触发
宿主 `ARG_MAX`）：

```bash
TASK_ID=ftfy \
MODEL=openai/gpt-5.6-sol \
LLM_BASE_URL=https://your-endpoint/v1 \
LLM_API_KEY="$YOUR_KEY" \
TIMEOUT_SECONDS=3600 \
REASONING_EFFORT=max \
RUN_ROOT=.nl2repo/runs/test-ftfy \
scripts/run_harbor_model.sh
```

直接调 Harbor（仅适合短 instruction 的调试场景）：

```bash
cd harbor-runner
uv run --frozen harbor run \
  -p ../catalog/tasks/ftfy/harbor \
  -a oracle \
  --jobs-dir ../.nl2repo/runs/test-ftfy
```

### 批量运行

`scripts/run_model_queue.sh` 是**串行** worker，并用 `flock` 保证同一模型不会
重复跑同一道题：

```bash
TASKS='ftfy,cerberus,aiofiles' \
MODEL='openai/gpt-5.6-sol' \
LLM_BASE_URL=https://your-endpoint/v1 \
LLM_API_KEY="$YOUR_KEY" \
RUN_ROOT=.nl2repo/runs/batch-gpt \
RUN_PREFIX=gpt56 \
scripts/run_model_queue.sh > .nl2repo/runs/batch-gpt.log 2>&1 &

# 监控进度
tail -f .nl2repo/runs/batch-gpt/queue.log
```

要同时评测两个模型，就启两条队列并给**不同的** `RUN_ROOT`；每条仍是串行，
峰值 Docker 负载为两个 agent 容器。

### 关键参数

| 参数 | 说明 | 推荐值 |
|---|---|---|
| `TIMEOUT_SECONDS` | Agent 外层超时（秒） | 3600 |
| `REASONING_EFFORT` | 透传给 SDK 的推理强度 | max |
| `MAX_RETRIES` | Harbor 重试（**仅** infra 错误） | 3 |
| `LLM_NUM_RETRIES` | SDK 内部 LLM 重试 | 10 |
| `LLM_TIMEOUT` | 单次 LLM 调用超时（秒） | 600 |
| 队列并发 | 每模型一条串行 worker | 1（脚本内置） |

只有被分类为基础设施的错误（rate limit、网关 5xx、overload、中途断流）会重试；
模型失败是终态，不会被重试静默救回。

### 输出结构

```text
.nl2repo/runs/<run-id>/
├── config.json              # 任务配置（API key 已脱敏）
├── result.json              # 运行结果
├── job.log                  # 队列日志
└── harbor__<id>/
    ├── agent/
    │   ├── openhands_sdk.txt       # agent 完整日志
    │   ├── trajectory.json         # 轨迹
    │   └── instruction.md          # 投喂的规格
    ├── verifier/
    │   ├── grading.json            # 判分结果（权威）
    │   ├── reward.json
    │   ├── junit.xml
    │   └── pytest-stdout.txt
    ├── artifacts/              # agent 产出的 workspace
    ├── lock.json
    └── trial.log
```

## 分析结果

### 计算宏平均

**必须逐题宏平均，不能汇总 passed 后再除以总测试数**：

```bash
# 收集所有 grading.json
find .nl2repo/runs -name grading.json > /tmp/gradings.txt

# 计算
python3 << 'PY'
import json
from pathlib import Path

scores, invalid, legacy = [], 0, 0
for line in open('/tmp/gradings.txt'):
    g = json.loads(Path(line.strip()).read_text())
    if 'valid' not in g:
        # 早期 grader 未写 valid 字段，口径不同，不能混入当前统计
        legacy += 1
    elif g['valid']:
        scores.append(g['reward'])
    else:
        invalid += 1

print(f'valid tasks : {len(scores)}')
print(f'invalid     : {invalid}   (题目/环境问题，不算模型分)')
print(f'legacy skip : {legacy}   (无 valid 字段的旧格式)')
if scores:
    print(f'macro avg   : {sum(scores)/len(scores):.4f}')
    print(f'min/max     : {min(scores):.4f} / {max(scores):.4f}')
PY
```

注意：早期运行的 `grading.json` 可能没有 `valid` 字段（当时 grader 版本不同）。
这些结果的判定口径与当前不一致，**应当单独统计**，不能混进当前数据集的
宏平均；需要比较时应用现行 verifier 重跑。

### 失败分类

```bash
# 统计 valid=false 的原因
find .nl2repo/runs -name grading.json \
  -exec jq -r 'select(.valid==false) | .reason' {} \; | sort | uniq -c
```

实际输出示例：

```text
     31 collection-mismatch
      2 installation-failed
     10 junit-missing
```

### Token 与成本

agent 日志末尾会记录累计 token，格式为：

```text
Tokens: ↑ input (total 123.4K) • cache hit (total 45.6K) • ↓ output (total 7.8K) • $ 1.23
```

取每次 trial 的最后一行统计：

```bash
# 列出每次 trial 的 token 行
find .nl2repo/runs -name openhands_sdk.txt | while read f; do
  line=$(grep -a 'Tokens:' "$f" | tail -1)
  [ -n "$line" ] && printf '%s\n  %s\n' "$f" "$line"
done | head -20
```

注意：`openhands_sdk.txt` 包含 ANSI 控制符，`grep` 需加 `-a` 按文本处理；
早期失败的 trial 可能显示 `total 0`，那是 agent 未真正开始就中断。

## OSS 数据归档

### 布局

归档到 `oss://dingshang-sg/nl2repobench/`，结构与 `itbench-live/` 一致：

```text
nl2repobench/
├── README.md
├── harbor-tasks/<task>/...          # 任务定义（catalog/tasks/*/harbor/）
└── runs/
    ├── <model>/<task>/<trial>/...   # 模型运行数据
    ├── oracle/<task>/<trial>/...    # Oracle 门禁证据
    └── _queue-logs/                 # 批次队列日志
```

**无日期、无 campaign 分层**。Trial 名称是 `<run-root>--<job-dir>`，保证重复运行可区分。

| 参数 | 说明 | 推荐值 |
|---|---|---|
| `--workers` | 上传并发 | 16 |
| `--dry-run` | 只打印将上传的 key | 首次必跑 |
| `--skip-tasks` / `--skip-runs` | 只传其中一部分 | 按需 |
| `--overwrite` | 覆盖已存在对象 | 默认跳过 |

### 上传

```bash
# 1. 扫描密钥（必须）
grep -rla 'sk-proj-' .nl2repo/runs  # 替换为你的真实 key 前缀
# 期望：0 匹配（Harbor 已脱敏为 sk-R****DeI）

# 2. 上传
export OSS_ACCESS_KEY_ID='...'
export OSS_ACCESS_KEY_SECRET='...'

python scripts/upload_runs_to_oss.py \
  --workers 16 \
  --readme docs/oss-readme.md

# 3. 验证
ossutil ls oss://dingshang-sg/nl2repobench/runs/ -d
```

### 检索

```bash
# 下载单任务的全部 trial
ossutil cp -r oss://dingshang-sg/nl2repobench/runs/gpt-5.6-sol/ftfy/ ./

# 只取判分文件
ossutil cp -r \
  oss://dingshang-sg/nl2repobench/runs/gpt-5.6-sol/ ./ \
  --include "grading.json"

# 下载任务定义
ossutil cp -r oss://dingshang-sg/nl2repobench/harbor-tasks/ftfy/ ./ftfy/
```

## 注意事项

### 创建题目

1. **上游 revision 必须不可变**：使用完整 commit SHA，不能用 tag、branch 或 `latest`。
2. **冻结测试分母**：`expected` = collected − skipped，自动计算后固化到 `task.toml`。
3. **source digest 用 git archive**：`git archive <sha> | sha256sum`，确保可复现。
4. **规格不能泄漏实现**：公开 `instruction.md` 只写行为契约，不给算法、内部 helper 或测试断言。
5. **Oracle 三次门禁**：一次 1.0 不够，需要三次独立运行均为 1.0。

### 运行 Benchmark

1. **并发上限**：GPT/Claude API 有 rate limit，保守设置 `MAX_ACTIVE=2`。
2. **超时配置**：agent 3600s，verifier 根据题目调整（`stable-baselines3` 需 1800s）。
3. **错误重试**：`ApiRateLimitError`、`ApiInternalServerError` 会自动重试（最多 10 次），其他错误立即停止。
4. **密钥轮换**：本地跑完后，轮换用过的 API key（即使 Harbor 脱敏，日志可能有残留）。

### OSS 归档

1. **上传前扫描**：`grep -rla 'sk-<prefix>' .nl2repo/runs` 必须 0 匹配。
2. **不要整批删本地**：OSS 只是备份，本地保留最近的运行数据方便调试。
3. **混合目录注意**：`legacy-results/` 类目录可能包含多个模型的数据，不能整目录删。
4. **`unknown` 保留原样**：早期实验目录如果无法确定模型归属，标记为 `unknown` 而不是猜测。

### 评分口径

1. **逐题宏平均**：`dataset_score = mean(task_score)`，不能用 `sum(passed) / sum(expected)`。
2. **valid=false 不算分**：`collection-mismatch`、`junit-missing` 等是题目/环境问题，排除出有效题集。
3. **Oracle 是门禁不是分数**：Oracle runs 存在 `runs/oracle/` 下，永远不与模型分数混在一起。
4. **固定分母**：每题的 `expected` 冻结后不变，verifier 收集数必须与之一致。

### Git 协作

1. **不提交 runs**：`.nl2repo/runs/` 已 gitignored，运行数据只上传 OSS。
2. **不提交临时文件**：`temp/`, `*.pyc`, `__pycache__/`, `.DS_Store` 已忽略。
3. **commit message 格式**：`feat: <summary>` / `fix: <summary>` / `docs: <summary>`。
4. **推送前检查**：`git diff --cached | grep -E 'sk-|LTAI'` 确保无密钥泄漏。

---

**完整技术设计见**：
- 出题流程：`docs/task-authoring-guide.zh-CN.md`
- 工程路线图：`docs/engineering-roadmap.zh-CN.md`
- Harbor 迁移：`docs/phase2-harbor-verifier.zh-CN.md`
- OSS 布局：`docs/run-artifacts-oss.md`
- 快速开始：`QUICKSTART.md`
