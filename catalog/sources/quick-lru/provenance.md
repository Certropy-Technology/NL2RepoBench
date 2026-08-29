# quick-lru authoring provenance

- Candidate: `quick-lru`, npm package version `7.3.0`.
- Upstream: `https://github.com/sindresorhus/quick-lru`, frozen commit
  `f2fe88e2932603c038c61ca29de6ad5286148e1b`, tree `593eecb770374504e235d0b20a42ca6014dda77f`.
- The source was cloned into `.nl2repo/authoring-work/node-author-wave2-20260828/quick-lru/source`
  and checked out detached. The raw `git archive --format=tar HEAD` digest is
  `sha256:5264a90e047bccde14f6b5705630d7aaf5ade2fa2987f985d517aee1dd5cfc6a`.
- License: MIT, source `license`; license digest is recorded in production evidence after
  packaging.
- Upstream implementation has no runtime dependencies and no build backend. Its upstream test
  command uses AVA, XO, NYC, and tsd development dependencies, so the Harbor task uses a private
  deterministic `node:test` slice covering the public runtime contract and keeps those tools out
  of the candidate image.
- Node/npm environment is pinned to Node `24.19.0`, npm `11.17.0`, Debian Bookworm, Linux amd64,
  glibc, and the digest-pinned Node base image in `task.toml`.
- Agent and verifier network policy is `no-network`; only the trusted Oracle solve script fetches
  the exact upstream revision from the exact upstream hostname and verifies both commit and
  archive digest before constructing the candidate workspace.
