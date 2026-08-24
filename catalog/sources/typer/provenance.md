# typer Remediation Evidence

Exact revision `9a7b2e83f6b62c750d6026b0de9ebf2026a8b8fa`, resolved by detached
checkout, not remote HEAD. Unprefixed `git archive` digest
`sha256:4713273f314d75895e287e1dfed01cd97d1d1c6ec643ebb9e379ff5e80dda71b`,
2,723,840 bytes, byte-identical to the digest recorded in `blocked.md`.
No submodules.

## License

Project metadata is MIT (`LICENSE`,
`sha256:58992cebcf8dfb6e40c4e2112ed12126c243666dca3912a3d78b7ecac4859d49`).
The runtime vendors an adapted Click 8.3.1 under `typer/_click/` whose
BSD-3-Clause notice (`typer/_click/LICENSE.txt`,
`sha256:9a8ad106a394e853bfe21f42f4e72d592819a22805d991b5f3275029292b658d`) is
carried inside the frozen source archive used by the Oracle, so both notices
travel with every artifact. `task.toml` records `license_spdx = "MIT"` because
the schema accepts a single expression; the vendored notice is documented here.
The public instruction has a Licensing section requiring the adapted notice to
be retained.

## Platform and dependency closure

The blocked audit's open platform question is resolved by narrowing to a single
policy: Linux `x86_64`, Debian 12, CPython 3.12.14. Windows console and the
upstream lowest/highest resolution matrix are explicitly out of scope, so
`colorama` is not in the closure.

The wheelhouse is hash-pinned and installed at image build time, then exposed to
the candidate at `/opt/candidate-dependencies/site`:
`annotated-doc==0.0.4`, `rich==15.0.0`, `markdown-it-py==4.0.0`, `mdurl==0.1.2`,
`pygments==2.20.0`, `shellingham==1.5.4`, `pdm-backend==2.4.9`,
`setuptools==80.9.0`, `wheel==0.45.1`. `pdm-backend` is required because the
generic candidate install runs `pip install --no-deps --no-build-isolation`,
which the blocked audit flagged as an unpinned build requirement absent from
`uv.lock`.

## Scored slice

The blocked audit's core objection was that 612 `invoke(...)` call sites build
live `Typer` objects and typed Python callbacks inside pytest, which cannot
cross a JSON boundary. This remediation does not try to carry Python objects
over JSON. Instead the private child adapter owns an allowlisted fixture table
(`typer-fixture-v1`, nine fixtures) and constructs every callback, annotation,
enum, option/argument metadata object, nested application and `CliRunner`
*inside the untrusted child*. The JSON request carries only a fixture name, an
argv list of strings, optional stdin text, and environment values restricted to
the single name `SLICE_REGION`. No callable, import path, filesystem path or
Python source crosses the boundary. Trusted code never imports candidate
modules.

23 frozen leaves cover the API surface plus scalar conversion, required options,
env-var options, enum member conversion, list/fixed-tuple/optional containers,
UUID/datetime/Path conversion, group callbacks and renamed commands, nested
`add_typer` routing, prompt stdin with separate stderr, `typer.Exit` codes,
uncaught callback exceptions, and four usage-error paths.

Rich renders errors inside a width-dependent panel, so the five error leaves
assert exit code, stream placement, empty stdout and message fragments rather
than frozen panel bytes. All 18 ordinary-output leaves are compared byte for
byte. The child pins `COLUMNS=80`, `TERM=dumb`, `NO_COLOR=1`, `LC_ALL=C.UTF-8`,
`TZ=UTC` and `PYTHONHASHSEED=0`.

`frozen_total = 23` comes from the verifier's own collection, and
`collection_mismatch = "fail"`.

## Evidence

- Local direct-adapter run against the frozen source: 23/23, reward 1.0.
- `uv run nl2repo harbor compile` succeeded; bundle manifest written.
- Generic compiled Harbor Oracle: `valid=true`, `collected=23`, `passed=23`,
  `failed=0`, `errors=0`, `collection_errors=[]`, `pytest_exit_code=0`,
  `reward=1.0`, at
  `jobs/2026-08-24__16-22-33/typer__T5S3RqB/verifier/grading.json`.
- `uv run nl2repo task lint-network`: 0 errors, 0 warnings, explicit policy
  present. The Oracle takes its source from the private bundle, so the
  `oracle-source-acquisition` GitHub-fetch failure mode does not apply.
- Hidden assets stay private: the compiled agent image contains no adapter,
  report writer or expected bytes.

Outstanding: empty/stub/forgery controls, blind and traceability review, pilot.
No model run was started.

## Integrated generic evidence

- Oracle: `valid=true`, `23/23`, reward `1.0`, at
  `.nl2repo/runs/oracle/typer-custom-compiled-current/2026-08-24__16-54-27/typer__RjJQ2jB/verifier/grading.json`.
- Empty: reward `0.0`, candidate-install failure classified as `model`, at
  `.nl2repo/runs/controls/typer-custom-empty-v1/2026-08-24__16-49-49/typer-empty__n73Ghfi/verifier/grading.json`.
- Stub: reward `0.0`, `23/23` leaves failed, at
  `.nl2repo/runs/controls/typer-custom-stub-v2/2026-08-24__16-44-58/typer-stub__RPVoScG/verifier/grading.json`.
- Forgery: reward `0.0`, `23/23` leaves failed, at
  `.nl2repo/runs/controls/typer-custom-forgery-v2/2026-08-24__16-44-58/typer-forgery__mfQAF4t/verifier/grading.json`.
- Offline: `task.toml` declares no-network for both agent and verifier and an
  explicit source-fetch-forbidden policy.
