# `commander` Blocked Audit

Status: **blocked**. This bounded audit is paired with a parseable blocked
descriptor and hashed remediation evidence. It contains no hidden tests,
Harbor runtime, verifier, Oracle, dependency cache, or shared catalog/index
edit; `catalog/tasks/commander/` remains absent.

## Candidate Identity

- Task candidate: `commander`.
- Upstream repository: `https://github.com/tj/commander.js`.
- Requested source path: `tj/commander.js`.
- Resolved revision: **unknown**. The bounded checkout does not contain the
  source tree or a trusted full commit SHA. No branch, tag, short SHA, or
  inferred release is recorded as a substitute.
- Source archive: **unknown**. No content-addressed archive, archive member
  list, archive digest, or reproducible archive command is available in this
  run.

The candidate must remain blocked until an immutable full commit and its
content-addressed source archive can be independently reproduced.

## License and Distribution

The project is recorded as **MIT** at the project level, consistent with the
requested upstream candidate. The exact `LICENSE` file, license text/hash,
copyright notices, package metadata, and archive contents were not available
for verification in this bounded run. MIT compatibility and notice
preservation therefore remain release blockers rather than publication proof.

The eventual archive must be reviewed for vendored code, fixtures, examples,
generated files, and any additional notices before it is used as a task
source. Runtime package contents and source-distribution contents must not be
treated as interchangeable without a recorded boundary and digest.

## Proposed Runtime Scope

The candidate scope is the `commander.js` CLI parser on **Node.js 22**, with
both CommonJS and ESM entry points considered part of the packaging contract.
The intended behavior boundary is limited to public command, argument,
option, parsing, help/version, output, error, and export behavior exposed by
the package. Exact APIs, signatures, defaults, supported Node versions,
entry-point conditions, and release-specific behavior remain unverified until
the immutable source is available.

The audit does not authorize expanding the task to unrelated documentation,
examples, build tooling, or private implementation details. CJS/ESM parity,
`package.json` exports, executable resolution, and CLI behavior must be
covered explicitly if this candidate is reopened.

## Lock and Offline Closure

Dependency and build closure: **unknown blocker**.

- No exact `package-lock.json`, `npm-shrinkwrap.json`, or equivalent lock was
  inspected.
- No package-manager choice, registry snapshot, artifact URL, integrity hash,
  or transitive dependency inventory is frozen.
- Node 22 base image, npm version, native build tools, and image digest are
  unknown.
- No offline npm cache or content-addressed dependency bundle is present.
- The CJS/ESM package export and executable resolution paths have not been
  replayed from a clean offline environment.

A future package must prove that install, build, import, and CLI execution
work without network access from the exact lock and preloaded artifacts. A
successful online install would not close this blocker.

## Tests and Verifier Risks

Test closure: **unknown blocker**. The upstream test files, test command,
framework/version, collection count, fixtures, environment variables, and
expected failure/skip treatment were not available in this bounded run.
Accordingly, there is no frozen denominator, traceability map, Oracle result,
or evidence that tests represent the proposed CJS/ESM CLI parser scope.

Specific risks to resolve before authoring:

- CLI tests may depend on subprocess timing, shell quoting, temporary files,
  current working directory, or platform-specific streams.
- Help, version, error, and exit-code assertions may be sensitive to Node/npm
  versions or terminal detection.
- CJS and ESM tests may exercise different package entry points or loader
  behavior, making a single import-only adapter incomplete.
- Tests may use network access, mutable fixtures, generated snapshots, or
  ambient environment state.
- Collection errors, skipped tests, retries, and subprocess failures need a
  structured verifier contract and fixed denominator rather than console
  parsing.

## Candidate Subprocess Contract

The generic candidate subprocess boundary is **not validated**. Before this
candidate can leave `blocked`, define and probe how the verifier supplies the
command, arguments, stdin, environment, and working directory, and how it
captures stdout, stderr, exit status, signals, timeouts, and output encoding.
The contract must distinguish a candidate CLI failure from setup, dependency,
Node-loader, or verifier infrastructure failure. Shell invocation and quoting
must be avoided or specified precisely; CJS and ESM execution must each be
tested in the same isolated contract.

## Reopen Gates

Reopen only after all of the following are recorded:

1. Full immutable commit SHA, commit metadata, clean source lock, archive
   member list, and repeatable archive SHA-256.
2. MIT license bytes and notices reviewed against the exact package/archive
