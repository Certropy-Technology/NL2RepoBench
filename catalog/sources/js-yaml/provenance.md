# js-yaml Authoring Provenance

## Frozen Source

- Upstream: `https://github.com/nodeca/js-yaml`
- Revision: `6b4ff5e92474186b0c0381021ba4120f883c1995` (`5.4.0` tag)
- License: MIT. The license file was checked from the frozen tree.
- Archive command: `git archive --format=tar 6b4ff5e92474186b0c0381021ba4120f883c1995 | sha256sum`
- Archive SHA-256: `2f0874ea3403323297f422b9a8f91fd28e506ec80b124a0ee6a90175ee368096`
- No submodules.

The frozen upstream tree contains 305 passing core test leaves in 29 files on
the authoring host after its generated dist build. The upstream spec suite
fetches external YAML Test Suite material and is not used as a runtime
dependency or as an unbounded model task. The task freezes a 36-leaf local
JSON-compatible contract instead.

## Remediation

The upstream commit's checked-in npm lock root still declares version `5.2.0`
while `package.json` declares `5.4.0`. This was recorded by a host `npm ci`
probe (exit 0) and repaired in the task closure by using a minimal, exact,
zero-runtime-dependency package lock for the candidate contract. The package's
upstream `argparse` dependency is CLI-only and excluded from the deterministic
scored slice; no registry or dependency is needed by the scored package.

The production runtime is Node `24.19.0` / npm `11.17.0` from the digest-pinned
Bookworm image in `toolchain.node.lock.toml`. Candidate and verifier runs use
no network. The verifier invokes candidate exports through the generic JSON
subprocess boundary and never imports candidate code in the trusted process.

## Private Artifacts

The final task-local CAS references are:

- npm dependency bundle: `sha256:c31c6bd8ffa0ea14677f5553b9d1b8c9146af0efb68c5abb51423cb8b647f683` (486 bytes)
- command bundle: `sha256:10606c297187a76df5147ec51ef029894b0c2446f23aee9a951801e5202950cf` (286 bytes)
- private test bundle: `sha256:b7d97a7463b8128e1760299004a71442aaaff0b6d80e15ff816f426d3fccb7a8` (2627 bytes)
- Oracle bundle: `sha256:194fcf78e706167a7e59becd5407b00809d4359f7a651c1de42d2fb1c268215e` (28532 bytes)

The Oracle bundle contains a source-derived `dist/js-yaml.mjs` payload whose
SHA-256 is `5936ce8c292cbcbf2f633bbf19bb21beefae9ae0d71bcf426e148ff996296ca4`.
The Oracle solve script still clones and checks out the frozen revision and
strictly checks the archive digest before using that payload. This keeps the
Oracle run source-authorized while avoiding an unreviewed npm registry fetch.

The final Harbor 0.21.0 Oracle run collected 36/36 and passed 36/36 with
reward 1.0. Empty, stub, forgery, hang, install-script, loader-hook, and
offline controls all exited zero, returned `valid=true`, emitted
`public_network_available=false`, and produced rewards `0.0`, `0.1111`,
`0.1667`, `0.0`, `0.0`, `0.1667`, and `0.1667` respectively. The final
production bundle has 75 files and manifest SHA-256
`1cf1bd7e5b2cd268df0f34c74ef070a30cc58c12ed74c52d1a4ab96276ccd38d`.
The source environment pins the currently available Node 24.19.0 image
digest
`sha256:a9f5f7c91a432850b2a8a7797adf5eadb6c733ceed61167806cee7ea7fbc29df`.

The public source intentionally contains no private tests, adapter, reward
code, Oracle source, or npm cache bytes.
