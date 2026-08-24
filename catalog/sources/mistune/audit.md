# `mistune` Evidence-First Authoring Audit

Status: **blocked development source**. This task-local directory contains a
public declarative descriptor, a public behavior specification, and this
provenance/validation record. It is not a Harbor task, a dataset entry, or a
publication approval. It contains no upstream test bytes, hidden assertions,
private command plan, dependency cache, wheel, Dockerfile, verifier, Oracle
solution, secret, or shared catalog/index update.

## Decision and Scope

Keep `mistune` at lifecycle status `blocked`. The exact source revision,
archive, license, package boundary, line count, Markdown/security behavior,
source test shape, and several local/offline installation probes are supported
by evidence below. Those facts are sufficient to create a reviewable task
source, but not a production benchmark unit.

The current generic separate-verifier client can cover a small JSON-safe render
subset. It cannot transparently carry live `Markdown`, parser, renderer, state,
plugin, directive, hook, callback, or filesystem behavior. The source suite
also exposes a denominator ambiguity: pytest collects 1,158 item node IDs, then
reports six successful `unittest` subtests in addition; its JUnit suite summary
says 1,164 while the XML contains only 1,158 `<testcase>` elements. No private
adapter or approved leaf policy exists here.

The only durable write root used by this authoring work is
`catalog/tasks/mistune/`. All source, cache, environment, report, and wheel
paths below were disposable files under `/tmp` and were not copied into the
catalog.

## Candidate Identity

The discovery report identifies `lepture/mistune` as a BSD-3-Clause,
Python-only Markdown candidate, but it did not freeze a commit. This audit
therefore resolved the upstream default branch and immediately detached at the
observed commit:

- distribution/import package: `mistune`;
- upstream: `https://github.com/lepture/mistune`;
- default branch observed: `main`;
- requested and resolved revision:
  `a1b50bc12e066e5707ff797f821829bfcdab03b5`;
- commit tree: `46b825df9a978ed7123b036fad5d712b362f0fbb`;
- parent: `bc1f7f3e0c7f4aed89dc6bdc226a60236914e7bf`;
- author and commit time: `2026-08-21T13:48:05+09:00`;
- subject: `docs: update docs`;
- tags at the commit: none;
- remote branches containing it: `origin/main` and `origin/HEAD`;
- submodules: none;
- detached checkout: `/tmp/nl2repo-mistune-audit`, clean after tracked-file
  inspection and probes;
- source version: `mistune.__version__ == "3.4.0"`.

This source version is unreleased at audit time. The public PyPI JSON endpoint
reported latest release `3.3.4` and no `3.4.0` release. The task is locked to
the Git commit above, not to PyPI or to a later value of mutable `main`.

The exact tree has 142 tracked files and 750,001 tracked blob bytes. The direct,
unprefixed archive is:

```text
git archive --format=tar HEAD
archive members: 159 (files plus directory entries)
archive bytes:   870400
archive sha256:  a3212a1b25c6c883ad17c4a6b7eff439016378acb325f105d3fcefe6b1709459
```

Two independent archive commands produced identical bytes. No prefix,
repacking, generated metadata, or source modification was introduced. The
archive digest is recorded as `source.source_digest` in `task.toml`.

For additional audit partitioning only:

```text
git archive HEAD src/mistune
  235520 bytes, 45 tar members
  sha256:6d2c738b46a13a4fb1c58e8e3734756f629a071bb3d37b2f3ebf9fa205c30cbc

git archive HEAD tests
  296960 bytes, 52 tar members
  sha256:c6569f850989878ec804d5c3a862ba8fe27295eb3fef02fac0d3801b74700efa
```

These partition hashes are evidence, not separate source locks.

## License Evidence

The frozen source license is internally consistent:

- path: `LICENSE`;
- size: 1,475 bytes;
- mode: `0644`;
- Git blob: `b141cdb9f3cb8010b9c3dfb392ff1a00db58a413`;
- file SHA-256:
  `539013fd8e19f744f8bf0e27a532bbff54cd689ecef7a800f56ae5dc824be870`;
- text: three-clause BSD redistribution, endorsement, warranty, and liability
  terms, copyright Hsiaoming Yang;
- `pyproject.toml`: `license = {text = "BSD-3-Clause"}`;
- source README: identifies the project as BSD licensed;
- latest public PyPI metadata (`3.3.4`): license value `BSD-3-Clause`.

The SPDX identity recorded in `task.toml` is therefore `BSD-3-Clause`. License
bytes remain in the upstream source archive only; they were not duplicated as a
task-local artifact.

## Package Boundary and LOC

The installable implementation is `src/mistune/`. It contains 38 Python
modules plus `py.typed` across these areas:

```text
mistune root parser/state/factory modules
mistune/_inline
mistune/plugins
mistune/directives
mistune/renderers
```

There is no C, Cython, Rust, shared-library, or generated native source in the
package. Runtime imports are Python standard library plus conditional
`typing_extensions.Self` on Python below 3.11.

Counts use physical lines, nonblank lines, and noncomment lines where a comment
line is a nonblank line whose left-stripped text starts with `#`:

| tree | Python files | physical | nonblank | noncomment |
| --- | ---: | ---: | ---: | ---: |
| `src/mistune/**/*.py` | 38 | 6,380 | 5,112 | **4,984** |
| `tests/**/*.py` | 19 | 1,505 | 1,192 | 1,158 |

The implementation count places this candidate in the benchmark's Hard band
(`>=4,000` source lines) under this explicit counting method. The test
noncomment count happens also to be 1,158; it is unrelated to the independently
collected 1,158 pytest items.

The package root explicitly exports 14 names. A wider static scan finds 24
public-looking module-level classes and 111 public-looking module-level
functions across submodules, but that lexical count includes parser helpers and
renderer callbacks. It is not used as an API denominator. `instruction.md`
uses documented exports and tested application-facing submodules instead.

No normalized `mistune` duplicate exists in `test_files/` or the catalog at the
start of this audit.

## Packaging, Optional Dependencies, and Lock Shape

The exact `pyproject.toml` has SHA-256
`fb14292d81625458634d080afab94321b8147313ee29f39a03a792b611221ad0`.
Relevant values are:

- project name: `mistune`;
- dynamic version: `mistune.__version__` (`3.4.0`);
- Python requirement: `>=3.10`;
- build backend: `setuptools.build_meta`;
- build requirement: unbounded `setuptools`;
- runtime requirement:
  `typing-extensions; python_version < '3.11'`;
- console script: `mistune = mistune.__main__:cli`;
- package discovery: `src` layout;
- package data: `mistune/py.typed`.

There is no `[project.optional-dependencies]` table. Built-in plugins and
directives do not add third-party runtime dependencies. Pygments appears only
as a documentation example for a user-defined renderer and is not imported by
the installed package.

The source declares three development dependency groups:

```text
lint:  mypy, ruff
test:  mypy, pytest, pytest-cov, ruff
docs:  shibuya, sphinx, sphinx-copybutton, sphinx-design
```

`uv.lock` has SHA-256
`a549846b9ed673c47bd1baf3c3e89fd83962c8577a9dc9f448ceba2f5c940f1d`.
It uses lock version 1/revision 1 and contains 46 package records: one editable
Mistune root and 45 registry packages. Every registry record contains an sdist
and at least one wheel with hashes. For CPython 3.12, the selected test group
installed these 15 packages:

```text
mistune 3.4.0
ast-serialize 0.6.0
coverage 7.15.2
iniconfig 2.3.0
librt 0.13.0
mypy 2.3.0
mypy-extensions 1.1.0
packaging 26.2
pathspec 1.1.1
pluggy 1.6.0
pygments 2.20.0
pytest 9.1.1
pytest-cov 7.1.0
ruff 0.15.22
typing-extensions 4.16.0
```

`typing-extensions` is present in that Python 3.12 test environment because the
tooling closure uses it, not because Mistune needs it at runtime there.

The lock does **not** include the PEP 517 build requirement `setuptools`.
Consequently it is not a complete immutable source-build closure. A future
dependency bundle must pin and contain the build backend in addition to the
selected runtime and verifier wheels.

## Offline Installation Evidence

A dedicated cache at `/tmp/nl2repo-mistune-uv-cache` was hydrated once from the
exact lock, then all listed offline operations used `uv --offline`. The cache
was approximately 96 MiB and is not stored or referenced by this task.

### Runtime-only sync

Fresh virtual environments were synchronized from the warmed cache with
`--frozen --no-default-groups`:

| Interpreter | Installed runtime set | Result |
| --- | --- | --- |
| CPython 3.10.20 | Mistune 3.4.0 + typing-extensions 4.16.0 | import/render passed |
| CPython 3.12.11 | Mistune 3.4.0 only | import/render passed |

Neither runtime environment contained pytest or setuptools after sync.

### Test-group sync

A fresh CPython 3.12.11 environment was removed and recreated using:

```text
uv sync --offline --frozen --group test --no-default-groups
```

It installed the 15-package set above and imported/rendered Mistune without
network access.

### Fresh archive build and no-index install

The exact Git archive was unpacked to a different path to avoid reusing the
editable source path. An offline wheel build selected cached
`setuptools==84.0.0`, built a wheel, and a fresh CPython 3.12 environment
installed that wheel using `uv pip install --offline --no-index`:

```text
wheel:  mistune-3.4.0-py3-none-any.whl
bytes:  67722
sha256: c862de1389a13f23d1818458ae2c23fc63451cfb7eece55a05e6589fdf453b20
metadata license: BSD-3-Clause
metadata Requires-Dist: typing-extensions; python_version < "3.11"
```

The installed wheel imported from site-packages, reported version 3.4.0, and
escaped a raw `<script>` input through `create_markdown()`.

These probes establish that offline installation is feasible after cache
hydration for the tested interpreters. They do **not** establish a production
`DependencyBundle`: the cache and wheel are disposable, the build backend was
resolved through an unpinned requirement, no base image is locked, and no
portable wheelhouse/content manifest is present. The wheel hash is a probe
result, not a canonical release artifact or reproducible-build claim.

## Markdown and Public Behavior Review

The package root and documentation define four main modes:

1. `mistune.html`: reusable HTML parser, raw HTML preserved, default
   strikethrough/footnotes/table plugins;
2. `create_markdown()`: reusable configurable parser, HTML escaping on by
   default, no plugins by default;
3. `markdown()`: cached convenience parse, HTML escaping on by default;
4. renderer `None` or `"ast"`: list-of-dictionary token output.

The source docstring identifies CommonMark 0.31.2 compatibility. Core behavior
covers headings, paragraphs, thematic breaks, code, block quotes, tight/loose
and nested lists, HTML, emphasis, code spans, links/images/autolinks/reference
links, escapes, entities, Unicode, and line-ending normalization. The default
block nesting, emphasis nesting, and image nesting limits are each 20 where
applicable.

Documented extension surfaces include:

- mutable `Markdown` before-parse, before-render, and after-render hook lists;
- mutable `BlockParser` and `InlineParser` rule registration;
- mutable renderer method registration and renderer subclassing;
- built-in and caller-defined plugins;
- HTML, Markdown, and reStructuredText renderers;
- RST-style and fenced directives;
- file-backed includes, image/figure directives, admonitions, and TOC;
- parser state and environment returned from `Markdown.parse`; and
- module/console CLI handling message, file, stdin, plugins, escaping,
  hard-wrap, renderer, output path, and version.

A source-only behavior probe independently recorded these distinguishing
outputs:

```text
mistune.html(raw script)                 -> raw script HTML
create_markdown()(raw script)            -> escaped paragraph
markdown(raw script)                     -> escaped paragraph
javascript and repeatedly encoded scheme -> #harmful-link
data:image/png                            -> allowed
data:image/svg+xml                        -> #harmful-link
allow_harmful_protocols=True              -> javascript URL retained
hard_wrap=True                            -> <br /> newline
renderer="ast"                            -> nested JSON-like tokens
```

The JSON probe output SHA-256 was
`361f542220c60905b7c46e21ede3248d3f51c63190239c2e9999f7bb61c21d92`.
The temporary output is not part of the task package.

## Security Behavior

Security behavior is first-class at this revision and is described explicitly
in `instruction.md`.

### HTML and URL policy

`HTMLRenderer(escape=True)` escapes raw inline/block HTML. The global
`mistune.html` parser and the CLI default use `escape=False`, so they preserve
raw HTML and must not be advertised as sanitizers.

`HTMLRenderer.safe_url` allows HTTP(S), mail, telephone, FTP(S), IRC(S),
good image-data prefixes, and relative/fragment/query URLs. It percent-decodes
up to three times for classification, lowercases, and strips leading
whitespace. Other explicit or unknown schemes become `#harmful-link`.
`data:image/svg+xml` is blocked; GIF, PNG, JPEG, and WebP data prefixes are
allowed. A caller can deliberately allow all or selected otherwise harmful
protocol prefixes.

Code content remains escaped independently of raw-HTML mode. Heading IDs, TOC
links, image/figure attributes, math content, titles, and image alt text have
context-specific escaping/filtering.

### Include boundary

The Include directive resolves paths relative to the current source file's real
directory. It rejects absolute paths, real paths outside that directory,
self-includes, circular chains, and missing files. Markdown includes recurse
with normalized line endings; HTML includes remain block HTML subject to
renderer escape mode; text includes are escaped in an escaping HTML renderer.
This behavior uses local filesystem access and shared `BlockState.env` state.

### Resource behavior

Nine dedicated `test_security_*.py` modules collect 42 test items. Two of those
items create three `unittest.subTest` cases each, producing six reported
subtests. They cover URL protocols and encoded schemes, include traversal and
cycles, attribute/CSS injection, TOC escaping/collisions, math escaping, deep
and malformed link/image/emphasis input, repeated formatting/math/spoiler/ruby
patterns, blank-list continuations, reference-link scale, and near-linear
performance checks.

Additional security/performance cases exist in `test_misc.py` and directive
coverage. Several checks use absolute one-second deadlines or relative timing
ratios. They passed on this host, but those thresholds are CPU/interpreter
sensitive and require repetition in the final pinned image. A production
adapter must run comparison phases in one candidate process without weakening
the assertion or conflating host contention with model failure.

## Exact Test Shape

The source pytest configuration is in `pyproject.toml`:

```text
pythonpath = ["src", "."]
testpaths = ["tests"]
filterwarnings = ["error"]
```

The tracked public suite has:

- 17 `tests/test_*.py` modules;
- two Python support modules (`tests/__init__.py` and
  `tests/fixtures/__init__.py`);
- 31 tracked fixture/support files under `tests/fixtures/`, totaling 200,995
  bytes;
- 113 statically declared `test*` functions/methods; and
- fixture-generated `unittest` methods registered at import time.

The 1,158 collected item nodes decompose as:

| Source shape | Items |
| --- | ---: |
| Static `test*` methods | 113 |
| CommonMark JSON fixture | 652 |
| Core fix/CommonMark text fixture | 11 |
| Fourteen plugin fixture sets, each run with and without compatibility `speedup` | 272 |
| Directive fixture classes | 58 |
| Markdown and RST renderer fixtures | 44 |
| TOC hook fixtures | 6 |
| CLI fixtures | 2 |
| **Collected item total** | **1,158** |

Per-module collection is:

```text
test_cli.py                    2
test_commonmark.py           652
test_directives.py            68
test_hooks.py                  8
test_misc.py                  38
test_plugins.py              276
test_renderers.py             61
test_security_edge_cases.py    8
test_security_formatting.py    3
test_security_image.py         2
test_security_include.py       4
test_security_inline.py       13
test_security_math.py          2
test_security_ref_links.py     1
test_security_toc.py           3
test_security_urls.py          6
test_syntax.py                11
TOTAL                       1,158
```

Cache-disabled, plugin-autoload-disabled collection ran twice on each of
CPython 3.10.20, 3.12.11, and 3.14.6 with pytest 9.1.1. Every run collected
1,158 items with no collection errors. All six normalized node lists were
byte-identical and have SHA-256:

```text
b9a9708569887fef1d2e7d155565a42f02a10353542765bc0e249bb9de6897d5
```

This demonstrates stable source collection across those probes, not a frozen
private denominator.

## Source Baselines and JUnit Ambiguity

The exact CPython 3.12.11 environment synchronized from the source `uv.lock`
and test group ran the public suite three times with cache/plugin autoload
disabled, changing `PYTHONHASHSEED` each time:

| Run | Collected items | Pytest result | JUnit summary | JUnit testcase elements | Time |
| --- | ---: | --- | ---: | ---: | ---: |
| 1 | 1,158 | 1,158 passed + 6 subtests passed | 1,164 | 1,158 | 3.94 s |
| 2 | 1,158 | 1,158 passed + 6 subtests passed | 1,164 | 1,158 | 3.70 s |
| 3 | 1,158 | 1,158 passed + 6 subtests passed | 1,164 | 1,158 | 3.84 s |

Additional source-only runs passed on CPython 3.10.20 (6.43 s) and CPython
3.14.6 (4.68 s), again as 1,158 passed plus six passed subtests. Those minimal
cross-version environments used pytest 9.1.1 but were not full production
lock/image replays.

The JUnit files have no failures, errors, or skips. Their root `<testsuite>`
attribute counts the six subtests, but no separate `<testcase>` nodes represent
those subtests. A grader that distrusts XML summary attributes and counts
`<testcase>` elements sees 1,158. Another report protocol could treat the six
subtests as leaves and see 1,164. `task.toml` records the collected-item value
1,158 with `expected_total_source = "unknown"`; it must not be promoted to
`frozen-collection` until the production report adapter and metric policy are
approved.

The full runs are source baselines only. They are not Harbor Oracle runs, do not
exercise an agent-generated repository, and do not establish verifier validity
or reward.

## Separate-Verifier Feasibility

The current generic Python client imports candidate code only in an untrusted
child and exchanges JSON values. A narrow subset is directly feasible:

- call `mistune.html` with a string and receive HTML;
- call `mistune.markdown` with JSON-safe scalar options and no plugin list;
- request `renderer="ast"` and receive built-in token dictionaries;
- call root string utilities; and
- run the module CLI with string arguments/stdin and the console entry point
  with string arguments.

The complete upstream behavior is not transparent through that contract:

1. `create_markdown()` returns a live `Markdown` instance, which is not JSON
   serializable.
2. `Markdown.parse()` returns a `BlockState`; parser state, shared `env`,
   reference dictionaries, and hook effects are process-local mutable objects.
3. Plugins and parser/renderer registration take callables. Custom renderers,
   hooks, directive plugins, and heading-ID functions also require Python
   classes or functions.
4. A JSON plugin array becomes a Python `list`; passing it through the generic
   `mistune.markdown()` path is not sufficient because that function uses the
   plugin iterable in a cache key and a list is unhashable. A child adapter
   must construct and invoke `create_markdown` inside one request instead.
5. Renderer overrides, plugin installation order, repeated calls, caching, and
   state transitions need multiple operations in one child process.
6. `Markdown.read` and Include require controlled candidate-side files and
   path relationships. Private fixture paths must not be exposed to the
   candidate.
7. Timing/security assertions compare repeated operations and need bounded,
   same-process execution with structured observations.
8. Raw objects, exceptions, warnings, bytes from files, parser callbacks, and
   arbitrary plugin metadata require explicit normalization.

Trusted pytest must not directly import the candidate to preserve these
semantics. A Mistune-specific child scenario adapter should accept a bounded,
allowlisted JSON description, construct parser/renderer/plugins/directives and
candidate-owned files inside the child, execute a sequence, and return only
validated JSON-safe HTML/AST/state projections, warnings, exceptions, and
timing samples. No such adapter or private suite exists in this lane.

## Exact Blockers and Reopen Conditions

Reopen this task only after all of the following are recorded:

1. A final Python/OS/base-image lock and a complete content-addressed offline
   dependency bundle, including a pinned setuptools build backend.
2. An explicit production policy for Python implementation/version, warning
   handling, timing tests, subtests, skips, and pytest plugin autoload.
3. A reviewed Mistune child-side scenario adapter covering reusable parsers,
   AST, renderers, built-in plugins, callbacks/hooks, directives, state, CLI,
   and controlled file includes without trusted candidate imports.
4. Private hidden tests and an allowlisted command-plan artifact in the
   authorized visibility-separated store. Do not copy upstream fixtures into
   this public catalog.
5. A frozen structured leaf report resolving the 1,158 item versus 1,164 JUnit
   summary discrepancy.
6. An Oracle bundle and three valid stable final-environment runs, followed by
   empty, stub, forgery, install-failure/hang, and offline controls.
7. A reviewed network/contamination policy. The exact 3.4.0 source is public on
   GitHub even though it is not a PyPI release.

No opaque private artifact refs were invented. No Docker, Harbor compilation,
Oracle, negative control, hidden-test materialization, shared dataset/index,
legacy projection, or secret-bearing command was used.

## Validation Commands Run

Source and provenance inspection:

```text
git clone --filter=blob:none --no-checkout https://github.com/lepture/mistune.git /tmp/nl2repo-mistune-audit
git checkout --detach a1b50bc12e066e5707ff797f821829bfcdab03b5
git show -s --format=... HEAD
git status --short --branch
git submodule status
git archive --format=tar HEAD (repeated)
git archive --format=tar HEAD src/mistune
git archive --format=tar HEAD tests
sha256sum and git hash-object for LICENSE, pyproject.toml, uv.lock, README files
Python static line/API/test-definition and fixture-count scripts
```

Dependency/install probes:

```text
uv 0.11.32
uv lock --check
uv sync --frozen --group test --no-default-groups --python 3.12
remove environment; repeat uv sync with --offline
runtime-only --offline sync on CPython 3.10.20 and 3.12.11
fresh-archive uv build --offline --wheel (cached setuptools 84.0.0)
fresh-venv uv pip install --offline --no-index <built wheel>
installed metadata/import/render smoke probes
```

Collection and source baseline:

```text
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest --collect-only -q -p no:cacheprovider
# repeated twice on CPython 3.10.20, 3.12.11, and 3.14.6

PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest -q -p no:cacheprovider --junitxml=<temporary path>
# three locked-group CPython 3.12 runs; one source probe each on 3.10 and 3.14
```

Task-local validation completed with the repository CLI and tests:

```text
nl2repo task validate-source catalog/tasks/mistune
nl2repo task compile catalog/tasks/mistune --output <temporary> ...
nl2repo task validate <temporary>/mistune/manifest.json
repeat compile to independent roots and byte-compare manifest.json
pytest -o addopts='' tests/test_catalog.py tests/test_metadata_models.py
custom revision/archive/license/dependency/LOC/collection fact assertions
git diff --check and public task-local file/type/private-ref scan
```

The first targeted pytest invocation inherited the repository-wide coverage
`addopts` and exited nonzero only because two selected modules cover 17%, below
the global 80% threshold; all 23 selected tests themselves passed. Re-running
the same tests with `-o addopts=''` passed `23 passed`. The acceptance report
records both commands rather than hiding the validation-command failure.
