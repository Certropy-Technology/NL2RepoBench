# rpds-py authoring audit

Mode: `author-one`.

The assigned source was cloned from `https://github.com/crate-py/rpds` and checked
out at commit `0c6a30b4016cd3738bc0dd19caba1b004bbee15c`. The commit tree is
`f9e00874d6cdfacc1911124670df515806ba428e`; the normalized source archive is
`sha256:b6f7619d8b389a078a84f36b4d84efba056482524f18a6a94b2781d2d1a59d1e` and
`LICENSE` is MIT with digest
`sha256:314e4e91be3baa93c0fb4bccc9e4e97cd643eb839b065af921782c2175fe9909`.

The package is a single Rust/PyO3 `cdylib`; it has no Python fallback. The committed
Cargo lock resolves 15 registry packages, including `pyo3 0.29.2`, `rpds 1.2.1`,
`archery 1.2.3`, and their transitive dependencies, with no git sources. An exact
CPython 3.12.11 native wheel was built with maturin 1.9.6 and Cargo offline; all
132 upstream pytest tests passed.

The task is blocked truthfully because the current Python Harbor compiler supports
hash-locked pip dependency installation but has no Rust/Cargo vendor build contract.
The current projection boundary also forbids placing the native reference wheel in
the public generated task. Unblocking requires a reviewed Rust/native compiler lane
that injects a private digest-bound Cargo closure and private native Oracle payload,
then a new separate verifier, fixed denominator, compile, Oracle, and control matrix.
