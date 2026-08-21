# npm / Node Harbor 题接入可行性

## 结论

Harbor `0.21.0` / task schema `1.4` 能运行 Node/npm 题，因为 Task 本身只要求
Docker environment、`tests/test.sh`、artifact 和数值 reward，并不限定 Python。
但 NL2RepoBench 当前 compiler、dependency bundle、candidate installer、subprocess
boundary 和 grader 都是 Python/pytest 专用。因此结论是：**可以做独立 Node pilot，
现在不能把 npm 题直接混入 Python dataset。**

Node 题使用单独的 `nl2repobench-node-pilot-v1`。它不与论文 104 题或现有 Python
Harbor pilot 合并评分，也不声称 parity。

## Production blocker

1. 当前 `EnvironmentLock` 只有 `python_version`，需要 Node/runtime profile、架构和
   libc 锁。
2. Python wheelhouse contract 不能表达 npm tarball、npm cache/pnpm store、lockfile
   版本、Corepack/package-manager 版本和 lifecycle-script policy。
3. 当前 verifier 通过 pip 安装 candidate，并使用 pytest collection/JUnit；Node
   需要独立 install/build/pack contract 和 framework adapter。
4. hidden test runner 不能在 trusted process 中直接 `require()` / `import()` candidate。
   需要 `node-subprocess-boundary-v1`，限制 stdout、时间、内存、进程和文件。
5. Jest/Vitest/Mocha/tap/`node:test` 对 skipped/todo、hook failure、nested test 和
   dynamic registration 的语义不同，需要新的 leaf-test metric contract。
6. native addon、Electron、browser、monorepo/workspace 和远端服务依赖不适合首批。

## 首批边界

首个 vertical slice 只支持：

- digest-pinned Node LTS `linux/amd64` image；
- npm + committed `package-lock.json`，执行 `npm ci --offline`；
- zero-dependency 或完整离线 tarball closure；
- 无 native addon、无 workspace、无浏览器、无远端服务；
- verifier-owned `node:test` runner 与结构化 reporter；
- candidate 先 `npm pack`，检查 tarball 后安装到隔离 target；
- agent 与 verifier 都默认断网；
- 独立子进程调用 JSON 可序列化 API 或 CLI；
- Oracle 三次 `valid=true`、稳定 collection、reward `>= 0.80`；
- empty、stub、forgery、install-script、loader-hook、hang 和 offline 控制。

适合的五类 pilot：纯 JavaScript 字符串/数组工具、parser/serializer、受限文件
转换库、小型 CLI、单一 ESM 或 CJS 输出的 TypeScript package。双 ESM/CJS package、
Jest/Vitest adapter 和 native addon 放在后续阶段。

## 关键工具约束

- `npm ci` 要求 package manifest 与 lockfile 一致，不修改 lockfile；生成 lock 时用的
  tree-shaping flags 必须在 CI 中一致。
- npm lifecycle scripts 是不可信代码。默认 dependency install 使用
  `--ignore-scripts`，必须构建时再运行 allowlisted、受资源限制的 build command。
- Corepack 从 Node 25 起不再随 Node 一起分发，不能隐式依赖；必须显式 pin，或直接
  pin npm/pnpm executable。
- Jest 的 `--collectTests --json` 会执行 test registration 顶层代码；Vitest 有 JSON
  和 JUnit reporter；Mocha 缺少同等静态 collection contract。首批优先 `node:test`。
- Candidate 不能控制 test runner config、reporter、trusted result 路径、`NODE_PATH`、
  loader hook、npm cache 或 registry config。

## 实施顺序

1. 新增 Node ADR、runtime/dependency/test schema 和独立 metric contract。
2. 实现一个 synthetic `node:test` separate-verifier task。
3. 实现 offline package closure、pack/install supervisor 和 JSON subprocess adapter。
4. 跑完整攻击/负向控制矩阵。
5. 选择 5 个 archetype pilot，做 blind/spec review 和多模型 pilot。
6. 单独发布 Node dataset；确认 framework normalization 后再讨论跨语言聚合。

## 参考

- Harbor task structure: <https://www.harborframework.com/docs/tasks>
- Harbor network policy: <https://www.harborframework.com/docs/tasks/network-policy>
- npm ci: <https://docs.npmjs.com/cli/v11/commands/npm-ci/>
- npm scripts: <https://docs.npmjs.com/cli/v11/using-npm/scripts/>
- pnpm install: <https://pnpm.io/cli/install>
- Node Corepack: <https://nodejs.org/api/corepack.html>
- Node package resolution: <https://nodejs.org/api/packages.html>
- Node test runner: <https://nodejs.org/api/test.html>
- Jest CLI: <https://jestjs.io/docs/cli>
- Vitest reporters: <https://vitest.dev/guide/reporters>
- Mocha JSON reporter: <https://mochajs.org/reporters/json/>
- node-gyp requirements: <https://github.com/nodejs/node-gyp/blob/main/README.md>
