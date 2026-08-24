#!/usr/bin/env sh
set -eu
URL="https://github.com/sympy/sympy"
REVISION="e950d313a932bc6cccbc95376b3821cd2f8b5af4"
SOURCE_DIR=/tmp/sympy-source
rm -rf "$SOURCE_DIR"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)" = "$REVISION"
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
git -C "$SOURCE_DIR" archive --format=tar "$REVISION" | tar -xf - -C /workspace
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

import re
from typing import Any

import sympy as _s
from sympy.parsing.sympy_parser import parse_expr

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _expression(value: str) -> _s.Expr:
    if not isinstance(value, str):
        raise TypeError("expression must be a string")
    try:
        return parse_expr(value, evaluate=True)
    except Exception as exc:
        raise ValueError(f"invalid expression: {exc}") from exc


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
    if any(not isinstance(value, (int, float, str)) or isinstance(value, bool) for row in rows for value in row):
        raise ValueError("matrix values must be numeric scalars")
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
