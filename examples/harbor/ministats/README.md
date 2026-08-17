# Harbor E2E 示例：`ministats`

本题要求 Agent 从空的 `/workspace` 开始，构建一个小型、可安装的 Python 仓库。公开行为契约见 [`instruction.md`](instruction.md)。

本示例面向 Harbor `0.21.0` 和 task schema `1.4`。本机安装的 Harbor `0.15.0` 版本过旧，无法使用该任务定义。

## 环境

- Agent 镜像：`python:3.12-slim`，并安装 Bash、curl 和 Git。
- Agent 工作目录：`/workspace`。
- Agent 网络：`public`，与原论文不限制工具使用的实验设置一致。若需要控制数据污染，应进一步收紧网络策略。
- Agent 超时：600 秒；2 个 CPU，2 GiB 内存。
- Verifier：使用独立的 `python:3.12-slim` 镜像，运行时不允许联网。

## 验证器

Agent 生成的整个 `/workspace` 被声明为 Harbor artifact，并在独立 verifier 中恢复到相同路径。隐藏测试不会进入 Agent 环境。

| Reward | 类型 | 含义 |
| --- | --- | --- |
| `reward` | 程序化评分 | 通过测试数除以冻结的 18 个测试 |
| `test_pass_rate` | 程序化评分 | benchmark 指标的具名副本 |

Verifier 会先把候选仓库复制到私有临时目录，在不下载依赖的情况下安装，然后运行 pytest 并生成 JUnit 报告，最后写入 `/logs/verifier/reward.json`。详细测试计数写入 `/logs/verifier/grading.json`。

## 目录结构

```text
ministats/
├── instruction.md          # 公开的仓库生成规格
├── task.toml               # Harbor 任务、资源、artifact 和 verifier 隔离配置
├── environment/
│   └── Dockerfile          # 空的 Python Agent 环境
├── solution/
│   └── solve.sh            # Oracle 参考实现
└── tests/
    ├── Dockerfile          # 隔离的 verifier 镜像
    ├── grade.py            # 将 JUnit 转换为固定分母的 reward
    ├── test.sh             # Verifier 入口
    └── test_ministats.py   # 隐藏行为测试
```

## 运行

在仓库根目录中，使用 Harbor `0.21.0` 或兼容的新版本运行：

```bash
harbor run -p examples/harbor/ministats -a oracle
```

Oracle 的 reward 必须为 `1.0`。

提供已经配置好的模型即可运行真实 Agent：

```bash
harbor run \
  -p examples/harbor/ministats \
  -a openhands \
  -m '<provider>/<model>'
```

若要与已发布的 benchmark 结果进行等价比较，还必须固定 Harbor commit、OpenHands 版本、模型请求参数、网络策略以及 timeout/iteration 策略。

## 验证结果

已于 2026-08-17 使用 Harbor `0.21.0`、commit `f03db62fd2ed2ed1f79aefe024cfcbc68a0d759e` 完成验证：

- Oracle：通过 18/18 个测试，`reward=1.0`、`test_pass_rate=1.0`，无异常。
- 空的 `nop` Agent：`reward=0.0`、`test_pass_rate=0.0`，无异常。
- Artifact manifest：`/workspace` 以目录形式成功收集，状态为 `ok`，并在独立 verifier 中恢复。
