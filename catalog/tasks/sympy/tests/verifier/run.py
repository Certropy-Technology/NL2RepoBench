from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import call


CASES = [
    ("parse_combines_terms", "parse_expression", ["x + x"], "2*x"),
    ("parse_sqrt", "parse_expression", ["sqrt(4)"], "2"),
    ("expand_polynomial", "expand_expression", ["(x + 1)**3"], "x**3 + 3*x**2 + 3*x + 1"),
    ("expand_trigonometric_product", "expand_expression", ["(x + y)*(x - y)"], "x**2 - y**2"),
    ("factor_difference_of_squares", "factor_expression", ["x**2 - 1"], "(x - 1)*(x + 1)"),
    ("factor_integer_content", "factor_expression", ["2*x**2 - 8"], "2*(x - 2)*(x + 2)"),
    ("simplify_cancelled_fraction", "simplify_expression", ["(x**2 - 1)/(x - 1)"], "x + 1"),
    ("simplify_radicals", "simplify_expression", ["sqrt(8)/sqrt(2)"], "2"),
    ("solve_quadratic", "solve_expression", ["x**2 - 4", "x"], ["-2", "2"]),
    ("solve_linear", "solve_expression", ["2*x + 6", "x"], ["-3"]),
    ("differentiate_composite", "differentiate_expression", ["sin(x**2)", "x"], "2*x*cos(x**2)"),
    ("differentiate_polynomial", "differentiate_expression", ["x**3 + 2*x", "x"], "3*x**2 + 2"),
    ("integrate_polynomial", "integrate_expression", ["x**2", "x"], "x**3/3"),
    ("integrate_sine", "integrate_expression", ["cos(x)", "x"], "sin(x)"),
    ("limit_sinc", "limit_expression", ["sin(x)/x", "x", "0"], "1"),
    ("limit_polynomial_at_two", "limit_expression", ["x**2 + x", "x", "2"], "6"),
    ("matrix_two_by_two", "matrix_determinant", [[[1, 2], [3, 4]]], "-2"),
    ("matrix_symbolic_numeric_strings", "matrix_determinant", [[['2', '0'], ['0', '3']]], "6"),
    ("repeatability", "factor_expression", ["x**4 - 1"], "(x - 1)*(x + 1)*(x**2 + 1)"),
]


def main() -> None:
    leaves = []
    for name, function, args, expected in CASES:
        result = call("sympy_slice", function, *args, timeout_sec=10)
        passed = result.ok and result.value == expected
        leaves.append({"id": name, "status": "passed" if passed else "failed", "message": str(result)})

    negative = [
        ("parse_rejects_malformed_expression", "parse_expression", ["x + ("], "ValueError"),
        ("expression_rejects_non_string", "expand_expression", [4], "TypeError"),
        ("symbol_rejects_unknown_name", "solve_expression", ["x**2", "y"], "ValueError"),
        ("matrix_rejects_non_square", "matrix_determinant", [[[1, 2, 3], [4, 5, 6]]], "ValueError"),
        ("expression_rejects_python_code", "parse_expression", ["__import__('os')"], "ValueError"),
    ]
    for name, function, args, exception_type in negative:
        result = call("sympy_slice", function, *args, timeout_sec=10)
        passed = not result.ok and (result.exception_type or "").endswith(exception_type)
        leaves.append({"id": name, "status": "passed" if passed else "failed", "message": str(result)})

    result = call("sympy_slice", "solve_expression", "x**2 - 1", "x", timeout_sec=10)
    try:
        json.dumps({"ok": result.ok, "value": result.value}, allow_nan=False)
        passed = result.ok and result.value == ["-1", "1"]
    except (TypeError, ValueError):
        passed = False
    leaves.append({"id": "rpc_value_is_json_safe", "status": "passed" if passed else "failed"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
