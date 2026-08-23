# SymPy bounded public slice

## Project Description

Create an installable Python project that exposes a small, deterministic facade over the core symbolic mathematics behavior represented by SymPy revision `e950d313a932bc6cccbc95376b3821cd2f8b5af4`. The task intentionally covers a stable public slice rather than the complete SymPy distribution, whose upstream test collection is too large for a fixed Harbor denominator. Do not copy the upstream repository or its tests.

The distribution name must be `sympy-bounded` and the import package must be `sympy_slice`. The project must support Python 3.12, install with `pip install .`, and declare runtime dependency `mpmath==1.3.0`. It must work without network access after installation.

## Supports

Use a conventional `src/sympy_slice/` layout, include a concise README, and expose the functions below from `sympy_slice`. Results are intentionally JSON-friendly: expressions are returned as canonical SymPy `str()` output and solutions are a list of strings. Inputs are ordinary JSON-compatible values. Do not expose callbacks, file handles, unevaluated object graphs, or process-global state.

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

The separate verifier invokes one API call per JSON request in a fresh candidate subprocess. A candidate response must be one JSON object with either `{"ok": true, "value": ...}` or `{"ok": false, "error": {"type": ..., "message": ...}}`; values must be JSON serializable. The hidden test source is unavailable to the candidate process.

The frozen private denominator is 24 tests in `harbor/tests/hidden/test_slice.py`. It covers every documented function, representative edge cases, malformed input, JSON serialization, and repeatability. It is a task-local slice denominator and must not be described as the full upstream SymPy collection.
