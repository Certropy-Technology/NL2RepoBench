# Build `pytest`

Create a complete, installable Python project named `pytest` from an empty
workspace. Implement the deterministic local behavior of the pinned pytest
release described here. Evaluation runs on CPython 3.12 with no network access.

## Project Description

pytest is a Python test runner and assertion framework. This task covers the
public, local core: importing the package, approximate comparisons, assertion
and outcome helpers, warning capture, fixtures and markers, parametrization,
monkeypatch cleanup, the console entry point, and running small local test
files. It does not require sockets, package downloads, external plugins,
debuggers, coverage, parallel workers, or access to hidden verifier files.

## Natural Language Instruction

Create the `pytest` project from an empty workspace and implement the bounded
public contract below. The result must be a real installable Python package,
not a collection of stand-alone helper files. Preserve the package root
exports, exception and outcome types, marker metadata, fixture metadata,
approximation semantics, monkeypatch cleanup, and the local test runner.

The required capability groups are:

1. Package metadata, public exports, `ExitCode`, and both console commands.
2. Numeric/sequence/mapping comparison and assertion/warning context managers.
3. Fixture, marker, parameter, skip, xfail, and import-skip representations.
4. Environment patching with reliable restoration after normal and failed use.
5. Deterministic local collection and execution through `pytest.main`.

Keep the implementation local and deterministic. The package must not download
plugins, discover external services, inspect evaluator-only paths, or turn
test-runner failures into successful results. Public behavior is defined by
the signatures and return/exception contracts in this instruction.

## Supports

- Provide an installable distribution named `pytest`, version `9.2.0.dev277`,
  with Python requirement `>=3.10` and console commands `pytest` and `py.test`.
- The package import root is `pytest`; internal modules may be organized under
  `_pytest` as needed. Runtime dependencies are limited to the standard library
  plus the declared compatible dependencies `iniconfig`, `packaging`, `pluggy`,
  and `pygments`.
- All behavior must be deterministic and local. Do not contact a network,
  launch an external service, inspect hidden paths, or write trusted reports.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── pytest/
│   ├── __init__.py
│   ├── __main__.py
│   ├── _approx.py
│   ├── _assertion.py
│   ├── _fixtures.py
│   ├── _markers.py
│   ├── _monkeypatch.py
│   ├── _outcomes.py
│   └── _runner.py
└── README.md
```

The root import is `pytest`; private implementation modules may live below
`pytest/` but must support the public re-exports listed below. `__main__.py`
backs `python -m pytest`, while the package metadata defines `pytest` and
`py.test` console entry points that call the same runner. The exact module
split may differ, but every documented public entry must be reachable after
installing from `workspace/`.

## API Usage Guide

### Package metadata and exit codes

`pytest.__version__` is the string `"9.2.0.dev277"`. The package exports the
documented public names, including `approx`, `raises`, `warns`, `fixture`,
`mark`, `param`, `MonkeyPatch`, `ExitCode`, `skip`, `xfail`, `fail`, and
`importorskip`. `pytest.ExitCode` is an integer enum with `OK=0`,
`TESTS_FAILED=1`, `INTERRUPTED=2`, `INTERNAL_ERROR=3`, `USAGE_ERROR=4`,
`NO_TESTS_COLLECTED=5`, and `MAX_WARNINGS_ERROR=6`.

### Approximate comparisons

`pytest.approx(expected, rel=1e-6, abs=1e-12, nan_ok=False)` returns a comparison
object. It supports scalar numbers, sequences, and mappings, compares numeric
values within the configured tolerances, treats NaN as unequal by default and
equal when `nan_ok=True`, and provides a stable human-readable `repr`.

### Assertion and warning helpers

`pytest.raises(expected_exception, func=None, *args, match=None, **kwargs)`
returns an exception-info object when used as a context manager or callable.
The captured object exposes the raised exception as `.value`; the expected type
and optional regular-expression `match` are enforced. `pytest.warns(category,
match=None)` is a context manager collecting matching warnings in order.
`pytest.deprecated_call()` is a warning context specialized for
`DeprecationWarning`. `pytest.fail(reason)` raises the framework failure
exception with the supplied reason.

### Fixtures, markers, and parameters

`pytest.fixture(scope="function", params=None, autouse=False, ids=None,
name=None)` decorates a fixture function and stores these options for the test
runner. `pytest.mark.<name>(*args, **kwargs)` creates a marker decorator whose
name, positional arguments, and keyword arguments are retained. The
`parametrize` and `usefixtures` markers use the same representation.
`pytest.param(*values, marks=(), id=None)` returns a parameter set preserving
its values, marks, and optional ID.

### Outcomes and patching

`pytest.skip(reason)`, `pytest.xfail(reason)`, and `pytest.importorskip(module)`
raise the corresponding control-flow exceptions when called during a test;
their reason text is preserved. `pytest.MonkeyPatch()` provides `setenv` and
`delenv` and `undo()` restores changes made to the process environment.

### Local runner

`pytest.main(args=None)` collects Python files named `test_*.py` or `*_test.py`,
runs test functions named `test_*`, supports simple fixtures and
`@pytest.mark.parametrize`, prints a concise result, and returns an
`ExitCode`. A passing file returns `ExitCode.OK`, a failing assertion returns
`ExitCode.TESTS_FAILED`, and a file with no collected tests returns
`ExitCode.NO_TESTS_COLLECTED`. The `pytest` console command reports the same
version as `pytest.__version__` for `--version`.

## Implementation Notes

Use a real installable package with a stable console entry point. Preserve
exception classes and deterministic representations. Keep candidate execution
inside the candidate-owned process boundary; the trusted verifier observes
only bounded JSON-compatible results and independently computes all scores.

## Examples

```python
import pytest

def test_sum():
    assert 2 + 2 == pytest.approx(4)
```

```python
with pytest.raises(ValueError, match="bad"):
    raise ValueError("bad input")
```

```python
@pytest.mark.parametrize("value", [1, 2])
def test_value(value):
    assert value in (1, 2)
```

```python
patch = pytest.MonkeyPatch()
patch.setenv("MODE", "test")
assert patch.getenv("MODE") == "test"
patch.undo()
```

## Error Handling and Boundary Conditions

- `pytest.raises` and `pytest.warns` must fail when the observed exception or
  warning category does not match, and `match` uses regular-expression
  matching against the captured message.
- `pytest.approx` treats NaN as unequal unless `nan_ok=True`; nested values
  preserve sequence order and mapping keys are compared by key.
- A fixture, marker, or parameter decorator preserves its declared scope,
  arguments, keyword arguments, IDs, and marks without mutating the caller's
  input containers.
- `skip`, `xfail`, and `importorskip` preserve the reason text in their
  control-flow exceptions. `MonkeyPatch.undo()` restores the prior state and
  is safe to call after an exception.
- `pytest.main` returns the documented `ExitCode`: success, test failure, or
  no collected tests are distinct outcomes. Collection and execution remain
  bounded and local; unsupported plugins and external services are not loaded.
- Installation and all agent, candidate, verifier, Oracle, and control runs
  are NoNetwork. Do not use a network fallback for missing dependencies.
