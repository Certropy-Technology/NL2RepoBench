# `docstring-parser` static authoring audit and blocker

Status: **blocked**. This directory contains public, task-local authoring
metadata, the public instruction, and this audit only. It contains no upstream
test copy, private test or command artifact, dependency wheelhouse, Dockerfile,
Harbor bundle, Oracle solution, reward, or shared catalog edit. The public
upstream revision was inspected in disposable paths under `/tmp`; those paths
are not task artifacts.

Audit timestamp: `2026-08-22T12:24:03Z`.

## Exact source freeze

The candidate identity still matches the `docstring-parser` entry in
`reports/github-package-candidates.v1.json`:

- upstream: `https://github.com/rr-/docstring_parser`;
- requested revision: `8347d8fb347bd66e4bf5711d3df586357166944a`;
- detached checkout HEAD:
  `8347d8fb347bd66e4bf5711d3df586357166944a`;
- subject: `fix: parse PEP 604 union simple types (int | str) in Google-style
  returns (#112)`;
- author and committer time: `2026-06-30T07:43:30+02:00`;
- parent: `87dca55a7b5bdc854ad1d190f1c461015ba5f008`;
- tree: `f3132c0190969673397361cb9665ff21e801b514`;
- submodules: none;
- checkout status before and after source tests: clean.

Three unprefixed `git archive --format=tar` runs each produced 225,280 bytes
and the same digest:

```text
sha256:2cb59707c20099e0f8b61ab9eeb6faeb7fea370a03b3468c822f84c0ac21f3e9
```

This exactly matches `[source].source_digest` in `task.toml`.

The project metadata declares distribution/import name `docstring_parser`,
version `0.18.0`, `requires-python = ">=3.8"`, Hatchling as its build backend,
no runtime dependencies, `pytest` as its test extra, and `pydoctor >=25.4.0`
as its docs extra. The exact commit is nevertheless one commit after the
`0.18.0` tag:

```text
0.18.0-1-g8347d8f
```

That commit changes `docstring_parser/google.py` and
`docstring_parser/tests/test_google.py` to recognize simple PEP 604 unions in
Google-style return entries. A release tree identified only as `0.18.0` is
therefore not a substitute for this commit-specific archive even though the
package version remains `0.18.0`.

## License evidence

`LICENSE.md` at the requested commit is the MIT License and agrees with
`pyproject.toml` (`license = { text = "MIT" }`) and the MIT classifier:

- size: 1,084 bytes;
- Git blob: `f75411dcf7bbeb12daaf9eebc2b9266f3d190ff6`;
- file SHA-256:
  `dfe514a337ae8417abd31a8af707bbd6172b03e5430bb083e145899ea97a3eea`;
- final byte: newline (`0x0a`).

The commit-specific public raw GitHub response had the same length and digest
and compared byte-for-byte equal with the detached checkout. SPDX `MIT` in
`task.toml` remains supported.

## API and instruction audit

The exact revision has 9 implementation Python files (2,163 physical / 1,818
nonblank lines) and 9 Python files under `docstring_parser/tests` (4,041
physical lines). Runtime signature and AST inventory covered every
implementation module.

The package root has exactly 14 `__all__` exports:

```text
parse, parse_from_object, combine_docstrings, compose, ParseError,
Docstring, DocstringMeta, DocstringParam, DocstringRaises,
DocstringReturns, DocstringDeprecated, DocstringStyle, RenderingStyle, Style
```

`Style is DocstringStyle` is true. The frozen tests additionally import the
same model/error/style definitions from `docstring_parser.common`, generic
functions from `docstring_parser.parser` and `docstring_parser.util`, dialect
functions from `rest`, `google`, `numpydoc`, and `epydoc`, stateful Google and
Numpydoc parser/section APIs, `docstring_parser.numpydoc.DEFAULT_SECTIONS`,
and four Numpydoc regular expressions.

The instruction was repaired narrowly to make those tested import paths and
signatures explicit. It also now states the semantic delta at the requested
post-tag revision: Google `Returns:` and `Yields:` entries whose type consists
of simple names joined by one or more PEP 604 `|` operators are typed entries,
not singular free-form descriptions. No implementation algorithm or upstream
test assertion was copied into the instruction.

The audited test-facing surface is:

| Module | Frozen-test API |
| --- | --- |
| `docstring_parser` | `parse_from_object` |
| `docstring_parser.common` | `ParseError`, `RenderingStyle`, `DocstringStyle`, `DocstringReturns` |
| `docstring_parser.parser` | `parse` |
| `docstring_parser.util` | `combine_docstrings` |
| `docstring_parser.rest` | `parse`, `compose` |
| `docstring_parser.google` | `parse`, `compose`, `GoogleParser`, `Section`, `SectionType` |
| `docstring_parser.numpydoc` | `parse`, `compose`, `NumpydocParser`, `Section`, `DEFAULT_SECTIONS`, `PARAM_KEY_REGEX`, `PARAM_OPTIONAL_REGEX`, `PARAM_DEFAULT_REGEX`, `PARAM_DEFAULT_REGEX_IN_DESC` |
| `docstring_parser.epydoc` | `parse`, `compose` |

The tests then assert the returned object model, ordering, exact composition
strings, parse errors, parser-instance configuration, regular-expression match
groups, object source inspection, and decorator mutation. Those behavior
families are present in `instruction.md`; publication still requires a formal
assertion-level traceability review after an approved verifier adapter exists.

## Frozen public test collection

Only the public upstream tests from the detached checkout were used. With
CPython 3.12.13, pytest 9.1.1, plugin autoload disabled, bytecode disabled, and
the pytest cache provider disabled, collection produced 254 unique node IDs:

| Test file | Collected |
| --- | ---: |
| `test_epydoc.py` | 55 |
| `test_google.py` | 58 |
| `test_numpydoc.py` | 93 |
| `test_parse_from_object.py` | 5 |
| `test_parser.py` | 10 |
| `test_rest.py` | 32 |
| `test_util.py` | 1 |
| **Total** | **254** |

`tests/__init__.py` and `tests/_pydoctor.py` contain no collected tests. Three
independent direct-source runs and one run of the exact command declared in
`task.toml` all passed:

| Run | Collected | Passed | Failed | Errors | Skipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-1 | 254 | 254 | 0 | 0 | 0 |
| baseline-2 | 254 | 254 | 0 | 0 | 0 |
| baseline-3 | 254 | 254 | 0 | 0 | 0 |
| declared command | 254 | 254 | 0 | 0 | 0 |

These are source baselines, not Harbor rewards or Oracle runs. This audit did
not use Docker. uv 0.11.32 had no managed CPython 3.12.14 download, so the
catalog's locked 3.12.14 image was not re-executed here; final collection must
still be repeated in the eventual verifier image before publication.

## Separate-verifier boundary audit

The current Python verifier is intentionally a generic subprocess boundary:
trusted tests call `candidate_client`, which starts a fresh candidate child for
each operation. `candidate_runner` supports JSON `call`/`get`, distribution
requirements metadata, module execution, and console entry-point execution.
For `call`/`get`, request arguments and the returned value must pass the
standard JSON codec. There is no object-handle, callback, fixture-injection,
or task-specific codec operation, and state does not persist between calls.
The repository's 20 focused candidate-boundary tests pass and confirm that
implemented contract; they do not make this task compatible with it.

The frozen `docstring_parser` assertions need capabilities outside that
contract:

| Required behavior | Generic-boundary result |
| --- | --- |
| `parse` and dialect parsers | Return `Docstring`; standard JSON raises `TypeError` |
| root/dialect `compose` | Requires a live `Docstring` and enum value; a JSON object remains a `dict` |
| `DocstringStyle` / `RenderingStyle` | `enum.Enum` values are not standard-JSON values |
| `GoogleParser` / `NumpydocParser` | Stateful instances and `add_section` changes need persistent object handles |
| Numpydoc regex assertions | `re.Match` is not JSON serializable and its named groups cannot be chained in one generic call |
| `parse_from_object` | Requires a live module/class/function and source inspection; hidden-test objects cannot be JSON arguments |
| source-unavailable fallback | The upstream test patches `inspect.getsource` in the implementation process; the generic operation has no patch hook |
| `combine_docstrings` | Requires live callables, signatures, decorator application, `__doc__` mutation, and the returned callable |

A public probe against the exact source confirmed the first-order failures:
`Docstring`, `DocstringStyle`, parser instances, functions, and `re.Match`
objects are not JSON serializable; passing a JSON object to `compose` fails
because it has no `.style`. The Google `Section` namedtuple alone serializes as
a list, but the protocol cannot preserve its type or attach it to a persistent
parser instance. The project declares no CLI or console script that could
serve as a fallback adapter.

Therefore the original upstream pytest files cannot be moved unchanged into a
trusted/root verifier: they import candidate code directly. A task-specific,
object-aware child protocol is required before the assertions can be adapted
without violating the separate-verifier rule.

## Current fail-closed publication gaps

The declarative source validates as a blocked task. A production compile,
without `--allow-incomplete` and without private authorization, exits 1 before
writing a Harbor task and reports exactly:

```text
task is not publishable: dependency_bundle.status=known, tests.test_bundle, tests.commands_artifact, oracle_bundle
```

Those machine-reported gaps are current:

1. `[dependencies].status` is `unknown`. The upstream project has no runtime
   dependency, but the frozen source declares Hatchling as its build backend
   and verification needs pytest; no complete hash-locked offline build/test
   wheelhouse is referenced.
2. No private content-addressed test bundle or allowlisted private command plan
   is referenced. No private artifact bytes or repository artifact cache were
   read during this audit.
3. No Oracle bundle is referenced or was run.
4. The compiler cannot express the additional object-aware adapter blocker;
   it remains an explicit authoring blocker documented above.

No `harbor/` directory or generated bundle was added. Development compilation
with `--allow-incomplete` was intentionally not used because it would not
satisfy production isolation or provenance.

## Principal commands used

```bash
AUDIT=/tmp/nl2repo-docstring-parser-audit
SRC="$AUDIT/source"
PY="$AUDIT/uv-python/cpython-3.12.13-linux-x86_64-gnu/bin/python3.12"

GIT_TERMINAL_PROMPT=0 git -c credential.helper= clone --no-checkout \
  https://github.com/rr-/docstring_parser.git "$SRC"
git -C "$SRC" checkout --detach 8347d8fb347bd66e4bf5711d3df586357166944a
git -C "$SRC" rev-parse HEAD 'HEAD^{tree}'
git -C "$SRC" ls-tree -r HEAD
for run in 1 2 3; do
  git -C "$SRC" archive --format=tar \
    8347d8fb347bd66e4bf5711d3df586357166944a \
    > "$AUDIT/evidence/archive-${run}.tar"
  sha256sum "$AUDIT/evidence/archive-${run}.tar"
done
sha256sum "$SRC/LICENSE.md"
curl --fail --silent --show-error --location \
  https://raw.githubusercontent.com/rr-/docstring_parser/8347d8fb347bd66e4bf5711d3df586357166944a/LICENSE.md \
  --output "$AUDIT/evidence/LICENSE.raw.md"
cmp "$SRC/LICENSE.md" "$AUDIT/evidence/LICENSE.raw.md"

export UV_CACHE_DIR="$AUDIT/uv-cache"
export UV_PYTHON_INSTALL_DIR="$AUDIT/uv-python"
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv python install 3.12.13
cd "$SRC"
uv run --isolated --no-project --python "$PY" --with pytest==9.1.1 -- \
  python -m pytest -p no:cacheprovider --collect-only -q \
  docstring_parser/tests
for run in 1 2 3; do
  uv run --isolated --no-project --python "$PY" --with pytest==9.1.1 -- \
    python -m pytest -p no:cacheprovider -q docstring_parser/tests \
    --junitxml="$AUDIT/evidence/baseline-${run}.xml"
done
uv run --isolated --no-project --python "$PY" --with pytest==9.1.1 -- \
  python -m pytest --continue-on-collection-errors docstring_parser/tests

cd <nl2repobench-worktree>
export UV_CACHE_DIR="$AUDIT/repo-uv-cache"
uv run --isolated --frozen nl2repo task validate-source \
  catalog/tasks/docstring-parser
uv run --isolated --frozen nl2repo harbor compile \
  catalog/tasks/docstring-parser \
  --output "$AUDIT/compile-output" \
  --artifact-root "$AUDIT/private-artifacts-not-used"
uv run --isolated --frozen pytest -q -o addopts='' -p no:cacheprovider \
  tests/test_candidate_boundary.py
```

All uv caches and validation outputs were confined to the disposable audit
root. They are not catalog artifacts and are removed after validation.

## Recommendation

Keep the task blocked. Reopening requires an approved object-aware subprocess
adapter, private content-addressed test and command artifacts, a complete
hash-locked offline dependency closure, and a private Oracle bundle. Only then
should collection be frozen again in the final image and the normal Oracle,
negative-control, review, and publication gates begin.
