# `simple-parsing` Authoring Pilot Audit

Status: **blocked**.  This directory records a public, task-local authoring
pilot and reproducibility evidence only.  It is not a production Harbor task.
No hidden tests, private test bytes, Oracle solution, Docker image, secret,
shared index, or verifier bundle is included here.

## Candidate identity and source provenance

The candidate entry was read from `reports/github-package-candidates.v1.json`:

- `task_id`: `simple-parsing`
- upstream: `https://github.com/lebrice/SimpleParsing`
- requested revision: `7a706bee8b258b548cb979c7321c1ba0cf8413e6`
- candidate license declaration: SPDX `MIT`
- candidate category/difficulty: `typed-cli` / `medium`
- discovery recommendation: `freeze-pilot`
- recorded risks: argparse compatibility and nested-dataclass semantics

A detached checkout was made from the upstream URL and resolved to the exact
requested full SHA.  The checkout was clean before and after validation.
The commit is dated `2026-07-27T17:15:46-04:00`, has subject
`Fix #322 (Union[Literal, ...]) (#325)`, and tree
`16ac6ad3094304aa650198f0c814f585ab7eb0fc`.

The immutable source evidence obtained from that checkout is:

- unprefixed `git archive --format=tar HEAD`: 1,228,800 bytes,
  SHA-256 `ad8a0b99dc079b03ba3091671f451c7c593aff01371a6c7313777fd120445b2f`;
- `LICENSE`: 1,074 bytes, Git blob
  `2a3f2a4ab0a044859f260e7961889deaa7144b4c`, SHA-256
  `885f25a54cc4c95e415b4032bff965a8a2a76bed1ad774da683914ed29c00fbf`;
- the license text is the standard MIT permission, warranty, and liability
  notice and agrees with the candidate's SPDX declaration;
- `pyproject.toml`: SHA-256
  `8f3bb967d403b9505dd03c54e67e38a5a455cd48598d3ef1708352a5e6b4fbce`;
- `uv.lock`: SHA-256
  `fe19a56213dcff64035dae05ced014bf2fbce1440d75dca32bb4d64d9efb8d4d`;
- `requirements-test.txt`: SHA-256
  `30ef1628c9b999c89742876f4d420faf7b52563a7e8d8f0d015e4e0aaf48d2e4`.

The `requirements-test.txt` digest above is retained as source evidence; the
file is not treated as a production lock because its requirements are
unversioned (see the dependency section below).

## Package metadata and size

`pyproject.toml` was parsed with Python `tomllib` rather than inferred from
README text:

- distribution name: `simple-parsing`;
- dynamic version resolved from the tag at this commit: `0.1.9` (`v0.1.9`);
- `requires-python`: `>=3.9`;
- build backend: `hatchling.build` with build requirements `hatchling` and
  `uv-dynamic-versioning`;
- runtime requirements: `docstring-parser~=0.15` and
  `typing-extensions>=4.5.0`;
- optional extras: `yaml` (`pyyaml>=6.0.2`) and `toml`
  (`tomli>=2.2.1`, `tomli-w>=1.0.0`);
- package layout: flat `simple_parsing/`, with no console-script entry point.

A source wheel was built without changing the checkout:

- `simple_parsing-0.1.9-py3-none-any.whl`, 113,700 bytes;
- wheel SHA-256 `7ac87119116434ee15dadb404938cbc9904e0ffed2a9cc4ac1ab57794369b990`.

The wheel metadata independently reports the same version, Python requirement,
runtime requirements, and optional extras.

LOC was measured from tracked Python source files using physical lines,
nonblank lines, and noncomment lines.  The production package excludes the two
`*_test.py` modules that live under the package:

| tree | files | physical | nonblank | noncomment |
| --- | ---: | ---: | ---: | ---: |
| `simple_parsing/` production | 33 | 9,962 | 8,224 | 7,447 |
| in-package `*_test.py` | 2 | 404 | 308 | 292 |
| `test/` suite | 76 | 11,011 | 8,637 | 8,227 |
| `examples/` | 40 | 2,894 | 2,277 | 2,079 |

The candidate's `medium` label is preserved in `task.toml` because it is the
label in the candidate manifest.  Under the original NL2RepoBench LOC bands,
9,962 production physical lines would fall in the `hard` band; the dataset
owner must choose and document one classification policy before publication
rather than silently presenting the two schemes as equivalent.

## Public API inventory and semantic review

The package has five explicit `__all__` declarations containing 51 entries and
44 unique names.  The top-level `simple_parsing.__all__` contains 26 names,
listed in `instruction.md`.  A separate AST inventory over the 33 production
modules found 43 unique public class names and 132 unique public function names
(175 unique names total; overload declarations were collapsed, and helper
internals are not automatically promoted to the supported API).

The reviewed user-facing seams are:

- `simple_parsing.ArgumentParser`, `parse`, and `parse_known_args`;
- `ArgumentGenerationMode`, `NestedMode`, `DashVariant`,
  `ConflictResolution`, `ParsingError`, and `SimpleHelpFormatter`;
- field constructors in `simple_parsing.helpers.fields` (`field`, `choice`,
  `list_field`, `dict_field`, `set_field`, `mutable_field`, `flag`, `flags`,
  `subgroups`, and `subparsers`);
- serialization in `simple_parsing.helpers.serialization` (`Serializable`,
  `SerializableMixin`, `FrozenSerializable`, `SimpleSerializable`,
  `YamlSerializable`, `to_dict`, `from_dict`, `load`, `save`, and JSON/YAML
  variants);
- `replace`, `replace_subgroups`, `config_for`, and `Partial`;
- hyperparameter helpers and models in `simple_parsing.helpers.hparams`;
- docstring helpers and the documented wrapper enums.

The public specification records signatures and behavior without copying
function bodies or upstream assertions.  The source review specifically
confirmed that dataclass registration recursively constructs nested values,
keeps ordinary argparse options on the same namespace, and preserves field
order.  It also confirmed lazy/optional handling for YAML, TOML, NumPy, and
PyTorch format paths; basic import and JSON behavior do not require those
optional features.

## Argparse and nested-dataclass evidence

The focused source tests cover the parser and nested behavior through the
following upstream modules: `test_base.py`, `test_multiple.py`,
`test_default_args.py`, `test_bools.py`, `test_choice.py`, `test_conflicts.py`,
`test_custom_args.py`, `test_fields.py`, `test_generation_mode.py`,
`test_lists.py`, `test_optional.py`, `test_optional_subparsers.py`,
`test_positional.py`, `test_subgroups.py`, `test_subparsers.py`,
`test_tuples.py`, and the complete `test/nesting/` subtree.  The focused run
collected 706 items and produced:

- 638 ordinary passes,
- 9 xpasses,
- 9 ordinary skips,
- 50 xfails,
- 0 unexpected failures or collection errors.

A separate smoke check against the locked CPython 3.12 environment observed:

```text
parse_nested Config(inner=Inner(count=7))
reused_dataclass 2 3
subgroup_a A(number=9)
subgroup_b B(text='hello')
```

The generation-mode check confirmed that flat mode can expose `--count`,
nested mode exposes `--config.inner.count`, and `BOTH` accepts both spellings.
Conflict resolution was also exercised by registering the same dataclass at two
destinations and parsing distinct values into both instances.  These checks are
behavioral observations, not an implementation prescription.

## Tests and deterministic collection

The upstream `pyproject.toml` contains a native `[tool.pytest]` table describing
test paths, doctest collection, and benchmark autosave. Pytest 8.3.x normally
reads `[tool.pytest.ini_options]`, not that native table. The authoring run did
not preserve enough parser/config diagnostics to prove whether these settings
were applied, ignored, or supplied by another plugin. The frozen checkout
contains 76 test-directory Python files plus two in-package test modules.

The worker reported the following temporary-environment observation:

- interpreter: CPython `3.12.11`;
- pytest: `8.3.4`;
- collection command: `PYTHONDONTWRITEBYTECODE=1 python -m pytest --collect-only -q`;
- collected total: **1,375**;
- collection errors: 0;
- full command: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`;
- full result: **1,259 passed, 12 skipped, 95 xfailed, 9 xpassed, 2 warnings**;
- JUnit root reported `tests=1375`, `failures=0`, `errors=0`.

The collection item identities from two independent CPython 3.12 runs are
byte-identical.  A CPython 3.13 run produced the same 1,375 item identities;
the normalized item-list SHA-256 in both interpreters is
`d1823dbf8898ebd97f38f0463856b9d357cb8523a7cdfa2cd5a181eea2bd5dfb`.
These figures are **not attested as reproducible collection evidence**. The
exact pytest 8.3.4 configuration resolution, item list, JUnit, and status totals
must be regenerated and retained before relying on the 1,375 count. The count
remains `expected_total_source = "unknown"` in `task.toml`; no final verifier
image or authorized test bundle has frozen it.

The full suite also exposed a real environment-pinning concern.  On CPython
3.13 with the same source, the item count stayed 1,375 but the run had 16
failures, including help-formatting and docstring-introspection differences,
and one missing-NumPy failure when the dev group was not installed.  The
production environment must therefore pin the interpreter, dependency set, and
pytest behavior rather than relying only on `requires-python >=3.9`.

## Dependency-closure evidence and gaps

`uv lock --check` passed, and `uv tree --locked --all-groups` resolved 32
package entries.  A fresh CPython 3.12.11 environment was then created with
`uv sync --locked --offline --all-extras --all-groups`; installation, editable
build, import, collection, and the full 1,375-item test run all completed
without a network request after the local uv cache was populated.
A separate `--no-dev` offline environment installed only the two runtime
requirements and the package.  It imported `simple_parsing` and parsed a
minimal dataclass successfully while `numpy`, `torch`, `yaml`, and `tomli_w`
were absent, confirming that the basic path does not eagerly require optional
format/scientific packages.

This is useful local evidence but not a production dependency bundle:

1. The PEP 517 build requirements (`hatchling` and
   `uv-dynamic-versioning`) are not represented as package entries in the
   committed `uv.lock`; build isolation currently resolves them separately.
2. `requirements-test.txt` contains unpinned `matplotlib`, `numpy`, and
   `orion`.  The committed dev group pins the first two through the lock but
   does not include `orion`; the source tests guard the Orion import and pass
   without it.  This discrepancy needs an owner-approved test/dependency
   policy.
3. NumPy, PyTorch, YAML, and TOML support have different optionality in source
   and tests.  The final verifier needs an explicit closure describing which
   features are required and which are intentionally skipped.
4. No content-addressed, hash-locked wheelhouse or immutable base-image digest
   is authorized in this lane.  A local uv cache is not a distributable
   `DependencyBundle`.

Consequently `[dependencies].status` and `[environment].status` remain
`unknown`, even though the source lock and local offline replay are coherent.

## Separate-verifier and publication blockers

The current production verifier boundary imports candidate code only in an
unprivileged child and exchanges JSON-safe call/module/console observations.
The upstream suite directly creates dataclasses and parser objects in the
trusted pytest process and asserts on behaviors that cannot be represented by
the generic JSON call shape alone, including:

- dynamically defined nested dataclasses, enums, partials, and custom
  argparse actions;
- exact `argparse` help/error output and `Namespace` construction;
- config-file reads and temporary serialized files;
- docstring/source inspection and decorator behavior;
- registered encoder/decoder callables and rich serializable objects;
- optional NumPy/PyTorch objects and benchmark fixtures.

Copying the upstream tests into a trusted verifier would violate the separate
candidate/verifier boundary.  A task-specific child-side scenario adapter (or
an approved declarative test rewrite that preserves every assertion) is needed
before production packaging.  No such adapter, private test artifact,
allowlisted command artifact, Oracle bundle, or verifier dependency artifact is
present or referenced here.

No Docker, Harbor, Oracle, empty/stub/forgery control, or production image was
run for this pilot, by design.  The local source baseline is not a Harbor
reward and must not be reported as one.

## Commands and evidence summary

The following commands were run against a detached, clean checkout; temporary
source/build/test artifacts were kept outside this task directory:

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none https://github.com/lebrice/SimpleParsing /tmp/simple-parsing-source
git -C /tmp/simple-parsing-source checkout --detach 7a706bee8b258b548cb979c7321c1ba0cf8413e6
git -C /tmp/simple-parsing-source archive --format=tar HEAD | sha256sum
sha256sum /tmp/simple-parsing-source/LICENSE
uv lock --check
uv tree --locked --all-groups
uv sync --locked --offline --python <cp312.11> --all-extras --all-groups
uv sync --locked --offline --python <cp312.11> --no-dev
python -m pytest --collect-only -q
python -m pytest -q --junitxml=/out/junit.xml
uv build --wheel --out-dir /out/dist
```

The focused argparse/nesting pytest command and the small semantic smoke checks
were run from the same CPython 3.12.11 environment.  Their output, JUnit, and
wheel are evidence artifacts under the temporary audit root only; none is a
hidden test or private byte committed to this catalog.

## Recommendation

Keep `simple-parsing` **blocked** as a development authoring pilot.  To reopen
it for production, first:

1. replay pytest 8.3.4 with explicit configuration resolution, preserve the
   item list/JUnit/status breakdown, and resolve xfail/xpass metric semantics;
2. approve a single difficulty policy for the measured 9,962-line source;
3. freeze Python/OS/pytest and an immutable verifier image, then regenerate the
   collection denominator in that final environment;
4. record a complete hash-locked build and test dependency closure, including
   the build backend and the `requirements-test.txt`/dev-group discrepancy;
5. provide an authorized separate-verifier adapter or declarative child-side
   scenario protocol for dataclass, argparse, serialization, and docstring
   behavior;
6. provision private command/test/Oracle artifacts without copying them into
   this public task tree; and
7. run three valid Oracle baselines followed by empty, stub, forgery, and
   offline controls before changing lifecycle status.
