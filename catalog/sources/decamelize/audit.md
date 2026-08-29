# Decamelize Authoring Audit

## Freeze

- Upstream: `https://github.com/sindresorhus/decamelize`
- Revision: `365e2e909c93c8a5e7c9398523290ba0b35a3a93`
- License: MIT, from upstream `license`
- Raw `git archive --format=tar <revision>` SHA-256:
  `4bc589382527a52de984f5768d6eece961d0a532439d894cdd4e2aef7a82696e`
- Codeload archive SHA-256:
  `8fe6e3ec9a058ca9a0cf7a944058f4409dcf3c22b2a15cdc8b892e46163c5e55`
  (6,263 bytes), verified during Oracle authoring.

## Baseline and environment

The frozen tree has 13 tracked files, one ESM runtime module, one declaration
file, and one AVA test file. The package has no runtime dependencies. The
production runtime is Node `24.19.0` with npm `11.17.0`, Debian bookworm,
linux/amd64, glibc, and the locked Node image recorded in `task.toml`.

## Scope decision

The public API is a single default function. The production verifier uses a
separate JSON child process and 24 leaf assertions. It does not expose the
upstream test runner or reference implementation to the model. Performance
thresholds and TypeScript-only checks are provenance evidence, not scored
behavior.

## Dependency/build remediation

The candidate closure is a root-only npm v3 lock and an empty npm cache. The
Oracle bundle fetches only the exact revision, checks its archive digest, and
creates a scripts-free package manifest and matching lock from the verified
runtime/declaration files. Agent and verifier phases remain no-network.
