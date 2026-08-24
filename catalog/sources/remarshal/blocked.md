# `remarshal` static authoring audit — blocked

**Status: blocked evidence only.** This directory records a static audit of the
exact public upstream revision. It is not a task descriptor, public
instruction, Harbor bundle, verifier, Oracle, dependency bundle, private test
bundle, or publication approval. No upstream source/test/fixture bytes,
license copy, wheelhouse, Dockerfile, image, secret, reward, generated
projection, or shared catalog/dataset file is stored here.

The candidate is promising as a **CLI-first** repository-generation task, but
it cannot advance from this record. The complete source suite depends on a
binary fixture corpus and in-process Python objects that the current generic
JSON subprocess boundary cannot represent. A reviewed, binary-safe
Remarshal-specific CLI adapter and a content-addressed offline dependency
bundle are both still missing.

## Immutable source and MIT license evidence

The requested revision was resolved in a detached public checkout of
`https://github.com/remarshal-project/remarshal`:

- requested and resolved commit:
  `2300f5dfc39411020c86ade0d202aaea2897ccf0`;
- commit tree: `684fd7efc3f6af103f00300e9f2685a2cb14ef29`;
- parent: `3456252db0d4571171e082d6a3a4e5dec3b6c84c`;
- subject: ``fix(cli): fix `-p` eating next argv token (#68)``;
- author date: `2026-08-01T08:42:44+02:00`;
- commit date: `2026-08-01T07:13:10Z`;
- nearest tag description: `v2.1.4-0-g2300f5d`;
- GitHub reports the commit verification as valid;
- the detached checkout was clean, had no submodules, and contained 113
  tracked files.

Three independent, unprefixed `git archive --format=tar HEAD` invocations were
byte-identical:

- size: `327,680` bytes;
- SHA-256:
  `fe8563f10fdadd96820ecce004cb00a4d9777004d12f3019733872ddad7e041f`.

The archive digest is the source provenance observation for this audit. The
archive itself was temporary and was not copied into the catalog.

License evidence is internally and remotely consistent:

- tracked path: `LICENSE`;
- Git blob: `6cb98bd8cb1fb395aac73f15994ac39a587817df`;
- size: `1,069` bytes;
- SHA-256:
  `3f1052ac54eeaf2fa1340b2887ce9a854ddb3446eceecd7bc4b10fbd866abcfe`;
- text: the MIT License, copyright `2014-2020, 2023-2026 D. Bohdan`;
- `pyproject.toml` declares `license = { text = "MIT" }`;
- GitHub's license endpoint at the exact revision reports path `LICENSE`, the
  same blob and size, and SPDX identifier `MIT`.

The frozen `pyproject.toml` is 6,844 bytes, Git blob
`6b428883f101acfa0af91d6a677d5a4585c77387`, and SHA-256
`f56206e78c9ed5b0fce56b76ba9ce9cad838700680d01ba2770cc1449a32c02f`.
The frozen `uv.lock` is 67,437 bytes, Git blob
`51673183752faebfca98b6b653492af118606b60`, and SHA-256
`0a855403d08e2b43c59ef444730b89a911a042e6a25bda18cb91f6ed729fc1a0`.

The installed package metadata identifies distribution `remarshal`, version
`2.1.4`, Python `>=3.12`, and repository
`https://github.com/remarshal-project/remarshal`. The implementation consists
of 14 Python files under `src/remarshal`: 1,783 physical lines, 1,445 nonblank
lines, 1,402 nonblank/non-leading-comment lines, and 50,887 bytes. This size is
an audit observation, not a difficulty or publication decision.

## Package, format, and CLI surface

Remarshal is primarily an application. Its README explicitly applies semantic
versioning to the CLI and says use of the Python API is at the user's risk.
The package root re-exports the 27 names in `remarshal.main.__all__`, but the
upstream tests also import private helpers such as `_parse_command_line`.
Silently treating all upstream imports as a stable public-library contract
would therefore widen the intended product surface.

The declared format surface is:

| Direction | Formats |
| --- | --- |
| Input | `cbor`, `json`, `msgpack`, `toml`, `yaml`, `yaml-1.1`, `yaml-1.2` |
| Output | `cbor`, `json`, `msgpack`, `python`, `toml`, `yaml`, `yaml-1.1`, `yaml-1.2` |

The `python` format is output-only. CBOR and MessagePack inputs/outputs are
arbitrary bytes, not UTF-8 text. YAML defaults to 1.2, while explicit 1.1 and
1.2 decoding/encoding are supported. The application aims for lossless
conversion by default and rejects unrepresentable values; `-k`/`--stringify`
enables documented lossy string conversion for special keys, nulls, and
selected date-time values.

The wheel declares 31 console entry points: `remarshal` plus the 30 base
format wrappers formed from five input names (`cbor`, `json`, `msgpack`,
`toml`, `yaml`) and six output names (`cbor`, `json`, `msgpack`, `py`, `toml`,
`yaml`). All wrappers target `remarshal.main:main`. `python -m remarshal` also
executes the same main function.

CLI behavior visible at the locked revision includes:

- input/output format selection through `-f`/`--from` and `-t`/`--to`, wrapper
  command name, or recognized filename extensions;
- positional input/output paths or mutually exclusive `-i`/`-o` flags;
- `-` and omitted paths for standard input/output;
- key sorting, JSON/YAML indentation, TOML multiline thresholds, output width,
  wrapping/unwrapping, value-count limits, YAML aliases/styles/tags, and
  Starlark expression/file transforms with step/allocation limits;
- exit status 0 on success, 1 on operational/conversion failure, and 2 on
  command-line parsing failure;
- a hidden backward-compatible `-p`/`--preserve-key-order` no-op. This exact
  revision restores `action="store_true"`, so the flag no longer consumes the
  following positional path.

Temporary CPython 3.12 probes against the installed locked source observed:

- `remarshal --version` and `python -m remarshal --version` both returned
  `2.1.4` with status 0;
- `{"b":2,"a":1}` converted from JSON to JSON as
  `{"b":2,"a":1}\n`, preserving insertion order by default;
- the same input through `json2yaml` produced `b: 2\na: 1\n`;
- `json2cbor` produced the seven binary bytes
  `a2 61 62 02 61 61 01`;
- malformed JSON produced status 1 and the stable `Error: Cannot parse as
  JSON (...)` error prefix;
- omitting both detectable formats produced argparse status 2;
- an inline Starlark transform completed successfully; and
- passing `-p input.json output.toml` reached the attempted open of
  `input.json`, demonstrating that `-p` did not swallow the input token.

These are direct source/CLI observations, not hidden adapter tests or a frozen
behavior contract. Help coloring is terminal-sensitive through `termcolor` and
`colorama`; a final adapter must use a deterministic non-TTY/no-color
environment if help bytes are scored.

## Public fixture corpus and source tests

The upstream tree contains two pytest modules and a small but behavior-dense
public fixture corpus:

- `tests/` contains 79 files: `__init__.py`, two pytest modules, and 76 data
  fixtures;
- the repository root contributes six `example.*` fixtures used by the tests;
- the combined fixture corpus is 82 files and 10,224 bytes;
- extension counts are: three `.cbor`, 22 `.json`, three `.msgpack`, two
  `.py`, 19 `.toml`, 30 `.yaml`, two `.yml`, and one extensionless malformed
  input;
- the six explicitly binary format files are `example.cbor`,
  `example.msgpack`, `tests/bin.msgpack`, `tests/date.cbor`,
  `tests/datetime-tz.cbor`, and `tests/datetime-tz.msgpack`;
- a canonical audit manifest made from each relative path, byte size, and
  file SHA-256 has SHA-256
  `43b5139437ad4fcb3b5d0b83a859ea9fa59ca061532891ed38d6927200c778c0`.

No fixture bytes or manifest file are included here. The digest only records
what was inspected in the public temporary checkout.

The corpus covers the cross-format example matrix, malformed input, binary
values, YAML aliases and alias expansion, the YAML "billion laughs" case,
YAML 1.1/1.2 interpretation, null and special map keys, ordering/sorting,
wrapping/unwrapping, TOML multiline arrays and 1.1 syntax, dates/times,
formatting styles and widths, YAML tags, and Starlark transforms and resource
limits.

The source tests do not invoke the installed commands as isolated
subprocesses. They import candidate modules directly, call
`remarshal.remarshal`, call private argument-parsing helpers, create Python
callbacks and compiled Starlark callables, pass bytes/date/time/custom option
objects, use temporary files, and compare exact binary or textual output. The
suite therefore cannot be moved unchanged into trusted root pytest under the
repository's separate-verifier policy.

In a temporary lock-backed environment, collection was stable across three
runs:

- interpreter: CPython `3.12.11`;
- host: Fedora 44, Linux x86-64, glibc 2.43;
- command shape:
  `python -m pytest --collect-only -q -p no:cacheprovider`;
- collected nodes: 196 (`141` from `test_remarshal.py`, `55` from
  `test_starlark.py`);
- stable ordered node-list SHA-256:
  `0e23378e6b4b46e8f74f98313b3f8fc7efb7d3d65dcf5272d53286a9256c511e`.

Three direct source baselines in that same temporary environment each passed
all 196 tests with no failure, error, or skip. Pytest reported 1.85 s, 1.86 s,
and 1.89 s; the three JUnit files each contained 196 passing testcase elements
and shared testcase/status digest
`ced60f68755a6ccc92d6567d9b267f4bd331ef63a4e77903f9b2e8368a3eb051`.
These runs establish only a local source baseline. They are not Harbor Oracle
jobs, do not produce `valid=true` grading, and do not freeze a future adapted
suite's denominator.

A temporary `uv build` probe produced a 26,714-byte pure-Python wheel and a
43,660-byte sdist. The wheel had 20 archive entries, all 31 console scripts,
and no tests. The sdist had 104 entries and intentionally included all 79
`tests/` entries plus the six root examples. The probe used host cache/network
state and is not an offline or reproducible build claim. In particular, the
upstream sdist must not be passed to an agent or reused as a public candidate
artifact because it carries the complete public source-test corpus.

## Python 3.12 and the eight-package runtime closure

`pyproject.toml` requires Python `>=3.12`; tox names Python 3.12, 3.13, and
3.14 environments. The static audit used CPython 3.12.11 because the requested
task boundary calls for Python 3.12. No Docker image was built or run, so the
repository's standard `python:3.12-slim` image digest was not revalidated for
this candidate.

The project declares exactly eight runtime requirements. The committed uv
lock resolves the Python 3.12 runtime graph to exactly these eight packages,
with no transitive dependency edges recorded for any of them:

| Distribution | Locked version |
| --- | ---: |
| `cbor2` | `5.9.0` |
| `colorama` | `0.4.6` |
| `ruamel-yaml` | `0.19.1` |
| `starlark` | `0.5.0` |
| `termcolor` | `3.3.0` |
| `tomli` | `2.4.1` |
| `tomlkit` | `0.15.0` |
| `u-msgpack-python` | `2.8.0` |

`uv lock --check` succeeded. A runtime-only `uv export --frozen --no-dev
--no-emit-project` emitted all eight exact versions with SHA-256 hashes. The
lock contains compatible CPython 3.12 Linux x86-64 wheels for `cbor2` and
`tomli` and universal wheels for the other six packages. Choosing the locked
manylinux x86-64 variants yields 839,660 compressed wheel bytes before adding
any build or verifier tooling.

This is lock evidence, not an offline dependency artifact:

- `uv.lock` has 26 package records because it also carries the project,
  optional development roots, and their transitives;
- the PEP 517 backend requirement is the range `poetry-core>=2.0`, but
  `poetry-core` is absent from `uv.lock`;
- the temporary `uv sync --frozen --extra dev` succeeded only with available
  host cache/network state and installed 26 packages;
- an empty-cache `uv sync --frozen --no-dev --offline` failed immediately
  because the locked `cbor2==5.9.0` wheel was unavailable; and
- there is no approved `requirements.lock.txt` plus wheelhouse artifact for
  the compiler to install with `--no-index --require-hashes`.

A future production dependency bundle must contain the eight runtime wheels
and every approved build requirement needed by the candidate install protocol.
It must decide and pin the build-backend policy rather than treating the
unlocked `poetry-core>=2.0` range as closed. The temporary host cache and build
outputs must not be promoted into that artifact.

## JSON/CLI separate-verifier analysis

The current generic Python candidate boundary is not sufficient for the
complete Remarshal behavior:

1. `candidate_client.call` accepts JSON arguments and the child serializes the
   return value with `json.dumps`. It cannot faithfully transport raw bytes,
   `datetime.date`/`time`/`datetime`, `TaggedValue`, format option dataclasses,
   compiled transform callables, codec instances, or other rich objects used
   by the source suite. `decode()` often returns such values and `encode()`
   returns bytes.
2. `run_module` accepts only text stdin, and candidate stdout/stderr are
   decoded as UTF-8 with replacement. This corrupts arbitrary CBOR or
   MessagePack output and cannot supply arbitrary binary input.
3. `run_console` does not currently accept stdin at all. It can identify one
   installed entry point, but cannot exercise normal stdin-driven conversion.
4. Neither operation offers a bounded child-owned fixture directory or a way
   to return output-file bytes. Passing trusted host paths would violate the
   hidden-test boundary and create an unintended file-reading surface.
5. The upstream tests are in-process and include callbacks/state that cannot
   simply be asserted by trusted pytest importing candidate code.

A task-specific **binary-safe CLI scenario adapter is feasible**, but choosing
it is an explicit scope/API decision and no such adapter exists in this task.
A reviewed adapter should, at minimum:

- accept only an allowlisted entry point (`remarshal` and the 30 declared
  wrappers), a bounded argv list, and either base64 stdin bytes or a bounded
  map of relative fixture paths to base64 bytes;
- create all input, output, and `--starlark-file` paths inside an untrusted
  child-owned temporary directory and reject absolute paths, `..`, arbitrary
  environment mutation, shell commands, and ambient executable access;
- invoke exactly one installed console entry point in the candidate child;
- capture return code, stdout, stderr, and requested output files as exact
  bytes and return them as bounded base64 fields in a JSON response;
- fix non-TTY/color, locale, and other process settings needed for deterministic
  CLI observations;
- leave expected bytes, collection, JUnit, and grading under root/trusted
  ownership; and
- retain the existing per-call process, time, output, process-count, and
  cumulative-budget limits.

That adapter can preserve the application's text and binary conversion
semantics without importing candidate code into trusted pytest. It would not,
by itself, establish parity for the unstable Python library surface. If a
future task intends to score `format_options`, codec classes, `TaggedValue`,
custom transforms, or other live objects directly, it needs separately
reviewed child-side scenario operations and a public contract for those
objects. The owner must approve CLI-only versus CLI-plus-library scope before
an instruction or private adapter suite is authored.

## Blockers and reopen conditions

Keep `remarshal` blocked. The current blockers are:

1. There is no approved binary-safe Remarshal CLI adapter or behavior mapping
   from the 196 direct-import source nodes to a separate-verifier suite.
2. There is no content-addressed offline dependency artifact. The eight
   runtime packages are hash-locked, but their wheel bytes are not bundled and
   the Poetry build backend is not locked in the committed project lock.
3. The local 196-node result is a source baseline, not a frozen denominator for
   an adapted private suite in a final immutable Python 3.12 environment.
4. No public instruction/task descriptor has been approved for the necessary
   CLI-only versus CLI-plus-library scope choice.
5. No private test/fixture bundle, allowlisted command-plan artifact, Oracle
   bundle, final image validation, negative controls, or review records exist;
   those assets were intentionally outside this static-only assignment.

To reopen, first approve the measured API surface and versioned adapter
contract. Then materialize content-addressed private test/command artifacts and
a complete hash-locked wheelhouse including the chosen build backend; validate
the exact Python 3.12 image offline; adapt and recollect the approved suite;
and only then run three stable Oracle jobs followed by empty, stub, forgery,
and offline controls and the required reviews.

## Static validation record

The audit used only public source material and temporary paths outside this
task directory. It performed detached source/commit/license checks, three
source archives, package and lock parsing, AST/test/fixture inventory, Python
3.12 lock-backed collection and direct source baselines, representative CLI
probes, a temporary package build, an empty-cache offline negative probe, and
inspection of the repository's generic candidate client/runner.

No Docker or Harbor command was run. No Oracle, control, model trial, private
artifact materialization, shared catalog edit, source/test/fixture copy, or
publication action was performed. No tests were added or modified.
