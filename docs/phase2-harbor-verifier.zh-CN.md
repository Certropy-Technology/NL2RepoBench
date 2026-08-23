# Phase 2：Harbor Compiler 与通用 Verifier

本文描述已经实现的 Phase 2 工程边界、评分语义和控制实验。它不把 synthetic `ministats` 的成功解释成 104 道真实题已经迁移。

## 技术栈与锁定

- Harbor：独立 `harbor-runner/pyproject.toml + uv.lock` 完整锁定，通过 `uv run --frozen --project harbor-runner harbor` 执行；不使用全局 `0.15.0` CLI；
- Harbor task schema：`1.4`；
- Agent/Verifier base：`python:3.12-slim` 的 `linux/amd64` digest；
- Verifier dependency：独立 `verifier/pyproject.toml`、`verifier/uv.lock` 和带 hash 的 `requirements.lock.txt`；
- Toolchain：根目录 [`toolchain.lock.toml`](../toolchain.lock.toml)；
- 生成器：`src/nl2repobench/harbor/`；
- Grader：`src/nl2repobench/verification/`。

四个 uv project 相互隔离：根目录 modern core、`legacy/` 历史 runner、`verifier/` separate verifier runtime、`harbor-runner/` Harbor CLI 与完整传递依赖。

## 编译链路

```text
catalog task.toml + instruction.md
  -> strict DeclarativeTaskSource
  -> canonical TaskManifest
  -> publication gap check
  -> pinned toolchain resolution
  -> Harbor task.toml
  -> agent Dockerfile
  -> separate verifier Dockerfile
  -> hash-locked verifier runtime
  -> private test bundle
  -> Oracle solution bundle
  -> bundle.manifest.json
```

Production 编译默认拒绝所有 `publication_gaps()`。Synthetic fixture 需要显式 `--allow-incomplete`，并在 bundle manifest 中标记 `mode=development`。

```bash
uv run nl2repo harbor compile \
  catalog/tasks/ministats \
  --output build/harbor \
  --toolchain toolchain.lock.toml \
  --allow-incomplete
```

Production task 的 `tests.test_bundle` 和 `oracle_bundle` 必须是授权的 private artifact tar。解包采用流式成员计数，并拒绝绝对路径、`..`、symlink、hardlink、device、重复路径、超长成员与超大展开体积。开发 fixture 可以从 `catalog/tasks/<id>/harbor/` 复制公开 synthetic assets，但不能发布。

## Verifier 执行顺序

1. `task.toml` 声明 Agent/Verifier phase policy；Verifier environment 额外生成 `docker-compose.yaml: network_mode: none`，Agent 只有声明 `no-network` 时才生成该 override，避免有效网络与 metadata 矛盾；启动后再证明 verifier 无法连接 `pypi.org:443` 和数字地址 `1.1.1.1:443`，并把 network namespace 与 route table 写入 `network.json`；
2. root 用 bounded regular-tree copier 接收 Harbor 恢复的 `/workspace`：最多 20,000 entries、单文件 64 MiB、总计 256 MiB、相对路径 512 bytes；拒绝 symlink 和其他 special file，并把原 workspace 改为 root-owned/read-only；candidate 导致的拒绝记 model zero；
3. verifier image build 从离线 wheelhouse 使用 `--no-index --require-hashes` 安装依赖；运行时再次读取并精确校验 allowlisted `VerifierCommandPlan`；
4. root install supervisor 以 UID 10001 和 CPU、地址空间、进程、FD、文件大小上限执行 candidate build backend，持续监控 wall clock、entry count 和 aggregate bytes；所有 success/failure/timeout 路径都终止 process group 并扫描 UID 至 quiescent，再把隔离 target 交给 tests；
5. private tests 仅 root 可读；root 对 private tests、command plan 和 verifier runtime 做 hash/mode snapshot；
6. trusted/root pytest 使用 `python -I -B`，只导入 private tests、trusted plugin 和 `candidate_client`，不把 candidate target 放入自身 `sys.path`，并禁用 `pytest11` autoload；
7. hidden tests 通过 `candidate_client` 为每次 API、module CLI 或 console entry point 调用创建 UID 10001 子进程；只有该子进程把 target 追加到路径并导入 candidate，candidate 看不到 private tests，不能向 root pytest 发信号，也不能写 trusted reports；
8. 每次 candidate 调用都有独立 timeout/资源上限，并共享 task-level cumulative wall budget；预算耗尽后后续调用立即失败。每次调用结束都终止 process group 并反复扫描 UID 10001，直到无残留进程；candidate 的 `os._exit`、`atexit`、后台进程或伪造输出只能影响该次实现响应；
9. root pytest 直接写 `/tmp/trusted-results` 的 collection/JUnit；candidate 无该目录权限。随后复核 trusted tree，并把有界 regular report 复制到 final logs；
10. root grader 用 `O_NOFOLLOW | O_NONBLOCK` 和大小上限读取报告；hardened parser 逐 testcase 分类，不信任 XML 汇总属性，并校验 collection、固定分母、JUnit 数量和 pytest exit/status 一致性；
11. 固定分母 grader 写 numeric `reward.json` 和详细 `grading.json`。

Verifier runtime 使用 `defusedxml` 拒绝实体展开。Agent image 不包含 test bundle、grader、runtime 或 verifier dependency。Production dependency tar 必须包含 hash-locked `requirements.lock.txt` 和完整 wheelhouse；compiler 拒绝未固定 requirement、远端/directive、缺 hash、非 wheel 文件和缺失 distribution wheel，Docker build 再由 pip 校验 wheel hash。Command artifact 必须是 allowlisted `VerifierCommandPlan`，compiler 与 runtime 双重验证，不执行任意 legacy shell 字符串。

## 评分和失败分类

| 场景 | `valid` | Failure class | Reward |
| --- | --- | --- | ---: |
| 正常测试通过/失败 | true | none | `passed / frozen_total` |
| Candidate 安装失败 | true | model | 0 |
| Candidate workspace 超限或含 special file | true | model | 0 |
| Collection error/mismatch | false | verifier | 0 |
| JUnit count mismatch | false | verifier | 0 |
| Artifact copy failure | false | verifier | 0 |
| JUnit/collection report 缺失或损坏 | false | verifier | 0 |
| 异常 pytest exit | false | verifier | 0 |
| pytest exit 与 JUnit 状态矛盾 | false | verifier | 0 |
| Verifier 可访问公网 | false | verifier | 0 |

Harbor 需要 numeric reward，因此 invalid grading 也写 0；结果分析必须读取 `grading.json.valid`，不能把 invalid verifier 结果解释为模型 0 分。

## 控制实验

Compiler 可以从不修改主 bundle 的前提下生成 stub/forgery control：

```bash
uv run nl2repo harbor prepare-control \
  build/harbor/ministats stub \
  --output build/controls

uv run nl2repo harbor prepare-control \
  build/harbor/ministats forgery \
  --output build/controls
```

使用 Harbor `0.21.0` 的实际结果：

| Control | Reward | Valid | 结论 |
| --- | ---: | --- | --- |
| Oracle（3 次独立运行） | 1.000 / 1.000 / 1.000 | true | 每次 18/18 |
| Empty/nop | 0.000 | true | Candidate 无法安装，model failure |
| Packaging + stub | 0.0556 | true | 1/18，仅极低基础分 |
| 恶意 build backend / `sitecustomize` / `pytest11` / forged JUnit、collection、reward / `os._exit` | 0.0556 | true | 攻击只终止 candidate child；root pytest 仍完成 18 项并记录 17 个失败 |
| Install hang + detached `setsid` worker | 0.000 | true | 15 秒 wall timeout 后强制终止并完成 UID cleanup，model failure |
| Candidate workspace symlink | 0.000 | true | 安装前由 bounded ingestion 拒绝，model failure |
| Repeated 9 秒 API calls | 0.1111 | true | 60 秒 cumulative budget 耗尽后立即失败，仍在 Harbor deadline 前完成 grading |
| Offline verifier | 1.000 | true | `public_network_available=false` |

历史扩展 pilot 曾要求 Oracle 在独立环境下运行三次；当前 Package campaign 改为运行一次，必须 `valid=true`、collection 与固定分母一致且 reward >= 0.80。低于 1.0 时保存失败集合和 Oracle ceiling。控制运行输出保存在 Harbor job artifact 中，不提交临时 job 目录。
脱敏后的实际结果记录在 [`phase2-ministats-controls.v1.json`](../reports/phase2-ministats-controls.v1.json)。

完整矩阵可重复执行：

```bash
scripts/run_phase2_ministats_controls.sh
```

脚本从 `harbor-runner/uv.lock` 运行 Harbor `0.21.0`，重新编译每次 Oracle bundle，运行九个 job，并由 `scripts/summarize_phase2_controls.py` 断言 reward、exceptions、grading validity、offline evidence、availability controls 和 checked report provenance。Scheduled CI 还会上传结构化 job/verifier artifacts。

## 真实 Easy/Medium/Hard Slice

真实候选审计见 [`phase2-real-slice-audit.v1.md`](../reports/phase2-real-slice-audit.v1.md)：

- Easy：`autorccar`；
- Medium：`aiofiles`；
- Hard：`boltons`。

三张 verifier image 已获得 immutable GHCR digest，但 source revision/license、Oracle、test bundle provenance、冻结 collection 和离线 dependency lock 仍缺失。因此三题状态是 `blocked`。在这些证据补齐前，不运行或发布伪造的 Oracle，不声称 Phase 2 production slice 完成。

## 当前限制

- Compiler 已生成 Harbor task bundle，但尚未生成完整 Harbor Dataset/Job experiment plan；
- PrivateArtifactResolver 当前只有本地 filesystem backend；
- Candidate install/call timeout 由 trusted supervisor 转成 model zero；只有 verifier 自身失去调度、宿主 OOM 或 Harbor 外层强制终止等 supervisor 无法执行的情况，才可能来不及写 grading，并在 Job result 中归类 environment/infrastructure；
- 当前安全 runner 是 subprocess contract，不是任意 upstream pytest 的透明 direct-import sandbox。API 返回需可 JSON 序列化；状态对象、callback、native in-process 行为和复杂 fixture 需要任务级 RPC/CLI adapter。没有 adapter 的真实题保持 `blocked`，不能回退为 root pytest 直接 import candidate；
- 真实题的 legacy verifier image adapter 尚未实现；
- Harbor parity 仍需真实题和固定 agent/model 的多 attempts 实验。
