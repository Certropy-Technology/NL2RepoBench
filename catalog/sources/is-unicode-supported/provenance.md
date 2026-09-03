# `is-unicode-supported` Authoring Provenance

Status: `awaiting-agent-run`. This source is locally compiled and verified;
the separate model Agent Run, independent review, and publication are outside
this authoring lane.

## Frozen Source

- Upstream: `https://github.com/sindresorhus/is-unicode-supported`.
- Revision: `e0373335038856c63034c8eef6ac43ee3827a601` (`2.1.0`), tree
  `cc51631d242a2da7ecfd5968ba6451323e7ed38a`, committed
  `2024-09-09T13:25:41+07:00`.
- `git archive --format=tar <revision> | sha256sum`:
  `f15b5aac5c7f5e331c91310d01ac6c73efb36686bd9ae87c47847dbf6978bc38`.
- License: MIT; `license` SHA-256:
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`.
- The detached checkout was clean and contains no submodules.

The package has thirteen tracked files, one default ESM export, no runtime
dependencies, and development-only `ava`, `tsd`, and `xo` ranges. Its original
test command cannot run from the frozen checkout without fetching those
development dependencies, so the task uses a private deterministic `node:test`
collection over the documented public API instead of vendoring upstream tests.

## Contract And Boundary

The only scored API is `isUnicodeSupported(): boolean`. The private adapter
spawns a candidate-owned Node process, supplies the documented terminal state,
and returns a bounded JSON result. It is needed because platform and environment
state are process-global and cannot be observed safely by importing candidate
code in the trusted verifier process. The 20-leaf collection covers the Linux
console exception, ordinary non-Windows behavior, every supported Windows
marker, exact matching, empty/unrecognized markers, and state changes between
calls. See `traceability.md` for the public-to-private mapping.

## Environment And Closure

- Runtime: Node `24.19.0`, npm `11.17.0`, Linux amd64/glibc, Debian Bookworm.
- Base image: `docker.io/library/node@sha256:65932751ed4073ed02f5c04e494e4b2572a891b7dbea0568a863dc80341bf848`.
- The locked OpenHands agent tag is
  `nl2repobench/openhands-sdk-fork:930e9b1da-bookworm`, expected by the shared
  toolchain as `sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f`.
  This daemon resolves that tag to
  `sha256:3b9288ec42f69da761f0aedb9a72c6888376e9395f9122192aca67e81d913c79`.
  The mismatch is recorded for integrator revalidation before any model run;
  it is not silently relocked in this task lane.
- Candidate dependency closure: private npm v3 archive
  `sha256:35899cb523c2a7a07e0639c5df87900c354a16eb0a9f53ddb74808ee18411fdd`.
  It contains only the immutable root `package-lock.json` and an empty cache,
  which is complete because the package has no runtime dependencies.
- Candidate and verifier runtime policies are `no-network`; lifecycle scripts
  are ignored. The Oracle source fetch is private and requires
  `ca-certificates=20250419~deb12u1` and `git=1:2.39.5-0+deb12u3`, declared in
  `environment.system_packages` and checked by the generated agent image.

The generated separate verifier was built successfully from the final private
artifacts. Its local no-network Oracle-equivalent run passed all 20 leaves with
reward `1.0`. The Oracle source script fetched the pinned Git revision, checked
the archive SHA-256, stripped development-only source files, generated the
root-only lock, and then passed the same no-network verifier.

## Controls

The final compiled-bundle controls all completed through the separate verifier:

| Control | Result |
| --- | --- |
| empty | permitted `candidate-installation-failed`, 0/0, reward 0.0 |
| stub | 0/20, reward 0.0 |
| forgery | 0/20, reward 0.0; verifier-owned receipt prevailed |
| install-script | permitted `candidate-installation-failed`, 0/0, reward 0.0 |
| loader-hook | 0/20, reward 0.0 |
| offline | 0/20, reward 0.0; verifier network receipt has public network unavailable |
| call-hang | bounded `candidate-call-failed`, 0/0, reward 0.0 |

Receipt paths and SHA-256 values are in `production-evidence.json`. They are
task-local `.nl2repo` material and are not public test or Oracle bytes.
