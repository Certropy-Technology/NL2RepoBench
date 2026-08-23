# NL2RepoBench Harbor Benchmark

**OSS 位置**: `oss://dingshang-sg/nl2repobench/`

NL2RepoBench 评测 LLM agent 能否从一份自然语言规格和**空 workspace** 出发，
生成完整、可安装、可运行的 Python 仓库。评分由独立 Harbor verifier 产出固定
隐藏测试的通过率，agent 全程看不到测试。

## 📦 目录结构

```
nl2repobench/
├── harbor-tasks/                  # 历史归档任务定义；当前数量以版本化 manifest 为准
│   ├── aiofiles/
│   │   ├── task.toml              # catalog 元数据（上游 revision、digest、冻结分母）
│   │   ├── instruction.md         # agent 唯一输入
│   │   └── harbor/                # 可直接 harbor run 的任务
│   │       ├── task.toml
│   │       ├── environment/       # agent 容器
│   │       ├── solution/          # Oracle（克隆冻结上游）
│   │       └── tests/             # 隐藏 verifier + 冻结测试
│   ├── boto/
│   └── ...
│
└── runs/                          # 运行数据（model / task / trial）
    ├── gpt-5.6-sol/
    │   ├── ftfy/
    │   │   └── batch-gpt--gpt56-ftfy/     # 一次 trial
    │   │       ├── config.json
    │   │       ├── result.json
    │   │       ├── agent/
    │   │       │   ├── openhands_sdk.txt
    │   │       │   └── trajectory.json
    │   │       └── verifier/
    │   │           ├── grading.json       # 判分结果（权威）
    │   │           ├── reward.json
    │   │           ├── junit.xml
    │   │           └── pytest-stdout.txt
    │   └── ...
    ├── claude-fable-5/
    ├── oracle/                    # Oracle 门禁证据（非模型分数）
    │   ├── ftfy/
    │   └── ...
    ├── unknown/                   # 早期实验，模型无法从目录结构还原
    └── _queue-logs/               # 批次队列日志
```

**模型分数与 Oracle 证据分开存放**：Oracle 是环境验证，任何情况下都不能当作
模型成绩。`unknown/` 保留原样而不猜测归属，避免误算到某个模型头上。

## 🔍 快速使用

```bash
# 列出所有任务定义
ossutil ls oss://dingshang-sg/nl2repobench/harbor-tasks/ -d

# 下载单个任务（可直接 harbor run）
ossutil cp -r oss://dingshang-sg/nl2repobench/harbor-tasks/ftfy/ ./ftfy/

# 下载某模型某题的全部 trial
ossutil cp -r oss://dingshang-sg/nl2repobench/runs/gpt-5.6-sol/ftfy/ ./

# 下载某模型的全部运行数据
ossutil cp -r oss://dingshang-sg/nl2repobench/runs/gpt-5.6-sol/ ./

# 只取判分结果
ossutil cp -r oss://dingshang-sg/nl2repobench/runs/ ./ --include "grading.json"
```

## 📁 核心文件说明

### Trial 级别
- `config.json` — 任务与 agent 配置（API key 已由 Harbor 脱敏为 `sk-R****DeI`）
- `result.json` — trial 结果、异常与终态

### Agent 数据
- `agent/openhands_sdk.txt` — agent 完整执行日志（含 token 统计、重试记录）
- `agent/trajectory.json` — agent 轨迹
- `agent/instruction.md` — 实际投喂给 agent 的规格

### Verifier 数据（判分权威）
- `verifier/grading.json` — **权威判分**，字段见下
- `verifier/reward.json` — reward 与 test_pass_rate
- `verifier/junit.xml` — 结构化测试结果
- `verifier/pytest-stdout.txt` — 完整 pytest 输出

## 📊 判分口径

```json
{
  "reward": 1.0,           // clamp(passed / expected, 0, 1)
  "valid": true,           // false 时不是模型分数
  "passed": 336,
  "expected": 336,         // 冻结分母 = collected - skipped
  "collected": 336,
  "skipped": 0,
  "reason": null
}
```

```text
task_score    = clamp(passed / frozen_total, 0, 1)
dataset_score = mean(task_score for every VALID task)
```

务必使用**逐题宏平均**；不能把所有 passed 相加再除以所有测试数，否则测试多的
项目会获得更高权重。

`valid: false` 表示该次运行不是模型分数：

| `reason` | 含义 | 处理 |
| --- | --- | --- |
| `collection-mismatch` | collected − skipped ≠ 冻结分母 | 题目/环境问题 |
| `junit-missing` | pytest 未产出结果 | 检查安装与 verifier 日志 |
| `installation-failed` | 候选包无法安装 | 先确认环境，再判定模型失败 |
| `pytest-abnormal-exit` | verifier 崩溃 | 基础设施问题 |

## 📌 历史数据集状态

以下是旧归档的描述，不是当前 Package campaign 的发布证明：

- 旧归档曾记录 **37 个 active 任务** 和 **13 个 blocked 候选**；
- 旧归档的单题冻结测试数从 26 到 1009；
- 当前 campaign 使用一次 Oracle gate，并通过
  `reports/package-expansion-campaign.json` 和 OSS run inventory 重新计算状态。

## 🔗 代码仓库

https://github.com/Certropy-Technology/NL2RepoBench

从零跑通 benchmark 见仓库 `QUICKSTART.md`。
