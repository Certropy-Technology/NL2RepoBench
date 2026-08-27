# Rollup task provenance

- Upstream: `https://github.com/rollup/rollup`
- Frozen revision: `89bda2cd8e9def2ea037e7dbffaf392ce9f1ddcb`
- Exact `git archive` SHA-256: `1be81f7d2cd36f7539701f6f93f107bf28eccb31a8ade43de5fd8c55137983d6`
- License: MIT (`LICENSE.md` at the frozen revision)
- Package version: `4.62.5`
- Runtime: Node `24.19.0`, npm `11.17.0`, Linux amd64/glibc

The reference artifact follows Rollup's own Node-WASM release path. Authoring
builds `wasm-node`, the generated AST converters, and the Node JavaScript
distribution from the frozen source. As prescribed by the upstream
`publish-wasm-node-package.js`, `dist/native.js` is replaced by the frozen
`native.wasm.js` adapter and `dist/wasm-node` is included. The resulting
package has no native addon, lifecycle hook, or runtime dependency.

The complete upstream Mocha suite passed 5,444 leaves in each of three
network-disabled runs. The production verifier freezes an 11-leaf JSON-only
subprocess contract derived from the public API and CLI behavior. Hidden test
source, candidate adapter source, and Oracle archives remain in the private
task-local artifact store and are not present in the agent image.

The final production compile used `toolchain.node.lock.toml` and the task-local
private artifact store without `--allow-incomplete`. Its bundle manifest is
`sha256:6b96466d88c2b563a01c7dbbe67ef6a9aec50987addaefbb1ebe5968e0ebfc25`.
Harbor 0.21.0 collected and passed all 11 Oracle leaves for reward 1.0. Empty
and hang controls scored 0; stub, forgery, loader-hook, and network-dependent
controls each scored 1/11; lifecycle-script packaging was rejected before its
script could run. Every separate-verifier network receipt reported no public
network access. Full paths and command outcomes are recorded in
`production-evidence.json` and task-local `.nl2repo` receipts. The receipts
were rerun after lifecycle advancement so they match canonical manifest
`sha256:1ccdc60b2c0196243c58c58ad82b021a473d564999262a420095a49b9da4d323`.
