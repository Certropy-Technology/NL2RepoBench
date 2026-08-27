# SymPy inventory

- Frozen revision: `e950d313a932bc6cccbc95376b3821cd2f8b5af4`
- Source archive: 35,287,040 bytes, SHA-256 `1d3ddf24d7ff12e2eb576275839e78ccad9aa3c474c6f033e9b2619a3bf37d1b`
- License: BSD-3-Clause (`LICENSE` present)
- Frozen source size: 3,168 Python files and approximately 1,598,712 Python lines.
- Upstream test inventory: 686 `test_*.py` files; the full suite is not used as the Harbor denominator.
- Top-level `sympy` exports: 904 public imported names in `sympy/__init__.py`.
- Task facade exports 9 JSON-safe operations from `sympy_slice`.

The task slice exercises parsing, expansion, factoring, simplification, solving,
differentiation, integration, limits, and numeric matrix determinants. The
candidate must recreate an installable project from an empty workspace; the
reference implementation materializes the frozen source only in the trusted
Oracle run.
