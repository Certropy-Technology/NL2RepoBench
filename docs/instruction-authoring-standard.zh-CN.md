# Task instruction authoring standard

`catalog/sources/<task-id>/instruction.md` 是给 coding agent 的公开项目规格，不是
测试摘要，也不是一句“实现一个类似 X 的库”。它必须让 agent 从空 workspace 推导出
可安装项目的目录、入口、公开 API 和可观察行为，同时不暴露 private verifier、隐藏
测试或参考实现。

本标准参考仓库中的 `docs/instruction-examples/autojump.start.md` 与
`docs/instruction-examples/bleach.start.md`。它们分别镜像给定的
`test_files/autojump/start.md` 和 `test_files/bleach/start.md`，并共同体现了本项目要求的写法：先说明项目和
用户目标，再给自然语言任务；随后固定环境和依赖，给出 **Project Directory
Structure**，逐个写公开 API 的 import path、signature、参数、返回值、状态变化、
异常和示例，最后补充功能节点、边界、安全和组合用法。新 instruction 必须遵守下面
的顺序和密度。

## Required section order

除非任务是有证据的 `blocked` source，否则必须包含这些一级标题。标题可以使用英文或
中文，但应保留括号中的 canonical phrase，方便静态检查：

1. `Project Description`：项目用途、目标用户、输入输出边界、明确排除项。
2. `Natural Language Instruction`：直接给 agent 的建题要求。至少列出四项 task-
   specific capabilities，并说明包名、import 包名、安装入口和不可违反的跨模块约束。
3. `Supports` 或 `Environment Configuration`：语言/runtime、包管理器、安装命令、
   运行时依赖、build dependency、NoNetwork 运行约束和版本/平台边界。
4. `Project Directory Structure`：一个 `text`/`plain` code fence，根为
   `workspace/`，列出 agent 必须创建的 public package、入口文件、配置文件和 CLI
   或脚本。目录树必须与后面的 API 入口一致，不能只写三行泛化目录。
5. `API Usage Guide`：按模块逐项描述公开 API。
6. `Implementation Notes` 或 `Detailed Implementation Nodes`：跨模块约束、状态机、
   确定性、序列化、资源清理、错误传播和少量实现提示，但不泄漏算法答案。
7. `Examples`、`Error Handling and Boundary Conditions` 或 `Security`：至少给出
   两个普通用法和两个边界/错误/安全例子。示例必须是公开规格的一部分，不得复制
   hidden test 的完整断言或 verifier fixture。

## API entry contract

每个核心公开函数、类、CLI 或 root export 至少包含：

- 完整 import path，或 CLI 命令和入口文件；
- 完整 signature，包含默认值、keyword-only 参数和泛型/返回形状（如果对 agent 可见）；
- 输入域和不接受的输入；
- 返回类型、容器形状、顺序和确定性；
- 文件、环境、网络、全局状态或对象状态副作用；
- 异常类型和触发条件；
- 一个普通例子，以及必要时一个空输入、Unicode、错误输入或重复调用例子。

只写 `实现类似 X` 不足以形成 contract。若 API 很多，先按模块列 root exports，再用
表格或小节覆盖每组行为。API inventory、test inventory 和 traceability 是写作输入，
但 instruction 必须把它们转换成 agent 可执行的公开规格，不能把文件名直接当作规格。

## Directory structure contract

目录树应描述目标项目，而不是复制上游 checkout 的所有文档、CI 和测试文件。至少列出：

- package source root 及每个公开模块；
- `pyproject.toml`/`setup.py`、`package.json`/lockfile 或 `go.mod` 等安装元数据；
- root export、CLI entry point、必要的资源/fixture 目录；
- 若任务要求 shell、plugin、adapter、migration 或多入口，逐个列出其位置；
- 与 API Usage Guide 中 import path 对应的实际 `.py`/`.js`/`.go` 文件。

Blocked source 可以没有完整目录树，但 `blocked.md` 必须说明缺失的 runtime/package
closure、已尝试的目录/构建 probe 和下一步解除条件。不要为 blocked 任务伪造可运行
结构。

## Writing rules

- 写成项目规格，使用直接、可检查的句子；避免宣传语和空泛形容词。
- 公开 instruction 可以说明行为，但不能复制函数体、完整算法、上游测试文件、隐藏
  leaf ID、grader 路径、private artifact digest 或 candidate/verifier 内部协议。
- 版本、依赖和目录必须与 `task.toml`、source evidence 和实际 compiler 输入一致。
- 示例必须可在公开规格语境中解释，不能依赖网络、付费服务或未声明的机器状态。
- NoNetwork 任务明确写出：agent、candidate、verifier、Oracle、controls 均不得运行期
  访问 GitHub、PyPI、npm、Go proxy、DNS 或外部服务。
- 术语和章节保持稳定。不要为了变长重复同一个承诺；新增文字必须增加可实现的
  输入、输出、状态、边界或目录信息。

## Review and gate

Instruction 改动后必须重新运行：

```bash
uv run python scripts/validate_instruction_quality.py
uv run nl2repo task validate-source catalog/sources/<task-id>
uv run nl2repo harbor compile catalog/sources/<task-id> --allow-private ...
```

instruction 进入 compiled manifest 后，旧 Oracle/control receipt 不得复用。任何目录、
版本、依赖、verifier、control 或 instruction 改动都需要绑定新的 final manifest。
