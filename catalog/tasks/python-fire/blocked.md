# `python-fire` Static Authoring Audit - Blocked

**Status: blocked.** This directory is a public, task-local evidence record
only. It is not a task descriptor, public instruction, private test bundle,
command plan, dependency bundle, verifier, Docker/Harbor tree, Oracle, control
result, or publication approval. No upstream source/archive bytes, license
bytes, hidden tests, secrets, generated projection, or shared catalog file are
included.

## Audit scope

The requested candidate is the exact revision
`716bbc23d7eca949fdb682172283c8d18f742cb6` of
`https://github.com/google/python-fire`. This static audit covers:

- exact source, archive, and Apache-2.0 license provenance;
- package, build, runtime, and public test dependency declarations;
- the reflection, object traversal, generated CLI, help, completion, and
  noninteractive terminal surface exercised by the public tests;
- the `termcolor` and Hypothesis version/determinism gaps; and
- compatibility with the repository's separate candidate subprocess
  boundary.

The public checkout and collection environment existed only under `/tmp`.
No test body, Docker build, Harbor job, Oracle, negative control, or benchmark
trial was run.

## Source and license lock

- Requested and resolved commit:
  `716bbc23d7eca949fdb682172283c8d18f742cb6`.
- Upstream URL: `https://github.com/google/python-fire.git`.
- Commit subject: `Add Python 3.13 and 3.14 checking in build workflow (#623)`.
- Author and committer timestamp: `2025-08-16T17:26:04-04:00`.
- Parent: `27f41ac38f7c77a32d2020c9c13bbf6154065166`.
- Commit tree: `acf36725a461b0f627fefb8115f8ffed779defbc`.
- The detached checkout had 79 tracked files, no gitlink/submodule entries,
  and no tracked changes after inspection.
- Three independent unprefixed `git archive --format=tar HEAD` streams were
  identical: 512,000 bytes, SHA-256
  `a0254d68a6e3b4aef32ce2f9fd1b10f45755149a1194b683897809d80b670494`.
- `LICENSE` is a 573-byte Apache License 2.0 notice. Its Git blob is
  `035adf953c2632a4fa9429f0afd4df1c80788b19`; its SHA-256 is
  `a5de77b62266bca0bb97bf058992f0b0f308a83a8ca55ee10fbf6bd8ed8f7ed0`.
- `pyproject.toml` is 1,862 bytes, Git blob
  `912c08aae90e9ff23bd9ff2bb3e99103cd37a4cb`, and SHA-256
  `f9819bd416ee8208d24cc51d365b3970b521d48dc5687ae9dc8f905603be85ff`.
  It independently declares `license = {text = "Apache-2.0"}`.

The immutable revision, direct Git archive, license notice, and project
metadata are internally consistent source evidence. This record does not
substitute an LLM judgment for the required human license approval.

## Package and dependency evidence

The distribution is `fire` version `0.7.1`, requires Python `>=3.7`, and uses
the flat `fire/` package. The package root exports only `Fire` through
`__all__` and also exposes `__version__`. There is no `[project.scripts]` or
other console entry point. The supported program-level entry is
`python -m fire`, implemented by `fire/__main__.py`.

The source has 24 implementation Python files after excluding tests and test
support: 6,953 physical lines, 5,683 nonblank lines, and 5,011 nonblank,
non-leading-comment lines. A top-level AST inventory found 65 module-level
non-underscore function definitions and 31 module-level non-underscore class
definitions. These names are an inventory, not an assertion that every
internal module is part of the public task contract.

The declarations do not form a frozen offline closure:

- The PEP 517 backend is `setuptools.build_meta`; build requirements are
  `setuptools>=45` and unversioned `wheel`.
- The sole declared runtime dependency is unversioned `termcolor`.
  `fire.formatting` imports it eagerly, and `fire.core` imports formatting, so
  a normal `import fire` requires it.
- The `test` extra contains upper bounds rather than exact locks:
  `setuptools<=80.9.0`, unversioned `pip`, `pylint<3.3.8`,
  `pytest<=8.4.1`, `pytest-pylint<=1.1.2`, `pytest-runner<7.0.0`,
  `termcolor<3.2.0`, `hypothesis<6.137.0`, and
  `levenshtein<=0.27.1`.
- The revision has no tracked lock, constraints file, hash-bearing
  requirements file, or wheelhouse.
- Upstream CI runs `pip install -e .[test]` and pytest once without IPython,
  then installs unpinned `ipython` and runs pytest again. IPython is not in the
  test extra. Its presence selects a different implementation in
  `inspectutils.Info` and a different REPL target in `interact`.

A temporary CPython 3.12.11 install from the public index selected
`termcolor==3.1.0`, `hypothesis==6.136.9`, `attrs==26.1.0`,
`sortedcontainers==2.4.0`, `pytest==8.4.1`, and `setuptools==80.9.0`.
Installing the second upstream-CI branch selected `IPython==9.16.1`. These are
resolution observations from the current host, not approved pins or a
content-addressed dependency artifact. The PEP 517 build used an isolated
temporary environment, and the resulting build files were not copied here.

### `termcolor` surface

`formatting.Bold`, `Underline`, `BoldUnderline`, and `Error` delegate directly
to `termcolor.colored`. The formatting tests accept either plain text or ANSI
escapes for bold and underline. Every help-text test sets
`ANSI_COLORS_DISABLED=1`, so exact help assertions expect an uncolored view.
The runtime requirement remains unbounded, and terminal/color behavior also
depends on inherited environment variables and stream capabilities. A final
task must pin one `termcolor` wheel and explicitly fix the color environment;
the temporary `3.1.0` resolution is not a task decision.

### Hypothesis surface

The default suite includes
`fire/docstrings_fuzz_test.py::DocstringsFuzzTest::test_fuzz_parse`. It uses
`@settings(max_examples=1000, deadline=1000)`, generated nonempty Unicode text,
and one explicit example. It does not set a seed, `derandomize=True`, or a
database policy. Thus it is one collected pytest item whose concrete inputs
and timing are not frozen by the source revision alone.

`fire/parser_fuzz_test.py` uses up to 10,000 Hypothesis examples and
`Levenshtein.distance`, but `pyproject.toml` excludes that module from default
pytest collection. Consequently the default install resolves Levenshtein even
though its only source test consumer is ignored. A production test plan must
not silently switch between the default and parser-fuzz surfaces.

A deterministic task needs an owner-approved policy: either pin Hypothesis
and an explicit seed/profile with no mutable example database, or replace the
property run with a frozen, private input corpus that preserves the approved
assertion semantics. This audit does neither.

## Public test collection

The repository contains 18 `fire/*_test.py` modules and four example test
modules. Static AST inspection found 262 test methods under `fire/` plus 12 in
the examples. The static method count is not a score denominator because the
default pytest configuration ignores `fire/parser_fuzz_test.py` and
`fire/test_components_py3.py`, and Hypothesis runs many examples inside one
collected item.

Collection-only was run in the temporary CPython 3.12.11 environment with the
resolved test extra and cache provider disabled:

```text
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  --collect-only -q -p no:cacheprovider
```

The result was 273 nodes with no collection error:

```text
examples/   12
fire/      261
total      273
```

Three runs without IPython and three runs after installing IPython produced
the same 17,160-byte normalized node list. Its SHA-256 is
`3d17bea9cf605de1a336b3caa4bd67e2a212db33a3745c12ab164448f48e058d`.
IPython's presence can still change test behavior even though it did not
change collection identities.

This is reproducible public-source collection evidence only. It is not a
frozen denominator: there is no final Python/base image, hash-locked offline
closure, approved private adapter suite, structured JUnit result, or metric
contract for this candidate. No test body was executed.

## Introspection, CLI, and help surface

The default tests are primarily in-process tests over live Python objects,
not black-box subprocess tests:

- AST call inventory found 263 direct `fire.Fire` or `core.Fire` invocations
  across `core_test.py`, `decorators_test.py`, `fire_import_test.py`, and
  `fire_test.py`. Inputs include functions, lambdas, classes, bound methods,
  callable instances, modules, dictionaries containing callbacks, lists,
  tuples, sets, generators, async functions, decorators, and custom serializer
  callables.
- `helptext_test.py` makes 29 direct `HelpText` calls and 12 `UsageText`
  calls. It asserts exact sections and formatting derived from signatures,
  annotations, defaults, docstrings, class members, builtins, source metadata,
  and traces. Several comments explicitly acknowledge Python-version-dependent
  builtin descriptions and member sets.
- `inspectutils_test.py` has 12 tests over live functions, classes, bound
  methods, builtins, named tuples, source file/line discovery, annotations,
  and the optional IPython inspector path.
- `completion_test.py` has 18 tests over live functions, classes, objects,
  dictionaries, lists, and a generator, including Bash and Fish script text.
- `main_test.py` has six in-process calls to `fire.__main__.main`. They import
  standard-library modules and temporary Python files; the upstream suite does
  not launch `python -m fire` through `subprocess`.
- Interactive tests replace `fire.interact.Embed`, `IPython.start_ipython`, or
  `code.InteractiveConsole` with mocks. They do not open a real REPL. Help
  output is captured with `StringIO`, so the console pager's TTY path and its
  `shell=True` subprocess are not exercised by these tests.
- The tests import candidate modules directly and also assert private helpers
  such as `core._OneLineResult`, `completion._BashScript`,
  `completion._FishScript`, and `docstrings._strip_blank_lines`.
- Default root discovery includes 12 example-project tests for cipher, diff,
  and widget code. Whether example implementations belong in a Python Fire
  repository-generation contract is an unapproved test-scope decision.

Therefore an instruction covering only root-level `Fire` cannot justify every
upstream assertion. Conversely, exposing all tested internals and example
programs as required public behavior would materially widen the product
contract. The owner must approve a traceable behavior subset before an
instruction or private test bundle is authored.

## Separate candidate boundary

The repository's generic `candidate_client.call` sends JSON-only `args` and
`kwargs`, starts a fresh unprivileged process for each operation, and requires
the return value to survive `json.dumps`. A successful `call` returns the JSON
value and exception fields, but not the candidate process's ordinary stdout
and stderr. This cannot transport or faithfully observe the callbacks,
classes, modules, bound methods, generators, custom objects, serializer
functions, shared process state, captured Fire output, or `FireExit.trace`
objects used by the public tests.

`run_module("fire", ...)` can exercise the `python -m fire` entry in a child
and does expose return code/stdout/stderr. It cannot by itself construct the
upstream component graph or safely provide arbitrary module/file fixtures.
`run_console` is inapplicable because the distribution declares no console
entry point. Trusted pytest must not solve these gaps by importing candidate
code directly.

### Minimum deterministic noninteractive adapter contract

A future task requires a reviewed, task-specific child operation. At minimum
it must:

1. Accept a bounded JSON request containing an allowlisted component fixture
   description, argv, command name, and an operation such as invoke, help, or
   completion. It must not accept arbitrary Python source, pickle, import
   paths, filesystem paths, callbacks, shell commands, or code strings.
2. Construct functions, classes, decorators, docstrings, annotations, and
   other approved component shapes inside the unprivileged child. The fixture
   schema and behavior mapping must be versioned and reviewed; a finite hidden
   scenario ID is not enough to define the public contract.
3. Run with stdin disconnected and no PTY; reject `-i` and `--interactive`;
   disable real pagers and subprocess helpers; and pin locale, timezone,
   `PYTHONHASHSEED`, `TERM`, `PAGER`, `ANSI_COLORS_DISABLED`, `NO_COLOR`, and
   `FORCE_COLOR` handling. CPython, `termcolor`, and the presence or absence of
   IPython must be explicit environment inputs.
4. Return a bounded deterministic object containing exit code, stdout, stderr,
   normalized result type/value, exception type/message, and any approved
   trace observation. Sets, tuples, bytes, paths, generators, classes, and
   Fire trace elements need explicit tagged normalization; ambient absolute
   paths and source line numbers must not leak into expected output.
5. Keep the adapter and fixture factory root-owned/read-only while importing
   candidate code only in the unprivileged child. Trusted pytest must retain
   private expectations and write collection/JUnit itself.
6. Use fixed, explicit text inputs for parser/docstring behavior, or apply the
   separately approved pinned Hypothesis policy. Network, current time,
   mutable Hypothesis databases, real REPLs, real pagers, and arbitrary target
   module execution must remain outside the scored boundary.

This is a reopen requirement, not an implemented adapter or an approval to
narrow the upstream suite.

## Blockers and reopen conditions

Keep `python-fire` blocked because:

1. The measured contract is not approved. The root public API, tested internal
   modules, live fixture graph, and 12 example tests are different possible
   scopes.
2. No Python Fire-specific child adapter or assertion-to-contract mapping
   exists, and the generic JSON/module operations cannot preserve the dominant
   introspection, callback, help, and output assertions.
3. There is no final environment or offline dependency closure. The build
   backend, runtime `termcolor`, test tools, Hypothesis transitives, and CI's
   optional IPython branch are not fully pinned or content-addressed.
4. The selected Hypothesis item has no fixed seed/profile/database policy, and
   parser fuzz inclusion is unresolved.
5. No authorized private tests, allowlisted command plan, structured final
   collection, Oracle bundle, or control record exists. These artifacts were
   intentionally not created under this static-only assignment.

To reopen, first approve the public behavior/test subset and versioned adapter
schema. Then freeze CPython/OS/build/runtime/test dependencies, materialize the
private test and command artifacts, recollect in the final offline verifier,
and only afterward run the required three Oracle baselines and empty, stub,
forgery, and offline controls. Do not claim upstream-suite parity if the task
is narrowed to a noninteractive declarative fixture subset.

## Static validation record

The following evidence commands were used without Docker, Harbor, Oracle, or
shared edits:

```text
git clone --no-tags https://github.com/google/python-fire.git \
  /tmp/nl2repo-python-fire-716bbc23
git -C /tmp/nl2repo-python-fire-716bbc23 switch --detach \
  716bbc23d7eca949fdb682172283c8d18f742cb6
git rev-parse; git show; git status; git submodule status; git ls-tree
git archive --format=tar HEAD | sha256sum  # repeated three times
git hash-object LICENSE pyproject.toml
sha256sum LICENSE pyproject.toml
Python AST, `tomllib`, `rg`, and line/file inventories over public source
uv venv --python CPython-3.12.11 /tmp/nl2repo-python-fire-collect-venv
uv pip install --python <venv>/bin/python '<checkout>[test]'
python -m pytest --collect-only -q -p no:cacheprovider  # three runs
uv pip install --python <venv>/bin/python ipython
python -m pytest --collect-only -q -p no:cacheprovider  # three runs
```

No tests were added or modified, and no test body was executed. No task
descriptor, instruction, Harbor/Docker file, private byte, source archive,
wheelhouse, Oracle, reward, legacy projection, dataset manifest, or shared
index was created or changed.
