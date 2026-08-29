# Emittery Authoring Provenance

## Frozen Source

- Upstream: `https://github.com/sindresorhus/emittery`
- Revision: `147a8591045e00d0fe8088e2393e3eefea3aa4a5`
- Commit subject: `Fix CI`
- License: MIT
- License file SHA-256: `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Frozen `package.json` SHA-256: `0c4b477a6dcc48435ba69f7de9ce443f4e40c00872d45042603aed8054e3ca48`
- Exact source archive command: `git archive --format=tar HEAD`
- Source archive SHA-256: `b650e76fc6fb9b6dc3ed45c5456b3226f1c05e3cf06e376f47d8b647a92ae138`
- No submodules; source tree contains one runtime JavaScript file, one
  declaration file, one upstream test file, examples, documentation, and media.

The frozen upstream package declares version `2.0.0`, Node `>=22`, ESM mode, root exports
`./index.js` and `./index.d.ts`, no runtime dependencies, and development-only
dependencies for AVA, XO, tsd, delay, and p-event. In the pinned Node
`24.19.0` image with npm `11.17.0`, the unmodified `npm test` command passed all
`253` upstream AVA leaves. Development dependencies are not part of the task
runtime closure.

## Deterministic Rescope

The production task scores 44 leaves derived from the upstream behavioral
families. A private custom-json-v1 child adapter constructs all callbacks,
promises, AbortSignals, symbols, iterators, and decorator targets internally.
Only scenario tags, bounded object inputs, and JSON-safe observations cross the
candidate boundary. Timing-sensitive upstream tests are represented using
controlled promises and microtasks; TTY, wall-clock, network, and source-text
inspection are excluded.

The candidate is installed from its packed distribution with development
scripts removed. The verifier owns the exact node:test contract, candidate
client, command plan, and report/reward generation. Private bytes are stored in
the worktree-local content-addressed artifact store and are not copied into
the public source.

## Environment and Network

The runtime is the digest-pinned Debian Bookworm Node image from
`toolchain.node.lock.toml`, Node `24.19.0`, npm `11.17.0`, linux/amd64/glibc.
The agent and separate verifier use `no-network`, with no static allowed hosts.
The Oracle solution alone fetches the frozen revision from the exact upstream
host and verifies both the resolved commit and archive digest before installing
the stripped distribution.

## Gate State

The private adapter passed `44/44` in a direct no-network Docker smoke test
after the candidate-site path was preserved through the unprivileged child
launch. Production compile, Harbor Oracle, controls, and final evidence are
recorded in the handoff when complete. This lane does not start a Harbor Agent
Run; blind review, model pilot, and publication remain downstream work.
