# Authoring Audit

- Mode: `author-one`; package writer: `node-author-wave2-20260828`.
- Frozen revision: `8d05c28d15ec5b690e7fbb08d703b0752d431109`; source archive SHA-256 is recorded in `provenance.md` and checked by Oracle `solve.sh`.
- Runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc; image and toolchain are digest pinned in `task.toml` and `toolchain.node.lock.toml`.
- Dependency remediation: exact npm v3 lock/cache closure contains 44 packages and is stored privately as the referenced CAS artifact. Candidate installation is offline with lifecycle scripts disabled.
- Boundary remediation: private tests call a task-local adapter child as UID/GID `10001`; trusted verifier never imports candidate code. Requests are JSON-only and bounded.
- Upstream baseline: `npm install --ignore-scripts --no-audit --no-fund && npm run test-api` passed `8/8` leaves under both development and production conditions on Node `22.23.1`/npm `10.9.8`.
- Frozen private collection: 30 `node:test` leaves. Generated report collection matched 30 with no collection errors.
- Oracle: Harbor `0.21.0`, exit `0`, `valid=true`, `30/30`, reward `1.0`, public network unavailable.
- Controls: empty install exception `0/0`; stub `0/30`; forgery `0/30` with verifier-owned grading; offline `0/30`; bounded timeout `0/0` candidate-call timeout. All controls exit `0` and report unavailable public network.
- Static network lint: this task has zero errors and one expected Oracle host-authorization warning; model Agent remains `no-network` with no static allowed hosts.

The full Harbor runtime and run trees remain task-local under `.nl2repo`; no
generated `catalog/tasks/mdast-util-mdxjs-esm/` was created in this lane.
