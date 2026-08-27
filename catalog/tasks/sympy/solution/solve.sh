#!/usr/bin/env sh
set -eu

URL="https://github.com/sympy/sympy"
REVISION="e950d313a932bc6cccbc95376b3821cd2f8b5af4"
ARCHIVE_SHA256="1d3ddf24d7ff12e2eb576275839e78ccad9aa3c474c6f033e9b2619a3bf37d1b"
SOURCE_DIR=/tmp/sympy-source
ARCHIVE=/tmp/sympy-source.tar

rm -rf "$SOURCE_DIR" "$ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)" = "$REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$REVISION" > "$ARCHIVE"
test "$(sha256sum "$ARCHIVE" | awk '{print $1}')" = "$ARCHIVE_SHA256"

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
tar -xf "$ARCHIVE" -C /workspace
rm -rf /workspace/.git /workspace/.github /workspace/sympy/tests

mkdir -p /workspace/src/sympy_slice
cp -a /workspace/sympy /workspace/src/sympy
cat > /workspace/setup.py <<'PY'
from setuptools import find_packages, setup

setup(
    name="sympy-bounded",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
)
PY
cat > /workspace/src/sympy_slice/__init__.py <<'PY'
from __future__ import annotations

import ast
import math
import re
from typing import Any

import sympy as _s

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


_FUNCTIONS = {
    "Abs": _s.Abs,
    "cos": _s.cos,
    "exp": _s.exp,
    "log": _s.log,
    "sin": _s.sin,
    "sqrt": _s.sqrt,
    "tan": _s.tan,
}
_CONSTANTS = {"E": _s.E, "I": _s.I, "oo": _s.oo, "pi": _s.pi}
_BINARY_OPERATORS = {
    ast.Add: lambda left, right: left + right,
    ast.Div: lambda left, right: left / right,
    ast.Mult: lambda left, right: left * right,
    ast.Pow: lambda left, right: left**right,
    ast.Sub: lambda left, right: left - right,
}


def _expression(value: str) -> _s.Expr:
    if not isinstance(value, str):
        raise TypeError("expression must be a string")
    try:
        tree = ast.parse(value.strip(), mode="eval")
        return _expression_node(tree.body)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid expression: {exc}") from exc


def _expression_node(node: ast.AST) -> _s.Expr:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        if isinstance(node.value, float) and not math.isfinite(node.value):
            raise ValueError("non-finite numeric literal")
        return _s.sympify(node.value)
    if isinstance(node, ast.Name) and _NAME.fullmatch(node.id):
        return _CONSTANTS.get(node.id, _s.Symbol(node.id))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _expression_node(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp):
        for operator_type, operation in _BINARY_OPERATORS.items():
            if isinstance(node.op, operator_type):
                return operation(_expression_node(node.left), _expression_node(node.right))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function = _FUNCTIONS.get(node.func.id)
        if function is not None and not node.keywords and len(node.args) == 1:
            return function(_expression_node(node.args[0]))
    raise ValueError("expression contains unsupported syntax")


def _symbol(value: str) -> _s.Symbol:
    if not isinstance(value, str) or not _NAME.fullmatch(value):
        raise ValueError("symbol must be an identifier")
    return _s.Symbol(value)


def parse_expression(expression: str) -> str:
    return str(_expression(expression))


def expand_expression(expression: str) -> str:
    return str(_s.expand(_expression(expression)))


def factor_expression(expression: str) -> str:
    return str(_s.factor(_expression(expression)))


def simplify_expression(expression: str) -> str:
    return str(_s.simplify(_expression(expression)))


def solve_expression(expression: str, symbol: str) -> list[str]:
    parsed = _expression(expression)
    variable = _symbol(symbol)
    if variable not in parsed.free_symbols:
        raise ValueError("symbol is not present in expression")
    return sorted(str(item) for item in _s.solve(parsed, variable))


def differentiate_expression(expression: str, symbol: str) -> str:
    return str(_s.diff(_expression(expression), _symbol(symbol)))


def integrate_expression(expression: str, symbol: str) -> str:
    return str(_s.integrate(_expression(expression), _symbol(symbol)))


def limit_expression(expression: str, symbol: str, point: str) -> str:
    return str(_s.limit(_expression(expression), _symbol(symbol), _expression(point)))


def matrix_determinant(rows: list[list[Any]]) -> str:
    if not isinstance(rows, list):
        raise TypeError("rows must be a list")
    if not rows or any(not isinstance(row, list) for row in rows):
        raise ValueError("rows must be a non-empty square matrix")
    size = len(rows)
    if any(len(row) != size for row in rows):
        raise ValueError("rows must be a non-empty square matrix")
    for value in (value for row in rows for value in row):
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ValueError("matrix values must be numeric scalars")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("matrix values must be finite")
        if isinstance(value, str):
            try:
                float(value)
            except ValueError as exc:
                raise ValueError("matrix values must be numeric scalars") from exc
    try:
        return str(_s.Matrix(rows).det())
    except Exception as exc:
        raise ValueError(f"invalid matrix: {exc}") from exc


__all__ = [
    "parse_expression",
    "expand_expression",
    "factor_expression",
    "simplify_expression",
    "solve_expression",
    "differentiate_expression",
    "integrate_expression",
    "limit_expression",
    "matrix_determinant",
]
PY
