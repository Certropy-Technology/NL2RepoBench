# `mdast-util-to-markdown` Authoring Provenance

Status: `controls-passed`; ready for independent review and later model pilot.

## Source and license freeze

- Upstream: `https://github.com/syntax-tree/mdast-util-to-markdown`.
- Revision: `ee3b3458a466c3224800ac7fa688b4a160a91ea2`.
- Package: `mdast-util-to-markdown@2.1.2`.
- Tree: `ce716a71cd2262a1be328af797f17fb5fbea7d67`.
- `git archive --format=tar` SHA-256:
  `de486cc3d34b204e8db55cd7e97074f60a8ede2e9b57bbe8cb8e2991ad1ddc5c`
  (296,960 bytes).
- MIT license SHA-256:
  `dd1081884a92952802f4803110a6bb543acea9a814c786d58605b4c1219b5ebb`.
- No submodules.

On the locked Node image, the frozen source passed its TypeScript build with
7,615/7,615 covered type expressions, one full 100% c8 gate, and three
independent offline behavior runs at 478/478.

## Environment and dependency closure

- Image:
  `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc 2.36.
- Exact direct package versions are declared in `task.toml`; the resulting
  graph has 17 packages and no native/install-script package.
- Private npm v3 closure:
  `sha256:29a9d2641d88d8bf563b0869eeb3c13a2bc81f1d66a7ba1d27d4cb27c2c58184`
  (1,105,920 bytes). It contains 68 cache entries, the npm v3 lock, and
  per-file SHA-256 records.
- `validate_npm_dependency_bundle` passed, followed by a clean
  `npm ci --offline --ignore-scripts --no-audit --no-fund` with network mode
  `none`.

## Verifier and Oracle boundary

- Separate no-network verifier; candidate UID 10001.
- Trusted `node:test` never imports candidate JavaScript. The candidate child
  accepts at most 128 KiB of JSON and emits at most 512 KiB in a two-second
  bounded process.
- Command plan:
  `sha256:40670b2d2de24a20505e059dfc05fc46d3b2f1291fe1276d2fa29646b0c167ed`
  (10,240 bytes).
- Private 72-leaf tests:
  `sha256:a1fe6049d2831352137541f734ae11d5fcb11d6079082df67329fda90c529264`
  (30,720 bytes).
- Private Oracle:
  `sha256:7c63571a5382d1000a5f9ff136d7d7e2f441e1520114197e83b921a5248ffde1`
  (20,480 bytes). Its solution fetches only the fixed revision, asserts the
  resolved commit, verifies the source archive digest, and applies a reviewed
  package-only lock adaptation before populating `/workspace`.
- A local generic verifier probe against the adapted frozen source collected
  and passed 72/72 leaves.

## Harbor outcomes

- Official Harbor `0.21.0` Oracle: `valid=true`, 72/72 passed, reward `1.0`,
  and `public_network_available=false`.
- Empty workspace: the allowed `candidate-installation-failed` exception,
  reward `0`.
- Stub: 6/72, reward `0.08333333333333333`.
- Forgery: 2/72, reward `0.027777777777777776`; forged workspace reward and
  grading files were ignored.
- Lifecycle-script control: rejected as `candidate-installation-failed`,
  reward `0`.
- Bounded call hang: 0/72 with complete collection, reward `0`.
- Offline network-attempt control: 1/72, reward
  `0.013888888888888888`.
- Every Oracle/control verifier network receipt reports
  `public_network_available=false`.

The first Oracle attempt is retained as remediation evidence: source fetch,
commit assertion, and source checksum passed, but the solution removed its own
current working directory before invoking Node. The corrected bundle changes
to `/` before replacing `/workspace`; the fresh retry passed fully.

The host's current `nl2repobench/openhands-sdk-fork:930e9b1da-bookworm` tag has
image ID `sha256:bb48824b85940a3b6083ce0a1d713af6963ebf92bcba318dfc5838461a4081c3`,
while `toolchain.node.lock.toml` requires
`sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f`.
The task embeds the correct expected ID; retagging the
global daemon is outside this isolated lane. Integrators must restore or verify
the immutable runtime before a model Agent run.

No model Agent run was permitted or performed in this lane.
