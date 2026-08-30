# tomli test traceability

The private verifier uses only the UID-isolated candidate client. Each leaf is
an explicit JSON-observable scenario and has one stable id. No trusted verifier
process imports the candidate package.

| Leaf group | Contract covered | Upstream basis |
| --- | --- | --- |
| `exports`, `version`, `metadata` | root API, version, PEP 517 metadata | `tests/test_misc.py`, package metadata |
| `scalars`, `tables`, `arrays`, `strings`, `numbers`, `dates`, `unicode` | TOML value grammar and result shape | `tests/test_data.py` and valid fixtures |
| `load-binary`, `load-empty`, `load-text` | file API and binary-mode error | `TestMiscellaneous.test_load`, `test_incorrect_load` |
| `parse-float`, `parse-float-reject` | callback conversion and safety rejection | `test_parse_float`, `test_invalid_parse_float` |
| `error-location`, `error-statement`, `error-end`, `error-escape`, `error-attrs`, `error-deprecated` | error type, coordinates, attributes and compatibility constructor | `tests/test_error.py` |
| `invalid-duplicate`, `invalid-date` | malformed input rejection | `TestData.test_invalid` |
| `crlf`, `deepcopy`, `recursion`, `types-module` | normalization, container behavior, defensive limit and compatibility import | `tests/test_misc.py` |

The large upstream fixture corpus is represented by multiple independent
grammar and invalid-input leaves rather than copied into the public source.
The public instruction states every behavior asserted by these leaves without
exposing hidden test files or the reference implementation.
