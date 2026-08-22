# Harbor/OpenHands Trajectory 产物说明

## 结论

当前 OpenHands SDK adapter 不保证生成 `history.json` 或 `event.json`。Harbor
标准产物是 ATIF JSON，通常叫 `agent/trajectory.json`。OpenHands 事件被 Harbor
转换为 ATIF；原始 event stream 不会自动以同名文件保留。

如果 Agent 在第一次模型响应前失败，例如 provider 返回 HTML、认证失败或 setup
失败，则可能没有 trajectory。这时应把 run 标成 incomplete/infrastructure，不能
手工补一个 trajectory。

## 成功 run 路径

```text
.nl2repo/runs/<root>/<prefix-task>/<timestamp>/harbor__<id>/
├── agent/trajectory.json
├── agent/openhands_sdk.txt
├── agent/run_agent.py
├── agent/instruction.md
├── artifacts/workspace/
├── result.json
├── lock.json
└── verifier/grading.json + reward.json + JUnit/collection files
```

GPT smoke 实测得到 `ATIF-v1.5`、131 steps、129 tool calls、83 observation steps 和
final token/cost metrics。Fable 在首次 provider 响应前收到 HTML，因此没有
`trajectory.json`，这是失败分类的一部分，不是需要补写的缺文件。

## 验证 ATIF

官方格式文档：

```text
https://www.harborframework.com/docs/agents/trajectory-format
```

本地验证：

```bash
harbor-runner/.venv/bin/python -m harbor.utils.trajectory_validator \
  .nl2repo/runs/<root>/<task>/<timestamp>/harbor__<id>/agent/trajectory.json
```

检查 schema version、step IDs、source、tool-call references、observations、时间戳和
metrics。reward 只从 `result.json`/`verifier/grading.json`读取。

## history/event 缺失排查

1. 查是否存在 `agent/trajectory.json`；
2. 查 `result.json.exception_info`、`job.log`、`trial.log`；
3. 查 `agent/openhands_sdk.txt` 是否为 HTML、401、gateway 或 transport error；
4. 若 Agent 阶段未完成，不要把缺文件归因于模型代码；
5. 若要原始 OpenHands events，单独扩展 adapter 的 artifact collection/retention，
   不要从 ATIF 反向伪造 event/history。

## 归档规则

- trajectory 上传 OSS 前必须做全 root secret scan；
- `openhands_sdk.txt` 可能包含 provider error 和大段输出，上传前检查 key；
- private instruction/test/grader 不应复制到 public task；
- 失败 trial 可以归档，但标记 invalid/infrastructure，不能进入宏平均；
- token/cost 缺失记录为缺失，不当作 0。
