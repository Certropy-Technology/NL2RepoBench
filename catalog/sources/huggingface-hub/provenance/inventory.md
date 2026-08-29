# Source And Test Inventory

- Frozen revision: `c6be77fb44d91f474da963e5ad6fce4801811027`.
- Source tree: 183 implementation Python files, 82 test Python files.
- Public AST definitions: 1,503 across 170 modules.
- Package version: `1.29.0.dev0`.
- The complete upstream tests are not a suitable production denominator because
  they include live HTTP/service behavior, optional native/Xet dependencies,
  credential and OAuth flows, CLI integration, Windows branches, and large
  development-only closures.
- A bounded direct collection of deterministic candidate modules found 118
  nodes before collection errors for missing `jedi` and `pytest-mock`.
- Production denominator: 40 JSON-safe deterministic leaves in the private
  custom verifier, with no candidate import in the trusted grading process.
