"""Untrusted adapter: the only process that imports candidate code.

Runs as uid 10001 under ``python -I``, which ignores PYTHONPATH, so both the
candidate install target and the preinstalled runtime dependency site are
inserted explicitly. Reads one JSON object on stdin, writes one JSON object on
stdout. Operands arrive as allowlisted ``kind`` tags mapped to in-process
constructors here; no source text or import path crosses the boundary.
"""

from __future__ import annotations

import json
import sys


def _build_operand(spec: dict, vector_cls: type) -> object:
    kind = spec.get("kind")
    if kind == "none":
        return None
    if kind == "num":
        return spec["value"]
    if kind == "str":
        return str(spec["value"])
    if kind == "tuple":
        return tuple(spec["value"])
    if kind == "list":
        return list(spec["value"])
    if kind == "vec":
        return vector_cls(*spec["value"])
    raise LookupError(f"operand kind is not allowlisted: {kind!r}")


def _raises_type_error(thunk) -> bool:
    try:
        thunk()
    except TypeError:
        return True
    except Exception:  # noqa: BLE001 - any other error is a contract failure
        return False
    return False


def _evaluate(case: dict, vector_cls: type) -> bool:
    op = case["op"]
    make = lambda pair: vector_cls(*pair)  # noqa: E731

    if op == "init_raises":
        x = _build_operand(case["x"], vector_cls)
        y = _build_operand(case["y"], vector_cls)
        return _raises_type_error(lambda: vector_cls(x, y))
    if op == "from_values":
        return make(case["exp"]) == make(case["lhs"])
    if op == "repr":
        return repr(make(case["lhs"])) == case["exp"]
    if op == "str":
        return str(make(case["lhs"])) == case["exp"]
    if op == "add":
        return make(case["lhs"]) + make(case["rhs"]) == make(case["exp"])
    if op == "sub":
        return make(case["lhs"]) - make(case["rhs"]) == make(case["exp"])
    if op == "dot":
        return make(case["lhs"]) * make(case["rhs"]) == case["exp"]
    if op == "mul_scalar":
        return make(case["lhs"]) * case["scalar"] == make(case["exp"])
    if op == "mul_raises":
        operand = _build_operand(case["rhs"], vector_cls)
        return _raises_type_error(lambda: make(case["lhs"]) * operand)
    if op == "div":
        return make(case["lhs"]) / case["scalar"] == make(case["exp"])
    if op == "div_raises":
        operand = _build_operand(case["rhs"], vector_cls)
        return _raises_type_error(lambda: make(case["lhs"]) / operand)
    if op == "operators_raises":
        operand = _build_operand(case["rhs"], vector_cls)
        return (
            _raises_type_error(lambda: make(case["lhs"]) < operand)
            and _raises_type_error(lambda: make(case["lhs"]) + operand)
            and _raises_type_error(lambda: make(case["lhs"]) - operand)
        )
    if op == "abs":
        return abs(make(case["lhs"])) == case["exp"]
    if op == "ne_other":
        operand = _build_operand(case["rhs"], vector_cls)
        return make(case["lhs"]) != operand
    if op == "lt":
        return make(case["lhs"]) < make(case["rhs"])
    raise LookupError(f"op is not allowlisted: {op!r}")


def main() -> None:
    request = json.loads(sys.stdin.read())
    for path in reversed(request["sys_path"]):
        sys.path.insert(0, path)

    try:
        from fastvector import Vector2D as vector_cls
    except Exception as exc:  # noqa: BLE001 - reported as a total import failure
        json.dump(
            {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:400]},
            sys.stdout,
        )
        sys.stdout.write("\n")
        return

    outcomes: dict[str, bool] = {}
    errors: dict[str, str] = {}
    for case in request["cases"]:
        try:
            outcomes[case["id"]] = bool(_evaluate(case, vector_cls))
        except Exception as exc:  # noqa: BLE001 - per-case failure, not fatal
            outcomes[case["id"]] = False
            errors[case["id"]] = f"{type(exc).__name__}: {exc}"[:200]
    json.dump({"ok": True, "outcomes": outcomes, "errors": errors}, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
