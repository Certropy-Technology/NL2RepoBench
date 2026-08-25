# `sqlparse` production authoring provenance

## Frozen source

- Upstream: `https://github.com/andialbrecht/sqlparse`
- Revision: `a801100e9843786a9139bebb97c951603637129c`
- Commit tree: `dad67975b7a2f2bfa17ab858db042de25940dfd6`
- Commit date: `2025-02-16T10:19:00+01:00`
- Subject: `Code cleanup.`
- Submodules: none.
- Unprefixed `git archive --format=tar <revision>` size: 399,360 bytes.
- Archive SHA-256: `215f55a40819101b2ca1d0c2c983ac9182539c6c32fc8bcb93a889b2bfdfd3ed`.
- Three source package directories (`sqlparse/`, `sqlparse/engine/`, and
  `sqlparse/filters/`) contain 4,023 physical Python lines at this revision.

The local Oracle bundle contains that exact archive plus a short `solve.sh`
that verifies the archive SHA-256 before extracting it. It performs no network
fetch and does not modify functional source.

## License

The frozen `LICENSE` is the three-clause BSD text, matching the upstream
classifier `License :: OSI Approved :: BSD License`.

- SPDX: `BSD-3-Clause`
- `LICENSE` SHA-256:
  `c1938235b80d39e93138eae89edc3af67e18ecbc40d266529fa57b2dce426310`

## Environment and dependencies

- Runtime image: `python:3.12-slim` at
  `sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
  (`linux/amd64`, CPython 3.12.14).
- The project declares no runtime dependencies.
- Build backend: Hatchling.
- The private requirements lock was generated with
  `uv pip compile --generate-hashes --no-annotate --no-header` from
  `hatchling==1.27.0`. It freezes Hatchling, Packaging, Pathspec, Pluggy, and
  Trove Classifiers and includes package-index hashes. No wheelhouse or vendored
  dependency bytes are part of the task.
- Candidate and verifier runtime are `no-network`; dependencies are installed
  only during Docker build.

## Bounded verifier contract

The private `custom-json-v1` bundle has one trusted parent (`run.py`) and one
child-side observation adapter (`adapter.py`). The parent launches the adapter
as UID 10001 in a fresh subprocess for each scenario, applies address-space,
CPU, file-size, descriptor, and process limits, kills residual UID 10001
processes, and compares JSON observations with trusted expected values. Only
the child imports the candidate package. The trusted parent emits 26 unique
leaves consumed by the generic fixed-denominator grader.

Frozen scenario IDs:

```text
api-surface
format-case
format-invalid-options
format-layout-options
format-operators
format-reindent
format-string-output
format-whitespace-comments
function-parameters
identifier-list
identifier-metadata
lexer-customization
lexer-inputs
nested-groups
parse-preservation
parsestream-behavior
split-basic
split-comments
split-dollar-quoted
statement-types
token-helpers
token-hierarchy
tokenize-comments-placeholders
tokenize-literals
tokenize-simple
where-comparison
```

Each leaf maps to a named section or exact example in `instruction.md`. The
contract deliberately excludes the CLI and the unbounded remainder of upstream
dialect/regression behavior; it does not claim full upstream pytest parity.

## Production gate results

Harbor 0.21.0 executed the compiled production bundle without
`--allow-incomplete`. The terminal receipts are hash-bound in
`production-evidence.json`:

- Oracle: valid, collected 26, passed 26, reward 1.0;
- empty/nop: valid model-class installation failure, reward 0.0;
- importable stub: valid, collected 26, passed 0, reward 0.0;
- forged reward/test-path attempt: valid, collected 26, passed 0, reward 0.0;
- Oracle, empty, stub, and forgery verifier network probes all reported
  `public_network_available=false`.

The lifecycle is therefore `controls-passed`. Blind review, traceability review,
and model pilots were explicitly outside this authoring run and remain pending.

## Controls

Task-local `stub.sh` creates an installable package with the right name/version
but no parser modules. `forgery.sh` adds attempted candidate-owned reward files
and writes to trusted paths only when permissions incorrectly permit it. Empty,
stub, forgery, and verifier offline behavior are required before lifecycle may
advance beyond `packaged`.
