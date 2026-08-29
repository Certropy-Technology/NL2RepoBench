# `micromark-util-character` Authoring Provenance

## Frozen source

- upstream: `https://github.com/micromark/micromark`
- revision: `774a70c6bae6dd94486d3385dbd9a0f14550b709`
- commit date: `2025-05-10T20:46:45+02:00`
- repository tree: `3cbac3a1337cd2d53cf432315efb3e30964bcddf`
- package subtree: `2c624cf628756f5ad5d8fa9ed44d7cf86a5b065a`
- package version: `2.1.1`
- license: MIT
- package license SHA-256: `dd1081884a92952802f4803110a6bb543acea9a814c786d58605b4c1219b5ebb`
- full `git archive --format=tar` bytes: `1116160`
- full archive SHA-256: `ffbc51c1237344db6b47db8000aaa1668e89eb207f6a94b3a5b6472d5dda08d1`
- tracked repository files: `235`; tracked package files: `6`
- submodules: none

## Build and dependency remediation

The frozen package stores authored runtime in `dev/index.js`. The package-only
`npm run build --workspace micromark-util-character` generated `index.js` but
exited the authoring probe before a declaration existed. The successful
upstream-prescribed order ran TypeScript build mode for the types, symbol, and
character workspaces, then the package build. It generated `index.js`,
`index.d.ts`, and `index.d.ts.map`; a Node 24 probe loaded exactly 12 exports and
confirmed ASCII, virtual-code, Unicode-symbol, and Unicode-space examples.

The candidate closure narrows the frozen semver ranges to
`micromark-util-symbol@2.0.1` and `micromark-util-types@2.0.2`. npm `11.17.0`
generated a v3 lock and populated 11 cache files (93,184 bytes). A clean
`npm ci --offline --ignore-scripts --no-audit --no-fund` installed both exact
packages without egress. The content-addressed dependency bundle is
`sha256:3715cd959353c56f2b92dfef87816b61d2344cbcb83110b387e9e2f91ab89ace`.

## Verifier and Oracle adaptation

The private 106-leaf contract covers the complete public export inventory and
the documented code domain. A verifier-owned adapter loads candidate code only
in a bounded UID/GID 10001 child. The Oracle fetches only the exact commit from
`github.com`, asserts the resolved revision, verifies the full archive digest,
and combines tracked package files with private generated output produced by
the successful frozen build. Candidate and verifier phases remain offline.

## Commands and outcomes before Harbor execution

| Stage | Command summary | Exit | Outcome |
| --- | --- | ---: | --- |
| source freeze | clone/fetch `main`, detach, `git archive` | 0 | exact revision/tree/archive recorded |
| first upstream package build | npm install; package workspace build; require declarations | 1 | environment sequencing gap identified |
| remediated upstream build | TypeScript build dependencies and package, then micromark build | 0 | generated runtime and declarations; 12-export probe passed |
| dependency closure | npm install followed by clean offline npm ci | 0 | two exact packages installed from 11-file cache |
| npm bundle validation | `validate_npm_dependency_bundle(..., 11.17.0)` | 0 | lock, integrity, cache inventory, and lifecycle policy accepted |

Oracle, controls, compile receipts, and any bounded retries are recorded in
`production-evidence.json` after execution.
