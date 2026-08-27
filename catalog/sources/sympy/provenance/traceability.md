# Traceability

| Requirement area | Verifier leaves |
| --- | --- |
| Parsing, canonical string output, and code safety | `parse_combines_terms`, `parse_sqrt`, `parse_rejects_malformed_expression`, `expression_rejects_python_code` |
| Expansion | `expand_polynomial`, `expand_trigonometric_product` |
| Factoring | `factor_difference_of_squares`, `factor_integer_content`, `repeatability` |
| Simplification | `simplify_cancelled_fraction`, `simplify_radicals` |
| Solving and symbol validation | `solve_quadratic`, `solve_linear`, `symbol_rejects_unknown_name`, `rpc_value_is_json_safe` |
| Differentiation | `differentiate_composite`, `differentiate_polynomial` |
| Integration | `integrate_polynomial`, `integrate_sine` |
| Limits | `limit_sinc`, `limit_polynomial_at_two` |
| Matrix validation and determinant | `matrix_two_by_two`, `matrix_symbolic_numeric_strings`, `matrix_rejects_non_square` |
| Input type contract | `expression_rejects_non_string` |

Every public promise in `instruction.md` has at least one leaf. The hidden
bundle tests behavior through the subprocess candidate boundary and never
imports candidate code in the trusted verifier process.
