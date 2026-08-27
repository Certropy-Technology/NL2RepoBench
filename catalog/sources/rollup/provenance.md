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
