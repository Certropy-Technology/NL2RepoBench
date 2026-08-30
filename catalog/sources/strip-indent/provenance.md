# `strip-indent` authoring provenance

## Source and license freeze

- Upstream: `https://github.com/sindresorhus/strip-indent`.
- Frozen revision: `102b553f9efaec1c2451cd9ac2385269768f1fed`
  (`4.1.1`), tree `13969e0fa709bc29c2a32b66c748c1c6b5c4c834`.
- `git archive` SHA-256:
  `9a3784a247647b173270b316dbd024f6a267e8eea6cb23dcaf5fb0339ba6e4dd`.
- Root `license` is MIT and the revision has no submodules.

The Oracle fetches only this commit, asserts the resolved commit, rebuilds the
archive, and verifies the archive digest before copying source into the trusted
Oracle workspace. The script is not included in the model Agent image.

## API and tests

The public runtime surface is the package-root default
`stripIndent(string: string): string` and named
`dedent(string: string): string` exports. Upstream uses AVA with 18 assertions
across two test blocks plus TypeScript declaration checks. The production
contract independently freezes 32 `node:test` leaves covering package shape,
minimum indentation, mixed spaces/tabs, blank lines, CRLF, dedent boundaries,
Unicode content, errors, and determinism.

## Environment and dependencies

- Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc.
- Node image is pinned by digest in `task.toml`.
- There are no runtime dependencies. The private npm v3 bundle contains an
  empty, integrity-described cache and exact lock metadata.
- Candidate and verifier phases are no-network. Task metadata has no source,
  registry, or provider allowlist.

## Verifier boundary

The separate verifier copies and packs a bounded candidate workspace, rejects
lifecycle scripts and unsafe package entries, installs into a candidate-owned
site with scripts disabled, and runs candidate calls as UID 10001. Trusted
`node:test` selects only the two documented root exports through the fixed
one-shot JSON child protocol. Grading, network evidence, collection, JUnit, and
reward are verifier-owned.

## Gate record

Production compile, Oracle, and controls receipts are recorded in
`production-evidence.json` and the task-local `.nl2repo/` run tree. The final
production bundle manifest is SHA-256
`2fdedb86d52649031a1ef2c80ed8ad01cfc0ab95eee44b0d72f74692779528ff`, with
canonical manifest digest
`e78ffad9f759755a74ddb3662cc645c1f7132f0efc79b9bb985a3bcfeff6522c`.

Using Harbor `0.21.0` and the locked Node toolchain, the trusted Oracle run
collected and passed 32/32 leaves with reward `1.0`; its verifier network
evidence reports `public_network_available=false`. A byte-identical repeat
production compile passed. Empty, stub, forgery, install-script, loader-hook,
call-hang, and offline controls all completed with verifier-owned reports and
no public network access. Independent review, model Agent Run, dataset
integration, and publication are outside this authoring lane.
