# `normalize-url` Provenance

- Upstream: `https://github.com/sindresorhus/normalize-url`
- Frozen revision: `863d275c21d6411a7494b8f728a515633bc01d84`
- Source archive SHA-256: `sha256:6c7fd8315e3feae64c76202281560a3b4a27f807d736371c783d921049ab5cfe`
- License: MIT; `license` SHA-256: `sha256:5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Upstream clone was clean at the frozen revision. The baseline `npm test` exited 0,
  with 33 AVA tests passing; the upstream lint emitted warning-only findings.

The production task uses Node `24.19.0` and npm `11.17.0` on `linux/amd64` with the
digest-pinned Node base image in `task.toml`. Candidate and verifier execution use
`no-network`; only the trusted Oracle run receives a run-scoped `github.com`
authorization. The Oracle script checks both the resolved commit and the archive
SHA-256 before extracting the reference source.

Private tests, command plan, npm closure, and Oracle script are stored only in the
task-local CAS under `.nl2repo/artifacts/private`; the public source contains no
private test bytes.
