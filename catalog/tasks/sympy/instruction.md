# Project Description

Create an installable Python project that exposes a small, deterministic facade over the core symbolic mathematics behavior represented by SymPy revision `e950d313a932bc6cccbc95376b3821cd2f8b5af4`. The task intentionally covers a stable public slice rather than the complete SymPy distribution, whose upstream test collection is too large for a fixed Harbor denominator. Do not copy the upstream repository or its tests.

The distribution name must be `sympy-bounded` and the import package must be `sympy_slice`. The project must support Python 3.12, install with `pip install .`, and declare runtime dependency `mpmath==1.3.0`. It must work without network access after installation.

## Natural Language Instruction

Create `sympy` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Distribution name: `sympy-bounded`. Primary import package: `sympy_slice`.
- CPython 3.12.14 on debian-12 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: mpmath==1.3.0. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `25` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── src/
    └── sympy_slice/
        └── __init__.py
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

All functions accept strings for expressions and symbols. Expressions use standard SymPy syntax (`x**2`, `sin(x)`, `sqrt(2)`) and must be parsed without executing arbitrary Python. Whitespace around expressions is allowed. Unknown names in an expression become real-free symbolic variables. A malformed expression raises `ValueError`; a non-string argument raises `TypeError`.

### `parse_expression(expression: str) -> str`

Parse an expression and return its canonical `str()` representation. For example, `parse_expression("x + x") == "2*x"` and `parse_expression("sqrt(4)") == "2"`.

### `expand_expression(expression: str) -> str`

Return the expanded form. `expand_expression("(x + 1)**3") == "x**3 + 3*x**2 + 3*x + 1"`.

### `factor_expression(expression: str) -> str`

Return the factored form. `factor_expression("x**2 - 1") == "(x - 1)*(x + 1)"`.

### `simplify_expression(expression: str) -> str`

Return SymPy's general simplified form. `simplify_expression("(x**2 - 1)/(x - 1)") == "x + 1"`.

### `solve_expression(expression: str, symbol: str) -> list[str]`

Solve an algebraic equation represented by an expression equal to zero for the named symbol. Return solutions in SymPy's deterministic ordering, each rendered with `str()`. For `solve_expression("x**2 - 4", "x")`, return `['-2', '2']`. An unknown or invalid symbol raises `ValueError`.

### `differentiate_expression(expression: str, symbol: str) -> str`

Differentiate with respect to the named symbol. For example, `differentiate_expression("sin(x**2)", "x") == "2*x*cos(x**2)"`.

### `integrate_expression(expression: str, symbol: str) -> str`

Return the indefinite integral with respect to the named symbol. For example, `integrate_expression("x**2", "x") == "x**3/3"`.

### `limit_expression(expression: str, symbol: str, point: str) -> str`

Return the limit as the named symbol approaches the parsed point. For example, `limit_expression("sin(x)/x", "x", "0") == "1"`. The point must parse to a finite or SymPy-supported limit value.

### `matrix_determinant(rows: list[list[object]]) -> str`

Construct a rectangular, non-empty matrix from JSON scalar rows and return its determinant as a string. The matrix must be square, have at least one row, and contain only integers, finite floats, or numeric strings. Invalid shape or values raise `ValueError`; non-list input raises `TypeError`. `matrix_determinant([[1, 2], [3, 4]]) == "-2"`.

## Implementation Notes

Use SymPy-compatible public semantics for this slice and keep all result conversion at the facade boundary. The evaluator must be safe for the documented expression language: do not pass untrusted text to `eval` or equivalent unrestricted execution. Deterministic output and documented exception types are part of the contract. Avoid optional dependencies such as NumPy, SciPy, gmpy2, LaTeX parsers, plotting backends, and database or network integrations.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
import sympy_slice
print(sympy_slice)
```

```python
import sympy_slice
# Invoke a documented API using an empty or boundary input.
```

```python
import sympy_slice
print(sympy_slice)
```

```python
import sympy_slice
# Invoke a documented API using an empty or boundary input.
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
