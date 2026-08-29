# Jinja2 Test Inventory

The frozen upstream tree contains 22 pytest modules with 911 statically named
test functions. The upstream suite also includes resource files, async tests,
extension tests, security tests, and tests whose parameterization or fixture
behavior is not suitable as a direct trusted-process contract.

The private verifier freezes 44 deterministic leaves. It covers package exports
and metadata, basic expressions and escaping, control flow and macros,
filters/tests/customization, undefined and syntax errors, environment options,
loaders and path traversal, bytecode cache, async rendering, sandbox
decisions, meta analysis, native types, and template generation. Each leaf
executes a self-contained scenario in a candidate-owned subprocess and returns
only JSON-safe observations. Collection is exactly 44 unique IDs with no
skipped leaves; a malformed or missing report is a verifier failure.
