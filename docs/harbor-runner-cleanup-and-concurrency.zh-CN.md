# Harbor Runner 清理、取消和并发运行手册

## 事故记录：`harbor__xdwqq5m__env-main-1`

2026-08-22 的 Fable `unittest-parametrize` trial 出现了一个看似“容器卡在
`sleep infinity`”的问题。

实际因果链是：

1. Harbor agent environment 的主进程使用 `sleep infinity`，这是保持环境服务存活的
   正常占位命令，不代表候选代码在无限循环；
2. OpenHands relay 连续返回 `ApiInternalServerError: upstream request failed`，Harbor
   进入 retry/cancel 路径；
3. Harbor 0.21.0 在 Python 3.14 下从另一个 asyncio context 执行
   `ContextVar.reset(token)`；
4. `scoped_exec_env` 抛出
   `ValueError: Token ... was created in a different Context`；
5. 随后的 artifact collection/`DockerEnvironment.stop()` 又遇到
   `RuntimeError: no running event loop`，所以 `delete=true` 没有完成；
6. compose environment 项目遗留，造成 `harbor__xdwqq5m__env-main-1` 长时间运行。

这类 trial 必须归类为 infrastructure/runner cleanup failure，不能算模型 0，也不能
把环境容器的 `sleep infinity` 当成 task 行为。

## 当前防护

### 安全 Harbor entrypoint

模型运行脚本现在使用：

```bash
cd harbor-runner
PYTHONPATH=../src \
  uv run --frozen python ../scripts/harbor_safe_entry.py run ...
```

entrypoint 在 Harbor CLI 启动前安装一个最小、幂等的 cleanup patch：当 ContextVar token
属于已取消的其他 context 时，将 overlay 恢复为已知的 previous value，而不是让异常
阻断环境停止。它不修改 reward、测试、重试分类或 agent 行为。

### 精确 compose cleanup

`scripts/run_harbor_model.sh` 在 Harbor 进程正常退出、失败或 shell 收尾时调用：

```bash
python scripts/cleanup_harbor_trials.py --jobs-dir <exact-jobs-dir>
```

cleanup 只读取该 jobs directory 下存在 `lock.json` 的 trial，按照 trial name 生成精确
的 `harbor__<trial>__env` project，并执行该 project 的 `docker compose down --volumes`。
它不会执行 `docker system prune`、`docker builder prune` 或删除其他 job。

手工检查可使用：

```bash
python scripts/cleanup_harbor_trials.py \
  --jobs-dir .nl2repo/runs/<run>/<task> --dry-run
```

如果 Harbor 进程被 `SIGKILL`、机器断电或宿主机崩溃，shell trap 也无法运行。恢复后
必须对对应 run root 做一次 dry-run 审计，再执行精确 cleanup；未知 jobs directory
下的容器不能凭名称猜测删除。

## 正确的诊断顺序

看到 `sleep infinity` 时按下面顺序判断：

```bash
# 1. 找到真实 compose service 名称（通常带 -1 后缀）
docker ps -a --filter name='harbor__' \
  --format '{{.ID}} {{.Names}} {{.Status}} {{.Image}} {{.Command}}'

# 2. 检查 trial 是否仍有 Harbor runner/job 进程
ps -eo pid,ppid,stat,etime,args | grep -E 'harbor run|run_model|<run-root>'

# 3. 读取 result/exception/trial.log，而不是只看容器状态
cat <run-root>/<task>/<timestamp>/harbor__<id>/result.json
cat <run-root>/<task>/<timestamp>/harbor__<id>/exception.txt
tail -200 <run-root>/<task>/<timestamp>/harbor__<id>/trial.log

# 4. runner 已退出且 trial 已终态时，才对精确 jobs-dir cleanup
python scripts/cleanup_harbor_trials.py --jobs-dir <exact-jobs-dir> --dry-run
python scripts/cleanup_harbor_trials.py --jobs-dir <exact-jobs-dir>
```

如果 runner 仍然存在，不能直接 `docker rm -f`；先通过 Harbor/job 控制面停止它，
避免 runner 继续写 artifact 或重新创建同名 compose 项目。只有确认 trial 终态后才可
手工移除残留容器。

## 并发策略

修复 cleanup 后可以提高并发，但不能机械地把并发设为机器 CPU 数：

- **静态 AST/discovery authoring**：可以 8–16 个 worker；主要受网络、Git 和磁盘限制；
- **source/environment probe**：建议 4–8；受 `/tmp`、Docker build cache 和 registry 限制；
- **Harbor Oracle/control**：先 2–4；每题有独立 jobs/run root，且不能与其他项目共享
  可写 artifact/cache；稳定一批后再提升到 6–8；
- **模型 benchmark**：根据模型 provider rate limit、Docker 内存和磁盘设置，默认 2–4；
  每个 task/attempt 必须独立 run root，不能追加到失败 job；
- **同一 task**：多个 attempts 可以并行，但共享 Harbor image build、private artifact
  和状态数据库必须有锁；不要让两个 writer 改同一 task/stage。

每次提升并发前检查：

```bash
df -h /tmp / /data
docker system df
docker ps --format '{{.Names}} {{.Status}}' | wc -l
```

不要在有其他 Harbor/Frontier 任务运行时执行全局 Docker cache prune。空间不足时先停止
新任务、等待在途任务收尾，再只清理本项目已终态的 jobs、trial compose project 和明确
归属的 temporary worktree。

## 未来 Bench 的必备验收

每个 batch runner 必须同时满足：

1. Harbor 进程退出后，精确 jobs-dir cleanup 已执行并写入 `cleanup.log`；
2. `docker ps -a` 不再出现该 run 的 compose project；
3. `result.json` 有 `finished_at` 和明确 termination/exception reason；
4. `valid=false`、API gateway failure、runner cleanup failure 与模型失败分开记录；
5. 取消、SIGTERM、timeout、API 5xx 各有至少一个 smoke/regression case；
6. 并发配置、attempt 数、retry policy、run root 和 cleanup artifact 写入 experiment
   manifest；
7. 任何 orphan container 都使 batch reliability gate 失败，不能只看 Harbor CLI exit code。
