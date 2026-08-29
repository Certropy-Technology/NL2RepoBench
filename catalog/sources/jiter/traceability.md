# Traceability

| Leaf group | Public contract | Evidence source | Adapter boundary |
| --- | --- | --- | --- |
| basic-values | `from_json` JSON primitives and nested containers | `crates/jiter-python/jiter.pyi`; README examples | JSON-safe bytes and JSON-safe return values |
| numbers | float modes, `allow_inf_nan` | `jiter.pyi`; upstream `test_jiter.py` numeric cases | Decimal and LosslessFloat are summarized in child JSON |
| partial | `partial_mode` forms and UTF-8 prefixes | README partial examples; upstream partial tests | no arbitrary callbacks or native parser state |
| errors | deterministic `ValueError`/`TypeError` behavior | public docstrings and upstream error tests | exception type/message observed in candidate child |
| strings | escapes and Unicode | upstream Unicode tests | input is UTF-8 bytes only |
| cache | cache controls and counters | `jiter.pyi`; upstream cache tests | process-local state is exercised per child call |
| lossless | constructor and conversion methods | `jiter.pyi`; upstream lossless tests | decimal values are converted to strings for JSON transport |

The verifier uses `custom-json-v1` and never imports candidate modules in the
trusted process. Each private scenario is a bounded child-side script or call;
the trusted process owns leaf IDs, collection, JUnit, and reward.
